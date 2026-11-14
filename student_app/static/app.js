// Santolina student page. Plain JavaScript, no libraries: the board has no internet.
// The visit token lives only in memory, so every new page load asks for the code again.
"use strict";

const app = document.getElementById("app");
let S = {};            // strings of the current language
let info = {};         // board name, professor mode, languages, address
let token = null;
let lang = "cat";
let teacher = false;

// ---------------------------------------------------------------- helpers
function h(tag, attrs, ...children) {
  const el = document.createElement(tag);
  for (const [k, v] of Object.entries(attrs || {})) {
    if (v === null || v === undefined || v === false) continue;
    if (k.startsWith("on")) el.addEventListener(k.slice(2), v);
    else if (k === "class") el.className = v;
    else el.setAttribute(k, v === true ? "" : v);
  }
  for (const c of children.flat()) {
    if (c === null || c === undefined || c === false) continue;
    el.append(c instanceof Node ? c : document.createTextNode(String(c)));
  }
  return el;
}
const t = (key, vars) => (S[key] || key).replace(/\{(\w+)\}/g, (_, k) => (vars && k in vars ? vars[k] : ""));
const sleep = (ms) => new Promise((r) => setTimeout(r, ms));

async function api(path, body) {
  const opts = { headers: { "Content-Type": "application/json" } };
  if (token) opts.headers["X-Session"] = token;
  if (body !== undefined) { opts.method = "POST"; opts.body = JSON.stringify(body); }
  const res = await fetch("/api/" + path, opts);
  const data = await res.json().catch(() => ({}));
  if (res.status === 401) { token = null; showLogin(t("session_ended")); throw new Error("expired"); }
  if (!res.ok) throw new Error(data.error || "error");
  return data;
}
function event(type, extra) {
  if (!token) return;
  fetch("/api/event", {
    method: "POST", keepalive: true,
    headers: { "Content-Type": "application/json", "X-Session": token },
    body: JSON.stringify({ type, ...(extra || {}) }),
  }).catch(() => {});
}
async function waitReply(ticket) {
  for (let i = 0; i < 300; i++) {
    const r = await api("reply?ticket=" + encodeURIComponent(ticket));
    if (r.status === "done") return r.result;
    if (r.status === "error" || r.status === "unknown") throw new Error(r.error || "error");
    await sleep(1000);
  }
  throw new Error("timeout");
}
async function loadStrings(l) {
  lang = l;
  S = await api("strings?lang=" + l);
  document.documentElement.lang = { cat: "ca", eng: "en", esp: "es" }[l] || "ca";
}
function go(hash) { if (location.hash === hash) route(); else location.hash = hash; }
function topbar(backTo) {
  return h("div", { class: "topbar" },
    backTo ? h("button", { class: "link", onclick: () => go(backTo) }, "← " + t("back"))
           : h("span", { class: "who" }, teacher ? "👩‍🏫" : "🎓"),
    h("button", { class: "link", onclick: logout }, t("not_you")));
}
function statusChip(status) {
  if (!status) return null;
  return h("span", { class: "chip " + status }, t("status_" + status));
}
function showError(e) {
  if (e && e.message === "expired") return;
  alert(t("error"));
}

// ---------------------------------------------------------------- login
function langButtons(onchange) {
  return h("div", { class: "langs" }, Object.entries(info.languages || {}).map(([code, name]) =>
    h("button", { class: code === lang ? "on" : "", onclick: async () => {
      await loadStrings(code); if (token) event("language_changed", { language: code }); onchange();
    } }, name)));
}
function showLogin(message) {
  history.replaceState(null, "", location.pathname);
  const input = h("input", { class: "code-input", maxlength: "12", autocomplete: "off",
    autocapitalize: "characters", spellcheck: "false", inputmode: "text", placeholder: t("code_placeholder") });
  const err = h("p", { class: "error" }, message || "");
  const start = async (asTeacher) => {
    err.textContent = "";
    try {
      const r = await fetch("/api/login", { method: "POST", headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ code: input.value, teacher: !!asTeacher, language: lang,
          client_ts: new Date().toISOString() }) });
      const data = await r.json();
      if (!r.ok) { err.textContent = t("bad_code"); input.select(); return; }
      token = data.token; teacher = data.teacher;
      go("#home");
    } catch (e) { err.textContent = t("error"); }
  };
  input.addEventListener("keydown", (e) => { if (e.key === "Enter") start(false); });
  app.replaceChildren(h("div", { class: "login" },
    info.board_name ? h("p", { class: "muted" }, "🎓 " + info.board_name) : null,
    h("h1", {}, t("welcome_title")),
    h("p", {}, t("welcome_text")),
    input,
    h("button", { class: "btn primary block", onclick: () => start(false) }, t("start")),
    err,
    info.professor ? h("button", { class: "btn block", onclick: () => start(true) }, t("teacher_entry")) : null,
    langButtons(() => showLogin(message)),
    info.address ? h("div", { class: "banner small" },
      h("p", {}, t("data_hint")),
      h("p", {}, t("address_hint", { address: info.address })),
      h("a", { class: "btn block", href: info.address, target: "_blank", rel: "noopener" }, t("open_in_browser"))) : null,
  ));
  setTimeout(() => input.focus(), 50);
}
async function logout() {
  try { await api("logout", {}); } catch (e) { /* ended anyway */ }
  token = null; showLogin();
}

// ---------------------------------------------------------------- home
async function showHome() {
  event("view_opened", { view: "home" });
  const d = await api("home");
  const tile = (icon, label, sub, onclick, badge, cls) =>
    h("button", { class: "tile " + (cls || ""), onclick },
      h("span", { class: "icon" }, icon),
      h("span", {}, h("div", { class: "label" }, label), sub ? h("div", { class: "sub" }, sub) : null),
      badge ? h("span", { class: "badge" }, badge) : null);
  const hw = d.homework_pending
    ? t("homework_pending", { n: d.homework_pending }) + (d.homework_next_due ? " · " + t("due", { date: d.homework_next_due }) : "")
    : t("homework_none");
  app.replaceChildren(
    topbar(null),
    teacher ? h("div", { class: "banner" }, t("teacher_banner")) : null,
    h("h1", {}, t("home_title")),
    d.exercises === 0 ? h("p", { class: "muted" }, t("no_exercises")) : null,
    h("div", { class: "tiles" },
      d.continue ? tile("▶", t("continue"), d.continue.title, () => openExercise(d.continue.key, d.continue.mode, d.continue.assignment_id), null, "continue") : null,
      tile("📚", t("homework"), hw, () => go("#homework"), d.homework_pending || null),
      tile("🧩", t("practice"), t("practice_sub"), () => go("#practice")),
      tile("💬", t("free"), t("free_sub"), () => go("#free"))),
  );
}

// ---------------------------------------------------------------- lists
function exerciseRow(x, onclick) {
  return h("button", { class: "row", onclick },
    h("span", { class: "title" }, x.title),
    x.level !== null && x.level !== undefined ? h("span", { class: "chip" }, t("level", { level: x.level })) : null,
    statusChip(x.status));
}
async function showHomework() {
  event("view_opened", { view: "homework" });
  const list = await api("homework");
  app.replaceChildren(topbar("#home"), h("h1", {}, t("homework")),
    list.length ? null : h("p", { class: "muted" }, t("homework_none")),
    list.map((a) => h("div", { class: "card" },
      h("h2", {}, a.title),
      a.due ? h("p", { class: "muted small" }, t("due", { date: a.due })) : null,
      h("div", { class: "list" }, a.exercises.map((x) =>
        exerciseRow(x, () => openExercise(x.key, "homework", a.assignment_id)))))));
}
async function showPractice() {
  event("view_opened", { view: "practice" });
  const topics = await api("practice");
  app.replaceChildren(topbar("#home"), h("h1", {}, t("practice")),
    topics.length ? null : h("p", { class: "muted" }, t("no_exercises")),
    topics.map((g, i) => h("details", { class: "topic", open: topics.length === 1 || i === 0 },
      h("summary", {}, h("span", {}, g.topic), h("span", { class: "muted" }, `${g.done}/${g.exercises.length}`)),
      h("div", { class: "list" }, g.exercises.map((x) => exerciseRow(x, () => openExercise(x.key, "practice")))))));
}

// ---------------------------------------------------------------- an exercise card
// Used on the exercise screen and inside the free-mode thread.
function exerciseCard(ex, hooks) {
  const feedback = h("div", { class: "feedback" });
  const state = ex.state;
  const buttons = {};
  const solutionBtn = h("button", { class: "btn", onclick: () => askSolution() }, "💡 " + t("solution"));
  const clueBtn = h("button", { class: "btn", onclick: () => askClue() }, "🔎 " + t("clue"));
  const refresh = () => {
    for (const [letter, b] of Object.entries(buttons)) {
      b.classList.toggle("wrong", state.wrong.includes(letter));
      b.disabled = state.solved || state.wrong.includes(letter);
    }
    solutionBtn.hidden = !(state.can_show_solution && !state.solution_shown) && !teacher;
    clueBtn.hidden = state.solved;
  };
  async function choose(letter) {
    try {
      const r = await api("answer", { key: ex.key, answer: letter });
      Object.assign(state, r.state);
      if (r.correct) {
        buttons[letter].classList.add("right");
        feedback.className = "feedback ok";
        feedback.textContent = t("correct") + (r.counts ? "" : " " + t("with_help_note"));
      } else {
        feedback.className = "feedback bad";
        feedback.textContent = t("wrong");
      }
      refresh();
      if (hooks.onAnswer) hooks.onAnswer(r);
    } catch (e) { showError(e); }
  }
  async function askClue() {
    try {
      const { ticket } = await api("clue", { key: ex.key });
      hooks.thread.reply(ticket, "🔎 " + t("clue"));
    } catch (e) { showError(e); }
  }
  async function askSolution() {
    try {
      const { ticket } = await api("solution", { key: ex.key });
      state.solution_shown = true; refresh();
      hooks.thread.reply(ticket, "💡 " + t("solution"), (r) => {
        if (r.answer && buttons[r.answer]) buttons[r.answer].classList.add("answer");
      });
    } catch (e) { showError(e); }
  }
  const options = Object.entries(ex.options || {}).map(([letter, text]) => {
    const b = h("button", { class: "option" + (teacher && ex.answer === letter ? " answer" : ""), onclick: () => choose(letter) },
      h("span", { class: "letter" }, letter), h("span", {}, text));
    buttons[letter] = b;
    return b;
  });
  const card = h("div", { class: "card exercise" },
    h("div", { class: "meta" }, [ex.pack_title, ex.topic, ex.level !== null ? t("level", { level: ex.level }) : null].filter(Boolean).join(" · ")),
    h("div", { class: "prompt" }, ex.prompt),
    h("div", { class: "images" }, ex.images.map((src) => h("img", { src, alt: "", loading: "lazy", onclick: () => zoom(src) }))),
    h("div", { class: "options" }, options),
    teacher && ex.answer ? h("p", { class: "muted small" }, t("answer_is", { answer: ex.answer })) : null,
    feedback,
    h("div", { class: "helpers" }, clueBtn, solutionBtn));
  refresh();
  if (state.solved) { feedback.className = "feedback ok"; feedback.textContent = t("correct"); }
  return card;
}
function zoom(src) {
  const z = document.getElementById("zoom");
  z.querySelector("img").src = src; z.hidden = false;
  z.onclick = () => { z.hidden = true; };
}

// ---------------------------------------------------------------- chat thread + composer
function makeThread(container) {
  function add(cls, who, text) {
    const m = h("div", { class: "msg " + cls }, h("span", { class: "who" }, who), text);
    container.append(m);
    m.scrollIntoView({ behavior: "smooth", block: "end" });
    return m;
  }
  return {
    me: (text) => add("me", t("you"), text),
    bot: (text) => add("bot", t("copilot"), text),
    node: (n) => { container.append(n); n.scrollIntoView({ behavior: "smooth", block: "start" }); },
    async reply(ticket, label, after) {
      if (label) add("me", t("you"), label);
      const wait = add("bot thinking", t("copilot"), t("thinking"));
      try {
        const r = await waitReply(ticket);
        wait.remove();
        const m = add("bot", t("copilot"), r.text);
        if (r.answer) m.append(h("p", {}, h("strong", {}, t("solution_answer", { answer: r.answer }))));
        for (const s of r.suggestions || []) {
          m.append(h("button", { class: "row suggest", onclick: () => this.onSuggest && this.onSuggest(s.key) },
            h("span", { class: "title" }, "➡ " + t("try_this") + ": " + s.title)));
        }
        if (after) after(r);
      } catch (e) { wait.remove(); if (e.message !== "expired") add("bot", t("copilot"), t("error")); }
    },
  };
}
function composer(thread, placeholder, getKey) {
  let photo = null;
  const attached = h("div", { class: "attached", hidden: true });
  const area = h("textarea", { rows: "1", placeholder });
  area.addEventListener("input", () => { area.style.height = "auto"; area.style.height = area.scrollHeight + "px"; });
  const file = h("input", { type: "file", accept: "image/*", capture: "environment", hidden: true,
    onchange: async () => {
      if (!file.files[0]) return;
      photo = await shrink(file.files[0]);
      attached.hidden = false; attached.textContent = "📷 " + t("photo_attached");
    } });
  async function send() {
    const text = area.value.trim();
    if (!text && !photo) return;
    area.value = ""; area.style.height = "auto";
    const body = { key: getKey(), text };
    if (photo) { body.photo_b64 = photo.b64; body.photo_type = photo.type; }
    photo = null; attached.hidden = true;
    thread.me(text || "📷");
    try { const { ticket } = await api("ask", body); thread.reply(ticket); } catch (e) { showError(e); }
  }
  area.addEventListener("keydown", (e) => { if (e.key === "Enter" && !e.shiftKey) { e.preventDefault(); send(); } });
  return h("div", { class: "composer" }, attached,
    h("div", { class: "inner" },
      h("button", { class: "icon-btn", title: t("photo"), "aria-label": t("photo"), onclick: () => file.click() }, "📷"),
      file, area,
      h("button", { class: "icon-btn send", title: t("send"), "aria-label": t("send"), onclick: send }, "➤")));
}
// Downscale a photo on the phone before sending: smaller upload, same use for the copilot.
function shrink(blob, max = 1280) {
  return new Promise((resolve, reject) => {
    const img = new Image();
    img.onload = () => {
      const scale = Math.min(1, max / Math.max(img.width, img.height));
      const c = document.createElement("canvas");
      c.width = Math.round(img.width * scale); c.height = Math.round(img.height * scale);
      c.getContext("2d").drawImage(img, 0, 0, c.width, c.height);
      const url = c.toDataURL("image/jpeg", 0.8);
      URL.revokeObjectURL(img.src);
      resolve({ b64: url.split(",")[1], type: "image/jpeg" });
    };
    img.onerror = reject;
    img.src = URL.createObjectURL(blob);
  });
}

// ---------------------------------------------------------------- exercise screen
let currentExercise = null;
function openExercise(key, mode, assignmentId, reason) {
  currentExercise = { key, mode, assignmentId, reason };
  go("#exercise");
}
async function showExercise() {
  if (!currentExercise) return go("#home");
  const { key, mode, assignmentId, reason } = currentExercise;
  event("view_opened", { view: "exercise" });
  const q = new URLSearchParams({ key, mode });
  if (assignmentId) q.set("assignment_id", assignmentId);
  if (reason) q.set("path_reason", reason);
  const ex = await api("exercise?" + q);
  const chat = h("div", { class: "thread" });
  const thread = makeThread(chat);
  thread.onSuggest = (k) => openExercise(k, mode, null, "suggested");
  app.replaceChildren(
    topbar(mode === "homework" ? "#homework" : "#practice"),
    teacher ? h("div", { class: "banner" }, t("teacher_banner")) : null,
    exerciseCard(ex, { thread }),
    chat,
    composer(thread, t("ask_about"), () => ex.key));
}

// ---------------------------------------------------------------- free mode
let freeThread = null;
async function showFree() {
  event("view_opened", { view: "free" });
  const box = h("div", { class: "thread" });
  const thread = makeThread(box);
  let current = null;
  freeThread = thread;
  async function show(promise) {
    try {
      const ex = await promise;
      current = ex.key;
      thread.node(exerciseCard(ex, { thread }));
    } catch (e) { if (e.message === "no exercises") thread.bot(t("no_exercises")); else showError(e); }
  }
  thread.onSuggest = (k) => show(api("exercise?" + new URLSearchParams({ key: k, mode: "free", path_reason: "suggested" })));
  app.replaceChildren(
    topbar("#home"),
    teacher ? h("div", { class: "banner" }, t("teacher_banner")) : null,
    h("h1", {}, t("free")),
    h("div", { class: "msg bot" }, h("span", { class: "who" }, t("copilot")), t("free_intro")),
    box,
    h("button", { class: "btn primary free-next", onclick: () => show(api("free/next", {})) }, "🎲 " + t("next_problem")),
    composer(thread, t("ask_placeholder"), () => current));
  show(api("free/next", {}));
}

// ---------------------------------------------------------------- routing
async function route() {
  if (!token) return showLogin();
  const view = location.hash.slice(1) || "home";
  try {
    if (view === "homework") await showHomework();
    else if (view === "practice") await showPractice();
    else if (view === "exercise") await showExercise();
    else if (view === "free") await showFree();
    else await showHome();
    window.scrollTo(0, 0);
  } catch (e) { showError(e); }
}
window.addEventListener("hashchange", route);
document.addEventListener("visibilitychange", () => event(document.hidden ? "page_hidden" : "page_visible"));

(async function start() {
  try { info = await api("info"); } catch (e) { info = {}; }
  await loadStrings("cat");  // Catalan by default; the student can switch on the login screen
  showLogin();
})();
