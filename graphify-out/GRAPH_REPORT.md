# Graph Report - edu-auto-grader  (2026-11-20)

## Corpus Check
- 86 files · ~240,497 words
- Verdict: corpus is large enough that graph structure adds value.
- Unclassified: 7 file(s) not represented in the graph (top: (none) 4, .ini 1, .mako 1)

## Summary
- 1484 nodes · 3994 edges · 68 communities (44 shown, 24 thin omitted)
- Extraction: 93% EXTRACTED · 7% INFERRED · 0% AMBIGUOUS · INFERRED: 298 edges (avg confidence: 0.93)
- Token cost: 0 input · 0 output

## Graph Freshness
- Built from commit: `34536c5c`
- Run `git rev-parse HEAD` and compare to check if the graph is stale.
- Run `graphify update .` after code changes (no API cost).

## Community Hubs (Navigation)
- UserRole
- postgres
- compilerOptions
- InvalidFileFormatError
- ._evaluate_column_exists
- accdb_grader.py
- get_current_user
- GradebookPage.tsx
- MarkdownRenderer.tsx
- vite-env.d.ts
- export_service.py
- InvalidFileFormatError
- BaseGrader
- config.py
- test_submissions_api.py
- schemas/__init__.py
- edu-auto-grader-backend
- conftest.py
- package.json
- App.tsx
- DomainError
- AdminUsersPage.tsx
- course.ts
- _SeedQuizQuestionPayload
- AuthContext.tsx
- XlsxGrader
- .evaluate
- QuizService
- HtmlSandbox.tsx
- collections_abc
- Settings
- SubmissionService
- student_import_service.py
- GradebookPage.tsx
- delete_quiz_question
- test_admin_api.py
- SqliteAsyncSessionAdapter
- ModuleViewPage.tsx
- DocxGrader
- build_seed_bundle
- db_session
- html_grader.py
- export_group_journal
- parse_docx_students
- get_db
- User
- xlsx_grader.py
- ._extract_single_table_schema
- seed.py
- AccdbGrader
- ._evaluate_page_margins
- .evaluate
- AccdbColumnSchema
- env.py
- DummySubmissionRecord
- test_docx_grader_supports_uniform_single_number_margin
- DomainError

## God Nodes (most connected - your core abstractions)
1. `DomainError` - 57 edges
2. `User` - 53 edges
3. `GradingRule` - 44 edges
4. `InvalidFileFormatError` - 41 edges
5. `get_db()` - 40 edges
6. `DocxGrader` - 39 edges
7. `SubmissionService` - 39 edges
8. `GradingError` - 36 edges
9. `XlsxGrader` - 35 edges
10. `UserRole` - 35 edges

## Surprising Connections (you probably didn't know these)
- `TokenPayload` --uses--> `UserRole`  [INFERRED]
  backend/app/schemas/auth.py → backend/app/models/user.py
- `get_group_journal()` --uses--> `GroupJournalRead`  [INFERRED]
  backend/app/api/v1/analytics.py → backend/app/schemas/submission.py
- `GroupJournalBundle` --uses--> `AcademicGroupRead`  [INFERRED]
  backend/app/services/export_service.py → backend/app/schemas/auth.py
- `PracticalColumnInfo` --uses--> `CourseSlug`  [INFERRED]
  backend/app/services/export_service.py → backend/app/models/course.py
- `export_group_journal()` --uses--> `ExportService`  [INFERRED]
  backend/app/api/v1/analytics.py → backend/app/services/export_service.py

## Import Cycles
- None detected.

## Communities (68 total, 24 thin omitted)

### Community 0 - "UserRole"
Cohesion: 0.06
Nodes (23): login(), read_current_user(), refresh_tokens(), create_access_token(), create_refresh_token(), create_token_pair(), decode_token(), _encode_jwt_token() (+15 more)

### Community 1 - "postgres"
Cohesion: 0.10
Nodes (20): POSTGRES_DB, POSTGRES_PASSWORD, POSTGRES_USER, interval, retries, test, timeout, container_name (+12 more)

### Community 2 - "compilerOptions"
Cohesion: 0.10
Nodes (20): compilerOptions, allowImportingTsExtensions, isolatedModules, jsx, lib, module, moduleDetection, moduleResolution (+12 more)

### Community 3 - "InvalidFileFormatError"
Cohesion: 0.11
Nodes (5): GradingError, GraderFactory, PracticalFormat, GradingRuleType, test_grader_factory_resolves_all_four_formats()

### Community 4 - "._evaluate_column_exists"
Cohesion: 0.18
Nodes (3): AccdbDatabaseSchema, _is_numeric_condition(), _strip_identifiers()

### Community 5 - "accdb_grader.py"
Cohesion: 0.16
Nodes (5): build_accdb_bytes(), _encode_data_page(), _encode_msys_catalog_record(), _encode_tdef_page(), _parse_ddl_column_type()

### Community 7 - "GradebookPage.tsx"
Cohesion: 0.11
Nodes (27): COURSE_SLUG_LABELS, CriterionBreakdownItem(), CriterionFilterMode, extractFileNameFromPath(), FORMAT_META, formatDateTime(), GradingReportCard(), GradingReportCardProps (+19 more)

### Community 8 - "MarkdownRenderer.tsx"
Cohesion: 0.12
Nodes (31): dedentBlockLines(), findClosingDoubleStar(), findClosingParen(), findClosingSingleStar(), findMatchingBracket(), getAlignmentClass(), getLineIndent(), hasUnsafeControlChars() (+23 more)

### Community 11 - "export_service.py"
Cohesion: 0.05
Nodes (20): CriterionErrorStat, ExportFormat, GroupJournalRead, GroupJournalRow, GroupJournalStudentCell, _auto_adjust_worksheet_columns(), build_content_disposition(), build_group_journal() (+12 more)

### Community 13 - "InvalidFileFormatError"
Cohesion: 0.08
Nodes (17): InvalidFileFormatError, check_submission_plagiarism(), _coerce_metadata(), compute_bytes_sha256(), compute_code_sha256(), compute_file_sha256(), compute_submission_hash(), evaluate_plagiarism() (+9 more)

### Community 14 - "BaseGrader"
Cohesion: 0.11
Nodes (4): BaseGrader, GradingReport, test_xlsx_grader_evaluates_formulas_values_and_charts(), test_xlsx_grader_rejects_static_value_instead_of_formula_and_missing_chart()

### Community 16 - "test_submissions_api.py"
Cohesion: 0.17
Nodes (8): make_auth_headers(), _get_course_module_and_practical(), _get_user_by_email(), test_antiplagiarism_flags_sha256_and_core_xml_matches_across_students(), test_health_check_and_jwt_login_flow(), test_submission_blocked_without_passed_quiz_and_unlocked_after_70_percent(), test_submit_all_four_practical_formats_via_api(), test_teacher_update_rules_manual_grade_and_group_export()

### Community 17 - "schemas/__init__.py"
Cohesion: 0.11
Nodes (19): _serialize_practical_teacher(), CourseCreate, CourseUpdate, ModuleCreate, ModuleDetailRead, ModuleSummaryRead, ModuleUpdate, PracticalCreate (+11 more)

### Community 22 - "conftest.py"
Cohesion: 0.11
Nodes (5): build_sample_docx(), build_sample_xlsx(), _compile_jsonb_for_sqlite(), _replace_zip_member(), rewrite_openxml_core_metadata()

### Community 23 - "package.json"
Cohesion: 0.07
Nodes (39): devDependencies, autoprefixer@^10.4.20, eslint@^9.15.0, @eslint/js@^9.15.0, eslint-plugin-react-hooks@^5.0.0, eslint-plugin-react-refresh@^0.4.14, globals@^15.12.0, postcss@^8.4.49 (+31 more)

### Community 24 - "App.tsx"
Cohesion: 0.12
Nodes (30): react-router-dom@^6.28.0, App(), ProtectedAppLayout(), RoleHomeRedirect(), Navbar(), NavbarProps, resolvePageTitle(), ROLE_BADGE_CONFIG (+22 more)

### Community 25 - "DomainError"
Cohesion: 0.09
Nodes (19): create_admin_group(), create_admin_user(), delete_admin_group(), delete_admin_user(), _ensure_email_unique(), _ensure_group_code_unique(), _get_group_or_404(), _get_user_with_group_or_404() (+11 more)

### Community 26 - "AdminUsersPage.tsx"
Cohesion: 0.07
Nodes (43): AdminTab, AdminUsersPage(), buildCredentialsReportText(), CourseYearFilter, DeleteTarget, downloadCredentialsReportTxt(), FeedbackBanner, fetchAdminGroups() (+35 more)

### Community 27 - "course.ts"
Cohesion: 0.08
Nodes (47): PracticalModuleContext, CourseEditorPage(), DISCIPLINE_META, DisciplineMeta, EditorTab, fetchCourses(), fetchModuleDetail(), fetchModuleQuizQuestions() (+39 more)

### Community 28 - "_SeedQuizQuestionPayload"
Cohesion: 0.18
Nodes (4): _SeedCoursePayload, _SeedModulePayload, _SeedPracticalPayload, _SeedQuizQuestionPayload

### Community 29 - "AuthContext.tsx"
Cohesion: 0.23
Nodes (15): apiClient, clearAuthTokens(), getAccessToken(), getRefreshToken(), setAccessToken(), setRefreshToken(), AuthContext, AuthContextValue (+7 more)

### Community 30 - "XlsxGrader"
Cohesion: 0.09
Nodes (4): _try_parse_numeric(), XlsxGrader, CriterionResult, GradingRule

### Community 32 - ".evaluate"
Cohesion: 0.23
Nodes (4): build_sample_accdb(), test_accdb_grader_accepts_hyperlink_type_as_memo(), test_accdb_grader_detects_missing_schema_elements_and_invalid_header(), test_accdb_grader_evaluates_tables_columns_and_types()

### Community 33 - "QuizService"
Cohesion: 0.13
Nodes (5): _build_module_detail_read(), get_practical_for_student(), submit_module_quiz(), PracticalStudentRead, QuizService

### Community 34 - "HtmlSandbox.tsx"
Cohesion: 0.13
Nodes (16): dependencies, axios@^1.7.7, lucide-react@^0.460.0, @monaco-editor/react@4.6.0, react@^18.3.1, react-dom@^18.3.1, buildStarterHtmlTemplate(), EditorColorTheme (+8 more)

### Community 35 - "collections_abc"
Cohesion: 0.17
Nodes (4): downgrade(), upgrade(), downgrade(), upgrade()

### Community 36 - "Settings"
Cohesion: 0.16
Nodes (3): get_settings(), _resolve_backend_path(), Settings

### Community 37 - "SubmissionService"
Cohesion: 0.06
Nodes (13): _extract_submission_payload(), submit_practical_work(), update_practical_grading_rules(), get_submission_detail(), list_my_submissions(), list_submissions(), update_submission_grade(), PlagiarismDetectedError (+5 more)

### Community 38 - "student_import_service.py"
Cohesion: 0.13
Nodes (3): build_generated_email(), generate_temp_password(), StudentImportService

### Community 40 - "GradebookPage.tsx"
Cohesion: 0.13
Nodes (21): @tanstack/react-query@^5.60.0, extractApiErrorMessage(), COURSE_VISUAL_META, CoursesPage(), CourseVisualMeta, fetchCourses(), FilterOption, ModuleRowCard() (+13 more)

### Community 42 - "test_admin_api.py"
Cohesion: 0.12
Nodes (11): calculate_variant_index(), resolve_student_variant(), _build_college_import_docx(), _get_user_by_email(), test_admin_academic_groups_crud_and_detachment(), test_admin_bulk_import_docx_sorts_ukrainian_alphabet_and_assigns_variants(), test_admin_bulk_import_rbac_and_validation_errors(), test_admin_bulk_import_txt_formats_continuing_list_number_and_duplicates() (+3 more)

### Community 43 - "SqliteAsyncSessionAdapter"
Cohesion: 0.17
Nodes (4): SqliteAsyncSessionAdapter, test_academic_group_course_year_restricted_to_1_through_4(), test_seed_database_sync_courses_preserves_users_and_groups(), _grant_quiz_pass()

### Community 44 - "ModuleViewPage.tsx"
Cohesion: 0.11
Nodes (29): AccessFieldDescriptor, AccessTableDescriptor, BinaryPracticalFormat, fetchModuleDetail(), fetchStudentPractical(), FILE_UPLOAD_FORMAT_META, FileUploadFormatMeta, FORMAT_BADGE_LABELS (+21 more)

### Community 46 - "build_seed_bundle"
Cohesion: 0.16
Nodes (7): QuizQuestion, build_seed_bundle(), _load_course_from_json(), seed_database(), SeedBundle, summarize_bundle(), test_full_course_json_bundle_validation()

### Community 47 - "db_session"
Cohesion: 0.13
Nodes (5): async_client(), _create_sqlite_test_engine(), _set_sqlite_pragma(), db_session(), _fast_seed_hash_password()

### Community 49 - "html_grader.py"
Cohesion: 0.06
Nodes (13): _attribute_value_matches(), _find_tag_attr_key(), _get_tag_attribute_str(), HtmlGrader, _is_doctype_target(), _normalize_selector(), _normalize_text(), _parse_text_match_expected() (+5 more)

### Community 50 - "export_group_journal"
Cohesion: 0.23
Nodes (3): export_group_journal(), get_group_journal(), list_academic_groups()

### Community 51 - "parse_docx_students"
Cohesion: 0.07
Nodes (18): _classify_header_cell(), _clean_whitespace(), _detect_docx_header_columns(), _DocxColumnMap, _encode_ukrainian_word(), _get_cell_value(), _infer_default_docx_columns(), _is_txt_header_line() (+10 more)

### Community 52 - "get_db"
Cohesion: 0.11
Nodes (20): create_course(), create_module(), create_quiz_question(), _fetch_user_progress_maps(), get_course(), get_module(), get_practical_for_teacher(), list_courses() (+12 more)

### Community 53 - "User"
Cohesion: 0.17
Nodes (8): Base, CourseSlug, _enum_values(), Practical, QuizAttempt, Submission, AcademicGroup, User

### Community 54 - "xlsx_grader.py"
Cohesion: 0.20
Nodes (3): _canonicalize_formula(), _format_cell_value(), _is_wrapped_in_parens()

### Community 56 - "seed.py"
Cohesion: 0.25
Nodes (4): hash_password(), main(), run_seed(), SeedSummary

### Community 63 - "env.py"
Cohesion: 0.14
Nodes (5): do_run_migrations(), run_async_migrations(), run_migrations_offline(), run_migrations_online(), test_media_courses_static_serving()

### Community 67 - "DomainError"
Cohesion: 0.12
Nodes (9): require_role(), role_checker(), _parse_export_format(), ExtractedSubmissionPayload, DomainError, QuizNotPassedError, _enum_values(), UserRole (+1 more)

## Knowledge Gaps
- **1 isolated node(s):** `edu-auto-grader-backend`
  These have ≤1 connection - possible missing edges. (Counts symbols only; 643 node(s) total have ≤1 connection when file, concept and rationale nodes are included.)
- **24 thin communities (<3 nodes) omitted from report** — run `graphify query` to explore isolated nodes.

## Suggested Questions
_Questions this graph is uniquely positioned to answer:_

- **Why does `GradingRule` connect `XlsxGrader` to `.evaluate`, `test_docx_grader_supports_uniform_single_number_margin`, `InvalidFileFormatError`, `accdb_grader.py`, `SubmissionService`, `InvalidFileFormatError`, `BaseGrader`, `build_seed_bundle`, `schemas/__init__.py`, `html_grader.py`, `User`, `xlsx_grader.py`, `seed.py`, `.evaluate`, `.build_criterion_result`?**
  _High betweenness centrality (0.047) - this node is a cross-community bridge._
- **Are the 13 inferred relationships involving `DomainError` (e.g. with `delete_admin_user()` and `update_admin_user()`) actually correct?**
  _`DomainError` has 13 INFERRED edges - model-reasoned connections that need verification._
- **What connects `edu-auto-grader-backend` to the rest of the system?**
  _1 weakly-connected nodes found - possible missing edges._
- **Should `UserRole` be split into smaller, more focused modules?**
  _Cohesion score 0.06352087114337568 - nodes in this community are weakly interconnected._
- **Why does `User` connect `User` to `UserRole`, `QuizService`, `DomainError`, `SubmissionService`, `get_current_user`, `student_import_service.py`, `test_admin_api.py`, `export_service.py`, `SqliteAsyncSessionAdapter`, `build_seed_bundle`, `test_submissions_api.py`, `schemas/__init__.py`, `get_db`, `seed.py`, `DomainError`?**
  _High betweenness centrality (0.038) - this node is a cross-community bridge._
- **Are the 20 inferred relationships involving `User` (e.g. with `get_current_user()` and `require_role()`) actually correct?**
  _`User` has 20 INFERRED edges - model-reasoned connections that need verification._
- **Should `postgres` be split into smaller, more focused modules?**
  _Cohesion score 0.09523809523809523 - nodes in this community are weakly interconnected._