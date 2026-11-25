# ARCHITECTURE.md — Технічна архітектура системи

## 1. Структура директорій проєкту

```text
edu-auto-grader/
├── AGENTS.md
├── SPEC.md
├── ARCHITECTURE.md
├── TASKS.md
├── docker-compose.yml
├── backend/
│   ├── pyproject.toml
│   ├── alembic.ini
│   ├── alembic/
│   │   └── versions/
│   ├── content/                     # Статичний контент 4 навчальних курсів
│   │   ├── courses/                 # Валідовані JSON-пакети курсів (word, excel, access, html)
│   │   │   ├── word.json
│   │   │   ├── excel.json
│   │   │   ├── access.json
│   │   │   └── html.json
│   │   └── media/                   # Медіафайли лекцій і практичних (роздача через /media/courses)
│   │       ├── word/
│   │       ├── excel/
│   │       └── access/
│   ├── app/
│   │   ├── main.py                  # Точка входу FastAPI, lifespan (автоочищення файлів), CORS, StaticFiles (/media/courses), exception handlers
│   │   ├── seed.py                  # CLI-імпорт 4 курсів із JSON (--dry-run, --sync-courses)
│   │   ├── core/
│   │   │   ├── config.py            # Налаштування середовища (Pydantic BaseSettings, production-валідація JWT_SECRET_KEY)
│   │   │   ├── database.py          # AsyncEngine, AsyncSessionLocal
│   │   │   ├── rate_limit.py        # Потокобезпечний in-memory sliding-window лімітер невдалих спроб входу
│   │   │   ├── security.py          # Хешування паролів (sha256$+bcrypt), генерація/валідація JWT із token_version
│   │   │   └── exceptions.py        # Доменні винятки системи
│   │   ├── models/                  # SQLAlchemy 2.0 ORM моделі
│   │   │   ├── user.py              # User, AcademicGroup
│   │   │   ├── course.py            # Course, Module, QuizQuestion, Practical
│   │   │   └── progress.py          # QuizAttempt, Submission
│   │   ├── schemas/                 # Pydantic v2 контракти (Request / Response / JSONB)
│   │   │   ├── auth.py
│   │   │   ├── course.py
│   │   │   ├── grading.py           # GradingRule, CriterionResult, GradingReport
│   │   │   └── submission.py
│   │   ├── graders/                 # Ядро автоперевірки (Strategy Pattern)
│   │   │   ├── base.py              # BaseGrader (ABC)
│   │   │   ├── metadata.py          # Екстрактор docProps/core.xml та SHA-256 антиплагіат
│   │   │   ├── docx_grader.py       # Парсер Word (.docx)
│   │   │   ├── xlsx_grader.py       # Парсер Excel (.xlsx)
│   │   │   ├── accdb_grader.py      # Парсер Access (.accdb)
│   │   │   ├── html_grader.py       # Валідатор HTML (BeautifulSoup4)
│   │   │   └── factory.py           # GraderFactory.get_grader(format_type)
│   │   ├── services/                # Бізнес-логіка
│   │   │   ├── quiz_service.py      # Перевірка тесту-допуску
│   │   │   ├── submission_service.py# Оркестрація перевірки, завантаження робіт і збереження результату
│   │   │   ├── retention_service.py # Автоочищення файлів/raw_code через 90 днів (lifespan + CLI) та при видаленні студента
│   │   │   ├── export_service.py    # Генерація .xlsx та .pdf відомостей
│   │   │   └── student_import_service.py # Масовий імпорт студентів (.docx/.txt)
│   │   └── api/
│   │       ├── deps.py              # Залежності get_db, get_current_user, require_role
│   │       └── v1/
│   │           ├── router.py
│   │           ├── auth.py
│   │           ├── admin.py
│   │           ├── courses.py
│   │           ├── practicals.py
│   │           ├── submissions.py
│   │           └── analytics.py
│   └── tests/
│       ├── conftest.py
│       ├── test_admin_api.py
│       ├── test_course_content.py
│       ├── test_graders.py
│       └── test_submissions_api.py
└── frontend/
    ├── package.json
    ├── tsconfig.json
    ├── vite.config.ts
    └── src/
        ├── main.tsx
        ├── App.tsx
        ├── types/                   # TypeScript контракти (синхронізовані з Pydantic)
        │   ├── api.ts
        │   ├── course.ts
        │   └── grading.ts
        ├── api/
        │   └── client.ts            # Axios instance з JWT інтерсепторами
        ├── context/
        │   └── AuthContext.tsx
        ├── components/
        │   ├── layout/              # Sidebar, Navbar, RoleGuard
        │   ├── sandbox/             # HtmlSandbox.tsx (Monaco Editor + iframe preview)
        │   └── grading/             # GradingReportCard.tsx, PlagiarismBadge.tsx
        └── pages/
            ├── LoginPage.tsx
            ├── student/
            │   ├── CoursesPage.tsx
            │   ├── ModuleViewPage.tsx      # Лекція + Тест-допуск + Практична
            │   └── GradebookPage.tsx
            ├── teacher/
            │   ├── CourseEditorPage.tsx
            │   ├── RuleBuilderPage.tsx
            │   └── GroupJournalPage.tsx
            └── admin/
                └── AdminUsersPage.tsx
```

## 2. Схема бази даних (PostgreSQL 16)

### Таблиці та зв'язки
1. **`academic_groups`**
   * `id`: `UUID` (PK)
   * `code`: `VARCHAR(32)` (UNIQUE, NOT NULL, напр. `"КН-31"`)
   * `specialty`: `VARCHAR(128)` (NOT NULL)
   * `course_year`: `SMALLINT` (NOT NULL, `CHECK (course_year BETWEEN 1 AND 4)` — 4 курси навчання коледжу)

2. **`users`**
   * `id`: `UUID` (PK)
   * `email`: `VARCHAR(255)` (UNIQUE, NOT NULL)
   * `password_hash`: `VARCHAR(255)` (NOT NULL)
   * `full_name`: `VARCHAR(255)` (NOT NULL)
   * `role`: `ENUM('student', 'teacher', 'admin')` (NOT NULL)
   * `group_id`: `UUID` (FK -> `academic_groups.id`, NULLABLE, `ON DELETE SET NULL`)
   * `list_number`: `SMALLINT` (NULLABLE — номер студента у журналі групи для розрахунку варіанта)
   * `token_version`: `INTEGER` (NOT NULL, DEFAULT `0` — версія JWT-токенів для відкликання сесій після зміни або скидання пароля)
   * `must_change_password`: `BOOLEAN` (NOT NULL, DEFAULT `false` — прапорець примусової зміни тимчасового пароля)
   * `created_at`: `TIMESTAMPTZ` (DEFAULT `now()`)

3. **`courses`**
   * `id`: `UUID` (PK)
   * `title`: `VARCHAR(255)` (NOT NULL)
   * `slug`: `ENUM('word', 'excel', 'access', 'html')` (UNIQUE, NOT NULL — фіксований перелік із 4 навчальних дисциплін)
   * `description`: `TEXT` (NOT NULL)
   * `teacher_id`: `UUID` (FK -> `users.id`, NOT NULL)

4. **`modules`**
   * `id`: `UUID` (PK)
   * `course_id`: `UUID` (FK -> `courses.id`, NOT NULL, `ON DELETE CASCADE`)
   * `order_index`: `SMALLINT` (NOT NULL)
   * `title`: `VARCHAR(255)` (NOT NULL)
   * `lecture_content`: `TEXT` (NOT NULL — Markdown/HTML текст лекції)

5. **`quiz_questions`**
   * `id`: `UUID` (PK)
   * `module_id`: `UUID` (FK -> `modules.id`, NOT NULL, `ON DELETE CASCADE`)
   * `question_text`: `TEXT` (NOT NULL)
   * `options`: `JSONB` (NOT NULL — масив рядків `["Варіант 1", "Варіант 2", ...]`)
   * `correct_option_index`: `SMALLINT` (NOT NULL)

6. **`quiz_attempts`**
   * `id`: `UUID` (PK)
   * `student_id`: `UUID` (FK -> `users.id`, NOT NULL, `ON DELETE CASCADE`)
   * `module_id`: `UUID` (FK -> `modules.id`, NOT NULL, `ON DELETE CASCADE`)
   * `score_percent`: `NUMERIC(5,2)` (NOT NULL)
   * `passed`: `BOOLEAN` (NOT NULL)
   * `attempted_at`: `TIMESTAMPTZ` (DEFAULT `now()`)

7. **`practicals`**
   * `id`: `UUID` (PK)
   * `module_id`: `UUID` (FK -> `modules.id`, UNIQUE, NOT NULL, `ON DELETE CASCADE`)
   * `title`: `VARCHAR(255)` (NOT NULL)
   * `instructions`: `TEXT` (NOT NULL)
   * `format_type`: `ENUM('docx', 'xlsx', 'accdb', 'html')` (NOT NULL)
   * `max_score`: `NUMERIC(5,2)` (NOT NULL, DEFAULT `10.00`)
   * `variants`: `JSONB` (NOT NULL — масив об'єктів індивідуальних вхідних даних для варіантів)
   * `grading_rules`: `JSONB` (NOT NULL — масив декларативних правил перевірки)

8. **`submissions`**
   * `id`: `UUID` (PK)
   * `practical_id`: `UUID` (FK -> `practicals.id`, NOT NULL, `ON DELETE CASCADE`)
   * `student_id`: `UUID` (FK -> `users.id`, NOT NULL, `ON DELETE CASCADE`)
   * `variant_index`: `SMALLINT` (NOT NULL)
   * `file_path`: `TEXT` (NULLABLE — шлях до завантаженого `.docx`/`.xlsx`/`.accdb`)
   * `raw_code`: `TEXT` (NULLABLE — вихідний код для `html`)
   * `file_hash`: `VARCHAR(64)` (NULLABLE — SHA-256 хеш файлу або нормалізованого коду)
   * `extracted_metadata`: `JSONB` (NOT NULL, DEFAULT `'{}'`)
   * `is_plagiarism_flagged`: `BOOLEAN` (NOT NULL, DEFAULT `false`)
   * `plagiarism_reason`: `TEXT` (NULLABLE)
   * `auto_score`: `NUMERIC(5,2)` (NOT NULL)
   * `final_score`: `NUMERIC(5,2)` (NOT NULL)
   * `grading_report`: `JSONB` (NOT NULL — деталізація по кожному правилу)
   * `teacher_comment`: `TEXT` (NULLABLE)
   * `submitted_at`: `TIMESTAMPTZ` (DEFAULT `now()`)

## 3. Контракти даних та модулів

### 3.1. Контракт JSONB `grading_rules` (Приклад)
```json
[
  {
    "id": "rule_1",
    "type": "xlsx_formula",
    "target": "D12",
    "expected": "SUM(D2:D11)",
    "points": 3.0,
    "description": "Використано функцію SUM для підрахунку підсумку в комірці D12"
  },
  {
    "id": "rule_2",
    "type": "xlsx_chart_exists",
    "target": "Sheet1",
    "expected": "true",
    "points": 2.0,
    "description": "На аркуші побудовано діаграму"
  },
  {
    "id": "rule_3",
    "type": "html_tag_count",
    "target": "table > tr",
    "expected": ">=4",
    "points": 2.5,
    "description": "Таблиця містить щонайменше 4 рядки"
  }
]
```

### 3.2. Інтерфейс ядра перевірки (`backend/app/graders/base.py`)
```python
from abc import ABC, abstractmethod
from pathlib import Path
from app.schemas.grading import GradingRule, GradingReport

class BaseGrader(ABC):
    @abstractmethod
    def evaluate(
        self,
        *,
        file_path: Path | None = None,
        raw_code: str | None = None,
        rules: list[GradingRule],
        variant_data: dict[str, object],
    ) -> GradingReport:
        """Виконує детерміновану перевірку роботи за списком правил."""
        raise NotImplementedError
```

### 3.3. Основні REST API Ендпоінти (`/api/v1`)
| Метод | Шлях | Роль | Призначення |
| :--- | :--- | :--- | :--- |
| `GET` | `/health`, `/api/v1/health` | Public | Liveness-перевірка працездатності API-процесу |
| `GET` | `/api/v1/health/ready` | Public | Readiness-перевірка PostgreSQL (`SELECT 1`) та доступності запису в `UPLOADS_DIR` (`200` / `503`) |
| `POST` | `/auth/login` | Public | Отримання JWT access + refresh токенів (із sliding-window rate limiting на невдалі спроби) |
| `POST` | `/auth/refresh` | Public | Оновлення пари JWT-токенів із перевіркою актуальності `token_version` (`tv`) |
| `POST` | `/auth/change-password` | All Auth | Самостійна зміна пароля, скидання `must_change_password`, інкремент `token_version` та видача нової пари токенів |
| `GET` | `/auth/me` | All Auth | Профіль поточного автентифікованого користувача |
| `GET` | `/courses` | All Auth | Перелік 4 навчальних курсів та прогрес поточного користувача |
| `GET` | `/courses/{course_id}` | All Auth | Детальна інформація про курс та список його модулів із прогресом |
| `POST` | `/courses` | Teacher / Admin | Створення навчального курсу (у межах 4 фіксованих дисциплін `word`/`excel`/`access`/`html`) |
| `PATCH` | `/courses/{course_id}` | Teacher (owner) / Admin | Оновлення назви, опису або (лише для `admin`) викладача курсу |
| `GET` | `/modules/{module_id}` | All Auth | Отримання тексту лекції, питань тесту-допуску, cooldown і статусу доступу до практичної |
| `POST` | `/courses/{course_id}/modules` | Teacher (owner) / Admin | Створення нового навчального модуля з лекцією |
| `PATCH` | `/modules/{module_id}` | Teacher (owner) / Admin | Оновлення заголовка, порядкового номера або лекції модуля |
| `DELETE` | `/modules/{module_id}` | Teacher (owner) / Admin | Видалення модуля курсу (каскадно з тестами, практичною та здачами), перенумерація тем `1..N` і безпечне видалення файлів здач із диска |
| `GET` | `/modules/{module_id}/quiz/questions` | Teacher (owner) / Admin | Перелік питань тесту-допуску модуля разом із правильними відповідями |
| `POST` | `/modules/{module_id}/quiz/questions` | Teacher (owner) / Admin | Додавання тестового питання до модуля |
| `DELETE` | `/quiz/questions/{question_id}` | Teacher (owner) / Admin | Видалення тестового питання |
| `POST` | `/modules/{module_id}/quiz/submit` | Student | Відправка відповідей тесту-допуску (з cooldown при невдачі) та розблокування практичної |
| `GET` | `/practicals/{practical_id}` | Student | Отримання умови та персонального варіанта студента |
| `GET` | `/practicals/{practical_id}/teacher` | Teacher / Admin | Повна конфігурація практичної роботи з усіма варіантами й правилами перевірки |
| `POST` | `/modules/{module_id}/practical` | Teacher (owner) / Admin | Створення або повне оновлення практичної роботи модуля |
| `PATCH` | `/practicals/{practical_id}` | Teacher (owner) / Admin | Часткове оновлення параметрів, варіантів, правил або `needs_rules_review` |
| `DELETE` | `/practicals/{practical_id}` | Teacher (owner) / Admin | Видалення практичної роботи та її здач (зі збереженням модуля, лекції й тесту) і безпечне видалення файлів здач із диска |
| `POST` | `/practicals/{practical_id}/submit` | Student | Завантаження файлу (`multipart/form-data`) або HTML-коду (`JSON`) та миттєва автоперевірка з антиплагіатом |
| `PUT` | `/practicals/{practical_id}/rules` | Teacher (owner) / Admin | Валідація та оновлення JSONB правил автоперевірки (опційно `sync_max_score`) |
| `GET` | `/submissions/me` | All Auth | Історія здач практичних робіт поточного користувача (електронна заліковка) |
| `GET` | `/submissions` | All Auth | Перелік здач із фільтрацією за `practical_id`, `student_id`, `group_id`, `plagiarism_only` |
| `GET` | `/submissions/{submission_id}` | All Auth | Детальний звіт автоперевірки та статус антиплагіату здачі |
| `GET` | `/submissions/{submission_id}/download` | Teacher (owner) / Admin | Завантаження вихідного файлу (`.docx`/`.xlsx`/`.accdb`) або `.html` (з `raw_code`) здачі студента |
| `PATCH` | `/submissions/{submission_id}/grade` | Teacher (owner) / Admin | Ручне коригування оцінки та додавання коментаря викладача |
| `GET` | `/analytics/groups` | Teacher / Admin | Перелік академічних груп коледжу для електронного журналу й експорту |
| `GET` | `/analytics/groups/{group_id}/journal` | Teacher / Admin | Зведена відомість успішності академічної групи (JSON) та статистика помилок по критеріях |
| `GET` | `/analytics/groups/{group_id}/export` | Teacher / Admin | Генерація відомості успішності у форматі `.xlsx` або `.pdf` |
| `GET` | `/admin/groups` | Admin | Перелік усіх академічних груп |
| `POST` | `/admin/groups` | Admin | Створення нової академічної групи (`course_year` у межах `1..4`) |
| `PATCH` | `/admin/groups/{group_id}` | Admin | Редагування шифру, спеціальності або курсу академічної групи |
| `DELETE` | `/admin/groups/{group_id}` | Admin | Видалення академічної групи з відв'язкою студентів |
| `GET` | `/admin/users` | Admin | Перелік облікових записів користувачів із фільтрацією (`role`, `group_id`, `search`) |
| `POST` | `/admin/users` | Admin | Створення користувача (`student`, `teacher`, `admin`) |
| `POST` | `/admin/users/import` | Admin | Масовий імпорт студентів із `.docx` або `.txt` з українським алфавітним сортуванням та звітом (`must_change_password=True`) |
| `PATCH` | `/admin/users/{user_id}` | Admin | Оновлення профілю, ролі, групи, номера у списку або пароля користувача |
| `POST` | `/admin/users/{user_id}/reset-password` | Admin | Скидання пароля користувача з інкрементом `token_version` (відкликання сесій) та встановленням `must_change_password=True` |
| `DELETE` | `/admin/users/{user_id}` | Admin | Видалення користувача та безпечне очищення фізичних файлів його здач із `UPLOADS_DIR` |
| `GET` | `/media/courses/{path}` | Public | Статична роздача медіафайлів курсів із `COURSE_MEDIA_DIR` через `StaticFiles` із заголовками `X-Content-Type-Options: nosniff` і `CSP` |

### 3.4. Контракт масового імпорту студентів (`POST /api/v1/admin/users/import`)
* **Запит (`multipart/form-data`):**
  * `group_id`: `UUID` — ідентифікатор цільової академічної групи;
  * `file`: бінарний файл `.docx` (офіційна таблиця видачі коледжу `ПІБ | Логін | E-mail | Пароль | Дод. інформація`) або `.txt` (UTF-8, один студент на рядок: `ПІБ; email; пароль`, `ПІБ; email` або `ПІБ`).
* **Алгоритм обробки:**
  1. Зчитування всіх валідних записів із нормалізацією символів апострофа (`` ` ``, `’`, `‘`, `ʼ`, `´` → `'`) у `full_name`. Якщо в `.docx` вказано лише `Логін`, формується `{login}@kpefk.com.ua`; якщо у `.txt` (або `.docx`) відсутній email чи пароль — генерується унікальний транслітерований `{surname}.{initial}@kpefk.com.ua` та тимчасовий 8-символьний пароль.
  2. Сортування всіх зібраних кандидатів за українською абеткою (`А Б В Г Ґ Д Е Є Ж З И І Ї Й К Л М Н О П Р С Т У Ф Х Ц Ч Ш Щ Ь Ю Я`).
  3. Пропуск дублікатів за `email` (у БД або в межах файлу) без переривання транзакції, присвоєння `list_number` (починаючи з `max(list_number у групі) + 1`, або з `1` для порожньої групи) та розрахунок `variant_number = calculate_variant_index(list_number, total_variants) + 1` (узгоджено з `quiz_service.py`).
* **Відповідь (`200 OK`, `StudentImportResponse`):**
```json
{
  "group_id": "00000000-0000-0000-0000-000000000000",
  "group_code": "КН-31",
  "total_variants": 3,
  "created_count": 2,
  "skipped_count": 1,
  "created": [
    {
      "user_id": "11111111-1111-1111-1111-111111111111",
      "list_number": 1,
      "variant_number": 1,
      "full_name": "Авраменко Іван Сергійович",
      "email": "avramenko.i@kpefk.com.ua",
      "temp_password": "PassWord1"
    }
  ],
  "skipped": [
    {
      "row_number": 3,
      "full_name": "Бондаренко Ірина Василівна",
      "email": "student1@kpefk.lcloud.in.ua",
      "reason": "Користувач із поштою «student1@kpefk.lcloud.in.ua» вже зареєстрований у системі."
    }
  ]
}
```

### 3.5. Завантаження робіт студентів і політика зберігання (`retention_service.py`)
* **Ендпоінт завантаження (`GET /api/v1/submissions/{submission_id}/download`):**
  * **RBAC:** доступ лише для `admin` та `teacher` (для `teacher` перевіряється `submission.practical.module.course.teacher_id == current_user.id`, інакше `403 Forbidden`).
  * **Бінарні формати (`.docx`, `.xlsx`, `.accdb`):** перевірка наявності файлу та захист від Path Traversal (`resolved_path.is_relative_to(UPLOADS_DIR.resolve())`); віддача через `FileResponse` із коректним `media_type` і заголовком RFC 5987 `Content-Disposition` (`{group_code}_{student_surname}_{course_slug}_v{variant_number}.{ext}`).
  * **HTML (`raw_code`):** генерація `.html` на льоту (`text/html; charset=utf-8`) із тим самим `Content-Disposition`.
  * **Відсутній або очищений файл:** повертає `404 Not Found` (`code="SUBMISSION_FILE_NOT_FOUND"`).
* **Політика 90-денного зберігання та очищення:**
  * Параметри конфігурації в `backend/app/core/config.py`: `SUBMISSION_FILE_RETENTION_DAYS: int = 90` (`>= 1`) та `ENABLE_RETENTION_CLEANUP_TASK: bool = True`.
  * У контракті `SubmissionRead` передаються обчислювані поля `is_file_available: bool` та `file_expires_at: datetime | None` (`submitted_at + timedelta(days=SUBMISSION_FILE_RETENTION_DAYS)` за наявності файлу/коду).
  * `cleanup_expired_submissions()` у `backend/app/services/retention_service.py` видаляє фізичні файли з диска (у межах `UPLOADS_DIR`) та обнуляє `file_path` і `raw_code` для здач старших за 90 днів, **не видаляючи** записи `Submission` (оцінки, `grading_report`, `teacher_comment`, `extracted_metadata` і `file_hash` зберігаються).
  * Запускається автоматично у фоновій `asyncio`-задачі через `lifespan` у `backend/app/main.py` (при старті + кожні 24 години) або вручну/cron через `python -m app.services.retention_service [--dry-run]`.
  * При видаленні користувача (`DELETE /api/v1/admin/users/{user_id}`), модуля курсу (`DELETE /api/v1/modules/{module_id}`) або практичної роботи (`DELETE /api/v1/practicals/{practical_id}`) усі пов'язані фізичні файли здач студентів безпечно видаляються з диска в межах `UPLOADS_DIR` через `delete_submission_files_for_paths()` після успішного `commit()`.