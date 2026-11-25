# Graph Report - edu-auto-grader  (2026-11-25)

## Corpus Check
- 97 files · ~282,607 words
- Verdict: corpus is large enough that graph structure adds value.
- Unclassified: 7 file(s) not represented in the graph (top: (none) 4, .ini 1, .mako 1)

## Summary
- 2112 nodes · 5885 edges · 169 communities (68 shown, 101 thin omitted)
- Extraction: 92% EXTRACTED · 8% INFERRED · 0% AMBIGUOUS · INFERRED: 469 edges (avg confidence: 0.91)
- Token cost: 0 input · 0 output

## Graph Freshness
- Built from commit: `8e7cfeec`
- Run `git rev-parse HEAD` and compare to check if the graph is stale.
- Run `graphify update .` after code changes (no API cost).

## Community Hubs (Navigation)
- QuizService
- postgres
- compilerOptions
- conftest.py
- AccdbGrader
- SubmissionService
- _find_named_entry
- test_db_indexes_and_constraints.py
- MarkdownRenderer.tsx
- vite-env.d.ts
- _get_user_by_email
- evaluate_plagiarism
- courses.py
- make_auth_headers
- submit_practical_work
- edu-auto-grader-backend
- change_password
- package.json
- App.tsx
- admin.py
- AdminUsersPage.tsx
- course.ts
- student_import_service.py
- AuthContext.tsx
- XlsxGrader
- 0002_restrict_course_year_to_4.py
- GroupJournalPage.tsx
- accdb_grader.py
- HtmlSandbox.tsx
- GradingError
- GradingReport
- schemas/__init__.py
- GradingRule
- GradingReportCard.tsx
- db_session
- export_service.py
- submission_service.py
- ModuleViewPage.tsx
- delete_admin_user
- SlidingWindowRateLimiter
- CourseSlug
- services/__init__.py
- @tanstack/react-query
- html_grader.py
- parse_docx_students
- export_group_journal
- _get_module_with_questions
- DocxGrader
- RuleBuilderPage.tsx
- GroupJournalRead
- DomainError
- list_my_submissions
- PracticalFormat
- User
- _get_user_by_email
- test_course_content.py
- test_auth_security.py
- math
- ExportService
- GradingRuleType
- rewrite_openxml_core_metadata
- do_run_migrations
- sqlalchemy
- xlsx_grader.py
- PracticalTeacherRead
- _FormulaParser
- test_graders.py
- read_upload_file_limited
- _build_module_detail_read
- _compile_jsonb_for_sqlite
- .submit_practical
- test_submissions_api.py
- get_db
- Settings
- compute_submission_hash
- AsyncSession
- ._check_submission_files_batch
- _build_submission_download_names
- _tokenize_formula
- ChangePasswordRequest
- .import_students

## God Nodes (most connected - your core abstractions)
1. `GradingRule` - 95 edges
2. `SqliteAsyncSessionAdapter` - 77 edges
3. `DomainError` - 67 edges
4. `User` - 66 edges
5. `CourseSlug` - 54 edges
6. `DocxGrader` - 52 edges
7. `GradingError` - 52 edges
8. `make_auth_headers()` - 49 edges
9. `Module` - 48 edges
10. `PracticalFormat` - 47 edges

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

## Communities (169 total, 101 thin omitted)

### Community 0 - "QuizService"
Cohesion: 0.13
Nodes (4): PracticalStudentRead, _ensure_utc(), get_quiz_pass_threshold_percent(), QuizService

### Community 1 - "postgres"
Cohesion: 0.10
Nodes (20): POSTGRES_DB, POSTGRES_PASSWORD, POSTGRES_USER, interval, retries, test, timeout, container_name (+12 more)

### Community 2 - "compilerOptions"
Cohesion: 0.10
Nodes (20): compilerOptions, allowImportingTsExtensions, isolatedModules, jsx, lib, module, moduleDetection, moduleResolution (+12 more)

### Community 3 - "conftest.py"
Cohesion: 0.10
Nodes (8): run_migrations_offline(), Base, _enum_values(), QuizAttempt, Submission, AcademicGroup, _fast_seed_hash_password(), test_all_alembic_revisions_fit_varchar_32_and_form_single_linear_chain()

### Community 4 - "AccdbGrader"
Cohesion: 0.06
Nodes (12): AccdbColumnSchema, AccdbDatabaseSchema, AccdbGrader, AccdbObjectsCatalog, AccdbTableSchema, _is_system_table_name(), build_sample_accdb(), test_all_course_rules_pass_validate_rule_definition_and_access_modules_separated() (+4 more)

### Community 7 - "test_db_indexes_and_constraints.py"
Cohesion: 0.10
Nodes (14): SqliteAsyncSessionAdapter, test_academic_group_course_year_restricted_to_1_through_4(), test_seed_database_sync_courses_preserves_users_and_groups(), _get_user_by_email(), test_admin_duplicate_group_list_number_returns_409_and_allows_other_groups(), test_delete_module_renumbers_cleanly_under_unique_constraint_with_reverse_uuids(), test_quiz_questions_preserve_order_index_independently_of_uuids(), test_schema_indexes_constraints_and_alembic_0004_backfill() (+6 more)

### Community 8 - "MarkdownRenderer.tsx"
Cohesion: 0.12
Nodes (31): dedentBlockLines(), findClosingDoubleStar(), findClosingParen(), findClosingSingleStar(), findMatchingBracket(), getAlignmentClass(), getLineIndent(), hasUnsafeControlChars() (+23 more)

### Community 11 - "_get_user_by_email"
Cohesion: 0.11
Nodes (11): _build_college_import_docx(), _get_user_by_email(), test_admin_academic_groups_crud_and_detachment(), test_admin_bulk_import_docx_sorts_ukrainian_alphabet_and_assigns_variants(), test_admin_bulk_import_rbac_and_validation_errors(), test_admin_bulk_import_returns_413_on_oversized_file_and_422_on_zip_bomb(), test_admin_bulk_import_txt_formats_continuing_list_number_and_duplicates(), test_admin_endpoints_enforce_admin_rbac() (+3 more)

### Community 13 - "evaluate_plagiarism"
Cohesion: 0.14
Nodes (5): check_submission_plagiarism(), _coerce_metadata(), evaluate_plagiarism(), SubmissionRecordProtocol, PlagiarismCheckResult

### Community 14 - "courses.py"
Cohesion: 0.23
Nodes (8): create_module(), _ensure_module_order_index_unique(), _fetch_user_progress_maps(), get_course(), _load_course_or_404(), _serialize_course(), update_course(), CourseRead

### Community 16 - "make_auth_headers"
Cohesion: 0.13
Nodes (17): make_auth_headers(), _get_course_module_and_practical(), _get_user_by_email(), _grant_quiz_pass(), test_antiplagiarism_flags_sha256_and_core_xml_matches_across_students(), test_best_score_unified_across_student_progress_and_group_journal_export(), test_download_submissions_by_course_teacher_and_admin_with_headers_and_content(), test_health_check_and_jwt_login_flow() (+9 more)

### Community 17 - "submit_practical_work"
Cohesion: 0.17
Nodes (3): _resolve_practical_upload_limit(), submit_practical_work(), update_practical_grading_rules()

### Community 22 - "change_password"
Cohesion: 0.07
Nodes (12): change_password(), _extract_client_ip(), login(), read_current_user(), refresh_tokens(), _extract_submission_payload(), ExtractedSubmissionPayload, create_access_token() (+4 more)

### Community 23 - "package.json"
Cohesion: 0.07
Nodes (41): @monaco-editor/react@4.6.0, devDependencies, autoprefixer@^10.4.20, eslint@^9.15.0, @eslint/js@^9.15.0, eslint-plugin-react-hooks@^5.0.0, eslint-plugin-react-refresh@^0.4.14, globals@^15.12.0 (+33 more)

### Community 24 - "App.tsx"
Cohesion: 0.15
Nodes (28): App(), ProtectedAppLayout(), RoleHomeRedirect(), ChangePasswordModal(), ChangePasswordModalProps, Navbar(), NavbarProps, resolvePageTitle() (+20 more)

### Community 25 - "admin.py"
Cohesion: 0.12
Nodes (13): create_admin_user(), _ensure_email_unique(), _ensure_group_code_unique(), _ensure_group_list_number_unique(), _get_group_or_404(), _get_user_with_group_or_404(), _normalize_email(), _normalize_non_empty() (+5 more)

### Community 26 - "AdminUsersPage.tsx"
Cohesion: 0.07
Nodes (44): RoleGuardProps, AdminTab, AdminUsersPage(), buildCredentialsReportText(), CourseYearFilter, DeleteTarget, downloadCredentialsReportTxt(), FeedbackBanner (+36 more)

### Community 27 - "course.ts"
Cohesion: 0.08
Nodes (42): apiClient, COURSE_VISUAL_META, CourseVisualMeta, fetchCourses(), FilterOption, ModuleRowCard(), PRACTICAL_FORMAT_LABELS, CourseEditorPage() (+34 more)

### Community 28 - "student_import_service.py"
Cohesion: 0.18
Nodes (5): build_generated_email(), _encode_ukrainian_word(), normalize_full_name(), ukrainian_sort_key(), test_ukrainian_alphabetical_sorting_and_apostrophe_normalization()

### Community 29 - "AuthContext.tsx"
Cohesion: 0.14
Nodes (25): API_BASE_URL, AuthFailureListener, authFailureListeners, clearAuthTokens(), getAccessToken(), getRefreshToken(), notifyAuthFailure(), refreshAccessToken() (+17 more)

### Community 30 - "XlsxGrader"
Cohesion: 0.11
Nodes (6): _coerce_formula_number(), _excel_round(), _FormulaEvalError, _require_single_number(), XlsxGrader, _eval()

### Community 32 - "GroupJournalPage.tsx"
Cohesion: 0.16
Nodes (18): PlagiarismBadge(), PlagiarismBadgeProps, COURSE_SLUG_BADGES, extractBlobApiErrorMessage(), fetchAcademicGroups(), fetchCourses(), fetchGroupJournal(), fetchSubmissionDetail() (+10 more)

### Community 33 - "accdb_grader.py"
Cohesion: 0.06
Nodes (20): AccdbRelationshipSchema, build_accdb_bytes(), _dedupe_names_casefold(), _dedupe_relationships(), _encode_data_page(), _encode_msys_catalog_record(), _encode_tdef_page(), _encode_text_record() (+12 more)

### Community 34 - "HtmlSandbox.tsx"
Cohesion: 0.18
Nodes (15): buildDraftStorageKey(), buildStarterHtmlTemplate(), DraftSaveState, EditorColorTheme, formatDraftSavedTime(), HtmlSandbox(), HtmlSandboxProps, PendingDraftState (+7 more)

### Community 35 - "GradingError"
Cohesion: 0.08
Nodes (5): GradingError, _parse_relationship_pair_target(), _strip_identifiers(), _check_selector(), _normalize_selector()

### Community 36 - "GradingReport"
Cohesion: 0.21
Nodes (4): GradingReport, SubmissionRead, _is_submission_file_available(), serialize_submission()

### Community 38 - "schemas/__init__.py"
Cohesion: 0.09
Nodes (19): AcademicGroupBase, AcademicGroupCreate, AcademicGroupRead, AcademicGroupUpdate, AdminResetPasswordRequest, AdminResetPasswordResponse, ChangePasswordResponse, ErrorResponse (+11 more)

### Community 39 - "GradingRule"
Cohesion: 0.08
Nodes (11): has_meaningful_html_body(), HtmlGrader, parse_html_document(), CriterionResult, GradingRule, test_minimal_html_starter_template_scores_zero_across_all_html_course_modules(), test_graders_validate_rule_definition_accepts_placeholders_and_rejects_invalid(), test_html_grader_attribute_filter_selector_and_compound_colspan() (+3 more)

### Community 40 - "GradingReportCard.tsx"
Cohesion: 0.10
Nodes (28): COURSE_SLUG_LABELS, CriterionBreakdownItem(), CriterionFilterMode, extractFileNameFromPath(), FORMAT_META, formatDateTime(), GradingReportCard(), GradingReportCardProps (+20 more)

### Community 41 - "db_session"
Cohesion: 0.15
Nodes (4): async_client(), _create_sqlite_test_engine(), _set_sqlite_pragma(), db_session()

### Community 42 - "export_service.py"
Cohesion: 0.09
Nodes (14): _parse_export_format(), CriterionErrorStat, ExportFormat, GroupJournalPracticalRead, GroupJournalRow, GroupJournalStudentCell, build_content_disposition(), build_group_journal() (+6 more)

### Community 43 - "submission_service.py"
Cohesion: 0.08
Nodes (16): CourseCreate, CourseUpdate, ModuleCreate, ModuleSummaryRead, ModuleUpdate, PracticalCreate, PracticalUpdate, PracticalVariant (+8 more)

### Community 44 - "ModuleViewPage.tsx"
Cohesion: 0.10
Nodes (34): AccessFieldDescriptor, AccessTableDescriptor, BinaryPracticalFormat, extractRetryAfterSeconds(), fetchModuleDetail(), fetchStudentPractical(), FILE_UPLOAD_FORMAT_META, FileUploadFormatMeta (+26 more)

### Community 45 - "delete_admin_user"
Cohesion: 0.13
Nodes (6): create_admin_group(), delete_admin_group(), delete_admin_user(), list_admin_groups(), list_admin_users(), reset_admin_user_password()

### Community 47 - "CourseSlug"
Cohesion: 0.15
Nodes (11): CourseSlug, build_sample_docx(), _copy_course_content_dir(), _get_user_by_email(), test_delete_module_and_practical_rbac_and_not_found(), test_delete_module_by_teacher_and_admin_cascades_cleans_files_and_renumbers(), test_delete_practical_preserves_module_lecture_quiz_and_cleans_files(), test_media_courses_static_serving() (+3 more)

### Community 48 - "services/__init__.py"
Cohesion: 0.12
Nodes (14): format_cooldown_remaining(), cleanup_expired_submissions(), _delete_submission_file_paths_with_stats(), delete_submission_file_safely(), delete_submission_file_safely_async(), delete_submission_files_for_paths(), delete_submission_files_for_paths_async(), _inspect_submission_file_paths() (+6 more)

### Community 49 - "@tanstack/react-query"
Cohesion: 0.17
Nodes (11): dependencies, axios@^1.7.7, lucide-react@^0.460.0, react@^18.3.1, react-dom@^18.3.1, react-router-dom@^6.28.0, @tanstack/react-query@^5.60.0, queryClient (+3 more)

### Community 50 - "html_grader.py"
Cohesion: 0.11
Nodes (9): _attribute_value_matches(), _find_tag_attr_key(), _get_tag_attribute_str(), _is_doctype_target(), _node_has_visible_content(), _normalize_text(), _parse_text_match_expected(), _strip_quotes() (+1 more)

### Community 51 - "parse_docx_students"
Cohesion: 0.10
Nodes (13): _classify_header_cell(), _clean_whitespace(), _detect_docx_header_columns(), _DocxColumnMap, _get_cell_value(), _infer_default_docx_columns(), _is_txt_header_line(), _normalize_header_token() (+5 more)

### Community 52 - "export_group_journal"
Cohesion: 0.19
Nodes (3): export_group_journal(), get_group_journal(), list_academic_groups()

### Community 55 - "_get_module_with_questions"
Cohesion: 0.17
Nodes (8): _build_answers_for_score(), _get_module_with_questions(), _get_user_by_email(), test_excel_q42_imported_in_module_8_with_media_and_dry_run(), test_quiz_cooldown_zero_disables_wait_and_negative_config_rejected(), test_quiz_pass_threshold_setting_controls_passed_flag(), test_quiz_retry_cooldown_blocks_immediate_retry_and_unlocks_after_window(), test_quiz_submit_rejects_incomplete_duplicate_foreign_and_invalid_answers()

### Community 57 - "DocxGrader"
Cohesion: 0.07
Nodes (3): DocxGrader, _format_number(), test_docx_grader_inherits_font_from_base_style_chain_and_doc_defaults()

### Community 58 - "RuleBuilderPage.tsx"
Cohesion: 0.20
Nodes (13): fetchCourses(), fetchPracticalTeacher(), FORMAT_BADGE_CONFIG, renderFormatIcon(), RULE_TYPE_SPECS, RuleBuilderPage(), RuleTypeSpec, CriterionResult (+5 more)

### Community 59 - "GroupJournalRead"
Cohesion: 0.13
Nodes (7): GroupJournalRead, _auto_adjust_worksheet_columns(), _configure_pdf_font(), GroupJournalBundle, PracticalColumnInfo, render_group_journal_pdf(), render_group_journal_xlsx()

### Community 60 - "DomainError"
Cohesion: 0.20
Nodes (4): role_checker(), DomainError, PlagiarismDetectedError, QuizNotPassedError

### Community 62 - "list_my_submissions"
Cohesion: 0.18
Nodes (5): download_submission_file(), get_submission_detail(), list_my_submissions(), list_submissions(), update_submission_grade()

### Community 66 - "PracticalFormat"
Cohesion: 0.13
Nodes (4): GraderFactory, PracticalFormat, test_docx_grader_evaluates_valid_document(), test_grader_factory_resolves_all_four_formats()

### Community 68 - "User"
Cohesion: 0.10
Nodes (9): require_role(), verify_password_async(), create_application(), lifespan(), _enum_values(), User, UserRole, calculate_variant_index() (+1 more)

### Community 69 - "_get_user_by_email"
Cohesion: 0.20
Nodes (5): _get_user_by_email(), test_change_password_validation_and_imported_student_flag(), test_login_rate_limiting_blocks_after_n_failures_and_resets_on_success(), test_long_cyrillic_password_create_login_and_change_without_500(), test_token_version_revokes_tokens_on_admin_reset_and_self_change()

### Community 70 - "test_course_content.py"
Cohesion: 0.08
Nodes (23): hash_password(), Course, Module, Practical, QuizQuestion, build_seed_bundle(), _extract_needs_rules_review(), _load_course_from_json() (+15 more)

### Community 72 - "test_auth_security.py"
Cohesion: 0.13
Nodes (7): build_login_rate_limit_key(), _sha256_password_bytes(), verify_password(), test_hash_and_verify_password_async_offload_to_worker_thread(), _recording_hash(), _recording_verify(), test_password_hashing_supports_long_cyrillic_and_legacy_bcrypt_hashes()

### Community 73 - "math"
Cohesion: 0.10
Nodes (13): _apply_binary_operator(), _coerce_formula_bool(), _collect_numeric_values(), _eval_countif(), _eval_sumif(), _eval_vlookup(), _excel_compare(), _excel_wildcard_to_regex() (+5 more)

### Community 77 - "GradingRuleType"
Cohesion: 0.06
Nodes (10): BaseGrader, GradingRuleType, test_docx_grader_detects_formatting_violations_and_corrupt_files(), test_docx_grader_resolves_placeholders_in_target_and_expected(), test_docx_grader_supports_uniform_single_number_margin(), test_docx_grader_table_exists_supports_rxc_and_rows_cols_conditions(), test_xlsx_grader_evaluates_formulas_values_and_charts(), test_xlsx_grader_evaluates_uncached_complex_cross_sheet_and_localized_formulas() (+2 more)

### Community 78 - "rewrite_openxml_core_metadata"
Cohesion: 0.28
Nodes (4): build_sample_xlsx(), _replace_zip_member(), rewrite_openxml_core_metadata(), test_core_xml_parser_rejects_xml_entity_expansion_billion_laughs()

### Community 80 - "do_run_migrations"
Cohesion: 0.29
Nodes (3): do_run_migrations(), run_async_migrations(), run_migrations_online()

### Community 82 - "sqlalchemy"
Cohesion: 0.11
Nodes (8): downgrade(), upgrade(), downgrade(), upgrade(), downgrade(), upgrade(), downgrade(), upgrade()

### Community 84 - "xlsx_grader.py"
Cohesion: 0.07
Nodes (17): _BoolNode, _canonicalize_formula(), _CellRefNode, _collect_logical_values(), _count_non_empty_values(), _EmptyArgNode, _format_cell_value(), _FuncCallNode (+9 more)

### Community 88 - "PracticalTeacherRead"
Cohesion: 0.28
Nodes (4): get_practical_for_teacher(), _serialize_practical_teacher(), update_practical(), PracticalTeacherRead

### Community 90 - "_FormulaParser"
Cohesion: 0.36
Nodes (4): _BinaryOpNode, _FormulaParser, _Token, _UnaryOpNode

### Community 91 - "test_graders.py"
Cohesion: 0.17
Nodes (7): extract_core_xml_metadata(), extract_document_metadata(), validate_zip_archive_safety(), ExtractedMetadata, DummySubmissionRecord, test_metadata_extraction_and_plagiarism_detection(), test_zip_bomb_protection_blocks_high_ratio_many_entries_and_oversized_uncompressed()

### Community 92 - "read_upload_file_limited"
Cohesion: 0.17
Nodes (6): _build_too_large_exception(), format_size_limit_mb(), read_upload_file_limited(), test_read_upload_file_limited_stops_reading_chunks_early(), __init__(), read()

### Community 93 - "_build_module_detail_read"
Cohesion: 0.18
Nodes (6): _build_module_detail_read(), update_module(), ModuleDetailRead, PracticalSummaryRead, QuizQuestionRead, QuizQuestionTeacherRead

### Community 97 - "get_db"
Cohesion: 0.14
Nodes (6): get_current_user(), get_module(), get_practical_for_student(), list_courses(), submit_module_quiz(), get_db()

### Community 99 - "Settings"
Cohesion: 0.08
Nodes (8): get_settings(), _resolve_backend_path(), Settings, _SeedCoursePayload, _SeedModulePayload, _SeedPracticalPayload, _SeedQuizQuestionPayload, test_settings_production_rejects_default_or_short_jwt_secret()

### Community 100 - "compute_submission_hash"
Cohesion: 0.19
Nodes (8): InvalidFileFormatError, compute_bytes_sha256(), compute_code_sha256(), compute_file_sha256(), compute_submission_hash(), _find_xml_text(), normalize_code_for_hashing(), parse_core_xml_bytes()

### Community 104 - "AsyncSession"
Cohesion: 0.15
Nodes (10): ensure_course_owner_or_admin(), _collect_practical_submission_file_paths(), create_course(), create_quiz_question(), delete_module(), delete_practical(), delete_quiz_question(), list_module_quiz_questions_teacher() (+2 more)

### Community 106 - "_build_submission_download_names"
Cohesion: 0.25
Nodes (4): transliterate_ukrainian_slug(), _sanitize_ascii_token(), _sanitize_utf8_token(), _strip_apostrophes()

### Community 114 - ".import_students"
Cohesion: 0.11
Nodes (3): import_admin_students(), generate_temp_password(), StudentImportService

## Knowledge Gaps
- **1 isolated node(s):** `edu-auto-grader-backend`
  These have ≤1 connection - possible missing edges. (Counts symbols only; 960 node(s) total have ≤1 connection when file, concept and rationale nodes are included.)
- **101 thin communities (<3 nodes) omitted from report** — run `graphify query` to explore isolated nodes.

## Suggested Questions
_Questions this graph is uniquely positioned to answer:_

- **Why does `GradingRule` connect `GradingRule` to `AccdbGrader`, `SubmissionService`, `evaluate_plagiarism`, `courses.py`, `XlsxGrader`, `accdb_grader.py`, `GradingError`, `schemas/__init__.py`, `submission_service.py`, `html_grader.py`, `DocxGrader`, `._evaluate_chart_exists`, `PracticalFormat`, `test_course_content.py`, `GradingRuleType`, `xlsx_grader.py`, `PracticalTeacherRead`, `test_graders.py`, `.submit_practical`, `docx_grader.py`, `Settings`?**
  _High betweenness centrality (0.058) - this node is a cross-community bridge._
- **Are the 20 inferred relationships involving `GradingRule` (e.g. with `_serialize_practical_teacher()` and `AccdbGrader`) actually correct?**
  _`GradingRule` has 20 INFERRED edges - model-reasoned connections that need verification._
- **What connects `edu-auto-grader-backend` to the rest of the system?**
  _1 weakly-connected nodes found - possible missing edges._
- **Should `QuizService` be split into smaller, more focused modules?**
  _Cohesion score 0.13405797101449277 - nodes in this community are weakly interconnected._
- **Why does `XlsxGrader` connect `XlsxGrader` to `PracticalFormat`, `GradingError`, `compute_submission_hash`, `GradingReport`, `test_course_content.py`, `GradingRule`, `GradingRuleType`, `xlsx_grader.py`, `test_graders.py`, `._evaluate_chart_exists`?**
  _High betweenness centrality (0.038) - this node is a cross-community bridge._
- **Are the 9 inferred relationships involving `User` (e.g. with `ensure_course_owner_or_admin()` and `get_current_user()`) actually correct?**
  _`User` has 9 INFERRED edges - model-reasoned connections that need verification._
- **Should `postgres` be split into smaller, more focused modules?**
  _Cohesion score 0.09523809523809523 - nodes in this community are weakly interconnected._