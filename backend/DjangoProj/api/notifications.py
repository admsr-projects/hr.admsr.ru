"""Дублирование заявок с портала на почту уполномоченных лиц."""
import logging
import mimetypes
import os

from django.conf import settings
from django.core.mail import EmailMessage

from .models import ApplicationRecipient

logger = logging.getLogger(__name__)

KIND_VACANCIES = 'vacancies'
KIND_RESERVE = 'reserve'
KIND_PRACTICE = 'practice'
KIND_TRAINING = 'training'

# Суммарный размер вложений, больше которого файлы не прикладываем (лимит почтовых серверов)
MAX_ATTACHMENTS_BYTES = 20 * 1024 * 1024


def recipient_emails(kind):
    return list(
        ApplicationRecipient.objects
        .filter(is_active=True, **{f'receives_{kind}': True})
        .exclude(email='')
        .values_list('email', flat=True)
        .distinct()
    )


def notify_recipients(kind, subject, fields, files=()):
    """
    Отправить копию заявки уполномоченным лицам.

    kind    — vacancies | reserve | practice | training
    fields  — список пар («Название поля», значение)
    files   — FieldFile'ы, которые нужно приложить к письму

    Ошибка отправки никогда не ломает приём заявки: она только пишется в лог.
    Возвращает число получателей, которым ушло письмо.
    """
    emails = recipient_emails(kind)
    if not emails:
        return 0

    lines = [f'{label}: {value}' for label, value in fields if value not in (None, '')]
    subject = ' '.join(str(subject).split())[:200]  # без переводов строк: защита от header injection
    message = EmailMessage(
        subject=subject,
        body='\n'.join(lines),
        from_email=settings.DEFAULT_FROM_EMAIL,
        to=emails,
    )

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

    if skipped:
        message.body += '\n\nФайлы не приложены (слишком большие или недоступны), см. админ-панель: ' + ', '.join(skipped)

    try:
        message.send()
    except Exception:
        logger.exception('Не удалось отправить копию заявки (%s)', kind)
        return 0
    return len(emails)
