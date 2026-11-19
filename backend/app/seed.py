import argparse
import asyncio
from collections.abc import Sequence
from dataclasses import dataclass
from decimal import Decimal

import bcrypt
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import AsyncSessionLocal
from app.models.course import (
    ALLOWED_COURSE_SLUGS,
    MAX_COURSES_COUNT,
    Course,
    CourseSlug,
    Module,
    Practical,
    PracticalFormat,
    QuizQuestion,
)
from app.models.user import (
    MAX_COURSE_YEAR,
    MIN_COURSE_YEAR,
    AcademicGroup,
    User,
    UserRole,
)


@dataclass(frozen=True, slots=True)
class SeedSummary:
    """Підсумок виконання скрипта початкового наповнення бази даних."""

    group_code: str
    users_count: int
    courses_count: int
    modules_count: int
    questions_count: int
    practicals_count: int


@dataclass(frozen=True, slots=True)
class SeedBundle:
    """Контейнер підготовлених ORM-об'єктів для ідемпотентного збереження в БД."""

    group: AcademicGroup
    admin: User
    teacher: User
    students: list[User]
    courses: list[Course]


def hash_password(plain_password: str) -> str:
    """Генерує bcrypt-хеш пароля користувача."""
    salt = bcrypt.gensalt(rounds=12)
    hashed: bytes = bcrypt.hashpw(plain_password.encode("utf-8"), salt)
    return hashed.decode("utf-8")


def _build_word_course(teacher: User) -> Course:
    """Створює навчальний курс Microsoft Word із лекцією, тестом та практичною."""
    course = Course(
        title="Microsoft Word: Оформлення текстових документів",
        slug=CourseSlug.WORD,
        description=(
            "Практичний курс зі створення, форматування та структурування "
            "офіційних і академічних документів у текстовому процесорі Microsoft Word."
        ),
        teacher=teacher,
    )
    module = Module(
        course=course,
        order_index=1,
        title="Параметри сторінки, стилі абзаців, таблиці та списки у Word",
        lecture_content=(
            "# Оформлення офіційних та академічних документів у Microsoft Word\n\n"
            "## 1. Параметри сторінки\n"
            "Згідно зі стандартами оформлення навчальних робіт коледжу, документ повинен мати:\n"
            "- ліве поле — **30 мм** (для підшивання);\n"
            "- праве поле — **10–15 мм**;\n"
            "- верхнє та нижнє поля — **20 мм**.\n\n"
            "## 2. Форматування тексту та абзаців\n"
            "Основний текст документа набирається гарнітурою **Times New Roman**, кегль **14 пт**, "
            "міжрядковий інтервал — **1.5 рядка**, вирівнювання — **за шириною** (`JUSTIFY`).\n\n"
            "## 3. Таблиці та списки\n"
            "Для подання структурованих даних використовуються таблиці з шапкою та марковані або "
            "нумеровані списки."
        ),
    )
    module.quiz_questions = [
        QuizQuestion(
            question_text="Який розмір лівого поля сторінки встановлюється для підшивання звіту?",
            options=["10 мм", "20 мм", "30 мм", "15 мм"],
            correct_option_index=2,
        ),
        QuizQuestion(
            question_text="Яка гарнітура та кегль є стандартними для основного тексту звіту?",
            options=[
                "Calibri, 11 пт",
                "Times New Roman, 14 пт",
                "Arial, 12 пт",
                "Courier New, 10 пт",
            ],
            correct_option_index=1,
        ),
        QuizQuestion(
            question_text="Який міжрядковий інтервал застосовується до основного тексту роботи?",
            options=["Одинарний (1.0)", "Множинний (1.15)", "Півтора (1.5)", "Подвійний (2.0)"],
            correct_option_index=2,
        ),
        QuizQuestion(
            question_text="Який тип вирівнювання абзаців є обов'язковим для основного тексту?",
            options=["За лівим краєм", "По центру", "За правим краєм", "За шириною"],
            correct_option_index=3,
        ),
        QuizQuestion(
            question_text="У якому XML-файлі архіву .docx зберігаються метадані автора документа?",
            options=[
                "word/document.xml",
                "docProps/core.xml",
                "word/styles.xml",
                "[Content_Types].xml",
            ],
            correct_option_index=1,
        ),
    ]
    module.practical = Practical(
        title="Практична робота №1: Форматування звіту з таблицями та списками (.docx)",
        instructions=(
            "Створіть документ Microsoft Word (`.docx`) відповідно до вашого індивідуального "
            "варіанта. Налаштуйте поля сторінки, шрифт Times New Roman 14 пт, міжрядковий "
            "інтервал 1.5, вирівнювання за шириною, додайте підсумкову таблицю та список."
        ),
        format_type=PracticalFormat.DOCX,
        max_score=Decimal("10.00"),
        variants=[
            {
                "variant_number": 1,
                "title": "Варіант 1: Звіт про успішність студентів відділення ІТ",
                "task_description": (
                    "Оформіть пояснювальну записку з таблицею результатів зимової сесії "
                    "(4 стовпці) та переліком рекомендованої літератури."
                ),
                "parameters": {"min_tables": 1, "min_rows": 4, "font_name": "Times New Roman"},
            },
            {
                "variant_number": 2,
                "title": "Варіант 2: Відомість інвентаризації комп'ютерної лабораторії",
                "task_description": (
                    "Оформіть акт інвентаризації обладнання кабінету інформатики з таблицею обліку "
                    "та списком відповідальних осіб."
                ),
                "parameters": {"min_tables": 1, "min_rows": 5, "font_name": "Times New Roman"},
            },
            {
                "variant_number": 3,
                "title": "Варіант 3: Програма студентської науково-практичної конференції",
                "task_description": (
                    "Оформіть програму секційного засідання з таблицею розкладу доповідей "
                    "та нумерованим переліком вимог до тез."
                ),
                "parameters": {"min_tables": 1, "min_rows": 4, "font_name": "Times New Roman"},
            },
        ],
        grading_rules=[
            {
                "id": "word_rule_1",
                "type": "docx_page_margins",
                "target": "section_0",
                "expected": "left=30,right=15,top=20,bottom=20",
                "points": 2.0,
                "description": "Поля сторінки відповідають стандарту (30/15/20/20 мм)",
            },
            {
                "id": "word_rule_2",
                "type": "docx_font",
                "target": "body",
                "expected": "Times New Roman:14",
                "points": 2.5,
                "description": "Основний текст набрано шрифтом Times New Roman, 14 пт",
            },
            {
                "id": "word_rule_3",
                "type": "docx_line_spacing",
                "target": "body",
                "expected": "1.5",
                "points": 1.5,
                "description": "Встановлено полуторний міжрядковий інтервал (1.5)",
            },
            {
                "id": "word_rule_4",
                "type": "docx_alignment",
                "target": "body",
                "expected": "JUSTIFY",
                "points": 1.5,
                "description": "Абзаци основного тексту вирівняно за шириною",
            },
            {
                "id": "word_rule_5",
                "type": "docx_table_exists",
                "target": "document",
                "expected": ">=1",
                "points": 1.5,
                "description": "Документ містить щонайменше одну зведену таблицю",
            },
            {
                "id": "word_rule_6",
                "type": "docx_list_exists",
                "target": "document",
                "expected": "true",
                "points": 1.0,
                "description": "Документ містить маркований або нумерований список",
            },
        ],
    )
    return course


def _build_excel_course(teacher: User) -> Course:
    """Створює навчальний курс Microsoft Excel із лекцією, тестом та практичною."""
    course = Course(
        title="Microsoft Excel: Електронні таблиці, формули та діаграми",
        slug=CourseSlug.EXCEL,
        description=(
            "Автоматизація фінансово-економічних та статистичних розрахунків у Microsoft Excel "
            "із використанням вбудованих функцій та візуалізації даних."
        ),
        teacher=teacher,
    )
    module = Module(
        course=course,
        order_index=1,
        title="Формули, статистичні функції SUM/AVERAGE та побудова діаграм",
        lecture_content=(
            "# Аналіз даних та візуалізація у Microsoft Excel\n\n"
            "## 1. Формули та адресація комірок\n"
            "Кожна формула в Excel починається зі знака `=`. Для підсумовування діапазону "
            "використовується функція `=SUM(D2:D11)`, для середнього значення — "
            "`=AVERAGE(D2:D11)`.\n\n"
            "## 2. Перевірка формул та обчислених значень\n"
            "Система автоперевірки інспектує книгу `.xlsx` у двох режимах:\n"
            "- `data_only=False` — перевірка наявності самої формули у цільовій комірці;\n"
            "- `data_only=True` — звірка обчисленого кешованого результату.\n\n"
            "## 3. Побудова діаграм\n"
            "Діаграма будується на основі підсумкового діапазону даних та розміщується на аркуші."
        ),
    )
    module.quiz_questions = [
        QuizQuestion(
            question_text="З якого символу обов'язково починається формула в Microsoft Excel?",
            options=["#", "=", "@", "$"],
            correct_option_index=1,
        ),
        QuizQuestion(
            question_text="Яка функція обчислює суму значень у діапазоні комірок D2:D11?",
            options=["=COUNT(D2:D11)", "=AVERAGE(D2:D11)", "=SUM(D2:D11)", "=MAX(D2:D11)"],
            correct_option_index=2,
        ),
        QuizQuestion(
            question_text="Як позначається абсолютне посилання на комірку A1 в Excel?",
            options=["A1", "$A$1", "&A&1", "#A#1"],
            correct_option_index=1,
        ),
        QuizQuestion(
            question_text="Який параметр openpyxl дозволяє зчитати текст формули замість числа?",
            options=["read_only=True", "data_only=False", "data_only=True", "keep_vba=True"],
            correct_option_index=1,
        ),
        QuizQuestion(
            question_text="Яка функція повертає середнє арифметичне діапазону комірок?",
            options=["=MEDIAN()", "=AVERAGE()", "=MEAN()", "=MID()"],
            correct_option_index=1,
        ),
    ]
    module.practical = Practical(
        title="Практична робота №1: Розрахункова відомість та діаграма в Excel (.xlsx)",
        instructions=(
            "Створіть книгу Microsoft Excel (`.xlsx`) з аркушем `Sheet1`. Заповніть вхідні дані "
            "вашого варіанта у рядках 2–11, обчисліть підсумок функцією `SUM(D2:D11)` у комірці "
            "`D12`, середнє значення функцією `AVERAGE(D2:D11)` у `D13` та побудуйте діаграму."
        ),
        format_type=PracticalFormat.XLSX,
        max_score=Decimal("10.00"),
        variants=[
            {
                "variant_number": 1,
                "title": "Варіант 1: Відомість нарахування стипендії студентам групи",
                "task_description": (
                    "Заповніть таблицю з 10 студентів, розрахуйте загальний фонд стипендії в D12 "
                    "та середній розмір виплати в D13."
                ),
                "parameters": {"sheet": "Sheet1", "sum_cell": "D12", "expected_sum": 18500},
            },
            {
                "variant_number": 2,
                "title": "Варіант 2: Облік споживання електроенергії підрозділами коледжу",
                "task_description": (
                    "Заповніть показники за 10 місяців, обчисліть сумарні витрати в D12 "
                    "та середньомісячне споживання в D13."
                ),
                "parameters": {"sheet": "Sheet1", "sum_cell": "D12", "expected_sum": 24200},
            },
            {
                "variant_number": 3,
                "title": "Варіант 3: Кошторис закупівлі мережевого обладнання",
                "task_description": (
                    "Заповніть 10 позицій специфікації, обчисліть підсумкову вартість у D12 "
                    "та середню вартість позиції в D13."
                ),
                "parameters": {"sheet": "Sheet1", "sum_cell": "D12", "expected_sum": 31400},
            },
        ],
        grading_rules=[
            {
                "id": "excel_rule_1",
                "type": "xlsx_formula",
                "target": "D12",
                "expected": "SUM(D2:D11)",
                "points": 3.5,
                "description": "Використано функцію SUM для підрахунку підсумку в комірці D12",
            },
            {
                "id": "excel_rule_2",
                "type": "xlsx_formula",
                "target": "D13",
                "expected": "AVERAGE(D2:D11)",
                "points": 2.5,
                "description": "Використано функцію AVERAGE для середнього значення в комірці D13",
            },
            {
                "id": "excel_rule_3",
                "type": "xlsx_value",
                "target": "D12",
                "expected": "not_null",
                "points": 2.0,
                "description": "У комірці D12 збережено обчислене числове значення",
            },
            {
                "id": "excel_rule_4",
                "type": "xlsx_chart_exists",
                "target": "Sheet1",
                "expected": "true",
                "points": 2.0,
                "description": "На аркуші Sheet1 побудовано діаграму",
            },
        ],
    )
    return course


def _build_access_course(teacher: User) -> Course:
    """Створює навчальний курс Microsoft Access із лекцією, тестом та практичною."""
    course = Course(
        title="Microsoft Access: Проєктування реляційних баз даних",
        slug=CourseSlug.ACCESS,
        description=(
            "Основи реляційного моделювання, створення таблиць, первинних ключів, типів полів "
            "та зв'язків між таблицями в СКБД Microsoft Access."
        ),
        teacher=teacher,
    )
    module = Module(
        course=course,
        order_index=1,
        title="Структура таблиць, типи даних полів та цілісність даних у Access",
        lecture_content=(
            "# Проєктування реляційних таблиць у Microsoft Access\n\n"
            "## 1. Таблиці та первинні ключі\n"
            "Кожна сутність предметної області моделюється окремою таблицею з первинним ключем "
            "(`Primary Key`, зазвичай поле `id` типу `AutoNumber` / `Long Integer`).\n\n"
            "## 2. Основні типи даних полів\n"
            "- **Short Text** (`TEXT`) — текстові рядки до 255 символів;\n"
            "- **Number / Long Integer** (`LONG`) — цілі числа та зовнішні ключі;\n"
            "- **Currency / Double** (`CURRENCY`, `DOUBLE`) — грошові та дробові величини;\n"
            "- **Date/Time** (`DATETIME`) — дати та часові позначки."
        ),
    )
    module.quiz_questions = [
        QuizQuestion(
            question_text="Яке розширення має сучасний файл бази даних Microsoft Access?",
            options=[".xlsx", ".docx", ".accdb", ".sqlite"],
            correct_option_index=2,
        ),
        QuizQuestion(
            question_text="Як називається поле або набір полів, що унікально ідентифікує запис?",
            options=["Зовнішній ключ", "Первинний ключ", "Індексне поле", "Обчислюване поле"],
            correct_option_index=1,
        ),
        QuizQuestion(
            question_text="Який тип даних Access використовується для автоматичної нумерації ID?",
            options=["Short Text", "AutoNumber (Лічильник)", "Memo", "Yes/No"],
            correct_option_index=1,
        ),
        QuizQuestion(
            question_text="Який тип зв'язку є найпоширенішим між таблицею груп та студентами?",
            options=[
                "Один-до-одного (1:1)",
                "Один-до-багатьох (1:M)",
                "Багато-до-багатьох (M:N) без проміжної таблиці",
                "Ієрархічний цикл",
            ],
            correct_option_index=1,
        ),
        QuizQuestion(
            question_text="Що забезпечує увімкнення параметра 'Забезпечення цілісності даних'?",
            options=[
                "Шифрування файлу паролем",
                "Заборону створення записів із неіснуючим зовнішнім ключем",
                "Автоматичний експорт у PDF",
                "Стиснення зображень у таблиці",
            ],
            correct_option_index=1,
        ),
    ]
    module.practical = Practical(
        title="Практична робота №1: Створення схеми бази даних коледжу (.accdb)",
        instructions=(
            "Створіть файл бази даних Microsoft Access (`.accdb`), який містить таблиці "
            "`Students` та `Grades` із визначеними стовпцями та відповідними типами даних "
            "згідно з вашим індивідуальним варіантом."
        ),
        format_type=PracticalFormat.ACCDB,
        max_score=Decimal("10.00"),
        variants=[
            {
                "variant_number": 1,
                "title": "Варіант 1: База даних обліку успішності студентів",
                "task_description": (
                    "Створіть таблицю Students (ID, FullName, GroupCode) та таблицю Grades "
                    "(ID, StudentID, SubjectName, Score)."
                ),
                "parameters": {
                    "required_tables": ["Students", "Grades"],
                    "primary_table": "Students",
                },
            },
            {
                "variant_number": 2,
                "title": "Варіант 2: База даних бібліотечного фонду коледжу",
                "task_description": (
                    "Створіть таблицю Students (ID, FullName, GroupCode) та таблицю Grades "
                    "для обліку рейтингових балів читацької активності."
                ),
                "parameters": {
                    "required_tables": ["Students", "Grades"],
                    "primary_table": "Students",
                },
            },
            {
                "variant_number": 3,
                "title": "Варіант 3: База даних результатів лабораторного практикуму",
                "task_description": (
                    "Створіть таблицю Students (ID, FullName, GroupCode) та таблицю Grades "
                    "(ID, StudentID, SubjectName, Score) із тестовими записами."
                ),
                "parameters": {
                    "required_tables": ["Students", "Grades"],
                    "primary_table": "Students",
                },
            },
        ],
        grading_rules=[
            {
                "id": "access_rule_1",
                "type": "accdb_table_exists",
                "target": "Students",
                "expected": "true",
                "points": 3.0,
                "description": "У базі даних присутня таблиця Students",
            },
            {
                "id": "access_rule_2",
                "type": "accdb_table_exists",
                "target": "Grades",
                "expected": "true",
                "points": 3.0,
                "description": "У базі даних присутня таблиця Grades",
            },
            {
                "id": "access_rule_3",
                "type": "accdb_column_exists",
                "target": "Students.FullName",
                "expected": "true",
                "points": 2.0,
                "description": "Таблиця Students містить текстове поле FullName",
            },
            {
                "id": "access_rule_4",
                "type": "accdb_column_exists",
                "target": "Grades.Score",
                "expected": "true",
                "points": 2.0,
                "description": "Таблиця Grades містить числове поле Score",
            },
        ],
    )
    return course


def _build_html_course(teacher: User) -> Course:
    """Створює навчальний курс HTML5 із лекцією, тестом та практичною для HTML-пісочниці."""
    course = Course(
        title="HTML5: Семантична верстка вебсторінок",
        slug=CourseSlug.HTML,
        description=(
            "Інтерактивний курс із розробки структурованих HTML5-документів: семантичні теги, "
            "таблиці, гіперпосилання та форми з миттєвою перевіркою DOM-дерева."
        ),
        teacher=teacher,
    )
    module = Module(
        course=course,
        order_index=1,
        title="Семантична структура HTML5, таблиці та форми",
        lecture_content=(
            "# Семантична розмітка вебсторінок у HTML5\n\n"
            "## 1. Базовий каркас документа\n"
            "Кожна HTML5-сторінка містить декларацію `<!DOCTYPE html>`, кореневий елемент "
            "`<html lang=\"uk\">`, секцію метаданих `<head>` та тіло `<main>` у `<body>`.\n\n"
            "## 2. Таблиці в HTML\n"
            "Таблиці створюються тегом `<table>`, рядки — `<tr>`, комірки заголовка — `<th>`, "
            "а комірки даних — `<td>`.\n\n"
            "## 3. Перевірка DOM через BeautifulSoup4\n"
            "Автоматичний валідатор аналізує CSS-селектори (`header > h1`, `table tr`, `form`) "
            "та перевіряє обов'язкові атрибути елементів."
        ),
    )
    module.quiz_questions = [
        QuizQuestion(
            question_text="Яка декларація на початку документа вказує браузеру на стандарт HTML5?",
            options=[
                "<?xml version='1.0'?>",
                "<!DOCTYPE html>",
                "<meta charset='utf-8'>",
                "<html version='5.0'>",
            ],
            correct_option_index=1,
        ),
        QuizQuestion(
            question_text=(
                "Який семантичний тег HTML5 призначений для основного унікального вмісту?"
            ),
            options=["<div>", "<main>", "<aside>", "<span>"],
            correct_option_index=1,
        ),
        QuizQuestion(
            question_text="Який тег використовується для створення рядка в HTML-таблиці?",
            options=["<td>", "<th>", "<tr>", "<row>"],
            correct_option_index=2,
        ),
        QuizQuestion(
            question_text=(
                "Який атрибут є обов'язковим для тегу зображення <img> з точки зору доступності?"
            ),
            options=["title", "alt", "name", "target"],
            correct_option_index=1,
        ),
        QuizQuestion(
            question_text="Який CSS-селектор обирає всі рядки tr усередині таблиці table?",
            options=["table + tr", "table tr", "tr > table", "#table.tr"],
            correct_option_index=1,
        ),
    ]
    module.practical = Practical(
        title="Практична робота №1: Верстка сторінки розкладу занять у HTML5",
        instructions=(
            "Напишіть HTML5-код у вбудованій пісочниці. Сторінка повинна містити семантичну "
            "шапку `<header>` із заголовком `<h1>`, блок `<main>`, таблицю `<table>` "
            "щонайменше з 4 рядками `<tr>` та форму зворотного зв'язку `<form>`."
        ),
        format_type=PracticalFormat.HTML,
        max_score=Decimal("10.00"),
        variants=[
            {
                "variant_number": 1,
                "title": "Варіант 1: Сторінка розкладу занять групи КН-31",
                "task_description": (
                    "Зверстайте сторінку з розкладом пар на тиждень у вигляді таблиці (4+ рядки) "
                    "та формою запису на консультацію викладача."
                ),
                "parameters": {"required_heading": "Розклад занять КН-31", "min_rows": 4},
            },
            {
                "variant_number": 2,
                "title": "Варіант 2: Сторінка каталогу електронних посібників кафедри",
                "task_description": (
                    "Зверстайте таблицю навчальних посібників (4+ рядки) із колонками Назва, "
                    "Дисципліна, Рік видання та формою замовлення примірника."
                ),
                "parameters": {"required_heading": "Каталог електронних посібників", "min_rows": 4},
            },
            {
                "variant_number": 3,
                "title": "Варіант 3: Сторінка рейтингу успішності студентів потоку",
                "task_description": (
                    "Зверстайте зведену таблицю рейтингу студентів (4+ рядки) "
                    "та форму подання апеляції щодо результатів перевірки."
                ),
                "parameters": {"required_heading": "Рейтинг успішності студентів", "min_rows": 4},
            },
        ],
        grading_rules=[
            {
                "id": "html_rule_1",
                "type": "html_tag_exists",
                "target": "header > h1",
                "expected": "true",
                "points": 2.5,
                "description": "Наявний семантичний блок <header> із заголовком першого рівня <h1>",
            },
            {
                "id": "html_rule_2",
                "type": "html_tag_exists",
                "target": "main",
                "expected": "true",
                "points": 2.0,
                "description": "Основний контент сторінки обгорнуто в семантичний тег <main>",
            },
            {
                "id": "html_rule_3",
                "type": "html_tag_count",
                "target": "table tr",
                "expected": ">=4",
                "points": 3.0,
                "description": "Таблиця містить щонайменше 4 рядки (<tr>)",
            },
            {
                "id": "html_rule_4",
                "type": "html_tag_exists",
                "target": "form",
                "expected": "true",
                "points": 2.5,
                "description": "Сторінка містить інтерактивну форму <form>",
            },
        ],
    )
    return course


def build_seed_bundle() -> SeedBundle:
    """Конструює повний граф тестових даних: групу, викладача, студентів та 4 курси."""
    group = AcademicGroup(
        code="КН-31",
        specialty="122 Комп'ютерні науки",
        course_year=3,
    )
    admin = User(
        email="admin@kpefk.lcloud.in.ua",
        password_hash=hash_password("Admin123!"),
        full_name="Адміністратор Системи",
        role=UserRole.ADMIN,
        group=None,
        list_number=None,
    )
    teacher = User(
        email="teacher@kpefk.lcloud.in.ua",
        password_hash=hash_password("Teacher123!"),
        full_name="Коваленко Олександр Петрович",
        role=UserRole.TEACHER,
        group=None,
        list_number=None,
    )
    students: list[User] = [
        User(
            email="student1@kpefk.lcloud.in.ua",
            password_hash=hash_password("Student123!"),
            full_name="Бондаренко Ірина Василівна",
            role=UserRole.STUDENT,
            group=group,
            list_number=1,
        ),
        User(
            email="student2@kpefk.lcloud.in.ua",
            password_hash=hash_password("Student123!"),
            full_name="Мельник Дмитро Сергійович",
            role=UserRole.STUDENT,
            group=group,
            list_number=2,
        ),
        User(
            email="student3@kpefk.lcloud.in.ua",
            password_hash=hash_password("Student123!"),
            full_name="Шевченко Максим Андрійович",
            role=UserRole.STUDENT,
            group=group,
            list_number=3,
        ),
    ]

    courses: list[Course] = [
        _build_word_course(teacher),
        _build_excel_course(teacher),
        _build_access_course(teacher),
        _build_html_course(teacher),
    ]

    if not (MIN_COURSE_YEAR <= group.course_year <= MAX_COURSE_YEAR):
        raise ValueError(
            f"Курс академічної групи має бути в межах {MIN_COURSE_YEAR}..{MAX_COURSE_YEAR}."
        )

    course_slugs = tuple(course.slug for course in courses)
    if len(courses) != MAX_COURSES_COUNT or course_slugs != ALLOWED_COURSE_SLUGS:
        raise ValueError(
            "Набір початкових даних повинен містити виключно 4 дисципліни: "
            "word, excel, access, html."
        )

    return SeedBundle(
        group=group,
        admin=admin,
        teacher=teacher,
        students=students,
        courses=courses,
    )


def summarize_bundle(bundle: SeedBundle) -> SeedSummary:
    """Обчислює кількісні показники підготовленого набору початкових даних."""
    modules_count = sum(len(course.modules) for course in bundle.courses)
    questions_count = sum(
        len(module.quiz_questions)
        for course in bundle.courses
        for module in course.modules
    )
    practicals_count = sum(
        1
        for course in bundle.courses
        for module in course.modules
        if module.practical is not None
    )
    return SeedSummary(
        group_code=bundle.group.code,
        users_count=2 + len(bundle.students),
        courses_count=len(bundle.courses),
        modules_count=modules_count,
        questions_count=questions_count,
        practicals_count=practicals_count,
    )


async def seed_database(session: AsyncSession) -> SeedSummary:
    """Ідемпотентно наповнює базу даних групою, користувачами та 4 курсами."""
    bundle = build_seed_bundle()

    existing_group_result = await session.execute(
        select(AcademicGroup).where(AcademicGroup.code == bundle.group.code)
    )
    group = existing_group_result.scalar_one_or_none()
    if group is None:
        group = bundle.group
        session.add(group)
        await session.flush()

    all_seed_users: list[User] = [bundle.admin, bundle.teacher, *bundle.students]
    persisted_teacher: User | None = None

    for candidate in all_seed_users:
        user_result = await session.execute(select(User).where(User.email == candidate.email))
        existing_user = user_result.scalar_one_or_none()
        if existing_user is None:
            if candidate.role == UserRole.STUDENT:
                candidate.group = group
            session.add(candidate)
            await session.flush()
            target_user = candidate
        else:
            target_user = existing_user

        if target_user.role == UserRole.TEACHER:
            persisted_teacher = target_user

    if persisted_teacher is None:
        raise RuntimeError("Не вдалося створити або знайти обліковий запис викладача.")

    for course in bundle.courses:
        course_result = await session.execute(
            select(Course).where(Course.slug == course.slug)
        )
        existing_course = course_result.scalar_one_or_none()
        if existing_course is None:
            course.teacher = persisted_teacher
            session.add(course)

    await session.commit()
    return summarize_bundle(bundle)


async def run_seed(*, dry_run: bool = False) -> SeedSummary:
    """Запускає ініціалізацію даних у режимі запису в БД або сухої перевірки (--dry-run)."""
    bundle = build_seed_bundle()
    if dry_run:
        return summarize_bundle(bundle)

    async with AsyncSessionLocal() as session:
        return await seed_database(session)


def main(argv: Sequence[str] | None = None) -> int:
    """CLI-точка входу для запуску наповнення бази даних (`python -m app.seed`)."""
    parser = argparse.ArgumentParser(
        description="Наповнення БД Edu Auto Grader початковими курсами та користувачами."
    )
    parser.add_argument(
        "--dry-run",
        action="store_true",
        help="Перевірити побудову ORM-об'єктів без підключення до PostgreSQL.",
    )
    args = parser.parse_args(argv)

    summary = asyncio.run(run_seed(dry_run=bool(args.dry_run)))
    mode_label = "DRY-RUN" if args.dry_run else "APPLIED"
    print(
        f"[seed:{mode_label}] group={summary.group_code} "
        f"users={summary.users_count} courses={summary.courses_count} "
        f"modules={summary.modules_count} questions={summary.questions_count} "
        f"practicals={summary.practicals_count}"
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
