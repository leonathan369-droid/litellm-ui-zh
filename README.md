# LiteLLM WebUI Simplified Chinese Patch

An independent Simplified Chinese browser-side translation overlay for the
[LiteLLM](https://github.com/BerriAI/litellm) Proxy WebUI. It translates the
dashboard after it renders and includes an `中 / EN` switch in the lower-right
corner. It does not modify LiteLLM's Python package, proxy API behavior,
database, keys, or model configuration.

> [!WARNING]
> This is an unofficial community patch. LiteLLM WebUI markup changes often;
> update LiteLLM deliberately and run `check` after each upgrade.

## Compatibility

The first release is verified against LiteLLM `1.99.0` on macOS. It requires
the installed LiteLLM environment to include the packaged static UI at:

```text
litellm/proxy/_experimental/out
```

The installer will locate that directory automatically when run with the same
Python environment as LiteLLM, or it accepts `--source` for explicit control.

## Install

Clone this repository, then create a separate custom UI directory. Pick a new
directory that does not exist yet:

```zsh
python3 scripts/install.py install \
  --target "$HOME/.config/litellm/ui-zh"
```

If LiteLLM is installed in a different virtual environment, point the script
at that Python executable:

```zsh
python3 scripts/install.py install \
  --python /path/to/litellm-venv/bin/python \
  --target "$HOME/.config/litellm/ui-zh"
```

Set `LITELLM_UI_PATH` to the created directory in the process environment that
starts LiteLLM, then restart LiteLLM. Platform notes are in
[docs/macos.md](docs/macos.md).

## Verify and restore

```zsh
python3 scripts/install.py check --target "$HOME/.config/litellm/ui-zh"
python3 scripts/install.py restore --target "$HOME/.config/litellm/ui-zh"
```

`check` confirms that every HTML route includes the overlay and that the script
matches its install manifest. `restore` replaces the target with a fresh copy
of the upstream packaged UI and keeps the prior patched directory as a
timestamped recovery backup. Neither command edits LiteLLM's installed package
or service configuration.

## Development

```zsh
python3 -m unittest discover -s tests -v
```

Translation strings live in [patches/litellm-zh.js](patches/litellm-zh.js).
Keep translations literal, preserve product names where useful, and test the
affected route in a real browser before releasing.

## Scope and attribution

This repository distributes only the translation overlay and installer.
LiteLLM itself, its static WebUI bundle, provider logos, credentials, and
configuration files are not included. See [NOTICE.md](NOTICE.md).
