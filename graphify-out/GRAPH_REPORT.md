# Graph Report - edu-auto-grader  (2026-11-20)

## Corpus Check
- 85 files · ~235,509 words
- Verdict: corpus is large enough that graph structure adds value.
- Unclassified: 7 file(s) not represented in the graph (top: (none) 4, .ini 1, .mako 1)

## Summary
- 1437 nodes · 3894 edges · 57 communities (39 shown, 18 thin omitted)
- Extraction: 92% EXTRACTED · 8% INFERRED · 0% AMBIGUOUS · INFERRED: 298 edges (avg confidence: 0.93)
- Token cost: 0 input · 0 output

## Graph Freshness
- Built from commit: `02907aa8`
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
- submission.py
- vite-env.d.ts
- build_group_journal
- InvalidFileFormatError
- submit_practical_work
- config.py
- ExportService
- schemas/__init__.py
- edu-auto-grader-backend
- InvalidFileFormatError
- package.json
- App.tsx
- DomainError
- AdminUsersPage.tsx
- course.ts
- _SeedQuizQuestionPayload
- AuthContext.tsx
- XlsxGrader
- DocxGrader
- AccdbGrader
- QuizService
- dependencies
- collections_abc
- Settings
- SubmissionService
- export_service.py
- _sanitize_filename_token
- GradebookPage.tsx
- delete_quiz_question
- test_admin_api.py
- _compile_jsonb_for_sqlite
- ModuleViewPage.tsx
- _serialize_practical_teacher
- build_seed_bundle
- _enum_values
- html_grader.py
- export_group_journal
- parse_docx_students
- get_db
- User
- 0002_restrict_course_year_to_4.py
- env.py
- admin.py

## God Nodes (most connected - your core abstractions)
1. `DomainError` - 57 edges
2. `User` - 53 edges
3. `GradingRule` - 44 edges
4. `InvalidFileFormatError` - 41 edges
5. `get_db()` - 40 edges
6. `DocxGrader` - 39 edges
7. `SubmissionService` - 39 edges
8. `GradingError` - 36 edges
9. `UserRole` - 35 edges
10. `XlsxGrader` - 35 edges

## Surprising Connections (you probably didn't know these)
- `test_grader_factory_resolves_all_four_formats()` --uses--> `AccdbGrader`  [INFERRED]
  backend/tests/test_graders.py → backend/app/graders/accdb_grader.py
- `test_grader_factory_resolves_all_four_formats()` --uses--> `DocxGrader`  [INFERRED]
  backend/tests/test_graders.py → backend/app/graders/docx_grader.py
- `test_grader_factory_resolves_all_four_formats()` --uses--> `HtmlGrader`  [INFERRED]
  backend/tests/test_graders.py → backend/app/graders/html_grader.py
- `create_admin_user()` --uses--> `UserRole`  [INFERRED]
  backend/app/api/v1/admin.py → backend/app/models/user.py
- `list_admin_users()` --uses--> `UserRole`  [INFERRED]
  backend/app/api/v1/admin.py → backend/app/models/user.py

## Import Cycles
- None detected.

## Communities (57 total, 18 thin omitted)

### Community 0 - "UserRole"
Cohesion: 0.10
Nodes (12): login(), read_current_user(), refresh_tokens(), create_access_token(), create_refresh_token(), create_token_pair(), decode_token(), _encode_jwt_token() (+4 more)

### Community 1 - "postgres"
Cohesion: 0.10
Nodes (20): POSTGRES_DB, POSTGRES_PASSWORD, POSTGRES_USER, interval, retries, test, timeout, container_name (+12 more)

### Community 2 - "compilerOptions"
Cohesion: 0.10
Nodes (20): compilerOptions, allowImportingTsExtensions, isolatedModules, jsx, lib, module, moduleDetection, moduleResolution (+12 more)

### Community 3 - "InvalidFileFormatError"
Cohesion: 0.09
Nodes (9): GradingError, InvalidFileFormatError, BaseGrader, GraderFactory, PracticalFormat, CriterionResult, GradingRule, GradingRuleType (+1 more)

### Community 4 - "._evaluate_column_exists"
Cohesion: 0.13
Nodes (5): AccdbColumnSchema, AccdbDatabaseSchema, AccdbTableSchema, _is_numeric_condition(), _strip_identifiers()

### Community 5 - "accdb_grader.py"
Cohesion: 0.14
Nodes (6): build_accdb_bytes(), _encode_data_page(), _encode_msys_catalog_record(), _encode_tdef_page(), _parse_ddl_column_type(), _resolve_canonical_type()

### Community 7 - "GradebookPage.tsx"
Cohesion: 0.10
Nodes (29): COURSE_SLUG_LABELS, CriterionBreakdownItem(), CriterionFilterMode, extractFileNameFromPath(), FORMAT_META, formatDateTime(), GradingReportCard(), GradingReportCardProps (+21 more)

### Community 8 - "submission.py"
Cohesion: 0.10
Nodes (12): get_submission_detail(), list_my_submissions(), list_submissions(), update_submission_grade(), CourseSlug, _enum_values(), CriterionErrorStat, GroupJournalRow (+4 more)

### Community 11 - "build_group_journal"
Cohesion: 0.10
Nodes (12): GroupJournalRead, _auto_adjust_worksheet_columns(), build_content_disposition(), build_group_journal(), calculate_criterion_error_stats(), ExportedDocument, GroupJournalBundle, PracticalColumnInfo (+4 more)

### Community 13 - "InvalidFileFormatError"
Cohesion: 0.08
Nodes (15): _coerce_metadata(), compute_bytes_sha256(), compute_code_sha256(), compute_file_sha256(), compute_submission_hash(), evaluate_plagiarism(), extract_core_xml_metadata(), extract_document_metadata() (+7 more)

### Community 14 - "submit_practical_work"
Cohesion: 0.15
Nodes (4): _extract_submission_payload(), ExtractedSubmissionPayload, submit_practical_work(), update_practical_grading_rules()

### Community 17 - "schemas/__init__.py"
Cohesion: 0.12
Nodes (18): CourseCreate, CourseUpdate, ModuleCreate, ModuleDetailRead, ModuleSummaryRead, ModuleUpdate, PracticalCreate, PracticalStudentRead (+10 more)

### Community 22 - "InvalidFileFormatError"
Cohesion: 0.08
Nodes (9): build_sample_docx(), build_sample_xlsx(), _replace_zip_member(), rewrite_openxml_core_metadata(), test_docx_grader_detects_formatting_violations_and_corrupt_files(), test_docx_grader_evaluates_valid_document(), test_docx_grader_supports_uniform_single_number_margin(), test_xlsx_grader_evaluates_formulas_values_and_charts() (+1 more)

### Community 23 - "package.json"
Cohesion: 0.07
Nodes (39): devDependencies, autoprefixer@^10.4.20, eslint@^9.15.0, @eslint/js@^9.15.0, eslint-plugin-react-hooks@^5.0.0, eslint-plugin-react-refresh@^0.4.14, globals@^15.12.0, postcss@^8.4.49 (+31 more)

### Community 24 - "App.tsx"
Cohesion: 0.12
Nodes (29): App(), ProtectedAppLayout(), RoleHomeRedirect(), Navbar(), NavbarProps, resolvePageTitle(), ROLE_BADGE_CONFIG, ROLE_LABELS (+21 more)

### Community 25 - "DomainError"
Cohesion: 0.06
Nodes (20): role_checker(), create_admin_group(), create_admin_user(), delete_admin_group(), delete_admin_user(), _ensure_email_unique(), _ensure_group_code_unique(), _get_group_or_404() (+12 more)

### Community 26 - "AdminUsersPage.tsx"
Cohesion: 0.07
Nodes (43): AdminTab, AdminUsersPage(), buildCredentialsReportText(), CourseYearFilter, DeleteTarget, downloadCredentialsReportTxt(), FeedbackBanner, fetchAdminGroups() (+35 more)

### Community 27 - "course.ts"
Cohesion: 0.08
Nodes (46): PracticalModuleContext, CourseEditorPage(), DISCIPLINE_META, DisciplineMeta, EditorTab, fetchCourses(), fetchModuleDetail(), fetchModuleQuizQuestions() (+38 more)

### Community 28 - "_SeedQuizQuestionPayload"
Cohesion: 0.18
Nodes (4): _SeedCoursePayload, _SeedModulePayload, _SeedPracticalPayload, _SeedQuizQuestionPayload

### Community 29 - "AuthContext.tsx"
Cohesion: 0.23
Nodes (15): apiClient, clearAuthTokens(), getAccessToken(), getRefreshToken(), setAccessToken(), setRefreshToken(), AuthContext, AuthContextValue (+7 more)

### Community 30 - "XlsxGrader"
Cohesion: 0.07
Nodes (5): _canonicalize_formula(), _format_cell_value(), _is_wrapped_in_parens(), _try_parse_numeric(), XlsxGrader

### Community 32 - "AccdbGrader"
Cohesion: 0.11
Nodes (6): AccdbGrader, _is_system_table_name(), build_sample_accdb(), test_accdb_grader_accepts_hyperlink_type_as_memo(), test_accdb_grader_detects_missing_schema_elements_and_invalid_header(), test_accdb_grader_evaluates_tables_columns_and_types()

### Community 33 - "QuizService"
Cohesion: 0.14
Nodes (4): _build_module_detail_read(), get_practical_for_student(), submit_module_quiz(), QuizService

### Community 34 - "dependencies"
Cohesion: 0.22
Nodes (9): dependencies, axios@^1.7.7, lucide-react@^0.460.0, @monaco-editor/react@4.6.0, react@^18.3.1, react-dom@^18.3.1, react-router-dom@^6.28.0, @monaco-editor/react (+1 more)

### Community 36 - "Settings"
Cohesion: 0.18
Nodes (3): get_settings(), _resolve_backend_path(), Settings

### Community 37 - "SubmissionService"
Cohesion: 0.10
Nodes (8): PlagiarismDetectedError, check_submission_plagiarism(), Submission, ExtractedMetadata, GradingReport, GradingRulesUpdateRequest, serialize_submission(), SubmissionService

### Community 38 - "export_service.py"
Cohesion: 0.10
Nodes (3): hash_password(), _configure_pdf_font(), _fast_seed_hash_password()

### Community 39 - "_sanitize_filename_token"
Cohesion: 0.33
Nodes (3): _prepare_pdf_text(), _sanitize_filename_token(), _transliterate_to_ascii()

### Community 40 - "GradebookPage.tsx"
Cohesion: 0.13
Nodes (21): @tanstack/react-query@^5.60.0, extractApiErrorMessage(), COURSE_VISUAL_META, CoursesPage(), CourseVisualMeta, fetchCourses(), FilterOption, ModuleRowCard() (+13 more)

### Community 42 - "test_admin_api.py"
Cohesion: 0.05
Nodes (27): calculate_variant_index(), resolve_student_variant(), async_client(), _create_sqlite_test_engine(), _set_sqlite_pragma(), db_session(), make_auth_headers(), SqliteAsyncSessionAdapter (+19 more)

### Community 44 - "ModuleViewPage.tsx"
Cohesion: 0.13
Nodes (22): buildStarterHtmlTemplate(), EditorColorTheme, HtmlSandbox(), HtmlSandboxProps, QUICK_HTML_SNIPPETS, QuickSnippet, SandboxViewMode, BinaryPracticalFormat (+14 more)

### Community 46 - "build_seed_bundle"
Cohesion: 0.15
Nodes (8): build_seed_bundle(), main(), run_seed(), seed_database(), SeedBundle, SeedSummary, summarize_bundle(), test_full_course_json_bundle_validation()

### Community 49 - "html_grader.py"
Cohesion: 0.07
Nodes (13): _attribute_value_matches(), _find_tag_attr_key(), _get_tag_attribute_str(), HtmlGrader, _is_doctype_target(), _normalize_selector(), _normalize_text(), _parse_text_match_expected() (+5 more)

### Community 50 - "export_group_journal"
Cohesion: 0.14
Nodes (5): export_group_journal(), get_group_journal(), list_academic_groups(), _parse_export_format(), ExportFormat

### Community 51 - "parse_docx_students"
Cohesion: 0.07
Nodes (19): build_generated_email(), _classify_header_cell(), _clean_whitespace(), _detect_docx_header_columns(), _DocxColumnMap, _encode_ukrainian_word(), _get_cell_value(), _infer_default_docx_columns() (+11 more)

### Community 52 - "get_db"
Cohesion: 0.12
Nodes (18): create_course(), create_module(), create_quiz_question(), _fetch_user_progress_maps(), get_course(), get_module(), get_practical_for_teacher(), list_courses() (+10 more)

### Community 53 - "User"
Cohesion: 0.19
Nodes (9): Base, Course, Module, Practical, QuizQuestion, QuizAttempt, AcademicGroup, User (+1 more)

### Community 63 - "env.py"
Cohesion: 0.14
Nodes (5): do_run_migrations(), run_async_migrations(), run_migrations_offline(), run_migrations_online(), test_media_courses_static_serving()

### Community 67 - "admin.py"
Cohesion: 0.09
Nodes (17): require_role(), serialize_user(), UserRole, AcademicGroupBase, AcademicGroupCreate, AcademicGroupRead, AcademicGroupUpdate, ErrorResponse (+9 more)

## Knowledge Gaps
- **1 isolated node(s):** `edu-auto-grader-backend`
  These have ≤1 connection - possible missing edges. (Counts symbols only; 629 node(s) total have ≤1 connection when file, concept and rationale nodes are included.)
- **18 thin communities (<3 nodes) omitted from report** — run `graphify query` to explore isolated nodes.

## Suggested Questions
_Questions this graph is uniquely positioned to answer:_

- **Why does `GradingRule` connect `InvalidFileFormatError` to `AccdbGrader`, `accdb_grader.py`, `SubmissionService`, `build_group_journal`, `_serialize_practical_teacher`, `schemas/__init__.py`, `html_grader.py`, `User`, `InvalidFileFormatError`, `XlsxGrader`, `DocxGrader`?**
  _High betweenness centrality (0.062) - this node is a cross-community bridge._
- **Are the 13 inferred relationships involving `DomainError` (e.g. with `delete_admin_user()` and `update_admin_user()`) actually correct?**
  _`DomainError` has 13 INFERRED edges - model-reasoned connections that need verification._
- **What connects `edu-auto-grader-backend` to the rest of the system?**
  _1 weakly-connected nodes found - possible missing edges._
- **Should `UserRole` be split into smaller, more focused modules?**
  _Cohesion score 0.10037878787878787 - nodes in this community are weakly interconnected._
- **Why does `GradingError` connect `InvalidFileFormatError` to `._evaluate_column_exists`, `accdb_grader.py`, `html_grader.py`, `DomainError`, `XlsxGrader`, `DocxGrader`?**
  _High betweenness centrality (0.060) - this node is a cross-community bridge._
- **Are the 20 inferred relationships involving `User` (e.g. with `get_current_user()` and `require_role()`) actually correct?**
  _`User` has 20 INFERRED edges - model-reasoned connections that need verification._
- **Should `postgres` be split into smaller, more focused modules?**
  _Cohesion score 0.09523809523809523 - nodes in this community are weakly interconnected._