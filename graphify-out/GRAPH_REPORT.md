# Graph Report - edu-auto-grader  (2026-11-25)

## Corpus Check
- 104 files · ~299,505 words
- Verdict: corpus is large enough that graph structure adds value.
- Unclassified: 14 file(s) not represented in the graph (top: (none) 9, .example 1, .ini 1)

## Summary
- 2356 nodes · 6584 edges · 130 communities (78 shown, 52 thin omitted)
- Extraction: 91% EXTRACTED · 9% INFERRED · 0% AMBIGUOUS · INFERRED: 582 edges (avg confidence: 0.92)
- Token cost: 0 input · 0 output

## Graph Freshness
- Built from commit: `32ae86fc`
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
- evaluate_plagiarism
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
- xlsx_grader.py
- schemas/auth.py
- .evaluate
- GradingReportCard.tsx
- db_session
- export_service.py
- courses.py
- ModuleViewPage.tsx
- _collect_docx_body_fragments
- SlidingWindowRateLimiter
- 0002_restrict_course_year_to_4.py
- cleanup_expired_submissions
- 0003_add_user_auth_security_fields.py
- submission_service.py
- student_import_service.py
- 0005_practical_rules_review.py
- test_antiplagiarism_accdb_fingerprint_corrupt_safety_and_backward_compat
- DomainError
- _get_module_with_questions
- .build_criterion_result
- DocxGrader
- build_sample_docx
- _extract_html_fingerprint
- ExtractedMetadata
- rewrite_openxml_core_metadata
- list_my_submissions
- HtmlGrader
- SqliteAsyncSessionAdapter
- html_grader.py
- networks
- SubmissionRead
- .__call__
- Settings
- test_course_content.py
- get_current_user
- .evaluate
- _FormulaEvalError
- test_change_password_validation_and_imported_student_flag
- @tanstack/react-query
- _strip_identifiers
- _format_student_placeholder_value
- do_run_migrations
- _find_named_entry
- 0001_initial_schema.py
- _parse_msys_relationships_csv
- SubmissionRecordProtocol
- _build_submission_download_names
- 0004_add_indexes_constraints_and_quiz_order.py
- async_client
- AccdbColumnSchema
- _tokenize_formula
- _FormulaParser
- _check_files_exist_batch
- test_hash_and_verify_password_async_offload_to_worker_thread
- _compile_jsonb_for_sqlite
- serialize_submission
- test_lifespan_starts_and_cancels_retention_background_task
- _enum_values
- run_migrations_offline
- _SeedCoursePayload
- metadata.py
- delete_submission_files_for_paths_async
- get_db
- frontend
- backend
- .import_students
- healthcheck
- build
- db
- InvalidFileFormatError
- _set_xlsx_text_cell
- backup.sh
- restore.sh

## God Nodes (most connected - your core abstractions)
1. `SqliteAsyncSessionAdapter` - 83 edges
2. `User` - 81 edges
3. `DomainError` - 71 edges
4. `GradingError` - 57 edges
5. `make_auth_headers()` - 54 edges
6. `DocxGrader` - 49 edges
7. `InvalidFileFormatError` - 46 edges
8. `UserRole` - 46 edges
9. `get_db()` - 46 edges
10. `PracticalFormat` - 45 edges

## Surprising Connections (you probably didn't know these)
- `_serialize_practical_teacher()` --uses--> `PracticalVariant`  [INFERRED]
  backend/app/api/v1/courses.py → backend/app/schemas/course.py
- `list_courses()` --uses--> `CourseRead`  [INFERRED]
  backend/app/api/v1/courses.py → backend/app/schemas/course.py
- `get_course()` --uses--> `CourseRead`  [INFERRED]
  backend/app/api/v1/courses.py → backend/app/schemas/course.py
- `create_course()` --uses--> `CourseCreate`  [INFERRED]
  backend/app/api/v1/courses.py → backend/app/schemas/course.py
- `create_course()` --uses--> `CourseRead`  [INFERRED]
  backend/app/api/v1/courses.py → backend/app/schemas/course.py

## Import Cycles
- None detected.

## Communities (130 total, 52 thin omitted)

### Community 0 - "QuizService"
Cohesion: 0.11
Nodes (7): _build_module_detail_read(), get_practical_for_student(), submit_module_quiz(), PracticalStudentRead, build_student_grading_criteria(), get_quiz_pass_threshold_percent(), QuizService

### Community 1 - "postgres"
Cohesion: 0.11
Nodes (18): POSTGRES_DB, POSTGRES_PASSWORD, POSTGRES_USER, interval, retries, test, timeout, container_name (+10 more)

### Community 2 - "compilerOptions"
Cohesion: 0.10
Nodes (20): compilerOptions, allowImportingTsExtensions, isolatedModules, jsx, lib, module, moduleDetection, moduleResolution (+12 more)

### Community 3 - "User"
Cohesion: 0.08
Nodes (20): Base, Course, Module, Practical, QuizQuestion, QuizAttempt, Submission, User (+12 more)

### Community 4 - "AccdbGrader"
Cohesion: 0.11
Nodes (4): AccdbGrader, AccdbObjectsCatalog, AccdbTableSchema, _parse_ddl_column_type()

### Community 5 - "env"
Cohesion: 0.06
Nodes (38): env, name, runs-on, services, steps, concurrency, cancel-in-progress, group (+30 more)

### Community 6 - "analytics.py"
Cohesion: 0.16
Nodes (4): export_group_journal(), get_group_journal(), list_academic_groups(), _parse_export_format()

### Community 7 - "test_auth_security.py"
Cohesion: 0.11
Nodes (12): hash_password(), _sha256_password_bytes(), verify_password(), _enum_values(), UserRole, test_password_hashing_supports_long_cyrillic_and_legacy_bcrypt_hashes(), _create_other_teacher(), _get_html_course_entities() (+4 more)

### Community 8 - "MarkdownRenderer.tsx"
Cohesion: 0.12
Nodes (31): dedentBlockLines(), findClosingDoubleStar(), findClosingParen(), findClosingSingleStar(), findMatchingBracket(), getAlignmentClass(), getLineIndent(), hasUnsafeControlChars() (+23 more)

### Community 11 - ".execute"
Cohesion: 0.10
Nodes (12): _set_sqlite_pragma(), _build_college_import_docx(), _get_user_by_email(), test_admin_academic_groups_crud_and_detachment(), test_admin_bulk_import_docx_sorts_ukrainian_alphabet_and_assigns_variants(), test_admin_bulk_import_rbac_and_validation_errors(), test_admin_bulk_import_returns_413_on_oversized_file_and_422_on_zip_bomb(), test_admin_bulk_import_txt_formats_continuing_list_number_and_duplicates() (+4 more)

### Community 13 - "evaluate_plagiarism"
Cohesion: 0.12
Nodes (11): _clean_optional_str(), _coerce_metadata(), compute_shingle_jaccard(), evaluate_plagiarism(), _is_content_fingerprint_match_actionable(), _is_generic_creator(), DummySubmissionRecord, test_antiplagiarism_detects_html_copy_with_comment_and_renamed_css_classes() (+3 more)

### Community 15 - "v1/auth.py"
Cohesion: 0.09
Nodes (16): change_password(), _extract_client_ip(), login(), read_current_user(), refresh_tokens(), serialize_user(), build_login_rate_limit_key(), create_access_token() (+8 more)

### Community 16 - "make_auth_headers"
Cohesion: 0.11
Nodes (19): make_auth_headers(), _get_course_module_and_practical(), _get_user_by_email(), _grant_quiz_pass(), test_antiplagiarism_api_html_structural_match_and_classroom_template_clean(), test_antiplagiarism_flags_sha256_and_core_xml_matches_across_students(), test_best_score_unified_across_student_progress_and_group_journal_export(), test_download_submissions_by_course_teacher_and_admin_with_headers_and_content() (+11 more)

### Community 17 - "test_graders.py"
Cohesion: 0.10
Nodes (13): GradingRule, GradingRuleType, test_docx_grader_detects_formatting_violations_and_corrupt_files(), test_docx_grader_evaluates_valid_document(), test_docx_grader_inherits_font_from_base_style_chain_and_doc_defaults(), test_docx_grader_resolves_placeholders_in_target_and_expected(), test_docx_grader_supports_uniform_single_number_margin(), test_docx_grader_table_exists_supports_rxc_and_rows_cols_conditions() (+5 more)

### Community 22 - "submit_practical_work"
Cohesion: 0.14
Nodes (5): _extract_submission_payload(), ExtractedSubmissionPayload, _resolve_practical_upload_limit(), submit_practical_work(), update_practical_grading_rules()

### Community 23 - "package.json"
Cohesion: 0.07
Nodes (39): devDependencies, autoprefixer@^10.4.20, eslint@^9.15.0, @eslint/js@^9.15.0, eslint-plugin-react-hooks@^5.0.0, eslint-plugin-react-refresh@^0.4.14, globals@^15.12.0, postcss@^8.4.49 (+31 more)

### Community 24 - "App.tsx"
Cohesion: 0.11
Nodes (35): App(), ProtectedAppLayout(), RoleHomeRedirect(), ChangePasswordModal(), ChangePasswordModalProps, Navbar(), NavbarProps, resolvePageTitle() (+27 more)

### Community 25 - "admin.py"
Cohesion: 0.11
Nodes (14): create_admin_user(), delete_admin_group(), delete_admin_user(), _ensure_email_unique(), _ensure_group_list_number_unique(), _get_group_or_404(), _get_user_with_group_or_404(), list_admin_groups() (+6 more)

### Community 26 - "AdminUsersPage.tsx"
Cohesion: 0.06
Nodes (47): AdminTab, AdminUsersPage(), buildCredentialsReportText(), CourseYearFilter, DeleteTarget, downloadCredentialsReportTxt(), FeedbackBanner, fetchAdminGroups() (+39 more)

### Community 27 - "course.ts"
Cohesion: 0.08
Nodes (44): CourseEditorPage(), deleteModuleById(), deletePracticalById(), DeleteTarget, DISCIPLINE_META, DisciplineMeta, EditorTab, fetchCourses() (+36 more)

### Community 28 - "GroupJournalPage.tsx"
Cohesion: 0.22
Nodes (15): PlagiarismBadge(), PlagiarismBadgeProps, extractApiErrorMessage(), COURSE_SLUG_BADGES, extractBlobApiErrorMessage(), fetchAcademicGroups(), fetchCourses(), fetchGroupJournal() (+7 more)

### Community 29 - "AuthContext.tsx"
Cohesion: 0.12
Nodes (29): axios@^1.7.7, API_BASE_URL, apiClient, AuthFailureListener, authFailureListeners, clearAuthTokens(), getAccessToken(), getRefreshToken() (+21 more)

### Community 30 - "XlsxGrader"
Cohesion: 0.08
Nodes (3): _format_cell_value(), XlsxGrader, _eval()

### Community 31 - "_get_student_and_word_practical"
Cohesion: 0.15
Nodes (6): _get_student_and_word_practical(), test_cleanup_superseded_respects_24h_grace_window(), test_cleanup_superseded_submission_files_keeps_best_and_latest_only(), test_health_ready_returns_200_when_healthy_and_503_on_uploads_or_db_failure(), test_media_courses_responses_include_security_headers(), test_uploads_dir_relative_path_is_anchored_to_backend_directory()

### Community 32 - "environment"
Cohesion: 0.13
Nodes (17): environment, environment, APP_ENV, CORS_ORIGINS, ENABLE_RETENTION_CLEANUP_TASK, FORWARDED_ALLOW_IPS, JWT_SECRET_KEY, POSTGRES_DB (+9 more)

### Community 33 - "accdb_grader.py"
Cohesion: 0.09
Nodes (13): build_accdb_bytes(), _dedupe_names_casefold(), _encode_data_page(), _encode_msys_catalog_record(), _encode_tdef_page(), _encode_text_record(), _is_hidden_or_system_object(), _is_system_table_name() (+5 more)

### Community 34 - "HtmlSandbox.tsx"
Cohesion: 0.13
Nodes (17): @monaco-editor/react@4.6.0, buildDraftStorageKey(), buildStarterHtmlTemplate(), DraftSaveState, EditorColorTheme, formatDraftSavedTime(), HtmlSandbox(), HtmlSandboxProps (+9 more)

### Community 35 - "GradingError"
Cohesion: 0.09
Nodes (3): GradingError, BaseGrader, _check_selector()

### Community 36 - "read_upload_file_limited"
Cohesion: 0.17
Nodes (6): _build_too_large_exception(), format_size_limit_mb(), read_upload_file_limited(), test_read_upload_file_limited_stops_reading_chunks_early(), __init__(), read()

### Community 37 - "xlsx_grader.py"
Cohesion: 0.08
Nodes (16): _BoolNode, _canonicalize_formula(), _CellRefNode, _count_non_empty_values(), _EmptyArgNode, _excel_wildcard_to_regex(), _FuncCallNode, _has_balanced_formula_delimiters() (+8 more)

### Community 38 - "schemas/auth.py"
Cohesion: 0.09
Nodes (17): create_admin_group(), _ensure_group_code_unique(), _normalize_non_empty(), AcademicGroupBase, AcademicGroupCreate, AcademicGroupRead, AcademicGroupUpdate, AdminResetPasswordRequest (+9 more)

### Community 39 - ".evaluate"
Cohesion: 0.08
Nodes (7): has_meaningful_html_body(), parse_html_document(), test_minimal_html_starter_template_scores_zero_across_all_html_course_modules(), test_html_grader_attribute_filter_selector_and_compound_colspan(), test_html_grader_detects_missing_tags_and_rejects_empty_code(), test_html_grader_empty_body_and_starter_template_score_zero(), test_html_grader_evaluates_semantic_dom_structure_and_attributes()

### Community 40 - "GradingReportCard.tsx"
Cohesion: 0.09
Nodes (29): COURSE_SLUG_LABELS, CriterionBreakdownItem(), CriterionFilterMode, extractFileNameFromPath(), FORMAT_META, formatDateTime(), GradingReportCard(), GradingReportCardProps (+21 more)

### Community 41 - "db_session"
Cohesion: 0.25
Nodes (3): _create_sqlite_test_engine(), db_session(), _fast_seed_hash_password()

### Community 42 - "export_service.py"
Cohesion: 0.05
Nodes (37): CourseSlug, CriterionErrorStat, GroupJournalPracticalRead, GroupJournalRead, GroupJournalRow, GroupJournalStudentCell, build_content_disposition(), build_group_journal() (+29 more)

### Community 43 - "courses.py"
Cohesion: 0.11
Nodes (19): CourseCreate, CourseRead, CourseUpdate, GradingCriterionPreviewRead, ModuleCreate, ModuleDetailRead, ModuleSummaryRead, ModuleUpdate (+11 more)

### Community 44 - "ModuleViewPage.tsx"
Cohesion: 0.08
Nodes (40): AccessFieldDescriptor, AccessTableDescriptor, ALIGNMENT_DISPLAY_LABELS, BinaryPracticalFormat, extractRetryAfterSeconds(), fetchModuleDetail(), fetchStudentPractical(), FILE_UPLOAD_FORMAT_META (+32 more)

### Community 45 - "_collect_docx_body_fragments"
Cohesion: 0.31
Nodes (4): _collect_docx_body_fragments(), _collect_docx_xml_table_texts(), _extract_docx_paragraph_xml_text(), _find_xml_text()

### Community 48 - "cleanup_expired_submissions"
Cohesion: 0.08
Nodes (15): cleanup_expired_submissions(), cleanup_superseded_submission_files(), _delete_submission_file_paths_with_stats(), delete_submission_file_safely(), delete_submission_file_safely_async(), delete_submission_files_for_paths(), _inspect_submission_file_paths(), _is_postgresql_session() (+7 more)

### Community 50 - "submission_service.py"
Cohesion: 0.07
Nodes (13): require_role(), GraderFactory, _check_uploads_dir_writable(), create_application(), readiness_check(), lifespan(), PracticalFormat, CriterionResult (+5 more)

### Community 51 - "student_import_service.py"
Cohesion: 0.07
Nodes (21): ImportSkippedItem, build_generated_email(), _classify_header_cell(), _clean_whitespace(), _detect_docx_header_columns(), _DocxColumnMap, _encode_ukrainian_word(), generate_temp_password() (+13 more)

### Community 53 - "test_antiplagiarism_accdb_fingerprint_corrupt_safety_and_backward_compat"
Cohesion: 0.20
Nodes (4): test_accdb_grader_inspects_queries_forms_reports_relationships_and_mdb_export_csv(), _fake_which(), test_antiplagiarism_accdb_fingerprint_corrupt_safety_and_backward_compat(), test_zip_bomb_protection_blocks_high_ratio_many_entries_and_oversized_uncompressed()

### Community 54 - "DomainError"
Cohesion: 0.14
Nodes (4): role_checker(), _raise_user_conflict_from_integrity_error(), DomainError, QuizNotPassedError

### Community 55 - "_get_module_with_questions"
Cohesion: 0.18
Nodes (8): _build_answers_for_score(), _get_module_with_questions(), _get_user_by_email(), test_excel_q42_imported_in_module_8_with_media_and_dry_run(), test_quiz_cooldown_zero_disables_wait_and_negative_config_rejected(), test_quiz_pass_threshold_setting_controls_passed_flag(), test_quiz_retry_cooldown_blocks_immediate_retry_and_unlocks_after_window(), test_quiz_submit_rejects_incomplete_duplicate_foreign_and_invalid_answers()

### Community 58 - "build_sample_docx"
Cohesion: 0.14
Nodes (11): build_sample_docx(), _copy_course_content_dir(), _get_user_by_email(), test_delete_module_and_practical_rbac_and_not_found(), test_delete_module_by_teacher_and_admin_cascades_cleans_files_and_renumbers(), test_delete_practical_preserves_module_lecture_quiz_and_cleans_files(), test_media_courses_static_serving(), test_seed_and_sync_courses_persist_needs_rules_review() (+3 more)

### Community 59 - "_extract_html_fingerprint"
Cohesion: 0.17
Nodes (6): _extract_css_property_blocks(), _extract_html_visible_text(), _walk(), _normalize_css_declarations(), _serialize_html_dom_structure(), _walk()

### Community 60 - "ExtractedMetadata"
Cohesion: 0.11
Nodes (5): check_submission_plagiarism(), ExtractedMetadata, GradingReport, GradingRulesUpdateRequest, PlagiarismCheckResult

### Community 61 - "rewrite_openxml_core_metadata"
Cohesion: 0.19
Nodes (7): build_sample_xlsx(), _replace_zip_member(), rewrite_openxml_core_metadata(), _strip_zip_member(), test_antiplagiarism_detects_resaved_xlsx_without_core_xml_and_respects_single_variant(), _build_calc_xlsx(), _make_template_docx()

### Community 62 - "list_my_submissions"
Cohesion: 0.19
Nodes (5): download_submission_file(), get_submission_detail(), list_my_submissions(), list_submissions(), update_submission_grade()

### Community 64 - "SqliteAsyncSessionAdapter"
Cohesion: 0.15
Nodes (7): SqliteAsyncSessionAdapter, test_academic_group_course_year_restricted_to_1_through_4(), test_seed_database_sync_courses_preserves_users_and_groups(), _get_user_by_email(), test_admin_duplicate_group_list_number_returns_409_and_allows_other_groups(), test_delete_module_renumbers_cleanly_under_unique_constraint_with_reverse_uuids(), test_quiz_questions_preserve_order_index_independently_of_uuids()

### Community 65 - "html_grader.py"
Cohesion: 0.13
Nodes (9): _attribute_value_matches(), _find_tag_attr_key(), _get_tag_attribute_str(), _is_doctype_target(), _node_has_visible_content(), _normalize_text(), _parse_text_match_expected(), _strip_quotes() (+1 more)

### Community 66 - "networks"
Cohesion: 0.40
Nodes (5): driver, internal, networks, edge, internal

### Community 67 - "SubmissionRead"
Cohesion: 0.19
Nodes (3): SubmissionRead, _is_submission_file_available(), serialize_submission()

### Community 69 - "Settings"
Cohesion: 0.12
Nodes (4): get_settings(), _resolve_backend_path(), Settings, test_settings_production_rejects_default_or_short_jwt_secret()

### Community 70 - "test_course_content.py"
Cohesion: 0.11
Nodes (14): format_student_criterion_description(), AcademicGroup, build_seed_bundle(), run_seed(), seed_database(), SeedBundle, SeedSummary, summarize_bundle() (+6 more)

### Community 71 - "get_current_user"
Cohesion: 0.13
Nodes (5): get_current_user(), get_practical_for_teacher(), list_courses(), _serialize_course(), _serialize_practical_teacher()

### Community 72 - ".evaluate"
Cohesion: 0.15
Nodes (6): build_sample_accdb(), test_all_course_rules_pass_validate_rule_definition_and_access_modules_separated(), test_accdb_grader_accepts_hyperlink_type_as_memo(), test_accdb_grader_detects_missing_schema_elements_and_invalid_header(), test_accdb_grader_evaluates_access_module_9_multiple_variants(), test_accdb_grader_evaluates_tables_columns_and_types()

### Community 73 - "_FormulaEvalError"
Cohesion: 0.10
Nodes (17): _apply_binary_operator(), _coerce_formula_bool(), _coerce_formula_number(), _collect_logical_values(), _collect_numeric_values(), _eval_countif(), _eval_sumif(), _eval_vlookup() (+9 more)

### Community 74 - "test_change_password_validation_and_imported_student_flag"
Cohesion: 0.22
Nodes (5): _get_user_by_email(), test_change_password_validation_and_imported_student_flag(), test_login_rate_limiting_blocks_after_n_failures_and_resets_on_success(), test_long_cyrillic_password_create_login_and_change_without_500(), test_token_version_revokes_tokens_on_admin_reset_and_self_change()

### Community 75 - "@tanstack/react-query"
Cohesion: 0.18
Nodes (10): dependencies, lucide-react@^0.460.0, react@^18.3.1, react-dom@^18.3.1, react-router-dom@^6.28.0, @tanstack/react-query@^5.60.0, queryClient, rootElement (+2 more)

### Community 77 - "_strip_identifiers"
Cohesion: 0.12
Nodes (5): AccdbDatabaseSchema, _is_numeric_condition(), _normalize_count_condition(), _parse_relationship_pair_target(), _strip_identifiers()

### Community 78 - "_format_student_placeholder_value"
Cohesion: 0.25
Nodes (5): _format_margin_measurement(), _format_margins_value(), _replace(), _format_student_placeholder_value(), _format_uk_decimal()

### Community 80 - "do_run_migrations"
Cohesion: 0.29
Nodes (3): do_run_migrations(), run_async_migrations(), run_migrations_online()

### Community 83 - "_parse_msys_relationships_csv"
Cohesion: 0.32
Nodes (4): AccdbRelationshipSchema, _dedupe_relationships(), _parse_msys_relationships_csv(), _parse_msys_relationships_table()

### Community 85 - "_build_submission_download_names"
Cohesion: 0.29
Nodes (4): _build_submission_download_names(), _sanitize_ascii_token(), _sanitize_utf8_token(), _strip_apostrophes()

### Community 90 - "_FormulaParser"
Cohesion: 0.36
Nodes (4): _BinaryOpNode, _FormulaParser, _Token, _UnaryOpNode

### Community 93 - "test_hash_and_verify_password_async_offload_to_worker_thread"
Cohesion: 0.50
Nodes (3): test_hash_and_verify_password_async_offload_to_worker_thread(), _recording_hash(), _recording_verify()

### Community 95 - "serialize_submission"
Cohesion: 0.13
Nodes (5): PlagiarismDetectedError, _resolve_existing_submission_file(), _save_uploaded_file(), SubmissionService, _unlink_file_quietly()

### Community 99 - "_SeedCoursePayload"
Cohesion: 0.18
Nodes (4): _SeedCoursePayload, _SeedModulePayload, _SeedPracticalPayload, _SeedQuizQuestionPayload

### Community 100 - "metadata.py"
Cohesion: 0.09
Nodes (15): _canonicalize_xlsx_formula(), compute_bytes_sha256(), compute_text_shingles(), _extract_accdb_fingerprint(), _extract_accdb_table_via_mdb_export(), _extract_accdb_tables_via_mdbtools(), extract_document_metadata(), _extract_docx_fingerprint() (+7 more)

### Community 104 - "get_db"
Cohesion: 0.11
Nodes (20): ensure_course_owner_or_admin(), _collect_practical_submission_file_paths(), create_course(), create_module(), create_quiz_question(), delete_module(), delete_practical(), delete_quiz_question() (+12 more)

### Community 108 - "frontend"
Cohesion: 0.25
Nodes (8): condition, backend, container_name, depends_on, networks, ports, restart, frontend

### Community 110 - "backend"
Cohesion: 0.25
Nodes (8): container_name, depends_on, networks, restart, volumes, condition, db, backend

### Community 114 - ".import_students"
Cohesion: 0.11
Nodes (6): import_admin_students(), ImportedStudentItem, StudentImportResponse, build_credentials_report(), StudentImportService, test_build_credentials_report_uses_list_number_and_dynamic_variant_note()

### Community 141 - "healthcheck"
Cohesion: 0.48
Nodes (7): healthcheck, healthcheck, interval, retries, start_period, test, timeout

### Community 145 - "build"
Cohesion: 0.40
Nodes (6): VITE_API_BASE_URL, build, args, context, dockerfile, build

### Community 147 - "db"
Cohesion: 0.17
Nodes (11): container_name, image, networks, restart, volumes, name, services, db (+3 more)

### Community 153 - "InvalidFileFormatError"
Cohesion: 0.13
Nodes (11): InvalidFileFormatError, compute_code_sha256(), compute_file_sha256(), compute_submission_hash(), extract_core_xml_metadata(), normalize_code_for_hashing(), parse_core_xml_bytes(), validate_zip_archive_safety() (+3 more)

## Knowledge Gaps
- **1 isolated node(s):** `edu-auto-grader-backend`
  These have ≤1 connection - possible missing edges. (Counts symbols only; 1043 node(s) total have ≤1 connection when file, concept and rationale nodes are included.)
- **52 thin communities (<3 nodes) omitted from report** — run `graphify query` to explore isolated nodes.

## Suggested Questions
_Questions this graph is uniquely positioned to answer:_

- **Why does `User` connect `User` to `QuizService`, `test_auth_security.py`, `.execute`, `ExportService`, `v1/auth.py`, `make_auth_headers`, `admin.py`, `_get_student_and_word_practical`, `schemas/auth.py`, `export_service.py`, `courses.py`, `submission_service.py`, `student_import_service.py`, `_get_module_with_questions`, `build_sample_docx`, `ExtractedMetadata`, `SqliteAsyncSessionAdapter`, `SubmissionRead`, `test_course_content.py`, `get_current_user`, `test_change_password_validation_and_imported_student_flag`, `_build_submission_download_names`, `serialize_submission`, `get_db`, `.import_students`?**
  _High betweenness centrality (0.050) - this node is a cross-community bridge._
- **Are the 35 inferred relationships involving `SqliteAsyncSessionAdapter` (e.g. with `_get_user_by_email()` and `test_academic_group_course_year_restricted_to_1_through_4()`) actually correct?**
  _`SqliteAsyncSessionAdapter` has 35 INFERRED edges - model-reasoned connections that need verification._
- **What connects `edu-auto-grader-backend` to the rest of the system?**
  _1 weakly-connected nodes found - possible missing edges._
- **Should `QuizService` be split into smaller, more focused modules?**
  _Cohesion score 0.10752688172043011 - nodes in this community are weakly interconnected._
- **Why does `GradingError` connect `GradingError` to `accdb_grader.py`, `html_grader.py`, `metadata.py`, `xlsx_grader.py`, `.evaluate`, `_strip_identifiers`, `docx_grader.py`, `test_graders.py`, `submission_service.py`, `test_antiplagiarism_accdb_fingerprint_corrupt_safety_and_backward_compat`, `DomainError`, `serialize_submission`, `AccdbColumnSchema`, `InvalidFileFormatError`, `.build_criterion_result`, `ExtractedMetadata`, `XlsxGrader`, `HtmlGrader`?**
  _High betweenness centrality (0.045) - this node is a cross-community bridge._
- **Are the 31 inferred relationships involving `User` (e.g. with `ensure_course_owner_or_admin()` and `get_current_user()`) actually correct?**
  _`User` has 31 INFERRED edges - model-reasoned connections that need verification._
- **Should `postgres` be split into smaller, more focused modules?**
  _Cohesion score 0.10526315789473684 - nodes in this community are weakly interconnected._