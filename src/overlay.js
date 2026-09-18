(function () {
  "use strict";

  var STORAGE_KEY = "litellm-ui-language";
  var translations = __LITELLM_ZH_TRANSLATIONS__;
  var TEXT_STATES = new WeakMap();
  var ATTRIBUTE_STATES = new WeakMap();
  var TRANSLATABLE_ATTRIBUTES = ["aria-label", "placeholder", "title"];
  var TEXT_SKIP_TAGS = /^(SCRIPT|STYLE|NOSCRIPT|TEXTAREA|INPUT|SELECT|OPTION|PRE|CODE)$/;
  var ATTRIBUTE_SKIP_TAGS = /^(SCRIPT|STYLE|NOSCRIPT|PRE|CODE)$/;
  var DATA_CELL_CONTROL_TAGS = /^(BUTTON|LABEL)$/;

  function hasOwn(object, key) {
    return Object.prototype.hasOwnProperty.call(object, key);
  }

  function isExplicitlyIgnored(element) {
    var current = element;
    while (current) {
      if (current.hasAttribute && current.hasAttribute("data-litellm-zh-ignore")) return true;
      if (current.isContentEditable) return true;
      if (current.getAttribute && current.getAttribute("contenteditable") === "true") return true;
      current = current.parentElement;
    }
    return false;
  }

  function isProtectedDataCellContext(element) {
    var current = element;
    while (current) {
      if (DATA_CELL_CONTROL_TAGS.test(current.tagName || "")) return false;
      if ((current.tagName || "") === "TD") return true;
      current = current.parentElement;
    }
    return false;
  }

  function shouldSkipText(node) {
    if (!node.parentElement) return false;
    if (isExplicitlyIgnored(node.parentElement)) return true;
    if (isProtectedDataCellContext(node.parentElement)) return true;
    var current = node.parentElement;
    while (current) {
      if (TEXT_SKIP_TAGS.test(current.tagName || "")) return true;
      current = current.parentElement;
    }
    return false;
  }

  function shouldSkipAttributes(element) {
    if (isExplicitlyIgnored(element)) return true;
    if (isProtectedDataCellContext(element)) return true;
    return ATTRIBUTE_SKIP_TAGS.test(element.tagName || "");
  }

  function translateExact(value) {
    if (hasOwn(translations, value)) return translations[value];

    var leadingMatch = value.match(/^\s*/);
    var trailingMatch = value.match(/\s*$/);
    var leading = leadingMatch ? leadingMatch[0] : "";
    var trailing = trailingMatch ? trailingMatch[0] : "";
    var coreEnd = value.length - trailing.length;
    var core = value.slice(leading.length, coreEnd);

    if (core && hasOwn(translations, core)) {
      return leading + translations[core] + trailing;
    }
    return value;
  }

  function translatedState(source) {
    return {
      source: source,
      translated: translateExact(source),
    };
  }

  function translateTextNode(node, language) {
    if (shouldSkipText(node)) return;

    var current = node.nodeValue;
    var state = TEXT_STATES.get(node);

    if (!state) {
      state = translatedState(current);
      TEXT_STATES.set(node, state);
    } else if (current !== state.source && current !== state.translated) {
      // React or another upstream script changed this node. Treat the new value
      // as the authoritative source instead of restoring the first value ever seen.
      state = translatedState(current);
      TEXT_STATES.set(node, state);
    }

    var desired = language === "zh-CN" ? state.translated : state.source;
    if (current !== desired) node.nodeValue = desired;
  }

  function getAttributeState(element, attribute, current) {
    var states = ATTRIBUTE_STATES.get(element);
    if (!states) {
      states = {};
      ATTRIBUTE_STATES.set(element, states);
    }

    var state = states[attribute];
    if (!state || (current !== state.source && current !== state.translated)) {
      state = translatedState(current);
      states[attribute] = state;
    }
    return state;
  }

  function translateAttribute(element, attribute, language) {
    if (!element.hasAttribute(attribute)) return;
    var current = element.getAttribute(attribute);
    if (current === null) return;

    var state = getAttributeState(element, attribute, current);
    var desired = language === "zh-CN" ? state.translated : state.source;
    if (current !== desired) element.setAttribute(attribute, desired);
  }

  function translateNode(node, language) {
    if (node.nodeType === Node.TEXT_NODE) {
      translateTextNode(node, language);
      return;
    }
    if (node.nodeType !== Node.ELEMENT_NODE) return;
    if (isExplicitlyIgnored(node)) return;

    if (!shouldSkipAttributes(node)) {
      TRANSLATABLE_ATTRIBUTES.forEach(function (attribute) {
        translateAttribute(node, attribute, language);
      });
    }

    if (TEXT_SKIP_TAGS.test(node.tagName || "")) return;
    Array.prototype.slice.call(node.childNodes).forEach(function (child) {
      translateNode(child, language);
    });
  }

  function applyLanguage(language) {
    document.documentElement.lang = language === "zh-CN" ? "zh-CN" : "en";
    document.documentElement.dataset.litellmLanguage = language;
    translateNode(document.body, language);

    var toggle = document.getElementById("litellm-zh-toggle");
    if (toggle) {
      toggle.textContent = language === "zh-CN" ? "中 / EN" : "EN / 中";
      toggle.setAttribute("aria-label", language === "zh-CN" ? "切换到英文" : "切换到中文");
    }
  }

  function addToggle() {
    if (document.getElementById("litellm-zh-toggle")) return;
    var button = document.createElement("button");
    button.id = "litellm-zh-toggle";
    button.type = "button";
    button.setAttribute("data-litellm-zh-ignore", "");
    button.style.cssText = "position:fixed;right:18px;bottom:18px;z-index:2147483647;border:1px solid #cbd5e1;border-radius:999px;background:#fff;color:#0f172a;padding:7px 12px;font:600 13px -apple-system,BlinkMacSystemFont,'Segoe UI',sans-serif;box-shadow:0 2px 10px rgba(15,23,42,.16);cursor:pointer";
    button.addEventListener("click", function () {
      var nextLanguage = document.documentElement.dataset.litellmLanguage === "zh-CN" ? "en" : "zh-CN";
      localStorage.setItem(STORAGE_KEY, nextLanguage);
      applyLanguage(nextLanguage);
    });
    document.body.appendChild(button);
  }

  function start() {
    var language = localStorage.getItem(STORAGE_KEY) === "en" ? "en" : "zh-CN";
    addToggle();
    applyLanguage(language);

    new MutationObserver(function (records) {
      var activeLanguage = document.documentElement.dataset.litellmLanguage || language;
      records.forEach(function (record) {
        if (record.type === "characterData") {
          translateTextNode(record.target, activeLanguage);
          return;
        }
        if (record.type === "attributes") {
          if (TRANSLATABLE_ATTRIBUTES.indexOf(record.attributeName) !== -1) {
            translateAttribute(record.target, record.attributeName, activeLanguage);
          }
          return;
        }
        Array.prototype.slice.call(record.addedNodes || []).forEach(function (node) {
          translateNode(node, activeLanguage);
        });
      });
    }).observe(document.body, {
      childList: true,
      characterData: true,
      attributes: true,
      attributeFilter: TRANSLATABLE_ATTRIBUTES,
      subtree: true,
    });
  }

  if (document.readyState === "loading") {
    document.addEventListener("DOMContentLoaded", start, { once: true });
  } else {
    start();
  }
})();
