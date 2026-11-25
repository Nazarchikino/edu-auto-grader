# Edu Auto Grader

[![Python 3.12+](https://img.shields.io/badge/Python-3.12%2B-3776AB?logo=python&logoColor=white)](https://www.python.org/)
[![FastAPI](https://img.shields.io/badge/FastAPI-0.115-009688?logo=fastapi&logoColor=white)](https://fastapi.tiangolo.com/)
[![React 18](https://img.shields.io/badge/React-18.3-61DAFB?logo=react&logoColor=black)](https://react.dev/)
[![TypeScript](https://img.shields.io/badge/TypeScript-5.6-3178C6?logo=typescript&logoColor=white)](https://www.typescriptlang.org/)
[![PostgreSQL 16](https://img.shields.io/badge/PostgreSQL-16-4169E1?logo=postgresql&logoColor=white)](https://www.postgresql.org/)
[![Docker](https://img.shields.io/badge/Docker-Compose-2496ED?logo=docker&logoColor=white)](https://www.docker.com/)

**Edu Auto Grader** — спеціалізована вебплатформа електронних навчально-методичних посібників із вбудованим ядром **100% детермінованої автоматизованої перевірки практичних робіт** із дисциплін **Microsoft Word (`.docx`)**, **Microsoft Excel (`.xlsx`)**, **Microsoft Access (`.accdb`)** та **HTML5**.

Система створена для коледжу як інтерактивне доповнення до базової платформи **`kpefk.lcloud.in.ua`**. Вона об'єднує структуровані лекції з тестами-допусками, автоматичний розподіл індивідуальних варіантів, миттєву перевірку файлів і HTML-коду, контроль академічної доброчесності та експорт зведених відомостей успішності у `.xlsx` та `.pdf`.

---

## Зміст

- [Ключові можливості за ролями](#ключові-можливості-за-ролями)
- [Ядро автоперевірки та зберігання робіт](#ядро-автоперевірки-та-зберігання-робіт)
- [Технологічний стек та архітектура](#технологічний-стек-та-архітектура)
- [Швидкий старт (локальний запуск)](#швидкий-старт-локальний-запуск)
- [Production-розгортання (Docker + Nginx + бекапи)](#production-розгортання-docker--nginx--бекапи)
- [Перевірка якості та тести](#перевірка-якості-та-тести)
- [Архітектурні обмеження (Out of Scope)](#архітектурні-обмеження-out-of-scope)

---

## Ключові можливості за ролями

Система використовує JWT-автентифікацію (`access` + `refresh` токени) та рольове розмежування доступу (**RBAC**).

### Студент (`student`)
- **Повний навчальний контент 4 дисциплін** (`word`, `excel`, `access`, `html`): **40 модулів**, **37 практичних робіт**, **254 індивідуальні варіанти**, **240 питань тестів-допусків** та **184 медіафайли** (ілюстрації й PDF-посібники, що роздаються через `/media/courses`).
- **Інтерактивні Markdown-лекції (`MarkdownRenderer`):** рендеринг заголовків, таблиць, блоків коду, цитат, вкладених списків, ілюстрацій зі збільшенням та безпечних посилань із PDF-бейджами; підтримка теоретичних модулів без практичної роботи.
- **Тест-допуск (поріг `>= 70%`):** до успішного складання тесту доступ до практичної роботи та ендпоінту здачі блокується на рівні бекенду (`HTTP 403`, код `QUIZ_NOT_PASSED`).
- **Персональний варіант:** визначається детерміновано за порядковим номером студента у списку групи (`variant_index = ((list_number or 1) - 1) % total_variants`, у UI відображається `variant_number = variant_index + 1`), зі структурованим виведенням параметрів та швидким копіюванням вхідного тексту.
- **Два режими здачі робіт:**
  - *Офісні файли (`.docx`, `.xlsx`, `.accdb`):* drag-and-drop завантаження файлу (`multipart/form-data`).
  - *Вбудована HTML5-пісочниця (`HtmlSandbox`):* редактор **Monaco Editor** із миттєвим рендерингом в ізольованому `<iframe sandbox>` та відправкою коду на серверну DOM-перевірку.
- **12-бальна система оцінювання та електронна заліковка (`GradebookPage`, `GradingReportCard`):** кожна практична робота оцінюється за 12-бальною шкалою — до **10 б.** автоматична перевірка базових вимог (із покроковим розбором очікуваного vs фактичного значення та статусом авторства) + до **2 б.** ручна оцінка викладача за творче завдання / додаткове оформлення.

### Викладач (`teacher`)
- **Конструктор курсів і лекцій (`CourseEditorPage`):** створення та редагування курсів, модулів, Markdown-лекцій, питань тестів-допусків і методичних вказівок до практичних робіт.
- **Візуальний редактор правил оцінювання (`RuleBuilderPage`):** налаштування декларативних `JSONB`-правил (`GradingRule`) і ваги кожного критерію в балах (`PUT /api/v1/practicals/{practical_id}/rules`).
- **Електронний журнал групи (`GroupJournalPage`):** матриця успішності з двосторонньою прокруткою та закріпленими областями (колонка `№ / ПІБ студента`, шапка практичних робіт і підсумкова колонка `Сума балів`), а також аналітика типових помилок по критеріях.
- **Контроль академічної доброчесності (`PlagiarismBadge`):** автоматична детекція плагіату за криптографічним хешем **`SHA-256`** (бінарного файлу або нормалізованого HTML-коду) та метаданими OpenXML **`docProps/core.xml`** (`creator`, `last_modified_by`, `created`, `modified`, `revision`).
- **Інспекція та завантаження робіт:** у вікні інспекції здачі викладач курсу (або адміністратор) може **завантажити оригінальний файл** (`.docx`, `.xlsx`, `.accdb`) або згенерований `.html`-файл із `raw_code` (`GET /api/v1/submissions/{submission_id}/download`), бачить термін зберігання файлу та може вручну скоригувати `final_score` або додати бонус за творче завдання (`+1` / `+2` б. до 12-бальної шкали через `teacher_score_adjustment`) і залишити коментар.
- **Експорт відомостей:** генерація зведених відомостей успішності групи у форматах **`.xlsx`** (`openpyxl`) та **`.pdf`** (`fpdf2` із підтримкою кирилиці) для перенесення оцінок у `kpefk.lcloud.in.ua`.

### Адміністратор (`admin`)
- **Керування користувачами та групами (`AdminUsersPage`):** CRUD-операції над обліковими записами, призначення ролей (`student`, `teacher`, `admin`), довідник академічних груп із бізнес-обмеженням курсів навчання **`1..4`** (`CHECK`-обмеження БД, Pydantic та UI).
- **Масовий імпорт студентів (`POST /api/v1/admin/users/import`):** імпорт із офіційних відомостей коледжу (`.docx`) та текстових списків (`.txt`) з обов'язковим сортуванням за **українською абеткою**, автоприсвоєнням порядкових номерів (`list_number`), розрахунком варіантів (`variant_number`), пропуском дублікатів `email` та вивантаженням звіту облікових даних (`.txt`).
- **Каскадне очищення файлів:** при видаленні облікового запису студента (`DELETE /api/v1/admin/users/{user_id}`) усі пов'язані фізичні файли його здач безпечно видаляються з диска в межах `UPLOADS_DIR`.

---

## Ядро автоперевірки та зберігання робіт

Усі парсери реалізовані за патерном **Strategy** як спадкоємці єдиного абстрактного класу `BaseGrader` (`backend/app/graders/base.py`) і підключаються через `GraderFactory`. Ядро підтримує числові умови (`>=`, `<=`, `==`, `!=`, `>`, `<`) та підстановку параметрів індивідуального варіанта `{param}` у полі `expected`.

| Формат | Парсер та бібліотека | Що перевіряється | Типи правил (`GradingRuleType`) |
| :--- | :--- | :--- | :--- |
| **Word (`.docx`)** | `DocxGrader` (`python-docx`) | Поля сторінки (мм), гарнітура й кегль шрифту, міжрядковий інтервал, вирівнювання абзаців, наявність таблиць і маркованих/нумерованих списків | `docx_page_margins`, `docx_font`, `docx_line_spacing`, `docx_alignment`, `docx_table_exists`, `docx_list_exists` |
| **Excel (`.xlsx`)** | `XlsxGrader` (`openpyxl`) | Формули у цільових комірках (`data_only=False`), кешовані обчислені значення (`data_only=True`), наявність і параметри діаграм (`_charts`) | `xlsx_formula`, `xlsx_value`, `xlsx_chart_exists` |
| **Access (`.accdb`)** | `AccdbGrader` (`access-parser`, резервний `mdb-schema` / `mdbtools` на Linux) | Наявність і кількість таблиць, існування стовпців (`Table.Column`) та відповідність їхніх типів даних схемі БД (включно з `Hyperlink` → `MEMO`) | `accdb_table_exists`, `accdb_column_exists`, `accdb_column_type` |
| **HTML5 (`.html`)** | `HtmlGrader` (`beautifulsoup4` + `lxml`) | Валідація DOM-дерева за CSS-селекторами, підрахунок елементів, перевірка обов'язкових атрибутів та їхніх значень | `html_tag_exists`, `html_tag_count`, `html_attribute_exists` |

### Політика зберігання та автоочищення файлів (90 днів)

- Завантажені файли (`.docx`, `.xlsx`, `.accdb` у `UPLOADS_DIR`) та вихідний HTML-код (`raw_code`) зберігаються протягом **90 днів** (налаштовується змінною `SUBMISSION_FILE_RETENTION_DAYS`). У відповіді `SubmissionRead` повертаються обчислювані поля `is_file_available` та `file_expires_at`, а скачування захищене від Path Traversal.
- Після завершення терміну зберігання фізичні файли з диска та значення `raw_code` автоматично очищуються фоновим `asyncio`-воркером у `lifespan` (`backend/app/main.py` — при старті сервера та кожні 24 години, якщо `ENABLE_RETENTION_CLEANUP_TASK=true`) або вручну/через cron за допомогою CLI-скрипта `backend/app/services/retention_service.py`.
- **Історія оцінок та антиплагіату зберігається:** очищення не видаляє записи `submissions` — поля `auto_score`, `final_score`, `grading_report`, `teacher_comment`, `extracted_metadata` та `file_hash` залишаються в PostgreSQL.

---

## Технологічний стек та архітектура

### Технології

| Категорія | Технології та версії |
| :--- | :--- |
| **Backend** | Python `3.12+`, FastAPI `0.115.6`, Uvicorn `0.32.1`, SQLAlchemy `2.0.36` (async), `asyncpg` `0.30.0`, Alembic `1.13.3`, Pydantic `2.10.3`, `pydantic-settings` `2.6.1`, PyJWT `2.10.1`, `bcrypt` `4.2.0`, `python-multipart` `0.0.19` |
| **Parsers & Export** | `python-docx` `1.1.2`, `openpyxl` `3.1.5`, `access-parser` `0.0.6`, `beautifulsoup4` `4.12.3`, `lxml` `5.3.0`, `fpdf2` `2.8.1` |
| **Frontend** | Node.js `20 LTS`, React `18.3.1`, TypeScript `~5.6.3` (`strict: true`), Vite `5.4.11`, Tailwind CSS `3.4.15`, `@monaco-editor/react` `4.6.0`, TanStack Query `^5.60.0`, React Router `^6.28.0`, Axios `^1.7.7`, Lucide React `^0.460.0` |
| **DB & Infrastructure** | PostgreSQL `16` (`postgres:16-alpine`, 8 реляційних таблиць із `UUID`, `ENUM` і `JSONB`), Docker & Docker Compose |
| **Quality Tools** | Ruff `0.8.3`, Mypy `1.13.0` (`--strict`), Pytest `8.3.4` + `pytest-asyncio` `0.24.0` + `httpx` `0.28.1`, ESLint `9.15+`, `tsc --noEmit` |

### Структура репозиторію

```text
edu-auto-grader/
├── docker-compose.yml              # Контейнер PostgreSQL 16 + volume uploads/
├── uploads/                        # Сховище файлів зданих робіт студентів
├── backend/
│   ├── pyproject.toml              # Залежності Python і конфігурація ruff/mypy/pytest
│   ├── alembic.ini                 # Конфігурація міграцій Alembic
│   ├── alembic/versions/           # Міграції БД (схема 8 таблиць, обмеження курсів 1..4)
│   ├── content/
│   │   ├── courses/                # JSON-пакети 4 дисциплін (word, excel, access, html)
│   │   └── media/                  # 184 медіафайли лекцій/тестів (word/, excel/, access/)
│   ├── app/
│   │   ├── main.py                 # FastAPI, lifespan (автоочищення), CORS, /media/courses, /health
│   │   ├── seed.py                 # CLI-ініціалізація та неруйнівна синхронізація курсів (--sync-courses)
│   │   ├── core/                   # config.py, database.py, security.py, exceptions.py
│   │   ├── models/                 # SQLAlchemy 2.0 моделі (user, course, progress)
│   │   ├── schemas/                # Pydantic v2 контракти (auth, course, grading, submission)
│   │   ├── graders/                # BaseGrader, GraderFactory, metadata.py, Docx/Xlsx/Accdb/Html парсери
│   │   ├── services/               # quiz, submission, retention, export (.xlsx/.pdf), student_import
│   │   └── api/v1/                 # REST-ендпоінти (auth, admin, courses, practicals, submissions, analytics)
│   └── tests/                      # 36 модульних та інтеграційних тестів (in-memory SQLite адаптер)
└── frontend/
    ├── package.json                # Залежності та npm-скрипти
    ├── vite.config.ts              # Dev-сервер (:5173) і проксі /api та /media -> :8000
    └── src/
        ├── api/                    # Axios-клієнт із JWT-інтерсепторами
        ├── context/                # AuthContext (сесія та оновлення токенів)
        ├── types/                  # TypeScript-контракти (синхронізовані з Pydantic)
        ├── components/             # common (MarkdownRenderer), grading, layout, sandbox (HtmlSandbox)
        └── pages/                  # LoginPage, student/, teacher/, admin/
```

---

## Швидкий старт (локальний запуск)

### Вимоги
- **Docker Desktop** (або Docker Engine + Docker Compose)
- **Python 3.12** *(рекомендовано саме **3.12** або **3.13** — для гарантованої наявності готових бінарних wheels `asyncpg`, `lxml` і `bcrypt` під Windows)*
- **Node.js 20 LTS** та **npm**
- *(Опційно, на Linux)* пакет `mdbtools` як резервний CLI-інструмент для читання `.accdb`

### Покроковий запуск (Windows PowerShell)

Усі команди нижче виконуються з кореня репозиторію (щоб `.env` і директорія `uploads/` збігалися з `docker-compose.yml`).

#### 1. Клонування та запуск PostgreSQL 16
```powershell
git clone <URL_РЕПОЗИТОРІЮ> edu-auto-grader
cd edu-auto-grader
docker compose up -d
docker compose ps
```
Дочекайтеся статусу `healthy` для контейнера `edu_auto_grader_db`.

#### 2. Створення `backend/.venv` та встановлення залежностей
```powershell
py -3.12 -m venv backend/.venv
.\backend\.venv\Scripts\Activate.ps1
pip install -e "./backend[dev]"
```

<details>
<summary>Аналог для Linux / macOS</summary>

```bash
python3.12 -m venv backend/.venv
source backend/.venv/bin/activate
pip install -e "./backend[dev]"
```

</details>

#### 3. Застосування міграцій та наповнення БД
```powershell
alembic -c backend/alembic.ini upgrade head
python -m app.seed --sync-courses
```

> [!TIP]
> Скрипт `app.seed` підтримує прапорці:
> - `--dry-run` — валідує JSON-пакети 4 курсів і правила `GradingRule` без підключення до PostgreSQL;
> - `--sync-courses` — **неруйнівно** (in-place `upsert`) оновлює контент курсів, модулів, тестів і практичних із `backend/content/courses/*.json`, зберігаючи користувачів, академічні групи, усі спроби тестів (`QuizAttempt`) та здачі студентів (`Submission`) разом із оцінками й коментарями викладача;
> - `--allow-destructive-module-delete` — опційний прапорець до `--sync-courses`, який явно дозволяє видаляти зайві модулі або практичні, вилучені з JSON, навіть якщо за ними вже є здачі чи спроби тестів (із безпечним очищенням пов'язаних файлів у `uploads/`).

#### 4. Запуск Backend API (FastAPI + Uvicorn)
```powershell
uvicorn app.main:app --app-dir backend --reload --host 0.0.0.0 --port 8000
```
- OpenAPI / Swagger UI: `http://localhost:8000/docs`
- Перевірка стану: `http://localhost:8000/health`

#### 5. Запуск Frontend (React + Vite)
В окремому вікні терміналу:
```powershell
npm --prefix frontend install
npm --prefix frontend run dev
```
- Вебінтерфейс: `http://localhost:5173` (Vite автоматично проксує `/api` та `/media` на `http://localhost:8000`).

---

### Ключові змінні середовища (`.env`)

Файл `.env` у корені проєкту зчитується як `docker-compose.yml`, так і `backend/app/core/config.py` (`Settings`). За відсутності `.env` застосовуються наведені значення за замовчуванням:

| Змінна | Значення за замовчуванням | Призначення |
| :--- | :--- | :--- |
| `POSTGRES_USER` | `postgres` | Користувач PostgreSQL |
| `POSTGRES_PASSWORD` | `postgres` | Пароль PostgreSQL |
| `POSTGRES_HOST` | `localhost` | Хост сервера БД |
| `POSTGRES_PORT` | `5432` | Порт PostgreSQL |
| `POSTGRES_DB` | `edu_auto_grader` | Назва бази даних |
| `DATABASE_URL` | *(не задано)* | Опційний повний async DSN (`postgresql+asyncpg://...`), має пріоритет над `POSTGRES_*` |
| `JWT_SECRET_KEY` | `change-me-in-production-super-secret-jwt-key-32b` | Секретний ключ підпису JWT (`HS256`) |
| `ACCESS_TOKEN_EXPIRE_MINUTES` | `60` | Час життя access-токена (хвилини) |
| `REFRESH_TOKEN_EXPIRE_DAYS` | `7` | Час життя refresh-токена (дні) |
| `CORS_ORIGINS` | `["http://localhost:5173","http://127.0.0.1:5173"]` | Дозволені origin-адреси фронтенду (JSON-масив) |
| `UPLOADS_DIR` | `backend/uploads` | Каталог збереження завантажених файлів студентів (відносні шляхи прив'язуються до `backend/`) |
| `SUBMISSION_FILE_RETENTION_DAYS` | `90` | Термін зберігання файлів та `raw_code` робіт у днях (`>= 1`) |
| `SUBMISSION_SUPERSEDED_GRACE_HOURS` | `24` | Мінімальний вік проміжної перездачі в годинах перед прибиранням зайвого файлу з диска |
| `ENABLE_RETENTION_CLEANUP_TASK` | `true` | Автозапуск фонового воркера очищення файлів (кожні 24 год) |
| `COURSE_CONTENT_DIR` | `backend/content/courses` | Шлях до JSON-файлів 4 навчальних курсів |
| `COURSE_MEDIA_DIR` | `backend/content/media` | Шлях до статичних медіафайлів курсів (`/media/courses`) |
| `QUIZ_PASS_THRESHOLD_PERCENT` | `70.0` | Мінімальний відсоток для проходження тесту-допуску |

### Ручне очищення прострочених файлів робіт (CLI)

Окрім фонового воркера в `main.py`, очищення можна запускати вручну або за розкладом (cron / Task Scheduler):

```powershell
# Безпечний попередній перегляд без видалення файлів та змін у БД
python -m app.services.retention_service --dry-run

# Фактичне очищення (можна додати --retention-days N для перевизначення терміну)
python -m app.services.retention_service
```

### Початкові облікові записи (`seed.py`)

Після виконання `python -m app.seed` створюється тестова академічна група **`КН-31`** (*«122 Комп'ютерні науки», 3 курс*) та 5 початкових облікових записів:

| Роль | Email | Пароль | ПІБ | Група / Номер у списку |
| :--- | :--- | :--- | :--- | :--- |
| `admin` | `admin@kpefk.lcloud.in.ua` | `Admin123!` | Адміністратор Системи | — |
| `teacher` | `teacher@kpefk.lcloud.in.ua` | `Teacher123!` | Коваленко Олександр Петрович | — |
| `student` | `student1@kpefk.lcloud.in.ua` | `Student123!` | Бондаренко Ірина Василівна | `КН-31` / №1 |
| `student` | `student2@kpefk.lcloud.in.ua` | `Student123!` | Мельник Дмитро Сергійович | `КН-31` / №2 |
| `student` | `student3@kpefk.lcloud.in.ua` | `Student123!` | Шевченко Максим Андрійович | `КН-31` / №3 |

> [!WARNING]
> Наведені облікові дані призначені **лише для локальної розробки та первинного налаштування**. Перед розгортанням у продакшні обов'язково змініть паролі всіх облікових записів та встановіть криптостійкий `JWT_SECRET_KEY`.

---

## Production-розгортання (Docker + Nginx + бекапи)

Готовий production-стек описано у [`docker-compose.prod.yml`](docker-compose.prod.yml) (ізольований Compose-проєкт `name: edu-auto-grader-prod`) та складається з трьох ізольованих контейнерів:
- **`db` (`postgres:16-alpine`)** — працює лише у внутрішній мережі `internal` без пробросу порту `5432` назовні;
- **`backend` (`backend/Dockerfile`)** — `python:3.12-slim` із `mdbtools`, шрифтами `fonts-dejavu-core` (для кириличного PDF-експорту через `fpdf2`), непривілейованим користувачем `appuser`, `APP_ENV=production`, `uvicorn --workers 2 --proxy-headers` і `HEALTHCHECK` на `/api/v1/health/ready`;
- **`frontend` (`frontend/Dockerfile` + `frontend/nginx.conf`)** — multi-stage збірка React SPA з локально вбудованим Monaco Editor (без запитів до зовнішнього CDN) за реверс-проксі Nginx (`client_max_body_size 35m`, `gzip`, заголовки безпеки, проксування `/api/` та `/media/courses/`).

> [!NOTE]
> Production-стек використовує окремий простір імен (`edu-auto-grader-prod`) і власні іменовані томи `postgres_data_prod` (PostgreSQL) та `uploads_data_prod` (`/app/uploads`), тому не перетинається з локальною dev-БД (`postgres_data` із [`docker-compose.yml`](docker-compose.yml)).

### Запуск у production

```bash
# 1. Скопіювати шаблон і задати надійні секрети (POSTGRES_PASSWORD, JWT_SECRET_KEY, CORS_ORIGINS)
cp .env.production.example .env.production
# Генерація JWT_SECRET_KEY: openssl rand -hex 32

# 2. Зібрати та підняти контейнери
docker compose -f docker-compose.prod.yml --env-file .env.production up -d --build

# 3. Застосувати міграції БД та завантажити контент 4 курсів
docker compose -f docker-compose.prod.yml --env-file .env.production exec backend alembic upgrade head
docker compose -f docker-compose.prod.yml --env-file .env.production exec backend python -m app.seed --sync-courses

# 4. Перевірити готовність (БД + UPLOADS_DIR)
curl -f http://127.0.0.1:8080/api/v1/health/ready
```

### Резервне копіювання та відновлення

Скрипт [`scripts/backup.sh`](scripts/backup.sh) виконує `pg_dump -Fc` із контейнера `db`, архівує том `uploads_data_prod` (`/app/uploads`) у `.tar.gz` та автоматично видаляє бекапи старші за `RETENTION_BACKUP_DAYS` (за замовчуванням `14` днів). Для відновлення передбачено [`scripts/restore.sh`](scripts/restore.sh):

```bash
# Щоденний бекап (рекомендовано додати в cron, напр. о 03:00 щодня)
chmod +x scripts/backup.sh scripts/restore.sh
./scripts/backup.sh

# Відновлення БД та файлів робіт із бекапу
./scripts/restore.sh ./backups/db_YYYYMMDD_HHMMSS.dump ./backups/uploads_YYYYMMDD_HHMMSS.tar.gz
```

---

## Перевірка якості та тести

Тестовий набір бекенду (`backend/tests/`, 36 модульних та інтеграційних тестів) використовує in-memory SQLite-адаптер для `JSONB` у `conftest.py`, тому запускається автономно без активного контейнера PostgreSQL.

```powershell
# Backend (в активованому середовищі backend/.venv із dev-залежностями)
ruff check backend
mypy --strict backend/app
pytest

# Frontend
npm --prefix frontend run typecheck
npm --prefix frontend run lint
npm --prefix frontend run build
```

*(За потреби явного підключення параметрів `pytest` із кореня репозиторію використовуйте `pytest -c backend/pyproject.toml`.)*

---

## Архітектурні обмеження (Out of Scope)

- **100% детермінована перевірка без LLM/AI:** оцінювання здійснюється виключно за формальними декларативними правилами (`GradingRule`) без суб'єктивних AI-оцінок.
- **Відсутність виконання довільного коду та макросів на сервері:** VBA-макроси у `.xlsx`/`.accdb` та зовнішній код (Python/JS/C++) ніколи не виконуються на сервері; прев'ю HTML5-робіт ізольоване на стороні браузера в `<iframe sandbox>`.
- **Автономний обмін із `kpefk.lcloud.in.ua`:** пряма API-інтеграція чи парсинг облікових записів базової платформи відсутні — результати передаються через експорт відомостей у `.xlsx` та `.pdf`.
- **Поза межами MVP:** офлайн-режим (PWA / IndexedDB), відеохостинг лекцій, чати в реальному часі (WebSockets) та зовнішні сповіщення (Telegram/Email).

---

## Документація проєкту

- [SPEC.md](SPEC.md) — продуктова специфікація, ролі та функціональні вимоги
- [ARCHITECTURE.md](ARCHITECTURE.md) — технічна архітектура, схема БД і контракти API
- [TASKS.md](TASKS.md) — покроковий журнал реалізації фаз проєкту (SDD)
- [AGENTS.md](AGENTS.md) — інженерні стандарти та робочий цикл розробки
