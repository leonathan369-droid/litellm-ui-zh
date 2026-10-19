const assert = require("node:assert/strict");
const fs = require("node:fs");
const path = require("node:path");
const test = require("node:test");
const vm = require("node:vm");


class TextNode {
  constructor(value) {
    this.nodeType = 3;
    this.nodeValue = value;
    this.parentElement = null;
  }
}


class Element {
  constructor(tagName) {
    this.nodeType = 1;
    this.tagName = tagName.toUpperCase();
    this.childNodes = [];
    this.attributes = new Map();
    this.listeners = new Map();
    this.style = { cssText: "" };
    this.dataset = {};
    this.id = "";
    this.type = "";
    this.parentElement = null;
    this.textContent = "";
    this.isContentEditable = false;
  }

  appendChild(node) {
    node.parentElement = this;
    this.childNodes.push(node);
    return node;
  }

  get textContent() {
    return this.childNodes.length
      ? this.childNodes.map((node) => node.nodeType === 3 ? node.nodeValue : node.textContent).join("")
      : this._textContent;
  }

  set textContent(value) {
    this._textContent = value;
  }

  contains(node) {
    return this === node || this.childNodes.some((child) => child === node || (child.contains && child.contains(node)));
  }

  querySelectorAll(selector) {
    assert.equal(selector, "[data-spinner-id]");
    const found = [];
    for (const child of this.childNodes) {
      if (child.nodeType !== 1) continue;
      if (child.hasAttribute("data-spinner-id")) found.push(child);
      found.push(...child.querySelectorAll(selector));
    }
    return found;
  }

  hasAttribute(name) {
    return this.attributes.has(name);
  }

  getAttribute(name) {
    return this.attributes.has(name) ? this.attributes.get(name) : null;
  }

  setAttribute(name, value) {
    this.attributes.set(name, String(value));
  }

  addEventListener(name, listener) {
    this.listeners.set(name, listener);
  }

  click() {
    const listener = this.listeners.get("click");
    if (listener) listener();
  }
}


function createEnvironment(children = []) {
  const body = new Element("body");
  children.forEach((child) => body.appendChild(child));

  const elementsById = new Map();
  const observers = [];
  const storage = new Map();

  const originalAppendChild = body.appendChild.bind(body);
  body.appendChild = (node) => {
    const result = originalAppendChild(node);
    if (node.id) elementsById.set(node.id, node);
    return result;
  };
  body.removeChild = (node) => {
    body.childNodes.splice(body.childNodes.indexOf(node), 1);
    node.parentElement = null;
    if (node.id) elementsById.delete(node.id);
    return node;
  };

  const document = {
    body,
    documentElement: { dataset: {}, lang: "en" },
    readyState: "complete",
    createElement: (tagName) => new Element(tagName),
    getElementById: (id) => elementsById.get(id) || null,
  };

  class MutationObserverMock {
    constructor(callback) {
      this.callback = callback;
      this.options = null;
      observers.push(this);
    }

    observe(_target, options) {
      this.options = options;
    }
  }

  const localStorage = {
    getItem: (key) => storage.has(key) ? storage.get(key) : null,
    setItem: (key, value) => storage.set(key, value),
  };

  const source = fs.readFileSync(
    path.join(__dirname, "..", "dist", "litellm-zh.js"),
    "utf8",
  );

  vm.runInNewContext(source, {
    Array,
    Map,
    MutationObserver: MutationObserverMock,
    Node: { ELEMENT_NODE: 1, TEXT_NODE: 3 },
    Object,
    WeakMap,
    document,
    localStorage,
  });

  return {
    body,
    document,
    observer: observers.at(-1),
    toggle: elementsById.get("litellm-zh-toggle"),
  };
}


test("restores the exact original English when a Chinese translation is ambiguous", () => {
  const heading = new TextNode("AI GATEWAY");
  const env = createEnvironment([heading]);

  assert.equal(heading.nodeValue, "AI 网关");
  env.toggle.click();
  assert.equal(heading.nodeValue, "AI GATEWAY");
});


test("waits for React to replace its initial loading shell before modifying the DOM", () => {
  const shell = new Element("div");
  const spinner = new Element("svg");
  spinner.setAttribute("data-spinner-id", "initial-spinner");
  const loading = new TextNode("Loading...");
  shell.appendChild(spinner);
  shell.appendChild(loading);
  const env = createEnvironment([shell]);

  assert.equal(loading.nodeValue, "Loading...");
  assert.equal(env.document.documentElement.lang, "en");
  assert.equal(env.document.documentElement.dataset.litellmLanguage, undefined);
  assert.equal(env.document.getElementById("litellm-zh-toggle"), null);
  const unrelated = new Element("script");
  env.body.appendChild(unrelated);
  env.observer.callback([{ type: "childList", addedNodes: [unrelated], removedNodes: [] }]);
  assert.equal(loading.nodeValue, "Loading...");
  assert.equal(env.document.getElementById("litellm-zh-toggle"), null);

  env.body.removeChild(shell);
  const label = new TextNode("User");
  env.body.appendChild(label);
  env.observer.callback([{ type: "childList", addedNodes: [label], removedNodes: [shell] }]);
  assert.equal(label.nodeValue, "用户");
  assert.equal(env.document.documentElement.lang, "zh-CN");
  const toggle = env.document.getElementById("litellm-zh-toggle");
  assert.ok(toggle);
  toggle.click();
  env.observer.callback([{ type: "childList", addedNodes: [toggle], removedNodes: [] }]);
  assert.equal(env.document.documentElement.lang, "en");
  assert.equal(label.nodeValue, "User");
  assert.equal(env.document.getElementById("litellm-zh-toggle"), toggle);
});


test("restores a removed language toggle without duplicating it or resetting the language", () => {
  const heading = new TextNode("User");
  const env = createEnvironment([heading]);

  for (const language of ["zh-CN", "en"]) {
    const previous = env.document.getElementById("litellm-zh-toggle");
    env.body.removeChild(previous);
    env.observer.callback([
      { type: "childList", removedNodes: [previous], addedNodes: [] },
    ]);
    const restored = env.document.getElementById("litellm-zh-toggle");
    assert.ok(restored);
    assert.notEqual(restored, previous);
    assert.equal(env.document.documentElement.dataset.litellmLanguage, language);
    assert.equal(restored.textContent, language === "zh-CN" ? "中 / EN" : "EN / 中");
    assert.equal(restored.getAttribute("aria-label"), language === "zh-CN" ? "切换到英文" : "切换到中文");

    env.observer.callback([
      { type: "childList", removedNodes: [], addedNodes: [restored] },
      { type: "attributes", target: restored, attributeName: "aria-label" },
    ]);
    assert.equal(env.document.getElementById("litellm-zh-toggle"), restored);
    assert.equal(env.body.childNodes.filter((node) => node.id === "litellm-zh-toggle").length, 1);
    restored.click();
    assert.equal(heading.nodeValue, language === "zh-CN" ? "User" : "用户");
  }
});


test("translates exact UI labels without translating table data or matching substrings", () => {
  const label = new Element("label");
  const labelText = new TextNode("User");
  label.appendChild(labelText);

  const table = new Element("table");
  const row = new Element("tr");
  const cell = new Element("td");
  const userValue = new TextNode("User");
  cell.appendChild(userValue);
  row.appendChild(cell);
  table.appendChild(row);

  const values = [
    "PageRank",
    "UserService",
    "All-MiniLM-L6-v2",
    "Runtime",
    "NewModel",
    "SaveGPT",
  ].map((value) => new TextNode(value));

  createEnvironment([label, table, ...values]);

  assert.equal(labelText.nodeValue, "用户");
  assert.equal(userValue.nodeValue, "User");
  assert.deepEqual(
    values.map((node) => node.nodeValue),
    [
      "PageRank",
      "UserService",
      "All-MiniLM-L6-v2",
      "Runtime",
      "NewModel",
      "SaveGPT",
    ],
  );
});


test("translates DataTable empty-state UI inside colspan cells while protecting ordinary data cells", () => {
  const table = new Element("table");
  const row = new Element("tr");

  const dataCell = new Element("td");
  const dataText = new TextNode("User");
  dataCell.appendChild(dataText);
  row.appendChild(dataCell);

  const emptyRow = new Element("tr");
  const emptyCell = new Element("td");
  emptyCell.setAttribute("colspan", "6");
  const emptyText = new TextNode("No keys found");
  emptyCell.appendChild(emptyText);
  emptyRow.appendChild(emptyCell);

  table.appendChild(row);
  table.appendChild(emptyRow);

  const env = createEnvironment([table]);

  assert.equal(dataText.nodeValue, "User");
  assert.equal(emptyText.nodeValue, "未找到密钥");

  env.toggle.click();
  assert.equal(dataText.nodeValue, "User");
  assert.equal(emptyText.nodeValue, "No keys found");
});



test("tracks upstream characterData changes instead of restoring stale first-seen text", () => {
  const status = new TextNode("Loading...");
  const env = createEnvironment([status]);

  assert.equal(status.nodeValue, "加载中…");

  status.nodeValue = "No data";
  env.observer.callback([{ type: "characterData", target: status }]);

  assert.equal(status.nodeValue, "暂无数据");

  env.toggle.click();
  assert.equal(status.nodeValue, "No data");
});


test("tracks dynamically updated translatable attributes", () => {
  const input = new Element("input");
  input.setAttribute("placeholder", "Search");
  const env = createEnvironment([input]);

  assert.equal(input.getAttribute("placeholder"), "搜索");

  input.setAttribute("placeholder", "Search model names…");
  env.observer.callback([
    { type: "attributes", target: input, attributeName: "placeholder" },
  ]);

  assert.equal(input.getAttribute("placeholder"), "搜索模型名称…");

  env.toggle.click();
  assert.equal(input.getAttribute("placeholder"), "Search model names…");
});


test("does not translate code, preformatted, contenteditable, or explicitly ignored content", () => {
  const code = new Element("code");
  const codeText = new TextNode("User");
  code.appendChild(codeText);

  const pre = new Element("pre");
  const preText = new TextNode("Page");
  pre.appendChild(preText);

  const editable = new Element("div");
  editable.isContentEditable = true;
  const editableText = new TextNode("Save");
  editable.appendChild(editableText);

  const ignored = new Element("div");
  ignored.setAttribute("data-litellm-zh-ignore", "");
  const ignoredText = new TextNode("New");
  ignored.appendChild(ignoredText);

  createEnvironment([code, pre, editable, ignored]);

  assert.equal(codeText.nodeValue, "User");
  assert.equal(preText.nodeValue, "Page");
  assert.equal(editableText.nodeValue, "Save");
  assert.equal(ignoredText.nodeValue, "New");
});


test("preserves protected attributes when upstream updates them dynamically", () => {
  const ignored = new Element("div");
  ignored.setAttribute("data-litellm-zh-ignore", "");
  const ignoredChild = new Element("span");
  ignored.appendChild(ignoredChild);
  const cell = new Element("td");
  const editable = new Element("div");
  editable.isContentEditable = true;
  const code = new Element("code");
  const protectedElements = [ignoredChild, cell, editable, code];
  for (const element of protectedElements) {
    element.setAttribute("title", "User");
  }

  const env = createEnvironment([ignored, cell, editable, code]);
  for (const element of protectedElements) {
    assert.equal(element.getAttribute("title"), "User");
    element.setAttribute("title", "Admin");
    env.observer.callback([
      { type: "attributes", target: element, attributeName: "title" },
    ]);
    assert.equal(element.getAttribute("title"), "Admin");
  }

  env.toggle.click();
  for (const element of protectedElements) {
    assert.equal(element.getAttribute("title"), "Admin");
  }
});


test("translates the audited management labels and restores their exact English", () => {
  const cases = [
    ["Traces", "追踪"],
    ["Investigations", "调查"],
    ["Find what needs attention", "发现需要关注的问题"],
    ["Set up traces", "配置追踪"],
    ["Basic Information (Required)", "基本信息（必填）"],
    ["Version (Optional)", "版本（可选）"],
    ["Run an investigation", "运行调查"],
    ["Add New Skill", "添加技能"],
    ["No vector stores", "暂无向量存储"],
    ["Request Lifecycle", "请求生命周期"],
    ["Cost Breakdown", "成本明细"],
    ["Create New Policy", "创建新策略"],
    ["Prompt Details", "提示词详情"],
    ["Publish Prompt", "发布提示词"],
    ["No conversations found", "未找到对话"],
    ["Test Configuration", "测试配置"],
    ["Regenerate Virtual Key", "重新生成虚拟密钥"],
    ["Member Permissions", "成员权限"],
    ["User Settings", "用户设置"],
    ["Edit Budget", "编辑预算"],
    ["Configure Model Fallbacks", "配置模型回退"],
  ];
  const labels = cases.map(([english]) => {
    const label = new Element("label");
    label.appendChild(new TextNode(english));
    return label;
  });
  const env = createEnvironment(labels);
  assert.deepEqual(labels.map((label) => label.childNodes[0].nodeValue), cases.map(([, chinese]) => chinese));
  env.toggle.click();
  assert.deepEqual(labels.map((label) => label.childNodes[0].nodeValue), cases.map(([english]) => english));
  env.toggle.click();
  assert.deepEqual(labels.map((label) => label.childNodes[0].nodeValue), cases.map(([, chinese]) => chinese));
});


test("new dictionary words do not translate matching model data, code, or user input", () => {
  const values = ["Traces", "Investigations", "Project", "System", "Assistant", "Home", "ok", "Live", "Errors", "Completed", "Datasets"];
  const nodes = [];
  const containers = [];
  for (const tag of ["td", "code", "pre", "textarea", "input"]) {
    for (const value of values) {
      const element = new Element(tag);
      const text = new TextNode(value);
      element.appendChild(text);
      nodes.push([text, value]);
      containers.push(element);
    }
  }
  const input = new Element("input");
  input.value = "Project";
  input.setAttribute("placeholder", "Enter User ID…");
  const env = createEnvironment([...containers, input]);
  assert.equal(input.getAttribute("placeholder"), "输入用户 ID…");
  for (let i = 0; i < 3; i += 1) {
    for (const [node, original] of nodes) assert.equal(node.nodeValue, original);
    assert.equal(input.value, "Project");
    env.toggle.click();
  }
  assert.equal(input.getAttribute("placeholder"), "Enter User ID…");
});
