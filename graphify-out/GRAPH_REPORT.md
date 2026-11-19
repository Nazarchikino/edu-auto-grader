# Graph Report - edu-auto-grader  (2026-11-19)

## Corpus Check
- 77 files · ~76,721 words
- Verdict: corpus is large enough that graph structure adds value.
- Unclassified: 7 file(s) not represented in the graph (top: (none) 4, .ini 1, .mako 1)

## Summary
- 1337 nodes · 3647 edges · 69 communities (43 shown, 26 thin omitted)
- Extraction: 91% EXTRACTED · 9% INFERRED · 0% AMBIGUOUS · INFERRED: 336 edges (avg confidence: 0.93)
- Token cost: 0 input · 0 output

## Graph Freshness
- Built from commit: `8834b701`
- Run `git rev-parse HEAD` and compare to check if the graph is stale.
- Run `graphify update .` after code changes (no API cost).

## Community Hubs (Navigation)
- schemas/__init__.py
- postgres
- compilerOptions
- test_graders.py
- test_admin_api.py
- _compile_jsonb_for_sqlite
- GroupJournalPage.tsx
- GradebookPage.tsx
- PracticalFormat
- vite-env.d.ts
- export_service.py
- InvalidFileFormatError
- config.py
- seed_database
- UserRole
- schemas/__init__.py
- edu-auto-grader-backend
- InvalidFileFormatError
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
- QuizService
- submission.py
- conftest.py
- list_my_submissions
- SubmissionService
- db_session
- export_group_journal
- CoursesPage.tsx
- v1/auth.py
- test_submissions_api.py
- submit_practical_work
- ModuleViewPage.tsx
- react
- User
- SqliteAsyncSessionAdapter
- ExportFormat
- html_grader.py
- ExportService
- submission_service.py
- courses.py
- 0001_initial_schema.py
- DomainError
- AcademicGroupRead
- 0002_restrict_course_year_to_4.py
- env.py

## God Nodes (most connected - your core abstractions)
1. `GradingRule` - 63 edges
2. `User` - 55 edges
3. `DomainError` - 55 edges
4. `DocxGrader` - 45 edges
5. `InvalidFileFormatError` - 45 edges
6. `PracticalFormat` - 43 edges
7. `GradingError` - 40 edges
8. `SubmissionService` - 39 edges
9. `get_db()` - 39 edges
10. `XlsxGrader` - 36 edges

## Surprising Connections (you probably didn't know these)
- `_serialize_course()` --uses--> `Course`  [INFERRED]
  backend/app/api/v1/courses.py → backend/app/models/course.py
- `_load_course_or_404()` --uses--> `Course`  [INFERRED]
  backend/app/api/v1/courses.py → backend/app/models/course.py
- `_load_course_or_404()` --uses--> `Module`  [INFERRED]
  backend/app/api/v1/courses.py → backend/app/models/course.py
- `_load_module_or_404()` --uses--> `Module`  [INFERRED]
  backend/app/api/v1/courses.py → backend/app/models/course.py
- `_build_module_detail_read()` --uses--> `Module`  [INFERRED]
  backend/app/api/v1/courses.py → backend/app/models/course.py

## Import Cycles
- None detected.

## Communities (69 total, 26 thin omitted)

### Community 0 - "schemas/__init__.py"
Cohesion: 0.15
Nodes (8): AcademicGroupBase, AcademicGroupCreate, ErrorResponse, LoginRequest, RefreshTokenRequest, UserBase, UserCreate, UserUpdate

### Community 1 - "postgres"
Cohesion: 0.10
Nodes (20): POSTGRES_DB, POSTGRES_PASSWORD, POSTGRES_USER, interval, retries, test, timeout, container_name (+12 more)

### Community 2 - "compilerOptions"
Cohesion: 0.10
Nodes (20): compilerOptions, allowImportingTsExtensions, isolatedModules, jsx, lib, module, moduleDetection, moduleResolution (+12 more)

### Community 3 - "test_graders.py"
Cohesion: 0.11
Nodes (4): _format_number(), GradingRuleType, test_xlsx_grader_evaluates_formulas_values_and_charts(), test_xlsx_grader_rejects_static_value_instead_of_formula_and_missing_chart()

### Community 4 - "test_admin_api.py"
Cohesion: 0.17
Nodes (5): _get_user_by_email(), test_admin_academic_groups_crud_and_detachment(), test_admin_endpoints_enforce_admin_rbac(), test_admin_users_crud_filters_and_safety_guards(), test_courses_restricted_strictly_to_4_disciplines()

### Community 6 - "GroupJournalPage.tsx"
Cohesion: 0.26
Nodes (11): PlagiarismBadge(), PlagiarismBadgeProps, COURSE_SLUG_BADGES, fetchAcademicGroups(), fetchCourses(), fetchGroupJournal(), fetchSubmissionDetail(), formatShortDate() (+3 more)

### Community 7 - "GradebookPage.tsx"
Cohesion: 0.11
Nodes (24): COURSE_SLUG_LABELS, CriterionBreakdownItem(), CriterionFilterMode, extractFileNameFromPath(), FORMAT_META, formatDateTime(), GradingReportCard(), GradingReportCardProps (+16 more)

### Community 8 - "PracticalFormat"
Cohesion: 0.10
Nodes (6): GradingError, BaseGrader, GraderFactory, _enum_values(), PracticalFormat, test_grader_factory_resolves_all_four_formats()

### Community 11 - "export_service.py"
Cohesion: 0.11
Nodes (9): _auto_adjust_worksheet_columns(), build_content_disposition(), _configure_pdf_font(), PracticalColumnInfo, _prepare_pdf_text(), render_group_journal_pdf(), render_group_journal_xlsx(), _sanitize_filename_token() (+1 more)

### Community 13 - "InvalidFileFormatError"
Cohesion: 0.08
Nodes (17): check_submission_plagiarism(), _coerce_metadata(), compute_bytes_sha256(), compute_code_sha256(), compute_file_sha256(), compute_submission_hash(), evaluate_plagiarism(), extract_core_xml_metadata() (+9 more)

### Community 15 - "seed_database"
Cohesion: 0.21
Nodes (5): main(), run_seed(), seed_database(), SeedSummary, summarize_bundle()

### Community 16 - "UserRole"
Cohesion: 0.16
Nodes (9): create_access_token(), create_refresh_token(), create_token_pair(), decode_token(), _encode_jwt_token(), _enum_values(), UserRole, TokenPayload (+1 more)

### Community 17 - "schemas/__init__.py"
Cohesion: 0.09
Nodes (16): CourseCreate, CourseRead, CourseUpdate, ModuleCreate, ModuleDetailRead, ModuleSummaryRead, ModuleUpdate, PracticalCreate (+8 more)

### Community 22 - "InvalidFileFormatError"
Cohesion: 0.09
Nodes (4): InvalidFileFormatError, HtmlGrader, test_html_grader_detects_missing_tags_and_rejects_empty_code(), test_html_grader_evaluates_semantic_dom_structure_and_attributes()

### Community 23 - "package.json"
Cohesion: 0.07
Nodes (39): devDependencies, autoprefixer@^10.4.20, eslint@^9.15.0, @eslint/js@^9.15.0, eslint-plugin-react-hooks@^5.0.0, eslint-plugin-react-refresh@^0.4.14, globals@^15.12.0, postcss@^8.4.49 (+31 more)

### Community 24 - "App.tsx"
Cohesion: 0.13
Nodes (27): react-router-dom@^6.28.0, App(), ProtectedAppLayout(), RoleHomeRedirect(), Navbar(), NavbarProps, resolvePageTitle(), ROLE_BADGE_CONFIG (+19 more)

### Community 25 - "admin.py"
Cohesion: 0.10
Nodes (18): create_admin_group(), create_admin_user(), delete_admin_group(), delete_admin_user(), _ensure_email_unique(), _ensure_group_code_unique(), _get_group_or_404(), _get_user_with_group_or_404() (+10 more)

### Community 26 - "AdminUsersPage.tsx"
Cohesion: 0.07
Nodes (37): AdminTab, AdminUsersPage(), CourseYearFilter, DeleteTarget, FeedbackBanner, fetchAdminGroups(), fetchAdminUsers(), formatRegistrationDate() (+29 more)

### Community 27 - "course.ts"
Cohesion: 0.08
Nodes (45): CourseEditorPage(), DISCIPLINE_META, DisciplineMeta, EditorTab, fetchCourses(), fetchModuleDetail(), fetchModuleQuizQuestions(), fetchPracticalTeacher() (+37 more)

### Community 28 - "build_accdb_bytes"
Cohesion: 0.31
Nodes (4): build_accdb_bytes(), _encode_data_page(), _encode_msys_catalog_record(), _encode_tdef_page()

### Community 29 - "AuthContext.tsx"
Cohesion: 0.23
Nodes (15): apiClient, clearAuthTokens(), getAccessToken(), getRefreshToken(), setAccessToken(), setRefreshToken(), AuthContext, AuthContextValue (+7 more)

### Community 30 - "XlsxGrader"
Cohesion: 0.07
Nodes (5): _canonicalize_formula(), _format_cell_value(), _is_wrapped_in_parens(), _try_parse_numeric(), XlsxGrader

### Community 31 - "DocxGrader"
Cohesion: 0.05
Nodes (5): DocxGrader, CriterionResult, GradingRule, test_docx_grader_detects_formatting_violations_and_corrupt_files(), test_docx_grader_evaluates_valid_document()

### Community 32 - "AccdbGrader"
Cohesion: 0.06
Nodes (11): AccdbColumnSchema, AccdbDatabaseSchema, AccdbGrader, AccdbTableSchema, _is_numeric_condition(), _is_system_table_name(), _parse_ddl_column_type(), _resolve_canonical_type() (+3 more)

### Community 34 - "submission.py"
Cohesion: 0.15
Nodes (8): CriterionErrorStat, GroupJournalRead, GroupJournalRow, GroupJournalStudentCell, HtmlSubmissionRequest, build_group_journal(), calculate_criterion_error_stats(), _RuleStatAccumulator

### Community 35 - "conftest.py"
Cohesion: 0.10
Nodes (5): build_sample_accdb(), build_sample_docx(), build_sample_xlsx(), _replace_zip_member(), rewrite_openxml_core_metadata()

### Community 36 - "list_my_submissions"
Cohesion: 0.18
Nodes (5): get_submission_detail(), list_my_submissions(), list_submissions(), update_submission_grade(), SubmissionRead

### Community 37 - "SubmissionService"
Cohesion: 0.14
Nodes (4): Submission, ManualGradeUpdateRequest, serialize_submission(), SubmissionService

### Community 38 - "db_session"
Cohesion: 0.13
Nodes (5): async_client(), _create_sqlite_test_engine(), _set_sqlite_pragma(), db_session(), _fast_seed_hash_password()

### Community 39 - "export_group_journal"
Cohesion: 0.23
Nodes (3): export_group_journal(), get_group_journal(), list_academic_groups()

### Community 40 - "CoursesPage.tsx"
Cohesion: 0.31
Nodes (8): extractApiErrorMessage(), COURSE_VISUAL_META, CoursesPage(), CourseVisualMeta, fetchCourses(), FilterOption, ModuleRowCard(), PRACTICAL_FORMAT_LABELS

### Community 41 - "v1/auth.py"
Cohesion: 0.10
Nodes (6): login(), read_current_user(), refresh_tokens(), verify_password(), create_application(), hash_password()

### Community 42 - "test_submissions_api.py"
Cohesion: 0.16
Nodes (11): CourseSlug, QuizAttempt, make_auth_headers(), _get_course_module_and_practical(), _get_user_by_email(), _grant_quiz_pass(), test_antiplagiarism_flags_sha256_and_core_xml_matches_across_students(), test_health_check_and_jwt_login_flow() (+3 more)

### Community 43 - "submit_practical_work"
Cohesion: 0.13
Nodes (5): _extract_submission_payload(), ExtractedSubmissionPayload, submit_practical_work(), update_practical_grading_rules(), GradingRulesUpdateRequest

### Community 44 - "ModuleViewPage.tsx"
Cohesion: 0.10
Nodes (26): buildStarterHtmlTemplate(), EditorColorTheme, HtmlSandbox(), HtmlSandboxProps, QUICK_HTML_SNIPPETS, QuickSnippet, SandboxViewMode, BinaryPracticalFormat (+18 more)

### Community 45 - "react"
Cohesion: 0.15
Nodes (13): dependencies, axios@^1.7.7, lucide-react@^0.460.0, @monaco-editor/react@4.6.0, react@^18.3.1, react-dom@^18.3.1, @tanstack/react-query@^5.60.0, queryClient (+5 more)

### Community 46 - "User"
Cohesion: 0.14
Nodes (13): require_role(), Base, Course, Module, QuizQuestion, AcademicGroup, User, _build_access_course() (+5 more)

### Community 48 - "ExportFormat"
Cohesion: 0.29
Nodes (3): _parse_export_format(), ExportFormat, ExportedDocument

### Community 49 - "html_grader.py"
Cohesion: 0.11
Nodes (9): _attribute_value_matches(), _find_tag_attr_key(), _get_tag_attribute_str(), _is_doctype_target(), _normalize_selector(), _normalize_text(), _parse_text_match_expected(), _strip_quotes() (+1 more)

### Community 51 - "submission_service.py"
Cohesion: 0.23
Nodes (6): Practical, PracticalTeacherRead, PracticalVariant, calculate_variant_index(), resolve_student_variant(), serialize_practical_teacher()

### Community 52 - "courses.py"
Cohesion: 0.07
Nodes (25): get_current_user(), _build_module_detail_read(), create_course(), create_module(), create_quiz_question(), delete_quiz_question(), _fetch_user_progress_maps(), get_course() (+17 more)

### Community 54 - "DomainError"
Cohesion: 0.25
Nodes (3): role_checker(), DomainError, PlagiarismDetectedError

### Community 63 - "env.py"
Cohesion: 0.13
Nodes (4): do_run_migrations(), run_async_migrations(), run_migrations_offline(), run_migrations_online()

## Knowledge Gaps
- **1 isolated node(s):** `edu-auto-grader-backend`
  These have ≤1 connection - possible missing edges. (Counts symbols only; 593 node(s) total have ≤1 connection when file, concept and rationale nodes are included.)
- **26 thin communities (<3 nodes) omitted from report** — run `graphify query` to explore isolated nodes.

## Suggested Questions
_Questions this graph is uniquely positioned to answer:_

- **Why does `GradingRule` connect `DocxGrader` to `AccdbGrader`, `test_graders.py`, `SubmissionService`, `PracticalFormat`, `InvalidFileFormatError`, `schemas/__init__.py`, `html_grader.py`, `submission_service.py`, `courses.py`, `InvalidFileFormatError`, `XlsxGrader`?**
  _High betweenness centrality (0.055) - this node is a cross-community bridge._
- **Are the 10 inferred relationships involving `GradingRule` (e.g. with `AccdbGrader` and `BaseGrader`) actually correct?**
  _`GradingRule` has 10 INFERRED edges - model-reasoned connections that need verification._
- **What connects `edu-auto-grader-backend` to the rest of the system?**
  _1 weakly-connected nodes found - possible missing edges._
- **Should `schemas/__init__.py` be split into smaller, more focused modules?**
  _Cohesion score 0.14619883040935672 - nodes in this community are weakly interconnected._
- **Why does `DocxGrader` connect `DocxGrader` to `test_graders.py`, `PracticalFormat`, `InvalidFileFormatError`, `schemas/__init__.py`, `InvalidFileFormatError`?**
  _High betweenness centrality (0.048) - this node is a cross-community bridge._
- **Are the 29 inferred relationships involving `User` (e.g. with `get_current_user()` and `require_role()`) actually correct?**
  _`User` has 29 INFERRED edges - model-reasoned connections that need verification._
- **Should `postgres` be split into smaller, more focused modules?**
  _Cohesion score 0.09523809523809523 - nodes in this community are weakly interconnected._