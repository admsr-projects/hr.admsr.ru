"""Данные страницы «Антикоррупционное просвещение» для API."""
import re

from .models import EducationCategory, EducationLegalAct, EducationPosition, EducationReviewPage

_BLANK_LINE = re.compile(r'\n\s*\n')
_NOTE_LINE = re.compile(r'^\s*(\d+)[.)]?\s+(.+)$')


def split_lines(value):
    return [line.strip() for line in (value or '').splitlines() if line.strip()]


def split_paragraphs(value):
    text = (value or '').replace('\r\n', '\n')
    return [part.strip() for part in _BLANK_LINE.split(text) if part.strip()]


def parse_notes(value):
    notes = []
    for index, line in enumerate(split_lines(value), start=1):
        match = _NOTE_LINE.match(line)
        if match:
            notes.append({'n': int(match.group(1)), 'text': match.group(2).strip()})
        else:
            notes.append({'n': index, 'text': line})
    return notes


def resolve_act(tag, abbreviations):
    """Нормативный акт нормы: самое длинное сокращение, встречающееся в тексте нормы."""
    best = ''
    for abbr in abbreviations:
        if len(abbr) > len(best) and re.search(r'(?<![\w-])' + re.escape(abbr) + r'(?!\d)', tag):
            best = abbr
    return best or tag


def build_education_payload():
    page = EducationReviewPage.get_solo()
    categories = list(EducationCategory.objects.all())
    acts = list(EducationLegalAct.objects.all())
    abbreviations = [act.abbr for act in acts]

    positions = []
    for position in EducationPosition.objects.filter(is_published=True).select_related('category'):
        positions.append({
            'id': position.number,
            'title': position.title,
            'category': position.category_id,
            'subjects': split_lines(position.subjects),
            'legal_basis': [
                {'tag': tag, 'act': resolve_act(tag, abbreviations)}
                for tag in split_lines(position.legal_basis)
            ],
            'outcome': position.outcome,
            'outcome_label': position.get_outcome_display() if position.outcome else '',
            'outcome_note': position.outcome_note,
            'in_favor_of_official': position.in_favor_of_official,
            'municipal': position.municipal,
            'norm_changed': position.norm_changed,
            'key_quote': position.key_quote,
            'facts_summary': position.facts_summary,
            'lesson': position.lesson,
            'page': position.page,
            'year': position.year,
            'years': position.years,
            'amount': position.amount,
            'paragraphs': split_paragraphs(position.full_text),
            'notes': parse_notes(position.notes),
        })

    return {
        'page': {
            'eyebrow': page.eyebrow,
            'title': page.title,
            'lead': page.lead,
            'approved_note': page.approved_note,
            'period': page.period,
            'intro': page.intro,
            'source_note': page.source_note,
        },
        'categories': [
            {'id': category.pk, 'name': category.name, 'short_name': category.short_name, 'color': category.color}
            for category in categories
        ],
        'acts': [
            {'abbr': act.abbr, 'full_name': act.full_name, 'changed_note': act.changed_note}
            for act in acts
        ],
        'outcomes': [{'id': value, 'label': label} for value, label in EducationPosition.OUTCOME_CHOICES],
        'positions': positions,
    }
