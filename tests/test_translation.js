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
  }

  appendChild(node) {
    node.parentElement = this;
    this.childNodes.push(node);
  }

  hasAttribute(name) {
    return this.attributes.has(name);
  }

  getAttribute(name) {
    return this.attributes.get(name) || null;
  }

  setAttribute(name, value) {
    this.attributes.set(name, value);
  }

  addEventListener(name, listener) {
    this.listeners.set(name, listener);
  }

  click() {
    this.listeners.get("click")();
  }
}


test("restores the exact original English when a Chinese translation is ambiguous", () => {
  const body = new Element("body");
  const heading = new TextNode("AI GATEWAY");
  body.appendChild(heading);
  const elementsById = new Map();
  const document = {
    body,
    documentElement: { dataset: {}, lang: "en" },
    readyState: "complete",
    createElement: (tagName) => new Element(tagName),
    getElementById: (id) => elementsById.get(id) || null,
  };
  const originalAppendChild = body.appendChild.bind(body);
  body.appendChild = (node) => {
    originalAppendChild(node);
    if (node.id) elementsById.set(node.id, node);
  };
  const source = fs.readFileSync(path.join(__dirname, "..", "patches", "litellm-zh.js"), "utf8");
  vm.runInNewContext(source, {
    Array,
    MutationObserver: class { observe() {} },
    Node: { ELEMENT_NODE: 1, TEXT_NODE: 3 },
    Object,
    document,
    localStorage: { getItem: () => null, setItem() {} },
  });

  assert.equal(heading.nodeValue, "AI 网关");
  elementsById.get("litellm-zh-toggle").click();
  assert.equal(heading.nodeValue, "AI GATEWAY");
});
