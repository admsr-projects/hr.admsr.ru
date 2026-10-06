from django.db import migrations, models
from django.utils import timezone


def mark_existing_as_notified(apps, schema_editor):
    """Уже опубликованные вакансии подписчикам не рассылаем — только новые."""
    Vacancy = apps.get_model('api', 'Vacancy')
    Vacancy.objects.filter(subscribers_notified_at__isnull=True).update(subscribers_notified_at=timezone.now())


class Migration(migrations.Migration):

    dependencies = [
        ('api', '0052_recipient_receives_feedback'),
    ]

    operations = [
        migrations.AddField(
            model_name='vacancy',
            name='subscribers_notified_at',
            field=models.DateTimeField(
                blank=True,
                editable=False,
                help_text='Когда подписчикам ушло письмо о вакансии. Пока пусто, письмо уйдёт при первой публикации (активной вакансии).',
                null=True,
                verbose_name='Подписчики уведомлены',
            ),
        ),
        migrations.RunPython(mark_existing_as_notified, migrations.RunPython.noop),
    ]
