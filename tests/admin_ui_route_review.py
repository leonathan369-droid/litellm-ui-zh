from __future__ import annotations

import json
import os
from pathlib import Path

from playwright.sync_api import sync_playwright


BASE_URL = os.environ.get("LITELLM_TEST_BASE_URL", "http://127.0.0.1:4000")
USERNAME = os.environ["UI_USERNAME"]
PASSWORD = os.environ["UI_PASSWORD"]
OUTPUT = Path(os.environ["RUNNER_TEMP"]) / "admin-routes"

EXPECTED_PLACEHOLDERS = {
    "virtual-keys": {"按密钥别名或 ID 搜索…"},
    "playground": {
        "可选：输入自定义代理 Base URL（例如 http://localhost:5000）",
        "选择模型",
        "选择或创建标签",
        "选择 MCP 服务器",
        "选择向量存储",
        "选择安全护栏",
        "选择策略（生产版或已发布版本）",
        "输入消息...（Shift+Enter 换行）",
    },
    "usage": {"按邮箱搜索用户…"},
    "teams": {"按名称或 ID 搜索团队…"},
    "users": {"按邮箱或 ID 搜索…"},
    "budgets": {"按预算 ID 搜索…"},
}


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
        login_body = page.locator("body").inner_text(timeout=10000)
        assert "默认情况下，用户名为" in login_body
        assert "密码为你设置的 LiteLLM Proxy" in login_body
        assert "需要设置界面凭据或 SSO？" in login_body
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
                placeholders = {
                    value
                    for value in page.locator("[placeholder]").evaluate_all(
                        "(els) => els.map((el) => el.getAttribute('placeholder')).filter(Boolean)"
                    )
                }
                record.update(
                    {
                        "url": current,
                        "lang": lang,
                        "body_preview": body[:1000],
                        "placeholders": sorted(placeholders),
                        "status": "checked",
                    }
                )
                expected_placeholders = EXPECTED_PLACEHOLDERS.get(name, set())
                missing = sorted(expected_placeholders - placeholders)
                if missing:
                    raise AssertionError(f"missing translated placeholders: {missing}")
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
