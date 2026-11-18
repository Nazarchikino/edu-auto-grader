# Graph Report - edu-auto-grader  (2026-11-19)

## Corpus Check
- 59 files · ~38,171 words
- Verdict: corpus is large enough that graph structure adds value.
- Unclassified: 7 file(s) not represented in the graph (top: (none) 4, .ini 1, .mako 1)

## Summary
- 1147 nodes · 2834 edges · 60 communities (39 shown, 21 thin omitted)
- Extraction: 97% EXTRACTED · 3% INFERRED · 0% AMBIGUOUS · INFERRED: 98 edges (avg confidence: 0.91)
- Token cost: 0 input · 0 output

## Graph Freshness
- Built from commit: `54b37b27`
- Run `git rev-parse HEAD` and compare to check if the graph is stale.
- Run `graphify update .` after code changes (no API cost).

## Community Hubs (Navigation)
- package.json
- postgres
- compilerOptions
- conftest.py
- main.tsx
- QuizService
- courses.py
- client.ts
- scripts
- vite-env.d.ts
- export_service.py
- InvalidFileFormatError
- env.py
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
- schemas/__init__.py
- xlsx_grader.py
- SubmissionService
- get_db
- User
- courses.py
- test_submissions_api.py
- evaluate_plagiarism
- Depends
- submission_service.py
- upsert_module_practical
- services/__init__.py
- create_course
- 0001_initial_schema.py
- ExportService
- _find_tag_attr_key
- get_current_user
- ExportFormat
- submission_service.py
- docx_grader.py
- Settings

## God Nodes (most connected - your core abstractions)
1. `DomainError` - 41 edges
2. `User` - 40 edges
3. `DocxGrader` - 37 edges
4. `InvalidFileFormatError` - 33 edges
5. `GradingError` - 33 edges
6. `get_db()` - 31 edges
7. `XlsxGrader` - 28 edges
8. `PracticalFormat` - 27 edges
9. `BaseGrader` - 25 edges
10. `GradingRule` - 24 edges

## Surprising Connections (you probably didn't know these)
- `GradingReport` --uses--> `PracticalFormat`  [INFERRED]
  backend/app/schemas/grading.py → backend/app/models/course.py
- `SubmissionRead` --uses--> `CourseSlug`  [INFERRED]
  backend/app/schemas/submission.py → backend/app/models/course.py
- `SubmissionRead` --uses--> `ExtractedMetadata`  [INFERRED]
  backend/app/schemas/submission.py → backend/app/schemas/grading.py
- `build_seed_bundle()` --uses--> `Course`  [INFERRED]
  backend/app/seed.py → backend/app/models/course.py
- `seed_database()` --uses--> `Course`  [INFERRED]
  backend/app/seed.py → backend/app/models/course.py

## Import Cycles
- None detected.

## Communities (60 total, 21 thin omitted)

### Community 0 - "package.json"
Cohesion: 0.17
Nodes (15): dependencies, lucide-react@^0.460.0, @monaco-editor/react@4.6.0, react-dom@^18.3.1, react-router-dom@^6.28.0, @tanstack/react-query@^5.60.0, name, private (+7 more)

### Community 1 - "postgres"
Cohesion: 0.10
Nodes (20): POSTGRES_DB, POSTGRES_PASSWORD, POSTGRES_USER, interval, retries, test, timeout, container_name (+12 more)

### Community 2 - "compilerOptions"
Cohesion: 0.10
Nodes (20): compilerOptions, allowImportingTsExtensions, isolatedModules, jsx, lib, module, moduleDetection, moduleResolution (+12 more)

### Community 3 - "conftest.py"
Cohesion: 0.05
Nodes (22): GradingRule, async_client(), build_sample_accdb(), build_sample_docx(), build_sample_xlsx(), _compile_jsonb_for_sqlite(), _create_sqlite_test_engine(), db_session() (+14 more)

### Community 4 - "main.tsx"
Cohesion: 0.32
Nodes (5): react@^18.3.1, App(), queryClient, rootElement, react

### Community 6 - "courses.py"
Cohesion: 0.08
Nodes (18): CourseCreate, CourseRead, CourseUpdate, ModuleCreate, ModuleDetailRead, ModuleSummaryRead, ModuleUpdate, PracticalCreate (+10 more)

### Community 7 - "client.ts"
Cohesion: 0.22
Nodes (3): axios@^1.7.7, apiClient, axios

### Community 8 - "scripts"
Cohesion: 0.33
Nodes (6): scripts, build, dev, lint, preview, typecheck

### Community 11 - "export_service.py"
Cohesion: 0.07
Nodes (18): CriterionErrorStat, GroupJournalRead, GroupJournalRow, GroupJournalStudentCell, _auto_adjust_worksheet_columns(), build_content_disposition(), build_group_journal(), calculate_criterion_error_stats() (+10 more)

### Community 13 - "InvalidFileFormatError"
Cohesion: 0.13
Nodes (11): InvalidFileFormatError, compute_bytes_sha256(), compute_code_sha256(), compute_file_sha256(), compute_submission_hash(), extract_core_xml_metadata(), extract_document_metadata(), _find_xml_text() (+3 more)

### Community 14 - "env.py"
Cohesion: 0.18
Nodes (4): do_run_migrations(), run_async_migrations(), run_migrations_offline(), run_migrations_online()

### Community 15 - "seed.py"
Cohesion: 0.15
Nodes (9): AcademicGroup, build_seed_bundle(), hash_password(), main(), run_seed(), seed_database(), SeedBundle, SeedSummary (+1 more)

### Community 17 - "UUID"
Cohesion: 0.20
Nodes (7): create_course(), _fetch_user_progress_maps(), get_course(), list_courses(), _load_course_or_404(), _serialize_course(), update_course()

### Community 22 - "HtmlGrader"
Cohesion: 0.14
Nodes (3): GradingError, HtmlGrader, _normalize_selector()

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
Cohesion: 0.14
Nodes (8): create_access_token(), create_refresh_token(), create_token_pair(), decode_token(), _encode_jwt_token(), hash_password(), verify_password(), TokenResponse

### Community 30 - "XlsxGrader"
Cohesion: 0.10
Nodes (3): _canonicalize_formula(), _try_parse_numeric(), XlsxGrader

### Community 32 - "AccdbGrader"
Cohesion: 0.06
Nodes (13): AccdbColumnSchema, AccdbDatabaseSchema, AccdbGrader, AccdbTableSchema, build_accdb_bytes(), _encode_data_page(), _encode_msys_catalog_record(), _encode_tdef_page() (+5 more)

### Community 35 - "schemas/__init__.py"
Cohesion: 0.15
Nodes (11): AcademicGroupBase, AcademicGroupCreate, AcademicGroupRead, ErrorResponse, LoginRequest, RefreshTokenRequest, TokenPayload, UserBase (+3 more)

### Community 37 - "SubmissionService"
Cohesion: 0.08
Nodes (7): _extract_submission_payload(), ExtractedSubmissionPayload, submit_practical_work(), update_practical_grading_rules(), serialize_practical_teacher(), serialize_submission(), SubmissionService

### Community 39 - "get_db"
Cohesion: 0.23
Nodes (4): get_submission_detail(), list_my_submissions(), list_submissions(), update_submission_grade()

### Community 40 - "User"
Cohesion: 0.22
Nodes (5): _build_module_detail_read(), create_module(), get_module(), _load_module_or_404(), update_module()

### Community 41 - "courses.py"
Cohesion: 0.13
Nodes (6): require_role(), role_checker(), DomainError, PlagiarismDetectedError, QuizNotPassedError, create_application()

### Community 42 - "test_submissions_api.py"
Cohesion: 0.09
Nodes (11): _set_sqlite_pragma(), make_auth_headers(), SqliteAsyncSessionAdapter, _get_course_module_and_practical(), _get_user_by_email(), _grant_quiz_pass(), test_antiplagiarism_flags_sha256_and_core_xml_matches_across_students(), test_health_check_and_jwt_login_flow() (+3 more)

### Community 43 - "evaluate_plagiarism"
Cohesion: 0.13
Nodes (5): check_submission_plagiarism(), _coerce_metadata(), evaluate_plagiarism(), SubmissionRecordProtocol, PlagiarismCheckResult

### Community 44 - "Depends"
Cohesion: 0.12
Nodes (6): export_group_journal(), get_group_journal(), list_academic_groups(), create_quiz_question(), delete_quiz_question(), list_module_quiz_questions_teacher()

### Community 45 - "submission_service.py"
Cohesion: 0.14
Nodes (7): _enum_values(), UserRole, GradingReport, GradingRulesUpdateRequest, HtmlSubmissionRequest, ManualGradeUpdateRequest, SubmissionRead

### Community 46 - "upsert_module_practical"
Cohesion: 0.21
Nodes (4): get_practical_for_teacher(), _serialize_practical_teacher(), update_practical(), upsert_module_practical()

### Community 47 - "services/__init__.py"
Cohesion: 0.29
Nodes (3): PracticalVariant, calculate_variant_index(), resolve_student_variant()

### Community 48 - "create_course"
Cohesion: 0.20
Nodes (3): get_practical_for_student(), submit_module_quiz(), get_db()

### Community 51 - "_find_tag_attr_key"
Cohesion: 0.38
Nodes (3): _find_tag_attr_key(), _get_tag_attribute_str(), _tag_has_attribute()

### Community 52 - "get_current_user"
Cohesion: 0.11
Nodes (5): get_current_user(), login(), read_current_user(), refresh_tokens(), serialize_user()

### Community 55 - "submission_service.py"
Cohesion: 0.13
Nodes (15): Base, Course, CourseSlug, _enum_values(), Module, Practical, PracticalFormat, QuizQuestion (+7 more)

### Community 57 - "docx_grader.py"
Cohesion: 0.09
Nodes (7): _attribute_value_matches(), _is_doctype_target(), _normalize_text(), _parse_text_match_expected(), _strip_quotes(), CriterionResult, GradingRuleType

## Knowledge Gaps
- **1 isolated node(s):** `edu-auto-grader-backend`
  These have ≤1 connection - possible missing edges. (Counts symbols only; 558 node(s) total have ≤1 connection when file, concept and rationale nodes are included.)
- **21 thin communities (<3 nodes) omitted from report** — run `graphify query` to explore isolated nodes.

## Suggested Questions
_Questions this graph is uniquely positioned to answer:_

- **Why does `DocxGrader` connect `DocxGrader` to `._parse_expected_font`, `BaseGrader`, `conftest.py`, `.build_criterion_result`, `InvalidFileFormatError`, `BaseGrader`, `._select_sections`, `._parse_expected_margins`, `docx_grader.py`?**
  _High betweenness centrality (0.063) - this node is a cross-community bridge._
- **Are the 6 inferred relationships involving `User` (e.g. with `_build_access_course()` and `_build_excel_course()`) actually correct?**
  _`User` has 6 INFERRED edges - model-reasoned connections that need verification._
- **What connects `edu-auto-grader-backend` to the rest of the system?**
  _1 weakly-connected nodes found - possible missing edges._
- **Should `postgres` be split into smaller, more focused modules?**
  _Cohesion score 0.09523809523809523 - nodes in this community are weakly interconnected._
- **Why does `GradingError` connect `HtmlGrader` to `AccdbGrader`, `._parse_expected_font`, `BaseGrader`, `conftest.py`, `xlsx_grader.py`, `.build_criterion_result`, `courses.py`, `InvalidFileFormatError`, `._parse_expected_margins`, `docx_grader.py`, `XlsxGrader`, `DocxGrader`?**
  _High betweenness centrality (0.061) - this node is a cross-community bridge._
- **Should `compilerOptions` be split into smaller, more focused modules?**
  _Cohesion score 0.09523809523809523 - nodes in this community are weakly interconnected._
- **Why does `DomainError` connect `courses.py` to `QuizService`, `SubmissionService`, `User`, `export_service.py`, `Depends`, `submission_service.py`, `upsert_module_practical`, `UUID`, `ExportService`, `get_current_user`, `ExportFormat`, `HtmlGrader`, `security.py`?**
  _High betweenness centrality (0.060) - this node is a cross-community bridge._