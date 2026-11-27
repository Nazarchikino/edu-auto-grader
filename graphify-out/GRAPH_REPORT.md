# Graph Report - edu-auto-grader  (2026-11-27)

## Corpus Check
- 108 files · ~324,549 words
- Verdict: corpus is large enough that graph structure adds value.
- Unclassified: 14 file(s) not represented in the graph (top: (none) 9, .example 1, .ini 1)

## Summary
- 2491 nodes · 7368 edges · 92 communities (67 shown, 25 thin omitted)
- Extraction: 87% EXTRACTED · 13% INFERRED · 0% AMBIGUOUS · INFERRED: 931 edges (avg confidence: 0.93)
- Token cost: 0 input · 0 output

## Graph Freshness
- Built from commit: `d201003b`
- Run `git rev-parse HEAD` and compare to check if the graph is stale.
- Run `graphify update .` after code changes (no API cost).

## Community Hubs (Navigation)
- QuizService
- postgres
- compilerOptions
- test_course_content.py
- practicals.py
- env
- analytics.py
- schemas/__init__.py
- MarkdownRenderer.tsx
- vite-env.d.ts
- test_delete_admin_user_removes_student_submissions_and_disk_files
- XlsxGrader
- ExportService
- v1/auth.py
- make_auth_headers
- test_graders.py
- edu-auto-grader-backend
- package.json
- App.tsx
- admin.py
- AdminUsersPage.tsx
- course.ts
- GroupJournalPage.tsx
- AuthContext.tsx
- XlsxGrader
- test_quiz_security.py
- environment
- list_my_submissions
- HtmlSandbox.tsx
- test_auth_security.py
- User
- xlsx_grader.py
- RuleBuilderPage.tsx
- test_postgresql_advisory_lock_skips_when_already_held
- GradingReportCard.tsx
- db_session
- test_export_service.py
- _sanitize_ascii_token
- ModuleViewPage.tsx
- _collect_docx_body_fragments
- SlidingWindowRateLimiter
- 0002_restrict_course_year_to_4.py
- retention_service.py
- test_export_service.py
- student_import_service.py
- _FormulaEvalError
- test_cleanup_superseded_respects_24h_grace_window
- db
- env.py
- _format_student_placeholder_value
- DocxGrader
- 0001_initial_schema.py
- _extract_html_fingerprint
- 0003_add_user_auth_security_fields.py
- submission_service.py
- _find_tag_attr_key
- SqliteAsyncSessionAdapter
- 0005_practical_rules_review.py
- 0006_practical_template_file.py
- test_read_upload_file_limited_stops_reading_chunks_early
- .__call__
- _excel_wildcard_to_regex
- @tanstack/react-query
- AccdbGrader
- GradingRule
- config.py
- UserRole
- export_service.py
- upload_utils.py
- _tokenize_formula
- _FormulaParser
- Decimal
- _compile_jsonb_for_sqlite
- conftest.py
- _SeedCoursePayload
- metadata.py
- courses.py
- frontend
- backend
- healthcheck
- docker-compose.prod.yml
- _set_xlsx_text_cell
- backup.sh
- restore.sh

## God Nodes (most connected - your core abstractions)
1. `GradingRule` - 110 edges
2. `SqliteAsyncSessionAdapter` - 102 edges
3. `User` - 92 edges
4. `CourseSlug` - 90 edges
5. `DomainError` - 85 edges
6. `Module` - 65 edges
7. `make_auth_headers()` - 65 edges
8. `Practical` - 63 edges
9. `GradingError` - 62 edges
10. `PracticalFormat` - 61 edges

## Surprising Connections (you probably didn't know these)
- `create_course()` --uses--> `CourseCreate`  [INFERRED]
  backend/app/api/v1/courses.py → backend/app/schemas/course.py
- `CourseCreate` --uses--> `CourseSlug`  [INFERRED]
  backend/app/schemas/course.py → backend/app/models/course.py
- `upload_course_media()` --uses--> `CourseMediaUploadRead`  [INFERRED]
  backend/app/api/v1/courses.py → backend/app/schemas/course.py
- `update_course()` --uses--> `CourseUpdate`  [INFERRED]
  backend/app/api/v1/courses.py → backend/app/schemas/course.py
- `create_module()` --uses--> `ModuleCreate`  [INFERRED]
  backend/app/api/v1/courses.py → backend/app/schemas/course.py

## Import Cycles
- None detected.

## Communities (92 total, 25 thin omitted)

### Community 0 - "QuizService"
Cohesion: 0.05
Nodes (27): _build_module_detail_read(), QuizNotPassedError, CourseCreate, CourseMediaUploadRead, CourseUpdate, GradingCriterionPreviewRead, ModuleCreate, ModuleDetailRead (+19 more)

### Community 1 - "postgres"
Cohesion: 0.11
Nodes (18): POSTGRES_DB, POSTGRES_PASSWORD, POSTGRES_USER, interval, retries, test, timeout, container_name (+10 more)

### Community 2 - "compilerOptions"
Cohesion: 0.10
Nodes (20): compilerOptions, allowImportingTsExtensions, isolatedModules, jsx, lib, module, moduleDetection, moduleResolution (+12 more)

### Community 3 - "test_course_content.py"
Cohesion: 0.06
Nodes (33): Base, Course, Module, Practical, QuizQuestion, Submission, build_seed_bundle(), _extract_needs_rules_review() (+25 more)

### Community 4 - "practicals.py"
Cohesion: 0.07
Nodes (20): delete_practical_template(), download_practical_template(), dry_run_practical_work(), _extract_dry_run_payload(), _extract_submission_payload(), ExtractedDryRunPayload, ExtractedSubmissionPayload, _load_practical_with_course_or_404() (+12 more)

### Community 5 - "env"
Cohesion: 0.06
Nodes (38): env, name, runs-on, services, steps, concurrency, cancel-in-progress, group (+30 more)

### Community 6 - "analytics.py"
Cohesion: 0.16
Nodes (4): export_group_journal(), get_group_journal(), list_academic_groups(), _parse_export_format()

### Community 7 - "schemas/__init__.py"
Cohesion: 0.08
Nodes (17): AcademicGroupBase, AcademicGroupCreate, AcademicGroupRead, AcademicGroupUpdate, ChangePasswordRequest, ErrorResponse, ImportedStudentItem, ImportSkippedItem (+9 more)

### Community 8 - "MarkdownRenderer.tsx"
Cohesion: 0.12
Nodes (31): dedentBlockLines(), findClosingDoubleStar(), findClosingParen(), findClosingSingleStar(), findMatchingBracket(), getAlignmentClass(), getLineIndent(), hasUnsafeControlChars() (+23 more)

### Community 11 - "test_delete_admin_user_removes_student_submissions_and_disk_files"
Cohesion: 0.09
Nodes (19): AcademicGroup, calculate_variant_index(), make_auth_headers(), _build_college_import_docx(), _get_user_by_email(), test_academic_group_course_year_restricted_to_1_through_4(), test_admin_academic_groups_crud_and_detachment(), test_admin_bulk_import_docx_sorts_ukrainian_alphabet_and_assigns_variants() (+11 more)

### Community 13 - "XlsxGrader"
Cohesion: 0.10
Nodes (3): XlsxGrader, test_xlsx_grader_evaluates_formulas_values_and_charts(), test_xlsx_grader_rejects_static_value_instead_of_formula_and_missing_chart()

### Community 14 - "ExportService"
Cohesion: 0.13
Nodes (3): ExportFormat, ExportedDocument, ExportService

### Community 15 - "v1/auth.py"
Cohesion: 0.07
Nodes (15): get_current_user(), change_password(), _extract_client_ip(), login(), read_current_user(), refresh_tokens(), create_access_token(), create_refresh_token() (+7 more)

### Community 16 - "make_auth_headers"
Cohesion: 0.08
Nodes (27): CourseSlug, build_sample_docx(), _replace_zip_member(), rewrite_openxml_core_metadata(), _get_course_module_and_practical(), _get_user_by_email(), _grant_quiz_pass(), test_antiplagiarism_api_html_structural_match_and_classroom_template_clean() (+19 more)

### Community 17 - "test_graders.py"
Cohesion: 0.04
Nodes (27): format_student_criterion_description(), _attribute_value_matches(), has_meaningful_html_body(), _node_has_visible_content(), _normalize_text(), _parse_text_match_expected(), _strip_quotes(), _canonicalize_formula() (+19 more)

### Community 23 - "package.json"
Cohesion: 0.07
Nodes (39): devDependencies, autoprefixer@^10.4.20, eslint@^9.15.0, @eslint/js@^9.15.0, eslint-plugin-react-hooks@^5.0.0, eslint-plugin-react-refresh@^0.4.14, globals@^15.12.0, postcss@^8.4.49 (+31 more)

### Community 24 - "App.tsx"
Cohesion: 0.11
Nodes (35): App(), ProtectedAppLayout(), RoleHomeRedirect(), ChangePasswordModal(), ChangePasswordModalProps, Navbar(), NavbarProps, resolvePageTitle() (+27 more)

### Community 25 - "admin.py"
Cohesion: 0.07
Nodes (24): create_admin_group(), create_admin_user(), delete_admin_group(), delete_admin_user(), _ensure_email_unique(), _ensure_group_code_unique(), _ensure_group_list_number_unique(), _get_group_or_404() (+16 more)

### Community 26 - "AdminUsersPage.tsx"
Cohesion: 0.06
Nodes (48): AdminTab, AdminUsersPage(), buildCredentialsReportText(), CourseYearFilter, DeleteTarget, downloadCredentialsReportTxt(), FeedbackBanner, fetchAdminGroups() (+40 more)

### Community 27 - "course.ts"
Cohesion: 0.10
Nodes (36): ALLOWED_MEDIA_IMAGE_EXTENSIONS, CourseEditorPage(), deleteModuleById(), deletePracticalById(), DeleteTarget, DISCIPLINE_META, DisciplineMeta, EditorTab (+28 more)

### Community 28 - "GroupJournalPage.tsx"
Cohesion: 0.20
Nodes (17): PlagiarismBadge(), PlagiarismBadgeProps, extractApiErrorMessage(), COURSE_SLUG_BADGES, extractBlobApiErrorMessage(), fetchAcademicGroups(), fetchCourses(), fetchGroupJournal() (+9 more)

### Community 29 - "AuthContext.tsx"
Cohesion: 0.13
Nodes (26): API_BASE_URL, apiClient, AuthFailureListener, authFailureListeners, clearAuthTokens(), getAccessToken(), getRefreshToken(), notifyAuthFailure() (+18 more)

### Community 30 - "XlsxGrader"
Cohesion: 0.13
Nodes (3): _RangeValue, _split_cell_coord(), _eval()

### Community 31 - "test_quiz_security.py"
Cohesion: 0.18
Nodes (8): _build_answers_for_score(), _get_module_with_questions(), _get_user_by_email(), test_excel_q42_imported_in_module_8_with_media_and_dry_run(), test_quiz_cooldown_zero_disables_wait_and_negative_config_rejected(), test_quiz_pass_threshold_setting_controls_passed_flag(), test_quiz_retry_cooldown_blocks_immediate_retry_and_unlocks_after_window(), test_quiz_submit_rejects_incomplete_duplicate_foreign_and_invalid_answers()

### Community 32 - "environment"
Cohesion: 0.12
Nodes (18): environment, environment, APP_ENV, CORS_ORIGINS, COURSE_MEDIA_DIR, ENABLE_RETENTION_CLEANUP_TASK, FORWARDED_ALLOW_IPS, JWT_SECRET_KEY (+10 more)

### Community 33 - "list_my_submissions"
Cohesion: 0.19
Nodes (5): download_submission_file(), get_submission_detail(), list_my_submissions(), list_submissions(), update_submission_grade()

### Community 34 - "HtmlSandbox.tsx"
Cohesion: 0.13
Nodes (18): @monaco-editor/react@4.6.0, buildDraftStorageKey(), buildStarterHtmlTemplate(), DraftSaveState, EditorColorTheme, formatDraftSavedTime(), HtmlSandbox(), HtmlSandboxProps (+10 more)

### Community 35 - "test_auth_security.py"
Cohesion: 0.13
Nodes (8): build_login_rate_limit_key(), verify_password(), verify_password_async(), test_hash_and_verify_password_async_offload_to_worker_thread(), _recording_hash(), _recording_verify(), test_login_rate_limiting_blocks_after_n_failures_and_resets_on_success(), test_password_hashing_supports_long_cyrillic_and_legacy_bcrypt_hashes()

### Community 36 - "User"
Cohesion: 0.07
Nodes (23): hash_password(), QuizAttempt, User, _create_other_teacher(), _get_course_by_slug(), _get_user_by_email(), test_patch_quiz_question_owner_validation_and_rbac(), test_practical_template_lifecycle_student_download_unmodified_reject_and_cleanup() (+15 more)

### Community 37 - "xlsx_grader.py"
Cohesion: 0.09
Nodes (13): _BoolNode, _CellRefNode, _count_non_empty_values(), _EmptyArgNode, _format_cell_value(), _FuncCallNode, _has_balanced_formula_delimiters(), _is_wrapped_in_parens() (+5 more)

### Community 38 - "RuleBuilderPage.tsx"
Cohesion: 0.11
Nodes (27): DryRunResultPanel(), DryRunResultPanelProps, formatPoints(), BinaryFormat, DRY_RUN_FILE_ACCEPT, fetchCourses(), fetchPracticalTeacher(), FORMAT_BADGE_CONFIG (+19 more)

### Community 39 - "test_postgresql_advisory_lock_skips_when_already_held"
Cohesion: 0.14
Nodes (3): test_health_ready_returns_200_when_healthy_and_503_on_uploads_or_db_failure(), test_postgresql_advisory_lock_skips_when_already_held(), test_uploads_dir_relative_path_is_anchored_to_backend_directory()

### Community 40 - "GradingReportCard.tsx"
Cohesion: 0.10
Nodes (29): COURSE_SLUG_LABELS, CriterionBreakdownItem(), CriterionFilterMode, extractFileNameFromPath(), FORMAT_META, formatDateTime(), GradingReportCard(), GradingReportCardProps (+21 more)

### Community 41 - "db_session"
Cohesion: 0.15
Nodes (4): async_client(), _create_sqlite_test_engine(), _set_sqlite_pragma(), db_session()

### Community 42 - "test_export_service.py"
Cohesion: 0.11
Nodes (17): CriterionErrorStat, GroupJournalPracticalRead, GroupJournalRead, GroupJournalRow, GroupJournalStudentCell, HtmlDryRunRequest, build_group_journal(), PracticalColumnInfo (+9 more)

### Community 43 - "_sanitize_ascii_token"
Cohesion: 0.33
Nodes (3): _sanitize_ascii_token(), _sanitize_utf8_token(), _strip_apostrophes()

### Community 44 - "ModuleViewPage.tsx"
Cohesion: 0.07
Nodes (47): AccessFieldDescriptor, AccessTableDescriptor, ALIGNMENT_DISPLAY_LABELS, BinaryPracticalFormat, dryRunFilePractical(), dryRunHtmlPractical(), extractBlobApiErrorMessage(), extractRetryAfterSeconds() (+39 more)

### Community 45 - "_collect_docx_body_fragments"
Cohesion: 0.31
Nodes (4): _collect_docx_body_fragments(), _collect_docx_xml_table_texts(), _extract_docx_paragraph_xml_text(), _find_xml_text()

### Community 48 - "retention_service.py"
Cohesion: 0.09
Nodes (17): main(), cleanup_expired_submissions(), cleanup_superseded_submission_files(), _delete_submission_file_paths_with_stats(), delete_submission_file_safely(), delete_submission_files_for_paths(), _inspect_submission_file_paths(), _is_postgresql_session() (+9 more)

### Community 49 - "test_export_service.py"
Cohesion: 0.21
Nodes (8): _configure_pdf_font(), _fit_pdf_text(), _format_pdf_score(), _prepare_pdf_text(), render_group_journal_pdf(), _draw_page_header(), _draw_table_header(), test_pdf_compact_score_formatting_and_text_fitting()

### Community 51 - "student_import_service.py"
Cohesion: 0.07
Nodes (21): build_credentials_report(), build_generated_email(), _classify_header_cell(), _clean_whitespace(), _detect_docx_header_columns(), _DocxColumnMap, _encode_ukrainian_word(), _get_cell_value() (+13 more)

### Community 52 - "_FormulaEvalError"
Cohesion: 0.10
Nodes (17): _apply_binary_operator(), _coerce_formula_bool(), _coerce_formula_number(), _collect_logical_values(), _collect_numeric_values(), _eval_countif(), _eval_sumif(), _eval_vlookup() (+9 more)

### Community 54 - "db"
Cohesion: 0.33
Nodes (6): container_name, image, networks, restart, volumes, db

### Community 55 - "env.py"
Cohesion: 0.18
Nodes (4): do_run_migrations(), run_async_migrations(), run_migrations_offline(), run_migrations_online()

### Community 56 - "_format_student_placeholder_value"
Cohesion: 0.29
Nodes (4): _format_margin_measurement(), _format_margins_value(), _format_student_placeholder_value(), _format_uk_decimal()

### Community 57 - "DocxGrader"
Cohesion: 0.05
Nodes (4): DocxGrader, _format_number(), CriterionResult, test_docx_grader_inherits_font_from_base_style_chain_and_doc_defaults()

### Community 59 - "_extract_html_fingerprint"
Cohesion: 0.17
Nodes (6): _extract_css_property_blocks(), _extract_html_visible_text(), _walk(), _normalize_css_declarations(), _serialize_html_dom_structure(), _walk()

### Community 62 - "submission_service.py"
Cohesion: 0.05
Nodes (18): InvalidFileFormatError, PlagiarismDetectedError, GraderFactory, PracticalFormat, GradingReport, GradingRulesUpdateRequest, DryRunGradingResponse, ManualGradeUpdateRequest (+10 more)

### Community 63 - "_find_tag_attr_key"
Cohesion: 0.38
Nodes (3): _find_tag_attr_key(), _get_tag_attribute_str(), _tag_has_attribute()

### Community 64 - "SqliteAsyncSessionAdapter"
Cohesion: 0.14
Nodes (11): build_sample_xlsx(), SqliteAsyncSessionAdapter, _count_quiz_attempts(), _count_submissions(), _get_module_and_practical_by_order(), _get_user_by_email(), _list_uploaded_files(), test_dry_run_docx_xlsx_and_html_success_with_zero_side_effects() (+3 more)

### Community 67 - "test_read_upload_file_limited_stops_reading_chunks_early"
Cohesion: 0.50
Nodes (3): test_read_upload_file_limited_stops_reading_chunks_early(), __init__(), read()

### Community 75 - "@tanstack/react-query"
Cohesion: 0.17
Nodes (11): dependencies, axios@^1.7.7, lucide-react@^0.460.0, react@^18.3.1, react-dom@^18.3.1, react-router-dom@^6.28.0, @tanstack/react-query@^5.60.0, queryClient (+3 more)

### Community 77 - "AccdbGrader"
Cohesion: 0.03
Nodes (31): AccdbColumnSchema, AccdbDatabaseSchema, AccdbGrader, AccdbObjectsCatalog, AccdbRelationshipSchema, AccdbTableSchema, build_accdb_bytes(), _dedupe_names_casefold() (+23 more)

### Community 78 - "GradingRule"
Cohesion: 0.05
Nodes (14): GradingError, _parse_relationship_pair_target(), BaseGrader, _replace(), HtmlGrader, _check_selector(), _is_doctype_target(), _normalize_selector() (+6 more)

### Community 80 - "config.py"
Cohesion: 0.11
Nodes (4): get_settings(), _resolve_backend_path(), Settings, test_settings_production_rejects_default_or_short_jwt_secret()

### Community 82 - "UserRole"
Cohesion: 0.10
Nodes (8): require_role(), role_checker(), _check_uploads_dir_writable(), create_application(), readiness_check(), lifespan(), _enum_values(), UserRole

### Community 85 - "export_service.py"
Cohesion: 0.11
Nodes (8): _build_template_content_disposition(), build_content_disposition(), calculate_criterion_error_stats(), GroupJournalBundle, _normalize_utc_timestamp(), _RuleStatAccumulator, _sanitize_filename_token(), _transliterate_to_ascii()

### Community 90 - "_FormulaParser"
Cohesion: 0.36
Nodes (4): _BinaryOpNode, _FormulaParser, _Token, _UnaryOpNode

### Community 97 - "conftest.py"
Cohesion: 0.11
Nodes (5): downgrade(), upgrade(), _enum_values(), _fast_seed_hash_password(), test_media_courses_responses_include_security_headers()

### Community 99 - "_SeedCoursePayload"
Cohesion: 0.18
Nodes (4): _SeedCoursePayload, _SeedModulePayload, _SeedPracticalPayload, _SeedQuizQuestionPayload

### Community 100 - "metadata.py"
Cohesion: 0.04
Nodes (42): _canonicalize_xlsx_formula(), check_submission_plagiarism(), _clean_optional_str(), _coerce_metadata(), compute_bytes_sha256(), compute_code_sha256(), compute_file_sha256(), compute_shingle_jaccard() (+34 more)

### Community 104 - "courses.py"
Cohesion: 0.07
Nodes (36): ensure_course_owner_or_admin(), _collect_practical_submission_file_paths(), create_course(), create_module(), create_quiz_question(), delete_module(), delete_practical(), delete_quiz_question() (+28 more)

### Community 108 - "frontend"
Cohesion: 0.25
Nodes (8): condition, backend, container_name, depends_on, networks, ports, restart, frontend

### Community 110 - "backend"
Cohesion: 0.15
Nodes (14): VITE_API_BASE_URL, build, container_name, depends_on, networks, restart, volumes, args (+6 more)

### Community 141 - "healthcheck"
Cohesion: 0.48
Nodes (7): healthcheck, healthcheck, interval, retries, start_period, test, timeout

### Community 147 - "docker-compose.prod.yml"
Cohesion: 0.18
Nodes (10): driver, internal, name, networks, edge, internal, services, volumes (+2 more)

### Community 168 - "_set_xlsx_text_cell"
Cohesion: 0.15
Nodes (4): _auto_adjust_worksheet_columns(), sanitize_spreadsheet_text(), _set_xlsx_text_cell(), test_sanitize_spreadsheet_text_escapes_all_formula_prefixes()

## Knowledge Gaps
- **1 isolated node(s):** `edu-auto-grader-backend`
  These have ≤1 connection - possible missing edges. (Counts symbols only; 1085 node(s) total have ≤1 connection when file, concept and rationale nodes are included.)
- **25 thin communities (<3 nodes) omitted from report** — run `graphify query` to explore isolated nodes.

## Suggested Questions
_Questions this graph is uniquely positioned to answer:_

- **Why does `GradingRule` connect `GradingRule` to `QuizService`, `test_course_content.py`, `practicals.py`, `xlsx_grader.py`, `metadata.py`, `schemas/__init__.py`, `courses.py`, `_SeedCoursePayload`, `test_export_service.py`, `AccdbGrader`, `XlsxGrader`, `retention_service.py`, `test_graders.py`, `DocxGrader`, `submission_service.py`?**
  _High betweenness centrality (0.058) - this node is a cross-community bridge._
- **Are the 30 inferred relationships involving `GradingRule` (e.g. with `_serialize_practical_teacher()` and `_extract_dry_run_payload()`) actually correct?**
  _`GradingRule` has 30 INFERRED edges - model-reasoned connections that need verification._
- **What connects `edu-auto-grader-backend` to the rest of the system?**
  _1 weakly-connected nodes found - possible missing edges._
- **Should `QuizService` be split into smaller, more focused modules?**
  _Cohesion score 0.04998148833765272 - nodes in this community are weakly interconnected._
- **Why does `DomainError` connect `courses.py` to `QuizService`, `practicals.py`, `analytics.py`, `schemas/__init__.py`, `GradingRule`, `v1/auth.py`, `ExportService`, `test_graders.py`, `UserRole`, `PlagiarismDetectedError`, `student_import_service.py`, `export_service.py`, `admin.py`, `submission_service.py`?**
  _High betweenness centrality (0.037) - this node is a cross-community bridge._
- **Are the 78 inferred relationships involving `SqliteAsyncSessionAdapter` (e.g. with `_get_user_by_email()` and `test_academic_group_course_year_restricted_to_1_through_4()`) actually correct?**
  _`SqliteAsyncSessionAdapter` has 78 INFERRED edges - model-reasoned connections that need verification._
- **Should `postgres` be split into smaller, more focused modules?**
  _Cohesion score 0.10526315789473684 - nodes in this community are weakly interconnected._