# Graph Report - edu-auto-grader  (2026-11-18)

## Corpus Check
- 53 files · ~29,313 words
- Verdict: corpus is large enough that graph structure adds value.
- Unclassified: 7 file(s) not represented in the graph (top: (none) 4, .ini 1, .mako 1)

## Summary
- 912 nodes · 2076 edges · 54 communities (36 shown, 18 thin omitted)
- Extraction: 97% EXTRACTED · 3% INFERRED · 0% AMBIGUOUS · INFERRED: 53 edges (avg confidence: 0.93)
- Token cost: 0 input · 0 output

## Graph Freshness
- Built from commit: `329558b5`
- Run `git rev-parse HEAD` and compare to check if the graph is stale.
- Run `graphify update .` after code changes (no API cost).

## Community Hubs (Navigation)
- package.json
- postgres
- compilerOptions
- main.py
- main.tsx
- QuizService
- courses.py
- client.ts
- scripts
- vite-env.d.ts
- schemas/__init__.py
- metadata.py
- env.py
- seed.py
- get_db
- edu-auto-grader-backend
- HtmlGrader
- devDependencies
- eslint.config.js
- api.ts
- vite
- course.ts
- grading.ts
- v1/auth.py
- XlsxGrader
- DocxGrader
- AccdbGrader
- BaseGrader
- courses.py
- xlsx_grader.py
- DomainError
- accdb_grader.py
- docx_grader.py
- User
- GradingError
- security.py
- evaluate_plagiarism
- UUID
- main.py
- BaseModel
- resolve_student_variant
- _find_tag_attr_key
- 0001_initial_schema.py
- UserBase
- _enum_values

## God Nodes (most connected - your core abstractions)
1. `DocxGrader` - 34 edges
2. `GradingError` - 32 edges
3. `User` - 28 edges
4. `DomainError` - 28 edges
5. `InvalidFileFormatError` - 27 edges
6. `PracticalFormat` - 25 edges
7. `XlsxGrader` - 25 edges
8. `BaseGrader` - 25 edges
9. `get_db()` - 22 edges
10. `compilerOptions` - 19 edges

## Surprising Connections (you probably didn't know these)
- `UserBase` --uses--> `UserRole`  [INFERRED]
  backend/app/schemas/auth.py → backend/app/models/user.py
- `UserUpdate` --uses--> `UserRole`  [INFERRED]
  backend/app/schemas/auth.py → backend/app/models/user.py
- `SubmissionRead` --uses--> `CourseSlug`  [INFERRED]
  backend/app/schemas/submission.py → backend/app/models/course.py
- `SubmissionRead` --uses--> `ExtractedMetadata`  [INFERRED]
  backend/app/schemas/submission.py → backend/app/schemas/grading.py
- `SubmissionRead` --uses--> `GradingReport`  [INFERRED]
  backend/app/schemas/submission.py → backend/app/schemas/grading.py

## Import Cycles
- None detected.

## Communities (54 total, 18 thin omitted)

### Community 0 - "package.json"
Cohesion: 0.17
Nodes (15): dependencies, lucide-react@^0.460.0, @monaco-editor/react@4.6.0, react-dom@^18.3.1, react-router-dom@^6.28.0, @tanstack/react-query@^5.60.0, name, private (+7 more)

### Community 1 - "postgres"
Cohesion: 0.10
Nodes (20): POSTGRES_DB, POSTGRES_PASSWORD, POSTGRES_USER, interval, retries, test, timeout, container_name (+12 more)

### Community 2 - "compilerOptions"
Cohesion: 0.10
Nodes (20): compilerOptions, allowImportingTsExtensions, isolatedModules, jsx, lib, module, moduleDetection, moduleResolution (+12 more)

### Community 4 - "main.tsx"
Cohesion: 0.32
Nodes (5): react@^18.3.1, App(), queryClient, rootElement, react

### Community 6 - "courses.py"
Cohesion: 0.08
Nodes (18): CourseCreate, CourseRead, CourseUpdate, ModuleCreate, ModuleDetailRead, ModuleSummaryRead, ModuleUpdate, PracticalCreate (+10 more)

### Community 7 - "client.ts"
Cohesion: 0.22
Nodes (3): axios@^1.7.7, apiClient, axios

### Community 8 - "scripts"
Cohesion: 0.33
Nodes (6): scripts, build, dev, lint, preview, typecheck

### Community 11 - "schemas/__init__.py"
Cohesion: 0.13
Nodes (11): AcademicGroupBase, AcademicGroupCreate, AcademicGroupRead, CriterionErrorStat, ExportFormat, GroupJournalRead, GroupJournalRow, GroupJournalStudentCell (+3 more)

### Community 13 - "metadata.py"
Cohesion: 0.15
Nodes (10): compute_bytes_sha256(), compute_code_sha256(), compute_file_sha256(), compute_submission_hash(), extract_core_xml_metadata(), extract_document_metadata(), _find_xml_text(), normalize_code_for_hashing() (+2 more)

### Community 14 - "env.py"
Cohesion: 0.10
Nodes (6): do_run_migrations(), run_async_migrations(), run_migrations_offline(), run_migrations_online(), get_settings(), Settings

### Community 15 - "seed.py"
Cohesion: 0.11
Nodes (19): Course, CourseSlug, Module, Practical, PracticalFormat, QuizQuestion, AcademicGroup, _build_access_course() (+11 more)

### Community 17 - "get_db"
Cohesion: 0.06
Nodes (21): get_current_user(), read_current_user(), serialize_user(), create_course(), create_quiz_question(), delete_quiz_question(), _fetch_user_progress_maps(), get_course() (+13 more)

### Community 22 - "HtmlGrader"
Cohesion: 0.11
Nodes (5): _attribute_value_matches(), HtmlGrader, _is_doctype_target(), _normalize_selector(), _normalize_text()

### Community 23 - "devDependencies"
Cohesion: 0.13
Nodes (15): devDependencies, autoprefixer@^10.4.20, eslint@^9.15.0, postcss@^8.4.49, tailwindcss@^3.4.15, @types/react@^18.3.12, @types/react-dom@^18.3.1, typescript@~5.6.3 (+7 more)

### Community 24 - "eslint.config.js"
Cohesion: 0.18
Nodes (10): @eslint/js@^9.15.0, eslint-plugin-react-hooks@^5.0.0, eslint-plugin-react-refresh@^0.4.14, globals@^15.12.0, typescript-eslint@^8.15.0, @eslint/js, eslint-plugin-react-hooks, eslint-plugin-react-refresh (+2 more)

### Community 25 - "api.ts"
Cohesion: 0.09
Nodes (23): AcademicGroupBase, AcademicGroupCreate, AcademicGroupRead, CriterionErrorStat, ErrorResponse, EXPORT_FORMATS, ExportFormat, GroupJournalRead (+15 more)

### Community 26 - "vite"
Cohesion: 0.40
Nodes (4): vite@^5.4.11, @vitejs/plugin-react@^4.3.3, vite, @vitejs/plugin-react

### Community 27 - "course.ts"
Cohesion: 0.13
Nodes (22): COURSE_SLUGS, CourseCreate, CourseRead, CourseUpdate, ModuleCreate, ModuleDetailRead, ModuleSummaryRead, ModuleUpdate (+14 more)

### Community 28 - "grading.ts"
Cohesion: 0.20
Nodes (10): SubmissionRead, CourseSlug, CriterionResult, ExtractedMetadata, GRADING_RULE_TYPES, GradingReport, GradingRulesUpdateRequest, GradingRuleType (+2 more)

### Community 29 - "v1/auth.py"
Cohesion: 0.17
Nodes (4): login(), refresh_tokens(), decode_token(), verify_password()

### Community 30 - "XlsxGrader"
Cohesion: 0.08
Nodes (3): _canonicalize_formula(), _is_wrapped_in_parens(), XlsxGrader

### Community 32 - "AccdbGrader"
Cohesion: 0.08
Nodes (7): AccdbColumnSchema, AccdbDatabaseSchema, AccdbGrader, AccdbTableSchema, _is_system_table_name(), _resolve_canonical_type(), _strip_identifiers()

### Community 35 - "courses.py"
Cohesion: 0.26
Nodes (3): Base, QuizAttempt, Submission

### Community 36 - "xlsx_grader.py"
Cohesion: 0.16
Nodes (3): _format_number(), _format_cell_value(), _try_parse_numeric()

### Community 37 - "DomainError"
Cohesion: 0.18
Nodes (5): require_role(), role_checker(), DomainError, PlagiarismDetectedError, QuizNotPassedError

### Community 38 - "accdb_grader.py"
Cohesion: 0.13
Nodes (6): build_accdb_bytes(), _encode_data_page(), _encode_msys_catalog_record(), _encode_tdef_page(), _is_numeric_condition(), _parse_ddl_column_type()

### Community 39 - "docx_grader.py"
Cohesion: 0.11
Nodes (6): CriterionResult, GradingReport, GradingRule, GradingRulesUpdateRequest, GradingRuleType, PlagiarismCheckResult

### Community 40 - "User"
Cohesion: 0.23
Nodes (5): _build_module_detail_read(), create_module(), get_module(), _load_module_or_404(), User

### Community 41 - "GradingError"
Cohesion: 0.21
Nodes (4): GradingError, InvalidFileFormatError, _parse_text_match_expected(), _strip_quotes()

### Community 42 - "security.py"
Cohesion: 0.18
Nodes (5): hash_password(), _enum_values(), UserRole, TokenPayload, TokenResponse

### Community 43 - "evaluate_plagiarism"
Cohesion: 0.16
Nodes (4): check_submission_plagiarism(), _coerce_metadata(), evaluate_plagiarism(), SubmissionRecordProtocol

### Community 44 - "UUID"
Cohesion: 0.29
Nodes (4): create_access_token(), create_refresh_token(), create_token_pair(), _encode_jwt_token()

### Community 46 - "BaseModel"
Cohesion: 0.22
Nodes (4): ErrorResponse, LoginRequest, RefreshTokenRequest, UserUpdate

### Community 47 - "resolve_student_variant"
Cohesion: 0.29
Nodes (3): PracticalVariant, calculate_variant_index(), resolve_student_variant()

### Community 48 - "_find_tag_attr_key"
Cohesion: 0.38
Nodes (3): _find_tag_attr_key(), _get_tag_attribute_str(), _tag_has_attribute()

### Community 50 - "UserBase"
Cohesion: 0.33
Nodes (3): UserBase, UserCreate, UserRead

## Knowledge Gaps
- **1 isolated node(s):** `edu-auto-grader-backend`
  These have ≤1 connection - possible missing edges. (Counts symbols only; 447 node(s) total have ≤1 connection when file, concept and rationale nodes are included.)
- **18 thin communities (<3 nodes) omitted from report** — run `graphify query` to explore isolated nodes.

## Suggested Questions
_Questions this graph is uniquely positioned to answer:_

- **Why does `GradingError` connect `GradingError` to `AccdbGrader`, `._parse_expected_margins`, `BaseGrader`, `xlsx_grader.py`, `DomainError`, `accdb_grader.py`, `docx_grader.py`, `HtmlGrader`, `XlsxGrader`, `DocxGrader`?**
  _High betweenness centrality (0.088) - this node is a cross-community bridge._
- **Are the 6 inferred relationships involving `User` (e.g. with `_build_access_course()` and `_build_excel_course()`) actually correct?**
  _`User` has 6 INFERRED edges - model-reasoned connections that need verification._
- **What connects `edu-auto-grader-backend` to the rest of the system?**
  _1 weakly-connected nodes found - possible missing edges._
- **Should `postgres` be split into smaller, more focused modules?**
  _Cohesion score 0.09523809523809523 - nodes in this community are weakly interconnected._
- **Why does `DocxGrader` connect `DocxGrader` to `._parse_expected_margins`, `BaseGrader`, `docx_grader.py`, `metadata.py`, `BaseGrader`, `._extract_alignment_name`?**
  _High betweenness centrality (0.069) - this node is a cross-community bridge._
- **Should `compilerOptions` be split into smaller, more focused modules?**
  _Cohesion score 0.09523809523809523 - nodes in this community are weakly interconnected._
- **Why does `DomainError` connect `DomainError` to `courses.py`, `QuizService`, `User`, `GradingError`, `security.py`, `main.py`, `get_db`, `v1/auth.py`?**
  _High betweenness centrality (0.064) - this node is a cross-community bridge._