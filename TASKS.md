# TASKS.md — Покроковий план реалізації (Spec-Driven Development)

## Фаза 1: Ініціалізація та конфігурація середовища
- [x] **T1.1:** Створити базову структуру директорій (`backend/`, `frontend/`) та `docker-compose.yml` із сервісом `postgres:16-alpine` і volume для збереження завантажених файлів студентів (`uploads/`).
- [x] **T1.2:** Ініціалізувати `backend/pyproject.toml` із фіксованими версіями залежностей (`fastapi`, `uvicorn`, `sqlalchemy`, `asyncpg`, `alembic`, `pydantic`, `pydantic-settings`, `pyjwt`, `bcrypt`, `python-multipart`, `python-docx`, `openpyxl`, `access-parser`, `beautifulsoup4`, `lxml`, `fpdf2`, `ruff`, `mypy`, `pytest`, `httpx`) та створити `backend/app/core/config.py`.
- [x] **T1.3:** Ініціалізувати фронтенд у `frontend/` (`Vite + React + TypeScript strict + Tailwind CSS`), налаштувати `tsconfig.json`, `eslint` та базовий Axios-клієнт у `frontend/src/api/client.ts`.
- [x] **T1.4:** Запустити початкову індексацію графа кодової бази командою `graphify . --code-only` та перевірити генерацію `graphify-out/GRAPH_REPORT.md`.

## Фаза 2: Схеми БД, типи та контракти (Contract-First)
- [ ] **T2.1:** Реалізувати асинхронне підключення до PostgreSQL у `backend/app/core/database.py` та створити SQLAlchemy 2.0 моделі `AcademicGroup`, `User` у `backend/app/models/user.py`.
- [ ] **T2.2:** Створити SQLAlchemy 2.0 моделі `Course`, `Module`, `QuizQuestion`, `Practical` у `backend/app/models/course.py` та `QuizAttempt`, `Submission` у `backend/app/models/progress.py`.
- [ ] **T2.3:** Налаштувати Alembic, згенерувати початкову міграцію БД, застосувати її та написати CLI-скрипт `backend/app/seed.py` для наповнення БД 4 курсами (`word`, `excel`, `access`, `html`), тестовою групою, викладачем та студентами.
- [ ] **T2.4:** Описати Pydantic v2 схеми контрактів у `backend/app/schemas/` (`auth.py`, `course.py`, `grading.py`, `submission.py`), включно зі строго типізованими моделями `GradingRule`, `CriterionResult` та `GradingReport`.
- [ ] **T2.5:** Синхронізувати контракти даних на фронтенді у `frontend/src/types/` (`api.ts`, `course.ts`, `grading.ts`) у повній відповідності до Pydantic-схем бекенду.

## Фаза 3: Бекенд та ядро автоперевірки
- [ ] **T3.1:** Реалізувати JWT-автентифікацію (`backend/app/core/security.py`), RBAC-залежності (`get_current_user`, `require_role` у `backend/app/api/deps.py`) та ендпоінти `/api/v1/auth/login` і `/auth/me`.
- [ ] **T3.2:** Реалізувати ендпоінти курсів, лекцій та логіку тесту-допуску (`backend/app/services/quiz_service.py`, `backend/app/api/v1/courses.py`) із розрахунком індивідуального варіанта студента.
- [ ] **T3.3:** Реалізувати абстрактний клас `BaseGrader` (`backend/app/graders/base.py`), фабрику `GraderFactory` (`factory.py`) та модуль екстракції метаданих `docProps/core.xml` + SHA-256 антиплагіату (`backend/app/graders/metadata.py`).
- [ ] **T3.4:** Реалізувати `DocxGrader` (`backend/app/graders/docx_grader.py`) для перевірки полів сторінки, шрифтів, інтервалів, вирівнювання, таблиць та списків у `.docx`.
- [ ] **T3.5:** Реалізувати `XlsxGrader` (`backend/app/graders/xlsx_grader.py`) для перевірки формул (`data_only=False`), обчислених значень (`data_only=True`) та діаграм у `.xlsx`.
- [ ] **T3.6:** Реалізувати `AccdbGrader` (`backend/app/graders/accdb_grader.py`) для інспекції таблиць, полів та типів даних у `.accdb` та `HtmlGrader` (`backend/app/graders/html_grader.py`) на базі `BeautifulSoup4`.
- [ ] **T3.7:** Реалізувати оркестратор здачі робіт `SubmissionService` (`backend/app/services/submission_service.py`) та ендпоінти `POST /practicals/{id}/submit`, `PUT /practicals/{id}/rules`, `PATCH /submissions/{id}/grade`.
- [ ] **T3.8:** Реалізувати `ExportService` (`backend/app/services/export_service.py`) для генерації відомостей групи у `.xlsx` та `.pdf` (`GET /analytics/groups/{group_id}/export`).
- [ ] **T3.9:** Написати модульні та інтеграційні тести (`backend/tests/test_graders.py`, `backend/tests/test_submissions_api.py`) для всіх 4 парсерів, перевірки антиплагіату та блокування здачі без тесту-допуску.

## Фаза 4: Фронтенд, HTML-пісочниця та інтеграція
- [ ] **T4.1:** Реалізувати `AuthContext.tsx`, сторінку входу `LoginPage.tsx` та захищений лейаут навігації (`Sidebar`, `Navbar`, `RoleGuard`) із розділенням меню для студента, викладача та адміністратора.
- [ ] **T4.2:** Реалізувати студентський перегляд курсів (`CoursesPage.tsx`) та сторінку модуля (`ModuleViewPage.tsx`) із рендерингом лекції та інтерактивним тестом-допуском.
- [ ] **T4.3:** Реалізувати компонент `HtmlSandbox.tsx` (Monaco Editor + ізольований `<iframe sandbox>` для живого прев'ю) та форму завантаження файлів `.docx`/`.xlsx`/`.accdb` з відображенням індивідуального варіанта.
- [ ] **T4.4:** Реалізувати електронну заліковку студента (`GradebookPage.tsx`) та компонент детального розбору помилок автоперевірки (`GradingReportCard.tsx`).
- [ ] **T4.5:** Реалізувати кабінет викладача: конструктор курсів/лекцій (`CourseEditorPage.tsx`), візуальний редактор правил перевірки (`RuleBuilderPage.tsx`) та журнал групи (`GroupJournalPage.tsx`) із плагіат-бейждами, ручним коригуванням балів та кнопками експорту `.xlsx`/`.pdf`.
- [ ] **T4.6:** Реалізувати сторінку адміністратора (`AdminUsersPage.tsx`) для керування групами, студентами та викладачами; виконати повну перевірку збірки (`vite build`, `mypy --strict`, `pytest`) та фінальне оновлення графа `graphify update .`.