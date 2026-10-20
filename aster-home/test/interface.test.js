const test = require("node:test");
const assert = require("node:assert/strict");
const fs = require("node:fs");
const path = require("node:path");

const root = path.join(__dirname, "..");

test("launcher contains every approved primary destination", () => {
  const html = fs.readFileSync(path.join(root, "index.html"), "utf8");
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
    assert.match(html, new RegExp(`data-id=["']${id}["']`));
  }
});

test("launcher has no remote recommendation or advertising dependencies", () => {
  for (const name of ["index.html", "styles.css", "app.js", "navigation.js"]) {
    const content = fs.readFileSync(path.join(root, name), "utf8");
    assert.doesNotMatch(content, /https?:\/\//i);
    assert.doesNotMatch(content, /advert|recommendation feed/i);
  }
});

test("first frame avoids full-screen blur and forced tile layers", () => {
  const css = fs.readFileSync(path.join(root, "styles.css"), "utf8");
  assert.doesNotMatch(css, /filter:\s*blur\(/i);
  assert.doesNotMatch(css, /translateZ\(/i);
});

test("application launch IDs match the audited TV components", () => {
  const js = fs.readFileSync(path.join(root, "app.js"), "utf8");
  for (const appId of [
    "org.tizen.netflix-app",
    "9Ur5IzDKqV.TizenYouTube",
    "org.tizen.primevideo",
    "com.samsung.tv.aria-video",
    "MCmYXNxgcu.DisneyPlus",
    "gzcc4LRFBF.Peacock",
    "5b8c3eb16b.BeamCTVDev",
    "rJyOSqC6Up.CBSAllAccess",
    "PvWgqxV3Xa.YouTubeTV",
  ]) {
    assert.match(js, new RegExp(appId.replace(/[.]/g, "\\.")));
  }
});

test("source switching resolves a Tizen video-source platform object", () => {
  const js = fs.readFileSync(path.join(root, "app.js"), "utf8");
  assert.match(js, /getPropertyValue\(\s*["']VIDEOSOURCE["']/);
  assert.match(js, /AsterNavigation\.findSource/);
});

test("successful source switching exits the launcher to reveal the source", () => {
  const js = fs.readFileSync(path.join(root, "app.js"), "utf8");
  assert.match(js, /function revealSource\(/);
  assert.match(js, /setStatus\(["']Switched to [\s\S]*revealSource\(\)/);
});

test("widget manifest declares the source-switch and app-launch privileges", () => {
  const manifest = fs.readFileSync(path.join(root, "config.xml"), "utf8");
  assert.equal(
    (manifest.match(/http:\/\/tizen\.org\/privilege\/tv\.window/g) || []).length,
    1,
  );
  assert.equal(
    (manifest.match(/http:\/\/tizen\.org\/privilege\/application\.launch/g) || []).length,
    1,
  );
});

test("widget manifest exposes only the capabilities used by the launcher", () => {
  const manifest = fs.readFileSync(path.join(root, "config.xml"), "utf8");
  const privileges = Array.from(
    manifest.matchAll(/<tizen:privilege name="([^"]+)"\s*\/>/g),
    (match) => match[1],
  ).sort();

  assert.deepEqual(privileges, [
    "http://tizen.org/privilege/application.launch",
    "http://tizen.org/privilege/tv.inputdevice",
    "http://tizen.org/privilege/tv.window",
  ]);
  assert.doesNotMatch(manifest, /<access\b/);
  assert.doesNotMatch(manifest, /<tizen:service\b/);
  assert.doesNotMatch(manifest, /microphone|mediacapture|recorder|web\.service/i);
  assert.doesNotMatch(manifest, /prelaunch\.support/);
  assert.match(manifest, /background-support="disable"/);
});

test("visible interface omits launcher branding and welcome prompts", () => {
  const html = fs.readFileSync(path.join(root, "index.html"), "utf8");
  for (const text of [
    "DAYBREAK",
    "Aster Home",
    "READY WHEN YOU ARE",
    "What sounds good?",
  ]) {
    assert.doesNotMatch(html, new RegExp(text, "i"));
  }
});

test("launcher icon is a 512px PNG suitable for Samsung Home", () => {
  const icon = fs.readFileSync(path.join(root, "launcher-icon.png"));
  assert.deepEqual(icon.subarray(0, 8), Buffer.from([137, 80, 78, 71, 13, 10, 26, 10]));
  assert.equal(icon.readUInt32BE(16), 512);
  assert.equal(icon.readUInt32BE(20), 512);
});

test("streaming monograms use the local blue-gray badge treatment", () => {
  const css = fs.readFileSync(path.join(root, "styles.css"), "utf8");
  assert.match(css, /\.app-monogram\s*\{[\s\S]*?display:\s*flex/);
  assert.match(css, /\.netflix \.app-monogram/);
  assert.match(css, /\.paramount \.app-monogram/);
});
