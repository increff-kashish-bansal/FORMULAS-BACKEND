# Features: Excel-to-Python Formula Converter

## Table of Contents
- [1. File Ingestion](#1-file-ingestion)
- [2. Formula Parsing & Mapping](#2-formula-parsing--mapping)
- [3. Python Script Generation](#3-python-script-generation)
- [4. Code Execution Environment](#4-code-execution-environment)
- [5. Interfaces](#5-interfaces)
- [6. Logging & Error Handling](#6-logging--error-handling)
- [7. Non-Functional Requirements](#7-non-functional-requirements)
- [8. Summary](#8-summary)

---

## 1. File Ingestion

| ID | Feature | Priority | User | Description | Acceptance Criteria | Complexity | Notes |
|----|---------|----------|------|-------------|----------------------|------------|-------|
| F1 | Support `.xlsx`, `.csv`, `.tsv` uploads | Must Have | All | Allow file uploads via CLI or REST endpoint | Upload via CLI/API must succeed and validate filetype | Low | |
| F2 | Multi-sheet parsing | Must Have | All | Read and parse all worksheets in uploaded files | All worksheets are processed with formula detection | Medium | Uses `formulas` library |
| F3 | File size limit enforcement | Must Have | All | Process files <10MB within 10s | Files >10MB are rejected with error log | Low | |

---

## 2. Formula Parsing & Mapping

| ID | Feature | Priority | User | Description | Acceptance Criteria | Complexity | Notes |
|----|---------|----------|------|-------------|----------------------|------------|-------|
| F4 | Formula extraction using `formulas` v1.2.2 | Must Have | All | Extract all cell formulas from workbook | At least 90% formula coverage on test sheets | High | |
| F5 | Placeholder for unsupported formulas | Must Have | All | Unsupported formulas replaced with no-op or dummy value | Log warning and include comment in code | Medium | |
| F6 | Variable naming from Named Ranges/Headers | Must Have | All | Auto-name variables from headers or labels | Naming hierarchy: Named Range > Header > `cell_A1` | Medium | |
| F7 | Cross-sheet reference support | Should Have | All | Allow formulas that reference other sheets | Reference maintained and resolved in output script | High | |

---

## 3. Python Script Generation

| ID | Feature | Priority | User | Description | Acceptance Criteria | Complexity | Notes |
|----|---------|----------|------|-------------|----------------------|------------|-------|
| F8 | Generate `.py` script with formulas | Must Have | All | Convert formulas to clean Python code | Python script reflects Excel logic correctly | Medium | |
| F9 | Consistent variable naming scheme | Should Have | All | Ensure clarity and reuse of variable names | Output uses meaningful identifiers consistently | Low | |
| F10 | Handle ambiguities in headers | Must Have | All | Flatten merged or empty headers with suffixes | Logs ambiguous headers and adds suffix (e.g., `_1`) | Medium | |
| F11 | Include function wrapper and main execution block | Must Have | All | Scripts have reusable functions + main block | Output includes main() and optional print | Low | |

---

## 4. Code Execution Environment

| ID | Feature | Priority | User | Description | Acceptance Criteria | Complexity | Notes |
|----|---------|----------|------|-------------|----------------------|------------|-------|
| F12 | Execute Python script within app | Could Have | All | Optional execution of output script | Output returned in JSON (API) or stdout (CLI) | High | |
| F13 | Enforce sandboxed limits (CPU, RAM, no internet) | Must Have | All | Restrict runtime via Docker or subprocess | Cannot exceed 30s CPU, 128MB RAM, no net | High | Use AppArmor/SECCOMP or subprocess limits |

---

## 5. Interfaces

| ID | Feature | Priority | User | Description | Acceptance Criteria | Complexity | Notes |
|----|---------|----------|------|-------------|----------------------|------------|-------|
| F14 | CLI interface for file upload and output | Must Have | All | Accept path to file and print output or log | `converter file.xlsx --run` prints result | Low | |
| F15 | REST API endpoint to accept file POST | Must Have | All | Accept files via FastAPI | Returns JSON output and log URL | Medium | |
| F16 | Downloadable `.py` file as part of response | Must Have | All | Python file downloadable via API or CLI | `result.py` available as link or saved file | Low | |

---

## 6. Logging & Error Handling

| ID | Feature | Priority | User | Description | Acceptance Criteria | Complexity | Notes |
|----|---------|----------|------|-------------|----------------------|------------|-------|
| F17 | Warning and error log generation | Must Have | All | Log skipped formulas, naming issues, etc. | `log.txt` contains human-readable warnings | Low | |
| F18 | JSON field `warnings[]` in API | Must Have | All | API response includes structured warnings | Warnings shown alongside result | Medium | |
| F19 | CLI writes errors to `stderr` | Must Have | All | CLI logs issues to screen and `log.txt` | Errors shown and saved | Low | |

---

## 7. Non-Functional Requirements

| ID | Feature | Priority | User | Description | Acceptance Criteria | Complexity | Notes |
|----|---------|----------|------|-------------|----------------------|------------|-------|
| F20 | <10s processing for files <10MB | Must Have | All | Performance guardrail | Process completes within 10 seconds | Medium | |
| F21 | Async workers support 10 uploads/min | Must Have | All | Handle concurrency via FastAPI workers | 95% of requests succeed under load | Medium | |
| F22 | Modular and maintainable codebase | Must Have | Dev | Clear, testable Python modules | Code passes linter and 80%+ test coverage | Medium | |
| F23 | Deployable on Azure | Must Have | DevOps | Azure App Service or VM deployment ready | Deployment works on Azure infra | Medium | |

---

## 8. Summary

### Feature Count by Priority

| Priority    | Count |
|-------------|-------|
| Must Have   | 17    |
| Should Have | 2     |
| Could Have  | 1     |
| Won’t Have  | 4 (documented only) |

### Feature Count by Category

| Category                  | Count |
|---------------------------|-------|
| File Ingestion            | 3     |
| Formula Parsing & Mapping| 4     |
| Python Script Generation  | 4     |
| Code Execution            | 2     |
| Interfaces                | 3     |
| Logging & Error Handling  | 3     |
| Non-Functional            | 4     |

---

