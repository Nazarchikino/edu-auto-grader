# Graph Report - edu-auto-grader  (2026-11-18)

## Corpus Check
- 40 files · ~11,291 words
- Verdict: corpus is large enough that graph structure adds value.
- Unclassified: 7 file(s) not represented in the graph (top: (none) 4, .ini 1, .mako 1)

## Summary
- 432 nodes · 744 edges · 30 communities (17 shown, 13 thin omitted)
- Extraction: 94% EXTRACTED · 6% INFERRED · 0% AMBIGUOUS · INFERRED: 41 edges (avg confidence: 0.95)
- Token cost: 0 input · 0 output

## Graph Freshness
- Built from commit: `6df36732`
- Run `git rev-parse HEAD` and compare to check if the graph is stale.
- Run `graphify update .` after code changes (no API cost).

## Community Hubs (Navigation)
- package.json
- postgres
- compilerOptions
- main.py
- main.tsx
- DomainError
- schemas/__init__.py
- client.ts
- scripts
- vite-env.d.ts
- env.py
- course.py
- auth.py
- edu-auto-grader-backend
- 0001_initial_schema.py
- devDependencies
- eslint.config.js
- api.ts
- vite
- course.ts
- grading.ts
- get_db

## God Nodes (most connected - your core abstractions)
1. `compilerOptions` - 19 edges
2. `PracticalFormat` - 18 edges
3. `Base` - 15 edges
4. `CourseSlug` - 14 edges
5. `User` - 14 edges
6. `build_seed_bundle()` - 14 edges
7. `Course` - 12 edges
8. `UserRole` - 12 edges
9. `seed_database()` - 11 edges
10. `Module` - 10 edges

## Surprising Connections (you probably didn't know these)
- `CourseCreate` --uses--> `CourseSlug`  [INFERRED]
  backend/app/schemas/course.py → backend/app/models/course.py
- `CourseRead` --uses--> `CourseSlug`  [INFERRED]
  backend/app/schemas/course.py → backend/app/models/course.py
- `SubmissionRead` --uses--> `CourseSlug`  [INFERRED]
  backend/app/schemas/submission.py → backend/app/models/course.py
- `_build_access_course()` --uses--> `PracticalFormat`  [INFERRED]
  backend/app/seed.py → backend/app/models/course.py
- `_build_excel_course()` --uses--> `PracticalFormat`  [INFERRED]
  backend/app/seed.py → backend/app/models/course.py

## Import Cycles
- None detected.

## Communities (30 total, 13 thin omitted)

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

### Community 5 - "DomainError"
Cohesion: 0.12
Nodes (6): DomainError, GradingError, InvalidFileFormatError, PlagiarismDetectedError, QuizNotPassedError, create_application()

### Community 6 - "schemas/__init__.py"
Cohesion: 0.05
Nodes (35): PracticalFormat, CourseCreate, CourseRead, CourseUpdate, ModuleCreate, ModuleDetailRead, ModuleSummaryRead, ModuleUpdate (+27 more)

### Community 7 - "client.ts"
Cohesion: 0.22
Nodes (3): axios@^1.7.7, apiClient, axios

### Community 8 - "scripts"
Cohesion: 0.33
Nodes (6): scripts, build, dev, lint, preview, typecheck

### Community 14 - "env.py"
Cohesion: 0.09
Nodes (6): do_run_migrations(), run_async_migrations(), run_migrations_offline(), run_migrations_online(), get_settings(), Settings

### Community 15 - "course.py"
Cohesion: 0.07
Nodes (25): Base, Course, CourseSlug, _enum_values(), Module, Practical, QuizQuestion, QuizAttempt (+17 more)

### Community 16 - "auth.py"
Cohesion: 0.11
Nodes (12): AcademicGroupBase, AcademicGroupCreate, AcademicGroupRead, ErrorResponse, LoginRequest, RefreshTokenRequest, TokenPayload, TokenResponse (+4 more)

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

## Knowledge Gaps
- **1 isolated node(s):** `edu-auto-grader-backend`
  These have ≤1 connection - possible missing edges. (Counts symbols only; 215 node(s) total have ≤1 connection when file, concept and rationale nodes are included.)
- **13 thin communities (<3 nodes) omitted from report** — run `graphify query` to explore isolated nodes.

## Suggested Questions
_Questions this graph is uniquely positioned to answer:_

- **Why does `PracticalFormat` connect `schemas/__init__.py` to `course.py`?**
  _High betweenness centrality (0.027) - this node is a cross-community bridge._
- **Are the 11 inferred relationships involving `PracticalFormat` (e.g. with `ModuleSummaryRead` and `PracticalCreate`) actually correct?**
  _`PracticalFormat` has 11 INFERRED edges - model-reasoned connections that need verification._
- **What connects `edu-auto-grader-backend` to the rest of the system?**
  _1 weakly-connected nodes found - possible missing edges._
- **Should `postgres` be split into smaller, more focused modules?**
  _Cohesion score 0.09523809523809523 - nodes in this community are weakly interconnected._
- **Why does `UserRole` connect `course.py` to `auth.py`?**
  _High betweenness centrality (0.020) - this node is a cross-community bridge._
- **Should `compilerOptions` be split into smaller, more focused modules?**
  _Cohesion score 0.09523809523809523 - nodes in this community are weakly interconnected._
- **Should `DomainError` be split into smaller, more focused modules?**
  _Cohesion score 0.11666666666666667 - nodes in this community are weakly interconnected._