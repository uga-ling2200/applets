// Explicit simulations of the course reference implementations.
export function extractWords(s) {
  return s
    .toLowerCase()
    .split(" ")
    .map((w) =>
      w.replace(/^[.!?'",;:()~#$%&*\-/]+|[.!?'",;:()~#$%&*\-/]+$/g, ""),
    )
    .filter(Boolean);
}
export function filterTrace(string, mode, filter) {
  const words = extractWords(string),
    set = new Set(filter.split(/\s+/).filter(Boolean));
  const active = mode === "provided" && set.size > 0;
  return words.map((word) => ({ word, keep: !active || set.has(word) }));
}
export function fileLines(s) {
  s = s.replace(/\r\n?/g, "\n");
  if (!s) return [];
  const a = s.split("\n");
  if (a.at(-1) === "") a.pop();
  return a.map(
    (line, i) => line + (i < a.length - 1 || s.endsWith("\n") ? "\n" : ""),
  );
}
export function fileTrace(text, n, program = "head") {
  const lines = fileLines(text),
    steps = [
      {
        action: "Open the file",
        position: 0,
        output: [],
        line: null,
        closed: false,
      },
    ];
  let pos = 0,
    out = [],
    state = {line: null};
  const add = (action, extra = {}) => {
    state = {...state, ...extra};
    steps.push({action, position: pos, output: [...out], closed: false, ...state, error: extra.error || false});
  };
  const read = () => {
    if (pos >= lines.length) {
      add("StopIteration: no unread line remains", { error: true, exception: "StopIteration" });
      return null;
    }
    const raw = lines[pos++];
    add("next(in_file) returns " + JSON.stringify(raw), { returned: raw });
    return raw;
  };
  if (program === "head") {
    for (let i = 0; i < n; i++) {
      add("Loop iteration " + i, { i });
      const raw = read();
      if (raw === null) break;
      const clean = raw.trim();
      add("strip() removes surrounding whitespace", { line: clean, i });
      out.push(clean);
      add("print(line)", { line: clean, i });
    }
  } else if (program === "skip") {
    const first = read();
    if (first !== null) {
      add("Discard the first returned line");
      const second = read();
      if (second !== null) {
        add("Assign the second returned line", {line: second});
        out.push(second.trim());
        add("Print the second returned line");
      }
    }
  } else {
    const first = read();
    if (first !== null) {
      out.push(first.trim());
      add("Print the first returned line");
      while (pos < lines.length) {
        const raw = lines[pos++];
        add("for line in in_file reads the next line", { line: raw });
        out.push(raw.trim());
        add("Print the loop line");
      }
      add("The for loop stops normally at end of file");
    }
  }
  add("Exit with: file closed", { closed: true });
  return steps;
}
