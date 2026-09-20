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
