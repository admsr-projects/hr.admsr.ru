# Кадровый портал администрации Сургутского района

Фронтенд: Nuxt 4 + Nuxt UI 4 (`frontend/`), бэкенд: Django REST (`backend/DjangoProj/`).

## Дизайн

Любой интерфейс (новая страница, компонент, правка стилей) делать по правилам из
[`docs/DESIGN-RULES.md`](docs/DESIGN-RULES.md): дизайн **SOFT** — тональные поверхности вместо рамок и теней,
фиксированная шкала шрифтов (12/14/16/18/20/36), скругления: кнопки и метки круглые (`rounded-full`), поля `rounded-lg`, панели `rounded-xl`,
второстепенные кнопки и метки в варианте `soft`. Не вводить новые размеры, цвета и скругления — выбирать из правил.
Если правила не хватает — сначала дополнить файл, потом писать код.

## Запуск для разработки

- Бэкенд: `cd backend/DjangoProj && DJANGO_DEBUG=True python manage.py runserver 8000`
- Фронт: `cd frontend && npm run dev` (порт 3000; CORS бэка разрешает только его)
- После добавления новых файлов страниц и плагинов dev-сервер Nuxt нужно перезапустить.

## Прочее

- Локальные `backend/DjangoProj/db.sqlite3` и `frontend/.data/content/contents.sqlite` меняются при разработке —
  в коммиты их не добавлять.
- Новые миграции применять командой `python manage.py migrate`.
- Полный текст новостей и описание мероприятий — Markdown: в админке редактор EasyMDE
  (`backend/DjangoProj/api/widgets.py`, файлы редактора в `api/static/api/`), на сайте `DsMarkdown` / `renderMarkdown`
  (`frontend/app/utils/markdown.ts`). После деплоя бэкенда нужен `python manage.py collectstatic`.
  Новое поле с Markdown в админке — через `MarkdownFieldsMixin`.
