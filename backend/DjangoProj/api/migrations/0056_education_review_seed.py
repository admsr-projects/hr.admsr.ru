import json
from pathlib import Path

from django.db import migrations

SEED_PATH = Path(__file__).resolve().parent.parent / 'seed' / 'education_review.json'


def load_seed(apps, schema_editor):
    """Начальное наполнение страницы «Антикоррупционное просвещение» (обзор ВС РФ N 14/2026)."""
    Page = apps.get_model('api', 'EducationReviewPage')
    Category = apps.get_model('api', 'EducationCategory')
    Act = apps.get_model('api', 'EducationLegalAct')
    Position = apps.get_model('api', 'EducationPosition')

    seed = json.loads(SEED_PATH.read_text(encoding='utf-8'))

    Page.objects.update_or_create(pk=1, defaults=seed['page'])

    categories = {}
    for item in seed['categories']:
        categories[item['key']] = Category.objects.create(
            name=item['name'],
            short_name=item['short_name'],
            color=item['color'],
            order=item['order'],
        )

    for item in seed['acts']:
        Act.objects.update_or_create(abbr=item['abbr'], defaults=item)

    for item in seed['positions']:
        fields = {**item, 'category': categories[item['category']]}
        Position.objects.update_or_create(number=item['number'], defaults=fields)


def unload_seed(apps, schema_editor):
    apps.get_model('api', 'EducationPosition').objects.all().delete()
    apps.get_model('api', 'EducationLegalAct').objects.all().delete()
    apps.get_model('api', 'EducationCategory').objects.all().delete()
    apps.get_model('api', 'EducationReviewPage').objects.all().delete()


class Migration(migrations.Migration):

    dependencies = [
        ('api', '0055_education_review'),
    ]

    operations = [
        migrations.RunPython(load_seed, unload_seed),
    ]
