# Graph Report - edu-auto-grader  (2026-11-25)

## Corpus Check
- 98 files · ~290,606 words
- Verdict: corpus is large enough that graph structure adds value.
- Unclassified: 7 file(s) not represented in the graph (top: (none) 4, .ini 1, .mako 1)

## Summary
- 2232 nodes · 6174 edges · 160 communities (60 shown, 100 thin omitted)
- Extraction: 93% EXTRACTED · 7% INFERRED · 0% AMBIGUOUS · INFERRED: 418 edges (avg confidence: 0.91)
- Token cost: 0 input · 0 output

## Graph Freshness
- Built from commit: `ac805c7a`
- Run `git rev-parse HEAD` and compare to check if the graph is stale.
- Run `graphify update .` after code changes (no API cost).

## Community Hubs (Navigation)
- QuizService
- postgres
- compilerOptions
- conftest.py
- AccdbGrader
- serialize_submission
- student_import_service.py
- .execute
- MarkdownRenderer.tsx
- vite-env.d.ts
- _get_user_by_email
- ExtractedMetadata
- _FormulaEvalError
- make_auth_headers
- submit_practical_work
- edu-auto-grader-backend
- change_password
- package.json
- App.tsx
- admin.py
- AdminUsersPage.tsx
- course.ts
- GroupJournalPage.tsx
- AuthContext.tsx
- ._eval_ast_node
- 0002_restrict_course_year_to_4.py
- RuleBuilderPage.tsx
- accdb_grader.py
- HtmlSandbox.tsx
- GradingError
- schemas/__init__.py
- CriterionResult
- GradingReportCard.tsx
- db_session
- export_service.py
- submission_service.py
- ModuleViewPage.tsx
- _collect_docx_body_fragments
- SlidingWindowRateLimiter
- CourseSlug
- services/__init__.py
- @tanstack/react-query
- main.py
- parse_docx_students
- _resolve_backend_path
- _get_module_with_questions
- DocxGrader
- rate_limit.py
- _extract_html_fingerprint
- submission_service.py
- GradingRule
- list_my_submissions
- InvalidFileFormatError
- admin.py
- test_auth_security.py
- test_course_content.py
- 0003_add_user_auth_security_fields.py
- math
- ExportService
- 0005_practical_rules_review.py
- do_run_migrations
- 0001_initial_schema.py
- xlsx_grader.py
- _FormulaParser
- extract_document_metadata
- test_read_upload_file_limited_stops_reading_chunks_early
- _compile_jsonb_for_sqlite
- SubmissionService
- test_lifespan_starts_and_cancels_retention_background_task
- _SeedCoursePayload
- metadata.py
- get_db
- .import_students
- _set_xlsx_text_cell

## God Nodes (most connected - your core abstractions)
1. `GradingRule` - 95 edges
2. `SqliteAsyncSessionAdapter` - 78 edges
3. `User` - 68 edges
4. `DomainError` - 67 edges
5. `GradingError` - 52 edges
6. `DocxGrader` - 51 edges
7. `make_auth_headers()` - 50 edges
8. `get_db()` - 45 edges
9. `Module` - 43 edges
10. `XlsxGrader` - 43 edges

## Surprising Connections (you probably didn't know these)
- `get_practical_for_student()` --uses--> `QuizService`  [INFERRED]
  backend/app/api/v1/courses.py → backend/app/services/quiz_service.py
- `submit_module_quiz()` --uses--> `QuizService`  [INFERRED]
  backend/app/api/v1/courses.py → backend/app/services/quiz_service.py
- `QuizService` --uses--> `Module`  [INFERRED]
  backend/app/services/quiz_service.py → backend/app/models/course.py
- `QuizService` --uses--> `Practical`  [INFERRED]
  backend/app/services/quiz_service.py → backend/app/models/course.py
- `QuizService` --uses--> `QuizQuestion`  [INFERRED]
  backend/app/services/quiz_service.py → backend/app/models/course.py

## Import Cycles
- None detected.

## Communities (160 total, 100 thin omitted)

### Community 0 - "QuizService"
Cohesion: 0.12
Nodes (5): _build_module_detail_read(), _ensure_utc(), format_cooldown_remaining(), get_quiz_pass_threshold_percent(), QuizService

### Community 1 - "postgres"
Cohesion: 0.10
Nodes (20): POSTGRES_DB, POSTGRES_PASSWORD, POSTGRES_USER, interval, retries, test, timeout, container_name (+12 more)

### Community 2 - "compilerOptions"
Cohesion: 0.10
Nodes (20): compilerOptions, allowImportingTsExtensions, isolatedModules, jsx, lib, module, moduleDetection, moduleResolution (+12 more)

### Community 3 - "conftest.py"
Cohesion: 0.08
Nodes (17): run_migrations_offline(), downgrade(), upgrade(), require_role(), Base, Course, Module, QuizQuestion (+9 more)

### Community 4 - "AccdbGrader"
Cohesion: 0.05
Nodes (14): AccdbColumnSchema, AccdbDatabaseSchema, AccdbGrader, AccdbObjectsCatalog, AccdbRelationshipSchema, AccdbTableSchema, _dedupe_relationships(), _find_named_entry() (+6 more)

### Community 5 - "serialize_submission"
Cohesion: 0.22
Nodes (3): _is_submission_file_available(), _resolve_existing_submission_file(), serialize_submission()

### Community 6 - "student_import_service.py"
Cohesion: 0.11
Nodes (11): PlagiarismDetectedError, QuizNotPassedError, Practical, calculate_variant_index(), resolve_student_variant(), build_generated_email(), _encode_ukrainian_word(), normalize_full_name() (+3 more)

### Community 7 - ".execute"
Cohesion: 0.11
Nodes (13): SqliteAsyncSessionAdapter, test_academic_group_course_year_restricted_to_1_through_4(), test_seed_database_sync_courses_preserves_users_and_groups(), _get_user_by_email(), test_admin_duplicate_group_list_number_returns_409_and_allows_other_groups(), test_delete_module_renumbers_cleanly_under_unique_constraint_with_reverse_uuids(), test_quiz_questions_preserve_order_index_independently_of_uuids(), test_schema_indexes_constraints_and_alembic_0004_backfill() (+5 more)

### Community 8 - "MarkdownRenderer.tsx"
Cohesion: 0.12
Nodes (31): dedentBlockLines(), findClosingDoubleStar(), findClosingParen(), findClosingSingleStar(), findMatchingBracket(), getAlignmentClass(), getLineIndent(), hasUnsafeControlChars() (+23 more)

### Community 11 - "_get_user_by_email"
Cohesion: 0.11
Nodes (11): _build_college_import_docx(), _get_user_by_email(), test_admin_academic_groups_crud_and_detachment(), test_admin_bulk_import_docx_sorts_ukrainian_alphabet_and_assigns_variants(), test_admin_bulk_import_rbac_and_validation_errors(), test_admin_bulk_import_returns_413_on_oversized_file_and_422_on_zip_bomb(), test_admin_bulk_import_txt_formats_continuing_list_number_and_duplicates(), test_admin_endpoints_enforce_admin_rbac() (+3 more)

### Community 13 - "ExtractedMetadata"
Cohesion: 0.11
Nodes (9): check_submission_plagiarism(), _clean_optional_str(), _coerce_metadata(), evaluate_plagiarism(), _is_content_fingerprint_match_actionable(), _is_generic_creator(), SubmissionRecordProtocol, ExtractedMetadata (+1 more)

### Community 14 - "_FormulaEvalError"
Cohesion: 0.12
Nodes (10): _apply_binary_operator(), _coerce_formula_number(), _excel_round(), _format_concat_operand(), _FormulaEvalError, _normalize_cell_coord(), _require_single_number(), _safe_power() (+2 more)

### Community 16 - "make_auth_headers"
Cohesion: 0.10
Nodes (25): _check_files_exist_batch(), build_sample_docx(), make_auth_headers(), rewrite_openxml_core_metadata(), _get_course_module_and_practical(), _get_user_by_email(), _grant_quiz_pass(), test_antiplagiarism_api_html_structural_match_and_classroom_template_clean() (+17 more)

### Community 17 - "submit_practical_work"
Cohesion: 0.13
Nodes (5): _extract_submission_payload(), ExtractedSubmissionPayload, _resolve_practical_upload_limit(), submit_practical_work(), update_practical_grading_rules()

### Community 22 - "change_password"
Cohesion: 0.09
Nodes (9): change_password(), _extract_client_ip(), login(), refresh_tokens(), create_access_token(), create_refresh_token(), create_token_pair(), decode_token() (+1 more)

### Community 23 - "package.json"
Cohesion: 0.07
Nodes (41): @monaco-editor/react@4.6.0, devDependencies, autoprefixer@^10.4.20, eslint@^9.15.0, @eslint/js@^9.15.0, eslint-plugin-react-hooks@^5.0.0, eslint-plugin-react-refresh@^0.4.14, globals@^15.12.0 (+33 more)

### Community 24 - "App.tsx"
Cohesion: 0.15
Nodes (28): App(), ProtectedAppLayout(), RoleHomeRedirect(), ChangePasswordModal(), ChangePasswordModalProps, Navbar(), NavbarProps, resolvePageTitle() (+20 more)

### Community 25 - "admin.py"
Cohesion: 0.08
Nodes (17): create_admin_group(), create_admin_user(), delete_admin_group(), delete_admin_user(), _ensure_email_unique(), _ensure_group_code_unique(), _ensure_group_list_number_unique(), _get_group_or_404() (+9 more)

### Community 26 - "AdminUsersPage.tsx"
Cohesion: 0.07
Nodes (44): RoleGuardProps, AdminTab, AdminUsersPage(), buildCredentialsReportText(), CourseYearFilter, DeleteTarget, downloadCredentialsReportTxt(), FeedbackBanner (+36 more)

### Community 27 - "course.ts"
Cohesion: 0.08
Nodes (42): apiClient, COURSE_VISUAL_META, CourseVisualMeta, fetchCourses(), FilterOption, ModuleRowCard(), PRACTICAL_FORMAT_LABELS, CourseEditorPage() (+34 more)

### Community 28 - "GroupJournalPage.tsx"
Cohesion: 0.16
Nodes (18): PlagiarismBadge(), PlagiarismBadgeProps, COURSE_SLUG_BADGES, extractBlobApiErrorMessage(), fetchAcademicGroups(), fetchCourses(), fetchGroupJournal(), fetchSubmissionDetail() (+10 more)

### Community 29 - "AuthContext.tsx"
Cohesion: 0.14
Nodes (25): API_BASE_URL, AuthFailureListener, authFailureListeners, clearAuthTokens(), getAccessToken(), getRefreshToken(), notifyAuthFailure(), refreshAccessToken() (+17 more)

### Community 32 - "RuleBuilderPage.tsx"
Cohesion: 0.20
Nodes (13): fetchCourses(), fetchPracticalTeacher(), FORMAT_BADGE_CONFIG, renderFormatIcon(), RULE_TYPE_SPECS, RuleBuilderPage(), RuleTypeSpec, CriterionResult (+5 more)

### Community 33 - "accdb_grader.py"
Cohesion: 0.08
Nodes (14): build_accdb_bytes(), _dedupe_names_casefold(), _encode_data_page(), _encode_msys_catalog_record(), _encode_tdef_page(), _encode_text_record(), _is_hidden_or_system_object(), _lookup_mapping_column() (+6 more)

### Community 34 - "HtmlSandbox.tsx"
Cohesion: 0.18
Nodes (15): buildDraftStorageKey(), buildStarterHtmlTemplate(), DraftSaveState, EditorColorTheme, formatDraftSavedTime(), HtmlSandbox(), HtmlSandboxProps, PendingDraftState (+7 more)

### Community 35 - "GradingError"
Cohesion: 0.07
Nodes (7): GradingError, _parse_relationship_pair_target(), _check_selector(), _normalize_selector(), test_all_course_rules_pass_validate_rule_definition_and_access_modules_separated(), test_all_course_variants_resolve_rule_placeholders_without_leftovers(), test_grader_factory_resolves_all_four_formats()

### Community 38 - "schemas/__init__.py"
Cohesion: 0.07
Nodes (20): AcademicGroupBase, AcademicGroupCreate, AcademicGroupRead, AcademicGroupUpdate, AdminResetPasswordRequest, AdminResetPasswordResponse, ChangePasswordRequest, ChangePasswordResponse (+12 more)

### Community 39 - "CriterionResult"
Cohesion: 0.05
Nodes (16): BaseGrader, _attribute_value_matches(), _find_tag_attr_key(), _get_tag_attribute_str(), has_meaningful_html_body(), HtmlGrader, _is_doctype_target(), _node_has_visible_content() (+8 more)

### Community 40 - "GradingReportCard.tsx"
Cohesion: 0.10
Nodes (28): COURSE_SLUG_LABELS, CriterionBreakdownItem(), CriterionFilterMode, extractFileNameFromPath(), FORMAT_META, formatDateTime(), GradingReportCard(), GradingReportCardProps (+20 more)

### Community 41 - "db_session"
Cohesion: 0.11
Nodes (6): async_client(), _create_sqlite_test_engine(), _set_sqlite_pragma(), db_session(), _fast_seed_hash_password(), _replace_zip_member()

### Community 42 - "export_service.py"
Cohesion: 0.05
Nodes (35): AcademicGroup, CriterionErrorStat, GroupJournalPracticalRead, GroupJournalRead, GroupJournalRow, GroupJournalStudentCell, build_content_disposition(), build_group_journal() (+27 more)

### Community 43 - "submission_service.py"
Cohesion: 0.09
Nodes (21): GraderFactory, PracticalFormat, CourseCreate, CourseUpdate, ModuleCreate, ModuleDetailRead, ModuleSummaryRead, ModuleUpdate (+13 more)

### Community 44 - "ModuleViewPage.tsx"
Cohesion: 0.10
Nodes (34): AccessFieldDescriptor, AccessTableDescriptor, BinaryPracticalFormat, extractRetryAfterSeconds(), fetchModuleDetail(), fetchStudentPractical(), FILE_UPLOAD_FORMAT_META, FileUploadFormatMeta (+26 more)

### Community 45 - "_collect_docx_body_fragments"
Cohesion: 0.31
Nodes (4): _collect_docx_body_fragments(), _collect_docx_xml_table_texts(), _extract_docx_paragraph_xml_text(), _find_xml_text()

### Community 47 - "CourseSlug"
Cohesion: 0.10
Nodes (13): _get_user_by_email(), test_change_password_validation_and_imported_student_flag(), test_login_rate_limiting_blocks_after_n_failures_and_resets_on_success(), test_long_cyrillic_password_create_login_and_change_without_500(), test_token_version_revokes_tokens_on_admin_reset_and_self_change(), _copy_course_content_dir(), _get_user_by_email(), test_delete_module_and_practical_rbac_and_not_found() (+5 more)

### Community 48 - "services/__init__.py"
Cohesion: 0.12
Nodes (13): cleanup_expired_submissions(), _delete_submission_file_paths_with_stats(), delete_submission_file_safely(), delete_submission_file_safely_async(), delete_submission_files_for_paths(), delete_submission_files_for_paths_async(), _inspect_submission_file_paths(), main() (+5 more)

### Community 49 - "@tanstack/react-query"
Cohesion: 0.17
Nodes (11): dependencies, axios@^1.7.7, lucide-react@^0.460.0, react@^18.3.1, react-dom@^18.3.1, react-router-dom@^6.28.0, @tanstack/react-query@^5.60.0, queryClient (+3 more)

### Community 51 - "parse_docx_students"
Cohesion: 0.10
Nodes (13): _classify_header_cell(), _clean_whitespace(), _detect_docx_header_columns(), _DocxColumnMap, _get_cell_value(), _infer_default_docx_columns(), _is_txt_header_line(), _normalize_header_token() (+5 more)

### Community 55 - "_get_module_with_questions"
Cohesion: 0.17
Nodes (8): _build_answers_for_score(), _get_module_with_questions(), _get_user_by_email(), test_excel_q42_imported_in_module_8_with_media_and_dry_run(), test_quiz_cooldown_zero_disables_wait_and_negative_config_rejected(), test_quiz_pass_threshold_setting_controls_passed_flag(), test_quiz_retry_cooldown_blocks_immediate_retry_and_unlocks_after_window(), test_quiz_submit_rejects_incomplete_duplicate_foreign_and_invalid_answers()

### Community 57 - "DocxGrader"
Cohesion: 0.05
Nodes (3): DocxGrader, _format_number(), test_docx_grader_inherits_font_from_base_style_chain_and_doc_defaults()

### Community 59 - "_extract_html_fingerprint"
Cohesion: 0.12
Nodes (10): compute_text_shingles(), _extract_css_property_blocks(), _extract_docx_fingerprint(), _extract_html_fingerprint(), _extract_html_visible_text(), _walk(), _normalize_css_declarations(), _serialize_html_dom_structure() (+2 more)

### Community 60 - "submission_service.py"
Cohesion: 0.10
Nodes (11): CourseSlug, _enum_values(), ExportFormat, HtmlSubmissionRequest, ManualGradeUpdateRequest, SubmissionRead, _build_submission_download_names(), _sanitize_ascii_token() (+3 more)

### Community 61 - "GradingRule"
Cohesion: 0.04
Nodes (27): _canonicalize_formula(), _format_cell_value(), XlsxGrader, GradingRule, GradingRuleType, build_sample_accdb(), build_sample_xlsx(), test_excel_course_formula_rules_have_valid_supported_expressions() (+19 more)

### Community 62 - "list_my_submissions"
Cohesion: 0.18
Nodes (5): download_submission_file(), get_submission_detail(), list_my_submissions(), list_submissions(), update_submission_grade()

### Community 66 - "InvalidFileFormatError"
Cohesion: 0.15
Nodes (10): InvalidFileFormatError, compute_bytes_sha256(), compute_code_sha256(), compute_file_sha256(), compute_submission_hash(), extract_core_xml_metadata(), normalize_code_for_hashing(), parse_core_xml_bytes() (+2 more)

### Community 68 - "admin.py"
Cohesion: 0.12
Nodes (7): read_current_user(), serialize_user(), hash_password_async(), _build_too_large_exception(), format_size_limit_mb(), read_upload_file_limited(), UserRead

### Community 69 - "test_auth_security.py"
Cohesion: 0.11
Nodes (11): get_settings(), Settings, hash_password(), _sha256_password_bytes(), verify_password(), verify_password_async(), test_hash_and_verify_password_async_offload_to_worker_thread(), _recording_hash() (+3 more)

### Community 70 - "test_course_content.py"
Cohesion: 0.11
Nodes (12): build_seed_bundle(), _extract_needs_rules_review(), _load_course_from_json(), main(), run_seed(), seed_database(), SeedBundle, SeedSummary (+4 more)

### Community 73 - "math"
Cohesion: 0.13
Nodes (11): _coerce_formula_bool(), _collect_logical_values(), _collect_numeric_values(), _eval_countif(), _eval_sumif(), _eval_vlookup(), _excel_compare(), _matches_exact_lookup() (+3 more)

### Community 76 - "ExportService"
Cohesion: 0.08
Nodes (5): export_group_journal(), get_group_journal(), list_academic_groups(), _parse_export_format(), ExportService

### Community 80 - "do_run_migrations"
Cohesion: 0.29
Nodes (3): do_run_migrations(), run_async_migrations(), run_migrations_online()

### Community 84 - "xlsx_grader.py"
Cohesion: 0.09
Nodes (13): _BoolNode, _CellRefNode, _count_non_empty_values(), _EmptyArgNode, _excel_wildcard_to_regex(), _FuncCallNode, _has_balanced_formula_delimiters(), _is_wrapped_in_parens() (+5 more)

### Community 90 - "_FormulaParser"
Cohesion: 0.36
Nodes (4): _BinaryOpNode, _FormulaParser, _Token, _UnaryOpNode

### Community 91 - "extract_document_metadata"
Cohesion: 0.10
Nodes (13): compute_shingle_jaccard(), extract_document_metadata(), DummySubmissionRecord, _strip_zip_member(), _fake_which(), test_antiplagiarism_accdb_fingerprint_corrupt_safety_and_backward_compat(), test_antiplagiarism_detects_html_copy_with_comment_and_renamed_css_classes(), test_antiplagiarism_detects_resaved_docx_without_core_xml_and_minor_edit() (+5 more)

### Community 92 - "test_read_upload_file_limited_stops_reading_chunks_early"
Cohesion: 0.50
Nodes (3): test_read_upload_file_limited_stops_reading_chunks_early(), __init__(), read()

### Community 95 - "SubmissionService"
Cohesion: 0.15
Nodes (4): GradingRulesUpdateRequest, _save_uploaded_file(), SubmissionService, _unlink_file_quietly()

### Community 99 - "_SeedCoursePayload"
Cohesion: 0.18
Nodes (3): _SeedCoursePayload, _SeedModulePayload, _SeedQuizQuestionPayload

### Community 100 - "metadata.py"
Cohesion: 0.14
Nodes (9): _canonicalize_xlsx_formula(), _extract_accdb_fingerprint(), _extract_accdb_table_via_mdb_export(), _extract_accdb_tables_via_mdbtools(), _extract_xlsx_fingerprint(), _extract_xlsx_formula_text(), _is_accdb_system_table(), _normalize_accdb_value() (+1 more)

### Community 104 - "get_db"
Cohesion: 0.07
Nodes (30): ensure_course_owner_or_admin(), get_current_user(), role_checker(), _collect_practical_submission_file_paths(), create_course(), create_module(), create_quiz_question(), delete_module() (+22 more)

### Community 114 - ".import_students"
Cohesion: 0.11
Nodes (4): import_admin_students(), build_credentials_report(), generate_temp_password(), StudentImportService

## Knowledge Gaps
- **1 isolated node(s):** `edu-auto-grader-backend`
  These have ≤1 connection - possible missing edges. (Counts symbols only; 1009 node(s) total have ≤1 connection when file, concept and rationale nodes are included.)
- **100 thin communities (<3 nodes) omitted from report** — run `graphify query` to explore isolated nodes.

## Suggested Questions
_Questions this graph is uniquely positioned to answer:_

- **Why does `GradingRule` connect `GradingRule` to `accdb_grader.py`, `GradingError`, `AccdbGrader`, `conftest.py`, `test_course_content.py`, `CriterionResult`, `get_db`, `submission_service.py`, `docx_grader.py`, `xlsx_grader.py`, `DocxGrader`, `submission_service.py`, `SubmissionService`?**
  _High betweenness centrality (0.053) - this node is a cross-community bridge._
- **Are the 20 inferred relationships involving `GradingRule` (e.g. with `_serialize_practical_teacher()` and `AccdbGrader`) actually correct?**
  _`GradingRule` has 20 INFERRED edges - model-reasoned connections that need verification._
- **What connects `edu-auto-grader-backend` to the rest of the system?**
  _1 weakly-connected nodes found - possible missing edges._
- **Should `QuizService` be split into smaller, more focused modules?**
  _Cohesion score 0.12307692307692308 - nodes in this community are weakly interconnected._
- **Why does `DocxGrader` connect `DocxGrader` to `InvalidFileFormatError`, `GradingError`, `CriterionResult`, `submission_service.py`, `docx_grader.py`, `GradingRule`?**
  _High betweenness centrality (0.045) - this node is a cross-community bridge._
- **Are the 9 inferred relationships involving `User` (e.g. with `ensure_course_owner_or_admin()` and `get_current_user()`) actually correct?**
  _`User` has 9 INFERRED edges - model-reasoned connections that need verification._
- **Should `postgres` be split into smaller, more focused modules?**
  _Cohesion score 0.09523809523809523 - nodes in this community are weakly interconnected._