# Graph Report - edu-auto-grader  (2026-11-25)

## Corpus Check
- 104 files · ~294,917 words
- Verdict: corpus is large enough that graph structure adds value.
- Unclassified: 14 file(s) not represented in the graph (top: (none) 9, .example 1, .ini 1)

## Summary
- 2387 nodes · 6438 edges · 176 communities (67 shown, 109 thin omitted)
- Extraction: 93% EXTRACTED · 7% INFERRED · 0% AMBIGUOUS · INFERRED: 430 edges (avg confidence: 0.9)
- Token cost: 0 input · 0 output

## Graph Freshness
- Built from commit: `574b911f`
- Run `git rev-parse HEAD` and compare to check if the graph is stale.
- Run `graphify update .` after code changes (no API cost).

## Community Hubs (Navigation)
- QuizService
- postgres
- compilerOptions
- submission_service.py
- AccdbGrader
- env
- export_group_journal
- .execute
- MarkdownRenderer.tsx
- vite-env.d.ts
- _get_user_by_email
- ExtractedMetadata
- _tokenize_formula
- make_auth_headers
- render_group_journal_pdf
- edu-auto-grader-backend
- login
- package.json
- App.tsx
- admin.py
- AdminUsersPage.tsx
- course.ts
- GroupJournalPage.tsx
- AuthContext.tsx
- XlsxGrader
- 0002_restrict_course_year_to_4.py
- environment
- accdb_grader.py
- HtmlSandbox.tsx
- GradingError
- PracticalFormat
- BaseModel
- CriterionResult
- GradingReportCard.tsx
- db_session
- export_service.py
- submission_service.py
- ModuleViewPage.tsx
- _collect_docx_body_fragments
- SlidingWindowRateLimiter
- _get_user_by_email
- cleanup_expired_submissions
- @tanstack/react-query
- create_application
- student_import_service.py
- _resolve_backend_path
- _get_module_with_questions
- DocxGrader
- decode_token
- _extract_html_fingerprint
- _build_submission_download_names
- test_graders.py
- list_my_submissions
- services
- .__call__
- Settings
- test_course_content.py
- downgrade
- math
- ExportService
- 0005_practical_rules_review.py
- do_run_migrations
- 0001_initial_schema.py
- xlsx_grader.py
- _FormulaParser
- .update_grading_rules
- test_read_upload_file_limited_stops_reading_chunks_early
- _compile_jsonb_for_sqlite
- SubmissionService
- test_lifespan_starts_and_cancels_retention_background_task
- _SeedCoursePayload
- metadata.py
- get_db
- frontend
- backend
- .import_students
- Tag
- healthcheck
- build
- db
- test_postgresql_advisory_lock_skips_when_already_held
- test_all_course_variants_resolve_rule_placeholders_without_leftovers
- _matches_exact_lookup
- run_migrations_offline
- _set_xlsx_text_cell
- test_all_alembic_revisions_fit_varchar_32_and_form_single_linear_chain
- test_media_courses_responses_include_security_headers
- test_duplicate_root_auth_router_removed_returns_404
- backup.sh
- restore.sh

## God Nodes (most connected - your core abstractions)
1. `GradingRule` - 95 edges
2. `SqliteAsyncSessionAdapter` - 82 edges
3. `User` - 70 edges
4. `DomainError` - 66 edges
5. `make_auth_headers()` - 53 edges
6. `GradingError` - 52 edges
7. `DocxGrader` - 51 edges
8. `get_db()` - 46 edges
9. `Module` - 45 edges
10. `XlsxGrader` - 43 edges

## Surprising Connections (you probably didn't know these)
- `test_health_ready_returns_200_when_healthy_and_503_on_uploads_or_db_failure()` --indirect_call--> `get_db()`  [INFERRED]
  backend/tests/test_production_hardening.py → backend/app/core/database.py
- `get_practical_for_student()` --uses--> `QuizService`  [INFERRED]
  backend/app/api/v1/courses.py → backend/app/services/quiz_service.py
- `submit_module_quiz()` --uses--> `QuizService`  [INFERRED]
  backend/app/api/v1/courses.py → backend/app/services/quiz_service.py
- `QuizService` --uses--> `Module`  [INFERRED]
  backend/app/services/quiz_service.py → backend/app/models/course.py
- `QuizService` --uses--> `Practical`  [INFERRED]
  backend/app/services/quiz_service.py → backend/app/models/course.py

## Import Cycles
- None detected.

## Communities (176 total, 109 thin omitted)

### Community 0 - "QuizService"
Cohesion: 0.12
Nodes (5): _build_module_detail_read(), QuizNotPassedError, _ensure_utc(), format_cooldown_remaining(), QuizService

### Community 1 - "postgres"
Cohesion: 0.11
Nodes (18): POSTGRES_DB, POSTGRES_PASSWORD, POSTGRES_USER, interval, retries, test, timeout, container_name (+10 more)

### Community 2 - "compilerOptions"
Cohesion: 0.10
Nodes (20): compilerOptions, allowImportingTsExtensions, isolatedModules, jsx, lib, module, moduleDetection, moduleResolution (+12 more)

### Community 3 - "submission_service.py"
Cohesion: 0.05
Nodes (28): upgrade(), downgrade(), upgrade(), require_role(), Base, PlagiarismDetectedError, hash_password(), _sha256_password_bytes() (+20 more)

### Community 4 - "AccdbGrader"
Cohesion: 0.04
Nodes (19): AccdbColumnSchema, AccdbDatabaseSchema, AccdbGrader, AccdbObjectsCatalog, AccdbRelationshipSchema, AccdbTableSchema, _dedupe_relationships(), _find_named_entry() (+11 more)

### Community 5 - "env"
Cohesion: 0.06
Nodes (38): env, name, runs-on, services, steps, concurrency, cancel-in-progress, group (+30 more)

### Community 6 - "export_group_journal"
Cohesion: 0.14
Nodes (5): export_group_journal(), get_group_journal(), list_academic_groups(), _parse_export_format(), ExportFormat

### Community 7 - ".execute"
Cohesion: 0.10
Nodes (14): SqliteAsyncSessionAdapter, test_academic_group_course_year_restricted_to_1_through_4(), _get_user_by_email(), test_admin_duplicate_group_list_number_returns_409_and_allows_other_groups(), test_delete_module_renumbers_cleanly_under_unique_constraint_with_reverse_uuids(), test_quiz_questions_preserve_order_index_independently_of_uuids(), test_schema_indexes_constraints_and_alembic_0004_backfill(), _get_student_and_word_practical() (+6 more)

### Community 8 - "MarkdownRenderer.tsx"
Cohesion: 0.13
Nodes (30): dedentBlockLines(), findClosingDoubleStar(), findClosingParen(), findClosingSingleStar(), findMatchingBracket(), getAlignmentClass(), getLineIndent(), hasUnsafeControlChars() (+22 more)

### Community 11 - "_get_user_by_email"
Cohesion: 0.11
Nodes (11): _build_college_import_docx(), _get_user_by_email(), test_admin_academic_groups_crud_and_detachment(), test_admin_bulk_import_docx_sorts_ukrainian_alphabet_and_assigns_variants(), test_admin_bulk_import_rbac_and_validation_errors(), test_admin_bulk_import_returns_413_on_oversized_file_and_422_on_zip_bomb(), test_admin_bulk_import_txt_formats_continuing_list_number_and_duplicates(), test_admin_endpoints_enforce_admin_rbac() (+3 more)

### Community 13 - "ExtractedMetadata"
Cohesion: 0.08
Nodes (16): check_submission_plagiarism(), _clean_optional_str(), _coerce_metadata(), evaluate_plagiarism(), _is_content_fingerprint_match_actionable(), _is_generic_creator(), SubmissionRecordProtocol, ExtractedMetadata (+8 more)

### Community 16 - "make_auth_headers"
Cohesion: 0.12
Nodes (23): HtmlSubmissionRequest, build_sample_docx(), make_auth_headers(), rewrite_openxml_core_metadata(), _get_course_module_and_practical(), _get_user_by_email(), _grant_quiz_pass(), test_antiplagiarism_api_html_structural_match_and_classroom_template_clean() (+15 more)

### Community 17 - "render_group_journal_pdf"
Cohesion: 0.13
Nodes (11): _fit_pdf_text(), _format_pdf_score(), _prepare_pdf_text(), render_group_journal_pdf(), _draw_page_header(), _draw_table_header(), _sanitize_filename_token(), _transliterate_to_ascii() (+3 more)

### Community 22 - "login"
Cohesion: 0.05
Nodes (14): _extract_client_ip(), login(), read_current_user(), refresh_tokens(), _extract_submission_payload(), ExtractedSubmissionPayload, _resolve_practical_upload_limit(), submit_practical_work() (+6 more)

### Community 23 - "package.json"
Cohesion: 0.07
Nodes (39): devDependencies, autoprefixer@^10.4.20, eslint@^9.15.0, @eslint/js@^9.15.0, eslint-plugin-react-hooks@^5.0.0, eslint-plugin-react-refresh@^0.4.14, globals@^15.12.0, postcss@^8.4.49 (+31 more)

### Community 24 - "App.tsx"
Cohesion: 0.11
Nodes (35): App(), ProtectedAppLayout(), RoleHomeRedirect(), ChangePasswordModal(), ChangePasswordModalProps, Navbar(), NavbarProps, resolvePageTitle() (+27 more)

### Community 25 - "admin.py"
Cohesion: 0.06
Nodes (25): create_admin_group(), create_admin_user(), delete_admin_group(), delete_admin_user(), _ensure_email_unique(), _ensure_group_code_unique(), _ensure_group_list_number_unique(), _get_group_or_404() (+17 more)

### Community 26 - "AdminUsersPage.tsx"
Cohesion: 0.06
Nodes (45): AdminTab, AdminUsersPage(), buildCredentialsReportText(), CourseYearFilter, DeleteTarget, downloadCredentialsReportTxt(), FeedbackBanner, fetchAdminGroups() (+37 more)

### Community 27 - "course.ts"
Cohesion: 0.07
Nodes (51): PracticalModuleContext, CourseEditorPage(), deleteModuleById(), deletePracticalById(), DeleteTarget, DISCIPLINE_META, DisciplineMeta, EditorTab (+43 more)

### Community 28 - "GroupJournalPage.tsx"
Cohesion: 0.22
Nodes (15): PlagiarismBadge(), PlagiarismBadgeProps, extractApiErrorMessage(), COURSE_SLUG_BADGES, extractBlobApiErrorMessage(), fetchAcademicGroups(), fetchCourses(), fetchGroupJournal() (+7 more)

### Community 29 - "AuthContext.tsx"
Cohesion: 0.11
Nodes (29): axios@^1.7.7, API_BASE_URL, apiClient, AuthFailureListener, authFailureListeners, clearAuthTokens(), getAccessToken(), getRefreshToken() (+21 more)

### Community 32 - "environment"
Cohesion: 0.13
Nodes (17): environment, environment, APP_ENV, CORS_ORIGINS, ENABLE_RETENTION_CLEANUP_TASK, FORWARDED_ALLOW_IPS, JWT_SECRET_KEY, POSTGRES_DB (+9 more)

### Community 33 - "accdb_grader.py"
Cohesion: 0.09
Nodes (14): build_accdb_bytes(), _dedupe_names_casefold(), _encode_data_page(), _encode_msys_catalog_record(), _encode_tdef_page(), _encode_text_record(), _is_hidden_or_system_object(), _lookup_mapping_column() (+6 more)

### Community 34 - "HtmlSandbox.tsx"
Cohesion: 0.13
Nodes (18): @monaco-editor/react@4.6.0, buildDraftStorageKey(), buildStarterHtmlTemplate(), DraftSaveState, EditorColorTheme, formatDraftSavedTime(), HtmlSandbox(), HtmlSandboxProps (+10 more)

### Community 35 - "GradingError"
Cohesion: 0.09
Nodes (6): GradingError, _parse_relationship_pair_target(), _check_selector(), _normalize_selector(), _canonicalize_formula(), test_excel_course_formula_rules_have_valid_supported_expressions()

### Community 36 - "PracticalFormat"
Cohesion: 0.20
Nodes (3): GraderFactory, PracticalFormat, test_grader_factory_resolves_all_four_formats()

### Community 38 - "BaseModel"
Cohesion: 0.12
Nodes (7): AdminResetPasswordRequest, ChangePasswordRequest, ErrorResponse, ImportedStudentItem, StudentImportResponse, build_credentials_report(), test_build_credentials_report_uses_list_number_and_dynamic_variant_note()

### Community 39 - "CriterionResult"
Cohesion: 0.06
Nodes (20): BaseGrader, _attribute_value_matches(), has_meaningful_html_body(), HtmlGrader, _is_doctype_target(), _node_has_visible_content(), _normalize_text(), parse_html_document() (+12 more)

### Community 40 - "GradingReportCard.tsx"
Cohesion: 0.11
Nodes (25): COURSE_SLUG_LABELS, CriterionBreakdownItem(), CriterionFilterMode, extractFileNameFromPath(), FORMAT_META, formatDateTime(), GradingReportCard(), GradingReportCardProps (+17 more)

### Community 41 - "db_session"
Cohesion: 0.12
Nodes (5): async_client(), _create_sqlite_test_engine(), _set_sqlite_pragma(), db_session(), _replace_zip_member()

### Community 42 - "export_service.py"
Cohesion: 0.07
Nodes (21): CriterionErrorStat, GroupJournalPracticalRead, GroupJournalRead, GroupJournalRow, GroupJournalStudentCell, ManualGradeUpdateRequest, build_group_journal(), calculate_criterion_error_stats() (+13 more)

### Community 43 - "submission_service.py"
Cohesion: 0.07
Nodes (22): AcademicGroupBase, AcademicGroupCreate, AcademicGroupRead, AcademicGroupUpdate, UserUpdate, CourseCreate, CourseUpdate, ModuleCreate (+14 more)

### Community 44 - "ModuleViewPage.tsx"
Cohesion: 0.10
Nodes (34): renderInlineMarkdown(), AccessFieldDescriptor, AccessTableDescriptor, BinaryPracticalFormat, extractRetryAfterSeconds(), fetchModuleDetail(), fetchStudentPractical(), FILE_UPLOAD_FORMAT_META (+26 more)

### Community 45 - "_collect_docx_body_fragments"
Cohesion: 0.43
Nodes (3): _collect_docx_body_fragments(), _collect_docx_xml_table_texts(), _extract_docx_paragraph_xml_text()

### Community 47 - "_get_user_by_email"
Cohesion: 0.28
Nodes (4): _get_user_by_email(), test_change_password_validation_and_imported_student_flag(), test_long_cyrillic_password_create_login_and_change_without_500(), test_token_version_revokes_tokens_on_admin_reset_and_self_change()

### Community 48 - "cleanup_expired_submissions"
Cohesion: 0.09
Nodes (15): cleanup_expired_submissions(), cleanup_superseded_submission_files(), _delete_submission_file_paths_with_stats(), delete_submission_file_safely(), delete_submission_file_safely_async(), delete_submission_files_for_paths(), _inspect_submission_file_paths(), _is_postgresql_session() (+7 more)

### Community 49 - "@tanstack/react-query"
Cohesion: 0.18
Nodes (10): dependencies, lucide-react@^0.460.0, react@^18.3.1, react-dom@^18.3.1, react-router-dom@^6.28.0, @tanstack/react-query@^5.60.0, queryClient, rootElement (+2 more)

### Community 50 - "create_application"
Cohesion: 0.25
Nodes (3): _check_uploads_dir_writable(), create_application(), readiness_check()

### Community 51 - "student_import_service.py"
Cohesion: 0.07
Nodes (23): ImportSkippedItem, calculate_variant_index(), SupersededCleanupSummary, build_generated_email(), _classify_header_cell(), _clean_whitespace(), _detect_docx_header_columns(), _DocxColumnMap (+15 more)

### Community 55 - "_get_module_with_questions"
Cohesion: 0.17
Nodes (8): _build_answers_for_score(), _get_module_with_questions(), _get_user_by_email(), test_excel_q42_imported_in_module_8_with_media_and_dry_run(), test_quiz_cooldown_zero_disables_wait_and_negative_config_rejected(), test_quiz_pass_threshold_setting_controls_passed_flag(), test_quiz_retry_cooldown_blocks_immediate_retry_and_unlocks_after_window(), test_quiz_submit_rejects_incomplete_duplicate_foreign_and_invalid_answers()

### Community 57 - "DocxGrader"
Cohesion: 0.05
Nodes (4): DocxGrader, _format_number(), test_docx_grader_inherits_font_from_base_style_chain_and_doc_defaults(), test_docx_grader_table_exists_supports_rxc_and_rows_cols_conditions()

### Community 58 - "decode_token"
Cohesion: 0.16
Nodes (5): decode_token(), test_hash_and_verify_password_async_offload_to_worker_thread(), _recording_hash(), _recording_verify(), test_login_rate_limiting_blocks_after_n_failures_and_resets_on_success()

### Community 59 - "_extract_html_fingerprint"
Cohesion: 0.13
Nodes (9): compute_text_shingles(), _extract_css_property_blocks(), _extract_html_fingerprint(), _extract_html_visible_text(), _walk(), _normalize_css_declarations(), _serialize_html_dom_structure(), _walk() (+1 more)

### Community 60 - "_build_submission_download_names"
Cohesion: 0.22
Nodes (5): build_content_disposition(), _build_submission_download_names(), _sanitize_ascii_token(), _sanitize_utf8_token(), _strip_apostrophes()

### Community 61 - "test_graders.py"
Cohesion: 0.06
Nodes (15): build_seed_bundle(), build_sample_xlsx(), test_full_course_json_bundle_validation(), _strip_zip_member(), test_accdb_grader_inspects_queries_forms_reports_relationships_and_mdb_export_csv(), test_docx_grader_detects_formatting_violations_and_corrupt_files(), test_docx_grader_evaluates_valid_document(), test_docx_grader_resolves_placeholders_in_target_and_expected() (+7 more)

### Community 62 - "list_my_submissions"
Cohesion: 0.18
Nodes (5): download_submission_file(), get_submission_detail(), list_my_submissions(), list_submissions(), update_submission_grade()

### Community 66 - "services"
Cohesion: 0.20
Nodes (9): driver, internal, networks, edge, internal, services, volumes, postgres_data (+1 more)

### Community 69 - "Settings"
Cohesion: 0.22
Nodes (3): get_settings(), Settings, test_settings_production_rejects_default_or_short_jwt_secret()

### Community 70 - "test_course_content.py"
Cohesion: 0.07
Nodes (30): Course, CourseSlug, _enum_values(), Module, Practical, QuizQuestion, _extract_needs_rules_review(), _load_course_from_json() (+22 more)

### Community 73 - "math"
Cohesion: 0.10
Nodes (17): _apply_binary_operator(), _coerce_formula_bool(), _coerce_formula_number(), _collect_logical_values(), _collect_numeric_values(), _eval_countif(), _eval_sumif(), _eval_vlookup() (+9 more)

### Community 76 - "ExportService"
Cohesion: 0.12
Nodes (3): ExportedDocument, ExportService, GroupJournalBundle

### Community 80 - "do_run_migrations"
Cohesion: 0.29
Nodes (3): do_run_migrations(), run_async_migrations(), run_migrations_online()

### Community 84 - "xlsx_grader.py"
Cohesion: 0.08
Nodes (14): _BoolNode, _CellRefNode, _count_non_empty_values(), _EmptyArgNode, _FuncCallNode, _has_balanced_formula_delimiters(), _is_wrapped_in_parens(), _normalize_bare_function_name() (+6 more)

### Community 90 - "_FormulaParser"
Cohesion: 0.36
Nodes (4): _BinaryOpNode, _FormulaParser, _Token, _UnaryOpNode

### Community 92 - "test_read_upload_file_limited_stops_reading_chunks_early"
Cohesion: 0.50
Nodes (3): test_read_upload_file_limited_stops_reading_chunks_early(), __init__(), read()

### Community 95 - "SubmissionService"
Cohesion: 0.08
Nodes (8): PlagiarismCheckResult, _is_submission_file_available(), _resolve_existing_submission_file(), _save_uploaded_file(), serialize_submission(), SubmissionDownloadPayload, SubmissionService, _unlink_file_quietly()

### Community 99 - "_SeedCoursePayload"
Cohesion: 0.15
Nodes (4): _SeedCoursePayload, _SeedModulePayload, _SeedPracticalPayload, _SeedQuizQuestionPayload

### Community 100 - "metadata.py"
Cohesion: 0.07
Nodes (24): InvalidFileFormatError, _canonicalize_xlsx_formula(), compute_bytes_sha256(), compute_code_sha256(), compute_file_sha256(), compute_shingle_jaccard(), compute_submission_hash(), _extract_accdb_fingerprint() (+16 more)

### Community 104 - "get_db"
Cohesion: 0.08
Nodes (31): ensure_course_owner_or_admin(), get_current_user(), role_checker(), _collect_practical_submission_file_paths(), create_course(), create_module(), create_quiz_question(), delete_module() (+23 more)

### Community 108 - "frontend"
Cohesion: 0.25
Nodes (8): condition, backend, container_name, depends_on, networks, ports, restart, frontend

### Community 110 - "backend"
Cohesion: 0.25
Nodes (8): container_name, depends_on, networks, restart, volumes, condition, db, backend

### Community 114 - ".import_students"
Cohesion: 0.10
Nodes (5): import_admin_students(), _build_too_large_exception(), format_size_limit_mb(), read_upload_file_limited(), StudentImportService

### Community 122 - "Tag"
Cohesion: 0.38
Nodes (3): _find_tag_attr_key(), _get_tag_attribute_str(), _tag_has_attribute()

### Community 141 - "healthcheck"
Cohesion: 0.48
Nodes (7): healthcheck, healthcheck, interval, retries, start_period, test, timeout

### Community 145 - "build"
Cohesion: 0.40
Nodes (6): VITE_API_BASE_URL, build, args, context, dockerfile, build

### Community 147 - "db"
Cohesion: 0.33
Nodes (6): container_name, image, networks, restart, volumes, db

### Community 157 - "test_postgresql_advisory_lock_skips_when_already_held"
Cohesion: 0.14
Nodes (3): test_health_ready_returns_200_when_healthy_and_503_on_uploads_or_db_failure(), test_postgresql_advisory_lock_skips_when_already_held(), test_uploads_dir_relative_path_is_anchored_to_backend_directory()

## Knowledge Gaps
- **1 isolated node(s):** `edu-auto-grader-backend`
  These have ≤1 connection - possible missing edges. (Counts symbols only; 1093 node(s) total have ≤1 connection when file, concept and rationale nodes are included.)
- **109 thin communities (<3 nodes) omitted from report** — run `graphify query` to explore isolated nodes.

## Suggested Questions
_Questions this graph is uniquely positioned to answer:_

- **Why does `GradingRule` connect `CriterionResult` to `accdb_grader.py`, `test_all_course_variants_resolve_rule_placeholders_without_leftovers`, `GradingError`, `AccdbGrader`, `_SeedCoursePayload`, `test_course_content.py`, `submission_service.py`, `get_db`, `submission_service.py`, `xlsx_grader.py`, `DocxGrader`, `.update_grading_rules`, `test_graders.py`, `XlsxGrader`, `SubmissionService`?**
  _High betweenness centrality (0.061) - this node is a cross-community bridge._
- **Are the 20 inferred relationships involving `GradingRule` (e.g. with `_serialize_practical_teacher()` and `AccdbGrader`) actually correct?**
  _`GradingRule` has 20 INFERRED edges - model-reasoned connections that need verification._
- **What connects `edu-auto-grader-backend` to the rest of the system?**
  _1 weakly-connected nodes found - possible missing edges._
- **Should `QuizService` be split into smaller, more focused modules?**
  _Cohesion score 0.12 - nodes in this community are weakly interconnected._
- **Why does `User` connect `submission_service.py` to `QuizService`, `test_course_content.py`, `.execute`, `get_db`, `export_service.py`, `_get_user_by_email`, `ExportService`, `_get_user_by_email`, `make_auth_headers`, `.import_students`, `student_import_service.py`, `login`, `_get_module_with_questions`, `admin.py`, `.update_grading_rules`, `test_graders.py`, `SubmissionService`?**
  _High betweenness centrality (0.035) - this node is a cross-community bridge._
- **Are the 9 inferred relationships involving `User` (e.g. with `ensure_course_owner_or_admin()` and `get_current_user()`) actually correct?**
  _`User` has 9 INFERRED edges - model-reasoned connections that need verification._
- **Should `postgres` be split into smaller, more focused modules?**
  _Cohesion score 0.10526315789473684 - nodes in this community are weakly interconnected._