# Graph Report - edu-auto-grader  (2026-11-19)

## Corpus Check
- 67 files · ~48,291 words
- Verdict: corpus is large enough that graph structure adds value.
- Unclassified: 7 file(s) not represented in the graph (top: (none) 4, .ini 1, .mako 1)

## Summary
- 1179 nodes · 3170 edges · 57 communities (35 shown, 22 thin omitted)
- Extraction: 90% EXTRACTED · 10% INFERRED · 0% AMBIGUOUS · INFERRED: 327 edges (avg confidence: 0.94)
- Token cost: 0 input · 0 output

## Graph Freshness
- Built from commit: `f6c4e399`
- Run `git rev-parse HEAD` and compare to check if the graph is stale.
- Run `graphify update .` after code changes (no API cost).

## Community Hubs (Navigation)
- schemas/__init__.py
- postgres
- compilerOptions
- GradingRule
- main.tsx
- db_session
- submission_service.py
- AuthContext.tsx
- submission_service.py
- vite-env.d.ts
- export_service.py
- InvalidFileFormatError
- ExtractedMetadata
- User
- get_db
- edu-auto-grader-backend
- HtmlGrader
- package.json
- App.tsx
- api.ts
- SqliteAsyncSessionAdapter
- course.ts
- _find_tag_attr_key
- UserRole
- XlsxGrader
- DocxGrader
- AccdbGrader
- build_sample_docx
- submission.py
- .execute
- analytics.py
- DomainError
- submissions.py
- submit_practical_work
- CoursesPage.tsx
- DomainError
- test_submit_all_four_practical_formats_via_api
- ._evaluate_page_margins
- ModuleViewPage.tsx
- HtmlSandbox.tsx
- conftest.py
- ExportService
- _parse_text_match_expected
- get_current_user
- resolve_student_variant
- _enum_values
- Settings

## God Nodes (most connected - your core abstractions)
1. `GradingRule` - 64 edges
2. `User` - 46 edges
3. `DomainError` - 46 edges
4. `InvalidFileFormatError` - 45 edges
5. `DocxGrader` - 45 edges
6. `PracticalFormat` - 43 edges
7. `GradingError` - 40 edges
8. `SubmissionService` - 39 edges
9. `CriterionResult` - 36 edges
10. `XlsxGrader` - 36 edges

## Surprising Connections (you probably didn't know these)
- `list_academic_groups()` --uses--> `AcademicGroupRead`  [INFERRED]
  backend/app/api/v1/analytics.py → backend/app/schemas/auth.py
- `ExportService` --uses--> `AcademicGroupRead`  [INFERRED]
  backend/app/services/export_service.py → backend/app/schemas/auth.py
- `GroupJournalBundle` --uses--> `AcademicGroupRead`  [INFERRED]
  backend/app/services/export_service.py → backend/app/schemas/auth.py
- `login()` --uses--> `LoginRequest`  [INFERRED]
  backend/app/api/v1/auth.py → backend/app/schemas/auth.py
- `decode_token()` --uses--> `TokenPayload`  [INFERRED]
  backend/app/core/security.py → backend/app/schemas/auth.py

## Import Cycles
- None detected.

## Communities (57 total, 22 thin omitted)

### Community 0 - "schemas/__init__.py"
Cohesion: 0.10
Nodes (13): serialize_user(), _enum_values(), UserRole, AcademicGroupBase, AcademicGroupCreate, AcademicGroupRead, ErrorResponse, LoginRequest (+5 more)

### Community 1 - "postgres"
Cohesion: 0.10
Nodes (20): POSTGRES_DB, POSTGRES_PASSWORD, POSTGRES_USER, interval, retries, test, timeout, container_name (+12 more)

### Community 2 - "compilerOptions"
Cohesion: 0.10
Nodes (20): compilerOptions, allowImportingTsExtensions, isolatedModules, jsx, lib, module, moduleDetection, moduleResolution (+12 more)

### Community 3 - "GradingRule"
Cohesion: 0.16
Nodes (11): GradingRule, GradingRuleType, test_accdb_grader_detects_missing_schema_elements_and_invalid_header(), test_accdb_grader_evaluates_tables_columns_and_types(), test_docx_grader_detects_formatting_violations_and_corrupt_files(), test_docx_grader_evaluates_valid_document(), test_grader_factory_resolves_all_four_formats(), test_html_grader_detects_missing_tags_and_rejects_empty_code() (+3 more)

### Community 4 - "main.tsx"
Cohesion: 0.18
Nodes (11): dependencies, axios@^1.7.7, react@^18.3.1, react-dom@^18.3.1, @tanstack/react-query@^5.60.0, queryClient, rootElement, axios (+3 more)

### Community 5 - "db_session"
Cohesion: 0.20
Nodes (3): async_client(), db_session(), _fast_seed_hash_password()

### Community 6 - "submission_service.py"
Cohesion: 0.10
Nodes (18): CourseCreate, CourseUpdate, ModuleCreate, ModuleSummaryRead, ModuleUpdate, PracticalCreate, PracticalStudentRead, PracticalSummaryRead (+10 more)

### Community 7 - "AuthContext.tsx"
Cohesion: 0.16
Nodes (19): apiClient, clearAuthTokens(), getAccessToken(), getRefreshToken(), setAccessToken(), setRefreshToken(), AuthContext, AuthContextValue (+11 more)

### Community 8 - "submission_service.py"
Cohesion: 0.12
Nodes (4): GraderFactory, PracticalFormat, GradingReport, GradingRulesUpdateRequest

### Community 11 - "export_service.py"
Cohesion: 0.10
Nodes (11): _auto_adjust_worksheet_columns(), build_content_disposition(), _configure_pdf_font(), ExportedDocument, GroupJournalBundle, PracticalColumnInfo, _prepare_pdf_text(), render_group_journal_pdf() (+3 more)

### Community 13 - "InvalidFileFormatError"
Cohesion: 0.16
Nodes (10): InvalidFileFormatError, compute_bytes_sha256(), compute_code_sha256(), compute_file_sha256(), compute_submission_hash(), extract_core_xml_metadata(), extract_document_metadata(), _find_xml_text() (+2 more)

### Community 14 - "ExtractedMetadata"
Cohesion: 0.12
Nodes (8): check_submission_plagiarism(), _coerce_metadata(), evaluate_plagiarism(), SubmissionRecordProtocol, ExtractedMetadata, PlagiarismCheckResult, DummySubmissionRecord, test_metadata_extraction_and_plagiarism_detection()

### Community 15 - "User"
Cohesion: 0.05
Nodes (28): do_run_migrations(), run_async_migrations(), run_migrations_offline(), run_migrations_online(), downgrade(), upgrade(), Base, QuizNotPassedError (+20 more)

### Community 17 - "get_db"
Cohesion: 0.10
Nodes (24): _build_module_detail_read(), create_course(), create_module(), create_quiz_question(), delete_quiz_question(), _fetch_user_progress_maps(), get_course(), get_module() (+16 more)

### Community 22 - "HtmlGrader"
Cohesion: 0.08
Nodes (8): GradingError, BaseGrader, _attribute_value_matches(), HtmlGrader, _is_doctype_target(), _normalize_selector(), _normalize_text(), CriterionResult

### Community 23 - "package.json"
Cohesion: 0.07
Nodes (39): devDependencies, autoprefixer@^10.4.20, eslint@^9.15.0, @eslint/js@^9.15.0, eslint-plugin-react-hooks@^5.0.0, eslint-plugin-react-refresh@^0.4.14, globals@^15.12.0, postcss@^8.4.49 (+31 more)

### Community 24 - "App.tsx"
Cohesion: 0.12
Nodes (31): lucide-react@^0.460.0, react-router-dom@^6.28.0, App(), ProtectedAppLayout(), RoleHomeRedirect(), WorkspaceSectionPlaceholder(), WorkspaceSectionProps, Navbar() (+23 more)

### Community 25 - "api.ts"
Cohesion: 0.09
Nodes (26): AcademicGroupBase, AcademicGroupCreate, AcademicGroupRead, CriterionErrorStat, EXPORT_FORMATS, ExportFormat, GroupJournalRead, GroupJournalRow (+18 more)

### Community 27 - "course.ts"
Cohesion: 0.13
Nodes (21): COURSE_SLUGS, CourseCreate, CourseRead, CourseUpdate, ModuleCreate, ModuleDetailRead, ModuleSummaryRead, ModuleUpdate (+13 more)

### Community 28 - "_find_tag_attr_key"
Cohesion: 0.38
Nodes (3): _find_tag_attr_key(), _get_tag_attribute_str(), _tag_has_attribute()

### Community 29 - "UserRole"
Cohesion: 0.18
Nodes (7): create_access_token(), create_refresh_token(), create_token_pair(), _encode_jwt_token(), hash_password(), verify_password(), TokenResponse

### Community 30 - "XlsxGrader"
Cohesion: 0.08
Nodes (4): _canonicalize_formula(), _is_wrapped_in_parens(), _try_parse_numeric(), XlsxGrader

### Community 32 - "AccdbGrader"
Cohesion: 0.06
Nodes (13): AccdbColumnSchema, AccdbDatabaseSchema, AccdbGrader, AccdbTableSchema, build_accdb_bytes(), _encode_data_page(), _encode_msys_catalog_record(), _encode_tdef_page() (+5 more)

### Community 33 - "build_sample_docx"
Cohesion: 0.21
Nodes (5): build_sample_accdb(), build_sample_docx(), build_sample_xlsx(), _replace_zip_member(), rewrite_openxml_core_metadata()

### Community 34 - "submission.py"
Cohesion: 0.15
Nodes (8): CriterionErrorStat, GroupJournalRead, GroupJournalRow, GroupJournalStudentCell, HtmlSubmissionRequest, build_group_journal(), calculate_criterion_error_stats(), _RuleStatAccumulator

### Community 36 - "analytics.py"
Cohesion: 0.15
Nodes (5): export_group_journal(), get_group_journal(), list_academic_groups(), _parse_export_format(), ExportFormat

### Community 37 - "DomainError"
Cohesion: 0.14
Nodes (7): DomainError, PlagiarismDetectedError, Submission, ManualGradeUpdateRequest, SubmissionRead, serialize_submission(), SubmissionService

### Community 38 - "submissions.py"
Cohesion: 0.23
Nodes (4): get_submission_detail(), list_my_submissions(), list_submissions(), update_submission_grade()

### Community 39 - "submit_practical_work"
Cohesion: 0.15
Nodes (4): _extract_submission_payload(), ExtractedSubmissionPayload, submit_practical_work(), update_practical_grading_rules()

### Community 40 - "CoursesPage.tsx"
Cohesion: 0.27
Nodes (8): extractApiErrorMessage(), COURSE_VISUAL_META, CoursesPage(), CourseVisualMeta, fetchCourses(), FilterOption, ModuleRowCard(), PRACTICAL_FORMAT_LABELS

### Community 41 - "DomainError"
Cohesion: 0.17
Nodes (3): require_role(), role_checker(), create_application()

### Community 42 - "test_submit_all_four_practical_formats_via_api"
Cohesion: 0.17
Nodes (10): CourseSlug, make_auth_headers(), _get_course_module_and_practical(), _get_user_by_email(), _grant_quiz_pass(), test_antiplagiarism_flags_sha256_and_core_xml_matches_across_students(), test_health_check_and_jwt_login_flow(), test_submission_blocked_without_passed_quiz_and_unlocked_after_70_percent() (+2 more)

### Community 44 - "ModuleViewPage.tsx"
Cohesion: 0.21
Nodes (14): BinaryPracticalFormat, fetchModuleDetail(), fetchStudentPractical(), FILE_UPLOAD_FORMAT_META, FileUploadFormatMeta, FORMAT_BADGE_LABELS, formatFileSize(), LectureMarkdownRenderer() (+6 more)

### Community 45 - "HtmlSandbox.tsx"
Cohesion: 0.22
Nodes (10): @monaco-editor/react@4.6.0, buildStarterHtmlTemplate(), EditorColorTheme, HtmlSandbox(), HtmlSandboxProps, QUICK_HTML_SNIPPETS, QuickSnippet, SandboxViewMode (+2 more)

### Community 52 - "get_current_user"
Cohesion: 0.11
Nodes (6): get_current_user(), login(), read_current_user(), refresh_tokens(), decode_token(), RefreshTokenRequest

## Knowledge Gaps
- **1 isolated node(s):** `edu-auto-grader-backend`
  These have ≤1 connection - possible missing edges. (Counts symbols only; 542 node(s) total have ≤1 connection when file, concept and rationale nodes are included.)
- **22 thin communities (<3 nodes) omitted from report** — run `graphify query` to explore isolated nodes.

## Suggested Questions
_Questions this graph is uniquely positioned to answer:_

- **Why does `GradingRule` connect `GradingRule` to `AccdbGrader`, `DomainError`, `submission_service.py`, `submission_service.py`, `._evaluate_page_margins`, `docx_grader.py`, `xlsx_grader.py`, `.evaluate`, `get_db`, `ExtractedMetadata`, `HtmlGrader`, `XlsxGrader`, `DocxGrader`?**
  _High betweenness centrality (0.084) - this node is a cross-community bridge._
- **Are the 11 inferred relationships involving `GradingRule` (e.g. with `_serialize_practical_teacher()` and `AccdbGrader`) actually correct?**
  _`GradingRule` has 11 INFERRED edges - model-reasoned connections that need verification._
- **What connects `edu-auto-grader-backend` to the rest of the system?**
  _1 weakly-connected nodes found - possible missing edges._
- **Should `schemas/__init__.py` be split into smaller, more focused modules?**
  _Cohesion score 0.09852216748768473 - nodes in this community are weakly interconnected._
- **Why does `DocxGrader` connect `DocxGrader` to `GradingRule`, `submission_service.py`, `._evaluate_page_margins`, `InvalidFileFormatError`, `docx_grader.py`, `.evaluate`, `HtmlGrader`?**
  _High betweenness centrality (0.053) - this node is a cross-community bridge._
- **Are the 22 inferred relationships involving `User` (e.g. with `get_current_user()` and `require_role()`) actually correct?**
  _`User` has 22 INFERRED edges - model-reasoned connections that need verification._
- **Should `postgres` be split into smaller, more focused modules?**
  _Cohesion score 0.09523809523809523 - nodes in this community are weakly interconnected._