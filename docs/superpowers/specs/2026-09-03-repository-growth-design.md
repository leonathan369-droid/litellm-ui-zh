# LiteLLM WebUI Chinese Patch Repository Growth Design

## Purpose

Make `leonathan369-droid/litellm-ui-zh` easy to discover, evaluate, install,
and maintain for two audiences:

- Individual Chinese-speaking LiteLLM users who need a working WebUI quickly.
- Team gateway administrators who need to judge compatibility, safety, and
  supportability before adopting an unofficial UI overlay.

The first audience gets the shortest path through the repository. The second
gets operational detail after the quick-start section. The project remains an
unofficial, browser-side overlay; it must not imply endorsement by BerriAI or
distribute LiteLLM static assets, configuration, credentials, or logs.

## Goals and Measures

The first 30 days balance awareness, successful adoption, and actionable
maintenance feedback.

| Goal | Observable evidence | Initial target |
| --- | --- | --- |
| Discoverability | Repository description and Topics cover Chinese and English LiteLLM UI terms. | 7 Topics, bilingual description. |
| First-use conversion | A new user can understand scope, install, configure `LITELLM_UI_PATH`, and verify the result from README. | Core path visible without scrolling past troubleshooting. |
| Trust | Compatibility scope, non-invasive behavior, rollback, and automated checks are explicit. | A support matrix and passing workflow are visible. |
| Feedback quality | Issues collect LiteLLM version, platform, install mode, and sanitized diagnostics. | 3 issue forms cover translation, installation, and compatibility. |
| Sustainable releases | Changes are documented and verified before a tagged release. | `v0.1.1` documents repository-operability improvements only. |

GitHub Insights traffic, clones, stars, forks, issue quality, and external
references will be reviewed monthly. Stars are a secondary signal, not a
release gate.

## Delivery Scope

### Repository metadata

Set the repository description to:

> LiteLLM WebUI 简体中文补丁 / Simplified Chinese translation overlay with a safe installer and rollback.

Set these Topics:

```text
litellm
litellm-proxy
ai-gateway
chinese
i18n
llmops
local-llm
```

Use the repository URL as the only homepage unless a dedicated documentation
site exists. Do not create a site for this release. Keep Issues enabled; do not
enable Discussions until issue traffic makes a community forum useful.

### README information architecture

Replace the current README order with this reader path:

1. Bilingual one-sentence value statement, scope, and a preview image.
2. Three guarantees: no LiteLLM package modification, no proxy behavior change,
   and recoverable UI directory replacement.
3. A concise quick-start: prerequisites, one installer command, required
   `LITELLM_UI_PATH` configuration, restart, and `check` command.
4. A visible expected-result section describing the Chinese UI and the `中 / EN`
   switch. The preview image must show only synthetic or already-public data.
5. Compatibility matrix with LiteLLM version, operating system, verification
   date, installer outcome, and browser check outcome.
6. Team-admin notes: configuration ownership, upgrade procedure, verification,
   and rollback. Do not publish environment-specific LaunchAgent commands that
   could encourage users to copy private paths or secrets.
7. Troubleshooting table for missing LiteLLM, an existing target directory,
   unpatched routes, and post-upgrade compatibility.
8. Links to support, contribution rules, changelog, license, and upstream
   LiteLLM attribution.

The quick-start must retain an explicit `--python` variant because LiteLLM is
commonly installed into an isolated virtual environment.

### Visual proof

Add one repository-owned screenshot under `docs/assets/` showing the translated
LiteLLM UI with all account data, keys, request payloads, URLs, and usage data
absent. A PNG is sufficient for this release; do not create an animated GIF.
The README renders it with meaningful alt text.

If a safe screenshot cannot be captured from the existing local UI, defer the
image rather than create a mock that falsely represents the software. The rest
of the release remains valid without it.

### Support and contribution boundaries

Add:

- `SUPPORT.md`: support scope, self-check command, redaction rules, expected
  response boundaries, and upstream-routing guidance.
- `CONTRIBUTING.md`: translation conventions, scope limits, required browser
  check for modified strings, and test command.
- `.github/ISSUE_TEMPLATE/translation.yml`: source text, expected Chinese,
  route, LiteLLM version, and screenshot after redaction.
- `.github/ISSUE_TEMPLATE/installation.yml`: operating system, LiteLLM version,
  install command with paths sanitized, exact error, and `check` output.
- `.github/ISSUE_TEMPLATE/compatibility.yml`: upgrade source/target version,
  browser, affected route, reproduction steps, and sanitized diagnostics.
- `.github/ISSUE_TEMPLATE/config.yml`: disables blank issues and points users
  to `SUPPORT.md` for basic setup questions.

Issue forms must warn users never to post API keys, master keys, database URLs,
cookies, full configuration files, or unredacted request logs.

### Verification signal

Add a GitHub Actions workflow triggered by push and pull request. It uses only
the repository Python source, runs:

```zsh
python3 -m unittest discover -s tests -v
python3 -m py_compile scripts/install.py
node --check patches/litellm-zh.js
```

Use currently supported Ubuntu and a minimal read-only permissions declaration.
The workflow must not install LiteLLM, access provider APIs, use repository
secrets, or start a proxy. This keeps verification deterministic and avoids
paid or private external dependencies.

### Release and outreach

After repository changes pass local and Actions validation:

1. Update `CHANGELOG.md` with `0.1.1` dated release notes scoped to
   discoverability and contribution experience.
2. Create GitHub Release `v0.1.1` only after its tag points to the validated
   commit and Actions pass on that commit.
3. Create `docs/community-post-zh.md`, a factual Chinese announcement with a
   problem statement, scope boundaries, screenshot, quick install, verification
   command, compatibility statement, and issue link. It must avoid inflated
   claims, rating requests, paid promotion, or unverified performance claims.
4. Publish manually to one relevant Chinese technical community and one
   LiteLLM-related GitHub surface only where its participation rules permit.
   The repository must not automate posts, comments, stars, follows, or issue
   creation on third-party services.

## Non-Goals

- No changes to `patches/litellm-zh.js` translation behavior in this release.
- No full LiteLLM fork, no vendored WebUI static bundle, and no Docker image.
- No collection of telemetry or user data.
- No paid promotion, follower acquisition, star exchange, or automation of
  social engagement.
- No promise of support for LiteLLM versions that have not been verified.

## Error Handling and Safety

Documentation examples use placeholders and sanitized paths only. The support
forms enforce redaction guidance. GitHub Actions uses no secrets and has no
write permissions. The release instructions retain the existing `check` and
`restore` paths; documentation must not instruct users to edit package files.

## Acceptance Criteria

The repository optimization is accepted when all conditions hold:

1. GitHub shows the specified bilingual description and all seven Topics.
2. README exposes the quick-start, verification, rollback, compatibility, and
   support paths with correct local links and no credential examples.
3. The support and contribution documents state scope and redaction rules.
4. Three issue forms render and collect the required reproduction fields.
5. The Actions workflow passes on the release commit.
6. Local tests, Python compilation, JavaScript syntax validation, and a real
   LiteLLM `1.99.0` installation/check run pass before release.
7. `v0.1.1` has a factual changelog and GitHub Release whose tag resolves to
   the validated commit.
8. A ready-to-publish Chinese community post exists locally; external posting
   remains a manual user action unless explicitly requested later.

## Risks and Responses

| Risk | Response |
| --- | --- |
| LiteLLM changes its static UI layout. | State the precise verified version, maintain the matrix, and request route-specific issues after upgrades. |
| A screenshot leaks local data. | Inspect the captured asset before commit; omit it when no safe capture exists. |
| Users report secrets in issues. | Repeat redaction warnings in every issue form and `SUPPORT.md`; redact or remove content through normal GitHub moderation when needed. |
| Search metadata overpromises compatibility. | Keep the description factual and place version claims only in the verified matrix. |
| Workflow status is misleading. | Limit CI claims to the exact commands it runs; retain manual real-LiteLLM verification before releases. |
