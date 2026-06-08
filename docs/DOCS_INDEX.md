# Documentation Index

**Purpose:** Navigation hub for the Hearth documentation suite.
**Intended audience:** All readers — engineers, operators, auditors, buyers.
**Confidence:** Confirmed against repository structure and source code.
**Last updated:** 2026-06-08

## Documents

| Path                                                                          | Summary                                                                                     | Audience                              |
| ----------------------------------------------------------------------------- | ------------------------------------------------------------------------------------------- | ------------------------------------- |
| [`README.md`](../README.md)                                                   | Project overview, quick start, stack, caveats                                               | Everyone                              |
| [`docs/overview.md`](overview.md)                                             | What the product is, main actors, core workflows, glossary                                  | New engineers, buyers, auditors       |
| [`docs/architecture.md`](architecture.md)                                     | System architecture, data flow, state management, boundaries                                | Engineers, architects                 |
| [`docs/repo-map.md`](repo-map.md)                                             | Directory structure, generated code, legacy areas, dead code                                | New engineers, maintainers            |
| [`docs/components.md`](components.md)                                         | Subsystem breakdown: purpose, entry points, key files, risks                                | Engineers                             |
| [`docs/api-reference.md`](api-reference.md)                                   | Public API surfaces: managers, widgets, data models                                         | Engineers, integrators                |
| [`docs/frontend-ui.md`](frontend-ui.md)                                       | GUI routes, widgets, layouts, data dependencies                                             | Frontend engineers                    |
| [`docs/data-model.md`](data-model.md)                                         | Entities, tables, relationships, migrations, validation                                     | Backend engineers, DBAs               |
| [`docs/environment.md`](environment.md)                                       | Environment variables, runtime config, build config, feature flags                          | Operators, devs                       |
| [`docs/development.md`](development.md)                                       | Local setup, build/release, testing commands                                                | Engineers                             |
| [`docs/deployment.md`](deployment.md)                                         | Environments, hosting, packaging, operational runbook                                       | Operators, release engineers          |
| [`docs/security.md`](security.md)                                             | Auth, encryption, secrets, access control, risks                                            | Security reviewers, auditors          |
| [`docs/SECURITY_HARDENING.md`](SECURITY_HARDENING.md)                         | Keyring fallback, license issuance, auto-updater security, release checklist                | Security reviewers, release engineers |
| [`docs/dependencies.md`](dependencies.md)                                     | Third-party packages, SaaS integrations, risk assessment                                    | Architects, security                  |
| [`docs/tech-debt-and-gaps.md`](tech-debt-and-gaps.md)                         | Prioritized technical debt, missing tests, partial features                                 | Maintainers, tech leads               |
| [`docs/onboarding.md`](onboarding.md)                                         | What to read first, what to run first, common traps                                         | New engineers                         |
| [`docs/contributing.md`](contributing.md)                                     | Coding standards, PR expectations, commit guidance                                          | Contributors                          |
| [`docs/assumptions.md`](assumptions.md)                                       | Tracked inference log: claims, evidence, confidence                                         | Auditors, maintainers                 |
| [`docs/BUSINESS_PLAN.md`](BUSINESS_PLAN.md)                                   | Formal business plan: brand, market, product, revenue, GTM, marketing, financials           | Investors, partners, founders         |
| [`docs/brand-strategy-and-positioning.md`](brand-strategy-and-positioning.md) | Brand foundation, voice, values, positioning, competitive matrix                            | Marketing, founders                   |
| [`docs/market-analysis-gtm-strategy.md`](market-analysis-gtm-strategy.md)     | TAM/SAM/SOM, competitive landscape, personas, GTM timeline, growth tactics                  | Growth, founders                      |
| [`docs/business-plan-product-revenue.md`](business-plan-product-revenue.md)   | Product architecture, feature tiers, pricing, revenue projections, unit economics           | Product, founders                     |
| [`docs/marketing_strategy.md`](marketing_strategy.md)                         | Content strategy, SEO, social media, community, paid acquisition, email                     | Marketing, content                    |
| [`docs/PRICING_JUSTIFICATION.md`](PRICING_JUSTIFICATION.md)                   | Pricing rationale for v1.1.0: feature-value mapping, market positioning, ethical boundaries | Product, founders, buyers             |
| [`docs/RELEASE_READINESS.md`](RELEASE_READINESS.md)                           | Verified strengths, decisive calls, blocker remediation index, known issues                 | Release engineers, auditors           |
| [`docs/RELEASE_REPORT_v1.1.0.md`](RELEASE_REPORT_v1.1.0.md)                   | Final build verification, artifact test results, distribution targets, next actions         | Release engineers                     |
| [`docs/RUNBOOK.md`](RUNBOOK.md)                                               | Operator runbook: data locations, build, release, backup/restore, support triage            | Operators, support                    |
| [`docs/testing.md`](testing.md)                                               | Test framework, conventions, coverage posture, known gaps                                   | Engineers, QA                         |

## Scripts & Tools

| Path                                                                      | Summary                                                                                                           | Audience              |
| ------------------------------------------------------------------------- | ----------------------------------------------------------------------------------------------------------------- | --------------------- |
| [`scripts/smoke_test.py`](../scripts/smoke_test.py)                       | Headless validation: imports, dependencies, resources, accessibility, widget instantiation, circular-import probe | CI, release engineers |
| [`scripts/issue_license.py`](../scripts/issue_license.py)                 | Ed25519 license key issuance with permission checks and git-repo warnings                                         | Release engineers     |
| [`scripts/generate_store_assets.py`](../scripts/generate_store_assets.py) | Windows Store PNG/ICO asset generation                                                                            | Release engineers     |

## Suggested Reading Order

### New Engineer

1. `README.md`
2. `docs/onboarding.md`
3. `docs/overview.md`
4. `docs/architecture.md`
5. `docs/repo-map.md`
6. `docs/development.md`

### Operator / Release Engineer

1. `README.md`
2. `docs/deployment.md`
3. `docs/environment.md`
4. `docs/security.md`
5. `docs/SECURITY_HARDENING.md`
6. `docs/RUNBOOK.md`

### Auditor / Buyer

1. `README.md`
2. `docs/overview.md`
3. `docs/security.md`
4. `docs/SECURITY_HARDENING.md`
5. `docs/tech-debt-and-gaps.md`
6. `docs/assumptions.md`

### Founder / Investor

1. `README.md`
2. `docs/BUSINESS_PLAN.md`
3. `docs/PRICING_JUSTIFICATION.md`
4. `docs/overview.md`
5. `docs/security.md`
6. `docs/assumptions.md`

### Maintainer

1. `docs/tech-debt-and-gaps.md`
2. `docs/architecture.md`
3. `docs/components.md`
4. `docs/api-reference.md`
5. `docs/data-model.md`
