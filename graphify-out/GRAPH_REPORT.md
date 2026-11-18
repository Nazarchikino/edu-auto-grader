# Graph Report - edu-auto-grader  (2026-11-18)

## Corpus Check
- 46 files · ~14,437 words
- Verdict: corpus is large enough that graph structure adds value.
- Unclassified: 7 file(s) not represented in the graph (top: (none) 4, .ini 1, .mako 1)

## Summary
- 571 nodes · 1224 edges · 35 communities (23 shown, 12 thin omitted)
- Extraction: 96% EXTRACTED · 4% INFERRED · 0% AMBIGUOUS · INFERRED: 46 edges (avg confidence: 0.94)
- Token cost: 0 input · 0 output

## Graph Freshness
- Built from commit: `7a015ddd`
- Run `git rev-parse HEAD` and compare to check if the graph is stale.
- Run `graphify update .` after code changes (no API cost).

## Community Hubs (Navigation)
- package.json
- postgres
- compilerOptions
- main.py
- main.tsx
- DomainError
- submission.py
- client.ts
- scripts
- vite-env.d.ts
- security.py
- env.py
- course.py
- auth.py
- get_db
- edu-auto-grader-backend
- 0001_initial_schema.py
- devDependencies
- eslint.config.js
- api.ts
- vite
- course.ts
- grading.ts
- login
- BaseModel
- seed_database
- UserRole
- GradingRuleType
- ExportFormat

## God Nodes (most connected - your core abstractions)
1. `User` - 28 edges
2. `DomainError` - 28 edges
3. `get_db()` - 22 edges
4. `compilerOptions` - 19 edges
5. `PracticalFormat` - 18 edges
6. `Course` - 16 edges
7. `get_current_user()` - 16 edges
8. `Base` - 15 edges
9. `Module` - 15 edges
10. `Practical` - 15 edges

## Surprising Connections (you probably didn't know these)
- `submit_module_quiz()` --uses--> `QuizService`  [INFERRED]
  backend/app/api/v1/courses.py → backend/app/services/quiz_service.py
- `get_practical_for_student()` --uses--> `QuizService`  [INFERRED]
  backend/app/api/v1/courses.py → backend/app/services/quiz_service.py
- `seed_database()` --uses--> `Course`  [INFERRED]
  backend/app/seed.py → backend/app/models/course.py
- `SubmissionRead` --uses--> `CourseSlug`  [INFERRED]
  backend/app/schemas/submission.py → backend/app/models/course.py
- `seed_database()` --uses--> `AcademicGroup`  [INFERRED]
  backend/app/seed.py → backend/app/models/user.py

## Import Cycles
- None detected.

## Communities (35 total, 12 thin omitted)

### Community 0 - "package.json"
Cohesion: 0.17
Nodes (15): dependencies, lucide-react@^0.460.0, @monaco-editor/react@4.6.0, react-dom@^18.3.1, react-router-dom@^6.28.0, @tanstack/react-query@^5.60.0, name, private (+7 more)

### Community 1 - "postgres"
Cohesion: 0.10
Nodes (20): POSTGRES_DB, POSTGRES_PASSWORD, POSTGRES_USER, interval, retries, test, timeout, container_name (+12 more)

### Community 2 - "compilerOptions"
Cohesion: 0.10
Nodes (20): compilerOptions, allowImportingTsExtensions, isolatedModules, jsx, lib, module, moduleDetection, moduleResolution (+12 more)

### Community 3 - "main.py"
Cohesion: 0.10
Nodes (3): create_application(), async_client(), test_health_check()

### Community 4 - "main.tsx"
Cohesion: 0.32
Nodes (5): react@^18.3.1, App(), queryClient, rootElement, react

### Community 5 - "DomainError"
Cohesion: 0.07
Nodes (10): require_role(), role_checker(), DomainError, GradingError, InvalidFileFormatError, PlagiarismDetectedError, QuizNotPassedError, calculate_variant_index() (+2 more)

### Community 6 - "submission.py"
Cohesion: 0.18
Nodes (6): CriterionResult, ExtractedMetadata, GradingReport, GradingRulesUpdateRequest, PlagiarismCheckResult, SubmissionRead

### Community 7 - "client.ts"
Cohesion: 0.22
Nodes (3): axios@^1.7.7, apiClient, axios

### Community 8 - "scripts"
Cohesion: 0.33
Nodes (6): scripts, build, dev, lint, preview, typecheck

### Community 11 - "security.py"
Cohesion: 0.14
Nodes (8): create_access_token(), create_refresh_token(), create_token_pair(), decode_token(), _encode_jwt_token(), hash_password(), verify_password(), TokenResponse

### Community 14 - "env.py"
Cohesion: 0.09
Nodes (6): do_run_migrations(), run_async_migrations(), run_migrations_offline(), run_migrations_online(), get_settings(), Settings

### Community 15 - "course.py"
Cohesion: 0.06
Nodes (39): Base, Course, CourseSlug, _enum_values(), Module, Practical, PracticalFormat, QuizQuestion (+31 more)

### Community 16 - "auth.py"
Cohesion: 0.15
Nodes (11): AcademicGroupBase, AcademicGroupCreate, AcademicGroupRead, ErrorResponse, LoginRequest, RefreshTokenRequest, TokenPayload, UserBase (+3 more)

### Community 17 - "get_db"
Cohesion: 0.06
Nodes (23): get_current_user(), _build_module_detail_read(), create_course(), create_module(), create_quiz_question(), delete_quiz_question(), _fetch_user_progress_maps(), get_course() (+15 more)

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

### Community 29 - "login"
Cohesion: 0.18
Nodes (4): login(), read_current_user(), refresh_tokens(), serialize_user()

### Community 30 - "BaseModel"
Cohesion: 0.15
Nodes (6): CriterionErrorStat, GroupJournalRead, GroupJournalRow, GroupJournalStudentCell, HtmlSubmissionRequest, ManualGradeUpdateRequest

### Community 31 - "seed_database"
Cohesion: 0.21
Nodes (5): main(), run_seed(), seed_database(), SeedSummary, summarize_bundle()

## Knowledge Gaps
- **1 isolated node(s):** `edu-auto-grader-backend`
  These have ≤1 connection - possible missing edges. (Counts symbols only; 283 node(s) total have ≤1 connection when file, concept and rationale nodes are included.)
- **12 thin communities (<3 nodes) omitted from report** — run `graphify query` to explore isolated nodes.

## Suggested Questions
_Questions this graph is uniquely positioned to answer:_

- **Why does `DomainError` connect `DomainError` to `main.py`, `security.py`, `course.py`, `get_db`, `login`?**
  _High betweenness centrality (0.047) - this node is a cross-community bridge._
- **Are the 6 inferred relationships involving `User` (e.g. with `_build_access_course()` and `_build_excel_course()`) actually correct?**
  _`User` has 6 INFERRED edges - model-reasoned connections that need verification._
- **What connects `edu-auto-grader-backend` to the rest of the system?**
  _1 weakly-connected nodes found - possible missing edges._
- **Should `postgres` be split into smaller, more focused modules?**
  _Cohesion score 0.09523809523809523 - nodes in this community are weakly interconnected._
- **Why does `User` connect `course.py` to `DomainError`, `security.py`, `get_db`, `login`, `seed_database`?**
  _High betweenness centrality (0.031) - this node is a cross-community bridge._
- **Should `compilerOptions` be split into smaller, more focused modules?**
  _Cohesion score 0.09523809523809523 - nodes in this community are weakly interconnected._
- **Why does `UserRole` connect `UserRole` to `auth.py`, `security.py`, `seed_database`, `course.py`?**
  _High betweenness centrality (0.019) - this node is a cross-community bridge._