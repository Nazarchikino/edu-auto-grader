# Graph Report - edu-auto-grader  (2026-11-18)

## Corpus Check
- 58 files · ~34,126 words
- Verdict: corpus is large enough that graph structure adds value.
- Unclassified: 7 file(s) not represented in the graph (top: (none) 4, .ini 1, .mako 1)

## Summary
- 1055 nodes · 2552 edges · 67 communities (35 shown, 32 thin omitted)
- Extraction: 97% EXTRACTED · 3% INFERRED · 0% AMBIGUOUS · INFERRED: 74 edges (avg confidence: 0.92)
- Token cost: 0 input · 0 output

## Graph Freshness
- Built from commit: `f735543c`
- Run `git rev-parse HEAD` and compare to check if the graph is stale.
- Run `graphify update .` after code changes (no API cost).

## Community Hubs (Navigation)
- package.json
- postgres
- compilerOptions
- main.py
- main.tsx
- QuizService
- courses.py
- client.ts
- scripts
- vite-env.d.ts
- export_service.py
- metadata.py
- base.py
- seed.py
- UUID
- edu-auto-grader-backend
- HtmlGrader
- devDependencies
- eslint.config.js
- api.ts
- vite
- course.ts
- grading.ts
- security.py
- XlsxGrader
- DocxGrader
- AccdbGrader
- BaseGrader
- practicals.py
- xlsx_grader.py
- DomainError
- GradingError
- get_db
- User
- DomainError
- submit_practical_work
- evaluate_plagiarism
- Depends
- create_application
- upsert_module_practical
- services/__init__.py
- create_course
- 0001_initial_schema.py
- ExportService
- ._evaluate_line_spacing
- get_current_user
- parse_core_xml_bytes
- submission_service.py
- accdb_grader.py
- html_grader.py
- docx_grader.py
- ._evaluate_file_submission
- ._extract_single_table_schema
- BaseGrader
- Settings
- AcademicGroupBase
- .update_grading_rules
- CriterionResult

## God Nodes (most connected - your core abstractions)
1. `DomainError` - 41 edges
2. `User` - 38 edges
3. `DocxGrader` - 34 edges
4. `InvalidFileFormatError` - 32 edges
5. `GradingError` - 32 edges
6. `get_db()` - 31 edges
7. `PracticalFormat` - 26 edges
8. `XlsxGrader` - 25 edges
9. `BaseGrader` - 25 edges
10. `Practical` - 21 edges

## Surprising Connections (you probably didn't know these)
- `list_academic_groups()` --uses--> `ExportService`  [INFERRED]
  backend/app/api/v1/analytics.py → backend/app/services/export_service.py
- `get_group_journal()` --uses--> `ExportService`  [INFERRED]
  backend/app/api/v1/analytics.py → backend/app/services/export_service.py
- `export_group_journal()` --uses--> `ExportService`  [INFERRED]
  backend/app/api/v1/analytics.py → backend/app/services/export_service.py
- `SubmissionRead` --uses--> `ExtractedMetadata`  [INFERRED]
  backend/app/schemas/submission.py → backend/app/schemas/grading.py
- `GradingReport` --uses--> `PracticalFormat`  [INFERRED]
  backend/app/schemas/grading.py → backend/app/models/course.py

## Import Cycles
- None detected.

## Communities (67 total, 32 thin omitted)

### Community 0 - "package.json"
Cohesion: 0.17
Nodes (15): dependencies, lucide-react@^0.460.0, @monaco-editor/react@4.6.0, react-dom@^18.3.1, react-router-dom@^6.28.0, @tanstack/react-query@^5.60.0, name, private (+7 more)

### Community 1 - "postgres"
Cohesion: 0.10
Nodes (20): POSTGRES_DB, POSTGRES_PASSWORD, POSTGRES_USER, interval, retries, test, timeout, container_name (+12 more)

### Community 2 - "compilerOptions"
Cohesion: 0.10
Nodes (20): compilerOptions, allowImportingTsExtensions, isolatedModules, jsx, lib, module, moduleDetection, moduleResolution (+12 more)

### Community 4 - "main.tsx"
Cohesion: 0.32
Nodes (5): react@^18.3.1, App(), queryClient, rootElement, react

### Community 6 - "courses.py"
Cohesion: 0.10
Nodes (22): PracticalFormat, CourseCreate, CourseRead, CourseUpdate, ModuleCreate, ModuleDetailRead, ModuleSummaryRead, ModuleUpdate (+14 more)

### Community 7 - "client.ts"
Cohesion: 0.22
Nodes (3): axios@^1.7.7, apiClient, axios

### Community 8 - "scripts"
Cohesion: 0.33
Nodes (6): scripts, build, dev, lint, preview, typecheck

### Community 11 - "export_service.py"
Cohesion: 0.10
Nodes (12): GradingReport, CriterionErrorStat, ExportFormat, GroupJournalRead, GroupJournalRow, GroupJournalStudentCell, HtmlSubmissionRequest, ManualGradeUpdateRequest (+4 more)

### Community 13 - "metadata.py"
Cohesion: 0.23
Nodes (6): InvalidFileFormatError, compute_bytes_sha256(), compute_code_sha256(), compute_file_sha256(), compute_submission_hash(), normalize_code_for_hashing()

### Community 15 - "seed.py"
Cohesion: 0.08
Nodes (20): do_run_migrations(), run_async_migrations(), run_migrations_online(), hash_password(), Course, Practical, QuizQuestion, AcademicGroup (+12 more)

### Community 17 - "UUID"
Cohesion: 0.23
Nodes (6): _fetch_user_progress_maps(), get_course(), list_courses(), _load_course_or_404(), _serialize_course(), update_course()

### Community 23 - "devDependencies"
Cohesion: 0.13
Nodes (15): devDependencies, autoprefixer@^10.4.20, eslint@^9.15.0, postcss@^8.4.49, tailwindcss@^3.4.15, @types/react@^18.3.12, @types/react-dom@^18.3.1, typescript@~5.6.3 (+7 more)

### Community 24 - "eslint.config.js"
Cohesion: 0.18
Nodes (10): @eslint/js@^9.15.0, eslint-plugin-react-hooks@^5.0.0, eslint-plugin-react-refresh@^0.4.14, globals@^15.12.0, typescript-eslint@^8.15.0, @eslint/js, eslint-plugin-react-hooks, eslint-plugin-react-refresh (+2 more)

### Community 25 - "api.ts"
Cohesion: 0.09
Nodes (23): AcademicGroupBase, AcademicGroupCreate, AcademicGroupRead, CriterionErrorStat, ErrorResponse, EXPORT_FORMATS, ExportFormat, GroupJournalRead (+15 more)

### Community 26 - "vite"
Cohesion: 0.40
Nodes (4): vite@^5.4.11, @vitejs/plugin-react@^4.3.3, vite, @vitejs/plugin-react

### Community 27 - "course.ts"
Cohesion: 0.13
Nodes (22): COURSE_SLUGS, CourseCreate, CourseRead, CourseUpdate, ModuleCreate, ModuleDetailRead, ModuleSummaryRead, ModuleUpdate (+14 more)

### Community 28 - "grading.ts"
Cohesion: 0.20
Nodes (10): SubmissionRead, CourseSlug, CriterionResult, ExtractedMetadata, GRADING_RULE_TYPES, GradingReport, GradingRulesUpdateRequest, GradingRuleType (+2 more)

### Community 29 - "security.py"
Cohesion: 0.10
Nodes (9): login(), read_current_user(), refresh_tokens(), serialize_user(), create_access_token(), create_refresh_token(), create_token_pair(), decode_token() (+1 more)

### Community 32 - "AccdbGrader"
Cohesion: 0.10
Nodes (6): AccdbColumnSchema, AccdbDatabaseSchema, AccdbGrader, _is_numeric_condition(), _is_system_table_name(), _strip_identifiers()

### Community 35 - "practicals.py"
Cohesion: 0.09
Nodes (13): require_role(), verify_password(), _enum_values(), UserRole, ErrorResponse, LoginRequest, RefreshTokenRequest, TokenPayload (+5 more)

### Community 36 - "xlsx_grader.py"
Cohesion: 0.16
Nodes (3): _canonicalize_formula(), _format_cell_value(), _is_wrapped_in_parens()

### Community 39 - "get_db"
Cohesion: 0.21
Nodes (4): get_submission_detail(), list_my_submissions(), list_submissions(), update_submission_grade()

### Community 40 - "User"
Cohesion: 0.24
Nodes (5): _build_module_detail_read(), create_module(), get_module(), _load_module_or_404(), update_module()

### Community 41 - "DomainError"
Cohesion: 0.14
Nodes (5): role_checker(), _parse_export_format(), DomainError, PlagiarismDetectedError, QuizNotPassedError

### Community 42 - "submit_practical_work"
Cohesion: 0.14
Nodes (4): _extract_submission_payload(), ExtractedSubmissionPayload, submit_practical_work(), update_practical_grading_rules()

### Community 43 - "evaluate_plagiarism"
Cohesion: 0.16
Nodes (4): check_submission_plagiarism(), _coerce_metadata(), evaluate_plagiarism(), SubmissionRecordProtocol

### Community 44 - "Depends"
Cohesion: 0.13
Nodes (6): export_group_journal(), get_group_journal(), list_academic_groups(), delete_quiz_question(), get_practical_for_student(), list_module_quiz_questions_teacher()

### Community 46 - "upsert_module_practical"
Cohesion: 0.24
Nodes (4): get_practical_for_teacher(), _serialize_practical_teacher(), update_practical(), upsert_module_practical()

### Community 48 - "create_course"
Cohesion: 0.15
Nodes (4): create_course(), create_quiz_question(), submit_module_quiz(), get_db()

### Community 50 - "ExportService"
Cohesion: 0.06
Nodes (12): _auto_adjust_worksheet_columns(), build_content_disposition(), _configure_pdf_font(), ExportedDocument, ExportService, GroupJournalBundle, PracticalColumnInfo, _prepare_pdf_text() (+4 more)

### Community 55 - "submission_service.py"
Cohesion: 0.18
Nodes (7): Base, CourseSlug, _enum_values(), Module, QuizAttempt, Submission, User

### Community 56 - "accdb_grader.py"
Cohesion: 0.13
Nodes (6): build_accdb_bytes(), _encode_data_page(), _encode_msys_catalog_record(), _encode_tdef_page(), _parse_ddl_column_type(), _resolve_canonical_type()

### Community 57 - "html_grader.py"
Cohesion: 0.13
Nodes (8): _attribute_value_matches(), _find_tag_attr_key(), _get_tag_attribute_str(), _is_doctype_target(), _normalize_text(), _parse_text_match_expected(), _strip_quotes(), _tag_has_attribute()

### Community 60 - "._evaluate_file_submission"
Cohesion: 0.27
Nodes (3): extract_core_xml_metadata(), extract_document_metadata(), ExtractedMetadata

### Community 64 - "AcademicGroupBase"
Cohesion: 0.33
Nodes (3): AcademicGroupBase, AcademicGroupCreate, AcademicGroupRead

## Knowledge Gaps
- **1 isolated node(s):** `edu-auto-grader-backend`
  These have ≤1 connection - possible missing edges. (Counts symbols only; 513 node(s) total have ≤1 connection when file, concept and rationale nodes are included.)
- **32 thin communities (<3 nodes) omitted from report** — run `graphify query` to explore isolated nodes.

## Suggested Questions
_Questions this graph is uniquely positioned to answer:_

- **Why does `DocxGrader` connect `DocxGrader` to `._evaluate_font`, `GradingError`, `metadata.py`, `BaseGrader`, `._evaluate_line_spacing`, `._evaluate_page_margins`, `DocxDocument`, `docx_grader.py`, `BaseGrader`?**
  _High betweenness centrality (0.069) - this node is a cross-community bridge._
- **Are the 6 inferred relationships involving `User` (e.g. with `_build_access_course()` and `_build_excel_course()`) actually correct?**
  _`User` has 6 INFERRED edges - model-reasoned connections that need verification._
- **What connects `edu-auto-grader-backend` to the rest of the system?**
  _1 weakly-connected nodes found - possible missing edges._
- **Should `postgres` be split into smaller, more focused modules?**
  _Cohesion score 0.09523809523809523 - nodes in this community are weakly interconnected._
- **Why does `GradingError` connect `GradingError` to `AccdbGrader`, `._evaluate_font`, `BaseGrader`, `practicals.py`, `xlsx_grader.py`, `DomainError`, `metadata.py`, `base.py`, `._evaluate_page_margins`, `HtmlGrader`, `submission_service.py`, `accdb_grader.py`, `html_grader.py`, `docx_grader.py`, `XlsxGrader`?**
  _High betweenness centrality (0.068) - this node is a cross-community bridge._
- **Should `compilerOptions` be split into smaller, more focused modules?**
  _Cohesion score 0.09523809523809523 - nodes in this community are weakly interconnected._
- **Why does `DomainError` connect `DomainError` to `.update_grading_rules`, `practicals.py`, `QuizService`, `courses.py`, `GradingError`, `User`, `DomainError`, `export_service.py`, `Depends`, `upsert_module_practical`, `create_course`, `UUID`, `ExportService`, `get_current_user`, `submission_service.py`, `security.py`?**
  _High betweenness centrality (0.060) - this node is a cross-community bridge._