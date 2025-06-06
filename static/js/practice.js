
initHandModel();
function clearResult() {
    const outputElement = document.getElementById("output");

    let words = outputElement.value.trim().split(/\s+/);

    if (words.length > 0 && words[0] !== "") {
      words.pop();
      outputElement.value = words.join(" ");
    }
  }
