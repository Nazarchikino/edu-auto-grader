# Graph Report - edu-auto-grader  (2026-11-25)

## Corpus Check
- 96 files · ~277,897 words
- Verdict: corpus is large enough that graph structure adds value.
- Unclassified: 7 file(s) not represented in the graph (top: (none) 4, .ini 1, .mako 1)

## Summary
- 2066 nodes · 5629 edges · 139 communities (61 shown, 78 thin omitted)
- Extraction: 94% EXTRACTED · 6% INFERRED · 0% AMBIGUOUS · INFERRED: 319 edges (avg confidence: 0.9)
- Token cost: 0 input · 0 output

## Graph Freshness
- Built from commit: `7f07ea42`
- Run `git rev-parse HEAD` and compare to check if the graph is stale.
- Run `graphify update .` after code changes (no API cost).

## Community Hubs (Navigation)
- QuizService
- postgres
- compilerOptions
- conftest.py
- AccdbGrader
- SubmissionService
- GradingRule
- test_db_indexes_and_constraints.py
- MarkdownRenderer.tsx
- vite-env.d.ts
- _get_user_by_email
- evaluate_plagiarism
- AsyncSession
- SqliteAsyncSessionAdapter
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
- student_import_service.py
- serialize_submission
- submission_service.py
- HtmlGrader
- GradingReportCard.tsx
- db_session
- calculate_criterion_error_stats
- courses.py
- ModuleViewPage.tsx
- delete_admin_user
- SlidingWindowRateLimiter
- services/__init__.py
- @tanstack/react-query
- admin.py
- parse_docx_students
- export_group_journal
- DocxGrader
- render_group_journal_pdf
- DomainError
- get_settings
- list_my_submissions
- GradingError
- create_application
- test_course_content.py
- test_auth_security.py
- _FormulaEvalError
- ExportService
- test_graders.py
- do_run_migrations
- 0001_initial_schema.py
- xlsx_grader.py
- courses.py
- _FormulaParser
- metadata.py
- read_upload_file_limited
- create_quiz_question
- _compile_jsonb_for_sqlite
- .submit_practical
- _resolve_backend_path
- get_current_user
- _enum_values
- _SeedQuizQuestionPayload
- compute_submission_hash
- get_db
- ensure_course_owner_or_admin
- _canonicalize_formula
- _build_submission_download_names
- UUID
- .import_students
- create_admin_group
- .update_grading_rules
- 0004_add_indexes_constraints_and_quiz_order.py
- SubmissionDownloadPayload

## God Nodes (most connected - your core abstractions)
1. `SqliteAsyncSessionAdapter` - 75 edges
2. `User` - 70 edges
3. `DomainError` - 67 edges
4. `GradingRule` - 62 edges
5. `DocxGrader` - 50 edges
6. `make_auth_headers()` - 48 edges
7. `get_db()` - 45 edges
8. `GradingError` - 43 edges
9. `XlsxGrader` - 40 edges
10. `InvalidFileFormatError` - 40 edges

## Surprising Connections (you probably didn't know these)
- `AccdbGrader` --uses--> `CriterionResult`  [INFERRED]
  backend/app/graders/accdb_grader.py → backend/app/schemas/grading.py
- `AccdbGrader` --uses--> `GradingReport`  [INFERRED]
  backend/app/graders/accdb_grader.py → backend/app/schemas/grading.py
- `AccdbGrader` --uses--> `GradingRule`  [INFERRED]
  backend/app/graders/accdb_grader.py → backend/app/schemas/grading.py
- `AccdbGrader` --uses--> `GradingRuleType`  [INFERRED]
  backend/app/graders/accdb_grader.py → backend/app/schemas/grading.py
- `test_grader_factory_resolves_all_four_formats()` --uses--> `AccdbGrader`  [INFERRED]
  backend/tests/test_graders.py → backend/app/graders/accdb_grader.py

## Import Cycles
- None detected.

## Communities (139 total, 78 thin omitted)

### Community 0 - "QuizService"
Cohesion: 0.11
Nodes (5): _build_module_detail_read(), ModuleDetailRead, PracticalSummaryRead, get_quiz_pass_threshold_percent(), QuizService

### Community 1 - "postgres"
Cohesion: 0.10
Nodes (20): POSTGRES_DB, POSTGRES_PASSWORD, POSTGRES_USER, interval, retries, test, timeout, container_name (+12 more)

### Community 2 - "compilerOptions"
Cohesion: 0.10
Nodes (20): compilerOptions, allowImportingTsExtensions, isolatedModules, jsx, lib, module, moduleDetection, moduleResolution (+12 more)

### Community 4 - "AccdbGrader"
Cohesion: 0.07
Nodes (11): AccdbColumnSchema, AccdbGrader, AccdbObjectsCatalog, AccdbTableSchema, _dedupe_relationships(), _is_system_table_name(), build_sample_accdb(), test_accdb_grader_accepts_hyperlink_type_as_memo() (+3 more)

### Community 6 - "GradingRule"
Cohesion: 0.08
Nodes (8): AccdbDatabaseSchema, _find_named_entry(), _is_numeric_condition(), _normalize_count_condition(), _parse_relationship_pair_target(), _strip_identifiers(), CriterionResult, GradingRule

### Community 7 - "test_db_indexes_and_constraints.py"
Cohesion: 0.10
Nodes (12): hash_password(), test_seed_database_sync_courses_preserves_users_and_groups(), _get_user_by_email(), test_admin_duplicate_group_list_number_returns_409_and_allows_other_groups(), test_all_alembic_revisions_fit_varchar_32_and_form_single_linear_chain(), test_delete_module_renumbers_cleanly_under_unique_constraint_with_reverse_uuids(), test_quiz_questions_preserve_order_index_independently_of_uuids(), _create_other_teacher() (+4 more)

### Community 8 - "MarkdownRenderer.tsx"
Cohesion: 0.13
Nodes (30): dedentBlockLines(), findClosingDoubleStar(), findClosingParen(), findClosingSingleStar(), findMatchingBracket(), getAlignmentClass(), getLineIndent(), hasUnsafeControlChars() (+22 more)

### Community 11 - "_get_user_by_email"
Cohesion: 0.10
Nodes (14): calculate_variant_index(), resolve_student_variant(), _build_college_import_docx(), _get_user_by_email(), test_academic_group_course_year_restricted_to_1_through_4(), test_admin_academic_groups_crud_and_detachment(), test_admin_bulk_import_docx_sorts_ukrainian_alphabet_and_assigns_variants(), test_admin_bulk_import_rbac_and_validation_errors() (+6 more)

### Community 13 - "evaluate_plagiarism"
Cohesion: 0.17
Nodes (4): check_submission_plagiarism(), _coerce_metadata(), evaluate_plagiarism(), SubmissionRecordProtocol

### Community 14 - "AsyncSession"
Cohesion: 0.23
Nodes (6): _fetch_user_progress_maps(), get_course(), list_courses(), _load_course_or_404(), _serialize_course(), update_course()

### Community 16 - "SqliteAsyncSessionAdapter"
Cohesion: 0.05
Nodes (39): Settings, HtmlSubmissionRequest, build_sample_docx(), make_auth_headers(), SqliteAsyncSessionAdapter, _get_user_by_email(), test_change_password_validation_and_imported_student_flag(), test_long_cyrillic_password_create_login_and_change_without_500() (+31 more)

### Community 17 - "submit_practical_work"
Cohesion: 0.11
Nodes (6): _extract_client_ip(), _extract_submission_payload(), ExtractedSubmissionPayload, _resolve_practical_upload_limit(), submit_practical_work(), update_practical_grading_rules()

### Community 22 - "change_password"
Cohesion: 0.09
Nodes (9): change_password(), login(), read_current_user(), refresh_tokens(), build_login_rate_limit_key(), create_access_token(), create_refresh_token(), create_token_pair() (+1 more)

### Community 23 - "package.json"
Cohesion: 0.07
Nodes (41): @monaco-editor/react@4.6.0, devDependencies, autoprefixer@^10.4.20, eslint@^9.15.0, @eslint/js@^9.15.0, eslint-plugin-react-hooks@^5.0.0, eslint-plugin-react-refresh@^0.4.14, globals@^15.12.0 (+33 more)

### Community 24 - "App.tsx"
Cohesion: 0.15
Nodes (28): App(), ProtectedAppLayout(), RoleHomeRedirect(), ChangePasswordModal(), ChangePasswordModalProps, Navbar(), NavbarProps, resolvePageTitle() (+20 more)

### Community 25 - "admin.py"
Cohesion: 0.15
Nodes (7): create_admin_user(), _ensure_email_unique(), _ensure_group_list_number_unique(), _get_user_with_group_or_404(), _normalize_email(), _raise_user_conflict_from_integrity_error(), update_admin_user()

### Community 26 - "AdminUsersPage.tsx"
Cohesion: 0.06
Nodes (47): AdminTab, AdminUsersPage(), buildCredentialsReportText(), CourseYearFilter, DeleteTarget, downloadCredentialsReportTxt(), FeedbackBanner, fetchAdminGroups() (+39 more)

### Community 27 - "course.ts"
Cohesion: 0.07
Nodes (50): PracticalModuleContext, CourseEditorPage(), deleteModuleById(), deletePracticalById(), DeleteTarget, DISCIPLINE_META, DisciplineMeta, EditorTab (+42 more)

### Community 28 - "student_import_service.py"
Cohesion: 0.16
Nodes (6): build_generated_email(), _encode_ukrainian_word(), normalize_full_name(), transliterate_ukrainian_slug(), ukrainian_sort_key(), test_ukrainian_alphabetical_sorting_and_apostrophe_normalization()

### Community 29 - "AuthContext.tsx"
Cohesion: 0.14
Nodes (25): API_BASE_URL, AuthFailureListener, authFailureListeners, clearAuthTokens(), getAccessToken(), getRefreshToken(), notifyAuthFailure(), refreshAccessToken() (+17 more)

### Community 32 - "GroupJournalPage.tsx"
Cohesion: 0.13
Nodes (24): apiClient, PlagiarismBadge(), PlagiarismBadgeProps, extractApiErrorMessage(), COURSE_VISUAL_META, CoursesPage(), CourseVisualMeta, fetchCourses() (+16 more)

### Community 33 - "accdb_grader.py"
Cohesion: 0.07
Nodes (17): AccdbRelationshipSchema, build_accdb_bytes(), _dedupe_names_casefold(), _encode_data_page(), _encode_msys_catalog_record(), _encode_tdef_page(), _encode_text_record(), _is_hidden_or_system_object() (+9 more)

### Community 34 - "HtmlSandbox.tsx"
Cohesion: 0.18
Nodes (15): buildDraftStorageKey(), buildStarterHtmlTemplate(), DraftSaveState, EditorColorTheme, formatDraftSavedTime(), HtmlSandbox(), HtmlSandboxProps, PendingDraftState (+7 more)

### Community 35 - "student_import_service.py"
Cohesion: 0.18
Nodes (6): _classify_header_cell(), _detect_docx_header_columns(), _DocxColumnMap, _infer_default_docx_columns(), _is_txt_header_line(), _normalize_header_token()

### Community 36 - "serialize_submission"
Cohesion: 0.16
Nodes (5): _check_files_exist_batch(), _is_submission_file_available(), _resolve_existing_submission_file(), serialize_submission(), test_check_files_exist_batch_handles_existing_missing_and_path_traversal()

### Community 38 - "submission_service.py"
Cohesion: 0.05
Nodes (29): downgrade(), upgrade(), require_role(), PlagiarismDetectedError, QuizNotPassedError, decode_token(), format_size_limit_mb(), _enum_values() (+21 more)

### Community 39 - "HtmlGrader"
Cohesion: 0.06
Nodes (17): _attribute_value_matches(), _find_tag_attr_key(), _get_tag_attribute_str(), has_meaningful_html_body(), HtmlGrader, _is_doctype_target(), _node_has_visible_content(), _normalize_selector() (+9 more)

### Community 40 - "GradingReportCard.tsx"
Cohesion: 0.11
Nodes (24): COURSE_SLUG_LABELS, CriterionBreakdownItem(), CriterionFilterMode, extractFileNameFromPath(), FORMAT_META, formatDateTime(), GradingReportCard(), GradingReportCardProps (+16 more)

### Community 41 - "db_session"
Cohesion: 0.10
Nodes (8): async_client(), build_sample_xlsx(), _create_sqlite_test_engine(), _set_sqlite_pragma(), db_session(), _fast_seed_hash_password(), _replace_zip_member(), rewrite_openxml_core_metadata()

### Community 42 - "calculate_criterion_error_stats"
Cohesion: 0.25
Nodes (3): calculate_criterion_error_stats(), _normalize_utc_timestamp(), _RuleStatAccumulator

### Community 43 - "courses.py"
Cohesion: 0.08
Nodes (21): CourseCreate, CourseUpdate, ModuleCreate, ModuleUpdate, PracticalCreate, PracticalStudentRead, PracticalUpdate, PracticalVariant (+13 more)

### Community 44 - "ModuleViewPage.tsx"
Cohesion: 0.10
Nodes (34): renderInlineMarkdown(), AccessFieldDescriptor, AccessTableDescriptor, BinaryPracticalFormat, extractRetryAfterSeconds(), fetchModuleDetail(), fetchStudentPractical(), FILE_UPLOAD_FORMAT_META (+26 more)

### Community 45 - "delete_admin_user"
Cohesion: 0.17
Nodes (4): delete_admin_group(), delete_admin_user(), list_admin_groups(), list_admin_users()

### Community 48 - "services/__init__.py"
Cohesion: 0.13
Nodes (13): format_cooldown_remaining(), cleanup_expired_submissions(), _delete_submission_file_paths_with_stats(), delete_submission_file_safely(), delete_submission_file_safely_async(), delete_submission_files_for_paths(), delete_submission_files_for_paths_async(), _inspect_submission_file_paths() (+5 more)

### Community 49 - "@tanstack/react-query"
Cohesion: 0.17
Nodes (11): dependencies, axios@^1.7.7, lucide-react@^0.460.0, react@^18.3.1, react-dom@^18.3.1, react-router-dom@^6.28.0, @tanstack/react-query@^5.60.0, queryClient (+3 more)

### Community 50 - "admin.py"
Cohesion: 0.14
Nodes (7): reset_admin_user_password(), serialize_user(), hash_password_async(), AcademicGroupBase, AcademicGroupCreate, AdminResetPasswordResponse, generate_temp_password()

### Community 51 - "parse_docx_students"
Cohesion: 0.12
Nodes (10): validate_zip_archive_safety(), ImportSkippedItem, _clean_whitespace(), _get_cell_value(), parse_docx_students(), parse_txt_students(), ParsedStudentCandidate, _strip_placeholder() (+2 more)

### Community 52 - "export_group_journal"
Cohesion: 0.13
Nodes (5): export_group_journal(), get_group_journal(), list_academic_groups(), _parse_export_format(), ExportFormat

### Community 57 - "DocxGrader"
Cohesion: 0.05
Nodes (3): DocxGrader, _format_number(), test_all_course_variants_resolve_rule_placeholders_without_leftovers()

### Community 59 - "render_group_journal_pdf"
Cohesion: 0.10
Nodes (9): _auto_adjust_worksheet_columns(), _configure_pdf_font(), ExportedDocument, PracticalColumnInfo, _prepare_pdf_text(), render_group_journal_pdf(), render_group_journal_xlsx(), _sanitize_filename_token() (+1 more)

### Community 60 - "DomainError"
Cohesion: 0.14
Nodes (7): role_checker(), create_module(), _ensure_module_order_index_unique(), get_module(), _load_module_or_404(), update_module(), DomainError

### Community 62 - "list_my_submissions"
Cohesion: 0.18
Nodes (5): download_submission_file(), get_submission_detail(), list_my_submissions(), list_submissions(), update_submission_grade()

### Community 66 - "GradingError"
Cohesion: 0.07
Nodes (6): GradingError, InvalidFileFormatError, BaseGrader, GraderFactory, PracticalFormat, GradingReport

### Community 68 - "create_application"
Cohesion: 0.18
Nodes (3): create_application(), lifespan(), test_lifespan_starts_and_cancels_retention_background_task()

### Community 70 - "test_course_content.py"
Cohesion: 0.08
Nodes (26): Base, Course, CourseSlug, Module, Practical, QuizQuestion, QuizAttempt, Submission (+18 more)

### Community 72 - "test_auth_security.py"
Cohesion: 0.11
Nodes (9): _sha256_password_bytes(), verify_password(), verify_password_async(), test_hash_and_verify_password_async_offload_to_worker_thread(), _recording_hash(), _recording_verify(), test_login_rate_limiting_blocks_after_n_failures_and_resets_on_success(), test_password_hashing_supports_long_cyrillic_and_legacy_bcrypt_hashes() (+1 more)

### Community 73 - "_FormulaEvalError"
Cohesion: 0.09
Nodes (18): _apply_binary_operator(), _coerce_formula_bool(), _coerce_formula_number(), _collect_logical_values(), _collect_numeric_values(), _eval_countif(), _eval_sumif(), _eval_vlookup() (+10 more)

### Community 77 - "test_graders.py"
Cohesion: 0.09
Nodes (12): GradingRuleType, test_docx_grader_detects_formatting_violations_and_corrupt_files(), test_docx_grader_evaluates_valid_document(), test_docx_grader_inherits_font_from_base_style_chain_and_doc_defaults(), test_docx_grader_resolves_placeholders_in_target_and_expected(), test_docx_grader_supports_uniform_single_number_margin(), test_grader_factory_resolves_all_four_formats(), test_html_grader_empty_body_and_starter_template_score_zero() (+4 more)

### Community 80 - "do_run_migrations"
Cohesion: 0.29
Nodes (3): do_run_migrations(), run_async_migrations(), run_migrations_online()

### Community 84 - "xlsx_grader.py"
Cohesion: 0.10
Nodes (13): _BoolNode, _CellRefNode, _count_non_empty_values(), _EmptyArgNode, _excel_wildcard_to_regex(), _FuncCallNode, _normalize_cell_coord(), _NumberNode (+5 more)

### Community 88 - "courses.py"
Cohesion: 0.15
Nodes (7): get_practical_for_teacher(), _serialize_practical_teacher(), update_practical(), upsert_module_practical(), CourseRead, ModuleSummaryRead, PracticalTeacherRead

### Community 90 - "_FormulaParser"
Cohesion: 0.36
Nodes (4): _BinaryOpNode, _FormulaParser, _Token, _UnaryOpNode

### Community 91 - "metadata.py"
Cohesion: 0.18
Nodes (6): extract_core_xml_metadata(), extract_document_metadata(), _find_xml_text(), parse_core_xml_bytes(), ExtractedMetadata, test_core_xml_parser_rejects_xml_entity_expansion_billion_laughs()

### Community 92 - "read_upload_file_limited"
Cohesion: 0.20
Nodes (5): _build_too_large_exception(), read_upload_file_limited(), test_read_upload_file_limited_stops_reading_chunks_early(), __init__(), read()

### Community 93 - "create_quiz_question"
Cohesion: 0.22
Nodes (4): create_quiz_question(), list_module_quiz_questions_teacher(), QuizQuestionRead, QuizQuestionTeacherRead

### Community 100 - "compute_submission_hash"
Cohesion: 0.15
Nodes (7): compute_bytes_sha256(), compute_code_sha256(), compute_file_sha256(), compute_submission_hash(), normalize_code_for_hashing(), DummySubmissionRecord, test_metadata_extraction_and_plagiarism_detection()

### Community 102 - "get_db"
Cohesion: 0.15
Nodes (4): create_course(), get_practical_for_student(), submit_module_quiz(), get_db()

### Community 104 - "ensure_course_owner_or_admin"
Cohesion: 0.24
Nodes (5): ensure_course_owner_or_admin(), _collect_practical_submission_file_paths(), delete_module(), delete_practical(), delete_quiz_question()

### Community 105 - "_canonicalize_formula"
Cohesion: 0.18
Nodes (5): _canonicalize_formula(), _is_wrapped_in_parens(), _normalize_bare_function_name(), _replace_localized_functions_in_segment(), test_excel_course_formula_rules_have_valid_supported_expressions()

### Community 106 - "_build_submission_download_names"
Cohesion: 0.22
Nodes (5): build_content_disposition(), _build_submission_download_names(), _sanitize_ascii_token(), _sanitize_utf8_token(), _strip_apostrophes()

### Community 113 - "UUID"
Cohesion: 0.28
Nodes (3): _ensure_group_code_unique(), _get_group_or_404(), update_admin_group()

## Knowledge Gaps
- **1 isolated node(s):** `edu-auto-grader-backend`
  These have ≤1 connection - possible missing edges. (Counts symbols only; 928 node(s) total have ≤1 connection when file, concept and rationale nodes are included.)
- **78 thin communities (<3 nodes) omitted from report** — run `graphify query` to explore isolated nodes.

## Suggested Questions
_Questions this graph is uniquely positioned to answer:_

- **Why does `GradingRule` connect `GradingRule` to `accdb_grader.py`, `GradingError`, `AccdbGrader`, `test_course_content.py`, `submission_service.py`, `HtmlGrader`, `courses.py`, `test_graders.py`, `xlsx_grader.py`, `courses.py`, `DocxGrader`, `XlsxGrader`?**
  _High betweenness centrality (0.050) - this node is a cross-community bridge._
- **Are the 18 inferred relationships involving `User` (e.g. with `ensure_course_owner_or_admin()` and `get_current_user()`) actually correct?**
  _`User` has 18 INFERRED edges - model-reasoned connections that need verification._
- **What connects `edu-auto-grader-backend` to the rest of the system?**
  _1 weakly-connected nodes found - possible missing edges._
- **Should `QuizService` be split into smaller, more focused modules?**
  _Cohesion score 0.10846560846560846 - nodes in this community are weakly interconnected._
- **Why does `GradingError` connect `GradingError` to `accdb_grader.py`, `AccdbGrader`, `submission_service.py`, `GradingRule`, `HtmlGrader`, `_canonicalize_formula`, `test_graders.py`, `parse_docx_students`, `xlsx_grader.py`, `DocxGrader`, `metadata.py`, `DomainError`, `XlsxGrader`, `.submit_practical`?**
  _High betweenness centrality (0.041) - this node is a cross-community bridge._
- **Are the 6 inferred relationships involving `GradingRule` (e.g. with `AccdbGrader` and `_parse_relationship_pair_target()`) actually correct?**
  _`GradingRule` has 6 INFERRED edges - model-reasoned connections that need verification._
- **Should `postgres` be split into smaller, more focused modules?**
  _Cohesion score 0.09523809523809523 - nodes in this community are weakly interconnected._