"""Выдача загруженных файлов (/media/…).

Файлы из форм сайта (резюме, фото, вложения) содержат персональные данные, поэтому отдаются только
сотрудникам, вошедшим в админку и имеющим право просмотра соответствующих заявок; каждое скачивание
попадает в журнал доступа к ПД. Остальные каталоги публичны (документы и картинки сайта).
Каталог, которого нет ни в одном списке, считается закрытым и доступен только суперпользователю.
"""
import posixpath

from django.conf import settings
from django.http import Http404
from django.core.exceptions import PermissionDenied
from django.views.static import serve

from .audit import log_event

# Верхний каталог внутри MEDIA_ROOT → публичный
PUBLIC_DIRS = frozenset({
    'tenders', 'staff', 'partners', 'anti_corruption_docs', 'competitions',
    'staff_reserve', 'vacancies', 'departments', 'news',
})

# Верхний каталог с ПД → модель, право просмотра которой нужно для скачивания
PROTECTED_DIRS = {
    'resumes': 'jobapplication',
    'photos': 'jobapplication',
    'subscription_resumes': 'vacancysubscription',
    'practice_applications': 'practiceapplication',
    'feedback_photos': 'feedback',
}


def media_serve(request, path):
    normalized = posixpath.normpath(path.replace('\\', '/'))
    if normalized.startswith(('/', '..')) or normalized == '.':
        raise Http404
    top_dir = normalized.split('/', 1)[0]

    if top_dir in PUBLIC_DIRS:
        return serve(request, normalized, document_root=settings.MEDIA_ROOT)

    user = request.user
    # Посторонним не раскрываем, что файл существует
    if not (user.is_authenticated and user.is_active and user.is_staff):
        raise Http404
    model_name = PROTECTED_DIRS.get(top_dir)
    allowed = user.has_perm(f'api.view_{model_name}') if model_name else user.is_superuser
    if not allowed:
        raise PermissionDenied

    response = serve(request, normalized, document_root=settings.MEDIA_ROOT)
    if response.status_code in (200, 206):
        log_event(
            'download', request,
            object_type=f'Файл ({top_dir})',
            details=normalized,
        )
        response['Cache-Control'] = 'private, no-store'
    return response
