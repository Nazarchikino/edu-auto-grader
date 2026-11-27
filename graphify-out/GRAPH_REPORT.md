# Graph Report - edu-auto-grader  (2026-11-27)

## Corpus Check
- 106 files · ~317,742 words
- Verdict: corpus is large enough that graph structure adds value.
- Unclassified: 14 file(s) not represented in the graph (top: (none) 9, .example 1, .ini 1)

## Summary
- 2424 nodes · 6962 edges · 98 communities (64 shown, 34 thin omitted)
- Extraction: 90% EXTRACTED · 10% INFERRED · 0% AMBIGUOUS · INFERRED: 725 edges (avg confidence: 0.92)
- Token cost: 0 input · 0 output

## Graph Freshness
- Built from commit: `be5e0649`
- Run `git rev-parse HEAD` and compare to check if the graph is stale.
- Run `graphify update .` after code changes (no API cost).

## Community Hubs (Navigation)
- QuizService
- postgres
- compilerOptions
- User
- practicals.py
- env
- analytics.py
- test_auth_security.py
- MarkdownRenderer.tsx
- vite-env.d.ts
- test_delete_admin_user_removes_student_submissions_and_disk_files
- main
- ExportService
- v1/auth.py
- make_auth_headers
- GradingRule
- edu-auto-grader-backend
- _postgresql_retention_advisory_lock
- package.json
- App.tsx
- admin.py
- AdminUsersPage.tsx
- course.ts
- GroupJournalPage.tsx
- AuthContext.tsx
- XlsxGrader
- environment
- list_my_submissions
- HtmlSandbox.tsx
- test_change_password_validation_and_imported_student_flag
- ExportFormat
- xlsx_grader.py
- RuleBuilderPage.tsx
- UserRole
- GradingReportCard.tsx
- db_session
- GroupJournalRead
- courses.py
- ModuleViewPage.tsx
- _collect_docx_body_fragments
- SlidingWindowRateLimiter
- 0002_restrict_course_year_to_4.py
- services/__init__.py
- test_export_service.py
- UserRole
- student_import_service.py
- _matches_exact_lookup
- DocxGrader
- _extract_html_fingerprint
- submission_service.py
- GradingRule
- SqliteAsyncSessionAdapter
- networks
- .__call__
- _resolve_backend_path
- seed.py
- get_current_user
- test_postgresql_advisory_lock_skips_when_already_held
- _FormulaEvalError
- @tanstack/react-query
- AccdbGrader
- InvalidFileFormatError
- do_run_migrations
- sqlalchemy
- export_service.py
- read_upload_file_limited
- _tokenize_formula
- _FormulaParser
- Decimal
- _compile_jsonb_for_sqlite
- _enum_values
- _SeedCoursePayload
- metadata.py
- get_db
- frontend
- backend
- main.py
- healthcheck
- build
- db
- _set_xlsx_text_cell
- backup.sh
- restore.sh

## God Nodes (most connected - your core abstractions)
1. `SqliteAsyncSessionAdapter` - 94 edges
2. `GradingRule` - 93 edges
3. `User` - 84 edges
4. `CourseSlug` - 74 edges
5. `DomainError` - 72 edges
6. `GradingError` - 61 edges
7. `make_auth_headers()` - 60 edges
8. `DocxGrader` - 56 edges
9. `InvalidFileFormatError` - 52 edges
10. `UserRole` - 50 edges

## Surprising Connections (you probably didn't know these)
- `list_courses()` --uses--> `CourseRead`  [INFERRED]
  backend/app/api/v1/courses.py → backend/app/schemas/course.py
- `get_course()` --uses--> `CourseRead`  [INFERRED]
  backend/app/api/v1/courses.py → backend/app/schemas/course.py
- `create_course()` --uses--> `CourseCreate`  [INFERRED]
  backend/app/api/v1/courses.py → backend/app/schemas/course.py
- `create_course()` --uses--> `CourseRead`  [INFERRED]
  backend/app/api/v1/courses.py → backend/app/schemas/course.py
- `update_course()` --uses--> `CourseRead`  [INFERRED]
  backend/app/api/v1/courses.py → backend/app/schemas/course.py

## Import Cycles
- None detected.

## Communities (98 total, 34 thin omitted)

### Community 0 - "QuizService"
Cohesion: 0.11
Nodes (6): _build_module_detail_read(), submit_module_quiz(), _ensure_utc(), format_cooldown_remaining(), get_quiz_pass_threshold_percent(), QuizService

### Community 1 - "postgres"
Cohesion: 0.11
Nodes (18): POSTGRES_DB, POSTGRES_PASSWORD, POSTGRES_USER, interval, retries, test, timeout, container_name (+10 more)

### Community 2 - "compilerOptions"
Cohesion: 0.10
Nodes (20): compilerOptions, allowImportingTsExtensions, isolatedModules, jsx, lib, module, moduleDetection, moduleResolution (+12 more)

### Community 3 - "User"
Cohesion: 0.10
Nodes (15): Base, Course, Module, QuizQuestion, QuizAttempt, Submission, User, test_all_alembic_revisions_fit_varchar_32_and_form_single_linear_chain() (+7 more)

### Community 4 - "practicals.py"
Cohesion: 0.08
Nodes (12): dry_run_practical_work(), _extract_dry_run_payload(), _extract_submission_payload(), ExtractedDryRunPayload, ExtractedSubmissionPayload, _parse_rules_json_field(), _resolve_practical_upload_limit(), submit_practical_work() (+4 more)

### Community 5 - "env"
Cohesion: 0.06
Nodes (38): env, name, runs-on, services, steps, concurrency, cancel-in-progress, group (+30 more)

### Community 6 - "analytics.py"
Cohesion: 0.19
Nodes (3): export_group_journal(), get_group_journal(), list_academic_groups()

### Community 7 - "test_auth_security.py"
Cohesion: 0.12
Nodes (5): get_settings(), Settings, test_settings_production_rejects_default_or_short_jwt_secret(), test_health_ready_returns_200_when_healthy_and_503_on_uploads_or_db_failure(), test_uploads_dir_relative_path_is_anchored_to_backend_directory()

### Community 8 - "MarkdownRenderer.tsx"
Cohesion: 0.13
Nodes (30): dedentBlockLines(), findClosingDoubleStar(), findClosingParen(), findClosingSingleStar(), findMatchingBracket(), getAlignmentClass(), getLineIndent(), hasUnsafeControlChars() (+22 more)

### Community 11 - "test_delete_admin_user_removes_student_submissions_and_disk_files"
Cohesion: 0.11
Nodes (11): _build_college_import_docx(), _get_user_by_email(), test_admin_academic_groups_crud_and_detachment(), test_admin_bulk_import_docx_sorts_ukrainian_alphabet_and_assigns_variants(), test_admin_bulk_import_rbac_and_validation_errors(), test_admin_bulk_import_returns_413_on_oversized_file_and_422_on_zip_bomb(), test_admin_bulk_import_txt_formats_continuing_list_number_and_duplicates(), test_admin_endpoints_enforce_admin_rbac() (+3 more)

### Community 15 - "v1/auth.py"
Cohesion: 0.06
Nodes (22): change_password(), _extract_client_ip(), login(), refresh_tokens(), build_login_rate_limit_key(), create_token_pair(), decode_token(), verify_password_async() (+14 more)

### Community 16 - "make_auth_headers"
Cohesion: 0.09
Nodes (28): CourseSlug, build_sample_docx(), build_sample_xlsx(), make_auth_headers(), _replace_zip_member(), rewrite_openxml_core_metadata(), _get_course_module_and_practical(), _get_user_by_email() (+20 more)

### Community 17 - "GradingRule"
Cohesion: 0.04
Nodes (33): format_student_criterion_description(), _canonicalize_formula(), _is_wrapped_in_parens(), _normalize_bare_function_name(), _replace_localized_functions_in_segment(), XlsxGrader, GradingRule, GradingRuleType (+25 more)

### Community 23 - "package.json"
Cohesion: 0.07
Nodes (39): devDependencies, autoprefixer@^10.4.20, eslint@^9.15.0, @eslint/js@^9.15.0, eslint-plugin-react-hooks@^5.0.0, eslint-plugin-react-refresh@^0.4.14, globals@^15.12.0, postcss@^8.4.49 (+31 more)

### Community 24 - "App.tsx"
Cohesion: 0.15
Nodes (28): App(), ProtectedAppLayout(), RoleHomeRedirect(), ChangePasswordModal(), ChangePasswordModalProps, Navbar(), NavbarProps, resolvePageTitle() (+20 more)

### Community 25 - "admin.py"
Cohesion: 0.08
Nodes (24): create_admin_group(), create_admin_user(), delete_admin_group(), delete_admin_user(), _ensure_email_unique(), _ensure_group_code_unique(), _ensure_group_list_number_unique(), _get_group_or_404() (+16 more)

### Community 26 - "AdminUsersPage.tsx"
Cohesion: 0.06
Nodes (46): AdminTab, AdminUsersPage(), buildCredentialsReportText(), CourseYearFilter, DeleteTarget, downloadCredentialsReportTxt(), FeedbackBanner, fetchAdminGroups() (+38 more)

### Community 27 - "course.ts"
Cohesion: 0.08
Nodes (44): COURSE_VISUAL_META, CoursesPage(), CourseVisualMeta, fetchCourses(), FilterOption, ModuleRowCard(), PRACTICAL_FORMAT_LABELS, CourseEditorPage() (+36 more)

### Community 28 - "GroupJournalPage.tsx"
Cohesion: 0.20
Nodes (17): PlagiarismBadge(), PlagiarismBadgeProps, extractApiErrorMessage(), COURSE_SLUG_BADGES, extractBlobApiErrorMessage(), fetchAcademicGroups(), fetchCourses(), fetchGroupJournal() (+9 more)

### Community 29 - "AuthContext.tsx"
Cohesion: 0.12
Nodes (29): axios@^1.7.7, API_BASE_URL, apiClient, AuthFailureListener, authFailureListeners, clearAuthTokens(), getAccessToken(), getRefreshToken() (+21 more)

### Community 32 - "environment"
Cohesion: 0.13
Nodes (17): environment, environment, APP_ENV, CORS_ORIGINS, ENABLE_RETENTION_CLEANUP_TASK, FORWARDED_ALLOW_IPS, JWT_SECRET_KEY, POSTGRES_DB (+9 more)

### Community 33 - "list_my_submissions"
Cohesion: 0.19
Nodes (5): download_submission_file(), get_submission_detail(), list_my_submissions(), list_submissions(), update_submission_grade()

### Community 34 - "HtmlSandbox.tsx"
Cohesion: 0.13
Nodes (18): @monaco-editor/react@4.6.0, buildDraftStorageKey(), buildStarterHtmlTemplate(), DraftSaveState, EditorColorTheme, formatDraftSavedTime(), HtmlSandbox(), HtmlSandboxProps (+10 more)

### Community 35 - "test_change_password_validation_and_imported_student_flag"
Cohesion: 0.24
Nodes (5): _get_user_by_email(), test_change_password_validation_and_imported_student_flag(), test_login_rate_limiting_blocks_after_n_failures_and_resets_on_success(), test_long_cyrillic_password_create_login_and_change_without_500(), test_token_version_revokes_tokens_on_admin_reset_and_self_change()

### Community 36 - "ExportFormat"
Cohesion: 0.29
Nodes (3): _parse_export_format(), ExportFormat, ExportedDocument

### Community 37 - "xlsx_grader.py"
Cohesion: 0.12
Nodes (10): _BoolNode, _CellRefNode, _count_non_empty_values(), _EmptyArgNode, _FuncCallNode, _NumberNode, _RangeRefNode, _RangeValue (+2 more)

### Community 38 - "RuleBuilderPage.tsx"
Cohesion: 0.13
Nodes (22): DryRunResultPanel(), DryRunResultPanelProps, formatPoints(), BinaryFormat, DRY_RUN_FILE_ACCEPT, fetchCourses(), fetchPracticalTeacher(), FORMAT_BADGE_CONFIG (+14 more)

### Community 39 - "UserRole"
Cohesion: 0.13
Nodes (8): create_access_token(), create_refresh_token(), _encode_jwt_token(), _sha256_password_bytes(), verify_password(), test_hash_and_verify_password_async_offload_to_worker_thread(), _recording_hash(), _recording_verify()

### Community 40 - "GradingReportCard.tsx"
Cohesion: 0.10
Nodes (30): COURSE_SLUG_LABELS, CriterionBreakdownItem(), CriterionFilterMode, extractFileNameFromPath(), FORMAT_META, formatDateTime(), GradingReportCard(), GradingReportCardProps (+22 more)

### Community 41 - "db_session"
Cohesion: 0.13
Nodes (5): async_client(), _create_sqlite_test_engine(), _set_sqlite_pragma(), db_session(), _fast_seed_hash_password()

### Community 42 - "GroupJournalRead"
Cohesion: 0.14
Nodes (12): CriterionErrorStat, GroupJournalPracticalRead, GroupJournalRead, GroupJournalRow, GroupJournalStudentCell, build_group_journal(), PracticalColumnInfo, render_group_journal_xlsx() (+4 more)

### Community 43 - "courses.py"
Cohesion: 0.10
Nodes (22): _serialize_practical_teacher(), CourseCreate, CourseRead, CourseUpdate, GradingCriterionPreviewRead, ModuleCreate, ModuleDetailRead, ModuleSummaryRead (+14 more)

### Community 44 - "ModuleViewPage.tsx"
Cohesion: 0.09
Nodes (40): renderInlineMarkdown(), AccessFieldDescriptor, AccessTableDescriptor, ALIGNMENT_DISPLAY_LABELS, BinaryPracticalFormat, dryRunFilePractical(), dryRunHtmlPractical(), extractRetryAfterSeconds() (+32 more)

### Community 45 - "_collect_docx_body_fragments"
Cohesion: 0.31
Nodes (4): _collect_docx_body_fragments(), _collect_docx_xml_table_texts(), _extract_docx_paragraph_xml_text(), _find_xml_text()

### Community 48 - "services/__init__.py"
Cohesion: 0.15
Nodes (14): cleanup_expired_submissions(), cleanup_superseded_submission_files(), _delete_submission_file_paths_with_stats(), delete_submission_file_safely(), delete_submission_file_safely_async(), delete_submission_files_for_paths(), delete_submission_files_for_paths_async(), _inspect_submission_file_paths() (+6 more)

### Community 49 - "test_export_service.py"
Cohesion: 0.12
Nodes (13): _configure_pdf_font(), _fit_pdf_text(), _format_pdf_score(), _prepare_pdf_text(), render_group_journal_pdf(), _draw_page_header(), _draw_table_header(), _count_pdf_pages() (+5 more)

### Community 50 - "UserRole"
Cohesion: 0.13
Nodes (6): require_role(), role_checker(), PlagiarismDetectedError, QuizNotPassedError, _enum_values(), UserRole

### Community 51 - "student_import_service.py"
Cohesion: 0.05
Nodes (27): ImportedStudentItem, ImportSkippedItem, StudentImportResponse, calculate_variant_index(), build_credentials_report(), build_generated_email(), _classify_header_cell(), _clean_whitespace() (+19 more)

### Community 57 - "DocxGrader"
Cohesion: 0.06
Nodes (3): DocxGrader, _format_number(), CriterionResult

### Community 59 - "_extract_html_fingerprint"
Cohesion: 0.17
Nodes (6): _extract_css_property_blocks(), _extract_html_visible_text(), _walk(), _normalize_css_declarations(), _serialize_html_dom_structure(), _walk()

### Community 62 - "submission_service.py"
Cohesion: 0.05
Nodes (15): DryRunGradingResponse, ManualGradeUpdateRequest, SubmissionRead, resolve_student_variant(), _build_submission_download_names(), _check_files_exist_batch(), _evaluate_dry_run_binary_file(), _is_submission_file_available() (+7 more)

### Community 63 - "GradingRule"
Cohesion: 0.05
Nodes (11): GradingError, _parse_relationship_pair_target(), HtmlGrader, _check_selector(), _is_doctype_target(), _normalize_selector(), _parse_text_match_expected(), _strip_quotes() (+3 more)

### Community 64 - "SqliteAsyncSessionAdapter"
Cohesion: 0.06
Nodes (29): SqliteAsyncSessionAdapter, test_academic_group_course_year_restricted_to_1_through_4(), test_seed_database_sync_courses_preserves_users_and_groups(), _get_user_by_email(), test_admin_duplicate_group_list_number_returns_409_and_allows_other_groups(), test_delete_module_renumbers_cleanly_under_unique_constraint_with_reverse_uuids(), test_quiz_questions_preserve_order_index_independently_of_uuids(), _count_quiz_attempts() (+21 more)

### Community 66 - "networks"
Cohesion: 0.40
Nodes (5): driver, internal, networks, edge, internal

### Community 70 - "seed.py"
Cohesion: 0.06
Nodes (28): hash_password(), Practical, AcademicGroup, build_seed_bundle(), _extract_needs_rules_review(), _load_course_from_json(), _question_signature(), run_seed() (+20 more)

### Community 73 - "_FormulaEvalError"
Cohesion: 0.10
Nodes (17): _apply_binary_operator(), _coerce_formula_bool(), _coerce_formula_number(), _collect_logical_values(), _collect_numeric_values(), _eval_countif(), _eval_sumif(), _eval_vlookup() (+9 more)

### Community 75 - "@tanstack/react-query"
Cohesion: 0.18
Nodes (10): dependencies, lucide-react@^0.460.0, react@^18.3.1, react-dom@^18.3.1, react-router-dom@^6.28.0, @tanstack/react-query@^5.60.0, queryClient, rootElement (+2 more)

### Community 77 - "AccdbGrader"
Cohesion: 0.03
Nodes (26): AccdbColumnSchema, AccdbDatabaseSchema, AccdbGrader, AccdbObjectsCatalog, AccdbRelationshipSchema, AccdbTableSchema, build_accdb_bytes(), _dedupe_names_casefold() (+18 more)

### Community 78 - "InvalidFileFormatError"
Cohesion: 0.04
Nodes (24): InvalidFileFormatError, _parse_ddl_column_type(), BaseGrader, _format_margin_measurement(), _format_margins_value(), _replace(), _format_student_placeholder_value(), _format_uk_decimal() (+16 more)

### Community 80 - "do_run_migrations"
Cohesion: 0.18
Nodes (4): do_run_migrations(), run_async_migrations(), run_migrations_offline(), run_migrations_online()

### Community 82 - "sqlalchemy"
Cohesion: 0.09
Nodes (8): downgrade(), upgrade(), downgrade(), upgrade(), downgrade(), upgrade(), downgrade(), upgrade()

### Community 85 - "export_service.py"
Cohesion: 0.13
Nodes (7): build_content_disposition(), calculate_criterion_error_stats(), GroupJournalBundle, _normalize_utc_timestamp(), _RuleStatAccumulator, _sanitize_filename_token(), _transliterate_to_ascii()

### Community 87 - "read_upload_file_limited"
Cohesion: 0.18
Nodes (6): _build_too_large_exception(), format_size_limit_mb(), read_upload_file_limited(), test_read_upload_file_limited_stops_reading_chunks_early(), __init__(), read()

### Community 90 - "_FormulaParser"
Cohesion: 0.36
Nodes (4): _BinaryOpNode, _FormulaParser, _Token, _UnaryOpNode

### Community 99 - "_SeedCoursePayload"
Cohesion: 0.18
Nodes (4): _SeedCoursePayload, _SeedModulePayload, _SeedPracticalPayload, _SeedQuizQuestionPayload

### Community 100 - "metadata.py"
Cohesion: 0.04
Nodes (43): _canonicalize_xlsx_formula(), check_submission_plagiarism(), _clean_optional_str(), _coerce_metadata(), compute_bytes_sha256(), compute_code_sha256(), compute_file_sha256(), compute_shingle_jaccard() (+35 more)

### Community 104 - "get_db"
Cohesion: 0.09
Nodes (24): ensure_course_owner_or_admin(), _collect_practical_submission_file_paths(), create_course(), create_module(), create_quiz_question(), delete_module(), delete_practical(), delete_quiz_question() (+16 more)

### Community 108 - "frontend"
Cohesion: 0.25
Nodes (8): condition, backend, container_name, depends_on, networks, ports, restart, frontend

### Community 110 - "backend"
Cohesion: 0.25
Nodes (8): container_name, depends_on, networks, restart, volumes, condition, db, backend

### Community 122 - "main.py"
Cohesion: 0.11
Nodes (5): _check_uploads_dir_writable(), create_application(), readiness_check(), lifespan(), test_lifespan_starts_and_cancels_retention_background_task()

### Community 141 - "healthcheck"
Cohesion: 0.48
Nodes (7): healthcheck, healthcheck, interval, retries, start_period, test, timeout

### Community 145 - "build"
Cohesion: 0.40
Nodes (6): VITE_API_BASE_URL, build, args, context, dockerfile, build

### Community 147 - "db"
Cohesion: 0.17
Nodes (11): container_name, image, networks, restart, volumes, name, services, db (+3 more)

### Community 168 - "_set_xlsx_text_cell"
Cohesion: 0.15
Nodes (4): _auto_adjust_worksheet_columns(), sanitize_spreadsheet_text(), _set_xlsx_text_cell(), test_sanitize_spreadsheet_text_escapes_all_formula_prefixes()

## Knowledge Gaps
- **1 isolated node(s):** `edu-auto-grader-backend`
  These have ≤1 connection - possible missing edges. (Counts symbols only; 1061 node(s) total have ≤1 connection when file, concept and rationale nodes are included.)
- **34 thin communities (<3 nodes) omitted from report** — run `graphify query` to explore isolated nodes.

## Suggested Questions
_Questions this graph is uniquely positioned to answer:_

- **Why does `GradingRule` connect `GradingRule` to `_SeedCoursePayload`, `practicals.py`, `xlsx_grader.py`, `metadata.py`, `seed.py`, `courses.py`, `AccdbGrader`, `InvalidFileFormatError`, `submission_service.py`, `DocxGrader`, `XlsxGrader`, `GradingRule`?**
  _High betweenness centrality (0.061) - this node is a cross-community bridge._
- **Are the 62 inferred relationships involving `SqliteAsyncSessionAdapter` (e.g. with `_get_user_by_email()` and `test_academic_group_course_year_restricted_to_1_through_4()`) actually correct?**
  _`SqliteAsyncSessionAdapter` has 62 INFERRED edges - model-reasoned connections that need verification._
- **What connects `edu-auto-grader-backend` to the rest of the system?**
  _1 weakly-connected nodes found - possible missing edges._
- **Should `QuizService` be split into smaller, more focused modules?**
  _Cohesion score 0.10591133004926108 - nodes in this community are weakly interconnected._
- **Why does `GradingError` connect `GradingRule` to `metadata.py`, `xlsx_grader.py`, `AccdbGrader`, `InvalidFileFormatError`, `GradingRule`, `UserRole`, `admin.py`, `submission_service.py`, `DocxGrader`?**
  _High betweenness centrality (0.033) - this node is a cross-community bridge._
- **Are the 17 inferred relationships involving `GradingRule` (e.g. with `AccdbGrader` and `_parse_relationship_pair_target()`) actually correct?**
  _`GradingRule` has 17 INFERRED edges - model-reasoned connections that need verification._
- **Should `postgres` be split into smaller, more focused modules?**
  _Cohesion score 0.10526315789473684 - nodes in this community are weakly interconnected._