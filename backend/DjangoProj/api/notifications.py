"""Письма портала: копии заявок уполномоченным лицам и рассылка подписчикам о новых вакансиях."""
import logging
import mimetypes
import os
import secrets
import threading
from datetime import datetime, timedelta
from urllib.parse import urlsplit
from zoneinfo import ZoneInfo

from django.conf import settings
from django.core import signing
from django.core.mail import EmailMultiAlternatives, get_connection
from django.db import connections
from django.template.loader import render_to_string
from django.utils import timezone
from django.utils.crypto import constant_time_compare, salted_hmac
from django.utils.text import Truncator

from .models import ApplicationRecipient, Vacancy, VacancySubscription

logger = logging.getLogger(__name__)

KIND_VACANCIES = 'vacancies'
KIND_RESERVE = 'reserve'
KIND_PRACTICE = 'practice'
KIND_TRAINING = 'training'
KIND_FEEDBACK = 'feedback'

KIND_LABELS = {
    KIND_VACANCIES: 'Заявка на вакансию',
    KIND_RESERVE: 'Кадровый резерв',
    KIND_PRACTICE: 'Практика',
    KIND_TRAINING: 'Предложение по обучению',
    KIND_FEEDBACK: 'Обратная связь',
}

# Суммарный размер вложений, больше которого файлы не прикладываем (лимит почтовых серверов)
MAX_ATTACHMENTS_BYTES = 20 * 1024 * 1024

# Время в письмах — по Сургуту (UTC+5), а не по серверному UTC
MAIL_TIMEZONE = ZoneInfo('Asia/Yekaterinburg')
MAIL_TIMEZONE_LABEL = 'Сургут, UTC+5'

UNSUBSCRIBE_SALT = 'vacancy-unsubscribe'


def _site_url():
    return settings.SITE_URL.rstrip('/')


def _site_host():
    return urlsplit(_site_url()).netloc or _site_url()


def recipient_emails(kind):
    return list(
        ApplicationRecipient.objects
        .filter(is_active=True, **{f'receives_{kind}': True})
        .exclude(email='')
        .values_list('email', flat=True)
        .distinct()
    )


def notify_recipients(kind, subject, fields, files=(), emails=None, reply_to=None):
    """
    Отправить копию заявки уполномоченным лицам.

    kind    — vacancies | reserve | practice | training | feedback
    fields  — список пар («Название поля», значение)
    files   — FieldFile'ы, которые нужно приложить к письму
    emails  — явный список адресов (для проверочной отправки); по умолчанию — получатели из админки
    reply_to — адрес отправителя заявки: ответ на письмо уйдёт ему

    Ошибка отправки никогда не ломает приём заявки: она только пишется в лог.
    Возвращает число получателей, которым ушло письмо.
    """
    if emails is None:
        emails = recipient_emails(kind)
    if not emails:
        return 0

    fields = [(label, str(value)) for label, value in fields if value not in (None, '')]
    subject = ' '.join(str(subject).split())[:200]  # без переводов строк: защита от header injection
    sent_at = datetime.now(MAIL_TIMEZONE).strftime('%d.%m.%Y, %H:%M')

    message = EmailMultiAlternatives(
        subject=subject,
        body='',
        from_email=settings.DEFAULT_FROM_EMAIL,
        to=emails,
        reply_to=[reply_to] if reply_to else None,
    )

    attached = []
    skipped = []
    total = 0
    for file_field in files:
        if not file_field:
            continue
        name = os.path.basename(file_field.name)
        try:
            size = file_field.size
            if total + size > MAX_ATTACHMENTS_BYTES:
                skipped.append(name)
                continue
            file_field.open('rb')
            try:
                content = file_field.read()
            finally:
                file_field.close()
        except OSError:
            logger.exception('Не удалось прочитать вложение %s', name)
            skipped.append(name)
            continue
        total += size
        mimetype = mimetypes.guess_type(name)[0] or 'application/octet-stream'
        message.attach(name, content, mimetype)
        attached.append(name)

    kind_label = KIND_LABELS.get(kind, 'Обращение')
    text_lines = [f'{subject}', f'{kind_label}. Получено {sent_at} ({MAIL_TIMEZONE_LABEL})', '']
    text_lines += [f'{label}: {value}' for label, value in fields]
    if attached:
        text_lines += ['', 'Вложения: ' + ', '.join(attached)]
    if skipped:
        text_lines += ['', 'Файлы не приложены (слишком большие или недоступны), см. админ-панель: ' + ', '.join(skipped)]
    message.body = '\n'.join(text_lines)

    message.attach_alternative(
        render_to_string('api/emails/application.html', {
            'title': subject,
            'preheader': f'{kind_label} — получено {sent_at}',
            'kind_label': kind_label,
            'sent_at': sent_at,
            'tz_label': MAIL_TIMEZONE_LABEL,
            'fields': fields,
            'attached': attached,
            'skipped': skipped,
            'admin_url': f'{_site_url()}/admin/',
            'site_url': _site_url(),
            'site_host': _site_host(),
        }),
        'text/html',
    )

    try:
        message.send()
    except Exception:
        logger.exception('Не удалось отправить копию заявки (%s)', kind)
        return 0
    return len(emails)


# ---------------------------------------------------------------------------
# Рассылка подписчикам о новых вакансиях
# ---------------------------------------------------------------------------

def unsubscribe_token(email):
    return signing.dumps(email.strip().lower(), salt=UNSUBSCRIBE_SALT)


def email_from_unsubscribe_token(token):
    """Email из токена отписки или None, если токен подделан."""
    try:
        return signing.loads(token, salt=UNSUBSCRIBE_SALT)
    except signing.BadSignature:
        return None


# ---------------------------------------------------------------------------
# Подтверждение email кодом из письма (подписка на вакансии, обратная связь)
# ---------------------------------------------------------------------------

CODE_LENGTH = 6
CODE_TTL = timedelta(minutes=10)
CODE_RESEND_COOLDOWN = timedelta(seconds=60)
CODE_MAX_ATTEMPTS = 5  # неверных вводов, после чего нужен новый код
CODE_MAX_SENDS = 5  # писем с кодом на одну запись


def _code_hash(obj, code):
    return salted_hmac('email-confirmation-code', f'{obj._meta.label_lower}:{obj.pk}:{obj.email}:{code}').hexdigest()


def seconds_until_resend(obj):
    """Сколько секунд осталось до следующей отправки кода (0 — можно отправлять)."""
    if not obj.code_sent_at:
        return 0
    left = obj.code_sent_at + CODE_RESEND_COOLDOWN - timezone.now()
    return max(0, int(left.total_seconds()) + (1 if left.microseconds else 0))


def send_email_code(obj, action, reason):
    """
    Сгенерировать новый код, сохранить его хэш и отправить письмо на obj.email.

    action — что произойдёт после подтверждения («включить подписку на новые вакансии»);
    reason — почему пришло письмо («для подписки на вакансии»).
    Если письмо не ушло — исключение пробрасывается, а состояние записи не меняется.
    """
    code = ''.join(secrets.choice('0123456789') for _ in range(CODE_LENGTH))
    ttl_minutes = int(CODE_TTL.total_seconds() // 60)
    name = (getattr(obj, 'name', '') or '').strip()
    greeting = f'Здравствуйте, {name}!' if name else 'Здравствуйте!'

    message = EmailMultiAlternatives(
        subject=f'Код подтверждения: {code}',
        body='\n'.join([
            greeting,
            '',
            f'Код подтверждения email: {code}',
            f'Введите его на сайте {_site_host()}, чтобы {action}. Код действует {ttl_minutes} минут.',
            '',
            f'Если вы не запрашивали код ({reason}), просто проигнорируйте это письмо.',
        ]),
        from_email=settings.DEFAULT_FROM_EMAIL,
        to=[obj.email],
    )
    message.attach_alternative(
        render_to_string('api/emails/subscription_code.html', {
            'title': 'Код подтверждения',
            'preheader': f'Ваш код: {code}',
            'greeting': greeting,
            'code': code,
            'action': action,
            'reason': reason,
            'ttl_minutes': ttl_minutes,
            'site_url': _site_url(),
            'site_host': _site_host(),
        }),
        'text/html',
    )
    message.send()

    obj.code_hash = _code_hash(obj, code)
    obj.code_sent_at = timezone.now()
    obj.code_attempts = 0
    obj.code_sends += 1
    obj.save(update_fields=['code_hash', 'code_sent_at', 'code_attempts', 'code_sends'])


CODE_OK = 'ok'
CODE_WRONG = 'wrong'
CODE_EXPIRED = 'expired'
CODE_LOCKED = 'locked'


def check_email_code(obj, code):
    """Проверить введённый код: CODE_OK / CODE_WRONG / CODE_EXPIRED / CODE_LOCKED. Неверный ввод учитывается."""
    code = ''.join(str(code or '').split())
    if not obj.code_hash or not obj.code_sent_at or timezone.now() > obj.code_sent_at + CODE_TTL:
        return CODE_EXPIRED
    if obj.code_attempts >= CODE_MAX_ATTEMPTS:
        return CODE_LOCKED
    if constant_time_compare(_code_hash(obj, code), obj.code_hash):
        return CODE_OK
    obj.code_attempts += 1
    obj.save(update_fields=['code_attempts'])
    return CODE_LOCKED if obj.code_attempts >= CODE_MAX_ATTEMPTS else CODE_WRONG


def _subscribers_for(vacancy):
    """Активные подписки, подходящие вакансии: без отраслевого органа — на любые, иначе только на совпадающий."""
    vacancy_branch = (vacancy.branch or '').strip().casefold()
    result = {}
    for sub in VacancySubscription.objects.filter(is_active=True, email_verified=True).exclude(email=''):
        sub_branch = (sub.branch or '').strip().casefold()
        if vacancy_branch and sub_branch and sub_branch != vacancy_branch:
            continue
        result.setdefault(sub.email.strip().lower(), sub)
    return list(result.values())


def _vacancy_facts(vacancy):
    facts = [
        ('Подразделение', vacancy.branch),
        ('Место работы', vacancy.location),
        ('Оплата труда', vacancy.salary),
        ('Тип должности', vacancy.job_type.name if vacancy.job_type else ''),
        ('Требуемый опыт', vacancy.required_experience.name if vacancy.required_experience else (vacancy.experience or '')),
        ('Режим работы', vacancy.working_hours.name if vacancy.working_hours else ''),
        ('Дата публикации', vacancy.published_at.strftime('%d.%m.%Y')),
    ]
    return [(label, value) for label, value in facts if value]


def _build_vacancy_message(vacancy, sub, facts, excerpt, skills):
    url = f'{_site_url()}/vacancyinfo/{vacancy.pk}'
    unsubscribe_url = f'{_site_url()}/api/vacancy-unsubscribe/{unsubscribe_token(sub.email)}/'
    name = (sub.name or '').strip()
    greeting = f'Здравствуйте, {name}! На портале опубликована новая вакансия.' if name else 'Здравствуйте! На портале опубликована новая вакансия.'

    text = [vacancy.title, greeting, '']
    text += [f'{label}: {value}' for label, value in facts]
    if excerpt:
        text += ['', excerpt]
    text += ['', f'Подробнее и отклик: {url}', '', f'Отписаться от рассылки: {unsubscribe_url}']

    message = EmailMultiAlternatives(
        subject=f'Новая вакансия: {vacancy.title}'.replace('\n', ' ')[:200],
        body='\n'.join(text),
        from_email=settings.DEFAULT_FROM_EMAIL,
        to=[sub.email],
        headers={
            'List-Unsubscribe': f'<{unsubscribe_url}>',
            'List-Unsubscribe-Post': 'List-Unsubscribe=One-Click',
        },
    )
    message.attach_alternative(
        render_to_string('api/emails/new_vacancy.html', {
            'title': vacancy.title,
            'preheader': f'{vacancy.branch or "Сургутский район"} · {vacancy.location}',
            'vacancy': vacancy,
            'greeting': greeting,
            'facts': [f for f in facts if f[0] != 'Подразделение'],
            'excerpt': excerpt,
            'skills': skills,
            'url': url,
            'unsubscribe_url': unsubscribe_url,
            'subscription_branch': (sub.branch or '').strip(),
            'site_url': _site_url(),
            'site_host': _site_host(),
        }),
        'text/html',
    )
    return message


def notify_subscribers_about_vacancy(vacancy_pk):
    """
    Разослать подписчикам письмо о новой вакансии. Безопасно вызывать повторно:
    «захват» вакансии делается атомарным UPDATE, поэтому каждая вакансия рассылается один раз.
    Возвращает число отправленных писем.
    """
    claimed = Vacancy.objects.filter(
        pk=vacancy_pk, is_active=True, subscribers_notified_at__isnull=True,
    ).update(subscribers_notified_at=timezone.now())
    if not claimed:
        return 0

    vacancy = Vacancy.objects.select_related('job_type', 'required_experience', 'working_hours').get(pk=vacancy_pk)
    subscribers = _subscribers_for(vacancy)
    if not subscribers:
        return 0

    facts = _vacancy_facts(vacancy)
    excerpt = Truncator((vacancy.description or '').strip()).chars(400)
    skills = [s.strip() for s in (vacancy.skills or '').splitlines() if s.strip()][:6]

    sent = 0
    try:
        connection = get_connection()
        connection.open()
        try:
            for sub in subscribers:
                try:
                    sent += connection.send_messages([_build_vacancy_message(vacancy, sub, facts, excerpt, skills)]) or 0
                except Exception:
                    logger.exception('Не удалось отправить письмо о вакансии %s подписчику %s', vacancy_pk, sub.pk)
        finally:
            connection.close()
    except Exception:
        logger.exception('Не удалось открыть почтовое соединение для рассылки по вакансии %s', vacancy_pk)
    logger.info('Рассылка о вакансии %s: отправлено %s из %s', vacancy_pk, sent, len(subscribers))
    return sent


def notify_subscribers_in_background(vacancy_pk):
    """Рассылка в отдельном потоке: сохранение вакансии в админке не ждёт почтовый сервер."""
    def run():
        try:
            notify_subscribers_about_vacancy(vacancy_pk)
        except Exception:
            logger.exception('Рассылка о вакансии %s завершилась ошибкой', vacancy_pk)
        finally:
            connections.close_all()  # поток живёт недолго — свои соединения с БД закрываем сами

    threading.Thread(target=run, name=f'vacancy-mailing-{vacancy_pk}', daemon=True).start()
