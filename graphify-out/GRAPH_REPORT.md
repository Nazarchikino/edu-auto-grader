# Graph Report - edu-auto-grader  (2026-11-19)

## Corpus Check
- 76 files · ~73,195 words
- Verdict: corpus is large enough that graph structure adds value.
- Unclassified: 7 file(s) not represented in the graph (top: (none) 4, .ini 1, .mako 1)

## Summary
- 1301 nodes · 3614 edges · 53 communities (40 shown, 13 thin omitted)
- Extraction: 90% EXTRACTED · 10% INFERRED · 0% AMBIGUOUS · INFERRED: 370 edges (avg confidence: 0.94)
- Token cost: 0 input · 0 output

## Graph Freshness
- Built from commit: `7567c587`
- Run `git rev-parse HEAD` and compare to check if the graph is stale.
- Run `graphify update .` after code changes (no API cost).

## Community Hubs (Navigation)
- schemas/__init__.py
- postgres
- compilerOptions
- test_graders.py
- RuleBuilderPage.tsx
- _compile_jsonb_for_sqlite
- GroupJournalPage.tsx
- GradebookPage.tsx
- InvalidFileFormatError
- vite-env.d.ts
- export_service.py
- InvalidFileFormatError
- config.py
- seed.py
- UserRole
- courses.py
- edu-auto-grader-backend
- GradingRule
- package.json
- App.tsx
- admin.py
- AdminUsersPage.tsx
- course.ts
- accdb_grader.py
- AuthContext.tsx
- XlsxGrader
- DocxGrader
- AccdbGrader
- submission.py
- conftest.py
- list_my_submissions
- SubmissionService
- _enum_values
- CoursesPage.tsx
- DomainError
- test_submissions_api.py
- submit_practical_work
- ModuleViewPage.tsx
- react
- User
- _find_tag_attr_key
- ExportService
- services/__init__.py
- get_current_user
- 0001_initial_schema.py
- env.py

## God Nodes (most connected - your core abstractions)
1. `GradingRule` - 64 edges
2. `DomainError` - 55 edges
3. `User` - 55 edges
4. `InvalidFileFormatError` - 45 edges
5. `DocxGrader` - 45 edges
6. `PracticalFormat` - 43 edges
7. `GradingError` - 40 edges
8. `get_db()` - 39 edges
9. `SubmissionService` - 39 edges
10. `XlsxGrader` - 36 edges

## Surprising Connections (you probably didn't know these)
- `get_current_user()` --uses--> `User`  [INFERRED]
  backend/app/api/deps.py → backend/app/models/user.py
- `require_role()` --uses--> `User`  [INFERRED]
  backend/app/api/deps.py → backend/app/models/user.py
- `require_role()` --uses--> `UserRole`  [INFERRED]
  backend/app/api/deps.py → backend/app/models/user.py
- `_get_group_or_404()` --uses--> `AcademicGroup`  [INFERRED]
  backend/app/api/v1/admin.py → backend/app/models/user.py
- `_get_user_with_group_or_404()` --uses--> `User`  [INFERRED]
  backend/app/api/v1/admin.py → backend/app/models/user.py

## Import Cycles
- None detected.

## Communities (53 total, 13 thin omitted)

### Community 0 - "schemas/__init__.py"
Cohesion: 0.10
Nodes (11): AcademicGroupBase, AcademicGroupCreate, AcademicGroupRead, ErrorResponse, LoginRequest, RefreshTokenRequest, TokenPayload, TokenResponse (+3 more)

### Community 1 - "postgres"
Cohesion: 0.10
Nodes (20): POSTGRES_DB, POSTGRES_PASSWORD, POSTGRES_USER, interval, retries, test, timeout, container_name (+12 more)

### Community 2 - "compilerOptions"
Cohesion: 0.10
Nodes (20): compilerOptions, allowImportingTsExtensions, isolatedModules, jsx, lib, module, moduleDetection, moduleResolution (+12 more)

### Community 3 - "test_graders.py"
Cohesion: 0.11
Nodes (9): GradingRuleType, build_sample_accdb(), test_accdb_grader_detects_missing_schema_elements_and_invalid_header(), test_accdb_grader_evaluates_tables_columns_and_types(), test_docx_grader_detects_formatting_violations_and_corrupt_files(), test_docx_grader_evaluates_valid_document(), test_grader_factory_resolves_all_four_formats(), test_xlsx_grader_evaluates_formulas_values_and_charts() (+1 more)

### Community 4 - "RuleBuilderPage.tsx"
Cohesion: 0.19
Nodes (14): extractApiErrorMessage(), fetchCourses(), fetchPracticalTeacher(), FORMAT_BADGE_CONFIG, renderFormatIcon(), RULE_TYPE_SPECS, RuleBuilderPage(), RuleTypeSpec (+6 more)

### Community 6 - "GroupJournalPage.tsx"
Cohesion: 0.26
Nodes (11): PlagiarismBadge(), PlagiarismBadgeProps, COURSE_SLUG_BADGES, fetchAcademicGroups(), fetchCourses(), fetchGroupJournal(), fetchSubmissionDetail(), formatShortDate() (+3 more)

### Community 7 - "GradebookPage.tsx"
Cohesion: 0.10
Nodes (27): COURSE_SLUG_LABELS, CriterionBreakdownItem(), CriterionFilterMode, extractFileNameFromPath(), FORMAT_META, formatDateTime(), GradingReportCard(), GradingReportCardProps (+19 more)

### Community 8 - "InvalidFileFormatError"
Cohesion: 0.10
Nodes (8): GradingError, InvalidFileFormatError, BaseGrader, GraderFactory, _parse_text_match_expected(), _strip_quotes(), _format_cell_value(), PracticalFormat

### Community 11 - "export_service.py"
Cohesion: 0.12
Nodes (6): _configure_pdf_font(), PracticalColumnInfo, _prepare_pdf_text(), render_group_journal_pdf(), _sanitize_filename_token(), _transliterate_to_ascii()

### Community 13 - "InvalidFileFormatError"
Cohesion: 0.09
Nodes (16): check_submission_plagiarism(), _coerce_metadata(), compute_bytes_sha256(), compute_code_sha256(), compute_file_sha256(), compute_submission_hash(), evaluate_plagiarism(), extract_core_xml_metadata() (+8 more)

### Community 15 - "seed.py"
Cohesion: 0.12
Nodes (15): Course, QuizQuestion, AcademicGroup, _build_access_course(), _build_excel_course(), _build_html_course(), build_seed_bundle(), _build_word_course() (+7 more)

### Community 16 - "UserRole"
Cohesion: 0.16
Nodes (8): create_access_token(), create_refresh_token(), create_token_pair(), _encode_jwt_token(), hash_password(), verify_password(), _enum_values(), UserRole

### Community 17 - "courses.py"
Cohesion: 0.05
Nodes (43): _build_module_detail_read(), create_course(), create_module(), create_quiz_question(), delete_quiz_question(), _fetch_user_progress_maps(), get_course(), get_module() (+35 more)

### Community 22 - "GradingRule"
Cohesion: 0.09
Nodes (8): _attribute_value_matches(), HtmlGrader, _is_doctype_target(), _normalize_selector(), _normalize_text(), GradingRule, test_html_grader_detects_missing_tags_and_rejects_empty_code(), test_html_grader_evaluates_semantic_dom_structure_and_attributes()

### Community 23 - "package.json"
Cohesion: 0.07
Nodes (39): devDependencies, autoprefixer@^10.4.20, eslint@^9.15.0, @eslint/js@^9.15.0, eslint-plugin-react-hooks@^5.0.0, eslint-plugin-react-refresh@^0.4.14, globals@^15.12.0, postcss@^8.4.49 (+31 more)

### Community 24 - "App.tsx"
Cohesion: 0.13
Nodes (27): react-router-dom@^6.28.0, App(), ProtectedAppLayout(), RoleHomeRedirect(), Navbar(), NavbarProps, resolvePageTitle(), ROLE_BADGE_CONFIG (+19 more)

### Community 25 - "admin.py"
Cohesion: 0.11
Nodes (17): create_admin_group(), create_admin_user(), delete_admin_group(), delete_admin_user(), _ensure_email_unique(), _ensure_group_code_unique(), _get_group_or_404(), _get_user_with_group_or_404() (+9 more)

### Community 26 - "AdminUsersPage.tsx"
Cohesion: 0.07
Nodes (36): AdminTab, AdminUsersPage(), COURSE_YEARS, CourseYearFilter, DeleteTarget, FeedbackBanner, fetchAdminGroups(), fetchAdminUsers() (+28 more)

### Community 27 - "course.ts"
Cohesion: 0.11
Nodes (30): CourseEditorPage(), DISCIPLINE_META, DisciplineMeta, EditorTab, fetchCourses(), fetchModuleDetail(), fetchModuleQuizQuestions(), fetchPracticalTeacher() (+22 more)

### Community 28 - "accdb_grader.py"
Cohesion: 0.14
Nodes (6): build_accdb_bytes(), _encode_data_page(), _encode_msys_catalog_record(), _encode_tdef_page(), _parse_ddl_column_type(), _resolve_canonical_type()

### Community 29 - "AuthContext.tsx"
Cohesion: 0.23
Nodes (15): apiClient, clearAuthTokens(), getAccessToken(), getRefreshToken(), setAccessToken(), setRefreshToken(), AuthContext, AuthContextValue (+7 more)

### Community 30 - "XlsxGrader"
Cohesion: 0.07
Nodes (4): _canonicalize_formula(), _is_wrapped_in_parens(), _try_parse_numeric(), XlsxGrader

### Community 31 - "DocxGrader"
Cohesion: 0.06
Nodes (3): DocxGrader, _format_number(), CriterionResult

### Community 32 - "AccdbGrader"
Cohesion: 0.08
Nodes (7): AccdbColumnSchema, AccdbDatabaseSchema, AccdbGrader, AccdbTableSchema, _is_numeric_condition(), _is_system_table_name(), _strip_identifiers()

### Community 34 - "submission.py"
Cohesion: 0.11
Nodes (12): GradingReport, GradingRulesUpdateRequest, PlagiarismCheckResult, CriterionErrorStat, GroupJournalRead, GroupJournalRow, GroupJournalStudentCell, HtmlSubmissionRequest (+4 more)

### Community 35 - "conftest.py"
Cohesion: 0.09
Nodes (6): async_client(), _create_sqlite_test_engine(), db_session(), _fast_seed_hash_password(), _replace_zip_member(), rewrite_openxml_core_metadata()

### Community 36 - "list_my_submissions"
Cohesion: 0.22
Nodes (4): get_submission_detail(), list_my_submissions(), list_submissions(), update_submission_grade()

### Community 37 - "SubmissionService"
Cohesion: 0.10
Nodes (5): PlagiarismDetectedError, Submission, SubmissionRead, serialize_submission(), SubmissionService

### Community 40 - "CoursesPage.tsx"
Cohesion: 0.24
Nodes (9): COURSE_VISUAL_META, CoursesPage(), CourseVisualMeta, fetchCourses(), FilterOption, ModuleRowCard(), PRACTICAL_FORMAT_LABELS, COURSE_SLUGS (+1 more)

### Community 41 - "DomainError"
Cohesion: 0.15
Nodes (6): require_role(), role_checker(), _parse_export_format(), ExtractedSubmissionPayload, DomainError, create_application()

### Community 42 - "test_submissions_api.py"
Cohesion: 0.08
Nodes (16): CourseSlug, build_sample_docx(), build_sample_xlsx(), _set_sqlite_pragma(), make_auth_headers(), SqliteAsyncSessionAdapter, test_admin_endpoints_enforce_admin_rbac(), test_admin_users_crud_filters_and_safety_guards() (+8 more)

### Community 43 - "submit_practical_work"
Cohesion: 0.18
Nodes (3): _extract_submission_payload(), submit_practical_work(), update_practical_grading_rules()

### Community 44 - "ModuleViewPage.tsx"
Cohesion: 0.13
Nodes (22): buildStarterHtmlTemplate(), EditorColorTheme, HtmlSandbox(), HtmlSandboxProps, QUICK_HTML_SNIPPETS, QuickSnippet, SandboxViewMode, BinaryPracticalFormat (+14 more)

### Community 45 - "react"
Cohesion: 0.15
Nodes (13): dependencies, axios@^1.7.7, lucide-react@^0.460.0, @monaco-editor/react@4.6.0, react@^18.3.1, react-dom@^18.3.1, @tanstack/react-query@^5.60.0, queryClient (+5 more)

### Community 46 - "User"
Cohesion: 0.20
Nodes (7): Base, Module, Practical, QuizAttempt, User, _get_user_by_email(), test_admin_academic_groups_crud_and_detachment()

### Community 49 - "_find_tag_attr_key"
Cohesion: 0.38
Nodes (3): _find_tag_attr_key(), _get_tag_attribute_str(), _tag_has_attribute()

### Community 50 - "ExportService"
Cohesion: 0.08
Nodes (7): export_group_journal(), get_group_journal(), list_academic_groups(), ExportFormat, build_content_disposition(), ExportedDocument, ExportService

### Community 51 - "services/__init__.py"
Cohesion: 0.15
Nodes (6): _auto_adjust_worksheet_columns(), GroupJournalBundle, render_group_journal_xlsx(), calculate_variant_index(), resolve_student_variant(), serialize_practical_teacher()

### Community 52 - "get_current_user"
Cohesion: 0.13
Nodes (5): get_current_user(), login(), read_current_user(), refresh_tokens(), decode_token()

### Community 63 - "env.py"
Cohesion: 0.18
Nodes (4): do_run_migrations(), run_async_migrations(), run_migrations_offline(), run_migrations_online()

## Knowledge Gaps
- **1 isolated node(s):** `edu-auto-grader-backend`
  These have ≤1 connection - possible missing edges. (Counts symbols only; 570 node(s) total have ≤1 connection when file, concept and rationale nodes are included.)
- **13 thin communities (<3 nodes) omitted from report** — run `graphify query` to explore isolated nodes.

## Suggested Questions
_Questions this graph is uniquely positioned to answer:_

- **Why does `GradingRule` connect `GradingRule` to `AccdbGrader`, `.evaluate`, `submission.py`, `test_graders.py`, `SubmissionService`, `InvalidFileFormatError`, `courses.py`, `services/__init__.py`, `accdb_grader.py`, `XlsxGrader`, `DocxGrader`?**
  _High betweenness centrality (0.067) - this node is a cross-community bridge._
- **Are the 11 inferred relationships involving `GradingRule` (e.g. with `_serialize_practical_teacher()` and `AccdbGrader`) actually correct?**
  _`GradingRule` has 11 INFERRED edges - model-reasoned connections that need verification._
- **What connects `edu-auto-grader-backend` to the rest of the system?**
  _1 weakly-connected nodes found - possible missing edges._
- **Should `schemas/__init__.py` be split into smaller, more focused modules?**
  _Cohesion score 0.10256410256410256 - nodes in this community are weakly interconnected._
- **Why does `DomainError` connect `DomainError` to `submission.py`, `SubmissionService`, `InvalidFileFormatError`, `export_service.py`, `User`, `UserRole`, `courses.py`, `ExportService`, `get_current_user`, `.__init__`, `admin.py`?**
  _High betweenness centrality (0.055) - this node is a cross-community bridge._
- **Are the 14 inferred relationships involving `DomainError` (e.g. with `delete_admin_user()` and `update_admin_user()`) actually correct?**
  _`DomainError` has 14 INFERRED edges - model-reasoned connections that need verification._
- **Should `postgres` be split into smaller, more focused modules?**
  _Cohesion score 0.09523809523809523 - nodes in this community are weakly interconnected._