# Graph Report - edu-auto-grader  (2026-11-21)

## Corpus Check
- 87 files · ~245,362 words
- Verdict: corpus is large enough that graph structure adds value.
- Unclassified: 7 file(s) not represented in the graph (top: (none) 4, .ini 1, .mako 1)

## Summary
- 1527 nodes · 4327 edges · 70 communities (47 shown, 23 thin omitted)
- Extraction: 89% EXTRACTED · 11% INFERRED · 0% AMBIGUOUS · INFERRED: 456 edges (avg confidence: 0.93)
- Token cost: 0 input · 0 output

## Graph Freshness
- Built from commit: `c09a2fdc`
- Run `git rev-parse HEAD` and compare to check if the graph is stale.
- Run `graphify update .` after code changes (no API cost).

## Community Hubs (Navigation)
- UserRole
- postgres
- compilerOptions
- BaseGrader
- AccdbGrader
- accdb_grader.py
- InvalidFileFormatError
- GradebookPage.tsx
- MarkdownRenderer.tsx
- vite-env.d.ts
- .execute
- InvalidFileFormatError
- courses.py
- list_my_submissions
- test_submissions_api.py
- ExportService
- edu-auto-grader-backend
- schemas/auth.py
- package.json
- App.tsx
- DomainError
- AdminUsersPage.tsx
- course.ts
- _SeedQuizQuestionPayload
- AuthContext.tsx
- XlsxGrader
- 0002_restrict_course_year_to_4.py
- GroupJournalPage.tsx
- PlagiarismDetectedError
- HtmlSandbox.tsx
- parse_docx_students
- Settings
- SubmissionService
- SqliteAsyncSessionAdapter
- DocxGrader
- GradebookPage.tsx
- .evaluate
- export_group_journal
- ._parse_table_column_target
- ModuleViewPage.tsx
- DomainError
- seed.py
- submission_service.py
- main.py
- GradingRule
- db_session
- @tanstack/react-query
- get_db
- GradingError
- .evaluate
- _attribute_value_matches
- _is_doctype_target
- _normalize_text
- services/__init__.py
- build_sample_docx
- do_run_migrations
- get_current_user
- 0001_initial_schema.py
- _parse_text_match_expected
- _enum_values
- run_migrations_offline
- submit_practical_work
- practicals.py
- _compile_jsonb_for_sqlite

## God Nodes (most connected - your core abstractions)
1. `GradingRule` - 72 edges
2. `DomainError` - 60 edges
3. `User` - 60 edges
4. `InvalidFileFormatError` - 50 edges
5. `DocxGrader` - 46 edges
6. `PracticalFormat` - 42 edges
7. `UserRole` - 42 edges
8. `get_db()` - 41 edges
9. `SubmissionService` - 41 edges
10. `GradingError` - 40 edges

## Surprising Connections (you probably didn't know these)
- `get_current_user()` --uses--> `User`  [INFERRED]
  backend/app/api/deps.py → backend/app/models/user.py
- `_get_group_or_404()` --uses--> `AcademicGroup`  [INFERRED]
  backend/app/api/v1/admin.py → backend/app/models/user.py
- `_get_user_with_group_or_404()` --uses--> `User`  [INFERRED]
  backend/app/api/v1/admin.py → backend/app/models/user.py
- `_ensure_group_code_unique()` --uses--> `AcademicGroup`  [INFERRED]
  backend/app/api/v1/admin.py → backend/app/models/user.py
- `_ensure_email_unique()` --uses--> `User`  [INFERRED]
  backend/app/api/v1/admin.py → backend/app/models/user.py

## Import Cycles
- None detected.

## Communities (70 total, 23 thin omitted)

### Community 0 - "UserRole"
Cohesion: 0.18
Nodes (7): create_access_token(), create_refresh_token(), create_token_pair(), decode_token(), _encode_jwt_token(), verify_password(), hash_password()

### Community 1 - "postgres"
Cohesion: 0.10
Nodes (20): POSTGRES_DB, POSTGRES_PASSWORD, POSTGRES_USER, interval, retries, test, timeout, container_name (+12 more)

### Community 2 - "compilerOptions"
Cohesion: 0.10
Nodes (20): compilerOptions, allowImportingTsExtensions, isolatedModules, jsx, lib, module, moduleDetection, moduleResolution (+12 more)

### Community 3 - "BaseGrader"
Cohesion: 0.13
Nodes (3): BaseGrader, _format_cell_value(), GradingReport

### Community 4 - "AccdbGrader"
Cohesion: 0.13
Nodes (4): AccdbGrader, _is_system_table_name(), test_accdb_grader_accepts_hyperlink_type_as_memo(), test_accdb_grader_evaluates_tables_columns_and_types()

### Community 5 - "accdb_grader.py"
Cohesion: 0.14
Nodes (6): build_accdb_bytes(), _encode_data_page(), _encode_msys_catalog_record(), _encode_tdef_page(), _parse_ddl_column_type(), _resolve_canonical_type()

### Community 6 - "InvalidFileFormatError"
Cohesion: 0.10
Nodes (12): InvalidFileFormatError, GraderFactory, PracticalFormat, GradingRuleType, test_accdb_grader_detects_missing_schema_elements_and_invalid_header(), test_docx_grader_detects_formatting_violations_and_corrupt_files(), test_docx_grader_supports_uniform_single_number_margin(), test_grader_factory_resolves_all_four_formats() (+4 more)

### Community 7 - "GradebookPage.tsx"
Cohesion: 0.25
Nodes (10): COURSE_SLUG_LABELS, CriterionBreakdownItem(), CriterionFilterMode, extractFileNameFromPath(), FORMAT_META, formatDateTime(), GradingReportCard(), renderFormatIcon() (+2 more)

### Community 8 - "MarkdownRenderer.tsx"
Cohesion: 0.12
Nodes (31): dedentBlockLines(), findClosingDoubleStar(), findClosingParen(), findClosingSingleStar(), findMatchingBracket(), getAlignmentClass(), getLineIndent(), hasUnsafeControlChars() (+23 more)

### Community 11 - ".execute"
Cohesion: 0.12
Nodes (10): _build_college_import_docx(), _get_user_by_email(), test_admin_academic_groups_crud_and_detachment(), test_admin_bulk_import_docx_sorts_ukrainian_alphabet_and_assigns_variants(), test_admin_bulk_import_rbac_and_validation_errors(), test_admin_bulk_import_txt_formats_continuing_list_number_and_duplicates(), test_admin_endpoints_enforce_admin_rbac(), test_admin_users_crud_filters_and_safety_guards() (+2 more)

### Community 13 - "InvalidFileFormatError"
Cohesion: 0.08
Nodes (17): check_submission_plagiarism(), _coerce_metadata(), compute_bytes_sha256(), compute_code_sha256(), compute_file_sha256(), compute_submission_hash(), evaluate_plagiarism(), extract_core_xml_metadata() (+9 more)

### Community 14 - "courses.py"
Cohesion: 0.07
Nodes (21): _build_module_detail_read(), submit_module_quiz(), QuizNotPassedError, CourseCreate, CourseUpdate, ModuleCreate, ModuleDetailRead, ModuleSummaryRead (+13 more)

### Community 15 - "list_my_submissions"
Cohesion: 0.19
Nodes (5): download_submission_file(), get_submission_detail(), list_my_submissions(), list_submissions(), update_submission_grade()

### Community 16 - "test_submissions_api.py"
Cohesion: 0.16
Nodes (14): CourseSlug, make_auth_headers(), _get_course_module_and_practical(), _get_user_by_email(), _grant_quiz_pass(), test_antiplagiarism_flags_sha256_and_core_xml_matches_across_students(), test_download_submission_forbidden_for_other_teacher_and_students(), test_download_submissions_by_course_teacher_and_admin_with_headers_and_content() (+6 more)

### Community 17 - "ExportService"
Cohesion: 0.07
Nodes (15): ExportFormat, GroupJournalRead, _auto_adjust_worksheet_columns(), build_content_disposition(), build_group_journal(), _configure_pdf_font(), ExportedDocument, ExportService (+7 more)

### Community 22 - "schemas/auth.py"
Cohesion: 0.11
Nodes (15): login(), refresh_tokens(), AcademicGroupBase, AcademicGroupCreate, AcademicGroupRead, AcademicGroupUpdate, ErrorResponse, LoginRequest (+7 more)

### Community 23 - "package.json"
Cohesion: 0.07
Nodes (39): devDependencies, autoprefixer@^10.4.20, eslint@^9.15.0, @eslint/js@^9.15.0, eslint-plugin-react-hooks@^5.0.0, eslint-plugin-react-refresh@^0.4.14, globals@^15.12.0, postcss@^8.4.49 (+31 more)

### Community 24 - "App.tsx"
Cohesion: 0.14
Nodes (27): App(), ProtectedAppLayout(), RoleHomeRedirect(), PlagiarismBadgeProps, Navbar(), NavbarProps, resolvePageTitle(), ROLE_BADGE_CONFIG (+19 more)

### Community 25 - "DomainError"
Cohesion: 0.11
Nodes (17): create_admin_group(), create_admin_user(), delete_admin_group(), delete_admin_user(), _ensure_email_unique(), _ensure_group_code_unique(), _get_group_or_404(), _get_user_with_group_or_404() (+9 more)

### Community 26 - "AdminUsersPage.tsx"
Cohesion: 0.06
Nodes (50): GradingReportCardProps, AdminTab, AdminUsersPage(), buildCredentialsReportText(), CourseYearFilter, DeleteTarget, downloadCredentialsReportTxt(), FeedbackBanner (+42 more)

### Community 27 - "course.ts"
Cohesion: 0.08
Nodes (43): CourseEditorPage(), DISCIPLINE_META, DisciplineMeta, EditorTab, fetchCourses(), fetchModuleDetail(), fetchModuleQuizQuestions(), fetchPracticalTeacher() (+35 more)

### Community 28 - "_SeedQuizQuestionPayload"
Cohesion: 0.18
Nodes (4): _SeedCoursePayload, _SeedModulePayload, _SeedPracticalPayload, _SeedQuizQuestionPayload

### Community 29 - "AuthContext.tsx"
Cohesion: 0.23
Nodes (15): apiClient, clearAuthTokens(), getAccessToken(), getRefreshToken(), setAccessToken(), setRefreshToken(), AuthContext, AuthContextValue (+7 more)

### Community 30 - "XlsxGrader"
Cohesion: 0.08
Nodes (4): _canonicalize_formula(), _is_wrapped_in_parens(), _try_parse_numeric(), XlsxGrader

### Community 32 - "GroupJournalPage.tsx"
Cohesion: 0.26
Nodes (14): PlagiarismBadge(), extractApiErrorMessage(), COURSE_SLUG_BADGES, extractBlobApiErrorMessage(), fetchAcademicGroups(), fetchCourses(), fetchGroupJournal(), fetchSubmissionDetail() (+6 more)

### Community 34 - "HtmlSandbox.tsx"
Cohesion: 0.22
Nodes (10): @monaco-editor/react@4.6.0, buildStarterHtmlTemplate(), EditorColorTheme, HtmlSandbox(), HtmlSandboxProps, QUICK_HTML_SNIPPETS, QuickSnippet, SandboxViewMode (+2 more)

### Community 35 - "parse_docx_students"
Cohesion: 0.07
Nodes (19): build_generated_email(), _classify_header_cell(), _clean_whitespace(), _detect_docx_header_columns(), _DocxColumnMap, _encode_ukrainian_word(), _get_cell_value(), _infer_default_docx_columns() (+11 more)

### Community 36 - "Settings"
Cohesion: 0.18
Nodes (3): get_settings(), _resolve_backend_path(), Settings

### Community 37 - "SubmissionService"
Cohesion: 0.12
Nodes (4): GradingRulesUpdateRequest, _is_submission_file_available(), serialize_submission(), SubmissionService

### Community 38 - "SqliteAsyncSessionAdapter"
Cohesion: 0.21
Nodes (3): SqliteAsyncSessionAdapter, test_academic_group_course_year_restricted_to_1_through_4(), test_seed_database_sync_courses_preserves_users_and_groups()

### Community 40 - "GradebookPage.tsx"
Cohesion: 0.11
Nodes (22): COURSE_VISUAL_META, CoursesPage(), CourseVisualMeta, fetchCourses(), FilterOption, ModuleRowCard(), PRACTICAL_FORMAT_LABELS, AttemptMeta (+14 more)

### Community 42 - "export_group_journal"
Cohesion: 0.16
Nodes (4): export_group_journal(), get_group_journal(), list_academic_groups(), _parse_export_format()

### Community 43 - "._parse_table_column_target"
Cohesion: 0.14
Nodes (4): AccdbColumnSchema, AccdbTableSchema, _is_numeric_condition(), _strip_identifiers()

### Community 44 - "ModuleViewPage.tsx"
Cohesion: 0.12
Nodes (29): AccessFieldDescriptor, AccessTableDescriptor, BinaryPracticalFormat, fetchModuleDetail(), fetchStudentPractical(), FILE_UPLOAD_FORMAT_META, FileUploadFormatMeta, FORMAT_BADGE_LABELS (+21 more)

### Community 45 - "DomainError"
Cohesion: 0.11
Nodes (7): role_checker(), import_admin_students(), DomainError, ImportedStudentItem, ImportSkippedItem, StudentImportResponse, StudentImportService

### Community 46 - "seed.py"
Cohesion: 0.13
Nodes (10): Course, build_seed_bundle(), _load_course_from_json(), main(), run_seed(), seed_database(), SeedBundle, SeedSummary (+2 more)

### Community 47 - "submission_service.py"
Cohesion: 0.07
Nodes (18): require_role(), Base, Module, Practical, QuizQuestion, QuizAttempt, AcademicGroup, _enum_values() (+10 more)

### Community 48 - "main.py"
Cohesion: 0.15
Nodes (3): create_application(), lifespan(), test_lifespan_starts_and_cancels_retention_background_task()

### Community 49 - "GradingRule"
Cohesion: 0.09
Nodes (8): AccdbDatabaseSchema, _find_tag_attr_key(), _get_tag_attribute_str(), HtmlGrader, _normalize_selector(), _tag_has_attribute(), CriterionResult, GradingRule

### Community 50 - "db_session"
Cohesion: 0.13
Nodes (5): async_client(), _create_sqlite_test_engine(), _set_sqlite_pragma(), db_session(), _fast_seed_hash_password()

### Community 51 - "@tanstack/react-query"
Cohesion: 0.17
Nodes (11): dependencies, axios@^1.7.7, lucide-react@^0.460.0, react@^18.3.1, react-dom@^18.3.1, react-router-dom@^6.28.0, @tanstack/react-query@^5.60.0, queryClient (+3 more)

### Community 52 - "get_db"
Cohesion: 0.10
Nodes (20): create_course(), create_module(), create_quiz_question(), delete_quiz_question(), _fetch_user_progress_maps(), get_course(), get_module(), get_practical_for_student() (+12 more)

### Community 58 - "services/__init__.py"
Cohesion: 0.09
Nodes (14): Submission, calculate_criterion_error_stats(), _RuleStatAccumulator, cleanup_expired_submissions(), delete_submission_file_safely(), delete_submission_files_for_paths(), main(), resolve_submission_file_path() (+6 more)

### Community 60 - "build_sample_docx"
Cohesion: 0.21
Nodes (5): build_sample_accdb(), build_sample_docx(), build_sample_xlsx(), _replace_zip_member(), rewrite_openxml_core_metadata()

### Community 61 - "do_run_migrations"
Cohesion: 0.29
Nodes (3): do_run_migrations(), run_async_migrations(), run_migrations_online()

### Community 67 - "submit_practical_work"
Cohesion: 0.15
Nodes (4): _extract_submission_payload(), ExtractedSubmissionPayload, submit_practical_work(), update_practical_grading_rules()

### Community 68 - "practicals.py"
Cohesion: 0.18
Nodes (6): CriterionErrorStat, GroupJournalRow, GroupJournalStudentCell, HtmlSubmissionRequest, ManualGradeUpdateRequest, SubmissionRead

## Knowledge Gaps
- **1 isolated node(s):** `edu-auto-grader-backend`
  These have ≤1 connection - possible missing edges. (Counts symbols only; 660 node(s) total have ≤1 connection when file, concept and rationale nodes are included.)
- **23 thin communities (<3 nodes) omitted from report** — run `graphify query` to explore isolated nodes.

## Suggested Questions
_Questions this graph is uniquely positioned to answer:_

- **Why does `GradingRule` connect `GradingRule` to `BaseGrader`, `AccdbGrader`, `accdb_grader.py`, `SubmissionService`, `DocxGrader`, `InvalidFileFormatError`, `.evaluate`, `._parse_table_column_target`, `InvalidFileFormatError`, `courses.py`, `submission_service.py`, `seed.py`, `get_db`, `.evaluate`, `schemas/auth.py`, `.evaluate`, `_SeedQuizQuestionPayload`, `XlsxGrader`?**
  _High betweenness centrality (0.065) - this node is a cross-community bridge._
- **Are the 14 inferred relationships involving `GradingRule` (e.g. with `_serialize_practical_teacher()` and `AccdbGrader`) actually correct?**
  _`GradingRule` has 14 INFERRED edges - model-reasoned connections that need verification._
- **What connects `edu-auto-grader-backend` to the rest of the system?**
  _1 weakly-connected nodes found - possible missing edges._
- **Should `postgres` be split into smaller, more focused modules?**
  _Cohesion score 0.09523809523809523 - nodes in this community are weakly interconnected._
- **Why does `DomainError` connect `DomainError` to `UserRole`, `PlagiarismDetectedError`, `submit_practical_work`, `practicals.py`, `BaseGrader`, `SubmissionService`, `export_group_journal`, `courses.py`, `submission_service.py`, `main.py`, `ExportService`, `get_db`, `GradingError`, `schemas/auth.py`, `DomainError`, `get_current_user`?**
  _High betweenness centrality (0.042) - this node is a cross-community bridge._
- **Are the 15 inferred relationships involving `DomainError` (e.g. with `delete_admin_user()` and `update_admin_user()`) actually correct?**
  _`DomainError` has 15 INFERRED edges - model-reasoned connections that need verification._
- **Should `compilerOptions` be split into smaller, more focused modules?**
  _Cohesion score 0.09523809523809523 - nodes in this community are weakly interconnected._