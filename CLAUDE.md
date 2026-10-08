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
- Киоск (kiosk-hr.admsr.ru, экран 1080×1920, без форм) — отдельная сборка того же фронта, правила в
  [`docs/DESIGN-RULES.md`](docs/DESIGN-RULES.md) §10. Разработка: `cd frontend && npm run dev:kiosk`;
  сборка: `npm run generate:kiosk` (результат в `frontend/.output-kiosk/public`), архив: `python deploy/pack_deploy.py --kiosk`.
  Любая новая форма или поле ввода на сайте должна скрываться в киоске (`useKiosk()`).

## Прочее

- Страница «Антикоррупционное просвещение» (`/anti-corruption/education`) — обзор практики ВС РФ: страница, категории, нормативные акты
  и позиции редактируются в админке (группа «Нет коррупции!: просвещение»), API `/api/anti-corruption-education/`
  (`backend/DjangoProj/api/education.py`). Начальные данные лежат в `api/seed/education_review.json` и загружаются миграцией 0056.

- Локальные `backend/DjangoProj/db.sqlite3` и `frontend/.data/content/contents.sqlite` меняются при разработке —
  в коммиты их не добавлять.
- Новые миграции применять командой `python manage.py migrate`.
- Полный текст новостей и описание мероприятий — Markdown: в админке редактор EasyMDE
  (`backend/DjangoProj/api/widgets.py`, файлы редактора в `api/static/api/`), на сайте `DsMarkdown` / `renderMarkdown`
  (`frontend/app/utils/markdown.ts`). После деплоя бэкенда нужен `python manage.py collectstatic`.
  Новое поле с Markdown в админке — через `MarkdownFieldsMixin`.
- Персональные данные: перечень и замечания в [`docs/PD-INVENTORY.md`](docs/PD-INVENTORY.md). Файлы из форм (`resumes/`, `photos/`,
  `subscription_resumes/`, `practice_applications/`, `feedback_photos/`) отдаёт только `api/media.py` вошедшим сотрудникам с правом
  просмотра; новый публичный каталог загрузок нужно добавить в `PUBLIC_DIRS`, иначе он закрыт. Доступ к ПД журналируется
  (`api/audit.py`, «Журнал доступа к ПД» в админке): у ModelAdmin с ПД подключать `PersonalDataAuditMixin`, у новой формы вызывать
  `log_event('submit', request, model=obj, object_id=obj.pk)`. Форм о коррупции на сайте нет: обращения идут через баннер Госуслуг.
- `db.sqlite3`, `frontend/.data/` и каталоги загрузок с ПД в `.gitignore`; в индекс их не возвращать.
