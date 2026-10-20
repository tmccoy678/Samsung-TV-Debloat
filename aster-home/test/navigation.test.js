const test = require("node:test");
const assert = require("node:assert/strict");

const { findSource, moveFocus } = require("../navigation.js");

const layout = [
  ["live-tv", "ps5"],
  ["netflix", "youtube", "prime-video", "apple-tv", "disney-plus"],
  ["peacock", "max", "paramount-plus", "youtube-tv"],
];

test("horizontal movement stays inside the active row", () => {
  assert.equal(moveFocus(layout, "live-tv", "right"), "ps5");
  assert.equal(moveFocus(layout, "ps5", "right"), "ps5");
  assert.equal(moveFocus(layout, "ps5", "left"), "live-tv");
});

test("vertical movement selects the nearest proportional tile", () => {
  assert.equal(moveFocus(layout, "live-tv", "down"), "netflix");
  assert.equal(moveFocus(layout, "ps5", "down"), "disney-plus");
  assert.equal(moveFocus(layout, "prime-video", "down"), "max");
  assert.equal(moveFocus(layout, "youtube-tv", "up"), "disney-plus");
});

test("movement from an unknown tile is deterministic", () => {
  assert.equal(moveFocus(layout, "missing", "left"), "live-tv");
});

test("empty layouts do not produce a focus target", () => {
  assert.equal(moveFocus([], "live-tv", "right"), null);
});

test("source selection returns the TV-provided platform object", () => {
  const hdmi2 = { type: "HDMI", number: 2 };
  const sourceState = {
    connected: [{ type: "TV", number: 1 }],
    disconnected: [{ type: "HDMI", number: 1 }, hdmi2],
  };

  assert.equal(findSource(sourceState, "HDMI", 2), hdmi2);
  assert.equal(findSource(sourceState, "HDMI", 3), null);
});
