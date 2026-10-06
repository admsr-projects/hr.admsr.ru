from django import forms


class MarkdownTextarea(forms.Textarea):
    """Поле для текста в формате Markdown: редактор EasyMDE с панелью и предпросмотром."""

    def __init__(self, attrs=None):
        base_attrs = {'data-markdown-editor': '', 'rows': 14}
        if attrs:
            base_attrs.update(attrs)
        super().__init__(base_attrs)

    class Media:
        css = {'all': ('api/easymde/easymde.min.css', 'api/markdown-editor/markdown-editor.css')}
        js = ('api/easymde/easymde.min.js', 'api/markdown-editor/markdown-editor.js')


MARKDOWN_HELP = (
    'Текст можно оформлять: **жирный**, *курсив*, [ссылка](https://example.ru), '
    'списки («- пункт» или «1. пункт»), заголовки («# Заголовок», «## Подзаголовок»). '
    'Кнопки над полем вставляют разметку, «Просмотр» показывает результат.'
)


class MarkdownFieldsMixin:
    """Для ModelAdmin: перечисленные в markdown_fields поля редактируются как Markdown."""

    markdown_fields: tuple[str, ...] = ()

    def formfield_for_dbfield(self, db_field, request, **kwargs):
        if db_field.name in self.markdown_fields:
            kwargs['widget'] = MarkdownTextarea
            formfield = super().formfield_for_dbfield(db_field, request, **kwargs)
            if formfield is not None:
                formfield.help_text = MARKDOWN_HELP
            return formfield
        return super().formfield_for_dbfield(db_field, request, **kwargs)
