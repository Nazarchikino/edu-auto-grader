# Graph Report - edu-auto-grader  (2026-11-25)

## Corpus Check
- 104 files · ~294,991 words
- Verdict: corpus is large enough that graph structure adds value.
- Unclassified: 14 file(s) not represented in the graph (top: (none) 9, .example 1, .ini 1)

## Summary
- 2288 nodes · 6635 edges · 88 communities (69 shown, 19 thin omitted)
- Extraction: 88% EXTRACTED · 12% INFERRED · 0% AMBIGUOUS · INFERRED: 796 edges (avg confidence: 0.93)
- Token cost: 0 input · 0 output

## Graph Freshness
- Built from commit: `cb7785bb`
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
- SqliteAsyncSessionAdapter
- ExtractedMetadata
- ExportService
- v1/auth.py
- make_auth_headers
- render_group_journal_pdf
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
- re
- schemas/auth.py
- GradingRule
- GradingReportCard.tsx
- db_session
- test_export_service.py
- submission_service.py
- ModuleViewPage.tsx
- _collect_docx_body_fragments
- SlidingWindowRateLimiter
- 0002_restrict_course_year_to_4.py
- cleanup_expired_submissions
- 0003_add_user_auth_security_fields.py
- create_application
- student_import_service.py
- 0005_practical_rules_review.py
- test_antiplagiarism_accdb_fingerprint_corrupt_safety_and_backward_compat
- DomainError
- _get_module_with_questions
- test_read_upload_file_limited_stops_reading_chunks_early
- DocxGrader
- security.py
- _extract_html_fingerprint
- test_graders.py
- SubmissionService
- networks
- .__call__
- _resolve_backend_path
- test_course_content.py
- xlsx_grader.py
- CriterionResult
- do_run_migrations
- 0001_initial_schema.py
- export_service.py
- _FormulaParser
- _compile_jsonb_for_sqlite
- serialize_submission
- _SeedCoursePayload
- metadata.py
- get_db
- frontend
- backend
- .import_students
- healthcheck
- build
- db
- PracticalFormat
- render_group_journal_xlsx
- backup.sh
- restore.sh

## God Nodes (most connected - your core abstractions)
1. `GradingRule` - 95 edges
2. `User` - 83 edges
3. `SqliteAsyncSessionAdapter` - 82 edges
4. `CourseSlug` - 73 edges
5. `DomainError` - 72 edges
6. `GradingError` - 62 edges
7. `PracticalFormat` - 57 edges
8. `Module` - 54 edges
9. `DocxGrader` - 54 edges
10. `make_auth_headers()` - 53 edges

## Surprising Connections (you probably didn't know these)
- `get_practical_for_student()` --uses--> `QuizService`  [INFERRED]
  backend/app/api/v1/courses.py → backend/app/services/quiz_service.py
- `submit_module_quiz()` --uses--> `QuizService`  [INFERRED]
  backend/app/api/v1/courses.py → backend/app/services/quiz_service.py
- `QuizService` --uses--> `DomainError`  [INFERRED]
  backend/app/services/quiz_service.py → backend/app/core/exceptions.py
- `QuizService` --uses--> `Module`  [INFERRED]
  backend/app/services/quiz_service.py → backend/app/models/course.py
- `QuizService` --uses--> `Practical`  [INFERRED]
  backend/app/services/quiz_service.py → backend/app/models/course.py

## Import Cycles
- None detected.

## Communities (88 total, 19 thin omitted)

### Community 0 - "QuizService"
Cohesion: 0.12
Nodes (4): QuizNotPassedError, _ensure_utc(), get_quiz_pass_threshold_percent(), QuizService

### Community 1 - "postgres"
Cohesion: 0.11
Nodes (18): POSTGRES_DB, POSTGRES_PASSWORD, POSTGRES_USER, interval, retries, test, timeout, container_name (+10 more)

### Community 2 - "compilerOptions"
Cohesion: 0.10
Nodes (20): compilerOptions, allowImportingTsExtensions, isolatedModules, jsx, lib, module, moduleDetection, moduleResolution (+12 more)

### Community 3 - "User"
Cohesion: 0.06
Nodes (18): run_migrations_offline(), downgrade(), upgrade(), Base, lifespan(), _enum_values(), QuizAttempt, Submission (+10 more)

### Community 4 - "AccdbGrader"
Cohesion: 0.08
Nodes (9): AccdbColumnSchema, AccdbGrader, AccdbObjectsCatalog, AccdbRelationshipSchema, AccdbTableSchema, _dedupe_relationships(), _is_system_table_name(), _parse_msys_relationships_table() (+1 more)

### Community 5 - "env"
Cohesion: 0.06
Nodes (38): env, name, runs-on, services, steps, concurrency, cancel-in-progress, group (+30 more)

### Community 6 - "analytics.py"
Cohesion: 0.15
Nodes (5): export_group_journal(), get_group_journal(), list_academic_groups(), _parse_export_format(), ExportFormat

### Community 7 - "test_auth_security.py"
Cohesion: 0.15
Nodes (8): hash_password(), test_password_hashing_supports_long_cyrillic_and_legacy_bcrypt_hashes(), _create_other_teacher(), _get_html_course_entities(), _get_user_by_email(), test_course_teacher_reassignment_forbidden_for_owner_and_allowed_for_admin(), test_cross_teacher_bola_blocked_across_all_course_and_submission_endpoints(), test_duplicate_root_auth_router_removed_returns_404()

### Community 8 - "MarkdownRenderer.tsx"
Cohesion: 0.12
Nodes (31): dedentBlockLines(), findClosingDoubleStar(), findClosingParen(), findClosingSingleStar(), findMatchingBracket(), getAlignmentClass(), getLineIndent(), hasUnsafeControlChars() (+23 more)

### Community 11 - "SqliteAsyncSessionAdapter"
Cohesion: 0.06
Nodes (25): AcademicGroup, resolve_student_variant(), SqliteAsyncSessionAdapter, _build_college_import_docx(), _get_user_by_email(), test_academic_group_course_year_restricted_to_1_through_4(), test_admin_academic_groups_crud_and_detachment(), test_admin_bulk_import_docx_sorts_ukrainian_alphabet_and_assigns_variants() (+17 more)

### Community 13 - "ExtractedMetadata"
Cohesion: 0.07
Nodes (19): check_submission_plagiarism(), _clean_optional_str(), _coerce_metadata(), compute_code_sha256(), compute_file_sha256(), compute_shingle_jaccard(), compute_submission_hash(), evaluate_plagiarism() (+11 more)

### Community 15 - "v1/auth.py"
Cohesion: 0.10
Nodes (11): change_password(), _extract_client_ip(), login(), read_current_user(), refresh_tokens(), build_login_rate_limit_key(), verify_password_async(), LoginRequest (+3 more)

### Community 16 - "make_auth_headers"
Cohesion: 0.10
Nodes (25): CourseSlug, _check_files_exist_batch(), build_sample_accdb(), build_sample_docx(), make_auth_headers(), _get_course_module_and_practical(), _get_user_by_email(), _grant_quiz_pass() (+17 more)

### Community 17 - "render_group_journal_pdf"
Cohesion: 0.20
Nodes (8): _configure_pdf_font(), _fit_pdf_text(), _format_pdf_score(), _prepare_pdf_text(), render_group_journal_pdf(), _draw_page_header(), _draw_table_header(), test_pdf_compact_score_formatting_and_text_fitting()

### Community 22 - "submit_practical_work"
Cohesion: 0.14
Nodes (5): _extract_submission_payload(), ExtractedSubmissionPayload, _resolve_practical_upload_limit(), submit_practical_work(), update_practical_grading_rules()

### Community 23 - "package.json"
Cohesion: 0.07
Nodes (39): devDependencies, autoprefixer@^10.4.20, eslint@^9.15.0, @eslint/js@^9.15.0, eslint-plugin-react-hooks@^5.0.0, eslint-plugin-react-refresh@^0.4.14, globals@^15.12.0, postcss@^8.4.49 (+31 more)

### Community 24 - "App.tsx"
Cohesion: 0.10
Nodes (36): dependencies, lucide-react@^0.460.0, react@^18.3.1, react-dom@^18.3.1, react-router-dom@^6.28.0, App(), ProtectedAppLayout(), RoleHomeRedirect() (+28 more)

### Community 25 - "admin.py"
Cohesion: 0.10
Nodes (19): create_admin_group(), create_admin_user(), delete_admin_group(), delete_admin_user(), _ensure_email_unique(), _ensure_group_code_unique(), _ensure_group_list_number_unique(), _get_group_or_404() (+11 more)

### Community 26 - "AdminUsersPage.tsx"
Cohesion: 0.06
Nodes (45): AdminTab, AdminUsersPage(), buildCredentialsReportText(), CourseYearFilter, DeleteTarget, downloadCredentialsReportTxt(), FeedbackBanner, fetchAdminGroups() (+37 more)

### Community 27 - "course.ts"
Cohesion: 0.07
Nodes (48): CourseEditorPage(), deleteModuleById(), deletePracticalById(), DeleteTarget, DISCIPLINE_META, DisciplineMeta, EditorTab, fetchCourses() (+40 more)

### Community 28 - "GroupJournalPage.tsx"
Cohesion: 0.22
Nodes (15): PlagiarismBadge(), PlagiarismBadgeProps, extractApiErrorMessage(), COURSE_SLUG_BADGES, extractBlobApiErrorMessage(), fetchAcademicGroups(), fetchCourses(), fetchGroupJournal() (+7 more)

### Community 29 - "AuthContext.tsx"
Cohesion: 0.12
Nodes (28): axios@^1.7.7, API_BASE_URL, apiClient, AuthFailureListener, authFailureListeners, clearAuthTokens(), getAccessToken(), getRefreshToken() (+20 more)

### Community 30 - "XlsxGrader"
Cohesion: 0.07
Nodes (4): _format_cell_value(), XlsxGrader, test_xlsx_grader_evaluates_formulas_values_and_charts(), test_xlsx_grader_rejects_static_value_instead_of_formula_and_missing_chart()

### Community 31 - "_get_student_and_word_practical"
Cohesion: 0.24
Nodes (4): _get_student_and_word_practical(), test_cleanup_superseded_respects_24h_grace_window(), test_cleanup_superseded_submission_files_keeps_best_and_latest_only(), test_media_courses_responses_include_security_headers()

### Community 32 - "environment"
Cohesion: 0.13
Nodes (17): environment, environment, APP_ENV, CORS_ORIGINS, ENABLE_RETENTION_CLEANUP_TASK, FORWARDED_ALLOW_IPS, JWT_SECRET_KEY, POSTGRES_DB (+9 more)

### Community 33 - "accdb_grader.py"
Cohesion: 0.09
Nodes (13): build_accdb_bytes(), _dedupe_names_casefold(), _encode_data_page(), _encode_msys_catalog_record(), _encode_tdef_page(), _encode_text_record(), _is_hidden_or_system_object(), _lookup_mapping_column() (+5 more)

### Community 34 - "HtmlSandbox.tsx"
Cohesion: 0.13
Nodes (17): @monaco-editor/react@4.6.0, buildDraftStorageKey(), buildStarterHtmlTemplate(), DraftSaveState, EditorColorTheme, formatDraftSavedTime(), HtmlSandbox(), HtmlSandboxProps (+9 more)

### Community 35 - "GradingError"
Cohesion: 0.06
Nodes (8): GradingError, _find_named_entry(), _is_numeric_condition(), _normalize_count_condition(), _parse_relationship_pair_target(), _strip_identifiers(), _check_selector(), _has_balanced_formula_delimiters()

### Community 36 - "read_upload_file_limited"
Cohesion: 0.28
Nodes (3): _build_too_large_exception(), format_size_limit_mb(), read_upload_file_limited()

### Community 37 - "re"
Cohesion: 0.29
Nodes (3): _parse_ddl_column_type(), _sanitize_filename_token(), _transliterate_to_ascii()

### Community 38 - "schemas/auth.py"
Cohesion: 0.09
Nodes (17): AcademicGroupBase, AcademicGroupCreate, AcademicGroupRead, AcademicGroupUpdate, AdminResetPasswordRequest, AdminResetPasswordResponse, ChangePasswordRequest, ChangePasswordResponse (+9 more)

### Community 39 - "GradingRule"
Cohesion: 0.05
Nodes (30): _attribute_value_matches(), _find_tag_attr_key(), _get_tag_attribute_str(), has_meaningful_html_body(), HtmlGrader, _is_doctype_target(), _node_has_visible_content(), _normalize_selector() (+22 more)

### Community 40 - "GradingReportCard.tsx"
Cohesion: 0.07
Nodes (37): @tanstack/react-query@^5.60.0, COURSE_SLUG_LABELS, CriterionBreakdownItem(), CriterionFilterMode, extractFileNameFromPath(), FORMAT_META, formatDateTime(), GradingReportCard() (+29 more)

### Community 41 - "db_session"
Cohesion: 0.13
Nodes (5): async_client(), _create_sqlite_test_engine(), _set_sqlite_pragma(), db_session(), _fast_seed_hash_password()

### Community 42 - "test_export_service.py"
Cohesion: 0.12
Nodes (14): CriterionErrorStat, GroupJournalPracticalRead, GroupJournalRead, GroupJournalRow, GroupJournalStudentCell, HtmlSubmissionRequest, build_group_journal(), PracticalColumnInfo (+6 more)

### Community 43 - "submission_service.py"
Cohesion: 0.09
Nodes (18): _serialize_practical_teacher(), CourseCreate, CourseUpdate, ModuleCreate, ModuleSummaryRead, ModuleUpdate, PracticalCreate, PracticalStudentRead (+10 more)

### Community 44 - "ModuleViewPage.tsx"
Cohesion: 0.10
Nodes (35): AccessFieldDescriptor, AccessTableDescriptor, BinaryPracticalFormat, extractRetryAfterSeconds(), fetchModuleDetail(), fetchStudentPractical(), FILE_UPLOAD_FORMAT_META, FileUploadFormatMeta (+27 more)

### Community 45 - "_collect_docx_body_fragments"
Cohesion: 0.31
Nodes (4): _collect_docx_body_fragments(), _collect_docx_xml_table_texts(), _extract_docx_paragraph_xml_text(), _find_xml_text()

### Community 48 - "cleanup_expired_submissions"
Cohesion: 0.06
Nodes (17): cleanup_expired_submissions(), cleanup_superseded_submission_files(), _delete_submission_file_paths_with_stats(), delete_submission_file_safely(), delete_submission_file_safely_async(), delete_submission_files_for_paths(), _inspect_submission_file_paths(), _is_postgresql_session() (+9 more)

### Community 50 - "create_application"
Cohesion: 0.25
Nodes (3): _check_uploads_dir_writable(), create_application(), readiness_check()

### Community 51 - "student_import_service.py"
Cohesion: 0.07
Nodes (21): build_credentials_report(), build_generated_email(), _classify_header_cell(), _clean_whitespace(), _detect_docx_header_columns(), _DocxColumnMap, _encode_ukrainian_word(), generate_temp_password() (+13 more)

### Community 53 - "test_antiplagiarism_accdb_fingerprint_corrupt_safety_and_backward_compat"
Cohesion: 0.20
Nodes (4): test_accdb_grader_inspects_queries_forms_reports_relationships_and_mdb_export_csv(), _fake_which(), test_antiplagiarism_accdb_fingerprint_corrupt_safety_and_backward_compat(), test_zip_bomb_protection_blocks_high_ratio_many_entries_and_oversized_uncompressed()

### Community 54 - "DomainError"
Cohesion: 0.12
Nodes (5): get_current_user(), require_role(), role_checker(), DomainError, PlagiarismDetectedError

### Community 55 - "_get_module_with_questions"
Cohesion: 0.11
Nodes (11): get_settings(), Settings, test_settings_production_rejects_default_or_short_jwt_secret(), _build_answers_for_score(), _get_module_with_questions(), _get_user_by_email(), test_excel_q42_imported_in_module_8_with_media_and_dry_run(), test_quiz_cooldown_zero_disables_wait_and_negative_config_rejected() (+3 more)

### Community 56 - "test_read_upload_file_limited_stops_reading_chunks_early"
Cohesion: 0.50
Nodes (3): test_read_upload_file_limited_stops_reading_chunks_early(), __init__(), read()

### Community 57 - "DocxGrader"
Cohesion: 0.05
Nodes (6): DocxGrader, _format_number(), test_docx_grader_evaluates_valid_document(), test_docx_grader_inherits_font_from_base_style_chain_and_doc_defaults(), test_docx_grader_resolves_placeholders_in_target_and_expected(), test_docx_grader_table_exists_supports_rxc_and_rows_cols_conditions()

### Community 58 - "security.py"
Cohesion: 0.14
Nodes (9): create_access_token(), create_refresh_token(), create_token_pair(), decode_token(), _encode_jwt_token(), _sha256_password_bytes(), verify_password(), _enum_values() (+1 more)

### Community 59 - "_extract_html_fingerprint"
Cohesion: 0.17
Nodes (6): _extract_css_property_blocks(), _extract_html_visible_text(), _walk(), _normalize_css_declarations(), _serialize_html_dom_structure(), _walk()

### Community 61 - "test_graders.py"
Cohesion: 0.09
Nodes (9): parse_core_xml_bytes(), build_sample_xlsx(), _replace_zip_member(), rewrite_openxml_core_metadata(), _strip_zip_member(), _build_calc_xlsx(), test_core_xml_parser_rejects_xml_entity_expansion_billion_laughs(), _write_custom_docx() (+1 more)

### Community 62 - "SubmissionService"
Cohesion: 0.11
Nodes (8): download_submission_file(), get_submission_detail(), list_my_submissions(), list_submissions(), update_submission_grade(), ManualGradeUpdateRequest, SubmissionRead, SubmissionService

### Community 66 - "networks"
Cohesion: 0.40
Nodes (5): driver, internal, networks, edge, internal

### Community 70 - "test_course_content.py"
Cohesion: 0.07
Nodes (29): Course, Module, Practical, QuizQuestion, build_seed_bundle(), _extract_needs_rules_review(), _load_course_from_json(), main() (+21 more)

### Community 73 - "xlsx_grader.py"
Cohesion: 0.06
Nodes (28): _apply_binary_operator(), _canonicalize_formula(), _coerce_formula_bool(), _coerce_formula_number(), _collect_logical_values(), _collect_numeric_values(), _count_non_empty_values(), _eval_countif() (+20 more)

### Community 77 - "CriterionResult"
Cohesion: 0.07
Nodes (6): AccdbDatabaseSchema, BaseGrader, CriterionResult, GradingReport, test_all_course_variants_resolve_rule_placeholders_without_leftovers(), _make_grading_report_dict()

### Community 80 - "do_run_migrations"
Cohesion: 0.29
Nodes (3): do_run_migrations(), run_async_migrations(), run_migrations_online()

### Community 84 - "export_service.py"
Cohesion: 0.11
Nodes (8): build_content_disposition(), calculate_criterion_error_stats(), ExportedDocument, GroupJournalBundle, _normalize_utc_timestamp(), _RuleStatAccumulator, format_cooldown_remaining(), SubmissionDownloadPayload

### Community 90 - "_FormulaParser"
Cohesion: 0.21
Nodes (11): _BinaryOpNode, _BoolNode, _CellRefNode, _EmptyArgNode, _FormulaParser, _FuncCallNode, _NumberNode, _RangeRefNode (+3 more)

### Community 95 - "serialize_submission"
Cohesion: 0.13
Nodes (5): _is_submission_file_available(), _resolve_existing_submission_file(), _save_uploaded_file(), serialize_submission(), _unlink_file_quietly()

### Community 99 - "_SeedCoursePayload"
Cohesion: 0.22
Nodes (3): _SeedCoursePayload, _SeedModulePayload, _SeedQuizQuestionPayload

### Community 100 - "metadata.py"
Cohesion: 0.09
Nodes (17): _canonicalize_xlsx_formula(), compute_bytes_sha256(), compute_text_shingles(), _extract_accdb_fingerprint(), _extract_accdb_table_via_mdb_export(), _extract_accdb_tables_via_mdbtools(), extract_core_xml_metadata(), extract_document_metadata() (+9 more)

### Community 104 - "get_db"
Cohesion: 0.08
Nodes (30): ensure_course_owner_or_admin(), _build_module_detail_read(), _collect_practical_submission_file_paths(), create_course(), create_module(), create_quiz_question(), delete_module(), delete_practical() (+22 more)

### Community 108 - "frontend"
Cohesion: 0.25
Nodes (8): condition, backend, container_name, depends_on, networks, ports, restart, frontend

### Community 110 - "backend"
Cohesion: 0.25
Nodes (8): container_name, depends_on, networks, restart, volumes, condition, db, backend

### Community 114 - ".import_students"
Cohesion: 0.11
Nodes (6): import_admin_students(), ImportedStudentItem, StudentImportResponse, calculate_variant_index(), StudentImportService, test_build_credentials_report_uses_list_number_and_dynamic_variant_note()

### Community 141 - "healthcheck"
Cohesion: 0.48
Nodes (7): healthcheck, healthcheck, interval, retries, start_period, test, timeout

### Community 145 - "build"
Cohesion: 0.40
Nodes (6): VITE_API_BASE_URL, build, args, context, dockerfile, build

### Community 147 - "db"
Cohesion: 0.17
Nodes (11): container_name, image, networks, restart, volumes, name, services, db (+3 more)

### Community 153 - "PracticalFormat"
Cohesion: 0.17
Nodes (4): InvalidFileFormatError, GraderFactory, PracticalFormat, test_grader_factory_resolves_all_four_formats()

### Community 168 - "render_group_journal_xlsx"
Cohesion: 0.12
Nodes (6): _auto_adjust_worksheet_columns(), render_group_journal_xlsx(), _resolve_practical_columns(), sanitize_spreadsheet_text(), _set_xlsx_text_cell(), test_sanitize_spreadsheet_text_escapes_all_formula_prefixes()

## Knowledge Gaps
- **1 isolated node(s):** `edu-auto-grader-backend`
  These have ≤1 connection - possible missing edges. (Counts symbols only; 1003 node(s) total have ≤1 connection when file, concept and rationale nodes are included.)
- **19 thin communities (<3 nodes) omitted from report** — run `graphify query` to explore isolated nodes.

## Suggested Questions
_Questions this graph is uniquely positioned to answer:_

- **Why does `GradingRule` connect `GradingRule` to `accdb_grader.py`, `PracticalFormat`, `GradingError`, `AccdbGrader`, `User`, `schemas/auth.py`, `test_course_content.py`, `xlsx_grader.py`, `submission_service.py`, `CriterionResult`, `test_antiplagiarism_accdb_fingerprint_corrupt_safety_and_backward_compat`, `SubmissionService`, `DocxGrader`, `test_graders.py`, `XlsxGrader`, `serialize_submission`?**
  _High betweenness centrality (0.050) - this node is a cross-community bridge._
- **Are the 20 inferred relationships involving `GradingRule` (e.g. with `_serialize_practical_teacher()` and `AccdbGrader`) actually correct?**
  _`GradingRule` has 20 INFERRED edges - model-reasoned connections that need verification._
- **What connects `edu-auto-grader-backend` to the rest of the system?**
  _1 weakly-connected nodes found - possible missing edges._
- **Should `QuizService` be split into smaller, more focused modules?**
  _Cohesion score 0.12 - nodes in this community are weakly interconnected._
- **Why does `CourseSlug` connect `make_auth_headers` to `User`, `AccdbGrader`, `test_auth_security.py`, `SqliteAsyncSessionAdapter`, `PracticalFormat`, `_get_student_and_word_practical`, `GradingRule`, `render_group_journal_xlsx`, `test_export_service.py`, `submission_service.py`, `_get_module_with_questions`, `DocxGrader`, `test_graders.py`, `SubmissionService`, `test_course_content.py`, `CriterionResult`, `export_service.py`, `serialize_submission`, `_SeedCoursePayload`, `get_db`?**
  _High betweenness centrality (0.036) - this node is a cross-community bridge._
- **Are the 41 inferred relationships involving `User` (e.g. with `ensure_course_owner_or_admin()` and `get_current_user()`) actually correct?**
  _`User` has 41 INFERRED edges - model-reasoned connections that need verification._
- **Should `postgres` be split into smaller, more focused modules?**
  _Cohesion score 0.10526315789473684 - nodes in this community are weakly interconnected._