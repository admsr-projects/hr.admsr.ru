import re
from datetime import timedelta

from django.contrib.auth import get_user_model
from django.core import mail
from django.test import Client, TestCase
from django.utils import timezone

from .models import ApplicationRecipient, Feedback, Vacancy, VacancySubscription
from .notifications import CODE_MAX_ATTEMPTS, CODE_RESEND_COOLDOWN, CODE_TTL, _subscribers_for


class SubscriptionEmailConfirmationTests(TestCase):
    """Подписка на вакансии включается только после ввода кода из письма."""

    subscribe_url = '/api/vacancy-subscribe/'
    confirm_url = '/api/vacancy-subscribe/confirm/'
    resend_url = '/api/vacancy-subscribe/resend/'

    def subscribe(self, email='ivan@example.com', **extra):
        return self.client.post(self.subscribe_url, {'name': 'Иван', 'email': email, 'branch': '', **extra})

    def last_code(self):
        return re.search(r'\b(\d{6})\b', mail.outbox[-1].body).group(1)

    def wrong_code(self):
        return '000000' if self.last_code() != '000000' else '111111'

    def test_subscribe_sends_code_and_stays_inactive(self):
        response = self.subscribe()

        self.assertEqual(response.status_code, 201)
        sub = VacancySubscription.objects.get()
        self.assertFalse(sub.is_active)
        self.assertFalse(sub.email_verified)
        self.assertEqual(response.json()['id'], sub.pk)
        self.assertEqual(len(mail.outbox), 1)
        self.assertEqual(mail.outbox[0].to, ['ivan@example.com'])
        self.assertIn(self.last_code(), mail.outbox[0].subject)
        # Код нигде не хранится открытым текстом
        self.assertNotIn(self.last_code(), sub.code_hash)

    def test_unconfirmed_subscription_gets_no_vacancy_mail(self):
        self.subscribe()
        vacancy = Vacancy(title='Специалист', branch='', location='Сургут')

        self.assertEqual(_subscribers_for(vacancy), [])

    def test_correct_code_activates_subscription(self):
        sub_id = self.subscribe().json()['id']

        response = self.client.post(self.confirm_url, {'id': sub_id, 'code': self.last_code()})

        self.assertEqual(response.status_code, 200)
        sub = VacancySubscription.objects.get(pk=sub_id)
        self.assertTrue(sub.is_active)
        self.assertTrue(sub.email_verified)
        self.assertEqual(sub.code_hash, '')
        self.assertEqual(len(_subscribers_for(Vacancy(title='Специалист', branch='', location='Сургут'))), 1)

    def test_code_with_spaces_is_accepted(self):
        sub_id = self.subscribe().json()['id']
        code = self.last_code()

        response = self.client.post(self.confirm_url, {'id': sub_id, 'code': f' {code[:3]} {code[3:]} '})

        self.assertEqual(response.status_code, 200)

    def test_wrong_code_is_rejected_and_counted(self):
        sub_id = self.subscribe().json()['id']

        response = self.client.post(self.confirm_url, {'id': sub_id, 'code': self.wrong_code()})

        self.assertEqual(response.status_code, 400)
        self.assertEqual(response.json()['reason'], 'wrong')
        self.assertEqual(response.json()['attempts_left'], CODE_MAX_ATTEMPTS - 1)
        self.assertFalse(VacancySubscription.objects.get(pk=sub_id).is_active)

    def test_too_many_wrong_codes_lock_even_the_right_one(self):
        sub_id = self.subscribe().json()['id']
        for _ in range(CODE_MAX_ATTEMPTS):
            self.client.post(self.confirm_url, {'id': sub_id, 'code': self.wrong_code()})

        response = self.client.post(self.confirm_url, {'id': sub_id, 'code': self.last_code()})

        self.assertEqual(response.status_code, 429)
        self.assertFalse(VacancySubscription.objects.get(pk=sub_id).email_verified)

    def test_expired_code_is_rejected(self):
        sub_id = self.subscribe().json()['id']
        VacancySubscription.objects.filter(pk=sub_id).update(code_sent_at=timezone.now() - CODE_TTL - timedelta(seconds=1))

        response = self.client.post(self.confirm_url, {'id': sub_id, 'code': self.last_code()})

        self.assertEqual(response.status_code, 400)
        self.assertEqual(response.json()['reason'], 'expired')

    def test_resend_is_throttled_then_replaces_the_code(self):
        sub_id = self.subscribe().json()['id']
        old_code = self.last_code()

        too_early = self.client.post(self.resend_url, {'id': sub_id})
        self.assertEqual(too_early.status_code, 429)
        self.assertEqual(len(mail.outbox), 1)

        VacancySubscription.objects.filter(pk=sub_id).update(
            code_sent_at=timezone.now() - CODE_RESEND_COOLDOWN - timedelta(seconds=1),
        )
        resent = self.client.post(self.resend_url, {'id': sub_id})
        self.assertEqual(resent.status_code, 200)
        self.assertEqual(len(mail.outbox), 2)

        new_code = self.last_code()
        if new_code != old_code:
            rejected = self.client.post(self.confirm_url, {'id': sub_id, 'code': old_code})
            self.assertEqual(rejected.status_code, 400)
        self.assertEqual(self.client.post(self.confirm_url, {'id': sub_id, 'code': new_code}).status_code, 200)

    def test_repeated_subscribe_is_throttled_by_email(self):
        self.subscribe()

        response = self.subscribe()

        self.assertEqual(response.status_code, 429)
        self.assertEqual(len(mail.outbox), 1)
        self.assertEqual(VacancySubscription.objects.count(), 1)

    def test_new_request_replaces_stale_pending_one(self):
        first_id = self.subscribe().json()['id']
        VacancySubscription.objects.filter(pk=first_id).update(
            code_sent_at=timezone.now() - CODE_RESEND_COOLDOWN - timedelta(seconds=1),
        )

        second_id = self.subscribe().json()['id']

        self.assertNotEqual(first_id, second_id)
        self.assertEqual(VacancySubscription.objects.count(), 1)

    def test_confirmed_subscription_cannot_be_confirmed_again(self):
        sub_id = self.subscribe().json()['id']
        self.client.post(self.confirm_url, {'id': sub_id, 'code': self.last_code()})

        response = self.client.post(self.confirm_url, {'id': sub_id, 'code': self.last_code()})

        self.assertEqual(response.status_code, 404)

    def test_resume_is_mailed_to_recipients_only_after_confirmation(self):
        ApplicationRecipient.objects.create(email='hr@example.com', receives_vacancies=True)
        sub_id = self.subscribe(about='Опыт 5 лет').json()['id']
        self.assertEqual([m.to for m in mail.outbox], [['ivan@example.com']])

        self.client.post(self.confirm_url, {'id': sub_id, 'code': self.last_code()})

        self.assertEqual(len(mail.outbox), 2)
        self.assertEqual(mail.outbox[1].to, ['hr@example.com'])

    def test_invalid_email_is_rejected_without_mail(self):
        response = self.subscribe(email='not-an-email')

        self.assertEqual(response.status_code, 400)
        self.assertEqual(len(mail.outbox), 0)
        self.assertEqual(VacancySubscription.objects.count(), 0)

    def test_logged_in_admin_can_subscribe_without_csrf_token(self):
        """У вошедшего в админку cookie сессии общая на весь домен: публичное API не должно требовать CSRF."""
        user = get_user_model().objects.create_user('admin', password='x', is_staff=True, is_superuser=True)
        client = Client(enforce_csrf_checks=True)
        client.force_login(user)

        response = client.post(self.subscribe_url, {'name': 'Иван', 'email': 'ivan@example.com', 'branch': ''})

        self.assertEqual(response.status_code, 201)


class FeedbackEmailConfirmationTests(TestCase):
    """Сообщение из формы обратной связи уходит команде портала только после ввода кода из письма."""

    submit_url = '/api/submit-feedback/'
    confirm_url = '/api/submit-feedback/confirm/'
    resend_url = '/api/submit-feedback/resend/'

    def submit(self, email='ivan@example.com', message='Не открывается раздел'):
        return self.client.post(self.submit_url, {'message': message, 'email': email})

    def last_code(self):
        return re.search(r'\b(\d{6})\b', mail.outbox[-1].body).group(1)

    def test_email_is_required(self):
        response = self.client.post(self.submit_url, {'message': 'Привет'})

        self.assertEqual(response.status_code, 400)
        self.assertIn('email', response.json())
        self.assertEqual(Feedback.objects.count(), 0)

    def test_submit_sends_code_but_not_the_message(self):
        ApplicationRecipient.objects.create(email='team@example.com', receives_feedback=True)

        response = self.submit()

        self.assertEqual(response.status_code, 201)
        self.assertEqual([m.to for m in mail.outbox], [['ivan@example.com']])
        feedback = Feedback.objects.get()
        self.assertFalse(feedback.email_verified)
        self.assertNotIn('code_hash', response.json())

    def test_correct_code_delivers_message_with_reply_to(self):
        ApplicationRecipient.objects.create(email='team@example.com', receives_feedback=True)
        feedback_id = self.submit().json()['id']

        response = self.client.post(self.confirm_url, {'id': feedback_id, 'code': self.last_code()})

        self.assertEqual(response.status_code, 200)
        self.assertTrue(Feedback.objects.get(pk=feedback_id).email_verified)
        self.assertEqual(len(mail.outbox), 2)
        team_mail = mail.outbox[1]
        self.assertEqual(team_mail.to, ['team@example.com'])
        self.assertEqual(team_mail.reply_to, ['ivan@example.com'])
        self.assertIn('ivan@example.com', team_mail.body)
        self.assertIn('feedback_cooldown', response.cookies)

    def test_wrong_code_does_not_deliver(self):
        ApplicationRecipient.objects.create(email='team@example.com', receives_feedback=True)
        feedback_id = self.submit().json()['id']
        wrong = '000000' if self.last_code() != '000000' else '111111'

        response = self.client.post(self.confirm_url, {'id': feedback_id, 'code': wrong})

        self.assertEqual(response.status_code, 400)
        self.assertEqual(len(mail.outbox), 1)
        self.assertFalse(Feedback.objects.get(pk=feedback_id).email_verified)

    def test_code_from_subscription_does_not_work_for_feedback(self):
        """Хэш кода привязан к модели: код подписки с тем же номером записи не подходит."""
        feedback_id = self.submit().json()['id']
        code = self.last_code()
        VacancySubscription.objects.create(pk=feedback_id, email='ivan@example.com', is_active=False)

        response = self.client.post('/api/vacancy-subscribe/confirm/', {'id': feedback_id, 'code': code})

        self.assertEqual(response.status_code, 400)

    def test_resend_is_throttled(self):
        feedback_id = self.submit().json()['id']

        response = self.client.post(self.resend_url, {'id': feedback_id})

        self.assertEqual(response.status_code, 429)
        self.assertEqual(len(mail.outbox), 1)
