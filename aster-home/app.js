(function () {
  "use strict";

  var layout = [
    ["live-tv", "ps5"],
    ["netflix", "youtube", "prime-video", "apple-tv", "disney-plus"],
    ["peacock", "max", "paramount-plus", "youtube-tv"]
  ];

  var launchIds = {
    "netflix": "org.tizen.netflix-app",
    "youtube": "9Ur5IzDKqV.TizenYouTube",
    "prime-video": "org.tizen.primevideo",
    "apple-tv": "com.samsung.tv.aria-video",
    "disney-plus": "MCmYXNxgcu.DisneyPlus",
    "peacock": "gzcc4LRFBF.Peacock",
    "max": "5b8c3eb16b.BeamCTVDev",
    "paramount-plus": "rJyOSqC6Up.CBSAllAccess",
    "youtube-tv": "PvWgqxV3Xa.YouTubeTV"
  };
  var currentId = "live-tv";
  var statusElement = document.getElementById("status");

  function tile(id) {
    return document.querySelector('[data-id="' + id + '"]');
  }

  function setStatus(message, isError) {
    statusElement.textContent = message;
    statusElement.className = isError ? "status error" : "status";
  }

  function exitLauncher() {
    try {
      tizen.application.getCurrentApplication().exit();
    } catch (error) {
      window.history.back();
    }
  }

  function revealSource() {
    window.setTimeout(exitLauncher, 250);
  }

  function focusTile(id) {
    var previous = document.querySelector(".tile.is-focused");
    var next = tile(id);
    if (!next) {
      return;
    }
    if (previous) {
      previous.classList.remove("is-focused");
    }
    next.classList.add("is-focused");
    currentId = id;
  }

  function signalLiveTvRelease() {
    try {
      window.localStorage.setItem("aster-release-live-tv", String(Date.now()));
    } catch (error) {
      return;
    }
  }

  function launchApplication(id) {
    var appId = launchIds[id];
    if (!appId) {
      setStatus("That app is not configured.", true);
      return;
    }
    setStatus("Opening " + tile(id).querySelector(".app-name").textContent + "…", false);
    try {
      tizen.application.launch(
        appId,
        function () {
          revealSource();
        },
        function (error) {
          setStatus("Could not open the app: " + error.message, true);
        }
      );
    } catch (error) {
      setStatus("App launch is available on the TV.", true);
    }
  }

  function switchSource(id) {
    var element = tile(id);
    var sourceType = element.getAttribute("data-source");
    var sourceNumber = Number(element.getAttribute("data-number"));
    var sourceName = id === "ps5" ? "PlayStation 5" : "Live TV";
    setStatus("Switching to " + sourceName + "…", false);
    try {
      tizen.systeminfo.getPropertyValue(
        "VIDEOSOURCE",
        function (sourceState) {
          var source = AsterNavigation.findSource(sourceState, sourceType, sourceNumber);
          if (!source) {
            setStatus(sourceName + " is not available right now.", true);
            return;
          }
          tizen.tvwindow.setSource(
            source,
            function () {
              setStatus("Switched to " + sourceName + ".", false);
              revealSource();
            },
            function (error) {
              setStatus("Could not switch sources: " + error.message, true);
            },
            "MAIN"
          );
        },
        function (error) {
          setStatus("Could not inspect sources: " + error.message, true);
        }
      );
    } catch (error) {
      setStatus("Could not switch sources: " + error.message, true);
    }
  }

  function activateCurrent() {
    var element = tile(currentId);
    if (!element) {
      return;
    }
    if (element.getAttribute("data-action") === "app") {
      launchApplication(currentId);
    } else {
      switchSource(currentId);
    }
  }

  function updateClock() {
    var now = new Date();
    var hours = now.getHours();
    var minutes = String(now.getMinutes());
    var suffix = hours >= 12 ? "PM" : "AM";
    hours = hours % 12 || 12;
    if (minutes.length < 2) {
      minutes = "0" + minutes;
    }
    document.getElementById("time").textContent = hours + ":" + minutes + " " + suffix;
    document.getElementById("date").textContent = now.toLocaleDateString("en-US", {
      weekday: "long",
      month: "long",
      day: "numeric"
    });
  }

  function directionForKey(keyCode) {
    if (keyCode === 37) { return "left"; }
    if (keyCode === 38) { return "up"; }
    if (keyCode === 39) { return "right"; }
    if (keyCode === 40) { return "down"; }
    return null;
  }

  document.addEventListener("keydown", function (event) {
    var direction = directionForKey(event.keyCode);
    var next;
    if (direction) {
      event.preventDefault();
      next = AsterNavigation.moveFocus(layout, currentId, direction);
      if (next) {
        focusTile(next);
      }
      return;
    }
    if (event.keyCode === 13) {
      event.preventDefault();
      activateCurrent();
      return;
    }
    if (event.keyCode === 10009 || event.keyCode === 27) {
      exitLauncher();
    }
  });

  Array.prototype.forEach.call(document.querySelectorAll(".tile"), function (element) {
    element.addEventListener("click", function () {
      focusTile(element.getAttribute("data-id"));
      activateCurrent();
    });
  });

  signalLiveTvRelease();
  updateClock();
  window.setInterval(updateClock, 30000);
  focusTile(currentId);
})();
