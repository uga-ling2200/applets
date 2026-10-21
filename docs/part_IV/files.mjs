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
function render() {
  let s = steps[at];
  if (!s) return;
  $("lines").replaceChildren();
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
  $("output").textContent = s.output.join("\n") + (s.output.length ? "\n" : "");
  $("prediction-comparison").textContent = s.closed && $("prediction").value.trim()
    ? "Your prediction: " + $("prediction").value.trim() : "";
  $("status").textContent = `Step ${at + 1}/${steps.length}: ${s.action}`;
  $("error").textContent = s.exception
    ? "StopIteration. The requested line does not exist. " + (s.closed ? "The with statement closed the file." : "The next trace step closes the file.")
    : "";
  $("step").disabled = !ready || at === steps.length - 1;
  $("run").disabled = !ready || at === steps.length - 1;
}
function prepare() {
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
  $(id).addEventListener("input", () => {
    $("n").disabled = $("program").value !== "head";
    ready = false;
    $("step").disabled = true;
    $("run").disabled = true;
    $("status").textContent = "Inputs changed. Reopen the file to start again.";
  });
prepare();

$("prediction").addEventListener("input", render);
