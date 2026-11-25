# Graph Report - edu-auto-grader  (2026-11-25)

## Corpus Check
- 104 files · ~302,052 words
- Verdict: corpus is large enough that graph structure adds value.
- Unclassified: 14 file(s) not represented in the graph (top: (none) 9, .example 1, .ini 1)

## Summary
- 2345 nodes · 6804 edges · 91 communities (69 shown, 22 thin omitted)
- Extraction: 88% EXTRACTED · 12% INFERRED · 0% AMBIGUOUS · INFERRED: 817 edges (avg confidence: 0.93)
- Token cost: 0 input · 0 output

## Graph Freshness
- Built from commit: `9e2849c5`
- Run `git rev-parse HEAD` and compare to check if the graph is stale.
- Run `graphify update .` after code changes (no API cost).

## Community Hubs (Navigation)
- QuizService
- postgres
- compilerOptions
- User
- test_graders.py
- env
- analytics.py
- test_auth_security.py
- MarkdownRenderer.tsx
- vite-env.d.ts
- delete_submission_files_for_paths_async
- main
- ExportService
- v1/auth.py
- make_auth_headers
- GradingRuleType
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
- accdb_grader.py
- HtmlSandbox.tsx
- PracticalFormat
- xlsx_grader.py
- RuleBuilderPage.tsx
- UserRole
- GradingReportCard.tsx
- db_session
- export_service.py
- courses.py
- ModuleViewPage.tsx
- _collect_docx_body_fragments
- SlidingWindowRateLimiter
- retention_service.py
- export_service.py
- DomainError
- student_import_service.py
- test_antiplagiarism_accdb_fingerprint_corrupt_safety_and_backward_compat
- _get_module_with_questions
- DocxGrader
- _extract_html_fingerprint
- ExtractedMetadata
- SubmissionService
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
- BaseGrader
- do_run_migrations
- sqlalchemy
- submission_service.py
- test_read_upload_file_limited_stops_reading_chunks_early
- _tokenize_formula
- _FormulaParser
- Decimal
- _compile_jsonb_for_sqlite
- ._matches_expected_formula
- _enum_values
- _SeedCoursePayload
- metadata.py
- get_db
- frontend
- backend
- html_grader.py
- lifespan
- healthcheck
- build
- db
- _set_xlsx_text_cell
- backup.sh
- restore.sh

## God Nodes (most connected - your core abstractions)
1. `GradingRule` - 101 edges
2. `User` - 84 edges
3. `SqliteAsyncSessionAdapter` - 84 edges
4. `CourseSlug` - 78 edges
5. `DomainError` - 72 edges
6. `GradingError` - 62 edges
7. `PracticalFormat` - 57 edges
8. `DocxGrader` - 56 edges
9. `Module` - 55 edges
10. `make_auth_headers()` - 55 edges

## Surprising Connections (you probably didn't know these)
- `get_current_user()` --uses--> `User`  [INFERRED]
  backend/app/api/deps.py → backend/app/models/user.py
- `require_role()` --uses--> `User`  [INFERRED]
  backend/app/api/deps.py → backend/app/models/user.py
- `require_role()` --uses--> `UserRole`  [INFERRED]
  backend/app/api/deps.py → backend/app/models/user.py
- `ensure_course_owner_or_admin()` --uses--> `Course`  [INFERRED]
  backend/app/api/deps.py → backend/app/models/course.py
- `ensure_course_owner_or_admin()` --uses--> `User`  [INFERRED]
  backend/app/api/deps.py → backend/app/models/user.py

## Import Cycles
- None detected.

## Communities (91 total, 22 thin omitted)

### Community 0 - "QuizService"
Cohesion: 0.13
Nodes (6): _build_module_detail_read(), submit_module_quiz(), QuizSubmitRequest, QuizSubmitResponse, _ensure_utc(), QuizService

### Community 1 - "postgres"
Cohesion: 0.11
Nodes (18): POSTGRES_DB, POSTGRES_PASSWORD, POSTGRES_USER, interval, retries, test, timeout, container_name (+10 more)

### Community 2 - "compilerOptions"
Cohesion: 0.10
Nodes (20): compilerOptions, allowImportingTsExtensions, isolatedModules, jsx, lib, module, moduleDetection, moduleResolution (+12 more)

### Community 3 - "User"
Cohesion: 0.10
Nodes (15): Base, Course, Module, QuizQuestion, QuizAttempt, Submission, User, test_all_alembic_revisions_fit_varchar_32_and_form_single_linear_chain() (+7 more)

### Community 4 - "test_graders.py"
Cohesion: 0.10
Nodes (9): compute_shingle_jaccard(), DummySubmissionRecord, _strip_zip_member(), test_antiplagiarism_detects_html_copy_with_comment_and_renamed_css_classes(), test_antiplagiarism_detects_resaved_docx_without_core_xml_and_minor_edit(), test_antiplagiarism_detects_resaved_xlsx_without_core_xml_and_respects_single_variant(), _build_calc_xlsx(), test_antiplagiarism_no_false_positive_on_shared_template_and_classroom_creator() (+1 more)

### Community 5 - "env"
Cohesion: 0.06
Nodes (38): env, name, runs-on, services, steps, concurrency, cancel-in-progress, group (+30 more)

### Community 6 - "analytics.py"
Cohesion: 0.23
Nodes (3): export_group_journal(), get_group_journal(), list_academic_groups()

### Community 7 - "test_auth_security.py"
Cohesion: 0.09
Nodes (11): get_settings(), Settings, hash_password(), verify_password(), test_hash_and_verify_password_async_offload_to_worker_thread(), _recording_hash(), _recording_verify(), test_password_hashing_supports_long_cyrillic_and_legacy_bcrypt_hashes() (+3 more)

### Community 8 - "MarkdownRenderer.tsx"
Cohesion: 0.13
Nodes (30): dedentBlockLines(), findClosingDoubleStar(), findClosingParen(), findClosingSingleStar(), findMatchingBracket(), getAlignmentClass(), getLineIndent(), hasUnsafeControlChars() (+22 more)

### Community 11 - "delete_submission_files_for_paths_async"
Cohesion: 0.25
Nodes (5): delete_submission_file_safely(), delete_submission_file_safely_async(), delete_submission_files_for_paths(), delete_submission_files_for_paths_async(), resolve_submission_file_path()

### Community 14 - "ExportService"
Cohesion: 0.11
Nodes (4): ExportFormat, ExportedDocument, ExportService, GroupJournalBundle

### Community 15 - "v1/auth.py"
Cohesion: 0.06
Nodes (22): change_password(), _extract_client_ip(), login(), read_current_user(), refresh_tokens(), build_login_rate_limit_key(), create_token_pair(), verify_password_async() (+14 more)

### Community 16 - "make_auth_headers"
Cohesion: 0.09
Nodes (29): CourseSlug, build_sample_accdb(), build_sample_docx(), build_sample_xlsx(), make_auth_headers(), _replace_zip_member(), rewrite_openxml_core_metadata(), _get_course_module_and_practical() (+21 more)

### Community 17 - "GradingRuleType"
Cohesion: 0.07
Nodes (17): _canonicalize_formula(), GradingRuleType, test_excel_course_formula_rules_have_valid_supported_expressions(), test_word_module2_has_no_hidden_rules_and_matches_instructions(), _make_grading_report_dict(), test_accdb_grader_accepts_hyperlink_type_as_memo(), test_accdb_grader_detects_missing_schema_elements_and_invalid_header(), test_accdb_grader_evaluates_access_module_9_multiple_variants() (+9 more)

### Community 23 - "package.json"
Cohesion: 0.07
Nodes (39): devDependencies, autoprefixer@^10.4.20, eslint@^9.15.0, @eslint/js@^9.15.0, eslint-plugin-react-hooks@^5.0.0, eslint-plugin-react-refresh@^0.4.14, globals@^15.12.0, postcss@^8.4.49 (+31 more)

### Community 24 - "App.tsx"
Cohesion: 0.14
Nodes (30): App(), ProtectedAppLayout(), RoleHomeRedirect(), ChangePasswordModal(), ChangePasswordModalProps, Navbar(), NavbarProps, resolvePageTitle() (+22 more)

### Community 25 - "admin.py"
Cohesion: 0.07
Nodes (23): create_admin_group(), create_admin_user(), delete_admin_group(), delete_admin_user(), _ensure_email_unique(), _ensure_group_code_unique(), _ensure_group_list_number_unique(), _get_group_or_404() (+15 more)

### Community 26 - "AdminUsersPage.tsx"
Cohesion: 0.06
Nodes (43): AdminTab, AdminUsersPage(), buildCredentialsReportText(), CourseYearFilter, DeleteTarget, downloadCredentialsReportTxt(), FeedbackBanner, fetchAdminGroups() (+35 more)

### Community 27 - "course.ts"
Cohesion: 0.08
Nodes (42): COURSE_VISUAL_META, CourseVisualMeta, fetchCourses(), FilterOption, ModuleRowCard(), PRACTICAL_FORMAT_LABELS, CourseEditorPage(), deleteModuleById() (+34 more)

### Community 28 - "GroupJournalPage.tsx"
Cohesion: 0.20
Nodes (16): PlagiarismBadge(), PlagiarismBadgeProps, COURSE_SLUG_BADGES, extractBlobApiErrorMessage(), fetchAcademicGroups(), fetchCourses(), fetchGroupJournal(), fetchSubmissionDetail() (+8 more)

### Community 29 - "AuthContext.tsx"
Cohesion: 0.11
Nodes (31): axios@^1.7.7, API_BASE_URL, apiClient, AuthFailureListener, authFailureListeners, clearAuthTokens(), getAccessToken(), getRefreshToken() (+23 more)

### Community 32 - "environment"
Cohesion: 0.13
Nodes (17): environment, environment, APP_ENV, CORS_ORIGINS, ENABLE_RETENTION_CLEANUP_TASK, FORWARDED_ALLOW_IPS, JWT_SECRET_KEY, POSTGRES_DB (+9 more)

### Community 33 - "accdb_grader.py"
Cohesion: 0.08
Nodes (15): build_accdb_bytes(), _dedupe_names_casefold(), _encode_data_page(), _encode_msys_catalog_record(), _encode_tdef_page(), _encode_text_record(), _is_hidden_or_system_object(), _lookup_mapping_column() (+7 more)

### Community 34 - "HtmlSandbox.tsx"
Cohesion: 0.13
Nodes (17): @monaco-editor/react@4.6.0, buildDraftStorageKey(), buildStarterHtmlTemplate(), DraftSaveState, EditorColorTheme, formatDraftSavedTime(), HtmlSandbox(), HtmlSandboxProps (+9 more)

### Community 35 - "PracticalFormat"
Cohesion: 0.10
Nodes (10): InvalidFileFormatError, GraderFactory, compute_bytes_sha256(), compute_code_sha256(), compute_file_sha256(), compute_submission_hash(), normalize_code_for_hashing(), PracticalFormat (+2 more)

### Community 37 - "xlsx_grader.py"
Cohesion: 0.08
Nodes (14): _BoolNode, _CellRefNode, _count_non_empty_values(), _EmptyArgNode, _excel_wildcard_to_regex(), _FuncCallNode, _has_balanced_formula_delimiters(), _is_wrapped_in_parens() (+6 more)

### Community 38 - "RuleBuilderPage.tsx"
Cohesion: 0.19
Nodes (14): fetchCourses(), fetchPracticalTeacher(), FORMAT_BADGE_CONFIG, formatPointsCompact(), renderFormatIcon(), RULE_TYPE_SPECS, RuleBuilderPage(), RuleTypeSpec (+6 more)

### Community 39 - "UserRole"
Cohesion: 0.15
Nodes (7): create_access_token(), create_refresh_token(), decode_token(), _encode_jwt_token(), _sha256_password_bytes(), _enum_values(), UserRole

### Community 40 - "GradingReportCard.tsx"
Cohesion: 0.09
Nodes (31): COURSE_SLUG_LABELS, CriterionBreakdownItem(), CriterionFilterMode, extractFileNameFromPath(), FORMAT_META, formatDateTime(), GradingReportCard(), GradingReportCardProps (+23 more)

### Community 41 - "db_session"
Cohesion: 0.13
Nodes (5): async_client(), _create_sqlite_test_engine(), _set_sqlite_pragma(), db_session(), _fast_seed_hash_password()

### Community 42 - "export_service.py"
Cohesion: 0.10
Nodes (18): CriterionErrorStat, GroupJournalPracticalRead, GroupJournalRead, GroupJournalRow, GroupJournalStudentCell, HtmlSubmissionRequest, ManualGradeUpdateRequest, build_group_journal() (+10 more)

### Community 43 - "courses.py"
Cohesion: 0.12
Nodes (17): CourseCreate, CourseRead, CourseUpdate, GradingCriterionPreviewRead, ModuleCreate, ModuleDetailRead, ModuleSummaryRead, ModuleUpdate (+9 more)

### Community 44 - "ModuleViewPage.tsx"
Cohesion: 0.09
Nodes (39): renderInlineMarkdown(), AccessFieldDescriptor, AccessTableDescriptor, ALIGNMENT_DISPLAY_LABELS, BinaryPracticalFormat, extractRetryAfterSeconds(), fetchModuleDetail(), fetchStudentPractical() (+31 more)

### Community 45 - "_collect_docx_body_fragments"
Cohesion: 0.19
Nodes (6): _collect_docx_body_fragments(), _collect_docx_xml_table_texts(), _extract_docx_paragraph_xml_text(), _find_xml_text(), parse_core_xml_bytes(), test_core_xml_parser_rejects_xml_entity_expansion_billion_laughs()

### Community 48 - "retention_service.py"
Cohesion: 0.22
Nodes (7): cleanup_expired_submissions(), cleanup_superseded_submission_files(), _delete_submission_file_paths_with_stats(), _inspect_submission_file_paths(), _normalize_utc(), RetentionCleanupSummary, SupersededCleanupSummary

### Community 49 - "export_service.py"
Cohesion: 0.11
Nodes (13): calculate_criterion_error_stats(), _configure_pdf_font(), _fit_pdf_text(), _format_pdf_score(), _normalize_utc_timestamp(), _prepare_pdf_text(), render_group_journal_pdf(), _draw_page_header() (+5 more)

### Community 50 - "DomainError"
Cohesion: 0.08
Nodes (12): require_role(), role_checker(), _parse_export_format(), _extract_submission_payload(), ExtractedSubmissionPayload, DomainError, PlagiarismDetectedError, _build_too_large_exception() (+4 more)

### Community 51 - "student_import_service.py"
Cohesion: 0.05
Nodes (27): format_size_limit_mb(), ImportedStudentItem, ImportSkippedItem, StudentImportResponse, build_credentials_report(), build_generated_email(), _classify_header_cell(), _clean_whitespace() (+19 more)

### Community 53 - "test_antiplagiarism_accdb_fingerprint_corrupt_safety_and_backward_compat"
Cohesion: 0.25
Nodes (3): _fake_which(), test_antiplagiarism_accdb_fingerprint_corrupt_safety_and_backward_compat(), test_zip_bomb_protection_blocks_high_ratio_many_entries_and_oversized_uncompressed()

### Community 55 - "_get_module_with_questions"
Cohesion: 0.18
Nodes (8): _build_answers_for_score(), _get_module_with_questions(), _get_user_by_email(), test_excel_q42_imported_in_module_8_with_media_and_dry_run(), test_quiz_cooldown_zero_disables_wait_and_negative_config_rejected(), test_quiz_pass_threshold_setting_controls_passed_flag(), test_quiz_retry_cooldown_blocks_immediate_retry_and_unlocks_after_window(), test_quiz_submit_rejects_incomplete_duplicate_foreign_and_invalid_answers()

### Community 57 - "DocxGrader"
Cohesion: 0.06
Nodes (4): DocxGrader, _format_number(), CriterionResult, test_docx_grader_inherits_font_from_base_style_chain_and_doc_defaults()

### Community 59 - "_extract_html_fingerprint"
Cohesion: 0.12
Nodes (10): compute_text_shingles(), _extract_css_property_blocks(), _extract_docx_fingerprint(), _extract_html_fingerprint(), _extract_html_visible_text(), _walk(), _normalize_css_declarations(), _serialize_html_dom_structure() (+2 more)

### Community 60 - "ExtractedMetadata"
Cohesion: 0.10
Nodes (9): check_submission_plagiarism(), _clean_optional_str(), _coerce_metadata(), evaluate_plagiarism(), _is_content_fingerprint_match_actionable(), _is_generic_creator(), SubmissionRecordProtocol, ExtractedMetadata (+1 more)

### Community 62 - "SubmissionService"
Cohesion: 0.05
Nodes (17): _resolve_practical_upload_limit(), submit_practical_work(), update_practical_grading_rules(), download_submission_file(), get_submission_detail(), list_my_submissions(), list_submissions(), update_submission_grade() (+9 more)

### Community 63 - "GradingRule"
Cohesion: 0.05
Nodes (17): GradingError, _parse_relationship_pair_target(), has_meaningful_html_body(), HtmlGrader, _check_selector(), _is_doctype_target(), _normalize_selector(), parse_html_document() (+9 more)

### Community 64 - "SqliteAsyncSessionAdapter"
Cohesion: 0.07
Nodes (24): SqliteAsyncSessionAdapter, _get_user_by_email(), test_change_password_validation_and_imported_student_flag(), test_login_rate_limiting_blocks_after_n_failures_and_resets_on_success(), test_long_cyrillic_password_create_login_and_change_without_500(), test_token_version_revokes_tokens_on_admin_reset_and_self_change(), _copy_course_content_dir(), _get_user_by_email() (+16 more)

### Community 66 - "networks"
Cohesion: 0.40
Nodes (5): driver, internal, networks, edge, internal

### Community 70 - "seed.py"
Cohesion: 0.06
Nodes (28): Practical, AcademicGroup, build_seed_bundle(), _extract_needs_rules_review(), _load_course_from_json(), _question_signature(), run_seed(), seed_database() (+20 more)

### Community 71 - "get_current_user"
Cohesion: 0.15
Nodes (4): get_current_user(), get_module(), get_practical_for_student(), list_courses()

### Community 73 - "_FormulaEvalError"
Cohesion: 0.09
Nodes (18): _apply_binary_operator(), _coerce_formula_bool(), _coerce_formula_number(), _collect_logical_values(), _collect_numeric_values(), _eval_countif(), _eval_sumif(), _eval_vlookup() (+10 more)

### Community 75 - "@tanstack/react-query"
Cohesion: 0.18
Nodes (10): dependencies, lucide-react@^0.460.0, react@^18.3.1, react-dom@^18.3.1, react-router-dom@^6.28.0, @tanstack/react-query@^5.60.0, queryClient, rootElement (+2 more)

### Community 77 - "AccdbGrader"
Cohesion: 0.05
Nodes (14): AccdbColumnSchema, AccdbDatabaseSchema, AccdbGrader, AccdbObjectsCatalog, AccdbRelationshipSchema, AccdbTableSchema, _dedupe_relationships(), _find_named_entry() (+6 more)

### Community 78 - "BaseGrader"
Cohesion: 0.06
Nodes (10): BaseGrader, _format_margin_measurement(), _format_margins_value(), format_student_criterion_description(), _replace(), _format_student_placeholder_value(), _format_uk_decimal(), GradingReport (+2 more)

### Community 80 - "do_run_migrations"
Cohesion: 0.18
Nodes (4): do_run_migrations(), run_async_migrations(), run_migrations_offline(), run_migrations_online()

### Community 82 - "sqlalchemy"
Cohesion: 0.09
Nodes (10): downgrade(), upgrade(), downgrade(), upgrade(), downgrade(), upgrade(), downgrade(), upgrade() (+2 more)

### Community 85 - "submission_service.py"
Cohesion: 0.09
Nodes (13): QuizNotPassedError, PracticalVariant, build_content_disposition(), build_student_grading_criteria(), calculate_variant_index(), format_cooldown_remaining(), get_quiz_pass_threshold_percent(), resolve_student_variant() (+5 more)

### Community 87 - "test_read_upload_file_limited_stops_reading_chunks_early"
Cohesion: 0.50
Nodes (3): test_read_upload_file_limited_stops_reading_chunks_early(), __init__(), read()

### Community 90 - "_FormulaParser"
Cohesion: 0.36
Nodes (4): _BinaryOpNode, _FormulaParser, _Token, _UnaryOpNode

### Community 99 - "_SeedCoursePayload"
Cohesion: 0.18
Nodes (4): _SeedCoursePayload, _SeedModulePayload, _SeedPracticalPayload, _SeedQuizQuestionPayload

### Community 100 - "metadata.py"
Cohesion: 0.12
Nodes (12): _canonicalize_xlsx_formula(), _extract_accdb_fingerprint(), _extract_accdb_table_via_mdb_export(), _extract_accdb_tables_via_mdbtools(), extract_core_xml_metadata(), extract_document_metadata(), _extract_xlsx_fingerprint(), _extract_xlsx_formula_text() (+4 more)

### Community 104 - "get_db"
Cohesion: 0.10
Nodes (22): ensure_course_owner_or_admin(), _collect_practical_submission_file_paths(), create_course(), create_module(), create_quiz_question(), delete_module(), delete_practical(), delete_quiz_question() (+14 more)

### Community 108 - "frontend"
Cohesion: 0.25
Nodes (8): condition, backend, container_name, depends_on, networks, ports, restart, frontend

### Community 110 - "backend"
Cohesion: 0.25
Nodes (8): container_name, depends_on, networks, restart, volumes, condition, db, backend

### Community 116 - "html_grader.py"
Cohesion: 0.14
Nodes (8): _attribute_value_matches(), _find_tag_attr_key(), _get_tag_attribute_str(), _node_has_visible_content(), _normalize_text(), _parse_text_match_expected(), _strip_quotes(), _tag_has_attribute()

### Community 122 - "lifespan"
Cohesion: 0.22
Nodes (3): lifespan(), run_periodic_retention_cleanup(), test_lifespan_starts_and_cancels_retention_background_task()

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
  These have ≤1 connection - possible missing edges. (Counts symbols only; 1023 node(s) total have ≤1 connection when file, concept and rationale nodes are included.)
- **22 thin communities (<3 nodes) omitted from report** — run `graphify query` to explore isolated nodes.

## Suggested Questions
_Questions this graph is uniquely positioned to answer:_

- **Why does `GradingRule` connect `GradingRule` to `accdb_grader.py`, `_SeedCoursePayload`, `PracticalFormat`, `xlsx_grader.py`, `seed.py`, `User`, `get_db`, `test_graders.py`, `courses.py`, `AccdbGrader`, `BaseGrader`, `GradingRuleType`, `html_grader.py`, `submission_service.py`, `SubmissionService`, `DocxGrader`, `XlsxGrader`?**
  _High betweenness centrality (0.052) - this node is a cross-community bridge._
- **Are the 25 inferred relationships involving `GradingRule` (e.g. with `_serialize_practical_teacher()` and `AccdbGrader`) actually correct?**
  _`GradingRule` has 25 INFERRED edges - model-reasoned connections that need verification._
- **What connects `edu-auto-grader-backend` to the rest of the system?**
  _1 weakly-connected nodes found - possible missing edges._
- **Should `QuizService` be split into smaller, more focused modules?**
  _Cohesion score 0.12923076923076923 - nodes in this community are weakly interconnected._
- **Why does `GradingError` connect `GradingRule` to `._matches_expected_formula`, `accdb_grader.py`, `PracticalFormat`, `metadata.py`, `xlsx_grader.py`, `test_graders.py`, `AccdbGrader`, `BaseGrader`, `_collect_docx_body_fragments`, `DomainError`, `html_grader.py`, `submission_service.py`, `test_antiplagiarism_accdb_fingerprint_corrupt_safety_and_backward_compat`, `SubmissionService`, `DocxGrader`, `XlsxGrader`?**
  _High betweenness centrality (0.034) - this node is a cross-community bridge._
- **Are the 41 inferred relationships involving `User` (e.g. with `ensure_course_owner_or_admin()` and `get_current_user()`) actually correct?**
  _`User` has 41 INFERRED edges - model-reasoned connections that need verification._
- **Should `postgres` be split into smaller, more focused modules?**
  _Cohesion score 0.10526315789473684 - nodes in this community are weakly interconnected._