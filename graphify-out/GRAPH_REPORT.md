# Graph Report - edu-auto-grader  (2026-11-25)

## Corpus Check
- 97 files · ~287,872 words
- Verdict: corpus is large enough that graph structure adds value.
- Unclassified: 7 file(s) not represented in the graph (top: (none) 4, .ini 1, .mako 1)

## Summary
- 2188 nodes · 6042 edges · 163 communities (61 shown, 102 thin omitted)
- Extraction: 93% EXTRACTED · 7% INFERRED · 0% AMBIGUOUS · INFERRED: 432 edges (avg confidence: 0.91)
- Token cost: 0 input · 0 output

## Graph Freshness
- Built from commit: `5a7c249a`
- Run `git rev-parse HEAD` and compare to check if the graph is stale.
- Run `graphify update .` after code changes (no API cost).

## Community Hubs (Navigation)
- QuizService
- postgres
- compilerOptions
- conftest.py
- AccdbGrader
- .prepare_submission_download
- _find_named_entry
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
- test_accdb_grader_inspects_queries_forms_reports_relationships_and_mdb_export_csv
- AuthContext.tsx
- ._eval_ast_node
- 0002_restrict_course_year_to_4.py
- create_token_pair
- accdb_grader.py
- HtmlSandbox.tsx
- GradingError
- serialize_submission
- schemas/__init__.py
- GradingRule
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
- html_grader.py
- parse_docx_students
- _resolve_backend_path
- _get_module_with_questions
- DocxGrader
- test_all_course_variants_resolve_rule_placeholders_without_leftovers
- _extract_html_visible_text
- _enum_values
- XlsxGrader
- list_my_submissions
- InvalidFileFormatError
- practicals.py
- test_auth_security.py
- test_course_content.py
- security.py
- math
- ExportService
- BaseGrader
- run_migrations_offline
- do_run_migrations
- sqlalchemy
- xlsx_grader.py
- test_all_alembic_revisions_fit_varchar_32_and_form_single_linear_chain
- _FormulaParser
- test_graders.py
- test_read_upload_file_limited_stops_reading_chunks_early
- _compile_jsonb_for_sqlite
- SubmissionService
- test_lifespan_starts_and_cancels_retention_background_task
- _SeedCoursePayload
- metadata.py
- get_db
- _tokenize_formula
- .import_students
- .update_grading_rules

## God Nodes (most connected - your core abstractions)
1. `GradingRule` - 95 edges
2. `SqliteAsyncSessionAdapter` - 78 edges
3. `DomainError` - 67 edges
4. `User` - 66 edges
5. `GradingError` - 52 edges
6. `DocxGrader` - 51 edges
7. `make_auth_headers()` - 50 edges
8. `get_db()` - 45 edges
9. `Module` - 44 edges
10. `XlsxGrader` - 43 edges

## Surprising Connections (you probably didn't know these)
- `AccdbGrader` --uses--> `GradingRuleType`  [INFERRED]
  backend/app/graders/accdb_grader.py → backend/app/schemas/grading.py
- `BaseGrader` --uses--> `GradingRuleType`  [INFERRED]
  backend/app/graders/base.py → backend/app/schemas/grading.py
- `DocxGrader` --uses--> `GradingRuleType`  [INFERRED]
  backend/app/graders/docx_grader.py → backend/app/schemas/grading.py
- `HtmlGrader` --uses--> `GradingRuleType`  [INFERRED]
  backend/app/graders/html_grader.py → backend/app/schemas/grading.py
- `test_all_course_rules_pass_validate_rule_definition_and_access_modules_separated()` --uses--> `GradingRuleType`  [INFERRED]
  backend/tests/test_course_content.py → backend/app/schemas/grading.py

## Import Cycles
- None detected.

## Communities (163 total, 102 thin omitted)

### Community 0 - "QuizService"
Cohesion: 0.09
Nodes (6): PlagiarismDetectedError, QuizNotPassedError, _ensure_utc(), format_cooldown_remaining(), get_quiz_pass_threshold_percent(), QuizService

### Community 1 - "postgres"
Cohesion: 0.10
Nodes (20): POSTGRES_DB, POSTGRES_PASSWORD, POSTGRES_USER, interval, retries, test, timeout, container_name (+12 more)

### Community 2 - "compilerOptions"
Cohesion: 0.10
Nodes (20): compilerOptions, allowImportingTsExtensions, isolatedModules, jsx, lib, module, moduleDetection, moduleResolution (+12 more)

### Community 3 - "conftest.py"
Cohesion: 0.11
Nodes (11): Base, CourseSlug, Module, Practical, QuizQuestion, QuizAttempt, Submission, AcademicGroup (+3 more)

### Community 4 - "AccdbGrader"
Cohesion: 0.05
Nodes (13): AccdbColumnSchema, AccdbDatabaseSchema, AccdbGrader, AccdbObjectsCatalog, AccdbTableSchema, _dedupe_relationships(), _is_numeric_condition(), _is_system_table_name() (+5 more)

### Community 7 - ".execute"
Cohesion: 0.11
Nodes (8): _get_user_by_email(), test_admin_duplicate_group_list_number_returns_409_and_allows_other_groups(), test_delete_module_renumbers_cleanly_under_unique_constraint_with_reverse_uuids(), test_quiz_questions_preserve_order_index_independently_of_uuids(), test_schema_indexes_constraints_and_alembic_0004_backfill(), _get_html_course_entities(), _get_user_by_email(), test_course_teacher_reassignment_forbidden_for_owner_and_allowed_for_admin()

### Community 8 - "MarkdownRenderer.tsx"
Cohesion: 0.13
Nodes (30): dedentBlockLines(), findClosingDoubleStar(), findClosingParen(), findClosingSingleStar(), findMatchingBracket(), getAlignmentClass(), getLineIndent(), hasUnsafeControlChars() (+22 more)

### Community 11 - "_get_user_by_email"
Cohesion: 0.09
Nodes (14): calculate_variant_index(), SqliteAsyncSessionAdapter, _build_college_import_docx(), _get_user_by_email(), test_academic_group_course_year_restricted_to_1_through_4(), test_admin_academic_groups_crud_and_detachment(), test_admin_bulk_import_docx_sorts_ukrainian_alphabet_and_assigns_variants(), test_admin_bulk_import_rbac_and_validation_errors() (+6 more)

### Community 13 - "ExtractedMetadata"
Cohesion: 0.12
Nodes (9): check_submission_plagiarism(), _clean_optional_str(), _coerce_metadata(), evaluate_plagiarism(), _is_content_fingerprint_match_actionable(), _is_generic_creator(), SubmissionRecordProtocol, ExtractedMetadata (+1 more)

### Community 14 - "_FormulaEvalError"
Cohesion: 0.15
Nodes (9): _coerce_formula_bool(), _coerce_formula_number(), _collect_logical_values(), _eval_countif(), _eval_vlookup(), _excel_round(), _FormulaEvalError, _require_single_number() (+1 more)

### Community 16 - "make_auth_headers"
Cohesion: 0.11
Nodes (22): build_sample_accdb(), make_auth_headers(), _get_course_module_and_practical(), _get_user_by_email(), _grant_quiz_pass(), test_antiplagiarism_api_html_structural_match_and_classroom_template_clean(), test_antiplagiarism_flags_sha256_and_core_xml_matches_across_students(), test_best_score_unified_across_student_progress_and_group_journal_export() (+14 more)

### Community 17 - "submit_practical_work"
Cohesion: 0.17
Nodes (3): _resolve_practical_upload_limit(), submit_practical_work(), update_practical_grading_rules()

### Community 22 - "change_password"
Cohesion: 0.08
Nodes (10): get_current_user(), role_checker(), change_password(), _extract_client_ip(), login(), read_current_user(), refresh_tokens(), serialize_user() (+2 more)

### Community 23 - "package.json"
Cohesion: 0.07
Nodes (41): @monaco-editor/react@4.6.0, devDependencies, autoprefixer@^10.4.20, eslint@^9.15.0, @eslint/js@^9.15.0, eslint-plugin-react-hooks@^5.0.0, eslint-plugin-react-refresh@^0.4.14, globals@^15.12.0 (+33 more)

### Community 24 - "App.tsx"
Cohesion: 0.11
Nodes (36): apiClient, App(), ProtectedAppLayout(), RoleHomeRedirect(), ChangePasswordModal(), ChangePasswordModalProps, Navbar(), NavbarProps (+28 more)

### Community 25 - "admin.py"
Cohesion: 0.08
Nodes (19): create_admin_group(), create_admin_user(), delete_admin_group(), delete_admin_user(), _ensure_email_unique(), _ensure_group_code_unique(), _ensure_group_list_number_unique(), _get_group_or_404() (+11 more)

### Community 26 - "AdminUsersPage.tsx"
Cohesion: 0.07
Nodes (42): AdminTab, AdminUsersPage(), buildCredentialsReportText(), CourseYearFilter, DeleteTarget, downloadCredentialsReportTxt(), FeedbackBanner, fetchAdminGroups() (+34 more)

### Community 27 - "course.ts"
Cohesion: 0.08
Nodes (46): CourseEditorPage(), deleteModuleById(), deletePracticalById(), DeleteTarget, DISCIPLINE_META, DisciplineMeta, EditorTab, fetchCourses() (+38 more)

### Community 28 - "test_accdb_grader_inspects_queries_forms_reports_relationships_and_mdb_export_csv"
Cohesion: 0.14
Nodes (6): _parse_msys_objects_csv(), _parse_msys_relationships_csv(), test_accdb_grader_inspects_queries_forms_reports_relationships_and_mdb_export_csv(), _fake_which(), test_antiplagiarism_accdb_fingerprint_corrupt_safety_and_backward_compat(), test_zip_bomb_protection_blocks_high_ratio_many_entries_and_oversized_uncompressed()

### Community 29 - "AuthContext.tsx"
Cohesion: 0.14
Nodes (25): API_BASE_URL, AuthFailureListener, authFailureListeners, clearAuthTokens(), getAccessToken(), getRefreshToken(), notifyAuthFailure(), refreshAccessToken() (+17 more)

### Community 32 - "create_token_pair"
Cohesion: 0.29
Nodes (4): create_access_token(), create_refresh_token(), create_token_pair(), _encode_jwt_token()

### Community 33 - "accdb_grader.py"
Cohesion: 0.08
Nodes (15): AccdbRelationshipSchema, build_accdb_bytes(), _dedupe_names_casefold(), _encode_data_page(), _encode_msys_catalog_record(), _encode_tdef_page(), _encode_text_record(), _is_hidden_or_system_object() (+7 more)

### Community 34 - "HtmlSandbox.tsx"
Cohesion: 0.18
Nodes (15): buildDraftStorageKey(), buildStarterHtmlTemplate(), DraftSaveState, EditorColorTheme, formatDraftSavedTime(), HtmlSandbox(), HtmlSandboxProps, PendingDraftState (+7 more)

### Community 35 - "GradingError"
Cohesion: 0.10
Nodes (4): GradingError, _parse_relationship_pair_target(), _check_selector(), _normalize_selector()

### Community 36 - "serialize_submission"
Cohesion: 0.14
Nodes (3): _check_files_exist_batch(), _is_submission_file_available(), serialize_submission()

### Community 38 - "schemas/__init__.py"
Cohesion: 0.07
Nodes (19): AcademicGroupBase, AcademicGroupCreate, AcademicGroupRead, AcademicGroupUpdate, AdminResetPasswordRequest, ChangePasswordRequest, ChangePasswordResponse, ErrorResponse (+11 more)

### Community 39 - "GradingRule"
Cohesion: 0.08
Nodes (9): _format_number(), HtmlGrader, CriterionResult, GradingRule, test_minimal_html_starter_template_scores_zero_across_all_html_course_modules(), test_html_grader_attribute_filter_selector_and_compound_colspan(), test_html_grader_detects_missing_tags_and_rejects_empty_code(), test_html_grader_empty_body_and_starter_template_score_zero() (+1 more)

### Community 40 - "GradingReportCard.tsx"
Cohesion: 0.06
Nodes (49): COURSE_SLUG_LABELS, CriterionBreakdownItem(), CriterionFilterMode, extractFileNameFromPath(), FORMAT_META, formatDateTime(), GradingReportCard(), GradingReportCardProps (+41 more)

### Community 41 - "db_session"
Cohesion: 0.11
Nodes (7): async_client(), build_sample_xlsx(), _create_sqlite_test_engine(), _set_sqlite_pragma(), db_session(), rewrite_openxml_core_metadata(), _make_template_docx()

### Community 42 - "export_service.py"
Cohesion: 0.07
Nodes (20): GradingRulesUpdateRequest, CriterionErrorStat, GroupJournalPracticalRead, GroupJournalRead, GroupJournalRow, GroupJournalStudentCell, HtmlSubmissionRequest, ManualGradeUpdateRequest (+12 more)

### Community 43 - "submission_service.py"
Cohesion: 0.11
Nodes (20): _build_module_detail_read(), PracticalFormat, CourseCreate, CourseUpdate, ModuleCreate, ModuleDetailRead, ModuleSummaryRead, ModuleUpdate (+12 more)

### Community 44 - "ModuleViewPage.tsx"
Cohesion: 0.10
Nodes (35): renderInlineMarkdown(), AccessFieldDescriptor, AccessTableDescriptor, BinaryPracticalFormat, extractRetryAfterSeconds(), fetchModuleDetail(), fetchStudentPractical(), FILE_UPLOAD_FORMAT_META (+27 more)

### Community 45 - "_collect_docx_body_fragments"
Cohesion: 0.31
Nodes (4): _collect_docx_body_fragments(), _collect_docx_xml_table_texts(), _extract_docx_paragraph_xml_text(), _find_xml_text()

### Community 46 - "SlidingWindowRateLimiter"
Cohesion: 0.10
Nodes (3): build_login_rate_limit_key(), SlidingWindowRateLimiter, test_sliding_window_rate_limiter_expires_old_attempts()

### Community 47 - "CourseSlug"
Cohesion: 0.14
Nodes (11): build_sample_docx(), _copy_course_content_dir(), _get_user_by_email(), test_delete_module_and_practical_rbac_and_not_found(), test_delete_module_by_teacher_and_admin_cascades_cleans_files_and_renumbers(), test_delete_practical_preserves_module_lecture_quiz_and_cleans_files(), test_media_courses_static_serving(), test_seed_sync_courses_protects_extra_modules_and_practicals_with_student_progress() (+3 more)

### Community 48 - "services/__init__.py"
Cohesion: 0.06
Nodes (21): create_application(), lifespan(), cleanup_expired_submissions(), _delete_submission_file_paths_with_stats(), delete_submission_file_safely(), delete_submission_file_safely_async(), delete_submission_files_for_paths(), delete_submission_files_for_paths_async() (+13 more)

### Community 49 - "@tanstack/react-query"
Cohesion: 0.17
Nodes (11): dependencies, axios@^1.7.7, lucide-react@^0.460.0, react@^18.3.1, react-dom@^18.3.1, react-router-dom@^6.28.0, @tanstack/react-query@^5.60.0, queryClient (+3 more)

### Community 50 - "html_grader.py"
Cohesion: 0.10
Nodes (11): _attribute_value_matches(), _find_tag_attr_key(), _get_tag_attribute_str(), has_meaningful_html_body(), _is_doctype_target(), _node_has_visible_content(), _normalize_text(), parse_html_document() (+3 more)

### Community 51 - "parse_docx_students"
Cohesion: 0.10
Nodes (13): _classify_header_cell(), _clean_whitespace(), _detect_docx_header_columns(), _DocxColumnMap, _get_cell_value(), _infer_default_docx_columns(), _is_txt_header_line(), _normalize_header_token() (+5 more)

### Community 55 - "_get_module_with_questions"
Cohesion: 0.17
Nodes (8): _build_answers_for_score(), _get_module_with_questions(), _get_user_by_email(), test_excel_q42_imported_in_module_8_with_media_and_dry_run(), test_quiz_cooldown_zero_disables_wait_and_negative_config_rejected(), test_quiz_pass_threshold_setting_controls_passed_flag(), test_quiz_retry_cooldown_blocks_immediate_retry_and_unlocks_after_window(), test_quiz_submit_rejects_incomplete_duplicate_foreign_and_invalid_answers()

### Community 61 - "XlsxGrader"
Cohesion: 0.06
Nodes (9): _canonicalize_formula(), _format_cell_value(), XlsxGrader, GradingRuleType, test_excel_course_formula_rules_have_valid_supported_expressions(), test_graders_validate_rule_definition_accepts_placeholders_and_rejects_invalid(), test_xlsx_grader_evaluates_formulas_values_and_charts(), test_xlsx_grader_evaluates_uncached_complex_cross_sheet_and_localized_formulas() (+1 more)

### Community 62 - "list_my_submissions"
Cohesion: 0.18
Nodes (5): download_submission_file(), get_submission_detail(), list_my_submissions(), list_submissions(), update_submission_grade()

### Community 66 - "InvalidFileFormatError"
Cohesion: 0.10
Nodes (9): InvalidFileFormatError, GraderFactory, compute_code_sha256(), compute_file_sha256(), compute_submission_hash(), normalize_code_for_hashing(), parse_core_xml_bytes(), test_grader_factory_resolves_all_four_formats() (+1 more)

### Community 68 - "practicals.py"
Cohesion: 0.19
Nodes (3): require_role(), _enum_values(), UserRole

### Community 69 - "test_auth_security.py"
Cohesion: 0.09
Nodes (14): get_settings(), Settings, verify_password(), verify_password_async(), _get_user_by_email(), test_change_password_validation_and_imported_student_flag(), test_hash_and_verify_password_async_offload_to_worker_thread(), _recording_hash() (+6 more)

### Community 70 - "test_course_content.py"
Cohesion: 0.09
Nodes (17): Course, build_seed_bundle(), _extract_needs_rules_review(), _load_course_from_json(), main(), _question_signature(), run_seed(), seed_database() (+9 more)

### Community 72 - "security.py"
Cohesion: 0.27
Nodes (3): hash_password(), _sha256_password_bytes(), _fast_seed_hash_password()

### Community 73 - "math"
Cohesion: 0.12
Nodes (10): _apply_binary_operator(), _collect_numeric_values(), _eval_sumif(), _excel_compare(), _excel_wildcard_to_regex(), _format_concat_operand(), _matches_exact_lookup(), _matches_excel_criteria() (+2 more)

### Community 76 - "ExportService"
Cohesion: 0.05
Nodes (14): export_group_journal(), get_group_journal(), list_academic_groups(), _parse_export_format(), ExportFormat, build_content_disposition(), ExportedDocument, ExportService (+6 more)

### Community 77 - "BaseGrader"
Cohesion: 0.10
Nodes (3): _parse_ddl_column_type(), BaseGrader, GradingReport

### Community 80 - "do_run_migrations"
Cohesion: 0.29
Nodes (3): do_run_migrations(), run_async_migrations(), run_migrations_online()

### Community 82 - "sqlalchemy"
Cohesion: 0.09
Nodes (8): downgrade(), upgrade(), downgrade(), upgrade(), downgrade(), upgrade(), downgrade(), upgrade()

### Community 84 - "xlsx_grader.py"
Cohesion: 0.10
Nodes (12): _BoolNode, _CellRefNode, _count_non_empty_values(), _EmptyArgNode, _FuncCallNode, _has_balanced_formula_delimiters(), _is_wrapped_in_parens(), _normalize_bare_function_name() (+4 more)

### Community 90 - "_FormulaParser"
Cohesion: 0.36
Nodes (4): _BinaryOpNode, _FormulaParser, _Token, _UnaryOpNode

### Community 91 - "test_graders.py"
Cohesion: 0.07
Nodes (17): compute_shingle_jaccard(), _replace_zip_member(), DummySubmissionRecord, _strip_zip_member(), test_antiplagiarism_detects_html_copy_with_comment_and_renamed_css_classes(), test_antiplagiarism_detects_resaved_docx_without_core_xml_and_minor_edit(), test_antiplagiarism_detects_resaved_xlsx_without_core_xml_and_respects_single_variant(), _build_calc_xlsx() (+9 more)

### Community 92 - "test_read_upload_file_limited_stops_reading_chunks_early"
Cohesion: 0.50
Nodes (3): test_read_upload_file_limited_stops_reading_chunks_early(), __init__(), read()

### Community 95 - "SubmissionService"
Cohesion: 0.18
Nodes (3): _save_uploaded_file(), SubmissionService, _unlink_file_quietly()

### Community 99 - "_SeedCoursePayload"
Cohesion: 0.18
Nodes (3): _SeedCoursePayload, _SeedModulePayload, _SeedQuizQuestionPayload

### Community 100 - "metadata.py"
Cohesion: 0.08
Nodes (21): _canonicalize_xlsx_formula(), compute_bytes_sha256(), compute_text_shingles(), _extract_accdb_fingerprint(), _extract_accdb_table_via_mdb_export(), _extract_accdb_tables_via_mdbtools(), extract_core_xml_metadata(), _extract_css_property_blocks() (+13 more)

### Community 104 - "get_db"
Cohesion: 0.09
Nodes (27): ensure_course_owner_or_admin(), _collect_practical_submission_file_paths(), create_course(), create_module(), create_quiz_question(), delete_module(), delete_practical(), delete_quiz_question() (+19 more)

### Community 114 - ".import_students"
Cohesion: 0.07
Nodes (8): import_admin_students(), _extract_submission_payload(), ExtractedSubmissionPayload, _build_too_large_exception(), format_size_limit_mb(), read_upload_file_limited(), generate_temp_password(), StudentImportService

## Knowledge Gaps
- **1 isolated node(s):** `edu-auto-grader-backend`
  These have ≤1 connection - possible missing edges. (Counts symbols only; 991 node(s) total have ≤1 connection when file, concept and rationale nodes are included.)
- **102 thin communities (<3 nodes) omitted from report** — run `graphify query` to explore isolated nodes.

## Suggested Questions
_Questions this graph is uniquely positioned to answer:_

- **Why does `GradingRule` connect `GradingRule` to `conftest.py`, `AccdbGrader`, `test_accdb_grader_inspects_queries_forms_reports_relationships_and_mdb_export_csv`, `accdb_grader.py`, `.update_grading_rules`, `GradingError`, `export_service.py`, `submission_service.py`, `html_grader.py`, `DocxGrader`, `test_all_course_variants_resolve_rule_placeholders_without_leftovers`, `XlsxGrader`, `InvalidFileFormatError`, `test_course_content.py`, `BaseGrader`, `xlsx_grader.py`, `test_graders.py`, `SubmissionService`, `get_db`?**
  _High betweenness centrality (0.062) - this node is a cross-community bridge._
- **Are the 20 inferred relationships involving `GradingRule` (e.g. with `_serialize_practical_teacher()` and `AccdbGrader`) actually correct?**
  _`GradingRule` has 20 INFERRED edges - model-reasoned connections that need verification._
- **What connects `edu-auto-grader-backend` to the rest of the system?**
  _1 weakly-connected nodes found - possible missing edges._
- **Should `QuizService` be split into smaller, more focused modules?**
  _Cohesion score 0.08522727272727272 - nodes in this community are weakly interconnected._
- **Why does `User` connect `conftest.py` to `QuizService`, `.prepare_submission_download`, `.execute`, `_get_user_by_email`, `make_auth_headers`, `change_password`, `admin.py`, `.update_grading_rules`, `serialize_submission`, `schemas/__init__.py`, `export_service.py`, `submission_service.py`, `CourseSlug`, `_get_module_with_questions`, `practicals.py`, `test_auth_security.py`, `test_course_content.py`, `ExportService`, `SubmissionService`, `get_db`, `.import_students`?**
  _High betweenness centrality (0.051) - this node is a cross-community bridge._
- **Are the 9 inferred relationships involving `User` (e.g. with `ensure_course_owner_or_admin()` and `get_current_user()`) actually correct?**
  _`User` has 9 INFERRED edges - model-reasoned connections that need verification._
- **Should `postgres` be split into smaller, more focused modules?**
  _Cohesion score 0.09523809523809523 - nodes in this community are weakly interconnected._