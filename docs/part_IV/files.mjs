import { fileLines, fileTrace } from "./core.mjs?v=20261017-state";
const $ = (id) => document.getElementById(id);
let steps = [],
  at = 0,
  lines = [],
  ready = false;
const codes = {
  head: `1. Open the text file at the beginning.
2. Read the next line, counting blank lines too.
3. Remove whitespace from the beginning and end of that line.
4. Print the cleaned line.
5. Repeat until n lines have been read, then close the file.
If a requested line does not exist, report StopIteration and close the file.`,
  skip: `1. Open the file at the beginning.
2. Read and discard the first line.
3. Read the next line and remove its surrounding whitespace.
4. Print the cleaned second line, then close the file.
If a requested line does not exist, report StopIteration and close the file.`,
  loop: `1. Open the file at the beginning.
2. Read, clean and print the first line.
3. Continue from the next unread line; clean and print each remaining line.
4. Stop at the end of the file and close it.
If the first read finds an empty file, report StopIteration and close the file.`,
};
function describeAction(action) {
  if (action.startsWith("next(in_file) returns ")) return "Read the next line: " + action.slice("next(in_file) returns ".length);
  if (action.startsWith("Loop iteration ")) return "Begin requested line " + (Number(action.slice("Loop iteration ".length)) + 1);
  if (action === "strip() removes surrounding whitespace") return "Remove surrounding whitespace from the returned line";
  if (action === "print(line)") return "Print the cleaned line";
  if (action === "for line in in_file reads the next line") return "Read the next unread line in the loop";
  if (action === "Exit with: file closed") return "Close the file";
  return action;
}
function invalidate(message) {
  ready = false; steps = []; at = 0;
  for (const id of ["lines", "variables", "output", "prediction-comparison", "error"]) $(id).textContent = "";
  $("step").disabled = true; $("run").disabled = true;
  $("n").disabled = $("program").value !== "head";
  $("code").textContent = codes[$("program").value];
  $("file-empty").hidden = false;
  $("file-empty").textContent = "Open the file to see its lines and reading position.";
  $("output-empty").hidden = false;
  $("output-empty").textContent = "No lines have been printed.";
  $("status").textContent = message;
}
function render() {
  let s = steps[at];
  if (!s || !ready) return;
  $("lines").replaceChildren();
  $("file-empty").hidden = lines.length > 0;
  $("file-empty").textContent = "Empty file (0 lines). There is no line to read. Add text above and reopen the file to try a non-empty example.";
  lines.forEach((line, i) => {
    const li = document.createElement("li");
    const active = i === s.position && !s.closed;
    li.textContent =
      (line.replace(/\n$/, "") || "(blank line)") +
      (line.endsWith("\n") ? " ↵" : "") +
      (active ? " ← next unread" : "");
    li.className = i < s.position ? "consumed" : active ? "next-line" : "";
    $("lines").append(li);
  });
  $("variables").textContent =
    `File: ${s.closed ? "closed" : "open"}. Consumed: ${s.position}/${lines.length}. ` +
    (s.line !== null ? `line = ${JSON.stringify(s.line)}. ` : "") +
    (s.i !== undefined ? `i = ${s.i}. ` : "") +
    (s.returned !== undefined ? `Last next() = ${JSON.stringify(s.returned)}. ` : "") +
    (s.exception ? `Exception: ${s.exception}.` : "");
  const onlyBlankLines = s.output.length > 0 && s.output.every(line => line === "");
  $("output-empty").hidden = s.output.length > 0 && !onlyBlankLines;
  $("output-empty").textContent = onlyBlankLines
    ? `${s.output.length} blank ${s.output.length === 1 ? "line" : "lines"} printed.`
    : s.closed ? "No lines were printed." : "No lines have been printed yet.";
  $("output").textContent = s.output.join("\n") + (s.output.length ? "\n" : "");
  $("prediction-comparison").textContent = s.closed && $("prediction").value.trim()
    ? "Your prediction: " + $("prediction").value.trim() : "";
  $("status").textContent = `Step ${at + 1}/${steps.length}: ${describeAction(s.action)}`;
  $("error").textContent = s.exception
    ? "StopIteration. The requested line does not exist. " + (s.closed ? "The file is closed." : "The next trace step closes the file.")
    : "";
  $("step").disabled = !ready || at === steps.length - 1;
  $("run").disabled = !ready || at === steps.length - 1;
}
function prepare() {
  invalidate("Choose valid inputs, then reopen the file.");
  const isHead = $("program").value === "head";
  const n = isHead ? Number($("n").value) : 0;
  if (isHead && (!$("n").value.trim() || !Number.isInteger(n) || n < 0 || n > 100)) {
    $("error").textContent = "Choose an integer n from 0 to 100.";
    return;
  }
  lines = fileLines($("filetext").value);
  steps = fileTrace($("filetext").value, n, $("program").value);
  at = 0;
  ready = true;
  $("code").textContent = codes[$("program").value];
  render();
}
$("prepare").onclick = prepare;
$("step").onclick = () => {
  at++;
  render();
};
$("run").onclick = () => {
  at = steps.length - 1;
  render();
};
for (const id of ["filetext", "n", "program"])
  $(id).addEventListener("input", () => invalidate("Inputs changed. Reopen the file to start again."));
invalidate("Predict the output, then choose Open file / restart to begin.");
$("prediction").addEventListener("input", () => { if (ready) render(); });
