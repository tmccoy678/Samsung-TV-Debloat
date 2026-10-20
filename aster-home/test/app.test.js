const test = require("node:test");
const assert = require("node:assert/strict");
const fs = require("node:fs");
const path = require("node:path");
const vm = require("node:vm");

const AsterNavigation = require("../navigation.js");

function runLauncher() {
  const listeners = {};
  const tiles = new Map();
  let focusedId = null;
  let launchedApp = null;
  const operations = [];
  let exitCount = 0;

  for (const id of [
    "live-tv",
    "ps5",
    "netflix",
    "youtube",
    "prime-video",
    "apple-tv",
    "disney-plus",
    "peacock",
    "max",
    "paramount-plus",
    "youtube-tv",
  ]) {
    const attributes = {
      "data-id": id,
      "data-action": ["live-tv", "ps5"].includes(id) ? "source" : "app",
      "data-source": id === "ps5" ? "HDMI" : "TV",
      "data-number": id === "ps5" ? "2" : "1",
    };
    tiles.set(id, {
      classList: {
        add(name) {
          if (name === "is-focused") focusedId = id;
        },
        remove(name) {
          if (name === "is-focused" && focusedId === id) focusedId = null;
        },
      },
      getAttribute(name) {
        return attributes[name];
      },
      querySelector(selector) {
        if (selector === ".app-name") return { textContent: id };
        return null;
      },
      addEventListener() {},
    });
  }

  const textElements = {
    status: { textContent: "", className: "status" },
    time: { textContent: "" },
    date: { textContent: "" },
  };
  const document = {
    addEventListener(name, callback) {
      listeners[name] = callback;
    },
    getElementById(id) {
      return textElements[id];
    },
    querySelector(selector) {
      if (selector === ".tile.is-focused") return tiles.get(focusedId) || null;
      const match = selector.match(/^\[data-id="([^"]+)"\]$/);
      return match ? tiles.get(match[1]) || null : null;
    },
    querySelectorAll(selector) {
      return selector === ".tile" ? Array.from(tiles.values()) : [];
    },
  };
  const context = {
    AsterNavigation,
    document,
    tizen: {
      application: {
        getCurrentApplication() {
          return { exit() { exitCount += 1; } };
        },
        launch(appId, onSuccess) {
          launchedApp = appId;
          operations.push("launch:" + appId);
          onSuccess();
        },
      },
      systeminfo: {
        getPropertyValue(name, onSuccess) {
          assert.equal(name, "VIDEOSOURCE");
          onSuccess({
            connected: [
              { type: "TV", number: 1 },
              { type: "HDMI", number: 2 },
            ],
          });
        },
      },
      tvwindow: {
        setSource(source, onSuccess) {
          operations.push("source:" + source.type + ":" + source.number);
          onSuccess();
        },
      },
    },
    window: {
      localStorage: {
        setItem(key) {
          operations.push("signal:" + key);
        },
      },
      setInterval() {},
      setTimeout(callback) { callback(); },
    },
  };

  vm.runInNewContext(
    fs.readFileSync(path.join(__dirname, "..", "app.js"), "utf8"),
    context,
  );

  return {
    press(keyCode) {
      listeners.keydown({ keyCode, preventDefault() {} });
    },
    result() {
      return { launchedApp, operations, exitCount };
    },
  };
}

test("opening a streaming app signals the TV-local release trigger and exits", () => {
  const launcher = runLauncher();

  launcher.press(40);
  launcher.press(13);

  assert.deepEqual(launcher.result(), {
    launchedApp: "org.tizen.netflix-app",
    operations: [
      "signal:aster-release-live-tv",
      "launch:org.tizen.netflix-app",
    ],
    exitCount: 1,
  });
});

test("opening Live TV switches the source and exits the launcher", () => {
  const launcher = runLauncher();

  launcher.press(13);

  assert.deepEqual(launcher.result(), {
    launchedApp: null,
    operations: [
      "signal:aster-release-live-tv",
      "source:TV:1",
    ],
    exitCount: 1,
  });
});
