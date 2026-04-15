# Stable API Coverage Dashboard

Generated At (UTC): 2026-04-10 11:06:24
Manual Test Source: tests/test_data/HRMIS_API-Test cases .xlsx
Stability Config: docs/coverage/stable_modules.json
Verified Mapping: docs/coverage/verified_case_mapping.json
JUnit Source: reports/20260410_142312/junit.xml

## Go-Signal Summary
- Modules with go signal: 2/5
- Manual cases (go-signal modules): 21
- Automated cases mapped to manual IDs: 21
- Spec-flow mapped cases: 2
- Overlap (automated + spec): 2
- Net covered (de-duplicated): 21
- Pending (go-signal modules): 0
- Passed test cases (go-signal modules): 11
- Failed test cases (go-signal modules): 16
- Coverage (go-signal modules): 100.0%
- Schema files across configured modules: 8
- Contract/spec paths inferred: 10

## Module Breakdown
| Module | Go Signal | Manual | Automated | Spec Flow | Overlap | Net Covered | Pending | Passed | Failed | Coverage % | Test Files | Schema Files |
|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|
| login | Yes | 10 | 10 | 1 | 1 | 10 | 0 | 8 | 7 | 100.0 | 1 | 1 |
| salary_management | Yes | 11 | 11 | 1 | 1 | 11 | 0 | 3 | 9 | 100.0 | 1 | 1 |
| announcements | No | 19 | 19 | 2 | 2 | 19 | 0 | 12 | 9 | 100.0 | 6 | 1 |
| dashboard | No | 14 | 1 | 1 | 1 | 1 | 13 | 1 | 0 | 7.14 | 0 | 1 |
| onboarding | No | 71 | 34 | 0 | 0 | 34 | 37 | 24 | 28 | 47.89 | 7 | 4 |

## Evidence Audit
| Module | Automated Mapped | Auto Evidence Present | Auto Evidence Missing | Spec Mapped | Spec Evidence Present | Spec Evidence Missing |
|---|---:|---:|---:|---:|---:|---:|
| login | 10 | 0 | 10 | 1 | 0 | 1 |
| salary_management | 11 | 0 | 11 | 1 | 0 | 1 |
| announcements | 19 | 19 | 0 | 2 | 2 | 0 |
| dashboard | 1 | 1 | 0 | 1 | 1 | 0 |
| onboarding | 34 | 34 | 0 | 0 | 0 | 0 |

## Notes
- Coverage here is ID-mapped against manual Excel case IDs.
- Automated coverage uses case IDs detected in tests and reviewed IDs from verified mapping.
- Spec-flow coverage uses reviewed IDs from verified mapping only (no endpoint-based auto inference).
- Pass/Fail counts are derived from the latest JUnit report; xfail cases are counted as failed.
- Strict verified-spec mode: disabled.
- Net coverage de-duplicates automated/spec overlap to avoid double counting.
- Only go-signal modules contribute to the top summary coverage.
- Update docs/coverage/stable_modules.json when devs mark a module stable.
