# Support

This repository supports the Simplified Chinese WebUI overlay, its installer,
and verification of the custom UI directory. It does not support LiteLLM core
proxy behavior, provider APIs, databases, authentication, billing, or upstream
WebUI defects unrelated to this overlay.

## Before opening an issue

Run the integrity check against your custom UI directory:

```zsh
python3 scripts/install.py check --target "$HOME/.config/litellm/ui-zh"
```

Use the issue forms for missing translations, installation errors, or
compatibility reports after a LiteLLM upgrade. A complete report includes the
LiteLLM version, operating system, affected route, and sanitized diagnostics.

## Keep reports safe

Never include API keys, master keys, passwords, database URLs, cookies, access
tokens, full configuration files, request or response bodies, or unredacted
logs. Replace private paths, hostnames, email addresses, and identifiers with
placeholders before posting.

## Where to report other problems

For LiteLLM Proxy API, routing, provider, database, or core WebUI issues, use
the upstream project: <https://github.com/BerriAI/litellm/issues>.

This is a community-maintained project. There is no guaranteed response time
or service-level agreement.
