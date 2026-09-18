> Historical document from the v0.1.1 repository-growth work. Some commands and constraints are superseded by v0.2.0; use `docs/maintenance.md` for current procedures.

# Repository Growth Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Make the LiteLLM Chinese WebUI patch discoverable, safe to evaluate, straightforward to install, and maintainable through structured feedback and visible verification.

**Architecture:** Keep product behavior unchanged. Add repository documentation, privacy-aware issue forms, deterministic CI, and factual GitHub metadata. Release only after local checks, real LiteLLM validation, and remote CI pass.

**Tech Stack:** Markdown, GitHub Issue Forms, GitHub Actions, Python `unittest`, Node.js syntax checking, GitHub CLI.

**Spec:** `docs/superpowers/specs/2026-09-03-repository-growth-design.md`

## Global Constraints

- Do not modify `patches/litellm-zh.js` translation behavior.
- Do not distribute LiteLLM source, static UI bundles, configuration, credentials, logs, or provider assets.
- State compatibility only for LiteLLM `1.99.0` on macOS, verified 2026-09-03.
- Never put API keys, master keys, database URLs, cookies, full configs, or unredacted logs in repository files, screenshots, issues, workflows, or releases.
- CI uses no secrets, write permissions, provider APIs, LiteLLM installation, or proxy process.
- Do not automate external promotion or third-party engagement.
- Release `v0.1.1` only after its target commit has a green workflow.

---

## File Structure

- `.github/workflows/verify.yml`: repository-only CI.
- `.github/ISSUE_TEMPLATE/*.yml`: structured issue intake.
- `SUPPORT.md`: support scope, self-check, redaction, upstream routing.
- `CONTRIBUTING.md`: translation and verification rules.
- `README.md`: first-use and administrator documentation.
- `docs/assets/litellm-ui-zh-preview.png`: sanitized real UI preview, if available.
- `docs/community-post-zh.md`: manual announcement draft.
- `CHANGELOG.md`: `0.1.1` release notes.

### Task 1: Add Continuous Verification

**Files:** Create `.github/workflows/verify.yml`.

**Produces:** `Verify` on push and pull request with `contents: read` only.

- [ ] **Step 1: Confirm the file is absent**

Run `test -f .github/workflows/verify.yml`; expected exit status `1`.

- [ ] **Step 2: Create the workflow**

Use `actions/checkout@v4`, `actions/setup-python@v5` with Python `3.11`,
`actions/setup-node@v4` with Node `20`, then run exactly:
`python3 -m unittest discover -s tests -v`,
`python3 -m py_compile scripts/install.py`, and
`node --check patches/litellm-zh.js`.

- [ ] **Step 3: Verify locally and commit**

Run the three commands above; expect exit status `0`. Then run
`git add .github/workflows/verify.yml && git commit -m "ci: verify patch installer and overlay"`.

### Task 2: Add Support and Issue Intake

**Files:** Create `SUPPORT.md`, `CONTRIBUTING.md`, `.github/ISSUE_TEMPLATE/config.yml`, `translation.yml`, `installation.yml`, and `compatibility.yml`.

**Produces:** Three issue forms for redacted, reproducible reports.

- [ ] **Step 1: Confirm the translation form is absent**

Run `test -f .github/ISSUE_TEMPLATE/translation.yml`; expected exit status `1`.

- [ ] **Step 2: Write support documents**

`SUPPORT.md` includes the exact `check` command, scope, upstream routing, no
response-time promise, and redaction of keys, credentialed URLs, cookies,
database URLs, configs, and logs. `CONTRIBUTING.md` includes fork/branch/PR
flow, literal Chinese translations, no product-logic changes, real-browser
checking, and the exact test command.

- [ ] **Step 3: Write issue forms**

Each starts with a warning not to post secrets or unredacted logs. Required
fields are: translation (source English, expected Chinese, route, LiteLLM
version, redacted screenshot); installation (OS, version, sanitized command,
exact error, sanitized check output); compatibility (previous and target
versions, browser, route, reproduction, sanitized diagnostics). `config.yml`
sets `blank_issues_enabled: false` and links to `SUPPORT.md`.

- [ ] **Step 4: Parse and inspect, then commit**

Run `ruby -e 'require "yaml"; Dir[".github/ISSUE_TEMPLATE/*.yml"].each { |p| YAML.load_file(p); puts p }'` and
`rg -n -i 'api key|master key|database|cookie|redact|脱敏|密钥' SUPPORT.md CONTRIBUTING.md .github/ISSUE_TEMPLATE`.
Expect YAML success and redaction guidance in all forms. Commit with
`git add SUPPORT.md CONTRIBUTING.md .github/ISSUE_TEMPLATE && git commit -m "docs: add support and issue intake guidance"`.

### Task 3: Improve Onboarding and Evidence

**Files:** Modify `README.md` and `CHANGELOG.md`; create `docs/community-post-zh.md`; optionally create `docs/assets/litellm-ui-zh-preview.png`.

**Produces:** Personal-user-first README, team-admin notes, announcement draft, and `0.1.1` changelog.

- [ ] **Step 1: Confirm documentation gaps**

Run `rg -n 'Quick start|快速安装|Support|支持|Compatibility matrix|兼容性矩阵' README.md`; expect the required headings are not all present.

- [ ] **Step 2: Capture safe evidence**

Capture a real local LiteLLM screen only if it contains no keys, private data,
request contents, credentialed URLs, usage data, or logs. Inspect it and save
as `docs/assets/litellm-ui-zh-preview.png`. If no safe capture exists, omit it
and state that fact in README; do not create a mock.

- [ ] **Step 3: Restructure README**

Use this order: bilingual value statement; three safety guarantees; quick-start;
expected result; alternate `--python`; verify/rollback; compatibility matrix;
team-admin upgrade notes; troubleshooting; support and contribution links.
Include the exact verified row: `LiteLLM 1.99.0 | macOS | 2026-09-03 | installer + check passed | browser UI manually checked`.
Do not claim Linux or Windows verification.

- [ ] **Step 4: Add post and changelog**

The Chinese post contains problem, scope, install/check commands, tested
version, issue link, and a redacted feedback invitation. The `0.1.1` section
lists README, support forms, CI, and metadata improvements only.

- [ ] **Step 5: Verify and commit**

Run `test -f SUPPORT.md && test -f CONTRIBUTING.md && test -f docs/community-post-zh.md`,
link checks with `rg`, and `file docs/assets/litellm-ui-zh-preview.png` when the
asset exists. Inspect the image before `git add`; commit with
`docs: improve LiteLLM patch onboarding`.

### Task 4: Configure Discovery and Release

**Files:** GitHub repository metadata and release through `gh`.

**Produces:** Bilingual description, seven Topics, green CI, and `v0.1.1`.

- [ ] **Step 1: Push and observe CI**

Run `git push origin main` and `gh run list --workflow Verify --branch main --limit 1`.

- [ ] **Step 2: Set metadata**

Run `gh repo edit leonathan369-droid/litellm-ui-zh --description 'LiteLLM WebUI 简体中文补丁 / Simplified Chinese translation overlay with a safe installer and rollback.' --add-topic litellm --add-topic litellm-proxy --add-topic ai-gateway --add-topic chinese --add-topic i18n --add-topic llmops --add-topic local-llm`.
Do not change visibility, remotes, collaborators, branch protection, or other administration.

- [ ] **Step 3: Read back metadata and CI**

Read metadata with `gh repo view ... --json description,repositoryTopics,url`.
Run `gh run watch --exit-status`; expect the newest `Verify` run to pass.

- [ ] **Step 4: Release and verify**

After CI passes, run `gh release create v0.1.1 --target main --title 'v0.1.1 - 项目可发现性与维护体验' --notes-file CHANGELOG.md`.
Then run `git ls-remote --tags origin refs/tags/v0.1.1`,
`gh release view v0.1.1 --repo leonathan369-droid/litellm-ui-zh --json url,isDraft,isPrerelease,tagName,targetCommitish`,
and `git status --short --branch`. Expect a published release targeting
`main` and a clean worktree.

## Plan Self-review

- Spec coverage: Task 1 covers CI; Task 2 covers support and feedback; Task 3
  covers onboarding, operations, screenshot safety, changelog, and manual post;
  Task 4 covers metadata, remote checks, and release.
- Placeholder scan: no implementation placeholders; the screenshot has an
  explicit safety-gated defer path.
- Interface consistency: Task 2 creates files linked by Task 3; all tasks use
  existing installer/test commands; Task 4 consumes committed artifacts only.
