# Graph Report - edu-auto-grader  (2026-11-27)

## Corpus Check
- 108 files · ~324,468 words
- Verdict: corpus is large enough that graph structure adds value.
- Unclassified: 14 file(s) not represented in the graph (top: (none) 9, .example 1, .ini 1)

## Summary
- 2514 nodes · 7304 edges · 101 communities (69 shown, 32 thin omitted)
- Extraction: 89% EXTRACTED · 11% INFERRED · 0% AMBIGUOUS · INFERRED: 815 edges (avg confidence: 0.92)
- Token cost: 0 input · 0 output

## Graph Freshness
- Built from commit: `d1c90631`
- Run `git rev-parse HEAD` and compare to check if the graph is stale.
- Run `graphify update .` after code changes (no API cost).

## Community Hubs (Navigation)
- QuizService
- postgres
- compilerOptions
- User
- upload_practical_template
- env
- analytics.py
- metadata.py
- MarkdownRenderer.tsx
- vite-env.d.ts
- test_delete_admin_user_removes_student_submissions_and_disk_files
- serialize_submission
- ExportService
- v1/auth.py
- make_auth_headers
- html_grader.py
- edu-auto-grader-backend
- submission.py
- package.json
- App.tsx
- admin.py
- AdminUsersPage.tsx
- course.ts
- GroupJournalPage.tsx
- AuthContext.tsx
- test_quiz_security.py
- environment
- list_my_submissions
- HtmlSandbox.tsx
- test_change_password_validation_and_imported_student_flag
- test_delete_module_renumbers_cleanly_under_unique_constraint_with_reverse_uuids
- xlsx_grader.py
- RuleBuilderPage.tsx
- submit_practical_work
- GradingReportCard.tsx
- db_session
- GroupJournalRead
- submission_service.py
- ModuleViewPage.tsx
- _collect_docx_body_fragments
- SlidingWindowRateLimiter
- 0002_restrict_course_year_to_4.py
- retention_service.py
- test_export_service.py
- PlagiarismDetectedError
- student_import_service.py
- math
- test_cleanup_superseded_respects_24h_grace_window
- db
- _resolve_existing_template_file
- DocxGrader
- _extract_html_fingerprint
- SubmissionService
- GradingRule
- SqliteAsyncSessionAdapter
- _sanitize_filename_token
- test_read_upload_file_limited_stops_reading_chunks_early
- .__call__
- _resolve_backend_path
- seed.py
- ._eval_function_call
- @tanstack/react-query
- AccdbGrader
- GradingError
- config.py
- practicals.py
- export_service.py
- read_upload_file_limited
- _FormulaEvalError
- _FormulaParser
- Decimal
- _compile_jsonb_for_sqlite
- _SeedCoursePayload
- test_graders.py
- courses.py
- frontend
- backend
- healthcheck
- docker-compose.prod.yml
- _set_xlsx_text_cell
- backup.sh
- restore.sh

## God Nodes (most connected - your core abstractions)
1. `SqliteAsyncSessionAdapter` - 102 edges
2. `GradingRule` - 93 edges
3. `User` - 87 edges
4. `CourseSlug` - 83 edges
5. `DomainError` - 81 edges
6. `Module` - 65 edges
7. `make_auth_headers()` - 65 edges
8. `Practical` - 63 edges
9. `GradingError` - 61 edges
10. `PracticalFormat` - 60 edges

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

## Communities (101 total, 32 thin omitted)

### Community 0 - "QuizService"
Cohesion: 0.09
Nodes (11): _build_module_detail_read(), QuizNotPassedError, PracticalStudentRead, QuizSubmitRequest, QuizSubmitResponse, build_student_grading_criteria(), _ensure_utc(), format_cooldown_remaining() (+3 more)

### Community 1 - "postgres"
Cohesion: 0.11
Nodes (18): POSTGRES_DB, POSTGRES_PASSWORD, POSTGRES_USER, interval, retries, test, timeout, container_name (+10 more)

### Community 2 - "compilerOptions"
Cohesion: 0.10
Nodes (20): compilerOptions, allowImportingTsExtensions, isolatedModules, jsx, lib, module, moduleDetection, moduleResolution (+12 more)

### Community 3 - "User"
Cohesion: 0.09
Nodes (26): Base, Course, Module, Practical, QuizQuestion, QuizAttempt, Submission, User (+18 more)

### Community 4 - "upload_practical_template"
Cohesion: 0.11
Nodes (8): delete_practical_template(), download_practical_template(), dry_run_practical_work(), _load_practical_with_course_or_404(), _resolve_practical_upload_limit(), _sanitize_template_display_name(), update_practical_grading_rules(), upload_practical_template()

### Community 5 - "env"
Cohesion: 0.06
Nodes (38): env, name, runs-on, services, steps, concurrency, cancel-in-progress, group (+30 more)

### Community 6 - "analytics.py"
Cohesion: 0.23
Nodes (3): export_group_journal(), get_group_journal(), list_academic_groups()

### Community 7 - "metadata.py"
Cohesion: 0.07
Nodes (20): _canonicalize_xlsx_formula(), compute_bytes_sha256(), compute_code_sha256(), compute_submission_hash(), compute_text_shingles(), _extract_accdb_fingerprint(), _extract_accdb_table_via_mdb_export(), _extract_accdb_tables_via_mdbtools() (+12 more)

### Community 8 - "MarkdownRenderer.tsx"
Cohesion: 0.12
Nodes (31): dedentBlockLines(), findClosingDoubleStar(), findClosingParen(), findClosingSingleStar(), findMatchingBracket(), getAlignmentClass(), getLineIndent(), hasUnsafeControlChars() (+23 more)

### Community 11 - "test_delete_admin_user_removes_student_submissions_and_disk_files"
Cohesion: 0.10
Nodes (12): _set_sqlite_pragma(), _build_college_import_docx(), _get_user_by_email(), test_admin_academic_groups_crud_and_detachment(), test_admin_bulk_import_docx_sorts_ukrainian_alphabet_and_assigns_variants(), test_admin_bulk_import_rbac_and_validation_errors(), test_admin_bulk_import_returns_413_on_oversized_file_and_422_on_zip_bomb(), test_admin_bulk_import_txt_formats_continuing_list_number_and_duplicates() (+4 more)

### Community 13 - "serialize_submission"
Cohesion: 0.13
Nodes (4): _check_files_exist_batch(), _is_submission_file_available(), _resolve_existing_submission_file(), serialize_submission()

### Community 14 - "ExportService"
Cohesion: 0.10
Nodes (5): _enum_values(), ExportFormat, ExportedDocument, ExportService, GroupJournalBundle

### Community 15 - "v1/auth.py"
Cohesion: 0.05
Nodes (28): get_current_user(), change_password(), _extract_client_ip(), login(), read_current_user(), refresh_tokens(), serialize_user(), build_login_rate_limit_key() (+20 more)

### Community 16 - "make_auth_headers"
Cohesion: 0.10
Nodes (25): CourseSlug, build_sample_docx(), make_auth_headers(), _get_course_module_and_practical(), _get_user_by_email(), _grant_quiz_pass(), test_antiplagiarism_api_html_structural_match_and_classroom_template_clean(), test_antiplagiarism_flags_sha256_and_core_xml_matches_across_students() (+17 more)

### Community 17 - "html_grader.py"
Cohesion: 0.05
Nodes (15): _format_margin_measurement(), _format_margins_value(), format_student_criterion_description(), _replace(), _format_student_placeholder_value(), _format_uk_decimal(), has_meaningful_html_body(), _is_doctype_target() (+7 more)

### Community 22 - "submission.py"
Cohesion: 0.13
Nodes (5): DryRunGradingResponse, HtmlDryRunRequest, HtmlSubmissionRequest, ManualGradeUpdateRequest, SubmissionRead

### Community 23 - "package.json"
Cohesion: 0.07
Nodes (39): devDependencies, autoprefixer@^10.4.20, eslint@^9.15.0, @eslint/js@^9.15.0, eslint-plugin-react-hooks@^5.0.0, eslint-plugin-react-refresh@^0.4.14, globals@^15.12.0, postcss@^8.4.49 (+31 more)

### Community 24 - "App.tsx"
Cohesion: 0.11
Nodes (37): apiClient, App(), ProtectedAppLayout(), RoleHomeRedirect(), ChangePasswordModal(), ChangePasswordModalProps, Navbar(), NavbarProps (+29 more)

### Community 25 - "admin.py"
Cohesion: 0.07
Nodes (23): create_admin_group(), create_admin_user(), delete_admin_group(), delete_admin_user(), _ensure_email_unique(), _ensure_group_code_unique(), _ensure_group_list_number_unique(), _get_group_or_404() (+15 more)

### Community 26 - "AdminUsersPage.tsx"
Cohesion: 0.06
Nodes (47): AdminTab, AdminUsersPage(), buildCredentialsReportText(), CourseYearFilter, DeleteTarget, downloadCredentialsReportTxt(), FeedbackBanner, fetchAdminGroups() (+39 more)

### Community 27 - "course.ts"
Cohesion: 0.09
Nodes (39): ALLOWED_MEDIA_IMAGE_EXTENSIONS, CourseEditorPage(), deleteModuleById(), deletePracticalById(), DeleteTarget, DISCIPLINE_META, DisciplineMeta, EditorTab (+31 more)

### Community 28 - "GroupJournalPage.tsx"
Cohesion: 0.20
Nodes (16): PlagiarismBadge(), PlagiarismBadgeProps, COURSE_SLUG_BADGES, extractBlobApiErrorMessage(), fetchAcademicGroups(), fetchCourses(), fetchGroupJournal(), fetchSubmissionDetail() (+8 more)

### Community 29 - "AuthContext.tsx"
Cohesion: 0.12
Nodes (28): axios@^1.7.7, API_BASE_URL, AuthFailureListener, authFailureListeners, clearAuthTokens(), getAccessToken(), getRefreshToken(), notifyAuthFailure() (+20 more)

### Community 31 - "test_quiz_security.py"
Cohesion: 0.21
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

### Community 35 - "test_change_password_validation_and_imported_student_flag"
Cohesion: 0.22
Nodes (5): _get_user_by_email(), test_change_password_validation_and_imported_student_flag(), test_login_rate_limiting_blocks_after_n_failures_and_resets_on_success(), test_long_cyrillic_password_create_login_and_change_without_500(), test_token_version_revokes_tokens_on_admin_reset_and_self_change()

### Community 36 - "test_delete_module_renumbers_cleanly_under_unique_constraint_with_reverse_uuids"
Cohesion: 0.17
Nodes (5): test_academic_group_course_year_restricted_to_1_through_4(), _get_user_by_email(), test_admin_duplicate_group_list_number_returns_409_and_allows_other_groups(), test_delete_module_renumbers_cleanly_under_unique_constraint_with_reverse_uuids(), test_quiz_questions_preserve_order_index_independently_of_uuids()

### Community 37 - "xlsx_grader.py"
Cohesion: 0.10
Nodes (13): _BoolNode, _canonicalize_formula(), _CellRefNode, _EmptyArgNode, _FuncCallNode, _has_balanced_formula_delimiters(), _is_wrapped_in_parens(), _normalize_bare_function_name() (+5 more)

### Community 38 - "RuleBuilderPage.tsx"
Cohesion: 0.13
Nodes (22): DryRunResultPanel(), DryRunResultPanelProps, formatPoints(), BinaryFormat, DRY_RUN_FILE_ACCEPT, fetchCourses(), fetchPracticalTeacher(), FORMAT_BADGE_CONFIG (+14 more)

### Community 39 - "submit_practical_work"
Cohesion: 0.25
Nodes (3): _extract_submission_payload(), ExtractedSubmissionPayload, submit_practical_work()

### Community 40 - "GradingReportCard.tsx"
Cohesion: 0.09
Nodes (31): COURSE_SLUG_LABELS, CriterionBreakdownItem(), CriterionFilterMode, extractFileNameFromPath(), FORMAT_META, formatDateTime(), GradingReportCard(), GradingReportCardProps (+23 more)

### Community 41 - "db_session"
Cohesion: 0.12
Nodes (7): async_client(), build_sample_xlsx(), _create_sqlite_test_engine(), db_session(), _replace_zip_member(), rewrite_openxml_core_metadata(), _make_template_docx()

### Community 42 - "GroupJournalRead"
Cohesion: 0.24
Nodes (6): GroupJournalRead, PracticalColumnInfo, render_group_journal_xlsx(), _resolve_practical_columns(), test_export_group_journal_xlsx_and_pdf_support_12_point_scale(), test_render_group_journal_xlsx_sanitizes_formula_injection_and_keeps_numbers()

### Community 43 - "submission_service.py"
Cohesion: 0.06
Nodes (27): _build_template_content_disposition(), CourseCreate, CourseMediaUploadRead, CourseUpdate, GradingCriterionPreviewRead, ModuleCreate, ModuleReorderRequest, ModuleSummaryRead (+19 more)

### Community 44 - "ModuleViewPage.tsx"
Cohesion: 0.07
Nodes (46): AccessFieldDescriptor, AccessTableDescriptor, ALIGNMENT_DISPLAY_LABELS, BinaryPracticalFormat, dryRunFilePractical(), dryRunHtmlPractical(), extractBlobApiErrorMessage(), extractRetryAfterSeconds() (+38 more)

### Community 45 - "_collect_docx_body_fragments"
Cohesion: 0.31
Nodes (4): _collect_docx_body_fragments(), _collect_docx_xml_table_texts(), _extract_docx_paragraph_xml_text(), _find_xml_text()

### Community 48 - "retention_service.py"
Cohesion: 0.05
Nodes (25): main(), cleanup_expired_submissions(), cleanup_superseded_submission_files(), _delete_submission_file_paths_with_stats(), delete_submission_file_safely(), delete_submission_file_safely_async(), delete_submission_files_for_paths(), delete_submission_files_for_paths_async() (+17 more)

### Community 49 - "test_export_service.py"
Cohesion: 0.12
Nodes (13): _configure_pdf_font(), _fit_pdf_text(), _format_pdf_score(), _prepare_pdf_text(), render_group_journal_pdf(), _draw_page_header(), _draw_table_header(), _count_pdf_pages() (+5 more)

### Community 51 - "student_import_service.py"
Cohesion: 0.06
Nodes (25): format_size_limit_mb(), ImportedStudentItem, ImportSkippedItem, StudentImportResponse, calculate_variant_index(), build_credentials_report(), build_generated_email(), _classify_header_cell() (+17 more)

### Community 52 - "math"
Cohesion: 0.11
Nodes (10): _apply_binary_operator(), _eval_countif(), _eval_sumif(), _excel_compare(), _excel_wildcard_to_regex(), _format_cell_value(), _format_concat_operand(), _matches_exact_lookup() (+2 more)

### Community 53 - "test_cleanup_superseded_respects_24h_grace_window"
Cohesion: 0.29
Nodes (3): test_cleanup_superseded_respects_24h_grace_window(), test_cleanup_superseded_submission_files_keeps_best_and_latest_only(), test_media_courses_responses_include_security_headers()

### Community 54 - "db"
Cohesion: 0.33
Nodes (6): container_name, image, networks, restart, volumes, db

### Community 57 - "DocxGrader"
Cohesion: 0.05
Nodes (3): DocxGrader, _format_number(), test_docx_grader_inherits_font_from_base_style_chain_and_doc_defaults()

### Community 59 - "_extract_html_fingerprint"
Cohesion: 0.17
Nodes (6): _extract_css_property_blocks(), _extract_html_visible_text(), _walk(), _normalize_css_declarations(), _serialize_html_dom_structure(), _walk()

### Community 62 - "SubmissionService"
Cohesion: 0.11
Nodes (3): _save_uploaded_file(), SubmissionService, _unlink_file_quietly()

### Community 63 - "GradingRule"
Cohesion: 0.05
Nodes (14): AccdbDatabaseSchema, _find_named_entry(), _is_numeric_condition(), _normalize_count_condition(), _parse_relationship_pair_target(), _strip_identifiers(), _attribute_value_matches(), _find_tag_attr_key() (+6 more)

### Community 64 - "SqliteAsyncSessionAdapter"
Cohesion: 0.09
Nodes (19): SqliteAsyncSessionAdapter, _create_other_teacher(), _get_course_by_slug(), _get_user_by_email(), test_patch_quiz_question_owner_validation_and_rbac(), test_practical_template_lifecycle_student_download_unmodified_reject_and_cleanup(), test_reorder_course_modules_two_step_no_unique_conflict_and_validation(), test_upload_course_media_raster_magic_bytes_security_and_limits() (+11 more)

### Community 67 - "test_read_upload_file_limited_stops_reading_chunks_early"
Cohesion: 0.50
Nodes (3): test_read_upload_file_limited_stops_reading_chunks_early(), __init__(), read()

### Community 70 - "seed.py"
Cohesion: 0.07
Nodes (20): hash_password(), AcademicGroup, build_seed_bundle(), _extract_needs_rules_review(), _load_course_from_json(), _question_signature(), run_seed(), seed_database() (+12 more)

### Community 73 - "._eval_function_call"
Cohesion: 0.14
Nodes (9): _coerce_formula_bool(), _coerce_formula_number(), _collect_logical_values(), _collect_numeric_values(), _count_non_empty_values(), _eval_vlookup(), _require_single_number(), _try_parse_numeric() (+1 more)

### Community 75 - "@tanstack/react-query"
Cohesion: 0.18
Nodes (10): dependencies, lucide-react@^0.460.0, react@^18.3.1, react-dom@^18.3.1, react-router-dom@^6.28.0, @tanstack/react-query@^5.60.0, queryClient, rootElement (+2 more)

### Community 77 - "AccdbGrader"
Cohesion: 0.04
Nodes (28): AccdbColumnSchema, AccdbGrader, AccdbObjectsCatalog, AccdbRelationshipSchema, AccdbTableSchema, build_accdb_bytes(), _dedupe_names_casefold(), _dedupe_relationships() (+20 more)

### Community 78 - "GradingError"
Cohesion: 0.04
Nodes (15): GradingError, InvalidFileFormatError, BaseGrader, GraderFactory, _check_selector(), parse_core_xml_bytes(), XlsxGrader, PracticalFormat (+7 more)

### Community 80 - "config.py"
Cohesion: 0.06
Nodes (12): do_run_migrations(), run_async_migrations(), run_migrations_offline(), run_migrations_online(), get_settings(), Settings, verify_password(), test_hash_and_verify_password_async_offload_to_worker_thread() (+4 more)

### Community 82 - "practicals.py"
Cohesion: 0.04
Nodes (21): downgrade(), upgrade(), downgrade(), upgrade(), downgrade(), upgrade(), downgrade(), upgrade() (+13 more)

### Community 85 - "export_service.py"
Cohesion: 0.14
Nodes (9): CriterionErrorStat, GroupJournalPracticalRead, GroupJournalRow, GroupJournalStudentCell, build_group_journal(), calculate_criterion_error_stats(), _normalize_utc_timestamp(), _RuleStatAccumulator (+1 more)

### Community 87 - "read_upload_file_limited"
Cohesion: 0.15
Nodes (5): _extract_dry_run_payload(), ExtractedDryRunPayload, _parse_rules_json_field(), _build_too_large_exception(), read_upload_file_limited()

### Community 89 - "_FormulaEvalError"
Cohesion: 0.20
Nodes (5): _excel_round(), _FormulaEvalError, _normalize_cell_coord(), _split_cell_coord(), _tokenize_formula()

### Community 90 - "_FormulaParser"
Cohesion: 0.36
Nodes (4): _BinaryOpNode, _FormulaParser, _Token, _UnaryOpNode

### Community 99 - "_SeedCoursePayload"
Cohesion: 0.22
Nodes (3): _SeedCoursePayload, _SeedModulePayload, _SeedQuizQuestionPayload

### Community 100 - "test_graders.py"
Cohesion: 0.04
Nodes (34): check_submission_plagiarism(), _clean_optional_str(), _coerce_metadata(), compute_file_sha256(), compute_shingle_jaccard(), evaluate_plagiarism(), _is_content_fingerprint_match_actionable(), _is_generic_creator() (+26 more)

### Community 104 - "courses.py"
Cohesion: 0.07
Nodes (34): ensure_course_owner_or_admin(), _collect_practical_submission_file_paths(), create_course(), create_module(), create_quiz_question(), delete_module(), delete_practical(), delete_quiz_question() (+26 more)

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
  These have ≤1 connection - possible missing edges. (Counts symbols only; 1106 node(s) total have ≤1 connection when file, concept and rationale nodes are included.)
- **32 thin communities (<3 nodes) omitted from report** — run `graphify query` to explore isolated nodes.

## Suggested Questions
_Questions this graph is uniquely positioned to answer:_

- **Why does `DomainError` connect `courses.py` to `QuizService`, `upload_practical_template`, `submit_practical_work`, `submission_service.py`, `serialize_submission`, `GradingError`, `v1/auth.py`, `ExportService`, `practicals.py`, `PlagiarismDetectedError`, `student_import_service.py`, `export_service.py`, `read_upload_file_limited`, `admin.py`, `SubmissionService`?**
  _High betweenness centrality (0.035) - this node is a cross-community bridge._
- **Are the 62 inferred relationships involving `SqliteAsyncSessionAdapter` (e.g. with `_get_user_by_email()` and `test_academic_group_course_year_restricted_to_1_through_4()`) actually correct?**
  _`SqliteAsyncSessionAdapter` has 62 INFERRED edges - model-reasoned connections that need verification._
- **What connects `edu-auto-grader-backend` to the rest of the system?**
  _1 weakly-connected nodes found - possible missing edges._
- **Should `QuizService` be split into smaller, more focused modules?**
  _Cohesion score 0.09102564102564102 - nodes in this community are weakly interconnected._
- **Why does `PracticalFormat` connect `GradingError` to `QuizService`, `User`, `upload_practical_template`, `test_graders.py`, `xlsx_grader.py`, `metadata.py`, `seed.py`, `submission_service.py`, `AccdbGrader`, `ExportService`, `serialize_submission`, `html_grader.py`, `practicals.py`, `test_export_service.py`, `submission.py`, `DocxGrader`, `SubmissionService`, `GradingRule`?**
  _High betweenness centrality (0.035) - this node is a cross-community bridge._
- **Are the 17 inferred relationships involving `GradingRule` (e.g. with `AccdbGrader` and `_parse_relationship_pair_target()`) actually correct?**
  _`GradingRule` has 17 INFERRED edges - model-reasoned connections that need verification._
- **Should `postgres` be split into smaller, more focused modules?**
  _Cohesion score 0.10526315789473684 - nodes in this community are weakly interconnected._