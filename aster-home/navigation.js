(function (root, factory) {
  var api = factory();
  if (typeof module === "object" && module.exports) {
    module.exports = api;
  } else {
    root.AsterNavigation = api;
  }
})(this, function () {
  "use strict";

  function locate(layout, id) {
    var row;
    var column;
    for (row = 0; row < layout.length; row += 1) {
      for (column = 0; column < layout[row].length; column += 1) {
        if (layout[row][column] === id) {
          return { row: row, column: column };
        }
      }
    }
    return null;
  }

  function proportionalColumn(sourceColumn, sourceLength, targetLength) {
    if (sourceLength <= 1 || targetLength <= 1) {
      return 0;
    }
    return Math.floor((sourceColumn / (sourceLength - 1)) * (targetLength - 1));
  }

  function moveFocus(layout, currentId, direction) {
    if (!layout || layout.length === 0 || layout[0].length === 0) {
      return null;
    }

    var position = locate(layout, currentId);
    if (!position) {
      return layout[0][0];
    }

    var row = position.row;
    var column = position.column;
    var targetRow;

    if (direction === "left") {
      column = Math.max(0, column - 1);
    } else if (direction === "right") {
      column = Math.min(layout[row].length - 1, column + 1);
    } else if (direction === "up") {
      targetRow = Math.max(0, row - 1);
      column = proportionalColumn(column, layout[row].length, layout[targetRow].length);
      row = targetRow;
    } else if (direction === "down") {
      targetRow = Math.min(layout.length - 1, row + 1);
      column = proportionalColumn(column, layout[row].length, layout[targetRow].length);
      row = targetRow;
    }

    return layout[row][column];
  }

  function findSource(sourceState, type, number) {
    var sources = [];
    var index;
    if (sourceState && sourceState.connected) {
      sources = sources.concat(sourceState.connected);
    }
    if (sourceState && sourceState.disconnected) {
      sources = sources.concat(sourceState.disconnected);
    }
    for (index = 0; index < sources.length; index += 1) {
      if (sources[index].type === type && Number(sources[index].number) === Number(number)) {
        return sources[index];
      }
    }
    return null;
  }

  return { findSource: findSource, moveFocus: moveFocus };
});
