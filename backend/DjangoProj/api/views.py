import logging
import time
from datetime import timedelta
from rest_framework.decorators import api_view, parser_classes
from rest_framework.parsers import MultiPartParser, FormParser
from rest_framework.response import Response
from rest_framework import status
from django.conf import settings
from django.shortcuts import get_object_or_404, render
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_http_methods
from django.db.models import Q
from django.utils import timezone

from .models import (
    Tender, Vacancy, StaffMember, RequiredExperience, JobType,
    AntiCorruptionDocument, AntiCorruptionDocumentCategory, AntiCorruptionInfo, CorruptionReport, BranchesGlobal, Feedback, VacancySubscription,
    Competition, CompetitionResult, StaffReserveInfo, StaffReserveDocument, VacancyDocument, WorkPartner, YouthInfo, PracticeApplication,
    TrainingEvent, TrainingFeedback, NewsPost, Department, Deputy, CompetitionDocument,
)
from .education import build_education_payload
from .search import search_portal
from .notifications import (
    CODE_MAX_ATTEMPTS, CODE_MAX_SENDS, CODE_OK, CODE_EXPIRED, CODE_LOCKED, CODE_TTL, check_subscription_code,
    seconds_until_resend, send_subscription_code, email_from_unsubscribe_token, notify_recipients, KIND_VACANCIES, KIND_RESERVE, KIND_PRACTICE, KIND_TRAINING, KIND_FEEDBACK,
)
from .serializers import (
    TenderSerializer, VacancySerializer, StaffMemberSerializer,
    JobApplicationSerializer,
    RequiredExperienceSerializer, JobTypeSerializer,
    AntiCorruptionDocumentSerializer, AntiCorruptionDocumentCategorySerializer, AntiCorruptionInfoSerializer, CorruptionReportSerializer,
    BranchesGlobalSerializer, WorkPartnerSerializer, FeedbackSerializer, VacancySubscriptionSerializer,
    CompetitionSerializer, CompetitionResultSerializer, StaffReserveInfoSerializer, StaffReserveDocumentSerializer, VacancyDocumentSerializer,
    YouthInfoSerializer, PracticeApplicationSerializer,
    TrainingEventSerializer, TrainingFeedbackSerializer, NewsPostSerializer,
    DepartmentSerializer, DeputySerializer, CompetitionDocumentSerializer,
)

logger = logging.getLogger(__name__)


@api_view(['GET'])
def hello(request):
    return Response({"message": "Hello from Django!"})

@api_view(['GET'])
def portal_search(request):
    query = (request.query_params.get('q') or '').strip()
    try:
        limit = max(1, min(int(request.query_params.get('limit', 6)), 100))
    except ValueError:
        limit = 6
    return Response(search_portal(request, query, limit))


@api_view(['GET'])
def tenders(request):
    items = Tender.objects.filter(is_active=True)
    serializer = TenderSerializer(items, many=True, context={'request': request})
    return Response(serializer.data)


@api_view(['GET'])
def competitions(request):
    items = Competition.objects.filter(is_active=True)
    competition_type = request.query_params.get('type')
    if competition_type in ('vacancy', 'reserve'):
        items = items.filter(competition_type=competition_type)
    serializer = CompetitionSerializer(items, many=True, context={'request': request})
    return Response(serializer.data)


@api_view(['GET'])
def staff_reserve_info(request):
    info = StaffReserveInfo.get_solo()
    serializer = StaffReserveInfoSerializer(info)
    return Response(serializer.data)


@api_view(['GET'])
def staff_reserve_documents(request):
    items = StaffReserveDocument.objects.filter(is_active=True)
    serializer = StaffReserveDocumentSerializer(items, many=True, context={'request': request})
    return Response(serializer.data)


@api_view(['GET'])
def vacancy_documents(request):
    items = VacancyDocument.objects.filter(is_active=True)
    serializer = VacancyDocumentSerializer(items, many=True, context={'request': request})
    return Response(serializer.data)


@api_view(['GET'])
def youth_info(request):
    info = YouthInfo.get_solo()
    serializer = YouthInfoSerializer(info)
    return Response(serializer.data)


@api_view(['POST'])
@parser_classes([MultiPartParser, FormParser])
def submit_practice_application(request):
    serializer = PracticeApplicationSerializer(data=request.data)
    if serializer.is_valid():
        serializer.save()
        app = serializer.instance
        notify_recipients(
            KIND_PRACTICE,
            f'Заявка на практику: {app.last_name} {app.first_name}',
            [
                ('ФИО', ' '.join(filter(None, [app.last_name, app.first_name, app.middle_name]))),
                ('Дата рождения', app.birth_date),
                ('Телефон', app.phone),
                ('Email', app.email),
                ('Учебное заведение', app.educational_institution),
                ('Курс', app.course),
                ('Специальность', app.specialty),
                ('Желаемый период практики', app.practice_period),
                ('Желаемый орган', app.preferred_department),
                ('Комментарий', app.comment),
            ],
            files=[app.application_letter],
        )
        return Response(
            {
                'message': 'Заявка на практику успешно отправлена!',
                'id': serializer.instance.id,
            },
            status=status.HTTP_201_CREATED,
        )
    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


@api_view(['GET'])
def news_posts(request):
    items = NewsPost.objects.filter(is_published=True, show_on_main=True)
    serializer = NewsPostSerializer(items, many=True, context={'request': request})
    return Response(serializer.data)


@api_view(['GET'])
def news_post_detail(request, pk: int):
    try:
        item = NewsPost.objects.get(pk=pk, is_published=True)
    except NewsPost.DoesNotExist:
        return Response({'error': 'News post not found'}, status=status.HTTP_404_NOT_FOUND)

    serializer = NewsPostSerializer(item, context={'request': request})
    return Response(serializer.data)


@api_view(['GET'])
def training_events(request):
    items = TrainingEvent.objects.filter(is_published=True)
    event_type = request.query_params.get('type')
    if event_type in dict(TrainingEvent.TYPE_CHOICES):
        items = items.filter(event_type=event_type)
    serializer = TrainingEventSerializer(items, many=True)
    return Response(serializer.data)


@api_view(['GET'])
def training_event_detail(request, pk: int):
    try:
        item = TrainingEvent.objects.get(pk=pk, is_published=True)
    except TrainingEvent.DoesNotExist:
        return Response({'error': 'Training event not found'}, status=status.HTTP_404_NOT_FOUND)

    serializer = TrainingEventSerializer(item)
    return Response(serializer.data)


@api_view(['POST'])
def submit_training_feedback(request):
    cooldown_seconds = 60

    last_submit = request.COOKIES.get('training_feedback_cooldown')
    if last_submit:
        try:
            last_time = float(last_submit)
            if time.time() - last_time < cooldown_seconds:
                remaining = int(cooldown_seconds - (time.time() - last_time))
                return Response(
                    {'error': f'Слишком частая отправка. Подождите {remaining} сек.'},
                    status=status.HTTP_429_TOO_MANY_REQUESTS,
                )
        except ValueError:
            pass

    serializer = TrainingFeedbackSerializer(data=request.data)
    if serializer.is_valid():
        instance = serializer.save()
        notify_recipients(
            KIND_TRAINING,
            'Предложение по обучению',
            [
                ('Имя', instance.name or 'Анонимно'),
                ('Подразделение', instance.department),
                ('Предложение', instance.message),
            ],
        )
        response = Response(
            {'message': 'Спасибо! Ваше предложение отправлено.', 'id': instance.id},
            status=status.HTTP_201_CREATED,
        )
        response.set_cookie(
            'training_feedback_cooldown',
            str(time.time()),
            max_age=cooldown_seconds,
            httponly=True,
            samesite='Lax',
        )
        return response
    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


@api_view(['GET'])
def competition_documents(request):
    items = CompetitionDocument.objects.filter(is_active=True)
    competition_type = request.query_params.get('type')
    if competition_type in (Competition.TYPE_VACANCY, Competition.TYPE_RESERVE):
        items = items.filter(competition_type=competition_type)
    serializer = CompetitionDocumentSerializer(items, many=True, context={'request': request})
    return Response(serializer.data)


@api_view(['GET'])
def competition_results(request):
    items = CompetitionResult.objects.prefetch_related('winners')
    competition_type = request.query_params.get('type')
    if competition_type in (Competition.TYPE_VACANCY, Competition.TYPE_RESERVE):
        items = items.filter(competition_type=competition_type)
    serializer = CompetitionResultSerializer(items, many=True, context={'request': request})
    return Response(serializer.data)


@api_view(['GET'])
def staff_members(request):
    if request.query_params.get('management_head'):
        items = StaffMember.objects.filter(is_management_head=True, is_active=True)
        serializer = StaffMemberSerializer(items, many=True, context={'request': request})
        return Response(serializer.data)

    if request.query_params.get('reserve'):
        items = StaffMember.objects.filter(show_on_reserve=True)
    else:
        items = StaffMember.objects.filter(is_active=True, show_on_reserve=False)
        if request.query_params.get('honorboard'):
            items = items.filter(show_on_honorboard=True)
        if request.query_params.get('contacts'):
            items = items.filter(show_on_contacts=True, is_management_head=False)

    serializer = StaffMemberSerializer(items, many=True, context={'request': request})
    return Response(serializer.data)


@api_view(['GET'])
def vacancies(request):
    items = Vacancy.objects.filter(is_active=True)

    required_experience = request.query_params.get('required_experience')
    if required_experience:
        items = items.filter(required_experience_id=required_experience)

    job_type = request.query_params.get('job_type')
    if job_type:
        items = items.filter(job_type_id=job_type)

    branch = request.query_params.get('branch') or request.query_params.get('org')
    if branch:
        branch = branch.strip()
        items = items.filter(branch__iexact=branch)

    serializer = VacancySerializer(items, many=True)
    return Response(serializer.data)


@api_view(['GET'])
def vacancy_detail(request, pk):
    vacancy = get_object_or_404(Vacancy, pk=pk, is_active=True)
    serializer = VacancySerializer(vacancy)
    return Response(serializer.data)


@api_view(['GET'])
def vacancy_filters(request, field_name):
    model_map = {
        'required_experience': (RequiredExperience, RequiredExperienceSerializer),
        'job_type': (JobType, JobTypeSerializer),
    }

    entry = model_map.get(field_name)
    if entry is None:
        return Response({'error': f'Unknown filter field: {field_name}'}, status=404)

    model_cls, serializer_cls = entry
    items = model_cls.objects.all()
    serializer = serializer_cls(items, many=True)
    return Response(serializer.data)


@api_view(['POST'])
@parser_classes([MultiPartParser, FormParser])
def apply(request):
    serializer = JobApplicationSerializer(data=request.data)
    if serializer.is_valid():
        serializer.save()
        app = serializer.instance
        kind = KIND_RESERVE if 'резерв' in (app.vacancy_title or '').lower() else KIND_VACANCIES
        subject = f'Заявка на вакансию: {app.last_name} {app.first_name}'
        if app.vacancy_title:
            subject += f' — {app.vacancy_title}'
        notify_recipients(
            kind,
            subject,
            [
                ('Вакансия', app.vacancy_title),
                ('ФИО', ' '.join(filter(None, [app.last_name, app.first_name, app.middle_name]))),
                ('Дата рождения', app.birth_date),
                ('Телефон', app.phone),
                ('Email', app.email),
                ('Образование', app.education),
                ('Специальность', app.specialty),
                ('Стаж муниципальной службы', app.municipal_experience),
                ('Трудовая деятельность', app.work_experience),
                ('Откуда узнал(а)', app.vacancy_source),
            ],
            files=[app.resume, app.photo],
        )
        return Response(
            {"message": "Заявка успешно отправлена!", "id": serializer.instance.id},
            status=status.HTTP_201_CREATED
        )
    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


def _notify_subscription_resume(sub):
    """Копия резюме из подписки — уполномоченным лицам (после подтверждения email)."""
    has_resume = bool(
        sub.resume or sub.desired_position or sub.education or sub.work_experience or sub.about
    )
    if not has_resume:
        return
    notify_recipients(
        KIND_VACANCIES,
        f'Резюме из подписки на вакансии: {sub.name or sub.email}',
        [
            ('Имя', sub.name),
            ('Email', sub.email),
            ('Телефон', sub.phone),
            ('Отраслевой орган', sub.branch or 'любой'),
            ('Желаемая должность', sub.desired_position),
            ('Образование', sub.education),
            ('Опыт работы', sub.work_experience),
            ('О себе, навыки', sub.about),
        ],
        files=[sub.resume],
    )


def _code_sent_payload(sub):
    return {
        'id': sub.pk,
        'email': sub.email,
        'expires_in': int(CODE_TTL.total_seconds()),
        'resend_after': seconds_until_resend(sub),
    }


def _pending_subscription(pk):
    """Неподтверждённая подписка по id или None."""
    try:
        return VacancySubscription.objects.filter(pk=int(pk), email_verified=False).first()
    except (TypeError, ValueError):
        return None


@api_view(['POST'])
def vacancy_subscribe(request):
    """Шаг 1: сохранить заявку на подписку (неактивной) и отправить на email код подтверждения."""
    serializer = VacancySubscriptionSerializer(data=request.data)
    if not serializer.is_valid():
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    email = serializer.validated_data['email']
    pending = VacancySubscription.objects.filter(email__iexact=email, email_verified=False)
    last = pending.exclude(code_sent_at=None).order_by('-code_sent_at').first()
    if last and seconds_until_resend(last):
        wait = seconds_until_resend(last)
        return Response(
            {'detail': f'Код уже отправлен. Повторно запросить его можно через {wait} с.', 'resend_after': wait},
            status=status.HTTP_429_TOO_MANY_REQUESTS,
        )

    # Прошлые неподтверждённые заявки с этим адресом и просроченные чужие — мусор, убираем
    stale = timezone.now() - timedelta(days=1)
    VacancySubscription.objects.filter(email_verified=False).filter(
        Q(email__iexact=email) | Q(created_at__lt=stale)
    ).delete()

    sub = serializer.save(is_active=False, email_verified=False)
    try:
        send_subscription_code(sub)
    except Exception:
        logger.exception('Не удалось отправить код подтверждения подписки на %s', email)
        sub.delete()
        return Response(
            {'detail': 'Не удалось отправить письмо с кодом. Проверьте адрес и попробуйте позже.'},
            status=status.HTTP_503_SERVICE_UNAVAILABLE,
        )
    return Response(
        {**_code_sent_payload(sub), 'message': f'Код подтверждения отправлен на {sub.email}.'},
        status=status.HTTP_201_CREATED,
    )


@api_view(['POST'])
def vacancy_subscribe_confirm(request):
    """Шаг 2: проверить код из письма и включить подписку."""
    sub = _pending_subscription(request.data.get('id'))
    if not sub:
        return Response(
            {'detail': 'Заявка не найдена или уже подтверждена. Оформите подписку заново.'},
            status=status.HTTP_404_NOT_FOUND,
        )
    result = check_subscription_code(sub, request.data.get('code'))
    if result == CODE_OK:
        sub.email_verified = True
        sub.is_active = True
        sub.code_hash = ''
        sub.save(update_fields=['email_verified', 'is_active', 'code_hash'])
        _notify_subscription_resume(sub)
        return Response({
            'message': 'Подписка оформлена. Уведомления о новых вакансиях будут приходить на указанный email.',
            'id': sub.pk,
        })
    if result == CODE_EXPIRED:
        return Response(
            {'detail': 'Срок действия кода истёк. Запросите новый код.', 'reason': 'expired'},
            status=status.HTTP_400_BAD_REQUEST,
        )
    if result == CODE_LOCKED:
        return Response(
            {'detail': 'Слишком много неверных попыток. Запросите новый код.', 'reason': 'locked'},
            status=status.HTTP_429_TOO_MANY_REQUESTS,
        )
    return Response(
        {
            'detail': 'Неверный код. Проверьте письмо и попробуйте ещё раз.',
            'reason': 'wrong',
            'attempts_left': CODE_MAX_ATTEMPTS - sub.code_attempts,
        },
        status=status.HTTP_400_BAD_REQUEST,
    )


@api_view(['POST'])
def vacancy_subscribe_resend(request):
    """Отправить код подтверждения ещё раз (не чаще раза в минуту и не больше пяти раз)."""
    sub = _pending_subscription(request.data.get('id'))
    if not sub:
        return Response(
            {'detail': 'Заявка не найдена или уже подтверждена. Оформите подписку заново.'},
            status=status.HTTP_404_NOT_FOUND,
        )
    wait = seconds_until_resend(sub)
    if wait:
        return Response(
            {'detail': f'Повторно запросить код можно через {wait} с.', 'resend_after': wait},
            status=status.HTTP_429_TOO_MANY_REQUESTS,
        )
    if sub.code_sends >= CODE_MAX_SENDS:
        return Response(
            {'detail': 'Лимит отправки кодов исчерпан. Оформите подписку заново позже.', 'reason': 'limit'},
            status=status.HTTP_429_TOO_MANY_REQUESTS,
        )
    try:
        send_subscription_code(sub)
    except Exception:
        logger.exception('Не удалось повторно отправить код подтверждения на %s', sub.email)
        return Response(
            {'detail': 'Не удалось отправить письмо с кодом. Попробуйте позже.'},
            status=status.HTTP_503_SERVICE_UNAVAILABLE,
        )
    return Response({**_code_sent_payload(sub), 'message': f'Новый код отправлен на {sub.email}.'})


@csrf_exempt  # токен в ссылке подписан, а почтовые клиенты шлют одношаговую отписку POST-ом без cookie
@require_http_methods(['GET', 'POST'])
def vacancy_unsubscribe(request, token):
    email = email_from_unsubscribe_token(token)
    context = {'site_url': settings.SITE_URL.rstrip('/'), 'email': email}
    if not email:
        context['state'] = 'invalid'
        return render(request, 'api/unsubscribe.html', context, status=400)
    if request.method == 'POST':
        VacancySubscription.objects.filter(email__iexact=email).update(is_active=False)
        context['state'] = 'done'
    else:
        context['state'] = 'confirm'
    return render(request, 'api/unsubscribe.html', context)


@api_view(['GET'])
def anti_corruption_info(request):
    info = AntiCorruptionInfo.get_solo()
    serializer = AntiCorruptionInfoSerializer(info)
    return Response(serializer.data)


@api_view(['GET'])
def anti_corruption_education(request):
    return Response(build_education_payload())


@api_view(['GET'])
def anti_corruption_documents(request):
    from django.db.models import Prefetch

    categories = AntiCorruptionDocumentCategory.objects.prefetch_related(
        Prefetch(
            'documents',
            queryset=AntiCorruptionDocument.objects.order_by('-created_at'),
        ),
    ).order_by('order', 'tab_label')
    serializer = AntiCorruptionDocumentCategorySerializer(
        categories,
        many=True,
        context={'request': request},
    )
    return Response(serializer.data)


@api_view(['POST'])
@parser_classes([MultiPartParser, FormParser])
def submit_corruption_report(request):
    cooldown_seconds = 60

    last_submit = request.COOKIES.get('corruption_cooldown')
    if last_submit:
        try:
            last_time = float(last_submit)
            if time.time() - last_time < cooldown_seconds:
                remaining = int(cooldown_seconds - (time.time() - last_time))
                return Response(
                    {'error': f'Слишком частая отправка. Подождите {remaining} сек.'},
                    status=status.HTTP_429_TOO_MANY_REQUESTS
                )
        except ValueError:
            pass

    serializer = CorruptionReportSerializer(data=request.data)
    if serializer.is_valid():
        serializer.save()
        response = Response(
            {"message": "Сообщение успешно отправлено!", "id": serializer.instance.id},
            status=status.HTTP_201_CREATED
        )
        response.set_cookie(
            'corruption_cooldown',
            str(time.time()),
            max_age=cooldown_seconds,
            httponly=True,
            samesite='Lax'
        )
        return response
    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


@api_view(['GET'])
def branches_global(request):
    items = BranchesGlobal.objects.all()
    serializer = BranchesGlobalSerializer(items, many=True)
    return Response(serializer.data)


@api_view(['GET'])
def work_partners(request):
    items = WorkPartner.objects.filter(is_active=True)
    serializer = WorkPartnerSerializer(items, many=True, context={'request': request})
    return Response(serializer.data)


@api_view(['GET'])
def departments(request):
    items = Department.objects.filter(is_published=True)
    serializer = DepartmentSerializer(items, many=True, context={'request': request})
    return Response(serializer.data)


@api_view(['GET'])
def department_detail(request, slug):
    item = get_object_or_404(Department, slug=slug, is_published=True)
    serializer = DepartmentSerializer(item, context={'request': request})
    return Response(serializer.data)


@api_view(['GET'])
def deputies(request):
    items = Deputy.objects.filter(is_published=True).prefetch_related(
        'deputy_departments__department'
    )
    serializer = DeputySerializer(items, many=True, context={'request': request})
    return Response(serializer.data)


@api_view(['POST'])
@parser_classes([MultiPartParser, FormParser])
def submit_feedback(request):
    cooldown_seconds = 60

    last_submit = request.COOKIES.get('feedback_cooldown')
    if last_submit:
        try:
            last_time = float(last_submit)
            if time.time() - last_time < cooldown_seconds:
                remaining = int(cooldown_seconds - (time.time() - last_time))
                return Response(
                    {'error': f'Слишком частая отправка. Подождите {remaining} сек.'},
                    status=status.HTTP_429_TOO_MANY_REQUESTS
                )
        except ValueError:
            pass

    serializer = FeedbackSerializer(data=request.data)
    if serializer.is_valid():
        instance = serializer.save()
        notify_recipients(
            KIND_FEEDBACK,
            'Обратная связь с портала',
            [('Сообщение', instance.message)],
            files=[instance.photo],
        )

        response = Response(
            {"message": "Сообщение отправлено!", "id": instance.id},
            status=status.HTTP_201_CREATED
        )
        response.set_cookie(
            'feedback_cooldown',
            str(time.time()),
            max_age=cooldown_seconds,
            httponly=True,
            samesite='Lax'
        )
        return response
    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)