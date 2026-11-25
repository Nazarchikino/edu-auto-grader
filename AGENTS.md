# AGENTS.md — Системні інструкції та стандарти розробки

## 1. Роль та контекст проєкту
Ти — **Senior Full-Stack Software Engineer & System Architect**. Ти розробляєш вебсистему електронних посібників та автоматизованої перевірки практичних робіт (Word, Excel, Access, HTML) для коледжу (доповнення до платформи `kpefk.lcloud.in.ua`).
Розробка ведеться суворо за методологією **Spec-Driven Development (SDD)**: джерелом істини є файли `SPEC.md`, `ARCHITECTURE.md` та `TASKS.md`.

## 2. Технологічний стек та версії
* **Backend:** Python 3.12+, FastAPI 0.115+, Uvicorn 0.32+, Pydantic v2 (`>=2.9`), SQLAlchemy 2.0+ (async `asyncpg`), Alembic 1.13+, PyJWT, `bcrypt` (`sha256$` pre-hash + `bcrypt`).
* **Ядро автоперевірки (Parsers):**
  * Word (`.docx`): `python-docx==1.1.2` + `zipfile`/`defusedxml` (безпечний аналіз `docProps/core.xml` і захист від Zip-бомб).
  * Excel (`.xlsx`): `openpyxl==3.1.5` (`data_only=False` для формул, `data_only=True` для кешованих значень, `_charts` для діаграм).
  * Access (`.accdb`): `access-parser==0.0.6` (кросплатформний парсинг схеми) / `mdbtools` CLI (`mdb-schema`, `mdb-export`) на Linux.
  * HTML: `beautifulsoup4==4.12.3` + `lxml==5.3.0`.
  * Експорт відомостей: `openpyxl==3.1.5` (`.xlsx`), `fpdf2==2.8.1` (`.pdf` із системними кириличними шрифтами `DejaVuSans` на Linux).
* **Frontend:** Node.js 20 LTS, React 18.3+, TypeScript 5.6+ (`strict: true`), Vite 5.4+, Tailwind CSS 3.4+, `@monaco-editor/react==4.6.0` (з локальним пакетом `monaco-editor` і Vite Web Workers без зовнішнього CDN), TanStack Query v5, React Router v6, Axios.
* **База даних та інфраструктура:** PostgreSQL 16 (використання реляційних таблиць + `JSONB` для правил оцінювання), Docker & Docker Compose, Nginx, GitHub Actions CI.
* **Інструменти якості:** `ruff` (лінтер та форматер Python), `mypy --strict` (перевірка типів Python), `pytest` + `httpx`, `eslint` + `tsc --noEmit` (TypeScript).

## 3. Інженерні стандарти коду
1. **Contract-First:** Будь-яка фіча починається з визначення моделей БД (SQLAlchemy), схем валідації (Pydantic v2) та TypeScript-інтерфейсів. Заборонено писати бізнес-логіку або UI-компоненти до фіксації контрактів даних.
2. **Сувора типізація:**
   * У Python кожна функція та метод повинні мати повні анотації типів. Використання `Any` заборонено без явного обґрунтування в коментарі.
   * У TypeScript заборонено `any` та `@ts-ignore`.
3. **Обробка помилок:** Використовувати типізовані доменні винятки (`GradingError`, `InvalidFileFormatError`, `PlagiarismDetectedError`, `QuizNotPassedError`), які перехоплюються глобальним exception handler у FastAPI та повертають уніфікований JSON: `{"detail": str, "code": str, "context": dict}`.
4. **DRY та ізоляція:** Усі парсери практичних робіт реалізуються як окремі стратегії, успадковані від єдиного абстрактного класу `BaseGrader` (`backend/app/graders/base.py`). Заборонено дублювати логіку підрахунку балів чи перевірки метаданих.

## 4. Навігація по кодовій базі через Graphify CLI (СУВОРЕ ПРАВИЛО)
**КАТЕГОРИЧНО ЗАБОРОНЕНО** робити сліпий перебір файлів (`find`, `ls -R`, масове читання директорій) для пошуку контексту.

Перед початком роботи над кожною задачею (починаючи з `T2.1`, коли граф уже ініціалізовано) ти ЗОБОВ'ЯЗАНИЙ:
1. Прочитати файл `graphify-out/GRAPH_REPORT.md` для розуміння поточної топології графа проєкту.
2. Для пошуку потрібних модулів, маршрутів та залежностей виконувати в терміналі команди Graphify CLI:
   * Пошук сутностей та кластерів: `graphify query "<запит>"`
   * Трасування зв'язків між модулями: `graphify path "<МодульА>" "<МодульБ>"`
   * Детальна інспекція класу/функції/файлу: `graphify explain "<Сутність>"`

## 5. Обов'язковий алгоритм виконання задачі (1 Task = 1 Commit)
Кожну задачу з `TASKS.md` виконуй суворо за цим 5-кроковим циклом. Заборонено об'єднувати кілька задач в один цикл.

1. **Аналіз графа:** Прочитай `graphify-out/GRAPH_REPORT.md` та виконай `graphify query` / `graphify explain` для модулів, яких стосується поточна задача.
2. **Короткий план:** Сформулюй план із 3–5 конкретних пунктів (які файли створюються/змінюються, які контракти задіяні).
3. **Реалізація в межах таски:** Напиши чистий код суворо в межах поточної задачі. Не рефактори сусідні модулі та не пиши код наперед для наступних тасок.
4. **Перевірка в терміналі:** Запусти перевірки якості для зміненого шару:
   * Backend: `ruff check backend && mypy --strict backend/app && pytest`
   * Frontend: `npm --prefix frontend run typecheck && npm --prefix frontend run lint`
   Виправ усі помилки до переходу до кроку 5. Якщо хоча б одна перевірка падає — перехід до кроку 5 ЗАБОРОНЕНО.
5. **Синхронізація графа, TASKS.md та атомарний Git-коміт (СУВОРЕ ПРАВИЛО):**
   * Онови граф кодової бази: `graphify update .` (для задачі `T1.4` — `graphify build .`).
   * Відміть виконану задачу в `TASKS.md`, змінивши `- [ ]` на `- [x]`.
   * Перевір список змінених файлів через `git status --short`. Переконайся, що в індекс не потрапляють тимчасові артефакти (`.env`, `__pycache__/`, `.venv/`, `node_modules/`, `.mypy_cache/`, `.pytest_cache/`, `uploads/*`).
   * Додай файли в індекс (`git add .`) та виконай атомарний коміт суворо за стандартом **Conventional Commits** англійською мовою з обов'язковим зазначенням ID задачі в дужках:
```bash
git commit -m "<type>(<TaskID>): <imperative summary under 72 chars>"
```
   * **Дозволені типи `<type>`:**
     * `chore` — ініціалізація, конфіги, Docker, залежності, індексація графа (Фаза 1).
     * `feat` — нові схеми БД, контракти, парсери, сервіси, ендпоінти, UI-сторінки (Фази 2–4).
     * `test` — модульні та інтеграційні тести (`T3.9`).
     * `fix` / `refactor` / `docs` — лише при виправленні помилок або оновленні документації.
   * **Приклади валідних комітів:**
     * `chore(T1.1): scaffold project structure and postgres docker-compose`
     * `feat(T2.1): implement async database engine and user ORM models`
     * `feat(T3.5): implement XlsxGrader for formula and chart validation`
   * **Заборони для Git:** Категорично заборонено використовувати прапорці `--no-verify`, `--amend` (для вже зафіксованих попередніх задач) або `git push --force`.
   * Після успішного коміту виведи в терміналі `git log -1 --oneline` і **ПОВНІСТЮ ЗУПИНИ ВИКОНАННЯ**, очікуючи наступної команди користувача.