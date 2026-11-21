# Graph Report - edu-auto-grader  (2026-11-21)

## Corpus Check
- 86 files · ~240,562 words
- Verdict: corpus is large enough that graph structure adds value.
- Unclassified: 7 file(s) not represented in the graph (top: (none) 4, .ini 1, .mako 1)

## Summary
- 1468 nodes · 4076 edges · 57 communities (38 shown, 19 thin omitted)
- Extraction: 90% EXTRACTED · 10% INFERRED · 0% AMBIGUOUS · INFERRED: 415 edges (avg confidence: 0.93)
- Token cost: 0 input · 0 output

## Graph Freshness
- Built from commit: `f875eefa`
- Run `git rev-parse HEAD` and compare to check if the graph is stale.
- Run `graphify update .` after code changes (no API cost).

## Community Hubs (Navigation)
- ExtractedMetadata
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
- SqliteAsyncSessionAdapter
- conftest.py
- edu-auto-grader-backend
- DomainError
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
- PlagiarismDetectedError
- HtmlSandbox.tsx
- 0001_initial_schema.py
- Settings
- SubmissionService
- SubmissionRead
- DocxGrader
- GradebookPage.tsx
- GradingReport
- test_admin_api.py
- GradingError
- ModuleViewPage.tsx
- User
- GradingRuleType
- do_run_migrations
- GradingRule
- dependencies
- parse_docx_students
- courses.py
- QuizService
- _enum_values
- _compile_jsonb_for_sqlite
- submit_practical_work

## God Nodes (most connected - your core abstractions)
1. `GradingRule` - 72 edges
2. `DomainError` - 59 edges
3. `User` - 57 edges
4. `InvalidFileFormatError` - 50 edges
5. `DocxGrader` - 46 edges
6. `UserRole` - 40 edges
7. `GradingError` - 40 edges
8. `PracticalFormat` - 40 edges
9. `get_db()` - 40 edges
10. `SubmissionService` - 39 edges

## Surprising Connections (you probably didn't know these)
- `create_admin_user()` --uses--> `UserRole`  [INFERRED]
  backend/app/api/v1/admin.py → backend/app/models/user.py
- `list_admin_users()` --uses--> `UserRole`  [INFERRED]
  backend/app/api/v1/admin.py → backend/app/models/user.py
- `update_admin_user()` --uses--> `UserRole`  [INFERRED]
  backend/app/api/v1/admin.py → backend/app/models/user.py
- `_build_module_detail_read()` --uses--> `UserRole`  [INFERRED]
  backend/app/api/v1/courses.py → backend/app/models/user.py
- `UserBase` --uses--> `UserRole`  [INFERRED]
  backend/app/schemas/auth.py → backend/app/models/user.py

## Import Cycles
- None detected.

## Communities (57 total, 19 thin omitted)

### Community 0 - "ExtractedMetadata"
Cohesion: 0.13
Nodes (8): check_submission_plagiarism(), _coerce_metadata(), evaluate_plagiarism(), SubmissionRecordProtocol, ExtractedMetadata, PlagiarismCheckResult, DummySubmissionRecord, test_metadata_extraction_and_plagiarism_detection()

### Community 1 - "postgres"
Cohesion: 0.10
Nodes (20): POSTGRES_DB, POSTGRES_PASSWORD, POSTGRES_USER, interval, retries, test, timeout, container_name (+12 more)

### Community 2 - "compilerOptions"
Cohesion: 0.10
Nodes (20): compilerOptions, allowImportingTsExtensions, isolatedModules, jsx, lib, module, moduleDetection, moduleResolution (+12 more)

### Community 3 - "GradingError"
Cohesion: 0.10
Nodes (6): GraderFactory, _is_wrapped_in_parens(), PracticalFormat, test_accdb_grader_evaluates_tables_columns_and_types(), test_docx_grader_evaluates_valid_document(), test_grader_factory_resolves_all_four_formats()

### Community 4 - "AccdbGrader"
Cohesion: 0.08
Nodes (7): AccdbColumnSchema, AccdbDatabaseSchema, AccdbGrader, AccdbTableSchema, _is_numeric_condition(), _is_system_table_name(), _strip_identifiers()

### Community 5 - "accdb_grader.py"
Cohesion: 0.14
Nodes (6): build_accdb_bytes(), _encode_data_page(), _encode_msys_catalog_record(), _encode_tdef_page(), _parse_ddl_column_type(), _resolve_canonical_type()

### Community 6 - "test_graders.py"
Cohesion: 0.16
Nodes (4): HtmlGrader, test_html_grader_attribute_filter_selector_and_compound_colspan(), test_html_grader_detects_missing_tags_and_rejects_empty_code(), test_html_grader_evaluates_semantic_dom_structure_and_attributes()

### Community 7 - "GradebookPage.tsx"
Cohesion: 0.11
Nodes (27): COURSE_SLUG_LABELS, CriterionBreakdownItem(), CriterionFilterMode, extractFileNameFromPath(), FORMAT_META, formatDateTime(), GradingReportCard(), GradingReportCardProps (+19 more)

### Community 8 - "MarkdownRenderer.tsx"
Cohesion: 0.13
Nodes (30): dedentBlockLines(), findClosingDoubleStar(), findClosingParen(), findClosingSingleStar(), findMatchingBracket(), getAlignmentClass(), getLineIndent(), hasUnsafeControlChars() (+22 more)

### Community 11 - "export_service.py"
Cohesion: 0.05
Nodes (23): _parse_export_format(), AcademicGroupRead, CriterionErrorStat, ExportFormat, GroupJournalRead, GroupJournalRow, GroupJournalStudentCell, HtmlSubmissionRequest (+15 more)

### Community 13 - "InvalidFileFormatError"
Cohesion: 0.16
Nodes (10): InvalidFileFormatError, compute_bytes_sha256(), compute_code_sha256(), compute_file_sha256(), compute_submission_hash(), extract_core_xml_metadata(), extract_document_metadata(), _find_xml_text() (+2 more)

### Community 15 - "list_my_submissions"
Cohesion: 0.22
Nodes (4): get_submission_detail(), list_my_submissions(), list_submissions(), update_submission_grade()

### Community 16 - "SqliteAsyncSessionAdapter"
Cohesion: 0.06
Nodes (17): async_client(), _create_sqlite_test_engine(), _set_sqlite_pragma(), db_session(), _fast_seed_hash_password(), SqliteAsyncSessionAdapter, test_academic_group_course_year_restricted_to_1_through_4(), test_media_courses_static_serving() (+9 more)

### Community 22 - "DomainError"
Cohesion: 0.06
Nodes (24): require_role(), role_checker(), login(), refresh_tokens(), ExtractedSubmissionPayload, DomainError, create_access_token(), create_refresh_token() (+16 more)

### Community 23 - "package.json"
Cohesion: 0.07
Nodes (41): @monaco-editor/react@4.6.0, devDependencies, autoprefixer@^10.4.20, eslint@^9.15.0, @eslint/js@^9.15.0, eslint-plugin-react-hooks@^5.0.0, eslint-plugin-react-refresh@^0.4.14, globals@^15.12.0 (+33 more)

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
Cohesion: 0.09
Nodes (42): CourseEditorPage(), DISCIPLINE_META, DisciplineMeta, EditorTab, fetchCourses(), fetchModuleDetail(), fetchModuleQuizQuestions(), fetchPracticalTeacher() (+34 more)

### Community 28 - "_SeedQuizQuestionPayload"
Cohesion: 0.22
Nodes (3): _SeedCoursePayload, _SeedModulePayload, _SeedQuizQuestionPayload

### Community 29 - "AuthContext.tsx"
Cohesion: 0.23
Nodes (15): apiClient, clearAuthTokens(), getAccessToken(), getRefreshToken(), setAccessToken(), setRefreshToken(), AuthContext, AuthContextValue (+7 more)

### Community 30 - "XlsxGrader"
Cohesion: 0.08
Nodes (4): _canonicalize_formula(), _format_cell_value(), _try_parse_numeric(), XlsxGrader

### Community 32 - "export_group_journal"
Cohesion: 0.23
Nodes (3): export_group_journal(), get_group_journal(), list_academic_groups()

### Community 34 - "HtmlSandbox.tsx"
Cohesion: 0.28
Nodes (8): buildStarterHtmlTemplate(), EditorColorTheme, HtmlSandbox(), HtmlSandboxProps, QUICK_HTML_SNIPPETS, QuickSnippet, SandboxViewMode, PracticalVariant

### Community 36 - "Settings"
Cohesion: 0.18
Nodes (3): get_settings(), _resolve_backend_path(), Settings

### Community 38 - "SubmissionRead"
Cohesion: 0.24
Nodes (3): ManualGradeUpdateRequest, SubmissionRead, serialize_submission()

### Community 40 - "GradebookPage.tsx"
Cohesion: 0.13
Nodes (20): @tanstack/react-query@^5.60.0, extractApiErrorMessage(), COURSE_VISUAL_META, CoursesPage(), CourseVisualMeta, fetchCourses(), FilterOption, ModuleRowCard() (+12 more)

### Community 42 - "test_admin_api.py"
Cohesion: 0.14
Nodes (13): AcademicGroup, calculate_variant_index(), resolve_student_variant(), make_auth_headers(), _build_college_import_docx(), _get_user_by_email(), test_admin_academic_groups_crud_and_detachment(), test_admin_bulk_import_docx_sorts_ukrainian_alphabet_and_assigns_variants() (+5 more)

### Community 43 - "GradingError"
Cohesion: 0.09
Nodes (10): GradingError, BaseGrader, _attribute_value_matches(), _find_tag_attr_key(), _get_tag_attribute_str(), _is_doctype_target(), _normalize_text(), _parse_text_match_expected() (+2 more)

### Community 44 - "ModuleViewPage.tsx"
Cohesion: 0.11
Nodes (32): renderInlineMarkdown(), AccessFieldDescriptor, AccessTableDescriptor, BinaryPracticalFormat, fetchModuleDetail(), fetchStudentPractical(), FILE_UPLOAD_FORMAT_META, FileUploadFormatMeta (+24 more)

### Community 46 - "User"
Cohesion: 0.10
Nodes (20): Base, Course, CourseSlug, Module, Practical, QuizQuestion, QuizAttempt, Submission (+12 more)

### Community 47 - "GradingRuleType"
Cohesion: 0.11
Nodes (12): GradingRuleType, build_sample_accdb(), build_sample_docx(), build_sample_xlsx(), _replace_zip_member(), rewrite_openxml_core_metadata(), test_accdb_grader_accepts_hyperlink_type_as_memo(), test_accdb_grader_detects_missing_schema_elements_and_invalid_header() (+4 more)

### Community 48 - "do_run_migrations"
Cohesion: 0.29
Nodes (3): do_run_migrations(), run_async_migrations(), run_migrations_online()

### Community 49 - "GradingRule"
Cohesion: 0.13
Nodes (4): _normalize_selector(), CriterionResult, GradingRule, _SeedPracticalPayload

### Community 50 - "dependencies"
Cohesion: 0.29
Nodes (7): dependencies, axios@^1.7.7, lucide-react@^0.460.0, react@^18.3.1, react-dom@^18.3.1, react-router-dom@^6.28.0, react-dom

### Community 51 - "parse_docx_students"
Cohesion: 0.05
Nodes (25): hash_password(), ImportedStudentItem, ImportSkippedItem, StudentImportResponse, build_generated_email(), _classify_header_cell(), _clean_whitespace(), _detect_docx_header_columns() (+17 more)

### Community 52 - "courses.py"
Cohesion: 0.06
Nodes (42): get_current_user(), _build_module_detail_read(), create_course(), create_module(), create_quiz_question(), delete_quiz_question(), _fetch_user_progress_maps(), get_course() (+34 more)

### Community 67 - "submit_practical_work"
Cohesion: 0.18
Nodes (3): _extract_submission_payload(), submit_practical_work(), update_practical_grading_rules()

## Knowledge Gaps
- **1 isolated node(s):** `edu-auto-grader-backend`
  These have ≤1 connection - possible missing edges. (Counts symbols only; 635 node(s) total have ≤1 connection when file, concept and rationale nodes are included.)
- **19 thin communities (<3 nodes) omitted from report** — run `graphify query` to explore isolated nodes.

## Suggested Questions
_Questions this graph is uniquely positioned to answer:_

- **Why does `GradingRule` connect `GradingRule` to `GradingError`, `AccdbGrader`, `accdb_grader.py`, `test_graders.py`, `DocxGrader`, `SubmissionService`, `GradingReport`, `GradingError`, `docx_grader.py`, `.evaluate`, `User`, `GradingRuleType`, `courses.py`, `XlsxGrader`?**
  _High betweenness centrality (0.073) - this node is a cross-community bridge._
- **Are the 14 inferred relationships involving `GradingRule` (e.g. with `_serialize_practical_teacher()` and `AccdbGrader`) actually correct?**
  _`GradingRule` has 14 INFERRED edges - model-reasoned connections that need verification._
- **What connects `edu-auto-grader-backend` to the rest of the system?**
  _1 weakly-connected nodes found - possible missing edges._
- **Should `ExtractedMetadata` be split into smaller, more focused modules?**
  _Cohesion score 0.12648221343873517 - nodes in this community are weakly interconnected._
- **Why does `DomainError` connect `DomainError` to `PlagiarismDetectedError`, `SubmissionService`, `SubmissionRead`, `export_service.py`, `GradingError`, `User`, `parse_docx_students`, `courses.py`, `QuizService`, `DomainError`?**
  _High betweenness centrality (0.048) - this node is a cross-community bridge._
- **Are the 15 inferred relationships involving `DomainError` (e.g. with `delete_admin_user()` and `update_admin_user()`) actually correct?**
  _`DomainError` has 15 INFERRED edges - model-reasoned connections that need verification._
- **Should `postgres` be split into smaller, more focused modules?**
  _Cohesion score 0.09523809523809523 - nodes in this community are weakly interconnected._