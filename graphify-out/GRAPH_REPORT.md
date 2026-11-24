# Graph Report - edu-auto-grader  (2026-11-25)

## Corpus Check
- 87 files · ~249,785 words
- Verdict: corpus is large enough that graph structure adds value.
- Unclassified: 7 file(s) not represented in the graph (top: (none) 4, .ini 1, .mako 1)

## Summary
- 1583 nodes · 4393 edges · 76 communities (45 shown, 31 thin omitted)
- Extraction: 92% EXTRACTED · 8% INFERRED · 0% AMBIGUOUS · INFERRED: 367 edges (avg confidence: 0.93)
- Token cost: 0 input · 0 output

## Graph Freshness
- Built from commit: `c24793d4`
- Run `git rev-parse HEAD` and compare to check if the graph is stale.
- Run `graphify update .` after code changes (no API cost).

## Community Hubs (Navigation)
- DomainError
- postgres
- compilerOptions
- AccdbGrader
- GradingRule
- InvalidFileFormatError
- UUID
- MarkdownRenderer.tsx
- vite-env.d.ts
- _get_user_by_email
- InvalidFileFormatError
- courses.py
- SubmissionService
- test_submissions_api.py
- ExportService
- edu-auto-grader-backend
- refresh_tokens
- package.json
- App.tsx
- admin.py
- AdminUsersPage.tsx
- course.ts
- _SeedQuizQuestionPayload
- AuthContext.tsx
- XlsxGrader
- 0002_restrict_course_year_to_4.py
- GroupJournalPage.tsx
- accdb_grader.py
- HtmlSandbox.tsx
- parse_docx_students
- Settings
- DomainError
- User
- DocxGrader
- GradebookPage.tsx
- ModuleViewPage.tsx
- grading.py
- User
- Submission
- GradingRule
- conftest.py
- AsyncSession
- export_service.py
- schemas/__init__.py
- SqliteAsyncSessionAdapter
- delete_admin_user
- delete_module
- get_db
- upsert_module_practical
- import_admin_students
- submit_practical_work
- test_lifespan_starts_and_cancels_retention_background_task
- _enum_values

## God Nodes (most connected - your core abstractions)
1. `GradingRule` - 64 edges
2. `DomainError` - 63 edges
3. `User` - 63 edges
4. `DocxGrader` - 45 edges
5. `InvalidFileFormatError` - 44 edges
6. `SqliteAsyncSessionAdapter` - 43 edges
7. `get_db()` - 43 edges
8. `SubmissionService` - 41 edges
9. `UserRole` - 39 edges
10. `GradingError` - 38 edges

## Surprising Connections (you probably didn't know these)
- `test_grader_factory_resolves_all_four_formats()` --uses--> `XlsxGrader`  [INFERRED]
  backend/tests/test_graders.py → backend/app/graders/xlsx_grader.py
- `require_role()` --uses--> `UserRole`  [INFERRED]
  backend/app/api/deps.py → backend/app/models/user.py
- `create_admin_user()` --uses--> `UserRole`  [INFERRED]
  backend/app/api/v1/admin.py → backend/app/models/user.py
- `list_admin_users()` --uses--> `UserRole`  [INFERRED]
  backend/app/api/v1/admin.py → backend/app/models/user.py
- `update_admin_user()` --uses--> `UserRole`  [INFERRED]
  backend/app/api/v1/admin.py → backend/app/models/user.py

## Import Cycles
- None detected.

## Communities (76 total, 31 thin omitted)

### Community 0 - "DomainError"
Cohesion: 0.18
Nodes (8): create_access_token(), create_refresh_token(), create_token_pair(), decode_token(), _encode_jwt_token(), _enum_values(), UserRole, TokenPayload

### Community 1 - "postgres"
Cohesion: 0.10
Nodes (20): POSTGRES_DB, POSTGRES_PASSWORD, POSTGRES_USER, interval, retries, test, timeout, container_name (+12 more)

### Community 2 - "compilerOptions"
Cohesion: 0.10
Nodes (20): compilerOptions, allowImportingTsExtensions, isolatedModules, jsx, lib, module, moduleDetection, moduleResolution (+12 more)

### Community 4 - "AccdbGrader"
Cohesion: 0.08
Nodes (7): AccdbColumnSchema, AccdbDatabaseSchema, AccdbGrader, AccdbTableSchema, _is_numeric_condition(), _is_system_table_name(), _strip_identifiers()

### Community 5 - "GradingRule"
Cohesion: 0.13
Nodes (13): GradingRule, build_sample_accdb(), build_sample_xlsx(), test_accdb_grader_accepts_hyperlink_type_as_memo(), test_accdb_grader_detects_missing_schema_elements_and_invalid_header(), test_accdb_grader_evaluates_tables_columns_and_types(), test_docx_grader_detects_formatting_violations_and_corrupt_files(), test_docx_grader_evaluates_valid_document() (+5 more)

### Community 6 - "InvalidFileFormatError"
Cohesion: 0.07
Nodes (7): GradingError, InvalidFileFormatError, BaseGrader, _format_number(), GraderFactory, PracticalFormat, GradingRuleType

### Community 7 - "UUID"
Cohesion: 0.15
Nodes (7): get_current_user(), _fetch_user_progress_maps(), get_course(), list_courses(), _load_course_or_404(), _serialize_course(), update_course()

### Community 8 - "MarkdownRenderer.tsx"
Cohesion: 0.12
Nodes (31): dedentBlockLines(), findClosingDoubleStar(), findClosingParen(), findClosingSingleStar(), findMatchingBracket(), getAlignmentClass(), getLineIndent(), hasUnsafeControlChars() (+23 more)

### Community 11 - "_get_user_by_email"
Cohesion: 0.12
Nodes (10): _build_college_import_docx(), _get_user_by_email(), test_admin_academic_groups_crud_and_detachment(), test_admin_bulk_import_docx_sorts_ukrainian_alphabet_and_assigns_variants(), test_admin_bulk_import_rbac_and_validation_errors(), test_admin_bulk_import_txt_formats_continuing_list_number_and_duplicates(), test_admin_endpoints_enforce_admin_rbac(), test_admin_users_crud_filters_and_safety_guards() (+2 more)

### Community 13 - "InvalidFileFormatError"
Cohesion: 0.09
Nodes (14): _coerce_metadata(), compute_bytes_sha256(), compute_code_sha256(), compute_file_sha256(), compute_submission_hash(), evaluate_plagiarism(), extract_core_xml_metadata(), extract_document_metadata() (+6 more)

### Community 14 - "courses.py"
Cohesion: 0.07
Nodes (20): QuizNotPassedError, CourseCreate, CourseRead, CourseUpdate, ModuleCreate, ModuleDetailRead, ModuleSummaryRead, ModuleUpdate (+12 more)

### Community 15 - "SubmissionService"
Cohesion: 0.08
Nodes (11): download_submission_file(), get_submission_detail(), list_my_submissions(), list_submissions(), update_submission_grade(), PlagiarismDetectedError, ManualGradeUpdateRequest, SubmissionRead (+3 more)

### Community 16 - "test_submissions_api.py"
Cohesion: 0.14
Nodes (15): CourseSlug, build_sample_docx(), make_auth_headers(), _get_course_module_and_practical(), _get_user_by_email(), _grant_quiz_pass(), test_antiplagiarism_flags_sha256_and_core_xml_matches_across_students(), test_download_submission_forbidden_for_other_teacher_and_students() (+7 more)

### Community 17 - "ExportService"
Cohesion: 0.10
Nodes (4): export_group_journal(), get_group_journal(), list_academic_groups(), ExportService

### Community 22 - "refresh_tokens"
Cohesion: 0.18
Nodes (5): login(), read_current_user(), refresh_tokens(), verify_password(), TokenResponse

### Community 23 - "package.json"
Cohesion: 0.07
Nodes (39): devDependencies, autoprefixer@^10.4.20, eslint@^9.15.0, @eslint/js@^9.15.0, eslint-plugin-react-hooks@^5.0.0, eslint-plugin-react-refresh@^0.4.14, globals@^15.12.0, postcss@^8.4.49 (+31 more)

### Community 24 - "App.tsx"
Cohesion: 0.08
Nodes (45): dependencies, axios@^1.7.7, lucide-react@^0.460.0, react@^18.3.1, react-dom@^18.3.1, react-router-dom@^6.28.0, @tanstack/react-query@^5.60.0, App() (+37 more)

### Community 25 - "admin.py"
Cohesion: 0.18
Nodes (10): create_admin_user(), _ensure_email_unique(), _get_group_or_404(), _get_user_with_group_or_404(), _normalize_email(), _normalize_non_empty(), update_admin_group(), update_admin_user() (+2 more)

### Community 26 - "AdminUsersPage.tsx"
Cohesion: 0.06
Nodes (46): AdminTab, AdminUsersPage(), buildCredentialsReportText(), CourseYearFilter, DeleteTarget, downloadCredentialsReportTxt(), FeedbackBanner, fetchAdminGroups() (+38 more)

### Community 27 - "course.ts"
Cohesion: 0.07
Nodes (50): PracticalModuleContext, CourseEditorPage(), deleteModuleById(), deletePracticalById(), DeleteTarget, DISCIPLINE_META, DisciplineMeta, EditorTab (+42 more)

### Community 28 - "_SeedQuizQuestionPayload"
Cohesion: 0.18
Nodes (4): _SeedCoursePayload, _SeedModulePayload, _SeedPracticalPayload, _SeedQuizQuestionPayload

### Community 29 - "AuthContext.tsx"
Cohesion: 0.23
Nodes (15): apiClient, clearAuthTokens(), getAccessToken(), getRefreshToken(), setAccessToken(), setRefreshToken(), AuthContext, AuthContextValue (+7 more)

### Community 30 - "XlsxGrader"
Cohesion: 0.07
Nodes (6): _canonicalize_formula(), _format_cell_value(), _is_wrapped_in_parens(), _try_parse_numeric(), XlsxGrader, test_excel_course_formula_rules_have_valid_supported_expressions()

### Community 32 - "GroupJournalPage.tsx"
Cohesion: 0.26
Nodes (14): PlagiarismBadge(), extractApiErrorMessage(), COURSE_SLUG_BADGES, extractBlobApiErrorMessage(), fetchAcademicGroups(), fetchCourses(), fetchGroupJournal(), fetchSubmissionDetail() (+6 more)

### Community 33 - "accdb_grader.py"
Cohesion: 0.14
Nodes (6): build_accdb_bytes(), _encode_data_page(), _encode_msys_catalog_record(), _encode_tdef_page(), _parse_ddl_column_type(), _resolve_canonical_type()

### Community 34 - "HtmlSandbox.tsx"
Cohesion: 0.22
Nodes (10): @monaco-editor/react@4.6.0, buildStarterHtmlTemplate(), EditorColorTheme, HtmlSandbox(), HtmlSandboxProps, QUICK_HTML_SNIPPETS, QuickSnippet, SandboxViewMode (+2 more)

### Community 35 - "parse_docx_students"
Cohesion: 0.05
Nodes (25): ImportedStudentItem, ImportSkippedItem, StudentImportResponse, calculate_variant_index(), build_generated_email(), _classify_header_cell(), _clean_whitespace(), _detect_docx_header_columns() (+17 more)

### Community 36 - "Settings"
Cohesion: 0.08
Nodes (7): do_run_migrations(), run_async_migrations(), run_migrations_offline(), run_migrations_online(), get_settings(), _resolve_backend_path(), Settings

### Community 38 - "User"
Cohesion: 0.15
Nodes (12): Base, Module, Practical, Submission, User, PracticalVariant, resolve_student_variant(), _build_submission_download_names() (+4 more)

### Community 40 - "GradebookPage.tsx"
Cohesion: 0.11
Nodes (25): COURSE_SLUG_LABELS, CriterionBreakdownItem(), CriterionFilterMode, extractFileNameFromPath(), FORMAT_META, formatDateTime(), GradingReportCard(), GradingReportCardProps (+17 more)

### Community 44 - "ModuleViewPage.tsx"
Cohesion: 0.12
Nodes (29): AccessFieldDescriptor, AccessTableDescriptor, BinaryPracticalFormat, fetchModuleDetail(), fetchStudentPractical(), FILE_UPLOAD_FORMAT_META, FileUploadFormatMeta, FORMAT_BADGE_LABELS (+21 more)

### Community 46 - "grading.py"
Cohesion: 0.17
Nodes (5): check_submission_plagiarism(), ExtractedMetadata, GradingReport, GradingRulesUpdateRequest, PlagiarismCheckResult

### Community 47 - "User"
Cohesion: 0.12
Nodes (13): Course, QuizQuestion, AcademicGroup, build_seed_bundle(), hash_password(), _load_course_from_json(), main(), run_seed() (+5 more)

### Community 48 - "Submission"
Cohesion: 0.08
Nodes (11): downgrade(), upgrade(), create_application(), lifespan(), cleanup_expired_submissions(), delete_submission_file_safely(), main(), resolve_submission_file_path() (+3 more)

### Community 49 - "GradingRule"
Cohesion: 0.06
Nodes (13): _attribute_value_matches(), _find_tag_attr_key(), _get_tag_attribute_str(), HtmlGrader, _is_doctype_target(), _normalize_selector(), _normalize_text(), _parse_text_match_expected() (+5 more)

### Community 50 - "conftest.py"
Cohesion: 0.08
Nodes (8): hash_password(), async_client(), _compile_jsonb_for_sqlite(), _create_sqlite_test_engine(), db_session(), _fast_seed_hash_password(), _replace_zip_member(), rewrite_openxml_core_metadata()

### Community 52 - "AsyncSession"
Cohesion: 0.16
Nodes (7): _build_module_detail_read(), create_module(), create_quiz_question(), get_module(), list_module_quiz_questions_teacher(), _load_module_or_404(), update_module()

### Community 58 - "export_service.py"
Cohesion: 0.07
Nodes (20): CriterionErrorStat, ExportFormat, GroupJournalRead, GroupJournalRow, GroupJournalStudentCell, _auto_adjust_worksheet_columns(), build_content_disposition(), build_group_journal() (+12 more)

### Community 60 - "schemas/__init__.py"
Cohesion: 0.16
Nodes (10): AcademicGroupBase, AcademicGroupCreate, AcademicGroupRead, AcademicGroupUpdate, ErrorResponse, LoginRequest, RefreshTokenRequest, UserBase (+2 more)

### Community 61 - "SqliteAsyncSessionAdapter"
Cohesion: 0.11
Nodes (10): QuizAttempt, _set_sqlite_pragma(), SqliteAsyncSessionAdapter, test_academic_group_course_year_restricted_to_1_through_4(), _get_user_by_email(), test_delete_module_and_practical_rbac_and_not_found(), test_delete_module_by_teacher_and_admin_cascades_cleans_files_and_renumbers(), test_delete_practical_preserves_module_lecture_quiz_and_cleans_files() (+2 more)

### Community 62 - "delete_admin_user"
Cohesion: 0.16
Nodes (6): create_admin_group(), delete_admin_group(), delete_admin_user(), _ensure_group_code_unique(), list_admin_groups(), list_admin_users()

### Community 63 - "delete_module"
Cohesion: 0.20
Nodes (6): _collect_practical_submission_file_paths(), delete_module(), delete_practical(), delete_quiz_question(), _ensure_course_owner_or_admin(), delete_submission_files_for_paths()

### Community 64 - "get_db"
Cohesion: 0.15
Nodes (4): create_course(), get_practical_for_student(), submit_module_quiz(), get_db()

### Community 65 - "upsert_module_practical"
Cohesion: 0.21
Nodes (4): get_practical_for_teacher(), _serialize_practical_teacher(), update_practical(), upsert_module_practical()

### Community 67 - "submit_practical_work"
Cohesion: 0.10
Nodes (7): require_role(), _parse_export_format(), _extract_submission_payload(), ExtractedSubmissionPayload, submit_practical_work(), update_practical_grading_rules(), HtmlSubmissionRequest

## Knowledge Gaps
- **1 isolated node(s):** `edu-auto-grader-backend`
  These have ≤1 connection - possible missing edges. (Counts symbols only; 696 node(s) total have ≤1 connection when file, concept and rationale nodes are included.)
- **31 thin communities (<3 nodes) omitted from report** — run `graphify query` to explore isolated nodes.

## Suggested Questions
_Questions this graph is uniquely positioned to answer:_

- **Why does `GradingRule` connect `GradingRule` to `accdb_grader.py`, `.evaluate`, `AccdbGrader`, `InvalidFileFormatError`, `DocxGrader`, `User`, `_SeedQuizQuestionPayload`, `courses.py`, `grading.py`, `User`, `GradingRule`, `SubmissionService`, `schemas/__init__.py`?**
  _High betweenness centrality (0.057) - this node is a cross-community bridge._
- **Are the 11 inferred relationships involving `GradingRule` (e.g. with `AccdbGrader` and `BaseGrader`) actually correct?**
  _`GradingRule` has 11 INFERRED edges - model-reasoned connections that need verification._
- **What connects `edu-auto-grader-backend` to the rest of the system?**
  _1 weakly-connected nodes found - possible missing edges._
- **Should `postgres` be split into smaller, more focused modules?**
  _Cohesion score 0.09523809523809523 - nodes in this community are weakly interconnected._
- **Why does `User` connect `User` to `submit_practical_work`, `parse_docx_students`, `UUID`, `_get_user_by_email`, `courses.py`, `SubmissionService`, `User`, `ExportService`, `test_submissions_api.py`, `AsyncSession`, `refresh_tokens`, `admin.py`, `export_service.py`, `SqliteAsyncSessionAdapter`, `delete_admin_user`, `delete_module`?**
  _High betweenness centrality (0.041) - this node is a cross-community bridge._
- **Are the 10 inferred relationships involving `DomainError` (e.g. with `delete_admin_user()` and `update_admin_user()`) actually correct?**
  _`DomainError` has 10 INFERRED edges - model-reasoned connections that need verification._
- **Should `compilerOptions` be split into smaller, more focused modules?**
  _Cohesion score 0.09523809523809523 - nodes in this community are weakly interconnected._