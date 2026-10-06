// Подключает EasyMDE к полям с атрибутом data-markdown-editor (см. api/widgets.py).
// Иконки FontAwesome не используются: сайт может работать без доступа к внешним CDN,
// поэтому кнопки панели подписаны текстом.
document.addEventListener('DOMContentLoaded', function () {
  document.querySelectorAll('textarea[data-markdown-editor]').forEach(function (textarea) {
    if (textarea.dataset.markdownReady || textarea.id.indexOf('__prefix__') !== -1) return;
    textarea.dataset.markdownReady = '1';

    new EasyMDE({
      element: textarea,
      autoDownloadFontAwesome: false,
      spellChecker: false,
      status: false,
      forceSync: true,
      minHeight: '260px',
      placeholder: 'Текст в формате Markdown',
      toolbar: [
        { name: 'bold', action: EasyMDE.toggleBold, text: 'Ж', title: 'Жирный', className: 'md-btn md-btn-bold' },
        { name: 'italic', action: EasyMDE.toggleItalic, text: 'К', title: 'Курсив', className: 'md-btn md-btn-italic' },
        { name: 'heading', action: EasyMDE.toggleHeading1, text: 'Заголовок', title: 'Заголовок раздела', className: 'md-btn' },
        { name: 'subheading', action: EasyMDE.toggleHeading2, text: 'Подзаголовок', title: 'Подзаголовок', className: 'md-btn' },
        '|',
        { name: 'ul', action: EasyMDE.toggleUnorderedList, text: '• Список', title: 'Маркированный список', className: 'md-btn' },
        { name: 'ol', action: EasyMDE.toggleOrderedList, text: '1. Список', title: 'Нумерованный список', className: 'md-btn' },
        { name: 'quote', action: EasyMDE.toggleBlockquote, text: 'Цитата', title: 'Цитата', className: 'md-btn' },
        '|',
        { name: 'link', action: EasyMDE.drawLink, text: 'Ссылка', title: 'Вставить ссылку', className: 'md-btn' },
        '|',
        { name: 'preview', action: EasyMDE.togglePreview, text: 'Просмотр', title: 'Просмотр', className: 'md-btn no-disable' },
        { name: 'side-by-side', action: EasyMDE.toggleSideBySide, text: 'Рядом', title: 'Редактор и просмотр рядом', className: 'md-btn no-disable no-mobile' },
      ],
    });
  });
});
