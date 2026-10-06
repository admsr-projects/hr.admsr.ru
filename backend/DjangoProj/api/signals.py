from django.db import transaction
from django.db.models.signals import post_save
from django.dispatch import receiver

from .models import Vacancy
from .notifications import notify_subscribers_in_background


@receiver(post_save, sender=Vacancy)
def mail_subscribers_about_new_vacancy(sender, instance, raw=False, **kwargs):
    """Активная вакансия, о которой подписчикам ещё не писали, уходит в рассылку после сохранения."""
    if raw or not instance.is_active or instance.subscribers_notified_at:
        return
    transaction.on_commit(lambda: notify_subscribers_in_background(instance.pk))
