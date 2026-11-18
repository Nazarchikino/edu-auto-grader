# Graph Report - edu-auto-grader  (2026-11-18)

## Corpus Check
- 37 files · ~10,399 words
- Verdict: corpus is large enough that graph structure adds value.
- Unclassified: 7 file(s) not represented in the graph (top: (none) 4, .ini 1, .mako 1)

## Summary
- 372 nodes · 636 edges · 27 communities (15 shown, 12 thin omitted)
- Extraction: 99% EXTRACTED · 1% INFERRED · 0% AMBIGUOUS · INFERRED: 7 edges (avg confidence: 0.94)
- Token cost: 0 input · 0 output

## Graph Freshness
- Built from commit: `8dbb51f6`
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
- run_seed
- devDependencies
- eslint.config.js
- 0001_initial_schema.py
- vite

## God Nodes (most connected - your core abstractions)
1. `compilerOptions` - 19 edges
2. `Base` - 15 edges
3. `User` - 12 edges
4. `build_seed_bundle()` - 12 edges
5. `Module` - 10 edges
6. `Practical` - 10 edges
7. `Course` - 9 edges
8. `QuizQuestion` - 9 edges
9. `DomainError` - 9 edges
10. `GradingRule` - 8 edges

## Surprising Connections (you probably didn't know these)
- `PracticalCreate` --uses--> `GradingRule`  [INFERRED]
  backend/app/schemas/course.py → backend/app/schemas/grading.py
- `PracticalUpdate` --uses--> `GradingRule`  [INFERRED]
  backend/app/schemas/course.py → backend/app/schemas/grading.py
- `PracticalTeacherRead` --uses--> `GradingRule`  [INFERRED]
  backend/app/schemas/course.py → backend/app/schemas/grading.py
- `SubmissionRead` --uses--> `GradingReport`  [INFERRED]
  backend/app/schemas/submission.py → backend/app/schemas/grading.py
- `SubmissionRead` --uses--> `ExtractedMetadata`  [INFERRED]
  backend/app/schemas/submission.py → backend/app/schemas/grading.py

## Import Cycles
- None detected.

## Communities (27 total, 12 thin omitted)

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
Nodes (34): CourseCreate, CourseRead, CourseUpdate, ModuleCreate, ModuleDetailRead, ModuleSummaryRead, ModuleUpdate, PracticalCreate (+26 more)

### Community 7 - "client.ts"
Cohesion: 0.22
Nodes (3): axios@^1.7.7, apiClient, axios

### Community 8 - "scripts"
Cohesion: 0.33
Nodes (6): scripts, build, dev, lint, preview, typecheck

### Community 14 - "env.py"
Cohesion: 0.08
Nodes (7): do_run_migrations(), run_async_migrations(), run_migrations_offline(), run_migrations_online(), get_settings(), Settings, main()

### Community 15 - "course.py"
Cohesion: 0.10
Nodes (18): Base, Course, CourseSlug, _enum_values(), Module, Practical, PracticalFormat, QuizQuestion (+10 more)

### Community 16 - "auth.py"
Cohesion: 0.11
Nodes (12): AcademicGroupBase, AcademicGroupCreate, AcademicGroupRead, ErrorResponse, LoginRequest, RefreshTokenRequest, TokenPayload, TokenResponse (+4 more)

### Community 22 - "run_seed"
Cohesion: 0.14
Nodes (8): get_db(), build_seed_bundle(), hash_password(), run_seed(), seed_database(), SeedBundle, SeedSummary, summarize_bundle()

### Community 23 - "devDependencies"
Cohesion: 0.13
Nodes (15): devDependencies, autoprefixer@^10.4.20, eslint@^9.15.0, postcss@^8.4.49, tailwindcss@^3.4.15, @types/react@^18.3.12, @types/react-dom@^18.3.1, typescript@~5.6.3 (+7 more)

### Community 24 - "eslint.config.js"
Cohesion: 0.18
Nodes (10): @eslint/js@^9.15.0, eslint-plugin-react-hooks@^5.0.0, eslint-plugin-react-refresh@^0.4.14, globals@^15.12.0, typescript-eslint@^8.15.0, @eslint/js, eslint-plugin-react-hooks, eslint-plugin-react-refresh (+2 more)

### Community 26 - "vite"
Cohesion: 0.40
Nodes (4): vite@^5.4.11, @vitejs/plugin-react@^4.3.3, vite, @vitejs/plugin-react

## Knowledge Gaps
- **1 isolated node(s):** `edu-auto-grader-backend`
  These have ≤1 connection - possible missing edges. (Counts symbols only; 175 node(s) total have ≤1 connection when file, concept and rationale nodes are included.)
- **12 thin communities (<3 nodes) omitted from report** — run `graphify query` to explore isolated nodes.

## Suggested Questions
_Questions this graph is uniquely positioned to answer:_

- **Why does `CourseSlug` connect `course.py` to `schemas/__init__.py`?**
  _High betweenness centrality (0.019) - this node is a cross-community bridge._
- **What connects `edu-auto-grader-backend` to the rest of the system?**
  _1 weakly-connected nodes found - possible missing edges._
- **Should `postgres` be split into smaller, more focused modules?**
  _Cohesion score 0.09523809523809523 - nodes in this community are weakly interconnected._
- **Why does `Base` connect `course.py` to `env.py`?**
  _High betweenness centrality (0.017) - this node is a cross-community bridge._
- **Should `compilerOptions` be split into smaller, more focused modules?**
  _Cohesion score 0.09523809523809523 - nodes in this community are weakly interconnected._
- **Should `DomainError` be split into smaller, more focused modules?**
  _Cohesion score 0.11666666666666667 - nodes in this community are weakly interconnected._
- **Should `schemas/__init__.py` be split into smaller, more focused modules?**
  _Cohesion score 0.050616050616050616 - nodes in this community are weakly interconnected._