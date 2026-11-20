# Graph Report - edu-auto-grader  (2026-11-20)

## Corpus Check
- 86 files · ~240,408 words
- Verdict: corpus is large enough that graph structure adds value.
- Unclassified: 7 file(s) not represented in the graph (top: (none) 4, .ini 1, .mako 1)

## Summary
- 1467 nodes · 4078 edges · 63 communities (40 shown, 23 thin omitted)
- Extraction: 90% EXTRACTED · 10% INFERRED · 0% AMBIGUOUS · INFERRED: 415 edges (avg confidence: 0.93)
- Token cost: 0 input · 0 output

## Graph Freshness
- Built from commit: `f84efa36`
- Run `git rev-parse HEAD` and compare to check if the graph is stale.
- Run `graphify update .` after code changes (no API cost).

## Community Hubs (Navigation)
- UserRole
- postgres
- compilerOptions
- GradingError
- AccdbGrader
- accdb_grader.py
- test_graders.py
- GradebookPage.tsx
- MarkdownRenderer.tsx
- vite-env.d.ts
- export_service.py
- InvalidFileFormatError
- list_my_submissions
- test_submissions_api.py
- SqliteAsyncSessionAdapter
- edu-auto-grader-backend
- admin.py
- package.json
- App.tsx
- DomainError
- AdminUsersPage.tsx
- course.ts
- _SeedQuizQuestionPayload
- AuthContext.tsx
- XlsxGrader
- 0002_restrict_course_year_to_4.py
- export_group_journal
- DomainError
- HtmlSandbox.tsx
- 0001_initial_schema.py
- config.py
- DomainError
- ._parse_attribute_rule_spec
- DocxGrader
- GradebookPage.tsx
- .evaluate
- test_admin_api.py
- _find_tag_attr_key
- ModuleViewPage.tsx
- asyncio
- build_seed_bundle
- conftest.py
- GradingRule
- ExportService
- parse_docx_students
- courses.py
- User
- _enum_values
- _attribute_value_matches
- _is_doctype_target
- _normalize_text
- _SeedPracticalPayload
- submit_practical_work

## God Nodes (most connected - your core abstractions)
1. `GradingRule` - 72 edges
2. `DomainError` - 59 edges
3. `User` - 57 edges
4. `InvalidFileFormatError` - 50 edges
5. `DocxGrader` - 46 edges
6. `PracticalFormat` - 40 edges
7. `GradingError` - 40 edges
8. `UserRole` - 40 edges
9. `get_db()` - 40 edges
10. `SubmissionService` - 39 edges

## Surprising Connections (you probably didn't know these)
- `update_admin_group()` --uses--> `AcademicGroupUpdate`  [INFERRED]
  backend/app/api/v1/admin.py → backend/app/schemas/auth.py
- `login()` --uses--> `LoginRequest`  [INFERRED]
  backend/app/api/v1/auth.py → backend/app/schemas/auth.py
- `refresh_tokens()` --uses--> `RefreshTokenRequest`  [INFERRED]
  backend/app/api/v1/auth.py → backend/app/schemas/auth.py
- `decode_token()` --uses--> `TokenPayload`  [INFERRED]
  backend/app/core/security.py → backend/app/schemas/auth.py
- `TokenPayload` --uses--> `UserRole`  [INFERRED]
  backend/app/schemas/auth.py → backend/app/models/user.py

## Import Cycles
- None detected.

## Communities (63 total, 23 thin omitted)

### Community 0 - "UserRole"
Cohesion: 0.11
Nodes (11): login(), refresh_tokens(), create_access_token(), create_refresh_token(), create_token_pair(), decode_token(), _encode_jwt_token(), hash_password() (+3 more)

### Community 1 - "postgres"
Cohesion: 0.10
Nodes (20): POSTGRES_DB, POSTGRES_PASSWORD, POSTGRES_USER, interval, retries, test, timeout, container_name (+12 more)

### Community 2 - "compilerOptions"
Cohesion: 0.10
Nodes (20): compilerOptions, allowImportingTsExtensions, isolatedModules, jsx, lib, module, moduleDetection, moduleResolution (+12 more)

### Community 3 - "GradingError"
Cohesion: 0.10
Nodes (6): GradingError, BaseGrader, GraderFactory, _format_cell_value(), PracticalFormat, GradingReport

### Community 4 - "AccdbGrader"
Cohesion: 0.10
Nodes (6): AccdbColumnSchema, AccdbGrader, _is_system_table_name(), test_accdb_grader_accepts_hyperlink_type_as_memo(), test_accdb_grader_detects_missing_schema_elements_and_invalid_header(), test_accdb_grader_evaluates_tables_columns_and_types()

### Community 5 - "accdb_grader.py"
Cohesion: 0.12
Nodes (7): build_accdb_bytes(), _encode_data_page(), _encode_msys_catalog_record(), _encode_tdef_page(), _is_numeric_condition(), _parse_ddl_column_type(), _resolve_canonical_type()

### Community 6 - "test_graders.py"
Cohesion: 0.11
Nodes (10): HtmlGrader, GradingRuleType, build_sample_xlsx(), test_docx_grader_supports_uniform_single_number_margin(), test_grader_factory_resolves_all_four_formats(), test_html_grader_attribute_filter_selector_and_compound_colspan(), test_html_grader_detects_missing_tags_and_rejects_empty_code(), test_html_grader_evaluates_semantic_dom_structure_and_attributes() (+2 more)

### Community 7 - "GradebookPage.tsx"
Cohesion: 0.12
Nodes (24): COURSE_SLUG_LABELS, CriterionBreakdownItem(), CriterionFilterMode, extractFileNameFromPath(), FORMAT_META, formatDateTime(), GradingReportCard(), GradingReportCardProps (+16 more)

### Community 8 - "MarkdownRenderer.tsx"
Cohesion: 0.13
Nodes (30): dedentBlockLines(), findClosingDoubleStar(), findClosingParen(), findClosingSingleStar(), findMatchingBracket(), getAlignmentClass(), getLineIndent(), hasUnsafeControlChars() (+22 more)

### Community 11 - "export_service.py"
Cohesion: 0.06
Nodes (23): _parse_export_format(), AcademicGroupRead, CriterionErrorStat, ExportFormat, GroupJournalRead, GroupJournalRow, GroupJournalStudentCell, HtmlSubmissionRequest (+15 more)

### Community 13 - "InvalidFileFormatError"
Cohesion: 0.08
Nodes (18): InvalidFileFormatError, check_submission_plagiarism(), _coerce_metadata(), compute_bytes_sha256(), compute_code_sha256(), compute_file_sha256(), compute_submission_hash(), evaluate_plagiarism() (+10 more)

### Community 15 - "list_my_submissions"
Cohesion: 0.22
Nodes (4): get_submission_detail(), list_my_submissions(), list_submissions(), update_submission_grade()

### Community 16 - "test_submissions_api.py"
Cohesion: 0.17
Nodes (10): CourseSlug, build_sample_accdb(), make_auth_headers(), _get_course_module_and_practical(), _get_user_by_email(), test_antiplagiarism_flags_sha256_and_core_xml_matches_across_students(), test_health_check_and_jwt_login_flow(), test_submission_blocked_without_passed_quiz_and_unlocked_after_70_percent() (+2 more)

### Community 17 - "SqliteAsyncSessionAdapter"
Cohesion: 0.17
Nodes (4): SqliteAsyncSessionAdapter, test_academic_group_course_year_restricted_to_1_through_4(), test_seed_database_sync_courses_preserves_users_and_groups(), _grant_quiz_pass()

### Community 22 - "admin.py"
Cohesion: 0.08
Nodes (14): create_application(), AcademicGroupBase, AcademicGroupCreate, AcademicGroupUpdate, ErrorResponse, ImportedStudentItem, ImportSkippedItem, LoginRequest (+6 more)

### Community 23 - "package.json"
Cohesion: 0.07
Nodes (39): devDependencies, autoprefixer@^10.4.20, eslint@^9.15.0, @eslint/js@^9.15.0, eslint-plugin-react-hooks@^5.0.0, eslint-plugin-react-refresh@^0.4.14, globals@^15.12.0, postcss@^8.4.49 (+31 more)

### Community 24 - "App.tsx"
Cohesion: 0.13
Nodes (27): App(), ProtectedAppLayout(), RoleHomeRedirect(), Navbar(), NavbarProps, resolvePageTitle(), ROLE_BADGE_CONFIG, ROLE_LABELS (+19 more)

### Community 25 - "DomainError"
Cohesion: 0.07
Nodes (20): create_admin_group(), create_admin_user(), delete_admin_group(), delete_admin_user(), _ensure_email_unique(), _ensure_group_code_unique(), _get_group_or_404(), _get_user_with_group_or_404() (+12 more)

### Community 26 - "AdminUsersPage.tsx"
Cohesion: 0.06
Nodes (47): AdminTab, AdminUsersPage(), buildCredentialsReportText(), CourseYearFilter, DeleteTarget, downloadCredentialsReportTxt(), FeedbackBanner, fetchAdminGroups() (+39 more)

### Community 27 - "course.ts"
Cohesion: 0.08
Nodes (44): PracticalModuleContext, CourseEditorPage(), DISCIPLINE_META, DisciplineMeta, EditorTab, fetchCourses(), fetchModuleDetail(), fetchModuleQuizQuestions() (+36 more)

### Community 28 - "_SeedQuizQuestionPayload"
Cohesion: 0.22
Nodes (3): _SeedCoursePayload, _SeedModulePayload, _SeedQuizQuestionPayload

### Community 29 - "AuthContext.tsx"
Cohesion: 0.23
Nodes (15): apiClient, clearAuthTokens(), getAccessToken(), getRefreshToken(), setAccessToken(), setRefreshToken(), AuthContext, AuthContextValue (+7 more)

### Community 30 - "XlsxGrader"
Cohesion: 0.09
Nodes (4): _canonicalize_formula(), _is_wrapped_in_parens(), _try_parse_numeric(), XlsxGrader

### Community 32 - "export_group_journal"
Cohesion: 0.23
Nodes (3): export_group_journal(), get_group_journal(), list_academic_groups()

### Community 33 - "DomainError"
Cohesion: 0.15
Nodes (5): require_role(), role_checker(), ExtractedSubmissionPayload, DomainError, QuizNotPassedError

### Community 34 - "HtmlSandbox.tsx"
Cohesion: 0.12
Nodes (17): dependencies, axios@^1.7.7, lucide-react@^0.460.0, @monaco-editor/react@4.6.0, react@^18.3.1, react-dom@^18.3.1, react-router-dom@^6.28.0, buildStarterHtmlTemplate() (+9 more)

### Community 36 - "config.py"
Cohesion: 0.08
Nodes (7): do_run_migrations(), run_async_migrations(), run_migrations_offline(), run_migrations_online(), get_settings(), _resolve_backend_path(), Settings

### Community 37 - "DomainError"
Cohesion: 0.09
Nodes (6): PlagiarismDetectedError, GradingRulesUpdateRequest, SubmissionRead, serialize_practical_teacher(), serialize_submission(), SubmissionService

### Community 38 - "._parse_attribute_rule_spec"
Cohesion: 0.25
Nodes (3): _normalize_selector(), _parse_text_match_expected(), _strip_quotes()

### Community 40 - "GradebookPage.tsx"
Cohesion: 0.13
Nodes (21): @tanstack/react-query@^5.60.0, extractApiErrorMessage(), COURSE_VISUAL_META, CoursesPage(), CourseVisualMeta, fetchCourses(), FilterOption, ModuleRowCard() (+13 more)

### Community 42 - "test_admin_api.py"
Cohesion: 0.13
Nodes (9): _build_college_import_docx(), _get_user_by_email(), test_admin_academic_groups_crud_and_detachment(), test_admin_bulk_import_docx_sorts_ukrainian_alphabet_and_assigns_variants(), test_admin_bulk_import_rbac_and_validation_errors(), test_admin_bulk_import_txt_formats_continuing_list_number_and_duplicates(), test_admin_endpoints_enforce_admin_rbac(), test_admin_users_crud_filters_and_safety_guards() (+1 more)

### Community 43 - "_find_tag_attr_key"
Cohesion: 0.38
Nodes (3): _find_tag_attr_key(), _get_tag_attribute_str(), _tag_has_attribute()

### Community 44 - "ModuleViewPage.tsx"
Cohesion: 0.11
Nodes (32): renderInlineMarkdown(), AccessFieldDescriptor, AccessTableDescriptor, BinaryPracticalFormat, fetchModuleDetail(), fetchStudentPractical(), FILE_UPLOAD_FORMAT_META, FileUploadFormatMeta (+24 more)

### Community 46 - "build_seed_bundle"
Cohesion: 0.13
Nodes (13): Course, QuizQuestion, AcademicGroup, build_seed_bundle(), hash_password(), _load_course_from_json(), main(), run_seed() (+5 more)

### Community 47 - "conftest.py"
Cohesion: 0.06
Nodes (10): async_client(), build_sample_docx(), _compile_jsonb_for_sqlite(), _create_sqlite_test_engine(), _set_sqlite_pragma(), db_session(), _fast_seed_hash_password(), _replace_zip_member() (+2 more)

### Community 49 - "GradingRule"
Cohesion: 0.09
Nodes (5): AccdbDatabaseSchema, AccdbTableSchema, _strip_identifiers(), CriterionResult, GradingRule

### Community 51 - "parse_docx_students"
Cohesion: 0.06
Nodes (21): calculate_variant_index(), build_generated_email(), _classify_header_cell(), _clean_whitespace(), _detect_docx_header_columns(), _DocxColumnMap, _encode_ukrainian_word(), generate_temp_password() (+13 more)

### Community 52 - "courses.py"
Cohesion: 0.06
Nodes (42): get_current_user(), _build_module_detail_read(), create_course(), create_module(), create_quiz_question(), delete_quiz_question(), _fetch_user_progress_maps(), get_course() (+34 more)

### Community 53 - "User"
Cohesion: 0.12
Nodes (8): Base, Module, Practical, QuizAttempt, Submission, User, QuizService, resolve_student_variant()

### Community 67 - "submit_practical_work"
Cohesion: 0.18
Nodes (3): _extract_submission_payload(), submit_practical_work(), update_practical_grading_rules()

## Knowledge Gaps
- **1 isolated node(s):** `edu-auto-grader-backend`
  These have ≤1 connection - possible missing edges. (Counts symbols only; 634 node(s) total have ≤1 connection when file, concept and rationale nodes are included.)
- **23 thin communities (<3 nodes) omitted from report** — run `graphify query` to explore isolated nodes.

## Suggested Questions
_Questions this graph is uniquely positioned to answer:_

- **Why does `GradingRule` connect `GradingRule` to `GradingError`, `AccdbGrader`, `DomainError`, `accdb_grader.py`, `DocxGrader`, `test_graders.py`, `.evaluate`, `._parse_attribute_rule_spec`, `.evaluate`, `build_seed_bundle`, `conftest.py`, `courses.py`, `User`, `_SeedPracticalPayload`, `XlsxGrader`?**
  _High betweenness centrality (0.066) - this node is a cross-community bridge._
- **Are the 14 inferred relationships involving `GradingRule` (e.g. with `_serialize_practical_teacher()` and `AccdbGrader`) actually correct?**
  _`GradingRule` has 14 INFERRED edges - model-reasoned connections that need verification._
- **What connects `edu-auto-grader-backend` to the rest of the system?**
  _1 weakly-connected nodes found - possible missing edges._
- **Should `UserRole` be split into smaller, more focused modules?**
  _Cohesion score 0.11182795698924732 - nodes in this community are weakly interconnected._
- **Why does `DocxGrader` connect `DocxGrader` to `GradingError`, `test_graders.py`, `.evaluate`, `InvalidFileFormatError`, `conftest.py`, `._is_list_paragraph`, `GradingRule`?**
  _High betweenness centrality (0.041) - this node is a cross-community bridge._
- **Are the 15 inferred relationships involving `DomainError` (e.g. with `delete_admin_user()` and `update_admin_user()`) actually correct?**
  _`DomainError` has 15 INFERRED edges - model-reasoned connections that need verification._
- **Should `postgres` be split into smaller, more focused modules?**
  _Cohesion score 0.09523809523809523 - nodes in this community are weakly interconnected._