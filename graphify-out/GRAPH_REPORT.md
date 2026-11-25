# Graph Report - edu-auto-grader  (2026-11-25)

## Corpus Check
- 104 files · ~302,052 words
- Verdict: corpus is large enough that graph structure adds value.
- Unclassified: 14 file(s) not represented in the graph (top: (none) 9, .example 1, .ini 1)

## Summary
- 2383 nodes · 6681 edges · 130 communities (73 shown, 57 thin omitted)
- Extraction: 91% EXTRACTED · 9% INFERRED · 0% AMBIGUOUS · INFERRED: 629 edges (avg confidence: 0.92)
- Token cost: 0 input · 0 output

## Graph Freshness
- Built from commit: `996c8485`
- Run `git rev-parse HEAD` and compare to check if the graph is stale.
- Run `graphify update .` after code changes (no API cost).

## Community Hubs (Navigation)
- QuizService
- postgres
- compilerOptions
- User
- AccdbGrader
- env
- analytics.py
- test_auth_security.py
- MarkdownRenderer.tsx
- vite-env.d.ts
- .execute
- DocxGrader
- ExportService
- v1/auth.py
- make_auth_headers
- test_graders.py
- edu-auto-grader-backend
- submit_practical_work
- package.json
- App.tsx
- admin.py
- AdminUsersPage.tsx
- course.ts
- GroupJournalPage.tsx
- AuthContext.tsx
- XlsxGrader
- _get_student_and_word_practical
- environment
- accdb_grader.py
- HtmlSandbox.tsx
- GradingError
- read_upload_file_limited
- _canonicalize_formula
- RuleBuilderPage.tsx
- UserRole
- GradingReportCard.tsx
- db_session
- export_service.py
- courses.py
- ModuleViewPage.tsx
- _collect_docx_body_fragments
- SlidingWindowRateLimiter
- 0002_restrict_course_year_to_4.py
- cleanup_expired_submissions
- render_group_journal_pdf
- submission_service.py
- student_import_service.py
- ._evaluate_page_margins
- test_accdb_grader_inspects_queries_forms_reports_relationships_and_mdb_export_csv
- QuizNotPassedError
- _get_module_with_questions
- _extract_html_fingerprint
- create_application
- list_my_submissions
- html_grader.py
- SqliteAsyncSessionAdapter
- calculate_criterion_error_stats
- networks
- serialize_submission
- .__call__
- _resolve_backend_path
- test_course_content.py
- get_current_user
- test_postgresql_advisory_lock_skips_when_already_held
- _FormulaEvalError
- @tanstack/react-query
- _strip_identifiers
- _format_student_placeholder_value
- .update_manual_grade
- do_run_migrations
- _find_named_entry
- 0001_initial_schema.py
- _parse_msys_relationships_table
- .prepare_submission_download
- re
- test_read_upload_file_limited_stops_reading_chunks_early
- ._extract_single_table_schema
- _tokenize_formula
- _FormulaParser
- Decimal
- _format_cell_value
- _has_balanced_formula_delimiters
- _compile_jsonb_for_sqlite
- SubmissionService
- _normalize_bare_function_name
- _enum_values
- _RangeValue
- _SeedCoursePayload
- metadata.py
- get_db
- frontend
- backend
- healthcheck
- build
- db
- _set_xlsx_text_cell
- backup.sh
- restore.sh

## God Nodes (most connected - your core abstractions)
1. `SqliteAsyncSessionAdapter` - 84 edges
2. `CourseSlug` - 78 edges
3. `User` - 76 edges
4. `DomainError` - 69 edges
5. `GradingError` - 56 edges
6. `make_auth_headers()` - 55 edges
7. `Module` - 54 edges
8. `Practical` - 53 edges
9. `PracticalFormat` - 52 edges
10. `DocxGrader` - 49 edges

## Surprising Connections (you probably didn't know these)
- `_serialize_course()` --uses--> `Course`  [INFERRED]
  backend/app/api/v1/courses.py → backend/app/models/course.py
- `_load_course_or_404()` --uses--> `Course`  [INFERRED]
  backend/app/api/v1/courses.py → backend/app/models/course.py
- `_load_course_or_404()` --uses--> `Module`  [INFERRED]
  backend/app/api/v1/courses.py → backend/app/models/course.py
- `_load_module_or_404()` --uses--> `Module`  [INFERRED]
  backend/app/api/v1/courses.py → backend/app/models/course.py
- `_ensure_module_order_index_unique()` --uses--> `Module`  [INFERRED]
  backend/app/api/v1/courses.py → backend/app/models/course.py

## Import Cycles
- None detected.

## Communities (130 total, 57 thin omitted)

### Community 0 - "QuizService"
Cohesion: 0.09
Nodes (9): _build_module_detail_read(), get_practical_for_student(), submit_module_quiz(), calculate_variant_index(), _ensure_utc(), format_cooldown_remaining(), get_quiz_pass_threshold_percent(), QuizService (+1 more)

### Community 1 - "postgres"
Cohesion: 0.11
Nodes (18): POSTGRES_DB, POSTGRES_PASSWORD, POSTGRES_USER, interval, retries, test, timeout, container_name (+10 more)

### Community 2 - "compilerOptions"
Cohesion: 0.10
Nodes (20): compilerOptions, allowImportingTsExtensions, isolatedModules, jsx, lib, module, moduleDetection, moduleResolution (+12 more)

### Community 3 - "User"
Cohesion: 0.12
Nodes (18): Base, Course, Module, Practical, QuizQuestion, QuizAttempt, Submission, User (+10 more)

### Community 4 - "AccdbGrader"
Cohesion: 0.12
Nodes (5): AccdbGrader, AccdbObjectsCatalog, _dedupe_relationships(), _is_system_table_name(), test_accdb_grader_evaluates_access_module_9_multiple_variants()

### Community 5 - "env"
Cohesion: 0.06
Nodes (38): env, name, runs-on, services, steps, concurrency, cancel-in-progress, group (+30 more)

### Community 6 - "analytics.py"
Cohesion: 0.12
Nodes (6): export_group_journal(), get_group_journal(), list_academic_groups(), _parse_export_format(), ExportFormat, ExportedDocument

### Community 7 - "test_auth_security.py"
Cohesion: 0.08
Nodes (13): Settings, hash_password(), _sha256_password_bytes(), verify_password(), _get_user_by_email(), test_change_password_validation_and_imported_student_flag(), test_hash_and_verify_password_async_offload_to_worker_thread(), _recording_hash() (+5 more)

### Community 8 - "MarkdownRenderer.tsx"
Cohesion: 0.12
Nodes (31): dedentBlockLines(), findClosingDoubleStar(), findClosingParen(), findClosingSingleStar(), findMatchingBracket(), getAlignmentClass(), getLineIndent(), hasUnsafeControlChars() (+23 more)

### Community 11 - ".execute"
Cohesion: 0.10
Nodes (12): _set_sqlite_pragma(), _build_college_import_docx(), _get_user_by_email(), test_admin_academic_groups_crud_and_detachment(), test_admin_bulk_import_docx_sorts_ukrainian_alphabet_and_assigns_variants(), test_admin_bulk_import_rbac_and_validation_errors(), test_admin_bulk_import_returns_413_on_oversized_file_and_422_on_zip_bomb(), test_admin_bulk_import_txt_formats_continuing_list_number_and_duplicates() (+4 more)

### Community 14 - "ExportService"
Cohesion: 0.13
Nodes (3): build_content_disposition(), ExportService, GroupJournalBundle

### Community 15 - "v1/auth.py"
Cohesion: 0.10
Nodes (9): change_password(), _extract_client_ip(), login(), read_current_user(), refresh_tokens(), build_login_rate_limit_key(), verify_password_async(), ChangePasswordResponse (+1 more)

### Community 16 - "make_auth_headers"
Cohesion: 0.10
Nodes (25): CourseSlug, build_sample_docx(), make_auth_headers(), _get_course_module_and_practical(), _get_user_by_email(), _grant_quiz_pass(), test_antiplagiarism_api_html_structural_match_and_classroom_template_clean(), test_antiplagiarism_flags_sha256_and_core_xml_matches_across_students() (+17 more)

### Community 17 - "test_graders.py"
Cohesion: 0.07
Nodes (28): GradingRule, GradingRuleType, build_sample_accdb(), build_sample_xlsx(), _replace_zip_member(), rewrite_openxml_core_metadata(), _strip_zip_member(), test_accdb_grader_accepts_hyperlink_type_as_memo() (+20 more)

### Community 22 - "submit_practical_work"
Cohesion: 0.14
Nodes (5): _extract_submission_payload(), ExtractedSubmissionPayload, _resolve_practical_upload_limit(), submit_practical_work(), update_practical_grading_rules()

### Community 23 - "package.json"
Cohesion: 0.07
Nodes (39): devDependencies, autoprefixer@^10.4.20, eslint@^9.15.0, @eslint/js@^9.15.0, eslint-plugin-react-hooks@^5.0.0, eslint-plugin-react-refresh@^0.4.14, globals@^15.12.0, postcss@^8.4.49 (+31 more)

### Community 24 - "App.tsx"
Cohesion: 0.15
Nodes (28): App(), ProtectedAppLayout(), RoleHomeRedirect(), ChangePasswordModal(), ChangePasswordModalProps, Navbar(), NavbarProps, resolvePageTitle() (+20 more)

### Community 25 - "admin.py"
Cohesion: 0.08
Nodes (23): create_admin_group(), create_admin_user(), delete_admin_group(), delete_admin_user(), _ensure_email_unique(), _ensure_group_code_unique(), _ensure_group_list_number_unique(), _get_group_or_404() (+15 more)

### Community 26 - "AdminUsersPage.tsx"
Cohesion: 0.07
Nodes (43): RoleGuardProps, AdminTab, AdminUsersPage(), buildCredentialsReportText(), CourseYearFilter, DeleteTarget, downloadCredentialsReportTxt(), FeedbackBanner (+35 more)

### Community 27 - "course.ts"
Cohesion: 0.08
Nodes (42): COURSE_VISUAL_META, CourseVisualMeta, fetchCourses(), FilterOption, ModuleRowCard(), PRACTICAL_FORMAT_LABELS, CourseEditorPage(), deleteModuleById() (+34 more)

### Community 28 - "GroupJournalPage.tsx"
Cohesion: 0.15
Nodes (20): PlagiarismBadge(), PlagiarismBadgeProps, COURSE_SLUG_BADGES, extractBlobApiErrorMessage(), fetchAcademicGroups(), fetchCourses(), fetchGroupJournal(), fetchSubmissionDetail() (+12 more)

### Community 29 - "AuthContext.tsx"
Cohesion: 0.12
Nodes (28): axios@^1.7.7, API_BASE_URL, apiClient, AuthFailureListener, authFailureListeners, clearAuthTokens(), getAccessToken(), getRefreshToken() (+20 more)

### Community 31 - "_get_student_and_word_practical"
Cohesion: 0.16
Nodes (5): test_cleanup_superseded_respects_24h_grace_window(), test_cleanup_superseded_submission_files_keeps_best_and_latest_only(), test_health_ready_returns_200_when_healthy_and_503_on_uploads_or_db_failure(), test_media_courses_responses_include_security_headers(), test_uploads_dir_relative_path_is_anchored_to_backend_directory()

### Community 32 - "environment"
Cohesion: 0.13
Nodes (17): environment, environment, APP_ENV, CORS_ORIGINS, ENABLE_RETENTION_CLEANUP_TASK, FORWARDED_ALLOW_IPS, JWT_SECRET_KEY, POSTGRES_DB (+9 more)

### Community 33 - "accdb_grader.py"
Cohesion: 0.15
Nodes (6): build_accdb_bytes(), _encode_data_page(), _encode_msys_catalog_record(), _encode_tdef_page(), _encode_text_record(), _parse_ddl_column_type()

### Community 34 - "HtmlSandbox.tsx"
Cohesion: 0.13
Nodes (17): @monaco-editor/react@4.6.0, buildDraftStorageKey(), buildStarterHtmlTemplate(), DraftSaveState, EditorColorTheme, formatDraftSavedTime(), HtmlSandbox(), HtmlSandboxProps (+9 more)

### Community 35 - "GradingError"
Cohesion: 0.06
Nodes (8): GradingError, InvalidFileFormatError, BaseGrader, GraderFactory, _check_selector(), _is_doctype_target(), PracticalFormat, test_grader_factory_resolves_all_four_formats()

### Community 36 - "read_upload_file_limited"
Cohesion: 0.28
Nodes (3): _build_too_large_exception(), format_size_limit_mb(), read_upload_file_limited()

### Community 37 - "_canonicalize_formula"
Cohesion: 0.33
Nodes (3): _canonicalize_formula(), _is_wrapped_in_parens(), _replace_localized_functions_in_segment()

### Community 38 - "RuleBuilderPage.tsx"
Cohesion: 0.19
Nodes (14): fetchCourses(), fetchPracticalTeacher(), FORMAT_BADGE_CONFIG, formatPointsCompact(), renderFormatIcon(), RULE_TYPE_SPECS, RuleBuilderPage(), RuleTypeSpec (+6 more)

### Community 39 - "UserRole"
Cohesion: 0.21
Nodes (6): create_access_token(), create_refresh_token(), create_token_pair(), _encode_jwt_token(), _enum_values(), UserRole

### Community 40 - "GradingReportCard.tsx"
Cohesion: 0.09
Nodes (31): COURSE_SLUG_LABELS, CriterionBreakdownItem(), CriterionFilterMode, extractFileNameFromPath(), FORMAT_META, formatDateTime(), GradingReportCard(), GradingReportCardProps (+23 more)

### Community 41 - "db_session"
Cohesion: 0.15
Nodes (4): async_client(), _create_sqlite_test_engine(), db_session(), _fast_seed_hash_password()

### Community 42 - "export_service.py"
Cohesion: 0.09
Nodes (20): GradingReport, CriterionErrorStat, GroupJournalPracticalRead, GroupJournalRead, GroupJournalRow, GroupJournalStudentCell, HtmlSubmissionRequest, _auto_adjust_worksheet_columns() (+12 more)

### Community 43 - "courses.py"
Cohesion: 0.08
Nodes (24): format_student_criterion_description(), CourseCreate, CourseRead, CourseUpdate, GradingCriterionPreviewRead, ModuleCreate, ModuleDetailRead, ModuleSummaryRead (+16 more)

### Community 44 - "ModuleViewPage.tsx"
Cohesion: 0.09
Nodes (39): AccessFieldDescriptor, AccessTableDescriptor, ALIGNMENT_DISPLAY_LABELS, BinaryPracticalFormat, extractRetryAfterSeconds(), fetchModuleDetail(), fetchStudentPractical(), FILE_UPLOAD_FORMAT_META (+31 more)

### Community 45 - "_collect_docx_body_fragments"
Cohesion: 0.31
Nodes (4): _collect_docx_body_fragments(), _collect_docx_xml_table_texts(), _extract_docx_paragraph_xml_text(), _find_xml_text()

### Community 48 - "cleanup_expired_submissions"
Cohesion: 0.10
Nodes (16): cleanup_expired_submissions(), cleanup_superseded_submission_files(), _delete_submission_file_paths_with_stats(), delete_submission_file_safely(), delete_submission_file_safely_async(), delete_submission_files_for_paths(), delete_submission_files_for_paths_async(), _inspect_submission_file_paths() (+8 more)

### Community 49 - "render_group_journal_pdf"
Cohesion: 0.21
Nodes (8): _configure_pdf_font(), _fit_pdf_text(), _format_pdf_score(), _prepare_pdf_text(), render_group_journal_pdf(), _draw_page_header(), _draw_table_header(), test_pdf_compact_score_formatting_and_text_fitting()

### Community 50 - "submission_service.py"
Cohesion: 0.07
Nodes (12): downgrade(), upgrade(), downgrade(), upgrade(), downgrade(), upgrade(), require_role(), get_settings() (+4 more)

### Community 51 - "student_import_service.py"
Cohesion: 0.04
Nodes (36): AcademicGroupBase, AcademicGroupUpdate, AdminResetPasswordRequest, AdminResetPasswordResponse, ChangePasswordRequest, ErrorResponse, ImportedStudentItem, ImportSkippedItem (+28 more)

### Community 53 - "test_accdb_grader_inspects_queries_forms_reports_relationships_and_mdb_export_csv"
Cohesion: 0.14
Nodes (8): _dedupe_names_casefold(), _is_hidden_or_system_object(), _parse_int_optional(), _parse_msys_objects_csv(), _parse_msys_objects_table(), _parse_msys_relationships_csv(), test_accdb_grader_inspects_queries_forms_reports_relationships_and_mdb_export_csv(), _fake_which()

### Community 55 - "_get_module_with_questions"
Cohesion: 0.18
Nodes (8): _build_answers_for_score(), _get_module_with_questions(), _get_user_by_email(), test_excel_q42_imported_in_module_8_with_media_and_dry_run(), test_quiz_cooldown_zero_disables_wait_and_negative_config_rejected(), test_quiz_pass_threshold_setting_controls_passed_flag(), test_quiz_retry_cooldown_blocks_immediate_retry_and_unlocks_after_window(), test_quiz_submit_rejects_incomplete_duplicate_foreign_and_invalid_answers()

### Community 59 - "_extract_html_fingerprint"
Cohesion: 0.12
Nodes (9): compute_text_shingles(), _extract_css_property_blocks(), _extract_html_fingerprint(), _extract_html_visible_text(), _walk(), _normalize_css_declarations(), _serialize_html_dom_structure(), _walk() (+1 more)

### Community 61 - "create_application"
Cohesion: 0.25
Nodes (3): _check_uploads_dir_writable(), create_application(), readiness_check()

### Community 62 - "list_my_submissions"
Cohesion: 0.18
Nodes (6): download_submission_file(), get_submission_detail(), list_my_submissions(), list_submissions(), update_submission_grade(), SubmissionRead

### Community 63 - "html_grader.py"
Cohesion: 0.07
Nodes (13): _attribute_value_matches(), _find_tag_attr_key(), _get_tag_attribute_str(), has_meaningful_html_body(), HtmlGrader, _node_has_visible_content(), _normalize_selector(), _normalize_text() (+5 more)

### Community 64 - "SqliteAsyncSessionAdapter"
Cohesion: 0.10
Nodes (14): SqliteAsyncSessionAdapter, test_academic_group_course_year_restricted_to_1_through_4(), test_long_cyrillic_password_create_login_and_change_without_500(), _get_user_by_email(), test_delete_module_and_practical_rbac_and_not_found(), test_delete_practical_preserves_module_lecture_quiz_and_cleans_files(), test_media_courses_static_serving(), test_seed_database_sync_courses_preserves_users_and_groups() (+6 more)

### Community 65 - "calculate_criterion_error_stats"
Cohesion: 0.29
Nodes (3): calculate_criterion_error_stats(), _normalize_utc_timestamp(), _RuleStatAccumulator

### Community 66 - "networks"
Cohesion: 0.40
Nodes (5): driver, internal, networks, edge, internal

### Community 67 - "serialize_submission"
Cohesion: 0.18
Nodes (3): _check_files_exist_batch(), _is_submission_file_available(), serialize_submission()

### Community 70 - "test_course_content.py"
Cohesion: 0.06
Nodes (24): AcademicGroup, build_seed_bundle(), _extract_needs_rules_review(), _load_course_from_json(), main(), _question_signature(), run_seed(), seed_database() (+16 more)

### Community 73 - "_FormulaEvalError"
Cohesion: 0.07
Nodes (21): _apply_binary_operator(), _coerce_formula_bool(), _coerce_formula_number(), _collect_logical_values(), _collect_numeric_values(), _count_non_empty_values(), _eval_countif(), _eval_sumif() (+13 more)

### Community 75 - "@tanstack/react-query"
Cohesion: 0.18
Nodes (10): dependencies, lucide-react@^0.460.0, react@^18.3.1, react-dom@^18.3.1, react-router-dom@^6.28.0, @tanstack/react-query@^5.60.0, queryClient, rootElement (+2 more)

### Community 77 - "_strip_identifiers"
Cohesion: 0.12
Nodes (5): AccdbDatabaseSchema, _is_numeric_condition(), _normalize_count_condition(), _parse_relationship_pair_target(), _strip_identifiers()

### Community 78 - "_format_student_placeholder_value"
Cohesion: 0.18
Nodes (5): _format_margin_measurement(), _format_margins_value(), _replace(), _format_student_placeholder_value(), _format_uk_decimal()

### Community 80 - "do_run_migrations"
Cohesion: 0.18
Nodes (4): do_run_migrations(), run_async_migrations(), run_migrations_offline(), run_migrations_online()

### Community 83 - "_parse_msys_relationships_table"
Cohesion: 0.33
Nodes (3): AccdbRelationshipSchema, _lookup_mapping_column(), _parse_msys_relationships_table()

### Community 85 - "re"
Cohesion: 0.20
Nodes (5): _sanitize_filename_token(), _transliterate_to_ascii(), _sanitize_ascii_token(), _sanitize_utf8_token(), _strip_apostrophes()

### Community 87 - "test_read_upload_file_limited_stops_reading_chunks_early"
Cohesion: 0.50
Nodes (3): test_read_upload_file_limited_stops_reading_chunks_early(), __init__(), read()

### Community 88 - "._extract_single_table_schema"
Cohesion: 0.16
Nodes (3): AccdbColumnSchema, AccdbTableSchema, _resolve_canonical_type()

### Community 90 - "_FormulaParser"
Cohesion: 0.21
Nodes (11): _BinaryOpNode, _BoolNode, _CellRefNode, _EmptyArgNode, _FormulaParser, _FuncCallNode, _NumberNode, _RangeRefNode (+3 more)

### Community 91 - "Decimal"
Cohesion: 0.14
Nodes (4): _serialize_practical_teacher(), calculate_practical_score_breakdown(), PracticalTeacherRead, serialize_practical_teacher()

### Community 95 - "SubmissionService"
Cohesion: 0.12
Nodes (3): _save_uploaded_file(), SubmissionService, _unlink_file_quietly()

### Community 99 - "_SeedCoursePayload"
Cohesion: 0.18
Nodes (4): _SeedCoursePayload, _SeedModulePayload, _SeedPracticalPayload, _SeedQuizQuestionPayload

### Community 100 - "metadata.py"
Cohesion: 0.05
Nodes (38): _canonicalize_xlsx_formula(), check_submission_plagiarism(), _clean_optional_str(), _coerce_metadata(), compute_bytes_sha256(), compute_code_sha256(), compute_file_sha256(), compute_shingle_jaccard() (+30 more)

### Community 104 - "get_db"
Cohesion: 0.10
Nodes (25): ensure_course_owner_or_admin(), role_checker(), _collect_practical_submission_file_paths(), create_course(), create_module(), create_quiz_question(), delete_module(), delete_practical() (+17 more)

### Community 108 - "frontend"
Cohesion: 0.25
Nodes (8): condition, backend, container_name, depends_on, networks, ports, restart, frontend

### Community 110 - "backend"
Cohesion: 0.25
Nodes (8): container_name, depends_on, networks, restart, volumes, condition, db, backend

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
Cohesion: 0.20
Nodes (3): sanitize_spreadsheet_text(), _set_xlsx_text_cell(), test_sanitize_spreadsheet_text_escapes_all_formula_prefixes()

## Knowledge Gaps
- **1 isolated node(s):** `edu-auto-grader-backend`
  These have ≤1 connection - possible missing edges. (Counts symbols only; 1050 node(s) total have ≤1 connection when file, concept and rationale nodes are included.)
- **57 thin communities (<3 nodes) omitted from report** — run `graphify query` to explore isolated nodes.

## Suggested Questions
_Questions this graph is uniquely positioned to answer:_

- **Why does `User` connect `User` to `QuizService`, `test_auth_security.py`, `.execute`, `ExportService`, `v1/auth.py`, `make_auth_headers`, `admin.py`, `export_service.py`, `courses.py`, `submission_service.py`, `student_import_service.py`, `_get_module_with_questions`, `list_my_submissions`, `SqliteAsyncSessionAdapter`, `serialize_submission`, `test_course_content.py`, `get_current_user`, `.update_manual_grade`, `.prepare_submission_download`, `SubmissionService`, `get_db`?**
  _High betweenness centrality (0.043) - this node is a cross-community bridge._
- **Are the 35 inferred relationships involving `SqliteAsyncSessionAdapter` (e.g. with `_get_user_by_email()` and `test_academic_group_course_year_restricted_to_1_through_4()`) actually correct?**
  _`SqliteAsyncSessionAdapter` has 35 INFERRED edges - model-reasoned connections that need verification._
- **What connects `edu-auto-grader-backend` to the rest of the system?**
  _1 weakly-connected nodes found - possible missing edges._
- **Should `QuizService` be split into smaller, more focused modules?**
  _Cohesion score 0.08739495798319327 - nodes in this community are weakly interconnected._
- **Why does `DocxGrader` connect `DocxGrader` to `GradingError`, `metadata.py`, `test_course_content.py`, `.evaluate`, `test_graders.py`, `._evaluate_page_margins`, `._resolve_paragraph_alignment`, `.build_criterion_result`, `DocxGrader`?**
  _High betweenness centrality (0.032) - this node is a cross-community bridge._
- **Are the 60 inferred relationships involving `CourseSlug` (e.g. with `CourseCreate` and `CourseRead`) actually correct?**
  _`CourseSlug` has 60 INFERRED edges - model-reasoned connections that need verification._
- **Should `postgres` be split into smaller, more focused modules?**
  _Cohesion score 0.10526315789473684 - nodes in this community are weakly interconnected._