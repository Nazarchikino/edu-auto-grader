# Graph Report - edu-auto-grader  (2026-11-19)

## Corpus Check
- 76 files · ~73,196 words
- Verdict: corpus is large enough that graph structure adds value.
- Unclassified: 7 file(s) not represented in the graph (top: (none) 4, .ini 1, .mako 1)

## Summary
- 1302 nodes · 3591 edges · 63 communities (42 shown, 21 thin omitted)
- Extraction: 90% EXTRACTED · 10% INFERRED · 0% AMBIGUOUS · INFERRED: 345 edges (avg confidence: 0.93)
- Token cost: 0 input · 0 output

## Graph Freshness
- Built from commit: `d91dcb45`
- Run `git rev-parse HEAD` and compare to check if the graph is stale.
- Run `graphify update .` after code changes (no API cost).

## Community Hubs (Navigation)
- schemas/__init__.py
- postgres
- compilerOptions
- GradingRule
- seed.py
- conftest.py
- submission_service.py
- api.ts
- InvalidFileFormatError
- vite-env.d.ts
- export_service.py
- InvalidFileFormatError
- QuizService
- models/course.py
- UserRole
- get_db
- edu-auto-grader-backend
- HtmlGrader
- package.json
- App.tsx
- admin.py
- AdminUsersPage.tsx
- course.ts
- build_accdb_bytes
- AuthContext.tsx
- XlsxGrader
- DocxGrader
- AccdbGrader
- build_sample_docx
- submission.py
- db_session
- list_my_submissions
- SubmissionService
- export_group_journal
- xlsx_grader.py
- GradebookPage.tsx
- DomainError
- test_submissions_api.py
- submit_practical_work
- ModuleViewPage.tsx
- dependencies
- .execute
- SqliteAsyncSessionAdapter
- services/__init__.py
- _find_tag_attr_key
- ExportService
- render_group_journal_xlsx
- get_current_user
- 0001_initial_schema.py
- calculate_criterion_error_stats
- _attribute_value_matches
- _is_doctype_target
- _normalize_text
- env.py

## God Nodes (most connected - your core abstractions)
1. `GradingRule` - 64 edges
2. `DomainError` - 55 edges
3. `User` - 51 edges
4. `DocxGrader` - 45 edges
5. `InvalidFileFormatError` - 45 edges
6. `PracticalFormat` - 43 edges
7. `GradingError` - 40 edges
8. `SubmissionService` - 39 edges
9. `get_db()` - 39 edges
10. `XlsxGrader` - 36 edges

## Surprising Connections (you probably didn't know these)
- `create_admin_group()` --uses--> `AcademicGroupCreate`  [INFERRED]
  backend/app/api/v1/admin.py → backend/app/schemas/auth.py
- `update_admin_group()` --uses--> `AcademicGroupUpdate`  [INFERRED]
  backend/app/api/v1/admin.py → backend/app/schemas/auth.py
- `create_admin_user()` --uses--> `UserCreate`  [INFERRED]
  backend/app/api/v1/admin.py → backend/app/schemas/auth.py
- `update_admin_user()` --uses--> `UserUpdate`  [INFERRED]
  backend/app/api/v1/admin.py → backend/app/schemas/auth.py
- `login()` --uses--> `LoginRequest`  [INFERRED]
  backend/app/api/v1/auth.py → backend/app/schemas/auth.py

## Import Cycles
- None detected.

## Communities (63 total, 21 thin omitted)

### Community 0 - "schemas/__init__.py"
Cohesion: 0.12
Nodes (10): AcademicGroupBase, AcademicGroupCreate, AcademicGroupUpdate, ErrorResponse, LoginRequest, RefreshTokenRequest, TokenPayload, UserBase (+2 more)

### Community 1 - "postgres"
Cohesion: 0.10
Nodes (20): POSTGRES_DB, POSTGRES_PASSWORD, POSTGRES_USER, interval, retries, test, timeout, container_name (+12 more)

### Community 2 - "compilerOptions"
Cohesion: 0.10
Nodes (20): compilerOptions, allowImportingTsExtensions, isolatedModules, jsx, lib, module, moduleDetection, moduleResolution (+12 more)

### Community 3 - "GradingRule"
Cohesion: 0.09
Nodes (5): GradingRuleType, test_docx_grader_detects_formatting_violations_and_corrupt_files(), test_docx_grader_evaluates_valid_document(), test_xlsx_grader_evaluates_formulas_values_and_charts(), test_xlsx_grader_rejects_static_value_instead_of_formula_and_missing_chart()

### Community 4 - "seed.py"
Cohesion: 0.21
Nodes (5): main(), run_seed(), seed_database(), SeedSummary, summarize_bundle()

### Community 6 - "submission_service.py"
Cohesion: 0.11
Nodes (20): _serialize_practical_teacher(), CourseCreate, CourseRead, CourseUpdate, ModuleCreate, ModuleDetailRead, ModuleSummaryRead, ModuleUpdate (+12 more)

### Community 7 - "api.ts"
Cohesion: 0.08
Nodes (38): COURSE_SLUG_LABELS, CriterionBreakdownItem(), CriterionFilterMode, extractFileNameFromPath(), FORMAT_META, formatDateTime(), GradingReportCard(), GradingReportCardProps (+30 more)

### Community 8 - "InvalidFileFormatError"
Cohesion: 0.08
Nodes (9): GradingError, InvalidFileFormatError, _is_numeric_condition(), _parse_ddl_column_type(), BaseGrader, GraderFactory, PracticalFormat, GradingReport (+1 more)

### Community 11 - "export_service.py"
Cohesion: 0.17
Nodes (5): _configure_pdf_font(), _prepare_pdf_text(), render_group_journal_pdf(), _sanitize_filename_token(), _transliterate_to_ascii()

### Community 13 - "InvalidFileFormatError"
Cohesion: 0.08
Nodes (17): check_submission_plagiarism(), _coerce_metadata(), compute_bytes_sha256(), compute_code_sha256(), compute_file_sha256(), compute_submission_hash(), evaluate_plagiarism(), extract_core_xml_metadata() (+9 more)

### Community 14 - "QuizService"
Cohesion: 0.13
Nodes (3): _build_module_detail_read(), QuizNotPassedError, QuizService

### Community 15 - "models/course.py"
Cohesion: 0.11
Nodes (21): Base, Course, CourseSlug, _enum_values(), Module, Practical, QuizQuestion, QuizAttempt (+13 more)

### Community 16 - "UserRole"
Cohesion: 0.11
Nodes (11): login(), read_current_user(), refresh_tokens(), create_access_token(), create_refresh_token(), create_token_pair(), decode_token(), _encode_jwt_token() (+3 more)

### Community 17 - "get_db"
Cohesion: 0.11
Nodes (20): create_course(), create_module(), create_quiz_question(), delete_quiz_question(), _fetch_user_progress_maps(), get_course(), get_module(), get_practical_for_student() (+12 more)

### Community 22 - "HtmlGrader"
Cohesion: 0.11
Nodes (6): HtmlGrader, _normalize_selector(), _parse_text_match_expected(), _strip_quotes(), test_html_grader_detects_missing_tags_and_rejects_empty_code(), test_html_grader_evaluates_semantic_dom_structure_and_attributes()

### Community 23 - "package.json"
Cohesion: 0.07
Nodes (39): devDependencies, autoprefixer@^10.4.20, eslint@^9.15.0, @eslint/js@^9.15.0, eslint-plugin-react-hooks@^5.0.0, eslint-plugin-react-refresh@^0.4.14, globals@^15.12.0, postcss@^8.4.49 (+31 more)

### Community 24 - "App.tsx"
Cohesion: 0.11
Nodes (32): react-router-dom@^6.28.0, App(), ProtectedAppLayout(), RoleHomeRedirect(), PlagiarismBadgeProps, Navbar(), NavbarProps, resolvePageTitle() (+24 more)

### Community 25 - "admin.py"
Cohesion: 0.10
Nodes (17): create_admin_group(), create_admin_user(), delete_admin_group(), delete_admin_user(), _ensure_email_unique(), _ensure_group_code_unique(), _get_group_or_404(), _get_user_with_group_or_404() (+9 more)

### Community 26 - "AdminUsersPage.tsx"
Cohesion: 0.11
Nodes (21): AdminTab, AdminUsersPage(), COURSE_YEARS, CourseYearFilter, DeleteTarget, FeedbackBanner, fetchAdminGroups(), fetchAdminUsers() (+13 more)

### Community 27 - "course.ts"
Cohesion: 0.09
Nodes (41): CourseEditorPage(), DISCIPLINE_META, DisciplineMeta, EditorTab, fetchCourses(), fetchModuleDetail(), fetchModuleQuizQuestions(), fetchPracticalTeacher() (+33 more)

### Community 28 - "build_accdb_bytes"
Cohesion: 0.24
Nodes (5): build_accdb_bytes(), _encode_data_page(), _encode_msys_catalog_record(), _encode_tdef_page(), build_sample_accdb()

### Community 29 - "AuthContext.tsx"
Cohesion: 0.16
Nodes (19): axios@^1.7.7, apiClient, clearAuthTokens(), getAccessToken(), getRefreshToken(), setAccessToken(), setRefreshToken(), AuthContext (+11 more)

### Community 30 - "XlsxGrader"
Cohesion: 0.07
Nodes (3): XlsxGrader, CriterionResult, GradingRule

### Community 32 - "AccdbGrader"
Cohesion: 0.07
Nodes (9): AccdbColumnSchema, AccdbDatabaseSchema, AccdbGrader, AccdbTableSchema, _is_system_table_name(), _resolve_canonical_type(), _strip_identifiers(), test_accdb_grader_detects_missing_schema_elements_and_invalid_header() (+1 more)

### Community 33 - "build_sample_docx"
Cohesion: 0.27
Nodes (4): build_sample_docx(), build_sample_xlsx(), _replace_zip_member(), rewrite_openxml_core_metadata()

### Community 34 - "submission.py"
Cohesion: 0.17
Nodes (7): CriterionErrorStat, GroupJournalRead, GroupJournalRow, GroupJournalStudentCell, HtmlSubmissionRequest, ManualGradeUpdateRequest, build_group_journal()

### Community 35 - "db_session"
Cohesion: 0.13
Nodes (5): async_client(), _create_sqlite_test_engine(), _set_sqlite_pragma(), db_session(), _fast_seed_hash_password()

### Community 36 - "list_my_submissions"
Cohesion: 0.22
Nodes (4): get_submission_detail(), list_my_submissions(), list_submissions(), update_submission_grade()

### Community 37 - "SubmissionService"
Cohesion: 0.14
Nodes (5): PlagiarismDetectedError, GradingRulesUpdateRequest, SubmissionRead, serialize_practical_teacher(), SubmissionService

### Community 38 - "export_group_journal"
Cohesion: 0.19
Nodes (3): export_group_journal(), get_group_journal(), list_academic_groups()

### Community 39 - "xlsx_grader.py"
Cohesion: 0.16
Nodes (4): _canonicalize_formula(), _format_cell_value(), _is_wrapped_in_parens(), _try_parse_numeric()

### Community 40 - "GradebookPage.tsx"
Cohesion: 0.13
Nodes (21): @tanstack/react-query@^5.60.0, extractApiErrorMessage(), COURSE_VISUAL_META, CoursesPage(), CourseVisualMeta, fetchCourses(), FilterOption, ModuleRowCard() (+13 more)

### Community 41 - "DomainError"
Cohesion: 0.13
Nodes (8): require_role(), role_checker(), _parse_export_format(), ExtractedSubmissionPayload, DomainError, create_application(), _enum_values(), UserRole

### Community 42 - "test_submissions_api.py"
Cohesion: 0.18
Nodes (9): make_auth_headers(), _get_course_module_and_practical(), _get_user_by_email(), _grant_quiz_pass(), test_antiplagiarism_flags_sha256_and_core_xml_matches_across_students(), test_health_check_and_jwt_login_flow(), test_submission_blocked_without_passed_quiz_and_unlocked_after_70_percent(), test_submit_all_four_practical_formats_via_api() (+1 more)

### Community 43 - "submit_practical_work"
Cohesion: 0.18
Nodes (3): _extract_submission_payload(), submit_practical_work(), update_practical_grading_rules()

### Community 44 - "ModuleViewPage.tsx"
Cohesion: 0.10
Nodes (25): buildStarterHtmlTemplate(), EditorColorTheme, HtmlSandbox(), HtmlSandboxProps, QUICK_HTML_SNIPPETS, QuickSnippet, SandboxViewMode, BinaryPracticalFormat (+17 more)

### Community 45 - "dependencies"
Cohesion: 0.29
Nodes (7): dependencies, lucide-react@^0.460.0, @monaco-editor/react@4.6.0, react@^18.3.1, react-dom@^18.3.1, @monaco-editor/react, react-dom

### Community 46 - ".execute"
Cohesion: 0.21
Nodes (4): _get_user_by_email(), test_admin_academic_groups_crud_and_detachment(), test_admin_endpoints_enforce_admin_rbac(), test_admin_users_crud_filters_and_safety_guards()

### Community 48 - "services/__init__.py"
Cohesion: 0.20
Nodes (4): ExportFormat, build_content_disposition(), ExportedDocument, GroupJournalBundle

### Community 49 - "_find_tag_attr_key"
Cohesion: 0.38
Nodes (3): _find_tag_attr_key(), _get_tag_attribute_str(), _tag_has_attribute()

### Community 51 - "render_group_journal_xlsx"
Cohesion: 0.29
Nodes (3): _auto_adjust_worksheet_columns(), PracticalColumnInfo, render_group_journal_xlsx()

### Community 63 - "env.py"
Cohesion: 0.10
Nodes (6): do_run_migrations(), run_async_migrations(), run_migrations_offline(), run_migrations_online(), get_settings(), Settings

## Knowledge Gaps
- **1 isolated node(s):** `edu-auto-grader-backend`
  These have ≤1 connection - possible missing edges. (Counts symbols only; 572 node(s) total have ≤1 connection when file, concept and rationale nodes are included.)
- **21 thin communities (<3 nodes) omitted from report** — run `graphify query` to explore isolated nodes.

## Suggested Questions
_Questions this graph is uniquely positioned to answer:_

- **Why does `GradingRule` connect `XlsxGrader` to `AccdbGrader`, `GradingRule`, `SubmissionService`, `submission_service.py`, `xlsx_grader.py`, `InvalidFileFormatError`, `InvalidFileFormatError`, `models/course.py`, `HtmlGrader`, `DocxGrader`?**
  _High betweenness centrality (0.071) - this node is a cross-community bridge._
- **Are the 11 inferred relationships involving `GradingRule` (e.g. with `_serialize_practical_teacher()` and `AccdbGrader`) actually correct?**
  _`GradingRule` has 11 INFERRED edges - model-reasoned connections that need verification._
- **What connects `edu-auto-grader-backend` to the rest of the system?**
  _1 weakly-connected nodes found - possible missing edges._
- **Should `schemas/__init__.py` be split into smaller, more focused modules?**
  _Cohesion score 0.11594202898550725 - nodes in this community are weakly interconnected._
- **Why does `DocxGrader` connect `DocxGrader` to `GradingRule`, `InvalidFileFormatError`, `InvalidFileFormatError`, `._parse_expected_font`, `._parse_expected_margins`, `XlsxGrader`?**
  _High betweenness centrality (0.063) - this node is a cross-community bridge._
- **Are the 12 inferred relationships involving `DomainError` (e.g. with `login()` and `refresh_tokens()`) actually correct?**
  _`DomainError` has 12 INFERRED edges - model-reasoned connections that need verification._
- **Should `postgres` be split into smaller, more focused modules?**
  _Cohesion score 0.09523809523809523 - nodes in this community are weakly interconnected._