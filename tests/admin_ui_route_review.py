from __future__ import annotations

import json
import os
from pathlib import Path

from playwright.sync_api import sync_playwright


BASE_URL = os.environ.get("LITELLM_TEST_BASE_URL", "http://127.0.0.1:4000")
USERNAME = os.environ["UI_USERNAME"]
PASSWORD = os.environ["UI_PASSWORD"]
OUTPUT = Path(os.environ["RUNNER_TEMP"]) / "admin-routes"

ROUTES = [
    ("virtual-keys", "api-keys"),
    ("models", "models-and-endpoints"),
    ("playground", "playground"),
    ("usage", "usage"),
    ("agents", "agents"),
    ("skills", "skills"),
    ("mcp-servers", "mcp-servers"),
    ("guardrails", "guardrails"),
    ("policies", "policies"),
    ("teams", "teams"),
    ("users", "users"),
    ("budgets", "budgets"),
    ("logs", "logs"),
    ("router-settings", "router-settings"),
    ("admin-panel", "admin-panel"),
]


def main() -> None:
    OUTPUT.mkdir(parents=True, exist_ok=True)
    results: list[dict[str, object]] = []
    failures: list[dict[str, object]] = []

    with sync_playwright() as playwright:
        browser = playwright.chromium.launch()
        page = browser.new_page(viewport={"width": 1440, "height": 1000})

        page.goto(f"{BASE_URL}/ui/login/", wait_until="domcontentloaded", timeout=45000)
        page.wait_for_selector("#litellm-zh-toggle", timeout=30000)
        page.wait_for_selector('input[placeholder="输入用户名"]', timeout=30000)
        assert page.locator('input[placeholder="输入密码"]').count() == 1
        page.screenshot(path=str(OUTPUT / "00-login-zh.png"), full_page=True)

        page.locator('input[placeholder="输入用户名"]').fill(USERNAME)
        page.locator('input[placeholder="输入密码"]').fill(PASSWORD)
        page.locator('button[type="submit"]').click()
        page.wait_for_url(lambda url: "/ui/login" not in url, timeout=45000)
        page.wait_for_selector("#litellm-zh-toggle", timeout=30000)

        for index, (name, segment) in enumerate(ROUTES, start=1):
            expected = f"{BASE_URL}/ui/{segment}/"
            record: dict[str, object] = {
                "name": name,
                "segment": segment,
                "expected": expected,
            }
            try:
                page.goto(expected, wait_until="domcontentloaded", timeout=45000)
                page.wait_for_selector("#litellm-zh-toggle", timeout=30000)
                page.wait_for_timeout(1200)
                current = page.url
                lang = page.locator("html").get_attribute("lang")
                body = page.locator("body").inner_text(timeout=10000)
                record.update(
                    {
                        "url": current,
                        "lang": lang,
                        "body_preview": body[:1000],
                        "status": "checked",
                    }
                )
                if "/ui/login" in current:
                    raise AssertionError("route redirected back to login")
                if lang != "zh-CN":
                    raise AssertionError(f"unexpected document language: {lang}")
                page.screenshot(
                    path=str(OUTPUT / f"{index:02d}-{name}.png"),
                    full_page=True,
                )
            except Exception as error:
                record["status"] = "failed"
                record["error"] = str(error)
                failures.append(record)
                try:
                    page.screenshot(
                        path=str(OUTPUT / f"{index:02d}-{name}-FAILED.png"),
                        full_page=True,
                    )
                except Exception:
                    pass
            results.append(record)

        browser.close()

    (OUTPUT / "route-results.json").write_text(
        json.dumps(results, ensure_ascii=False, indent=2) + "\n",
        encoding="utf-8",
    )
    print(json.dumps(results, ensure_ascii=False, indent=2))
    if failures:
        raise SystemExit(f"{len(failures)} authenticated UI routes failed")


if __name__ == "__main__":
    main()
