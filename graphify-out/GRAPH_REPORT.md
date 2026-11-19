# Graph Report - edu-auto-grader  (2026-11-19)

## Corpus Check
- 78 files · ~82,740 words
- Verdict: corpus is large enough that graph structure adds value.
- Unclassified: 7 file(s) not represented in the graph (top: (none) 4, .ini 1, .mako 1)

## Summary
- 1423 nodes · 3867 edges · 74 communities (33 shown, 41 thin omitted)
- Extraction: 92% EXTRACTED · 8% INFERRED · 0% AMBIGUOUS · INFERRED: 324 edges (avg confidence: 0.93)
- Token cost: 0 input · 0 output

## Graph Freshness
- Built from commit: `2b0ce5af`
- Run `git rev-parse HEAD` and compare to check if the graph is stale.
- Run `graphify update .` after code changes (no API cost).

## Community Hubs (Navigation)
- v1/auth.py
- postgres
- compilerOptions
- InvalidFileFormatError
- list_admin_users
- test_admin_api.py
- get_current_user
- GradebookPage.tsx
- list_my_submissions
- vite-env.d.ts
- build_group_journal
- InvalidFileFormatError
- submit_practical_work
- SqliteAsyncSessionAdapter
- seed_database
- schemas/__init__.py
- edu-auto-grader-backend
- package.json
- App.tsx
- DomainError
- AdminUsersPage.tsx
- course.ts
- build_accdb_bytes
- AuthContext.tsx
- XlsxGrader
- DocxGrader
- AccdbGrader
- QuizService
- _format_number
- import_admin_students
- _canonicalize_formula
- submission_service.py
- conftest.py
- _create_sqlite_test_engine
- GradebookPage.tsx
- test_submissions_api.py
- _compile_jsonb_for_sqlite
- ModuleViewPage.tsx
- _normalize_text
- export_service.py
- _enum_values
- html_grader.py
- ExportService
- student_import_service.py
- get_db
- 0001_initial_schema.py
- 0002_restrict_course_year_to_4.py
- env.py

## God Nodes (most connected - your core abstractions)
1. `GradingRule` - 63 edges
2. `DomainError` - 58 edges
3. `User` - 53 edges
4. `InvalidFileFormatError` - 49 edges
5. `DocxGrader` - 45 edges
6. `PracticalFormat` - 43 edges
7. `GradingError` - 40 edges
8. `get_db()` - 40 edges
9. `SubmissionService` - 39 edges
10. `XlsxGrader` - 36 edges

## Surprising Connections (you probably didn't know these)
- `create_admin_group()` --uses--> `AcademicGroupCreate`  [INFERRED]
  backend/app/api/v1/admin.py → backend/app/schemas/auth.py
- `update_admin_group()` --uses--> `AcademicGroupUpdate`  [INFERRED]
  backend/app/api/v1/admin.py → backend/app/schemas/auth.py
- `list_admin_users()` --uses--> `UserRead`  [INFERRED]
  backend/app/api/v1/admin.py → backend/app/schemas/auth.py
- `create_admin_user()` --uses--> `UserCreate`  [INFERRED]
  backend/app/api/v1/admin.py → backend/app/schemas/auth.py
- `create_admin_user()` --uses--> `UserRead`  [INFERRED]
  backend/app/api/v1/admin.py → backend/app/schemas/auth.py

## Import Cycles
- None detected.

## Communities (74 total, 41 thin omitted)

### Community 0 - "v1/auth.py"
Cohesion: 0.07
Nodes (22): login(), read_current_user(), refresh_tokens(), serialize_user(), create_access_token(), create_refresh_token(), create_token_pair(), decode_token() (+14 more)

### Community 1 - "postgres"
Cohesion: 0.10
Nodes (20): POSTGRES_DB, POSTGRES_PASSWORD, POSTGRES_USER, interval, retries, test, timeout, container_name (+12 more)

### Community 2 - "compilerOptions"
Cohesion: 0.10
Nodes (20): compilerOptions, allowImportingTsExtensions, isolatedModules, jsx, lib, module, moduleDetection, moduleResolution (+12 more)

### Community 3 - "InvalidFileFormatError"
Cohesion: 0.06
Nodes (21): GradingError, InvalidFileFormatError, AccdbGrader, _parse_ddl_column_type(), BaseGrader, GraderFactory, HtmlGrader, PracticalFormat (+13 more)

### Community 5 - "test_admin_api.py"
Cohesion: 0.14
Nodes (9): _build_college_import_docx(), _get_user_by_email(), test_admin_academic_groups_crud_and_detachment(), test_admin_bulk_import_docx_sorts_ukrainian_alphabet_and_assigns_variants(), test_admin_bulk_import_rbac_and_validation_errors(), test_admin_bulk_import_txt_formats_continuing_list_number_and_duplicates(), test_admin_endpoints_enforce_admin_rbac(), test_admin_users_crud_filters_and_safety_guards() (+1 more)

### Community 7 - "GradebookPage.tsx"
Cohesion: 0.11
Nodes (27): lucide-react@^0.460.0, COURSE_SLUG_LABELS, CriterionBreakdownItem(), CriterionFilterMode, extractFileNameFromPath(), FORMAT_META, formatDateTime(), GradingReportCard() (+19 more)

### Community 8 - "list_my_submissions"
Cohesion: 0.22
Nodes (4): get_submission_detail(), list_my_submissions(), list_submissions(), update_submission_grade()

### Community 11 - "build_group_journal"
Cohesion: 0.07
Nodes (13): CriterionErrorStat, GroupJournalRow, GroupJournalStudentCell, _auto_adjust_worksheet_columns(), build_group_journal(), calculate_criterion_error_stats(), _configure_pdf_font(), PracticalColumnInfo (+5 more)

### Community 13 - "InvalidFileFormatError"
Cohesion: 0.08
Nodes (17): check_submission_plagiarism(), _coerce_metadata(), compute_bytes_sha256(), compute_code_sha256(), compute_file_sha256(), compute_submission_hash(), evaluate_plagiarism(), extract_core_xml_metadata() (+9 more)

### Community 14 - "submit_practical_work"
Cohesion: 0.15
Nodes (4): _extract_submission_payload(), ExtractedSubmissionPayload, submit_practical_work(), update_practical_grading_rules()

### Community 16 - "seed_database"
Cohesion: 0.21
Nodes (5): main(), run_seed(), seed_database(), SeedSummary, summarize_bundle()

### Community 17 - "schemas/__init__.py"
Cohesion: 0.10
Nodes (21): _build_module_detail_read(), CourseCreate, CourseRead, CourseUpdate, ModuleCreate, ModuleDetailRead, ModuleSummaryRead, ModuleUpdate (+13 more)

### Community 23 - "package.json"
Cohesion: 0.07
Nodes (41): @monaco-editor/react@4.6.0, devDependencies, autoprefixer@^10.4.20, eslint@^9.15.0, @eslint/js@^9.15.0, eslint-plugin-react-hooks@^5.0.0, eslint-plugin-react-refresh@^0.4.14, globals@^15.12.0 (+33 more)

### Community 24 - "App.tsx"
Cohesion: 0.10
Nodes (35): dependencies, axios@^1.7.7, react@^18.3.1, react-dom@^18.3.1, react-router-dom@^6.28.0, App(), ProtectedAppLayout(), RoleHomeRedirect() (+27 more)

### Community 25 - "DomainError"
Cohesion: 0.12
Nodes (17): role_checker(), create_admin_group(), create_admin_user(), delete_admin_group(), delete_admin_user(), _ensure_email_unique(), _ensure_group_code_unique(), _get_group_or_404() (+9 more)

### Community 26 - "AdminUsersPage.tsx"
Cohesion: 0.07
Nodes (44): AdminTab, AdminUsersPage(), buildCredentialsReportText(), CourseYearFilter, DeleteTarget, downloadCredentialsReportTxt(), FeedbackBanner, fetchAdminGroups() (+36 more)

### Community 27 - "course.ts"
Cohesion: 0.08
Nodes (45): PracticalModuleContext, CourseEditorPage(), DISCIPLINE_META, DisciplineMeta, EditorTab, fetchCourses(), fetchModuleDetail(), fetchModuleQuizQuestions() (+37 more)

### Community 28 - "build_accdb_bytes"
Cohesion: 0.31
Nodes (4): build_accdb_bytes(), _encode_data_page(), _encode_msys_catalog_record(), _encode_tdef_page()

### Community 29 - "AuthContext.tsx"
Cohesion: 0.23
Nodes (15): apiClient, clearAuthTokens(), getAccessToken(), getRefreshToken(), setAccessToken(), setRefreshToken(), AuthContext, AuthContextValue (+7 more)

### Community 30 - "XlsxGrader"
Cohesion: 0.05
Nodes (5): _is_doctype_target(), _try_parse_numeric(), XlsxGrader, CriterionResult, GradingRule

### Community 32 - "AccdbGrader"
Cohesion: 0.08
Nodes (7): AccdbColumnSchema, AccdbDatabaseSchema, AccdbTableSchema, _is_numeric_condition(), _is_system_table_name(), _resolve_canonical_type(), _strip_identifiers()

### Community 33 - "QuizService"
Cohesion: 0.13
Nodes (3): QuizNotPassedError, QuizService, resolve_student_variant()

### Community 37 - "submission_service.py"
Cohesion: 0.09
Nodes (10): require_role(), PlagiarismDetectedError, UserRole, GradingRulesUpdateRequest, GroupJournalRead, HtmlSubmissionRequest, ManualGradeUpdateRequest, SubmissionRead (+2 more)

### Community 38 - "conftest.py"
Cohesion: 0.09
Nodes (6): async_client(), build_sample_docx(), db_session(), _fast_seed_hash_password(), _replace_zip_member(), rewrite_openxml_core_metadata()

### Community 40 - "GradebookPage.tsx"
Cohesion: 0.13
Nodes (21): @tanstack/react-query@^5.60.0, extractApiErrorMessage(), COURSE_VISUAL_META, CoursesPage(), CourseVisualMeta, fetchCourses(), FilterOption, ModuleRowCard() (+13 more)

### Community 42 - "test_submissions_api.py"
Cohesion: 0.18
Nodes (9): make_auth_headers(), _get_course_module_and_practical(), _get_user_by_email(), _grant_quiz_pass(), test_antiplagiarism_flags_sha256_and_core_xml_matches_across_students(), test_health_check_and_jwt_login_flow(), test_submission_blocked_without_passed_quiz_and_unlocked_after_70_percent(), test_submit_all_four_practical_formats_via_api() (+1 more)

### Community 44 - "ModuleViewPage.tsx"
Cohesion: 0.11
Nodes (25): buildStarterHtmlTemplate(), EditorColorTheme, HtmlSandbox(), HtmlSandboxProps, QUICK_HTML_SNIPPETS, QuickSnippet, SandboxViewMode, BinaryPracticalFormat (+17 more)

### Community 46 - "export_service.py"
Cohesion: 0.11
Nodes (18): Base, Course, CourseSlug, _enum_values(), Module, Practical, QuizQuestion, QuizAttempt (+10 more)

### Community 49 - "html_grader.py"
Cohesion: 0.10
Nodes (7): _attribute_value_matches(), _find_tag_attr_key(), _get_tag_attribute_str(), _normalize_selector(), _parse_text_match_expected(), _strip_quotes(), _tag_has_attribute()

### Community 50 - "ExportService"
Cohesion: 0.07
Nodes (10): export_group_journal(), get_group_journal(), list_academic_groups(), _parse_export_format(), ExportFormat, build_content_disposition(), ExportedDocument, ExportService (+2 more)

### Community 51 - "student_import_service.py"
Cohesion: 0.06
Nodes (25): ImportedStudentItem, ImportSkippedItem, StudentImportResponse, calculate_variant_index(), build_generated_email(), _classify_header_cell(), _clean_whitespace(), _detect_docx_header_columns() (+17 more)

### Community 52 - "get_db"
Cohesion: 0.08
Nodes (21): create_course(), create_module(), create_quiz_question(), delete_quiz_question(), _fetch_user_progress_maps(), get_course(), get_module(), get_practical_for_student() (+13 more)

### Community 63 - "env.py"
Cohesion: 0.07
Nodes (7): do_run_migrations(), run_async_migrations(), run_migrations_offline(), run_migrations_online(), get_settings(), Settings, create_application()

## Knowledge Gaps
- **1 isolated node(s):** `edu-auto-grader-backend`
  These have ≤1 connection - possible missing edges. (Counts symbols only; 639 node(s) total have ≤1 connection when file, concept and rationale nodes are included.)
- **41 thin communities (<3 nodes) omitted from report** — run `graphify query` to explore isolated nodes.

## Suggested Questions
_Questions this graph is uniquely positioned to answer:_

- **Why does `GradingRule` connect `XlsxGrader` to `AccdbGrader`, `InvalidFileFormatError`, `submission_service.py`, `InvalidFileFormatError`, `schemas/__init__.py`, `html_grader.py`, `InvalidFileFormatError`, `DocxGrader`?**
  _High betweenness centrality (0.056) - this node is a cross-community bridge._
- **Are the 10 inferred relationships involving `GradingRule` (e.g. with `AccdbGrader` and `BaseGrader`) actually correct?**
  _`GradingRule` has 10 INFERRED edges - model-reasoned connections that need verification._
- **What connects `edu-auto-grader-backend` to the rest of the system?**
  _1 weakly-connected nodes found - possible missing edges._
- **Should `v1/auth.py` be split into smaller, more focused modules?**
  _Cohesion score 0.06818181818181818 - nodes in this community are weakly interconnected._
- **Why does `DomainError` connect `DomainError` to `v1/auth.py`, `QuizService`, `InvalidFileFormatError`, `submission_service.py`, `get_current_user`, `.__init__`, `submit_practical_work`, `export_service.py`, `schemas/__init__.py`, `ExportService`, `student_import_service.py`, `get_db`, `env.py`?**
  _High betweenness centrality (0.049) - this node is a cross-community bridge._
- **Are the 7 inferred relationships involving `DomainError` (e.g. with `login()` and `refresh_tokens()`) actually correct?**
  _`DomainError` has 7 INFERRED edges - model-reasoned connections that need verification._
- **Should `postgres` be split into smaller, more focused modules?**
  _Cohesion score 0.09523809523809523 - nodes in this community are weakly interconnected._