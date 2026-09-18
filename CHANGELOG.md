# Changelog

## 0.2.0 - Unreleased

- Reworked translation matching to avoid generic substring replacement of user-visible data.
- Added WeakMap-backed text and attribute state for React-driven updates and reliable language restoration.
- Added ignored DOM zones for code, preformatted, editable, and explicitly excluded content.
- Split locale data, runtime source, and reproducible distribution build.
- Added safe `upgrade` and `diagnose` commands plus Manifest v2, content-hash cache busting, source fingerprints, backups, and rollback protection.
- Expanded tests for false-positive translation, dynamic text and attributes, installer integrity, upgrade, rollback, build reproducibility, and compatibility states.
- Expanded verification CI to Ubuntu and macOS on Python 3.11 and 3.13.
- Added upstream stable-release monitoring and untranslated HTML candidate collection.
- Added real-package LiteLLM v1.101.0 compatibility CI on Ubuntu and macOS, including process startup, served UI verification, and Linux Chromium smoke testing.
- Distinguished `VERIFIED` from `AUTOMATED_VERIFIED`.
- Pinned first-party GitHub Actions to immutable commit SHAs.
- Added architecture, maintenance, and security documentation.

## 0.1.1 - 2026-09-03

- Added repository verification with GitHub Actions.
- Added privacy-aware support, contribution, and issue-reporting guidance.
- Improved Chinese-first onboarding, compatibility, rollback, and team-admin documentation.
- Added repository discoverability metadata and a manual Chinese announcement draft.

## 0.1.0 - 2026-09-03

- Initial Simplified Chinese translation overlay for the LiteLLM WebUI.
- Safe installer that creates a standalone custom UI directory.
- Verification and restore commands with recoverable backups.
