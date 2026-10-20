# Changelog

## Unreleased

- Translate `Open` as the action “打开”, keeping “待处理” only in visible table headers (open-item counts) through a header context rule; the previous translation was wrong in the command palette, the Entra description, and screen-reader action column headers.
- Add 251 entries (6,100 to 6,351) for LiteLLM 1.106.0's new Home page, its command palette and account menu, and the redesigned Lens onboarding, tabs, signals, and demo-data finding, trace, and investigation views; extend the data-protection regression case with the new generic words.

- Expand the LiteLLM 1.105.1 dictionary from 739 to 6,100 entries, covering Lens, management dialogs, permissions, routing, cost views, MCP, agents, and shared form text.
- Add regression cases for audited labels, exact English restoration, and dictionary collisions with protected data/code/input values.

- Validate LiteLLM 1.105.1 on isolated Ubuntu with PostgreSQL-backed login and 15 core admin routes; update compatibility workflows to the exact release and Prisma 0.15.0.
- Wait for the initial React loading shell to be replaced before translating, preventing the reproduced hydration error #418.
- Restore a removed language toggle without resetting the selected language.
- Preserve protected data and ignored regions when translatable attributes change dynamically.
- Add regression tests, per-route language switching and browser-error checks, and translate newly observed 1.105.1 interface text.
- Verify the same overlay in an Ubuntu production deployment, including 15 admin routes and a custom reports plugin iframe; macOS and exhaustive manual workflows remain unverified.

## 0.2.0 - 2026-09-20

- Reworked translation matching to avoid generic substring replacement of user-visible data.
- Added WeakMap-backed text and attribute state for React-driven updates and reliable language restoration.
- Protected table data cells from exact-match collisions while retaining translation for explicit controls.
- Added ignored DOM zones for code, preformatted, editable, and explicitly excluded content.
- Split locale data, runtime source, and reproducible distribution build.
- Added safe `upgrade` and `diagnose` commands plus Manifest v2, content-hash cache busting, source fingerprints, backups, and rollback protection.
- Expanded tests for false-positive translation, dynamic text and attributes, installer integrity, upgrade, rollback, build reproducibility, and compatibility states.
- Expanded verification CI to Ubuntu and macOS on Python 3.11 and 3.13.
- Added upstream stable-release monitoring, untranslated HTML candidate collection, and an allowlist-gated static-string compatibility check.
- Added real-package LiteLLM v1.101.0 compatibility CI on Ubuntu and macOS, including process startup, served UI verification, and Linux Chromium smoke testing of dynamic translation, language restoration, and table-data protection.
- Added PostgreSQL-backed authenticated Admin UI review on Linux with 15 core routes, screenshots, and regression checks for translated placeholders.
- Fixed audited login, search, and Playground placeholder gaps found during manual screenshot review.
- Changed upstream release discovery to compare against the highest compatibility-reviewed version, preventing duplicate alerts for already reviewed releases.
- Updated the Simplified Chinese dictionary for LiteLLM v1.101.0 Auto-Router, Agent/Skill Hub, Guardrail detail, login, and related UI changes.
- Distinguished `VERIFIED` from `AUTOMATED_VERIFIED`.
- Pinned first-party GitHub Actions to immutable commit SHAs.
- Added architecture, maintenance, and security documentation.

## 0.1.2 - 2026-09-18

- Verified the overlay and safe installer with LiteLLM 1.101.0 on macOS.
- Confirmed the launch-agent-managed proxy and local launchpad health after upgrade.

## 0.1.1 - 2026-09-03

- Added repository verification with GitHub Actions.
- Added privacy-aware support, contribution, and issue-reporting guidance.
- Improved Chinese-first onboarding, compatibility, rollback, and team-admin documentation.
- Added repository discoverability metadata and a manual Chinese announcement draft.

## 0.1.0 - 2026-09-03

- Initial Simplified Chinese translation overlay for the LiteLLM WebUI.
- Safe installer that creates a standalone custom UI directory.
- Verification and restore commands with recoverable backups.
