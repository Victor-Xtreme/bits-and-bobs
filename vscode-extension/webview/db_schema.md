# RepoSense — database schema reference

This document describes every model stored after a completed analysis job. An AI agent reading this should be able to understand what data exists, how models relate to each other, and what fields to use for any query or traversal.

---

## Top-level envelope: `ApiResponse`

Every analysis job produces one `ApiResponse` record.

| field | type | notes |
|---|---|---|
| `type` | `PayloadType` | `request` · `result` · `error` |
| `job_id` | `str` | unique identifier for this analysis run |
| `progress` | `ProgressStep[]` | ordered list of pipeline stages and their completion status |
| `payload` | `AnalysisResult \| AnalysisError \| null` | null while running, populated on completion or failure |

---

## Progress tracking: `ProgressStep`

One entry per pipeline stage (parse, architecture, review, docs, security, score).

| field | type | notes |
|---|---|---|
| `name` | `str` | human-readable stage name |
| `status` | `StepStatus` | `done` · `active` · `pending` |
| `files_processed` | `int?` | only present during parse stage |
| `files_total` | `int?` | only present during parse stage |
| `current_file` | `str?` | path of file currently being processed |

---

## Parsed codebase: `ParsedCodebase`

Raw structural representation of the scanned repository. This is the source of truth for all code-level detail.

### `ParsedCodebase`

| field | type | notes |
|---|---|---|
| `files` | `ParsedFile[]` | one entry per source file |
| `import_graph` | `dict[str, str[]]` | maps file path → list of file paths it imports. **Keys are file paths, same as `ParsedFile.path`.** |

### `ParsedFile`

| field | type | notes |
|---|---|---|
| `path` | `str` | relative file path — **primary key** for this file across all models |
| `language` | `str` | e.g. `"python"`, `"typescript"` |
| `imports` | `str[]` | raw import strings as they appear in source |
| `classes` | `ParsedClass[]` | flat list — includes nested classes (use `parent_id` to reconstruct hierarchy) |
| `functions` | `ParsedFunction[]` | flat list — includes methods (use `parent_id` to reconstruct hierarchy) |

### `ParsedClass`

| field | type | notes |
|---|---|---|
| `id` | `str` | pattern: `file_path::ClassName` for top-level, `file_path::ParentClass::NestedClass` for nested |
| `name` | `str` | class name |
| `parent_id` | `str?` | `null` for top-level; references enclosing class `id` for nested |
| `line_start` | `int` | |
| `line_end` | `int` | |
| `docstring` | `str?` | |
| `bases` | `str[]` | names of base classes |

### `ParsedFunction`

| field | type | notes |
|---|---|---|
| `id` | `str` | pattern: `file_path::function_name` for top-level, `file_path::ClassName::method_name` for methods |
| `name` | `str` | function or method name |
| `parent_id` | `str?` | `null` for top-level; references enclosing class `id` for methods |
| `line_start` | `int` | |
| `line_end` | `int` | |
| `docstring` | `str?` | |
| `params` | `str[]` | parameter names |
| `returns` | `str?` | return type annotation if present |

---

## Architecture graph: `ArchitectureGraph`

High-level module dependency graph produced by the architecture agent. This is what the dependency tree webview consumes.

### `GraphNode`

| field | type | notes |
|---|---|---|
| `id` | `str` | **must match a `ParsedFile.path`** to allow enrichment lookups |
| `label` | `str` | display name shown in the UI |
| `type` | `NodeType` | `entry` · `service` · `util` · `config` · `test` |
| `description` | `str` | one-sentence summary shown in tooltip or sidebar |

`NodeType` semantics:

| value | meaning |
|---|---|
| `entry` | application entrypoint — expected to have many dependents, few dependencies |
| `service` | core business logic |
| `util` | shared helper — expected to have few dependents but be imported widely |
| `config` | configuration module |
| `test` | test file — should have no dependents |

### `GraphEdge`

| field | type | notes |
|---|---|---|
| `source` | `str` | `GraphNode.id` of the module that **has** the dependency |
| `target` | `str` | `GraphNode.id` of the module that **is depended on** |
| `relationship` | `EdgeRelationship` | `imports` · `extends` · `calls` |

**Direction convention:** `source → target` means *source depends on target*. Target is upstream.

`EdgeRelationship` semantics:

| value | meaning |
|---|---|
| `imports` | source file imports target at module level |
| `extends` | source class inherits from a class defined in target |
| `calls` | source calls a function or method defined in target at runtime |

---

## Code review: `CodeReview`

### `CodeReviewFinding`

| field | type | notes |
|---|---|---|
| `file` | `str` | matches `ParsedFile.path` |
| `line` | `int` | line number of the issue |
| `severity` | `Severity` | `LOW` · `MEDIUM` · `HIGH` · `CRITICAL` |
| `issue` | `str` | description of the problem |
| `suggestion` | `str` | recommended fix |

---

## Documentation: `Documentation`

### `DocEntry`

| field | type | notes |
|---|---|---|
| `function_name` | `str` | matches `ParsedFunction.id` |
| `description` | `str` | |
| `params` | `DocParam[]` | |
| `returns` | `str` | |
| `example` | `str` | usage example |

### `DocParam`

| field | type | notes |
|---|---|---|
| `name` | `str` | |
| `type` | `str` | |
| `description` | `str` | |

### `TestEntry`

| field | type | notes |
|---|---|---|
| `function_name` | `str` | matches `ParsedFunction.id` |
| `test_cases` | `TestCase[]` | |

### `TestCase`

| field | type | notes |
|---|---|---|
| `description` | `str` | |
| `input` | `str` | |
| `expected` | `str` | |

---

## Security report: `SecurityReport`

### `SecurityIssue`

| field | type | notes |
|---|---|---|
| `issue` | `str` | |
| `severity` | `Severity` | `LOW` · `MEDIUM` · `HIGH` · `CRITICAL` |
| `file` | `str` | matches `ParsedFile.path` |
| `fix` | `str` | recommended remediation |

### `ModernizationItem`

| field | type | notes |
|---|---|---|
| `pattern` | `str` | outdated pattern detected |
| `suggestion` | `str` | modern equivalent |
| `effort` | `Effort` | `LOW` · `MEDIUM` · `HIGH` |

---

## Health score: `HealthScore`

| field | type | notes |
|---|---|---|
| `score` | `int` | 0–100 overall score |
| `grade` | `Grade` | `A` · `B` · `C` · `D` · `F` |
| `breakdown` | `ScoreBreakdown` | four sub-scores |
| `summary` | `str` | narrative summary |
| `top_priorities` | `str[]` | ordered list of highest-impact actions |

### `ScoreBreakdown`

| field | type | notes |
|---|---|---|
| `quality` | `int` | 0–100 |
| `security` | `int` | 0–100 |
| `documentation` | `int` | 0–100 |
| `architecture` | `int` | 0–100 |

---

## Error handling: `AnalysisError`

| field | type | notes |
|---|---|---|
| `code` | `ErrorCode` | `PARSE_FAILED` · `AGENT_TIMEOUT` · `AGENT_INVALID_JSON` · `WATSONX_UNAVAILABLE` · `UNKNOWN` |
| `message` | `str` | human-readable error detail |
| `stage` | `str` | pipeline stage where the failure occurred |

---

## Cross-model join keys

| from | to | join on |
|---|---|---|
| `GraphNode.id` | `ParsedFile.path` | file path string — exact match |
| `GraphNode.id` | `ParsedCodebase.import_graph` key | file path string — exact match |
| `CodeReviewFinding.file` | `ParsedFile.path` | file path string |
| `SecurityIssue.file` | `ParsedFile.path` | file path string |
| `DocEntry.function_name` | `ParsedFunction.id` | function id string |
| `TestEntry.function_name` | `ParsedFunction.id` | function id string |
| `ParsedFunction.parent_id` | `ParsedClass.id` | class id string (for methods) |
| `ParsedClass.parent_id` | `ParsedClass.id` | class id string (for nested classes) |
