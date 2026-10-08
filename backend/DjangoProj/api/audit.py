"""Журнал доступа к персональным данным (модель PersonalDataAccessLog).

Что фиксируем:
  * просмотр списков и карточек заявок в админке, их создание, изменение и удаление (PersonalDataAuditMixin);
  * скачивание файлов с ПД (api/media.py);
  * получение данных с сайта (формы) и передачу копий заявок по почте;
  * вход, неудачный вход и выход из админки.

Данные из самих записей в журнал не попадают: только тип записи, её номер и служебные сведения
(имя скачанного файла может содержать ФИО, поэтому доступ к журналу ограничен суперпользователями).
Ошибка записи в журнал никогда не ломает основное действие: она пишется в обычный лог.
"""
import ipaddress
import logging

from django.contrib.auth.signals import user_logged_in, user_logged_out, user_login_failed
from django.dispatch import receiver

logger = logging.getLogger(__name__)


def client_ip(request):
    """IP посетителя. За nginx адрес берётся из X-Real-IP, но только если запрос пришёл с самого сервера."""
    if request is None:
        return None
    remote = request.META.get('REMOTE_ADDR') or ''
    candidate = remote
    try:
        if ipaddress.ip_address(remote).is_loopback:
            candidate = (request.META.get('HTTP_X_REAL_IP') or remote).strip()
        ipaddress.ip_address(candidate)
    except ValueError:
        return None
    return candidate


def log_event(action, request=None, *, user=None, username='', model=None, object_type='', object_id='', details=''):
    """Записать событие в журнал. model — класс или экземпляр модели; из него берётся название раздела."""
    try:
        from .models import PersonalDataAccessLog

        if user is None and request is not None:
            candidate = getattr(request, 'user', None)
            if candidate is not None and candidate.is_authenticated:
                user = candidate
        if model is not None and not object_type:
            object_type = str(model._meta.verbose_name)
        if user is not None and not username:
            username = user.get_username()

        PersonalDataAccessLog.objects.create(
            action=action,
            user=user if user is not None and user.pk else None,
            username=(username or '')[:150],
            object_type=(object_type or '')[:120],
            object_id=str(object_id or '')[:64],
            ip_address=client_ip(request),
            user_agent=((request.META.get('HTTP_USER_AGENT') or '')[:255] if request is not None else ''),
            details=(details or '')[:500],
        )
    except Exception:
        logger.exception('Не удалось записать событие в журнал доступа к ПД (%s)', action)


class PersonalDataAuditMixin:
    """Миксин для ModelAdmin моделей с ПД: журналирует просмотр, создание, изменение и удаление записей."""

    def changelist_view(self, request, extra_context=None):
        response = super().changelist_view(request, extra_context)
        if request.method == 'GET' and response.status_code == 200 and self.has_view_or_change_permission(request):
            # Значения поиска и фильтров могут содержать ПД, поэтому пишем только имена параметров
            params = ', '.join(sorted(request.GET.keys()))
            log_event(
                'list', request, model=self.model,
                details=f'параметры: {params}' if params else '',
            )
        return response

    def changeform_view(self, request, object_id=None, form_url='', extra_context=None):
        response = super().changeform_view(request, object_id, form_url, extra_context)
        if object_id and request.method == 'GET' and response.status_code == 200:
            log_event('view', request, model=self.model, object_id=object_id)
        return response

    def log_addition(self, request, obj, message):
        log_event('add', request, model=obj, object_id=obj.pk)
        return super().log_addition(request, obj, message)

    def log_change(self, request, obj, message):
        log_event('change', request, model=obj, object_id=obj.pk)
        return super().log_change(request, obj, message)

    def log_deletions(self, request, queryset):
        for obj in queryset:
            log_event('delete', request, model=obj, object_id=obj.pk)
        return super().log_deletions(request, queryset)


@receiver(user_logged_in)
def _log_login(sender, request, user, **kwargs):
    log_event('login', request, user=user)


@receiver(user_logged_out)
def _log_logout(sender, request, user, **kwargs):
    if user is not None:
        log_event('logout', request, user=user)


@receiver(user_login_failed)
def _log_login_failed(sender, credentials, request=None, **kwargs):
    # Пароль в журнал не попадает; логин пишем как есть, он нужен для разбора подбора пароля
    log_event('login_failed', request, username=str(credentials.get('username', '')))
