# Посібник із розгортання та обслуговування Edu Auto Grader

Практичний покроковий посібник із запуску, оновлення та супроводу платформи `edu-auto-grader` у двох режимах:

- **Dev** — локальна розробка на Windows / Linux / macOS (PostgreSQL у Docker, бекенд і фронтенд запускаються напряму з вихідного коду з hot-reload);
- **Prod** — бойовий сервер (Ubuntu 22.04/24.04 LTS або Windows із Docker Desktop), де вся система (`db` + `backend` + `frontend`) працює в ізольованих Docker-контейнерах.

Усі імена контейнерів, сервісів, томів, змінних середовища, портів і команд у цьому документі звірено з поточними файлами репозиторію: [`docker-compose.yml`](docker-compose.yml), [`docker-compose.prod.yml`](docker-compose.prod.yml), [`.env.production.example`](.env.production.example), [`backend/Dockerfile`](backend/Dockerfile), [`frontend/Dockerfile`](frontend/Dockerfile), [`frontend/nginx.conf`](frontend/nginx.conf), [`frontend/vite.config.ts`](frontend/vite.config.ts), [`backend/app/core/config.py`](backend/app/core/config.py), [`backend/app/seed.py`](backend/app/seed.py), [`backend/app/services/retention_service.py`](backend/app/services/retention_service.py), [`scripts/backup.sh`](scripts/backup.sh), [`scripts/restore.sh`](scripts/restore.sh), [`.github/workflows/ci.yml`](.github/workflows/ci.yml).

> [!NOTE]
> **Умовні позначення.** Блоки `powershell` — для Windows PowerShell, блоки `bash` — для Linux (Ubuntu/Debian) та macOS. Якщо команда однакова для обох ОС, наведено один блок. Після кожного критичного кроку є блок **«✅ Очікуваний результат / Як перевірити»**. Усі команди (якщо не сказано інше) виконуються **з кореня репозиторію** `edu-auto-grader/`.

---

## Зміст

- [Розділ 1. Архітектура розгортання та різниця між Dev і Prod](#розділ-1-архітектура-розгортання-та-різниця-між-dev-і-prod)
  - [1.1. Схема компонентів](#11-схема-компонентів)
  - [1.2. Порівняльна таблиця Dev vs Prod](#12-порівняльна-таблиця-dev-vs-prod)
  - [1.3. Ізоляція середовищ](#13-ізоляція-середовищ)
  - [1.4. Звідки бекенд бере налаштування](#14-звідки-бекенд-бере-налаштування)
- [Розділ 2. Запуск DEV-середовища (локальна розробка)](#розділ-2-запуск-dev-середовища-локальна-розробка)
  - [2.1. Системні вимоги](#21-системні-вимоги)
  - [2.2. Клонування та підготовка `.env`](#22-клонування-та-підготовка-env)
  - [2.3. Крок 1 — PostgreSQL 16 у Docker](#23-крок-1--postgresql-16-у-docker)
  - [2.4. Крок 2 — Backend (FastAPI)](#24-крок-2--backend-fastapi)
  - [2.5. Крок 3 — Frontend (React + Vite)](#25-крок-3--frontend-react--vite)
  - [2.6. Крок 4 — Перший вхід і стартові акаунти](#26-крок-4--перший-вхід-і-стартові-акаунти)
  - [2.7. Щоденна розробка та перевірка якості](#27-щоденна-розробка-та-перевірка-якості)
  - [2.8. Зупинка та скидання dev-стеку](#28-зупинка-та-скидання-dev-стеку)
- [Розділ 3. Запуск PROD-середовища (бойовий деплой)](#розділ-3-запуск-prod-середовища-бойовий-деплой)
  - [3.1. Вимоги до сервера та встановлення Docker](#31-вимоги-до-сервера-та-встановлення-docker)
  - [3.2. Крок 1 — Файл секретів `.env.production`](#32-крок-1--файл-секретів-envproduction)
  - [3.3. Крок 2 — Збірка та запуск контейнерів](#33-крок-2--збірка-та-запуск-контейнерів)
  - [3.4. Крок 3 — Ініціалізація бойової БД](#34-крок-3--ініціалізація-бойової-бд)
  - [3.5. Крок 4 — Чеклист безпеки після першого запуску](#35-крок-4--чеклист-безпеки-після-першого-запуску)
  - [3.6. Крок 5 — Публікація в мережу та HTTPS](#36-крок-5--публікація-в-мережу-та-https)
- [Розділ 4. Щоденна експлуатація Prod (Day-2 Operations)](#розділ-4-щоденна-експлуатація-prod-day-2-operations)
  - [4.1. Безпечне оновлення версії](#41-безпечне-оновлення-версії)
  - [4.2. Резервне копіювання та відновлення](#42-резервне-копіювання-та-відновлення)
  - [4.3. Очищення старих файлів робіт (Retention Policy)](#43-очищення-старих-файлів-робіт-retention-policy)
  - [4.4. Моніторинг і логи](#44-моніторинг-і-логи)
  - [4.5. Зміна налаштувань працюючого стеку](#45-зміна-налаштувань-працюючого-стеку)
- [Розділ 5. Усунення типових несправностей (Troubleshooting)](#розділ-5-усунення-типових-несправностей-troubleshooting)
- [Додаток. Швидка довідка](#додаток-швидка-довідка)

---

## Розділ 1. Архітектура розгортання та різниця між Dev і Prod

### 1.1. Схема компонентів

```mermaid
flowchart LR
    subgraph DEV["DEV (локальна машина розробника)"]
        B1["Браузер"] -->|"http://localhost:5173"| V["Vite dev server :5173"]
        V -->|"проксі /api, /media"| U["uvicorn --reload :8000 (з вихідного коду)"]
        U -->|"127.0.0.1:5432"| P1[("postgres (контейнер edu_auto_grader_db)")]
        U --> F1["backend/uploads/ (локальний диск)"]
    end
```

```mermaid
flowchart LR
    subgraph PROD["PROD (Docker Compose project edu-auto-grader-prod)"]
        B2["Браузер"] -->|"HTTPS (опційно, зовнішній Caddy/Nginx)"| RP["Reverse Proxy :443"]
        RP -->|"APP_HTTP_PORT (8080)"| N["frontend: Nginx :80 (edu_auto_grader_prod_frontend)"]
        B2 -.->|"LAN: http://IP:8080"| N
        N -->|"/api/, /media/courses/"| API["backend: uvicorn 2 workers :8000 (edu_auto_grader_prod_backend)"]
        API -->|"мережа internal"| DB[("db: postgres:16-alpine (edu_auto_grader_prod_db)")]
        API --> VOL1[("том uploads_data_prod → /app/uploads")]
        DB --> VOL2[("том postgres_data_prod")]
    end
```

У prod назовні публікується **лише один порт** — `APP_HTTP_PORT` контейнера `frontend` (Nginx). Бекенд (`8000`) і PostgreSQL (`5432`) доступні тільки у внутрішній Docker-мережі `internal` (оголошена з `internal: true`, тобто без виходу назовні).

### 1.2. Порівняльна таблиця Dev vs Prod

| Аспект | **Dev** (`docker-compose.yml` + локальний код) | **Prod** (`docker-compose.prod.yml`) |
| :--- | :--- | :--- |
| Compose-проєкт | `edu-auto-grader` (за назвою каталогу репозиторію) | `edu-auto-grader-prod` (задано явно: `name: edu-auto-grader-prod`) |
| PostgreSQL | Сервіс `postgres`, контейнер `edu_auto_grader_db`, образ `postgres:16-alpine` | Сервіс `db`, контейнер `edu_auto_grader_prod_db`, образ `postgres:16-alpine` |
| Облікові дані БД | `POSTGRES_USER=postgres`, `POSTGRES_PASSWORD=postgres`, `POSTGRES_DB=edu_auto_grader` (за замовчуванням) | `POSTGRES_USER=edu_grader` (за замовчуванням), `POSTGRES_PASSWORD` — **обов'язковий**, `POSTGRES_DB=edu_auto_grader` |
| Том БД (фактичне ім'я Docker volume) | `postgres_data` → `edu-auto-grader_postgres_data` | `postgres_data_prod` → `edu-auto-grader-prod_postgres_data_prod` |
| Backend | `uvicorn app.main:app --app-dir backend --reload` з `backend/.venv` на хості | Контейнер `edu_auto_grader_prod_backend` (`python:3.12-slim`), `uvicorn --workers 2 --proxy-headers`, користувач `appuser` |
| Frontend | `npm --prefix frontend run dev` (Vite dev server, HMR) | Контейнер `edu_auto_grader_prod_frontend`: статична збірка SPA за `nginx:1.27-alpine` |
| Відкриті порти на хості | `127.0.0.1:5432` (БД), `8000` (API, uvicorn), `5173` (Vite) | Лише `APP_HTTP_PORT` (за замовчуванням `8080` → `80` у контейнері) |
| Файли робіт студентів (`UPLOADS_DIR`) | `backend/uploads/` (значення за замовчуванням) | `/app/uploads` у контейнері ← том `uploads_data_prod` (`edu-auto-grader-prod_uploads_data_prod`) |
| Файл налаштувань | `.env` у **поточному робочому каталозі** (рекомендовано — корінь репозиторію); файл опційний | `.env.production` (передається через `--env-file .env.production`) |
| `APP_ENV` | `development` (за замовчуванням у `config.py`) | `production` (жорстко задано в `docker-compose.prod.yml`, не з `.env.production`) |
| `JWT_SECRET_KEY` | Дозволено значення за замовчуванням `change-me-in-production-super-secret-jwt-key-32b` | **Обов'язковий**, ≥ 32 символи і не дорівнює значенню за замовчуванням, інакше бекенд не стартує |
| CORS | `["http://localhost:5173","http://127.0.0.1:5173"]` (за замовчуванням) | `CORS_ORIGINS` — **обов'язковий** (JSON-масив) |
| Проксування `/api` і `/media` | Vite proxy → `http://localhost:8000` | Nginx: `location /api/` і `location /media/courses/` → `http://backend:8000` |
| Ліміт тіла запиту на проксі | Немає (Vite) | `client_max_body_size 35m` у `frontend/nginx.conf` |
| Health-check | Вручну: `GET /api/v1/health/ready` | Docker `HEALTHCHECK` для `db`, `backend` і `frontend` (статус `healthy`) |
| `mdbtools` / шрифти DejaVu | Потрібно ставити вручну (лише Linux) | Вбудовано в образ бекенду (`mdbtools`, `fonts-dejavu-core`) |

### 1.3. Ізоляція середовищ

Dev і Prod можуть співіснувати навіть на одній машині, бо вони не перетинаються за жодним ресурсом:

1. **Різні Compose-проєкти.** `docker-compose.prod.yml` має `name: edu-auto-grader-prod`, тому всі його ресурси отримують префікс `edu-auto-grader-prod_` (мережі `edu-auto-grader-prod_internal`, `edu-auto-grader-prod_edge`, томи `edu-auto-grader-prod_postgres_data_prod`, `edu-auto-grader-prod_uploads_data_prod`). Dev-стек використовує префікс за назвою каталогу (`edu-auto-grader_postgres_data`).
2. **Різні імена контейнерів.** `edu_auto_grader_db` (dev) проти `edu_auto_grader_prod_db` / `edu_auto_grader_prod_backend` / `edu_auto_grader_prod_frontend` (prod).
3. **Різні порти.** Dev займає `127.0.0.1:5432`, `8000`, `5173`; prod — лише `8080` (або інший `APP_HTTP_PORT`). Prod-БД узагалі не публікує порт.
4. **Різні файли змінних.** `docker compose` без `-f` читає `docker-compose.yml` і `.env`; prod-команди завжди містять `-f docker-compose.prod.yml --env-file .env.production`.

**Як переконатися, що dev і prod не перетинаються:**

```bash
docker ps --format "table {{.Names}}\t{{.Status}}\t{{.Ports}}"
docker volume ls --filter name=edu-auto-grader
```

✅ **Очікуваний результат:** dev-контейнер `edu_auto_grader_db` показує `127.0.0.1:5432->5432/tcp`; `edu_auto_grader_prod_db` показує лише `5432/tcp` (без прив'язки до хоста); `edu_auto_grader_prod_frontend` — `0.0.0.0:8080->80/tcp`. Серед томів окремо присутні `edu-auto-grader_postgres_data` і `edu-auto-grader-prod_postgres_data_prod`.

> [!IMPORTANT]
> Усі prod-команди `docker compose` **обов'язково** містять `-f docker-compose.prod.yml --env-file .env.production`. Без `--env-file` Compose не зможе підставити обов'язкові змінні і завершиться помилкою `required variable POSTGRES_PASSWORD is missing a value` (навіть для `ps` чи `logs`). Без `-f` ви взагалі керуватимете dev-стеком.

Щоб не набирати довгий префікс, можна створити локальний скорочений виклик (це лише зручність вашої оболонки, не частина репозиторію):

```bash
# Linux: додати в ~/.bashrc
alias dcp='docker compose -f docker-compose.prod.yml --env-file .env.production'
# приклад: dcp ps
```

```powershell
# Windows PowerShell: додати в $PROFILE
function dcp { docker compose -f docker-compose.prod.yml --env-file .env.production @args }
# приклад: dcp ps
```

Далі в документі команди наведено **в повній формі**, щоб їх можна було копіювати без налаштованого скорочення.

### 1.4. Звідки бекенд бере налаштування

Бекенд використовує `pydantic-settings` (`backend/app/core/config.py`, клас `Settings`):

- Змінні читаються зі **змінних середовища процесу** та з файлу **`.env` у поточному робочому каталозі** (`env_file=".env"`). Змінні середовища мають пріоритет над `.env`.
- Імена **чутливі до регістру** (`case_sensitive=True`) — пишіть їх лише ВЕЛИКИМИ літерами, як у таблицях нижче.
- Невідомі змінні ігноруються (`extra="ignore"`), тому одним `.env` можуть користуватися і `docker compose`, і бекенд.
- Відносні шляхи `UPLOADS_DIR`, `COURSE_CONTENT_DIR`, `COURSE_MEDIA_DIR` резолвляться **відносно каталогу `backend/`** (наприклад, `UPLOADS_DIR=uploads` → `backend/uploads`).

У **prod**-контейнер бекенду потрапляють **лише** змінні, явно перелічені в секції `environment:` сервісу `backend` у `docker-compose.prod.yml` (див. [3.2](#32-крок-1--файл-секретів-envproduction)). Усі інші параметри `config.py` (ліміти завантаження, rate limit входу, час життя токенів) у prod працюють зі значеннями за замовчуванням.

---

## Розділ 2. Запуск DEV-середовища (локальна розробка)

### 2.1. Системні вимоги

| Компонент | Версія | Примітки |
| :--- | :--- | :--- |
| **Docker Desktop** (Windows/macOS) або **Docker Engine + Compose v2 plugin** (Linux) | Актуальна стабільна з підтримкою `docker compose` (v2) | Потрібен лише для PostgreSQL 16. Перевірка: `docker --version`, `docker compose version` |
| **Python** | **3.12** (`requires-python = ">=3.12"` у `backend/pyproject.toml`) | На Windows рекомендовано саме 3.12 (або 3.13): для них гарантовано існують готові бінарні wheels `asyncpg`, `lxml`, `bcrypt` — без потреби в компіляторі C/C++ |
| **Node.js** | **20 LTS** (разом із `npm`) | Ту саму версію використовує CI (`actions/setup-node`, `node-version: "20"`) і `frontend/Dockerfile` (`node:20-alpine`) |
| **Git** | Будь-яка актуальна | Для клонування репозиторію |
| *(Опційно, Linux)* `mdbtools` | З репозиторію дистрибутива | Резервний CLI (`mdb-schema`, `mdb-export`) для `AccdbGrader`: `sudo apt-get install -y mdbtools` |
| *(Опційно, Linux)* `fonts-dejavu-core` | З репозиторію дистрибутива | Кириличний шрифт для PDF-відомостей: `sudo apt-get install -y fonts-dejavu-core` |

Перевірка встановлених інструментів:

```powershell
docker --version; docker compose version; py -3.12 --version; node --version; npm --version; git --version
```

```bash
docker --version && docker compose version && python3.12 --version && node --version && npm --version && git --version
```

✅ **Очікуваний результат:** кожна команда друкує версію; `node --version` починається з `v20.`, Python — `Python 3.12.x`.

### 2.2. Клонування та підготовка `.env`

```bash
git clone <URL_РЕПОЗИТОРІЮ> edu-auto-grader
cd edu-auto-grader
```

**Файл `.env` для dev — опційний.** Значення за замовчуванням у `config.py` і `docker-compose.yml` повністю узгоджені (`postgres` / `postgres` / `edu_auto_grader` / `localhost:5432`), тому «з коробки» все працює без `.env`. Створюйте `.env`, лише якщо потрібно щось змінити.

> [!IMPORTANT]
> **Де лежить `.env`.** Рекомендовано тримати **один файл `.env` у корені репозиторію** і запускати всі команди з кореня (як у цьому посібнику): його читають і `docker compose` (підстановка `POSTGRES_*` у `docker-compose.yml`), і бекенд (`uvicorn`, `alembic`, `python -m app.seed`), бо поточний каталог — корінь. Варіант `backend/.env` спрацює **лише** якщо запускати бекенд-команди з каталогу `backend/`; `docker compose` його не побачить. Файл `.env` уже внесено в `.gitignore`. Шаблону `.env.example` у репозиторії немає — використовуйте приклад нижче.

Приклад `.env` (корінь репозиторію) для dev:

```dotenv
# --- PostgreSQL (читає docker-compose.yml і backend) ---
POSTGRES_USER=postgres
POSTGRES_PASSWORD=postgres
POSTGRES_DB=edu_auto_grader
POSTGRES_HOST=localhost
POSTGRES_PORT=5432

# --- Режим і автентифікація ---
APP_ENV=development
JWT_SECRET_KEY=change-me-in-production-super-secret-jwt-key-32b
ACCESS_TOKEN_EXPIRE_MINUTES=60
REFRESH_TOKEN_EXPIRE_DAYS=7

# --- Захист входу (rate limit) ---
ENABLE_LOGIN_RATE_LIMIT=true
LOGIN_RATE_LIMIT_MAX_ATTEMPTS=10
LOGIN_RATE_LIMIT_WINDOW_SECONDS=60

# --- CORS (JSON-масив) ---
CORS_ORIGINS=["http://localhost:5173","http://127.0.0.1:5173"]

# --- Файли робіт і політика зберігання ---
UPLOADS_DIR=uploads
SUBMISSION_FILE_RETENTION_DAYS=90
SUBMISSION_SUPERSEDED_GRACE_HOURS=24
ENABLE_RETENTION_CLEANUP_TASK=true

# --- Тести-допуски ---
QUIZ_PASS_THRESHOLD_PERCENT=70.0
QUIZ_RETRY_COOLDOWN_SECONDS=300
```

#### Повна таблиця змінних бекенду (`backend/app/core/config.py`)

| Змінна | За замовчуванням | Приклад / допустимі значення | Призначення |
| :--- | :--- | :--- | :--- |
| `APP_ENV` | `development` | `development`, `test`, `production` | Режим. У `production` вмикається перевірка `JWT_SECRET_KEY` |
| `POSTGRES_USER` | `postgres` | `postgres` | Користувач PostgreSQL |
| `POSTGRES_PASSWORD` | `postgres` | `postgres` | Пароль PostgreSQL |
| `POSTGRES_HOST` | `localhost` | `localhost` | Хост БД (у prod — `db`) |
| `POSTGRES_PORT` | `5432` | `5433` | Порт БД. У dev цей же параметр задає порт публікації в `docker-compose.yml` |
| `POSTGRES_DB` | `edu_auto_grader` | `edu_auto_grader` | Назва БД |
| `DATABASE_URL` | *(не задано)* | `postgresql+asyncpg://postgres:postgres@localhost:5432/edu_auto_grader` | Повний async DSN; якщо задано — має пріоритет над `POSTGRES_*` |
| `JWT_SECRET_KEY` | `change-me-in-production-super-secret-jwt-key-32b` | 64 hex-символи | Ключ підпису JWT |
| `JWT_ALGORITHM` | `HS256` | `HS256` | Алгоритм підпису JWT (змінювати не потрібно) |
| `ACCESS_TOKEN_EXPIRE_MINUTES` | `60` | `60` | Час життя access-токена, хв |
| `REFRESH_TOKEN_EXPIRE_DAYS` | `7` | `7` | Час життя refresh-токена, днів |
| `ENABLE_LOGIN_RATE_LIMIT` | `true` | `true` / `false` | Увімкнути обмеження невдалих спроб входу |
| `LOGIN_RATE_LIMIT_MAX_ATTEMPTS` | `10` | `≥ 1` | Макс. кількість невдалих спроб у вікні |
| `LOGIN_RATE_LIMIT_WINDOW_SECONDS` | `60` | `≥ 1` | Довжина ковзного вікна, с |
| `CORS_ORIGINS` | `["http://localhost:5173","http://127.0.0.1:5173"]` | JSON-масив рядків | Дозволені origin фронтенду |
| `UPLOADS_DIR` | `backend/uploads` | `uploads` або абсолютний шлях | Каталог файлів здач студентів |
| `SUBMISSION_FILE_RETENTION_DAYS` | `90` | `≥ 1` | Термін зберігання файлів і `raw_code`, днів |
| `SUBMISSION_SUPERSEDED_GRACE_HOURS` | `24` | `≥ 0` | Мінімальний вік проміжної перездачі перед видаленням її файлу, год |
| `ENABLE_RETENTION_CLEANUP_TASK` | `true` | `true` / `false` | Фоновий воркер очищення (при старті та кожні 24 год) |
| `COURSE_CONTENT_DIR` | `backend/content/courses` | шлях | JSON-пакети 4 курсів (для `app.seed`) |
| `COURSE_MEDIA_DIR` | `backend/content/media` | шлях | Медіафайли, що роздаються через `/media/courses` |
| `QUIZ_PASS_THRESHOLD_PERCENT` | `70.0` | `0.0`–`100.0` | Поріг складання тесту-допуску, % |
| `QUIZ_RETRY_COOLDOWN_SECONDS` | `300` | `≥ 0` (`0` — вимкнути) | Пауза після **невдалої** спроби тесту, с |
| `MAX_OFFICE_UPLOAD_BYTES` | `15728640` (15 МБ) | `≥ 1` | Ліміт `.docx` / `.xlsx` |
| `MAX_ACCDB_UPLOAD_BYTES` | `31457280` (30 МБ) | `≥ 1` | Ліміт `.accdb` |
| `MAX_IMPORT_UPLOAD_BYTES` | `5242880` (5 МБ) | `≥ 1` | Ліміт файлу імпорту студентів (`.docx` / `.txt`) |
| `MAX_ZIP_ENTRIES` | `500` | `≥ 1` | Захист від Zip-бомб: макс. кількість записів в OpenXML-архіві |
| `MAX_ZIP_UNCOMPRESSED_BYTES` | `52428800` (50 МБ) | `≥ 1` | Макс. сумарний розпакований розмір |
| `MAX_ZIP_SINGLE_ENTRY_BYTES` | `20971520` (20 МБ) | `≥ 1` | Макс. розмір одного запису |
| `MAX_ZIP_COMPRESSION_RATIO` | `100.0` | `> 0` | Макс. коефіцієнт стиснення |

**Пояснення до ключових змінних:**

- **`UPLOADS_DIR`** — сюди зберігаються оригінали здач (`.docx`, `.xlsx`, `.accdb`). За замовчуванням це `backend/uploads/` (каталог уже існує в репозиторії з `.gitkeep`). Відносний шлях завжди відраховується від `backend/`, тож `UPLOADS_DIR=uploads` і `UPLOADS_DIR=backend/uploads` дають той самий результат. Каталог має **існувати й бути доступним для запису** — інакше `GET /api/v1/health/ready` поверне `503` з `"uploads": "error"`.
- **`QUIZ_RETRY_COOLDOWN_SECONDS`** — після невдалої спроби тесту-допуску студент може повторити її лише через вказану кількість секунд (за замовчуванням 300 с = 5 хв). Під час паузи API повертає `429` з кодом `QUIZ_RETRY_COOLDOWN` і заголовком `Retry-After`. Для зручної локальної розробки можна задати `0`.
- **`LOGIN_RATE_LIMIT_*`** — після `LOGIN_RATE_LIMIT_MAX_ATTEMPTS` невдалих входів протягом `LOGIN_RATE_LIMIT_WINDOW_SECONDS` для пари «IP + email» API повертає `429` з кодом `TOO_MANY_LOGIN_ATTEMPTS`. Успішний вхід скидає лічильник. Лічильник зберігається в пам'яті процесу (скидається при перезапуску бекенду).
- **`SUBMISSION_FILE_RETENTION_DAYS`** — через стільки днів фізичний файл здачі та `raw_code` HTML-робіт очищуються, а оцінки, звіт перевірки та дані антиплагіату залишаються в БД (див. [4.3](#43-очищення-старих-файлів-робіт-retention-policy)).

#### Змінні фронтенду

Фронтенд використовує єдину змінну **`VITE_API_BASE_URL`** (у `frontend/src/api/client.ts`, за замовчуванням `/api/v1`). Змінної `VITE_API_URL` у проєкті **немає**. Для dev файл `frontend/.env` **не потрібен**: відносний шлях `/api/v1` проксується Vite на бекенд. У prod значення `/api/v1` передається як build-arg у `docker-compose.prod.yml`.

### 2.3. Крок 1 — PostgreSQL 16 у Docker

Переконайтеся, що Docker Desktop запущено (Windows/macOS), і виконайте з кореня репозиторію:

```bash
docker compose up -d
docker compose ps
```

Перегляд логів БД:

```bash
docker compose logs --tail=50 postgres
```

✅ **Очікуваний результат:**

- у `docker compose ps` контейнер `edu_auto_grader_db` має статус `Up ... (healthy)` (health-check `pg_isready` виконується кожні 5 с, тож статус `healthy` з'являється за 5–30 с);
- у логах — рядок `database system is ready to accept connections`;
- колонка `PORTS` показує `127.0.0.1:5432->5432/tcp`.

> [!NOTE]
> Порт опубліковано як `127.0.0.1:5432`, тобто dev-БД **слухає лише локальний інтерфейс** і недоступна з інших комп'ютерів мережі. Якщо порт `5432` зайнятий локальним PostgreSQL, задайте в `.env` `POSTGRES_PORT=5433` — ця змінна одночасно змінить порт публікації в `docker-compose.yml` і порт підключення бекенду.

### 2.4. Крок 2 — Backend (FastAPI)

#### 2.4.1. Віртуальне середовище та залежності

Залежності описані в `backend/pyproject.toml`; група `dev` додає `ruff`, `mypy`, `pytest`, `pytest-asyncio`, `httpx`, `types-defusedxml`. Пакет встановлюється в editable-режимі, тому `app` імпортується з будь-якого каталогу.

**Windows PowerShell:**

```powershell
py -3.12 -m venv backend/.venv
.\backend\.venv\Scripts\Activate.ps1
python -m pip install --upgrade pip
pip install -e "./backend[dev]"
```

> [!TIP]
> Якщо `Activate.ps1` блокується політикою виконання (`running scripts is disabled on this system`), виконайте один раз: `Set-ExecutionPolicy -Scope CurrentUser -ExecutionPolicy RemoteSigned`.

**Linux / macOS:**

```bash
python3.12 -m venv backend/.venv
source backend/.venv/bin/activate
python -m pip install --upgrade pip
pip install -e "./backend[dev]"
```

✅ **Очікуваний результат:** `pip` завершується рядком `Successfully installed ... edu-auto-grader-backend-0.1.0 ...`. Перевірка: `python -c "import app, fastapi; print(fastapi.__version__)"` → `0.115.6`.

> [!IMPORTANT]
> Усі наступні бекенд-команди виконуються **в активованому `backend/.venv`** (у запрошенні терміналу видно `(.venv)`) і **з кореня репозиторію**.

#### 2.4.2. Міграції БД (Alembic)

`backend/alembic.ini` використовує шляхи відносно власного розташування (`%(here)s`), а `backend/alembic/env.py` бере DSN із `Settings` (тобто з `.env` / змінних середовища), тому запуск із кореня виглядає так:

```bash
alembic -c backend/alembic.ini upgrade head
alembic -c backend/alembic.ini current
```

✅ **Очікуваний результат:** `upgrade head` друкує рядки `Running upgrade ... -> 0001_initial_schema ...` … `-> 0005_practical_rules_review`; `current` показує поточну ревізію з позначкою `(head)` (на момент написання — `0005_practical_rules_review (head)`). Історію міграцій можна переглянути командою `alembic -c backend/alembic.ini history`.

#### 2.4.3. Перевірка та наповнення БД контентом (`app.seed`)

CLI `python -m app.seed` має рівно три прапорці:

| Прапорець | Дія |
| :--- | :--- |
| *(без прапорців)* | Ідемпотентно створює групу `КН-31`, 5 стартових користувачів і 4 курси, **якщо їх ще немає**. Існуючі курси не змінює |
| `--dry-run` | Лише валідує JSON-пакети 4 курсів (`backend/content/courses/*.json`) і правила `GradingRule`, **без підключення до PostgreSQL** |
| `--sync-courses` | Те саме, що без прапорців, **плюс неруйнівна in-place синхронізація** вже існуючих курсів, модулів, тестів і практичних із JSON. Користувачі, групи, спроби тестів (`QuizAttempt`) і здачі (`Submission`) з оцінками й коментарями зберігаються |
| `--allow-destructive-module-delete` | Використовується **лише разом із `--sync-courses`**: дозволяє видаляти модулі/практичні, вилучені з JSON, **навіть якщо за ними вже є здачі чи спроби тестів** (пов'язані файли в `uploads/` теж видаляються). Без цього прапорця такі модулі пропускаються з попередженням у лозі |

```bash
python -m app.seed --dry-run
python -m app.seed --sync-courses
```

✅ **Очікуваний результат:**

```text
[seed:DRY-RUN] group=КН-31 users=5 courses=4 modules=40 questions=241 practicals=37 variants=254
[seed:SYNCED] group=КН-31 users=5 courses=4 modules=40 questions=241 practicals=37 variants=254
```

(Числа відображають поточний контент у `backend/content/courses/` і змінюватимуться разом із ним.) На свіжій БД `--sync-courses` сам створює всі курси, тож окремо запускати `python -m app.seed` без прапорців не обов'язково.

#### 2.4.4. Запуск FastAPI з hot-reload

```bash
uvicorn app.main:app --app-dir backend --reload --host 0.0.0.0 --port 8000
```

> [!TIP]
> `--host 0.0.0.0` робить API доступним з інших пристроїв у вашій мережі. Якщо це не потрібно, безпечніше використовувати `--host 127.0.0.1`.

Перевірка готовності (в іншому терміналі):

```powershell
curl.exe -s http://localhost:8000/api/v1/health/ready
# або
Invoke-RestMethod http://localhost:8000/api/v1/health/ready
```

```bash
curl -s http://localhost:8000/api/v1/health/ready
```

✅ **Очікуваний результат:**

- у терміналі uvicorn: `Uvicorn running on http://0.0.0.0:8000` і `Application startup complete.`;
- відповідь readiness: `{"status":"ready","database":"ok","uploads":"ok"}` (HTTP 200). Якщо БД або `UPLOADS_DIR` недоступні — HTTP `503` і `"status":"not_ready"` з полем `details`;
- Swagger UI відкривається на **http://localhost:8000/docs** (OpenAPI-схема — `http://localhost:8000/api/v1/openapi.json`);
- також доступні liveness-ендпоінти `GET /health` та `GET /api/v1/health` → `{"status":"ok","version":"0.1.0"}`.

### 2.5. Крок 3 — Frontend (React + Vite)

В **окремому** терміналі (бекенд має продовжувати працювати):

```bash
npm --prefix frontend ci
npm --prefix frontend run dev
```

`npm ci` встановлює точні версії з `frontend/package-lock.json` (так само, як CI та Docker-збірка). `npm --prefix frontend install` теж підходить, але може оновити lock-файл.

**Як працює проксування** (фактичний `frontend/vite.config.ts`):

- dev-сервер слухає порт **`5173`**;
- запити на `/api/*` проксуються на `http://localhost:8000` (`changeOrigin: true`);
- запити на `/media/*` (зокрема `/media/courses/...` — ілюстрації та PDF лекцій) проксуються на `http://localhost:8000`.

Завдяки цьому фронтенд і API працюють з одного origin (`http://localhost:5173`), і окремий `frontend/.env` не потрібен.

✅ **Очікуваний результат:** Vite друкує `Local: http://localhost:5173/`. Інтерфейс відкривається на **http://localhost:5173** і показує сторінку входу. У DevTools → Network запити йдуть на `http://localhost:5173/api/v1/...` і отримують відповіді від бекенду.

> [!TIP]
> Щоб відкрити dev-фронтенд з іншого пристрою в мережі, запустіть `npm --prefix frontend run dev -- --host` (стандартний прапорець Vite) і відкрийте `http://<IP_ПК>:5173`.

### 2.6. Крок 4 — Перший вхід і стартові акаунти

`app.seed` створює академічну групу **`КН-31`** і 5 облікових записів (з `backend/app/seed.py`):

| Роль | Email (логін) | Пароль | ПІБ | Група / № у списку |
| :--- | :--- | :--- | :--- | :--- |
| `admin` | `admin@kpefk.lcloud.in.ua` | `Admin123!` | Адміністратор Системи | — |
| `teacher` | `teacher@kpefk.lcloud.in.ua` | `Teacher123!` | Коваленко Олександр Петрович | — |
| `student` | `student1@kpefk.lcloud.in.ua` | `Student123!` | Бондаренко Ірина Василівна | `КН-31` / №1 |
| `student` | `student2@kpefk.lcloud.in.ua` | `Student123!` | Мельник Дмитро Сергійович | `КН-31` / №2 |
| `student` | `student3@kpefk.lcloud.in.ua` | `Student123!` | Шевченко Максим Андрійович | `КН-31` / №3 |

✅ **Як перевірити:** увійдіть як `teacher@kpefk.lcloud.in.ua` — у списку курсів мають бути 4 дисципліни (`word`, `excel`, `access`, `html`). Увійдіть як `student1@...` — відкрийте модуль, складіть тест-допуск (поріг 70 %) і перевірте, що практична робота розблокувалася.

> [!WARNING]
> Ці паролі публічні (вони є в коді та документації). Використовуйте їх **лише локально**. У prod їх потрібно змінити одразу після першого запуску — див. [3.5](#35-крок-4--чеклист-безпеки-після-першого-запуску).

### 2.7. Щоденна розробка та перевірка якості

Типовий щоденний запуск (БД уже створена, залежності встановлені):

```powershell
docker compose up -d
.\backend\.venv\Scripts\Activate.ps1
alembic -c backend/alembic.ini upgrade head      # якщо підтягнули нові міграції
uvicorn app.main:app --app-dir backend --reload --host 0.0.0.0 --port 8000
# в іншому терміналі:
npm --prefix frontend run dev
```

```bash
docker compose up -d
source backend/.venv/bin/activate
alembic -c backend/alembic.ini upgrade head      # якщо підтягнули нові міграції
uvicorn app.main:app --app-dir backend --reload --host 0.0.0.0 --port 8000
# в іншому терміналі:
npm --prefix frontend run dev
```

Перевірки якості (ті самі, що в `.github/workflows/ci.yml`):

```bash
# Backend (в активованому backend/.venv)
ruff check backend
mypy --strict backend/app
mypy --strict backend/tests
pytest -c backend/pyproject.toml

# Frontend
npm --prefix frontend run typecheck
npm --prefix frontend run lint
npm --prefix frontend run build
```

✅ **Очікуваний результат:** `ruff` → `All checks passed!`; `mypy` → `Success: no issues found in N source files`; `pytest` — усі тести `passed`; `typecheck` і `lint` завершуються без помилок; `build` створює `frontend/dist/`.

> [!NOTE]
> Тести бекенду використовують in-memory SQLite-адаптер (`backend/tests/conftest.py`), тому **не потребують** запущеного PostgreSQL. Параметр `-c backend/pyproject.toml` гарантує, що з кореня репозиторію підхопиться конфігурація pytest (`asyncio_mode = "auto"`, `testpaths`), як у CI.

Після `git pull` з новими залежностями повторіть `pip install -e "./backend[dev]"` і `npm --prefix frontend ci`; після змін JSON-курсів — `python -m app.seed --sync-courses`.

### 2.8. Зупинка та скидання dev-стеку

Зупинити бекенд і фронтенд — `Ctrl+C` у відповідних терміналах. Зупинити PostgreSQL **зі збереженням даних**:

```bash
docker compose down
```

✅ **Очікуваний результат:** контейнер `edu_auto_grader_db` видалено, том `edu-auto-grader_postgres_data` залишився (`docker volume ls`). Наступний `docker compose up -d` підніме БД з усіма даними.

> [!CAUTION]
> **`docker compose down -v` БЕЗПОВОРОТНО ВИДАЛЯЄ локальну dev-базу даних** (том `edu-auto-grader_postgres_data`): усіх користувачів, курси, спроби тестів, здачі та оцінки. Виконуйте лише тоді, коли свідомо хочете почати «з нуля». Ця команда стосується тільки dev-проєкту і не зачіпає prod-томи `edu-auto-grader-prod_*`. Файли в `backend/uploads/` вона **не** видаляє — за потреби очистіть їх вручну.

Повне скидання dev-БД:

```bash
docker compose down -v
docker compose up -d
alembic -c backend/alembic.ini upgrade head
python -m app.seed --sync-courses
```

---

## Розділ 3. Запуск PROD-середовища (бойовий деплой)

### 3.1. Вимоги до сервера та встановлення Docker

**Операційна система:** Ubuntu Server 22.04 LTS або 24.04 LTS (рекомендовано), Debian 12; або Windows 10/11 / Windows Server із Docker Desktop (Linux-контейнери).

**Рекомендовані ресурси** (орієнтир для коледжу на кілька сотень студентів):

| Ресурс | Мінімум | Рекомендовано | Коментар |
| :--- | :--- | :--- | :--- |
| CPU | 2 vCPU | 4 vCPU | Бекенд запускає 2 воркери `uvicorn`; парсинг `.accdb`/`.docx` навантажує CPU |
| RAM | 2 ГБ | 4 ГБ | Збірка фронтенду (`npm run build` з Monaco Editor) — найбільш вимогливий до пам'яті етап |
| Диск | 20 ГБ SSD | 40+ ГБ SSD | Образи Docker (~1–2 ГБ), PostgreSQL (зазвичай сотні МБ), том `uploads_data_prod` і локальні бекапи |

Оцінка обсягу `uploads`: `кількість_студентів × кількість_практичних × середній_розмір_файлу × (1 + частка_перездач)`. Обсяг обмежується політикою зберігання (90 днів) і автоочищенням проміжних перездач. Закладайте ще стільки ж місця під бекапи (`backups/`, за замовчуванням зберігаються 14 днів).

#### Встановлення Docker Engine + Compose v2 plugin (Ubuntu)

```bash
sudo apt-get update
sudo apt-get install -y ca-certificates curl git
sudo install -m 0755 -d /etc/apt/keyrings
sudo curl -fsSL https://download.docker.com/linux/ubuntu/gpg -o /etc/apt/keyrings/docker.asc
sudo chmod a+r /etc/apt/keyrings/docker.asc
echo "deb [arch=$(dpkg --print-architecture) signed-by=/etc/apt/keyrings/docker.asc] https://download.docker.com/linux/ubuntu $(. /etc/os-release && echo "$VERSION_CODENAME") stable" \
  | sudo tee /etc/apt/sources.list.d/docker.list > /dev/null
sudo apt-get update
sudo apt-get install -y docker-ce docker-ce-cli containerd.io docker-buildx-plugin docker-compose-plugin

# Дозволити поточному користувачу працювати з Docker без sudo (потрібен перелогін)
sudo usermod -aG docker "$USER"
newgrp docker
```

*(Для Debian замініть `linux/ubuntu` на `linux/debian` в обох URL.)*

```bash
docker --version
docker compose version
docker run --rm hello-world
```

✅ **Очікуваний результат:** версії Docker Engine і `Docker Compose version v2.x` (або новіше); `hello-world` друкує `Hello from Docker!`.

#### Розміщення коду на сервері

```bash
sudo mkdir -p /opt/edu-auto-grader
sudo chown "$USER":"$USER" /opt/edu-auto-grader
git clone <URL_РЕПОЗИТОРІЮ> /opt/edu-auto-grader
cd /opt/edu-auto-grader
```

Далі всі prod-команди виконуються з `/opt/edu-auto-grader` (або з кореня репозиторію на Windows-сервері).

> [!NOTE]
> Скрипти `scripts/*.sh` зберігаються в Git із закінченнями рядків LF. Клонуйте репозиторій **безпосередньо на Linux-сервері**. Якщо копіювати робочу копію з Windows, де Git перетворив файли на CRLF, bash видасть помилку `$'\r': command not found` (див. [Розділ 5](#розділ-5-усунення-типових-несправностей-troubleshooting)).

### 3.2. Крок 1 — Файл секретів `.env.production`

#### Створення файлу та права доступу

```bash
cp .env.production.example .env.production
chmod 600 .env.production
```

```powershell
Copy-Item .env.production.example .env.production
# Обмежити доступ лише поточним користувачем
icacls .env.production /inheritance:r /grant:r "$($env:USERNAME):(R,W)"
```

`.env.production` уже внесено в `.gitignore` — **ніколи не комітьте його**.

#### Генерація криптостійких секретів

**Linux** — одним рядком згенерувати й одразу підставити у файл:

```bash
sed -i "s|^JWT_SECRET_KEY=.*|JWT_SECRET_KEY=$(openssl rand -hex 32)|" .env.production
sed -i "s|^POSTGRES_PASSWORD=.*|POSTGRES_PASSWORD=$(openssl rand -hex 24)|" .env.production
```

(`openssl rand -hex 32` → 32 випадкові байти = 64 hex-символи; `openssl rand -hex 24` → 48 hex-символів.)

**Windows PowerShell:**

```powershell
function New-HexSecret([int]$Bytes = 32) {
  $b = New-Object byte[] $Bytes
  [System.Security.Cryptography.RandomNumberGenerator]::Create().GetBytes($b)
  -join ($b | ForEach-Object { $_.ToString('x2') })
}
$lines = (Get-Content .env.production) `
  -replace '^JWT_SECRET_KEY=.*', "JWT_SECRET_KEY=$(New-HexSecret 32)" `
  -replace '^POSTGRES_PASSWORD=.*', "POSTGRES_PASSWORD=$(New-HexSecret 24)"
[System.IO.File]::WriteAllLines("$PWD\.env.production", $lines)   # UTF-8 без BOM
```

> [!WARNING]
> Використовуйте для `POSTGRES_PASSWORD` **лише літери та цифри** (hex-вивід саме такий). Пароль підставляється в DSN `postgresql+asyncpg://user:password@host:port/db` без URL-кодування, тому символи `@ : / # ? %` зламають підключення. Також уникайте символу `$` у будь-яких значеннях — Docker Compose трактує його як підстановку змінної.

#### Розбір кожної змінної `.env.production.example`

| Змінна | Значення в шаблоні | Що вказати | Пояснення |
| :--- | :--- | :--- | :--- |
| `APP_HTTP_PORT` | `8080` | `8080`, `80` або `127.0.0.1:8080` | Порт хоста, на який публікується Nginx (`"${APP_HTTP_PORT:-8080}:80"`). Значення `127.0.0.1:8080` прив'язує порт лише до локального інтерфейсу — використовуйте його, коли перед системою стоїть reverse proxy на тому ж сервері (див. [3.6](#36-крок-5--публікація-в-мережу-та-https)) |
| `POSTGRES_USER` | `edu_grader` | `edu_grader` | Власник БД. Застосовується **лише при першій ініціалізації тому** `postgres_data_prod` |
| `POSTGRES_PASSWORD` | `REPLACE_WITH_STRONG_POSTGRES_PASSWORD` | результат `openssl rand -hex 24` | **Обов'язкова** (`:?` у compose). Також застосовується лише при першій ініціалізації тому — подальша зміна у файлі не змінює пароль у вже створеній БД |
| `POSTGRES_DB` | `edu_auto_grader` | `edu_auto_grader` | Назва БД |
| `JWT_SECRET_KEY` | `REPLACE_WITH_AT_LEAST_32_CHARS_RANDOM_SECRET_KEY` | результат `openssl rand -hex 32` | **Обов'язкова.** Ключ підпису access/refresh-токенів. Зміна ключа робить недійсними всі видані токени (усім доведеться увійти знову) |
| `CORS_ORIGINS` | `["http://localhost:8080"]` | `["https://grader.example.edu.ua"]` або `["http://192.168.1.50:8080"]` | **Обов'язкова.** JSON-масив точних origin (схема + хост + порт, без кінцевого `/`) |
| `SUBMISSION_FILE_RETENTION_DAYS` | `90` | `90` | Термін зберігання файлів робіт і `raw_code`, днів (`≥ 1`) |
| `SUBMISSION_SUPERSEDED_GRACE_HOURS` | `24` | `24` | Через скільки годин видаляються файли проміжних перездач (`≥ 0`) |
| `ENABLE_RETENTION_CLEANUP_TASK` | `true` | `true` | Фонове автоочищення в бекенді (при старті + кожні 24 год) |
| `QUIZ_PASS_THRESHOLD_PERCENT` | `70.0` | `70.0` | Поріг тесту-допуску, % |
| `QUIZ_RETRY_COOLDOWN_SECONDS` | `300` | `300` | Пауза після невдалої спроби тесту, с |
| `RETENTION_BACKUP_DAYS` | `14` | `14` | Скільки днів зберігати бекапи. **Увага:** `scripts/backup.sh` бере це значення зі **змінної середовища оболонки**, а не з `.env.production` автоматично — передавайте його явно (див. [4.2](#42-резервне-копіювання-та-відновлення)) |

**Змінні, які задаються в `docker-compose.prod.yml` жорстко** (їх не потрібно і не можна перевизначити через `.env.production`):

| Змінна | Значення | Де |
| :--- | :--- | :--- |
| `APP_ENV` | `production` | `backend.environment` |
| `POSTGRES_HOST` / `POSTGRES_PORT` | `db` / `5432` | `backend.environment` |
| `UPLOADS_DIR` | `/app/uploads` | `backend.environment` (+ `ENV` у `backend/Dockerfile`) |
| `FORWARDED_ALLOW_IPS` | `"*"` | `backend.environment` — uvicorn довіряє заголовкам `X-Forwarded-*` від Nginx |
| `VITE_API_BASE_URL` | `/api/v1` | build-arg сервісу `frontend` |

**Параметри, які в prod працюють зі значеннями за замовчуванням** (вони відсутні в `environment:` сервісу `backend`, тому додавати їх у `.env.production` марно): `MAX_OFFICE_UPLOAD_BYTES` = 15 МБ, `MAX_ACCDB_UPLOAD_BYTES` = 30 МБ, `MAX_IMPORT_UPLOAD_BYTES` = 5 МБ, `MAX_ZIP_*`, `ENABLE_LOGIN_RATE_LIMIT=true`, `LOGIN_RATE_LIMIT_MAX_ATTEMPTS=10`, `LOGIN_RATE_LIMIT_WINDOW_SECONDS=60`, `ACCESS_TOKEN_EXPIRE_MINUTES=60`, `REFRESH_TOKEN_EXPIRE_DAYS=7`. Щоб змінити будь-який із них у prod, його потрібно додати в секцію `environment:` сервісу `backend` у `docker-compose.prod.yml`.

#### Чому бекенд не стартує з неправильним `JWT_SECRET_KEY`

`docker-compose.prod.yml` встановлює `APP_ENV: production`. У `Settings` (`backend/app/core/config.py`) є валідатор `_validate_production_security`, який при `APP_ENV=production` кидає `ValueError`, якщо `JWT_SECRET_KEY`:

- дорівнює значенню за замовчуванням `change-me-in-production-super-secret-jwt-key-32b`, або
- після обрізання пробілів коротший за **32 символи** (`MIN_PRODUCTION_JWT_SECRET_LENGTH = 32`).

Об'єкт `settings` створюється під час імпорту модуля, тому uvicorn-воркери падають ще до старту застосунку з повідомленням `У режимі production необхідно задати надійний JWT_SECRET_KEY довжиною щонайменше 32 символів, відмінний від значення за замовчуванням.`, а контейнер (`restart: unless-stopped`) безкінечно перезапускається. Якщо ж змінну не задати взагалі, Compose відмовиться запускатися ще раніше: `required variable JWT_SECRET_KEY is missing a value`.

> [!CAUTION]
> Плейсхолдер із шаблону `REPLACE_WITH_AT_LEAST_32_CHARS_RANDOM_SECRET_KEY` має 48 символів і **пройде** валідацію! Валідатор не захищає від того, що ви забули замінити шаблонне значення, — тому обов'язково виконайте перевірку нижче.

#### Перевірка файлу перед запуском

```bash
grep -n "REPLACE_WITH" .env.production || echo "OK: плейсхолдерів немає"
docker compose -f docker-compose.prod.yml --env-file .env.production config --quiet && echo "OK: compose-конфігурація валідна"
```

```powershell
if (Select-String -Path .env.production -Pattern 'REPLACE_WITH') { Write-Warning 'Залишились плейсхолдери!' } else { 'OK: плейсхолдерів немає' }
docker compose -f docker-compose.prod.yml --env-file .env.production config --quiet; if ($LASTEXITCODE -eq 0) { 'OK: compose-конфігурація валідна' }
```

✅ **Очікуваний результат:** обидві перевірки друкують `OK: ...`.

### 3.3. Крок 2 — Збірка та запуск контейнерів

```bash
docker compose -f docker-compose.prod.yml --env-file .env.production up -d --build
```

Перша збірка триває кілька хвилин (завантаження базових образів, `pip install`, `npm ci`, `vite build`).

**Що відбувається всередині:**

| Сервіс | Що робиться |
| :--- | :--- |
| `db` | `postgres:16-alpine`; при першому старті ініціалізує том `postgres_data_prod` з `POSTGRES_USER` / `POSTGRES_PASSWORD` / `POSTGRES_DB`. Health-check — `pg_isready` кожні 10 с. Порт назовні **не** публікується |
| `backend` | Образ `python:3.12-slim` + системні пакети **`mdbtools`** (резервний парсинг `.accdb`) і **`fonts-dejavu-core`** (кирилиця в PDF-відомостях `fpdf2`). Встановлюється пакет з `pyproject.toml`, копіюються `alembic/`, `app/`, `content/`. Процес запускається від непривілейованого `appuser` командою `uvicorn app.main:app --host 0.0.0.0 --port 8000 --workers 2 --proxy-headers`. Стартує лише після `db: service_healthy`. Health-check — `GET http://127.0.0.1:8000/api/v1/health/ready` кожні 30 с (`start_period: 15s`) |
| `frontend` | Multi-stage: `node:20-alpine` виконує `npm ci` + `npm run build` (Monaco Editor бандлиться локально — **жодних запитів до зовнішніх CDN**), далі статика копіюється в `nginx:1.27-alpine`. Nginx: `client_max_body_size 35m`, `gzip`, заголовки `X-Content-Type-Options`, `X-Frame-Options`, `Referrer-Policy`, проксування `/api/` і `/media/courses/` на `backend:8000`, SPA-fallback на `index.html`. Стартує лише після `backend: service_healthy` |

Перевірка стану:

```bash
docker compose -f docker-compose.prod.yml --env-file .env.production ps
```

✅ **Очікуваний результат:** три контейнери `edu_auto_grader_prod_db`, `edu_auto_grader_prod_backend`, `edu_auto_grader_prod_frontend` у стані `Up ... (healthy)` (бекенду може знадобитися до ~45 с). Якщо `backend` у стані `Restarting` — див. [Розділ 5](#розділ-5-усунення-типових-несправностей-troubleshooting).

Перевірка готовності через Nginx (підставте свій `APP_HTTP_PORT`, якщо він не `8080`):

```bash
curl -f http://localhost:8080/api/v1/health/ready
curl -sI http://localhost:8080/ | head -n 1
```

```powershell
curl.exe -f http://localhost:8080/api/v1/health/ready
Invoke-WebRequest http://localhost:8080/ -UseBasicParsing | Select-Object StatusCode
```

✅ **Очікуваний результат:** `{"status":"ready","database":"ok","uploads":"ok"}` і `HTTP/1.1 200 OK` (або `StatusCode 200`) для головної сторінки.

> [!NOTE]
> Readiness-перевірка контролює лише підключення до БД (`SELECT 1`) і запис у `/app/uploads`, тому бекенд стає `healthy` ще **до** застосування міграцій. При найпершому старті фоновий воркер автоочищення може записати в лог помилку (таблиць ще немає) — це очікувано: воркер повторить спробу в наступному циклі або після перезапуску бекенду.

### 3.4. Крок 3 — Ініціалізація бойової БД

У контейнері `WORKDIR` — `/app`, де лежить `alembic.ini`, тому прапорець `-c` не потрібен.

```bash
# 1. Міграції схеми
docker compose -f docker-compose.prod.yml --env-file .env.production exec backend alembic upgrade head

# 2. Перевірка версії схеми
docker compose -f docker-compose.prod.yml --env-file .env.production exec backend alembic current

# 3. (опційно) Валідація JSON-контенту без запису в БД
docker compose -f docker-compose.prod.yml --env-file .env.production exec backend python -m app.seed --dry-run

# 4. Наповнення 4 курсами, групою КН-31 і стартовими акаунтами
docker compose -f docker-compose.prod.yml --env-file .env.production exec backend python -m app.seed --sync-courses

# 5. Перезапуск бекенду, щоб автоочищення одразу стартувало на готовій схемі
docker compose -f docker-compose.prod.yml --env-file .env.production restart backend
```

✅ **Очікуваний результат:**

- `alembic current` → ревізія з позначкою `(head)` (зараз `0005_practical_rules_review (head)`);
- seed → `[seed:SYNCED] group=КН-31 users=5 courses=4 modules=40 questions=241 practicals=37 variants=254`;
- після перезапуску `ps` знову показує `backend` як `healthy`, а за адресою `http://<сервер>:8080` відкривається сторінка входу, після входу викладача видно 4 курси.

### 3.5. Крок 4 — Чеклист безпеки після першого запуску

Виконайте **всі** пункти **до** того, як видавати доступ студентам.

- [ ] **1. Змініть паролі `admin` і `teacher`.** Увійдіть під кожним акаунтом → у верхній панелі натисніть **«Змінити пароль»** → введіть поточний і новий пароль. Бекенд (`POST /api/v1/auth/change-password`) збереже новий хеш і **інкрементує `token_version`**, через що всі раніше видані токени цього користувача (інші браузери/пристрої) стають недійсними.
- [ ] **2. Змініть паролі тестових студентів** `student1..3@kpefk.lcloud.in.ua`: увійдіть як `admin` → сторінка керування користувачами (`AdminUsersPage`) → редагування користувача з новим паролем (або скидання пароля, `POST /api/v1/admin/users/{user_id}/reset-password`). Після зміни адміністратором користувачу також інкрементується `token_version` і виставляється `must_change_password`.

  > [!WARNING]
  > **Не видаляйте й не перейменовуйте** стартові акаунти (email) як спосіб захисту: `python -m app.seed --sync-courses` (який запускається при кожному оновленні) **створює заново** будь-який відсутній стартовий акаунт із паролем за замовчуванням. Існуючим акаунтам seed паролі **не** скидає — тому правильний захист саме зміна паролів.

- [ ] **3. Перевірте `JWT_SECRET_KEY` та `CORS_ORIGINS`** (фактичні значення, які бачить бекенд):

  ```bash
  docker compose -f docker-compose.prod.yml --env-file .env.production exec backend \
    python -c "from app.core.config import settings; print(settings.APP_ENV, len(settings.JWT_SECRET_KEY), settings.CORS_ORIGINS)"
  ```

  ✅ Очікується `production 64 ['https://grader.example.edu.ua']` — лише ваш реальний домен/IP, без `localhost`, якщо доступ іде не з самого сервера.

- [ ] **4. Переконайтеся, що PostgreSQL не відкритий назовні:**

  ```bash
  sudo ss -tulpn | grep -E ':5432|:8080'
  docker ps --format "table {{.Names}}\t{{.Ports}}"
  ```

  ✅ Очікується: порт `5432` **відсутній** у виводі `ss`; у `docker ps` для `edu_auto_grader_prod_db` колонка `PORTS` містить лише `5432/tcp` (без `0.0.0.0:`); назовні слухає тільки `8080` (`docker-proxy`). На Windows-сервері: `Get-NetTCPConnection -State Listen -LocalPort 5432,8080 -ErrorAction SilentlyContinue`.

- [ ] **5. Права на секрети:** `ls -l .env.production` → `-rw-------`.
- [ ] **6. Брандмауер.** Відкрийте лише потрібні порти (SSH, 80/443 для reverse proxy).

  > [!IMPORTANT]
  > Порти, опубліковані Docker (`ports:`), **оминають правила UFW** (Docker додає власні правила iptables). Тому `ufw deny 8080` не закриє порт контейнера. Якщо перед системою стоїть reverse proxy на тому ж сервері, задайте в `.env.production` `APP_HTTP_PORT=127.0.0.1:8080` і виконайте `docker compose -f docker-compose.prod.yml --env-file .env.production up -d` — тоді Nginx-контейнер буде доступний лише локально, а назовні — тільки через проксі.

- [ ] **7. Налаштуйте щоденний бекап** ([4.2](#42-резервне-копіювання-та-відновлення)) і зробіть перший бекап вручну.

### 3.6. Крок 5 — Публікація в мережу та HTTPS

#### Варіант А. Локальна мережа коледжу (LAN) по IP сервера

1. Дізнайтеся IP сервера: `ip -4 addr show` (Linux) або `ipconfig` (Windows), напр. `192.168.1.50`.
2. У `.env.production`: `APP_HTTP_PORT=8080` і `CORS_ORIGINS=["http://192.168.1.50:8080"]`.
3. Застосуйте: `docker compose -f docker-compose.prod.yml --env-file .env.production up -d`.
4. Відкрийте з комп'ютера в аудиторії: `http://192.168.1.50:8080`.

✅ **Як перевірити:** з іншого ПК у мережі `curl -f http://192.168.1.50:8080/api/v1/health/ready` повертає `{"status":"ready",...}`. На Windows-сервері з Docker Desktop може знадобитися дозволити вхідні підключення на порт у Windows Defender Firewall.

> [!NOTE]
> У режимі LAN трафік (паролі, файли) передається без шифрування. Для доступу з інтернету обов'язково використовуйте варіант Б з HTTPS.

#### Варіант Б. Інтернет через зовнішній Reverse Proxy з HTTPS

Схема: `Інтернет → :443 Caddy/Nginx (TLS) → 127.0.0.1:8080 (контейнер frontend) → backend`. Підготовка:

1. DNS-запис `A` для домену (напр. `grader.example.edu.ua`) вказує на публічний IP сервера; порти 80 і 443 відкриті.
2. У `.env.production`: `APP_HTTP_PORT=127.0.0.1:8080` і `CORS_ORIGINS=["https://grader.example.edu.ua"]`.
3. `docker compose -f docker-compose.prod.yml --env-file .env.production up -d`.

**Б1. Caddy (автоматичний Let's Encrypt HTTPS)** — встановлення на Ubuntu:

```bash
sudo apt-get install -y debian-keyring debian-archive-keyring apt-transport-https curl
curl -1sLf 'https://dl.cloudsmith.io/public/caddy/stable/gpg.key' | sudo gpg --dearmor -o /usr/share/keyrings/caddy-stable-archive-keyring.gpg
curl -1sLf 'https://dl.cloudsmith.io/public/caddy/stable/debian.deb.txt' | sudo tee /etc/apt/sources.list.d/caddy-stable.list
sudo apt-get update && sudo apt-get install -y caddy
```

Мінімальний `/etc/caddy/Caddyfile`:

```caddyfile
grader.example.edu.ua {
    encode gzip

    request_body {
        max_size 35MB
    }

    reverse_proxy 127.0.0.1:8080
}
```

```bash
sudo caddy validate --config /etc/caddy/Caddyfile
sudo systemctl reload caddy
```

Caddy сам отримує й поновлює сертифікат Let's Encrypt, перенаправляє HTTP → HTTPS і передає заголовки `X-Forwarded-For` / `X-Forwarded-Proto` / `X-Forwarded-Host`.

**Б2. Nginx на хості** (сертифікат через `certbot`):

```nginx
# /etc/nginx/sites-available/edu-auto-grader
server {
    listen 80;
    server_name grader.example.edu.ua;
    return 301 https://$host$request_uri;
}

server {
    listen 443 ssl;
    server_name grader.example.edu.ua;

    ssl_certificate     /etc/letsencrypt/live/grader.example.edu.ua/fullchain.pem;
    ssl_certificate_key /etc/letsencrypt/live/grader.example.edu.ua/privkey.pem;

    # Має бути не менше за ліміт внутрішнього Nginx (35m), інакше великі .accdb отримають 413
    client_max_body_size 35m;

    location / {
        proxy_pass http://127.0.0.1:8080;
        proxy_http_version 1.1;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        # Перезаписуємо (а не доповнюємо) X-Forwarded-For реальною IP клієнта
        proxy_set_header X-Forwarded-For $remote_addr;
        proxy_set_header X-Forwarded-Proto $scheme;
        proxy_read_timeout 120s;
        proxy_send_timeout 120s;
    }
}
```

```bash
sudo apt-get install -y nginx certbot python3-certbot-nginx
# Для першого отримання сертифіката можна тимчасово залишити лише server-блок на :80, далі:
sudo certbot --nginx -d grader.example.edu.ua
sudo ln -s /etc/nginx/sites-available/edu-auto-grader /etc/nginx/sites-enabled/
sudo nginx -t && sudo systemctl reload nginx
```

> [!NOTE]
> **Чому `X-Forwarded-For $remote_addr`.** Бекенд працює з `--proxy-headers` і `FORWARDED_ALLOW_IPS="*"`, тож IP клієнта (за яким рахується rate limit входу) uvicorn бере з `X-Forwarded-For`. Внутрішній Nginx доповнює цей заголовок (`$proxy_add_x_forwarded_for`), тому зовнішній проксі має **записувати туди реальну IP клієнта**, а не пропускати значення, надіслане браузером. HTTPS завершується на зовнішньому проксі; внутрішній Nginx передає бекенду `X-Forwarded-Proto` зі своїм `$scheme` (`http`).

✅ **Як перевірити:** `curl -fI https://grader.example.edu.ua/` → `HTTP/2 200` (Caddy) або `HTTP/1.1 200 OK` (Nginx); `curl -f https://grader.example.edu.ua/api/v1/health/ready` → `{"status":"ready",...}`; у браузері немає попереджень про сертифікат; завантаження `.accdb` розміром до 30 МБ проходить без `413`.

---

## Розділ 4. Щоденна експлуатація Prod (Day-2 Operations)

### 4.1. Безпечне оновлення версії

Оновлення **не зачіпає** томи `postgres_data_prod` і `uploads_data_prod` — пересобираються лише образи `backend` і `frontend`.

```bash
cd /opt/edu-auto-grader

# 1. Бекап ПЕРЕД оновленням (обов'язково)
./scripts/backup.sh

# 2. Отримати нову версію коду
git pull origin main

# 3. Перевірити, чи не з'явилися нові змінні/параметри
git diff HEAD@{1} -- .env.production.example docker-compose.prod.yml

# 4. Перезібрати й перезапустити контейнери
docker compose -f docker-compose.prod.yml --env-file .env.production up -d --build

# 5. Застосувати нові міграції схеми
docker compose -f docker-compose.prod.yml --env-file .env.production exec backend alembic upgrade head

# 6. Неруйнівно синхронізувати оновлений навчальний контент
docker compose -f docker-compose.prod.yml --env-file .env.production exec backend python -m app.seed --sync-courses

# 7. Перевірити готовність і стан
curl -f http://localhost:8080/api/v1/health/ready
docker compose -f docker-compose.prod.yml --env-file .env.production ps

# 8. (опційно) Прибрати старі образи, що залишилися після збірки
docker image prune -f
```

✅ **Очікуваний результат:** усі 3 контейнери `healthy`, `alembic current` показує `(head)`, seed друкує `[seed:SYNCED] ...`, readiness повертає `ready`. Оцінки, здачі й файли студентів на місці.

> [!TIP]
> Щоб скоротити простій, спершу зберіть образи, поки стара версія ще працює: `docker compose -f docker-compose.prod.yml --env-file .env.production build`, а потім виконайте крок 4 — він лише перестворить контейнери (кілька секунд). Якщо після оновлення сайт віддає `502`, виконайте `docker compose -f docker-compose.prod.yml --env-file .env.production restart frontend`.

**Неруйнівність `--sync-courses`.** Курси оновлюються in-place (upsert) за `slug` курсу та `order_index` модуля: змінюються лекції, питання тестів, практичні, варіанти й правила оцінювання з `backend/content/courses/*.json`, але **зберігаються** користувачі, групи, спроби тестів і здачі з оцінками та коментарями викладачів. Якщо модуль/практичну прибрано з JSON, а за ними вже є прогрес студентів, вони **не видаляються** — у лозі з'являється попередження `Пропущено видалення зайвого модуля ... Для примусового видалення передайте --allow-destructive-module-delete.`

> [!CAUTION]
> `--allow-destructive-module-delete` **безповоротно видаляє** такі модулі/практичні разом зі спробами тестів, здачами, оцінками та файлами робіт у `uploads/`. Використовуйте лише свідомо, після свіжого бекапу, і ніколи — як частину рутинного оновлення.

**Відкат.** Якщо нова версія непрацездатна і міграції ще не застосовувались — `git checkout <попередній_коміт>` і повторіть крок 4. Якщо міграції вже застосовано, найнадійніший шлях — повернути попередній код і відновити БД з бекапу, зробленого на кроці 1 ([4.2](#42-резервне-копіювання-та-відновлення)).

### 4.2. Резервне копіювання та відновлення

#### Ручний бекап (`scripts/backup.sh`)

Скрипт працює з prod-проєктом і створює у `BACKUP_DIR` два файли:

- `db_YYYYMMDD_HHMMSS.dump` — `pg_dump -Fc` (custom-формат) з контейнера `db`;
- `uploads_YYYYMMDD_HHMMSS.tar.gz` — архів `/app/uploads` з контейнера `backend` (том `uploads_data_prod`).

Мітка часу — у **UTC**. Порожній дамп/архів вважається помилкою (скрипт завершується з кодом `1`). Після успіху видаляються файли `db_*.dump` і `uploads_*.tar.gz`, старші за `RETENTION_BACKUP_DAYS` днів.

Параметри (лише змінні середовища, аргументів командного рядка немає):

| Змінна | За замовчуванням | Призначення |
| :--- | :--- | :--- |
| `COMPOSE_PROJECT_NAME` | `edu-auto-grader-prod` | Compose-проєкт (`-p`) |
| `COMPOSE_FILE` | `docker-compose.prod.yml` | Compose-файл (`-f`) |
| `ENV_FILE` | `.env.production` | Передається як `--env-file`, якщо файл існує |
| `BACKUP_DIR` | `./backups` | Каталог бекапів (вже в `.gitignore`) |
| `RETENTION_BACKUP_DAYS` | `14` | Скільки днів зберігати бекапи (ціле `≥ 0`) |

Скрипт використовує відносні шляхи, тому запускайте його **з кореня репозиторію**; контейнери `db` і `backend` мають бути запущені.

```bash
cd /opt/edu-auto-grader
chmod +x scripts/backup.sh scripts/restore.sh
./scripts/backup.sh

# З власним каталогом і терміном зберігання
RETENTION_BACKUP_DAYS=30 BACKUP_DIR=/var/backups/edu-auto-grader ./scripts/backup.sh
```

✅ **Очікуваний результат:**

```text
[backup] Starting backup at 20261125_010000 UTC...
[backup] Completed successfully:
  - Database: ./backups/db_20261125_010000.dump (1.2M)
  - Uploads:  ./backups/uploads_20261125_010000.tar.gz (350M)
  - Retention policy: delete backups older than 14 days
```

Перевірка цілісності бекапу:

```bash
docker compose -f docker-compose.prod.yml --env-file .env.production exec -T db pg_restore --list < ./backups/db_20261125_010000.dump | head -n 20
tar -tzf ./backups/uploads_20261125_010000.tar.gz | head -n 20
```

> [!TIP]
> Регулярно копіюйте каталог бекапів **за межі сервера** (інший сервер, NAS, хмарне сховище), напр. `rsync -a /var/backups/edu-auto-grader/ backup-user@nas:/backups/edu-auto-grader/`. Бекап на тому ж диску не захистить від виходу диска з ладу.

**Бекап на Windows-сервері.** `backup.sh` — bash-скрипт. Найпростіше запускати його у WSL або Git Bash; у Git Bash обов'язково вимкніть автоконвертацію шляхів: `MSYS_NO_PATHCONV=1 bash scripts/backup.sh`. Еквівалент на чистому PowerShell (без перенаправлення бінарного потоку, яке PowerShell 5.1 пошкоджує):

```powershell
$ts = (Get-Date).ToUniversalTime().ToString('yyyyMMdd_HHmmss')
New-Item -ItemType Directory -Force backups | Out-Null
docker compose -f docker-compose.prod.yml --env-file .env.production exec -T db sh -c 'pg_dump -Fc -U $POSTGRES_USER -d $POSTGRES_DB -f /tmp/backup.dump'
docker cp edu_auto_grader_prod_db:/tmp/backup.dump "backups/db_$ts.dump"
docker compose -f docker-compose.prod.yml --env-file .env.production exec -T db rm -f /tmp/backup.dump
docker compose -f docker-compose.prod.yml --env-file .env.production exec -T backend tar -czf /tmp/uploads.tar.gz -C /app uploads
docker cp edu_auto_grader_prod_backend:/tmp/uploads.tar.gz "backups/uploads_$ts.tar.gz"
docker compose -f docker-compose.prod.yml --env-file .env.production exec -T backend rm -f /tmp/uploads.tar.gz
```

#### Щоденний автобекап у `cron` (Ubuntu)

Користувач, від імені якого працює cron, має входити до групи `docker`.

```bash
sudo mkdir -p /var/backups/edu-auto-grader
sudo chown "$USER":"$USER" /var/backups/edu-auto-grader
sudo touch /var/log/edu-auto-grader-backup.log
sudo chown "$USER":"$USER" /var/log/edu-auto-grader-backup.log
crontab -e
```

Додайте рядок (щодня о 03:00 за часом сервера, з логуванням):

```cron
0 3 * * * cd /opt/edu-auto-grader && RETENTION_BACKUP_DAYS=14 BACKUP_DIR=/var/backups/edu-auto-grader ./scripts/backup.sh >> /var/log/edu-auto-grader-backup.log 2>&1
```

✅ **Як перевірити:** `crontab -l` показує рядок; наступного ранку `tail -n 20 /var/log/edu-auto-grader-backup.log` містить `[backup] Completed successfully:`, а в `/var/backups/edu-auto-grader/` є свіжі `db_*.dump` і `uploads_*.tar.gz`. (На Windows аналогічне розкладання налаштовується в Task Scheduler.)

#### Відновлення (`scripts/restore.sh`)

Синтаксис:

```text
./scripts/restore.sh <db_backup.dump> [uploads_backup.tar.gz] [--yes]
```

- перший аргумент — **обов'язковий** дамп БД;
- другий — опційний архів `uploads`;
- `--yes` — пропустити інтерактивне підтвердження `Continue? [y/N]`;
- підтримуються ті самі змінні `COMPOSE_PROJECT_NAME`, `COMPOSE_FILE`, `ENV_FILE`, що й у `backup.sh`.

Скрипт виконує `pg_restore --clean --if-exists --no-owner --no-privileges` у контейнері `db` (наявні об'єкти БД перезаписуються даними з дампа) і, якщо передано архів, розпаковує його в `/app` контейнера `backend` (перезаписуючи файли в `/app/uploads`).

**А. Відновлення на існуючому сервері:**

```bash
cd /opt/edu-auto-grader

# 1. Зупинити доступ користувачів (бекенд і БД мають працювати — скрипт виконує в них exec)
docker compose -f docker-compose.prod.yml --env-file .env.production stop frontend

# 2. Відновити БД і файли
./scripts/restore.sh ./backups/db_20261125_030000.dump ./backups/uploads_20261125_030000.tar.gz

# 3. Довести схему до версії поточного коду та перезапустити
docker compose -f docker-compose.prod.yml --env-file .env.production exec backend alembic upgrade head
docker compose -f docker-compose.prod.yml --env-file .env.production restart backend
docker compose -f docker-compose.prod.yml --env-file .env.production start frontend

# 4. Перевірка
curl -f http://localhost:8080/api/v1/health/ready
```

**Б. Відновлення на чистому сервері:**

1. Встановіть Docker ([3.1](#31-вимоги-до-сервера-та-встановлення-docker)) і клонуйте репозиторій **тієї ж версії**, з якої зроблено бекап (`git checkout <коміт>`).
2. Перенесіть `.env.production` зі старого сервера (або створіть новий за [3.2](#32-крок-1--файл-секретів-envproduction); новий `JWT_SECRET_KEY` лише змусить усіх увійти заново) і скопіюйте файли бекапу в `./backups/`.
3. Підніміть стек: `docker compose -f docker-compose.prod.yml --env-file .env.production up -d --build` і дочекайтеся `healthy`.
4. **Не** запускайте `seed` — відновіть дані: `./scripts/restore.sh ./backups/db_<TS>.dump ./backups/uploads_<TS>.tar.gz --yes`.
5. `docker compose -f docker-compose.prod.yml --env-file .env.production exec backend alembic upgrade head` і `... restart backend`.
6. Перевірте вхід викладача, журнал групи й можливість завантажити старі здачі.

✅ **Очікуваний результат:** скрипт завершується рядком `[restore] Restore completed successfully.`; readiness → `ready`; оцінки та файли збігаються зі станом на момент бекапу.

> [!WARNING]
> Відновлюйте дамп на **ту саму або старішу** версію коду, з якої його зроблено, і лише потім оновлюйтеся. Якщо в цільовій БД уже є таблиці з новіших міграцій, яких немає в дампі, `pg_restore --clean` їх не видалить, і подальший `alembic upgrade head` може завершитися помилкою `already exists`.

### 4.3. Очищення старих файлів робіт (Retention Policy)

**Як працює автоматично.** Якщо `ENABLE_RETENTION_CLEANUP_TASK=true`, у `lifespan` FastAPI (`backend/app/main.py`) запускається фонова задача `run_periodic_retention_cleanup` — **при старті та кожні 24 години**. Оскільки в prod працюють 2 воркери uvicorn, задачу стартує кожен із них, але цикл захищено `pg_try_advisory_lock`: виконує роботу лише той воркер, що отримав блокування, інший пише в лог `Фонове автоочищення пропущено: блокування вже утримується іншим воркером.`

За один цикл виконуються два етапи:

1. **Прострочені здачі** — старші за `SUBMISSION_FILE_RETENTION_DAYS` (90 днів): з диска видаляється фізичний файл, у БД очищується `raw_code` HTML-робіт.
2. **Проміжні перездачі** — старші за `SUBMISSION_SUPERSEDED_GRACE_HOURS` (24 год): видаляються файли проміжних спроб, **залишаються найкраща й остання** здачі студента.

Записи `submissions` **не видаляються**: `auto_score`, `final_score`, `grading_report`, `teacher_comment`, `extracted_metadata` і `file_hash` залишаються, тому журнал оцінок і перевірка на плагіат за SHA-256-хешем продовжують працювати. Видалення файлів обмежене каталогом `UPLOADS_DIR` (шляхи поза ним пропускаються як небезпечні).

**Ручний запуск (CLI `python -m app.services.retention_service`):**

| Прапорець | Дія |
| :--- | :--- |
| `--dry-run` | Показати, скільки робіт буде очищено, **без** видалення файлів і змін у БД |
| `--retention-days N` | Перевизначити термін зберігання (`N ≥ 1`), інакше — `SUBMISSION_FILE_RETENTION_DAYS` |
| `--superseded-grace-hours N` | Перевизначити вік проміжних перездач (`N ≥ 0`), інакше — `SUBMISSION_SUPERSEDED_GRACE_HOURS` |
| `--skip-superseded` | Виконати лише 90-денне очищення, без проміжних перездач |

```bash
# Prod: попередній перегляд
docker compose -f docker-compose.prod.yml --env-file .env.production exec backend python -m app.services.retention_service --dry-run

# Prod: фактичне очищення
docker compose -f docker-compose.prod.yml --env-file .env.production exec backend python -m app.services.retention_service
```

```bash
# Dev (в активованому backend/.venv)
python -m app.services.retention_service --dry-run
```

✅ **Очікуваний результат** (формат рядка; числа — приклад):

```text
[retention:DRY-RUN] retention_days=90 cutoff=2026-08-27T... inspected=12 cleaned=12 deleted_files=0 superseded_cleaned=5 superseded_deleted_files=0 missing_files=0 cleared_raw_code=0 skipped_unsafe=0
```

Якщо цикл саме виконується фоновим воркером, CLI надрукує `[retention:DRY-RUN] skipped_due_to_lock=True` — повторіть пізніше. Попередження Python `RuntimeWarning: 'app.services.retention_service' found in sys.modules ...` під час запуску CLI нешкідливе.

Якщо фонову задачу вимкнено (`ENABLE_RETENTION_CLEANUP_TASK=false`), очищення можна запускати з cron хоста:

```cron
30 4 * * * cd /opt/edu-auto-grader && docker compose -f docker-compose.prod.yml --env-file .env.production exec -T backend python -m app.services.retention_service >> /var/log/edu-auto-grader-retention.log 2>&1
```

### 4.4. Моніторинг і логи

```bash
# Стан і health усіх сервісів
docker compose -f docker-compose.prod.yml --env-file .env.production ps

# Логи бекенду в реальному часі (помилки старту, автоочищення, запити)
docker compose -f docker-compose.prod.yml --env-file .env.production logs -f --tail=100 backend

# Логи Nginx (access/error, 413, 502)
docker compose -f docker-compose.prod.yml --env-file .env.production logs --tail=100 frontend

# Логи PostgreSQL
docker compose -f docker-compose.prod.yml --env-file .env.production logs --tail=100 db

# Деталі health-check конкретного контейнера
docker inspect --format '{{json .State.Health}}' edu_auto_grader_prod_backend

# Споживання CPU/RAM
docker stats --no-stream

# Місце на диску: образи, контейнери, томи (з розмірами)
docker system df -v
df -h /var/lib/docker

# Розмір БД і каталогу робіт
docker compose -f docker-compose.prod.yml --env-file .env.production exec db \
  sh -c 'psql -U "$POSTGRES_USER" -d "$POSTGRES_DB" -c "SELECT pg_size_pretty(pg_database_size(current_database()));"'
docker compose -f docker-compose.prod.yml --env-file .env.production exec backend du -sh /app/uploads
```

> [!TIP]
> За замовчуванням Docker зберігає логи контейнерів без обмеження розміру. Обмежте їх у `/etc/docker/daemon.json`:
> ```json
> { "log-driver": "json-file", "log-opts": { "max-size": "10m", "max-file": "5" } }
> ```
> Потім `sudo systemctl restart docker` і `docker compose -f docker-compose.prod.yml --env-file .env.production up -d --force-recreate` (налаштування застосовуються до нових контейнерів).

Для зовнішнього моніторингу (Uptime Kuma, Zabbix тощо) використовуйте `GET /api/v1/health/ready`: HTTP `200` — система готова, `503` — проблема з БД або `uploads` (деталі в полі `details`).

### 4.5. Зміна налаштувань працюючого стеку

Після редагування `.env.production` виконайте:

```bash
docker compose -f docker-compose.prod.yml --env-file .env.production up -d
```

Compose перестворить лише ті контейнери, чия конфігурація змінилась. **`restart` не підхоплює нові значення змінних** — він перезапускає контейнер зі старим середовищем.

> [!IMPORTANT]
> Зміна `POSTGRES_USER` / `POSTGRES_PASSWORD` / `POSTGRES_DB` у `.env.production` **не змінює** облікові дані у вже ініціалізованому томі `postgres_data_prod`. Щоб змінити пароль БД, спершу змініть його в самій БД (приклад для `POSTGRES_USER=edu_grader`, `POSTGRES_DB=edu_auto_grader`), а потім у файлі:
> ```bash
> docker compose -f docker-compose.prod.yml --env-file .env.production exec db \
>   psql -U edu_grader -d edu_auto_grader -c "ALTER USER edu_grader WITH PASSWORD 'NEW_HEX_PASSWORD';"
> # потім замініть POSTGRES_PASSWORD у .env.production на NEW_HEX_PASSWORD і виконайте up -d
> ```
> Для dev-БД аналогічно: `docker compose exec postgres psql -U postgres -d edu_auto_grader -c "ALTER USER postgres WITH PASSWORD 'NEW_PASSWORD';"`.

---

## Розділ 5. Усунення типових несправностей (Troubleshooting)

Почніть діагностику з трьох команд:

```bash
docker compose -f docker-compose.prod.yml --env-file .env.production ps
docker compose -f docker-compose.prod.yml --env-file .env.production logs --tail=100 backend
curl -s http://localhost:8080/api/v1/health/ready
```

| # | Симптом / помилка | Причина | Точне рішення |
| :-- | :--- | :--- | :--- |
| 1 | Контейнер `edu_auto_grader_prod_backend` постійно в стані `Restarting`; у лозі `ValueError` / `ValidationError`: `У режимі production необхідно задати надійний JWT_SECRET_KEY довжиною щонайменше 32 символів...` | `APP_ENV=production` + `JWT_SECRET_KEY` коротший за 32 символи або дорівнює `change-me-in-production-super-secret-jwt-key-32b` | Згенеруйте ключ (`openssl rand -hex 32`), запишіть у `.env.production` і виконайте `docker compose -f docker-compose.prod.yml --env-file .env.production up -d` (не `restart`) |
| 2 | Будь-яка prod-команда завершується `required variable POSTGRES_PASSWORD is missing a value` (або `JWT_SECRET_KEY`, `CORS_ORIGINS`) | Команду запущено без `--env-file .env.production`, або змінна порожня у файлі | Завжди використовуйте `docker compose -f docker-compose.prod.yml --env-file .env.production ...`; перевірте файл командою `... config --quiet` |
| 3 | `password authentication failed for user "edu_grader"` (prod) або `"postgres"` (dev); readiness → `"database": "error"` | Пароль у `.env*` змінили **після** ініціалізації тому БД (PostgreSQL бере `POSTGRES_PASSWORD` лише при першому створенні тому); або сплутали dev/prod (запуск без `-f`, інший `.env`) | Поверніть попередній пароль у файл або змініть його в БД через `ALTER USER` ([4.5](#45-зміна-налаштувань-працюючого-стеку)). Перевірте, який том використовується: `docker volume ls --filter name=edu-auto-grader`. У dev, якщо дані не потрібні: `docker compose down -v` (видаляє dev-БД!) |
| 4 | `413 Request Entity Too Large` при завантаженні `.accdb` / `.docx` | (а) HTML-сторінка 413 від Nginx — файл > 35 МБ або зовнішній проксі має менший ліміт (у Nginx за замовчуванням лише `1m`); (б) JSON-відповідь 413 від бекенду — перевищено ліміт застосунку: `.docx`/`.xlsx` 15 МБ, `.accdb` 30 МБ, імпорт студентів 5 МБ | (а) На зовнішньому Nginx задайте `client_max_body_size 35m;` (Caddy: `request_body { max_size 35MB }`) і перезавантажте проксі. (б) Попросіть студента зменшити файл (стиснути зображення, «Стиснути й відновити» БД Access) або додайте `MAX_ACCDB_UPLOAD_BYTES` / `MAX_OFFICE_UPLOAD_BYTES` в `environment:` сервісу `backend` |
| 5 | `502 Bad Gateway` у браузері | Бекенд ще стартує, впав (див. #1, #3), або після перестворення контейнера `backend` внутрішній Nginx тримає стару IP-адресу | `docker compose -f docker-compose.prod.yml --env-file .env.production ps` → дочекайтеся `healthy` бекенду; перегляньте `logs backend`; якщо бекенд `healthy`, а 502 лишається — `docker compose -f docker-compose.prod.yml --env-file .env.production restart frontend` |
| 6 | `Bind for 0.0.0.0:8080 failed: port is already allocated` / `address already in use` (або `127.0.0.1:5432` у dev) | Порт зайнятий іншим процесом (інший вебсервер, локальний PostgreSQL, ще один Compose-стек) | Знайдіть процес: Linux `sudo ss -tulpn` + `grep :8080`; Windows `Get-NetTCPConnection -LocalPort 8080` → `Get-Process -Id <OwningProcess>`. Зупиніть його або змініть порт: prod — `APP_HTTP_PORT=8081` у `.env.production` (+ оновіть `CORS_ORIGINS`); dev — `POSTGRES_PORT=5433` у `.env` |
| 7 | Після входу список курсів порожній | Не виконано наповнення БД (`app.seed`) | Prod: `docker compose -f docker-compose.prod.yml --env-file .env.production exec backend python -m app.seed --sync-courses`. Dev: `python -m app.seed --sync-courses` |
| 8 | Помилки `alembic upgrade head`: `Can't locate revision identified by ...`, `relation "..." already exists`, `connection refused`; або API падає з `relation "..." does not exist` | Міграції не застосовано; код старіший за схему БД (відкат коду після міграцій); схему створено поза Alembic або відновлено дамп поверх новішої схеми; БД не запущена | Перевірте `alembic current` і `alembic history` (dev — з `-c backend/alembic.ini`). Не застосовано → `alembic upgrade head`. `Can't locate revision` → поверніть код до версії, що містить цю ревізію. `already exists` після restore → відновіть дамп на ту саму версію коду ([4.2](#42-резервне-копіювання-та-відновлення)). `connection refused` у dev → `docker compose up -d` і `docker compose ps` |
| 9 | PDF-відомість без кирилиці (порожні квадрати/помилка шрифту) на Linux dev-машині | `ExportService` шукає TTF-шрифти (Windows: Arial/Calibri/Tahoma; Linux: DejaVuSans, Liberation, FreeSans); якщо жодного немає — fallback на `Helvetica` без кирилиці | Linux: `sudo apt-get install -y fonts-dejavu-core`. У prod-образі бекенду пакет уже встановлено; на Windows використовуються системні шрифти |
| 10 | `.accdb` не перевіряється на Windows dev (`Не вдалося розібрати структуру бази даних Access ...`) або відсутні запити/зв'язки, хоча в prod той самий файл працює | Основний парсер `access-parser` кросплатформний, але резервні `mdb-schema` / `mdb-export` (`mdbtools`) на Windows відсутні | Перевіряйте такі файли в Linux/WSL з `sudo apt-get install -y mdbtools` або через prod-подібний Docker-образ бекенду, де `mdbtools` уже встановлено |
| 11 | `429 Too Many Requests` при вході, код `TOO_MANY_LOGIN_ATTEMPTS` | ≥ 10 невдалих спроб за 60 с для пари «IP + email» (in-memory лімітер, окремий у кожному воркері uvicorn) | Дочекайтеся часу із заголовка `Retry-After` (до 60 с) і введіть правильний пароль; адміністратор може скинути пароль користувачу. Перезапуск бекенду обнуляє лічильники. У dev можна вимкнути: `ENABLE_LOGIN_RATE_LIMIT=false` у `.env` |
| 12 | `429` при відправці тесту-допуску, код `QUIZ_RETRY_COOLDOWN` («зачекайте X хв Y сек») | Після **невдалої** спроби діє пауза `QUIZ_RETRY_COOLDOWN_SECONDS` (300 с = 5 хв) | Це очікувана поведінка — дочекатися завершення паузи. Змінити тривалість: `QUIZ_RETRY_COOLDOWN_SECONDS` у `.env.production` → `up -d` (`0` вимикає паузу) |
| 13 | У консолі браузера `blocked by CORS policy: No 'Access-Control-Allow-Origin' header` після зміни домену/порту | Фронтенд відкрито з origin, якого немає в `CORS_ORIGINS` (актуально, коли сторінка і API на різних origin; у стандартній схемі через Nginx вони збігаються) | Додайте точний origin (схема + хост + порт, без `/` у кінці) у JSON-масив, напр. `CORS_ORIGINS=["https://grader.example.edu.ua","http://192.168.1.50:8080"]`, і виконайте `up -d`. Перевірка — команда з [3.5, п. 3](#35-крок-4--чеклист-безпеки-після-першого-запуску) |
| 14 | `./scripts/backup.sh: line 2: $'\r': command not found` або `/usr/bin/env: 'bash\r': No such file or directory` | Скрипт має CRLF-закінчення (скопійовано з Windows) | `sed -i 's/\r$//' scripts/backup.sh scripts/restore.sh` або клонуйте репозиторій безпосередньо на Linux |
| 15 | `permission denied while trying to connect to the Docker daemon socket` | Користувач не в групі `docker` | `sudo usermod -aG docker "$USER"` і перелогіньтеся (або `newgrp docker`) |
| 16 | Readiness → `503`, `"uploads": "error"` (`Каталог UPLOADS_DIR не існує` / `недоступний для запису`) | Dev: каталог `UPLOADS_DIR` не створено. Prod: порушено права на том після ручних маніпуляцій | Dev: створіть каталог (`mkdir backend/uploads`) або виправте `UPLOADS_DIR`. Prod: `docker compose -f docker-compose.prod.yml --env-file .env.production exec -u root backend chown -R appuser:appuser /app/uploads` |
| 17 | `.\backend\.venv\Scripts\Activate.ps1 cannot be loaded because running scripts is disabled` | Політика виконання PowerShell | `Set-ExecutionPolicy -Scope CurrentUser -ExecutionPolicy RemoteSigned` |

---

## Додаток. Швидка довідка

**Контейнери, сервіси, томи**

| Середовище | Сервіс | Контейнер | Том (фактичне ім'я) | Порт на хості |
| :--- | :--- | :--- | :--- | :--- |
| Dev | `postgres` | `edu_auto_grader_db` | `edu-auto-grader_postgres_data` | `127.0.0.1:5432` |
| Prod | `db` | `edu_auto_grader_prod_db` | `edu-auto-grader-prod_postgres_data_prod` | — |
| Prod | `backend` | `edu_auto_grader_prod_backend` | `edu-auto-grader-prod_uploads_data_prod` → `/app/uploads` | — |
| Prod | `frontend` | `edu_auto_grader_prod_frontend` | — | `APP_HTTP_PORT` (`8080`) |

**Найчастіші команди**

| Дія | Dev | Prod |
| :--- | :--- | :--- |
| Підняти | `docker compose up -d` + uvicorn + `npm --prefix frontend run dev` | `docker compose -f docker-compose.prod.yml --env-file .env.production up -d --build` |
| Міграції | `alembic -c backend/alembic.ini upgrade head` | `docker compose -f docker-compose.prod.yml --env-file .env.production exec backend alembic upgrade head` |
| Контент курсів | `python -m app.seed --sync-courses` | `docker compose -f docker-compose.prod.yml --env-file .env.production exec backend python -m app.seed --sync-courses` |
| Готовність | `curl http://localhost:8000/api/v1/health/ready` | `curl -f http://localhost:8080/api/v1/health/ready` |
| Логи | `docker compose logs -f postgres` | `docker compose -f docker-compose.prod.yml --env-file .env.production logs -f --tail=100 backend` |
| Бекап | — | `./scripts/backup.sh` |
| Відновлення | — | `./scripts/restore.sh ./backups/db_<TS>.dump ./backups/uploads_<TS>.tar.gz` |
| Очищення файлів | `python -m app.services.retention_service --dry-run` | `docker compose -f docker-compose.prod.yml --env-file .env.production exec backend python -m app.services.retention_service --dry-run` |
| Зупинити | `docker compose down` | `docker compose -f docker-compose.prod.yml --env-file .env.production down` |

> [!CAUTION]
> Ніколи не виконуйте `docker compose -f docker-compose.prod.yml --env-file .env.production down -v` на бойовому сервері — це видалить томи `postgres_data_prod` і `uploads_data_prod`, тобто **всі оцінки, здачі та файли студентів**. Звичайний `down` (без `-v`) дані зберігає.

**Пов'язані документи:** [README.md](README.md) · [TEACHER_GUIDE.md](TEACHER_GUIDE.md) · [ARCHITECTURE.md](ARCHITECTURE.md) · [SPEC.md](SPEC.md)
