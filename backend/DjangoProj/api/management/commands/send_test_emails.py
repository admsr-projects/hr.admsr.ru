"""Проверочная отправка всех писем сайта на один адрес (в базу ничего не пишется)."""
from django.core.management.base import BaseCommand, CommandError
from django.core.validators import validate_email
from django.core.exceptions import ValidationError

from api.models import Vacancy, VacancySubscription
from api.notifications import (
    KIND_FEEDBACK, KIND_PRACTICE, KIND_RESERVE, KIND_TRAINING, KIND_VACANCIES,
    _build_vacancy_message, _vacancy_facts, notify_recipients,
)
from django.utils.text import Truncator
from django.core.mail import get_connection


class SampleFile:
    """Минимальная замена FieldFile для проверки вложений."""

    def __init__(self, name, content):
        self.name = name
        self._content = content
        self.size = len(content)

    def __bool__(self):
        return True

    def open(self, mode='rb'):
        return self

    def read(self):
        return self._content

    def close(self):
        pass


CASES = [
    ('vacancies', 'Заявка на вакансию', KIND_VACANCIES),
    ('reserve', 'Кадровый резерв', KIND_RESERVE),
    ('practice', 'Практика', KIND_PRACTICE),
    ('training', 'Предложение по обучению', KIND_TRAINING),
    ('feedback', 'Обратная связь', KIND_FEEDBACK),
]


class Command(BaseCommand):
    help = (
        'Отправляет на указанный адрес по одному письму каждого вида: заявка на вакансию, кадровый резерв, '
        'практика, предложение по обучению, обратная связь и рассылка о новой вакансии.'
    )

    def add_arguments(self, parser):
        parser.add_argument('email', help='Куда отправить проверочные письма')
        parser.add_argument(
            '--only', choices=[c[0] for c in CASES] + ['subscriber'],
            help='Отправить только один вид письма',
        )

    def handle(self, *args, **options):
        email = options['email'].strip()
        try:
            validate_email(email)
        except ValidationError:
            raise CommandError(f'Некорректный адрес: {email}')
        only = options['only']

        fixtures = {
            'vacancies': (
                '[ТЕСТ] Заявка на вакансию: Иванов Иван — Главный специалист',
                [
                    ('Вакансия', 'Главный специалист отдела кадров'),
                    ('ФИО', 'Иванов Иван Иванович'), ('Дата рождения', '01.01.1990'),
                    ('Телефон', '+7 900 000-00-00'), ('Email', 'ivanov@example.com'),
                    ('Образование', 'Высшее'), ('Специальность', 'Государственное и муниципальное управление'),
                    ('Стаж муниципальной службы', '5 лет'),
                    ('Трудовая деятельность', '2015–2020 — специалист\n2020–2026 — ведущий специалист'),
                    ('Откуда узнал(а)', 'Сайт администрации'),
                ],
                [SampleFile('resume.pdf', b'%PDF-1.4 test')],
            ),
            'reserve': (
                '[ТЕСТ] Заявка на вакансию: Петрова Анна — Кадровый резерв',
                [('Вакансия', 'Кадровый резерв'), ('ФИО', 'Петрова Анна Сергеевна'), ('Телефон', '+7 900 111-11-11'), ('Email', 'petrova@example.com')],
                [],
            ),
            'practice': (
                '[ТЕСТ] Заявка на практику: Сидоров Пётр',
                [
                    ('ФИО', 'Сидоров Пётр Петрович'), ('Телефон', '+7 900 222-22-22'), ('Email', 'sidorov@example.com'),
                    ('Учебное заведение', 'СурГУ'), ('Курс', '3'), ('Специальность', 'Юриспруденция'),
                    ('Желаемый период практики', 'июль 2027'), ('Комментарий', 'Хочу пройти практику в правовом управлении.'),
                ],
                [SampleFile('letter.pdf', b'%PDF-1.4 test')],
            ),
            'training': (
                '[ТЕСТ] Предложение по обучению',
                [('Имя', 'Анонимно'), ('Подразделение', 'Управление по кадрам'), ('Предложение', 'Добавить курс по работе с обращениями граждан.')],
                [],
            ),
            'feedback': (
                '[ТЕСТ] Обратная связь с портала',
                [('Сообщение', 'Тестовое сообщение с формы обратной связи.\nВторая строка сообщения.')],
                [SampleFile('photo.jpg', b'\xff\xd8\xff test')],
            ),
        }

        sent = 0
        for key, label, kind in CASES:
            if only and only != key:
                continue
            subject, fields, files = fixtures[key]
            count = notify_recipients(kind, subject, fields, files=files, emails=[email])
            self.stdout.write(f'{"OK " if count else "ОШИБКА"} {label}')
            sent += bool(count)

        if not only or only == 'subscriber':
            sent += self._send_subscriber_mail(email)

        self.stdout.write(self.style.SUCCESS(f'Готово: отправлено {sent}. Проверьте ящик {email}.'))

    def _send_subscriber_mail(self, email):
        vacancy = Vacancy.objects.filter(is_active=True).select_related(
            'job_type', 'required_experience', 'working_hours').first()
        if vacancy is None:
            vacancy = Vacancy(
                pk=1, title='Главный специалист отдела кадров', branch='Управление по кадрам', location='г. Сургут',
                salary='от 60 000 ₽', description='Ведение кадрового делопроизводства.', skills='Знание ТК РФ\nОпыт от 3 лет',
            )
        subscription = VacancySubscription(email=email, name='Тест', branch=vacancy.branch)
        facts = _vacancy_facts(vacancy) if vacancy.published_at else []
        excerpt = Truncator((vacancy.description or '').strip()).chars(400)
        skills = [s.strip() for s in (vacancy.skills or '').splitlines() if s.strip()][:6]
        message = _build_vacancy_message(vacancy, subscription, facts, excerpt, skills)
        message.subject = '[ТЕСТ] ' + message.subject
        try:
            get_connection().send_messages([message])
        except Exception as exc:
            self.stdout.write(self.style.ERROR(f'ОШИБКА Рассылка о вакансии: {exc}'))
            return 0
        self.stdout.write(f'OK  Рассылка подписчику о новой вакансии («{vacancy.title}»)')
        return 1
