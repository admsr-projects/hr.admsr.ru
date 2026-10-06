"""Поиск по всему порталу: вакансии, новости, мероприятия, конкурсы, документы, структура, контакты."""
from .models import (
    AntiCorruptionDocument, Competition, CompetitionDocument, CompetitionResult, Department, Deputy,
    EducationPosition, NewsPost, StaffMember, StaffReserveDocument, StaffReservePosition, Tender, TrainingEvent, Vacancy,
    VacancyDocument,
)

MIN_QUERY_LENGTH = 2
RESULT_KEYS = ('vacancies', 'news', 'events', 'competitions', 'documents', 'structure', 'contacts')


def _tokens(query: str) -> list[str]:
    return [token for token in query.casefold().split() if token]


def _matches(values, tokens: list[str]) -> bool:
    """Все слова запроса встречаются в тексте полей (регистр не важен, в том числе для кириллицы)."""
    text = ' '.join(str(value) for value in values if value).casefold()
    return all(token in text for token in tokens)


def _collect(queryset, tokens, limit, fields, build):
    """
    Перебираем записи в Python, а не через icontains: SQLite не различает регистр кириллицы,
    а таблицы портала небольшие.
    """
    found = []
    for obj in queryset:
        if _matches([getattr(obj, field) for field in fields], tokens):
            found.append(build(obj))
            if len(found) >= limit:
                break
    return found


def _file_url(request, field_file):
    return request.build_absolute_uri(field_file.url) if field_file else ''


def _documents(request, tokens, limit):
    docs = []

    def add(queryset, section, anchor, file_field='file'):
        docs.extend(_collect(
            queryset, tokens, limit, ['name'],
            lambda obj: {
                'title': obj.name,
                'section': section,
                'to': _file_url(request, getattr(obj, file_field)) or anchor,
                'page': anchor,
                'file': bool(getattr(obj, file_field)),
            },
        ))

    add(Tender.objects.filter(is_active=True), 'Конкурсы — документы', '/tenders#competition-rules', file_field='link')
    add(CompetitionDocument.objects.filter(is_active=True), 'Конкурсы — нормативные документы', '/tenders#active-competitions')
    add(VacancyDocument.objects.filter(is_active=True), 'Вакансии — документы', '/vacancies#vacancies-documents')
    add(StaffReserveDocument.objects.filter(is_active=True), 'Кадровый резерв — документы', '/staffreserve#reserve-documents')
    add(AntiCorruptionDocument.objects.all(), 'Нет коррупции! — документы', '/anti-corruption#anticorruption-documents')

    for result in CompetitionResult.objects.all():
        if not _matches([result.title], tokens):
            continue
        for label, field in (
            ('постановление о проведении', result.decree_conduct),
            ('постановление о результатах', result.decree_results),
        ):
            if field:
                docs.append({
                    'title': f'{result.title} — {label}',
                    'section': 'Конкурсы — результаты',
                    'to': _file_url(request, field),
                    'page': '/tenders#competition-results',
                    'file': True,
                })

    for position in EducationPosition.objects.filter(is_published=True):
        if _matches([position.title, position.key_quote, position.facts_summary, position.legal_basis], tokens):
            docs.append({
                'title': f'№ {position.number}. {position.title}',
                'section': 'Антикоррупционное просвещение',
                'to': f'/anti-corruption/education/positions#pos-{position.number}',
                'page': '/anti-corruption/education/positions',
                'file': False,
            })

    return docs[:limit * 2]


def search_portal(request, query: str, limit: int = 6) -> dict:
    tokens = _tokens(query)
    if not tokens or len(query.strip()) < MIN_QUERY_LENGTH:
        return {key: [] for key in RESULT_KEYS}

    vacancies = _collect(
        Vacancy.objects.filter(is_active=True), tokens, limit,
        ['title', 'branch', 'location', 'description', 'skills'],
        lambda v: {'id': v.id, 'title': v.title, 'branch': v.branch},
    )

    news = _collect(
        NewsPost.objects.filter(is_published=True), tokens, limit,
        ['title', 'description', 'content'],
        lambda n: {'id': n.id, 'title': n.title, 'date': n.published_at.isoformat()},
    )

    events = _collect(
        TrainingEvent.objects.filter(is_published=True), tokens, limit,
        ['title', 'description', 'location'],
        lambda e: {'id': e.id, 'title': e.title, 'date': e.event_date.isoformat(), 'location': e.location},
    )

    competitions = _collect(
        Competition.objects.filter(is_active=True), tokens, limit,
        ['title', 'content', 'requirements', 'acceptance_info'],
        lambda c: {
            'title': c.title,
            'section': 'Действующий конкурс',
            'to': '/tenders#active-competitions',
        },
    )
    for result in CompetitionResult.objects.prefetch_related('winners'):
        if len(competitions) >= limit:
            break
        winners = [w.full_name for w in result.winners.all()]
        if _matches([result.title, *winners], tokens):
            competitions.append({
                'title': result.title,
                'section': 'Результаты конкурса',
                'to': '/tenders#competition-results',
            })

    structure = _collect(
        Department.objects.filter(is_published=True), tokens, limit,
        ['name', 'intro', 'about_paragraphs'],
        lambda d: {'title': d.name, 'section': 'Орган администрации', 'to': f'/about/departments/{d.slug}'},
    )
    structure += _collect(
        Deputy.objects.filter(is_published=True), tokens, limit,
        ['surname', 'name', 'patronymic', 'role'],
        lambda d: {'title': f'{d.surname} {d.name} {d.patronymic}', 'section': d.role, 'to': '/about/structure'},
    )
    structure += _collect(
        StaffReservePosition.objects.filter(is_active=True), tokens, limit,
        ['title', 'description'],
        lambda p: {'title': p.title, 'section': 'Кадровый резерв — должность', 'to': '/staffreserve#reserve-positions'},
    )
    structure = structure[:limit * 2]

    contacts = []
    for member in StaffMember.objects.filter(is_active=True):
        if not (member.show_on_contacts or member.show_on_honorboard):
            continue
        if _matches([member.surname, member.name, member.patronym, member.role, member.phone, member.email], tokens):
            contacts.append({
                'id': member.id,
                'surname': member.surname,
                'name': member.name,
                'patronym': member.patronym,
                'role': member.role,
                'phone': member.phone,
                'email': member.email,
                'to': '/contacts#contacts-directory' if member.show_on_contacts else '/honorboard',
            })
            if len(contacts) >= limit:
                break

    return {
        'vacancies': vacancies,
        'news': news,
        'events': events,
        'competitions': competitions,
        'documents': _documents(request, tokens, limit),
        'structure': structure,
        'contacts': contacts,
    }
