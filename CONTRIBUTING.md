# Contributing

Contributions are welcome for Simplified Chinese wording, installer
documentation, compatibility verification, and reproducible fixes within this
repository's overlay scope.

## Contribution flow

1. Fork the repository and create a focused branch.
2. Keep the change limited to one user-visible improvement or repair.
3. Preserve literal meaning and consistent terminology in Chinese
   translations. Keep useful product names, paths, API field names, and
   technical identifiers in their original form.
4. Do not add LiteLLM proxy behavior, credentials, configuration files, or
   vendored LiteLLM static assets.
5. Test modified translations in a real LiteLLM browser route before opening a
   pull request.
6. Run the repository checks:

```zsh
python3 -m unittest discover -s tests -v
python3 -m py_compile scripts/install.py
node --check patches/litellm-zh.js
```

7. Describe the tested LiteLLM version, browser, route, and any remaining
   untranslated text in the pull request.

Never commit API keys, master keys, database URLs, cookies, full configuration
files, or unredacted logs.
