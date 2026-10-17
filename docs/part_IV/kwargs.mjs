import { filterTrace } from "./core.mjs";
const $ = (id) => document.getElementById(id);
let rows = [],
  cursor = 0,
  prepared = false;
const code = `def extract_and_filter_words(string, words_to_include=None):
    if words_to_include is None:
        words_to_include = set()
    words = extract_words(string)
    if words_to_include:
        filtered_words = []
        for word in words:
            if word in words_to_include:
                filtered_words.append(word)
    else:
        filtered_words = words
    return filtered_words`;
$("code").textContent = code;
const repr = (values) => "[" + values.map(JSON.stringify).join(", ") + "]";
function render() {
  const result = [];
  $("tokens").replaceChildren();
  rows.forEach((r, i) => {
    const li = document.createElement("li");
    li.textContent =
      r.word +
      (i < cursor ? (r.keep ? " — kept" : " — excluded") : " — waiting");
    li.className = i < cursor ? (r.keep ? "kept" : "excluded") : "";
    $("tokens").append(li);
    if (i < cursor && r.keep) result.push(r.word);
  });
  $("result").textContent = repr(result);
  $("step").disabled = !prepared || cursor >= rows.length;
  $("run").disabled = !prepared || cursor >= rows.length;
}
function prepare() {
  const mode = $("mode").value;
  const words =
    mode !== "provided" ? [] : $("filter").value.split(/\s+/).filter(Boolean);
  const arg =
    mode === "omitted"
      ? "None"
      : words.length
        ? "{" + words.map(JSON.stringify).join(", ") + "}"
        : "set()";
  const string = JSON.stringify($("sentence").value);
  $("call").textContent =
    mode === "omitted"
      ? `extract_and_filter_words(${string})`
      : $("order").value === "reversed"
        ? `extract_and_filter_words(words_to_include=${arg}, string=${string})`
        : `extract_and_filter_words(${string}, words_to_include=${arg})`;
  $("binding").textContent =
    `words_to_include = ${arg}. ` +
    (mode === "omitted"
      ? "Default None → empty set → keep all words."
      : words.length
        ? "Keep words found in this set."
        : "Empty set → keep all words in this reference.");
  rows = filterTrace($("sentence").value, mode, $("filter").value);
  cursor = 0;
  prepared = true;
  $("status").textContent =
    "Call prepared. Your prediction stays above; process the words to check it.";
  render();
}
$("prepare").onclick = prepare;
$("step").onclick = () => {
  cursor++;
  render();
  $("status").textContent = `Processed ${cursor} of ${rows.length} words.`;
};
$("run").onclick = () => {
  cursor = rows.length;
  render();
  $("status").textContent = "Function returned. Compare with your prediction.";
};
for (const id of ["sentence", "filter", "mode", "order"])
  $(id).addEventListener("input", () => {
    prepared = false;
    $("filter").disabled = $("mode").value !== "provided";
    $("status").textContent = "Inputs changed. Prepare a new call.";
    render();
  });
$("filter").disabled = true;
prepare();
