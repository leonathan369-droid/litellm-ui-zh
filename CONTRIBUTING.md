# Contributing

欢迎提交简体中文措辞、兼容性验证、安装器修复和 Overlay 正确性改进。

## 普通翻译

优先只修改 `locales/zh-CN.json`。保留技术标识、API 字段、路径、模型名和必要的产品专有名词。修改后重新构建：

```bash
python3 scripts/build_patch.py
python3 scripts/build_patch.py --check
```

不要直接编辑 `dist/litellm-zh.js`。

## 提交前检查

```bash
python3 -m unittest discover -s tests -v
python3 -m py_compile scripts/install.py scripts/build_patch.py scripts/check_upstream.py scripts/collect_strings.py
node --check dist/litellm-zh.js
node --test tests/test_translation.js
```

涉及 LiteLLM 新版本时，请说明精确 LiteLLM 版本、系统、浏览器、检查路由和仍未验证部分。

## 边界

不要提交 LiteLLM 原始静态 UI、Proxy 配置、API Key、MASTER_KEY、数据库 URL、Cookie、完整环境文件或未脱敏日志。
