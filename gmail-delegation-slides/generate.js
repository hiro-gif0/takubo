const pptxgen = require("pptxgenjs");

// ---------- palette ----------
const NAVY = "1C2E4A";
const NAVY_DEEP = "12213A";
const ICE = "DCE7F5";
const ICE_MID = "B9CCE8";
const WHITE = "FFFFFF";
const INK = "1F2430";
const SUB = "5B6577";
const WARN = "A6480E";
const WARN_BG = "FDF1E6";
const GOOD_BG = "E7EEF8";
const FONT = "IPAGothic";

const W = 10, H = 5.625;

function newPres() {
  const p = new pptxgen();
  p.defineLayout({ name: "SOCIAL16x9", width: W, height: H });
  p.layout = "SOCIAL16x9";
  return p;
}

// fresh shadow object every call (pptxgenjs mutates shadow objects in place)
function softShadow(opts = {}) {
  return {
    type: "outer", color: "132038", opacity: opts.opacity != null ? opts.opacity : 0.22,
    blur: opts.blur != null ? opts.blur : 7, offset: opts.offset != null ? opts.offset : 2.5,
    angle: opts.angle != null ? opts.angle : 90,
  };
}

// large, very faint circle used as quiet texture on dark slides (not a stripe/gradient)
function bgCircle(s, cx, cy, r, opts = {}) {
  s.addShape("ellipse", {
    x: cx - r, y: cy - r, w: r * 2, h: r * 2,
    fill: { type: "none" },
    line: { color: opts.color || "2A4568", width: opts.width || 1.25, transparency: opts.transparency != null ? opts.transparency : 0 },
  });
}

// an icon (emoji) centered in a colored circle badge — the deck's recurring icon motif
function iconCircle(s, x, y, d, icon, opts = {}) {
  s.addShape("ellipse", { x, y, w: d, h: d, fill: { color: opts.bg || ICE }, line: opts.border ? { color: opts.border, width: 1.25 } : { type: "none" }, shadow: opts.shadow ? softShadow({ opacity: 0.14, blur: 5, offset: 1.5 }) : undefined });
  s.addText(icon, { x, y, w: d, h: d, fontFace: "Noto Color Emoji", fontSize: opts.size || d * 34, align: "center", valign: "middle", margin: 0 });
}

// small "not allowed" badge (red circle + white slash) pinned to the corner of an icon circle
function crossBadge(s, x, y, d) {
  s.addShape("ellipse", { x, y, w: d, h: d, fill: { color: WARN }, line: { color: "FFFFFF", width: 1.5 } });
  s.addText("×", { x, y, w: d, h: d, fontFace: FONT, fontSize: d * 44, bold: true, color: "FFFFFF", align: "center", valign: "middle", margin: 0 });
}

function baseSlide(pres, opts = {}) {
  const s = pres.addSlide();
  s.background = { color: opts.dark ? NAVY_DEEP : WHITE };
  return s;
}

function pageNum(s, n, total, dark) {
  s.addText(`${n} / ${total}`, {
    x: W - 1.0, y: H - 0.38, w: 0.8, h: 0.3,
    fontFace: FONT, fontSize: 9, color: dark ? "8FA2C4" : "9AA3B2",
    align: "right", margin: 0,
  });
}

function kicker(s, text, dark) {
  s.addText(text, {
    x: 0.55, y: 0.4, w: 6, h: 0.4,
    fontFace: FONT, fontSize: 13, bold: true,
    color: dark ? ICE_MID : NAVY,
    charSpacing: 1, margin: 0,
  });
}

function title(s, text, opts = {}) {
  s.addText(text, {
    x: 0.55, y: opts.y || 0.72, w: opts.w || 8.9, h: opts.h || 0.75,
    fontFace: FONT, fontSize: opts.size || 30, bold: true,
    color: opts.dark ? WHITE : NAVY_DEEP, margin: 0,
    align: opts.align || "left",
  });
}

function personBox(s, x, y, w, h, label) {
  s.addShape("roundRect", {
    x, y, w, h, rectRadius: 0.08,
    fill: { color: ICE }, line: { color: ICE_MID, width: 1 }, shadow: softShadow({ opacity: 0.12, blur: 4, offset: 1.5 }),
  });
  s.addText(label, {
    x: x + 0.1, y, w: w - 0.2, h, fontFace: FONT, fontSize: 12, bold: true,
    color: NAVY_DEEP, align: "left", valign: "middle", margin: 0,
  });
}

// three items fan in to one target box (used for "delegation" diagram)
function fanIn(pres_or_slide, s, x, y, w, h, items, targetLabel, targetSub) {
  const rowH = 0.62;
  const gap = (h - rowH * 3) / 2;
  const boxW = w * 0.46;
  const busX = x + boxW + 0.35;
  const targetX = busX + 0.3;
  const targetW = x + w - targetX;

  const rowYs = [y, y + rowH + gap, y + (rowH + gap) * 2];
  rowYs.forEach((ry, i) => {
    personBox(s, x, ry, boxW, rowH, items[i]);
    // connector from box to bus
    s.addShape("line", {
      x: x + boxW, y: ry + rowH / 2, w: busX - (x + boxW), h: 0,
      line: { color: ICE_MID, width: 2 },
    });
  });
  // vertical bus line connecting the three connector ends
  s.addShape("line", {
    x: busX, y: rowYs[0] + rowH / 2, w: 0, h: rowYs[2] + rowH / 2 - (rowYs[0] + rowH / 2),
    line: { color: ICE_MID, width: 2 },
  });
  // arrow from bus midpoint to target
  const midY = rowYs[1] + rowH / 2;
  s.addShape("line", {
    x: busX, y: midY, w: targetX - busX, h: 0,
    line: { color: NAVY, width: 2.5, endArrowType: "triangle" },
  });
  // target box
  s.addShape("roundRect", {
    x: targetX, y, w: targetW, h, rectRadius: 0.1,
    fill: { color: NAVY }, line: { type: "none" }, shadow: softShadow({ opacity: 0.28, blur: 9, offset: 3 }),
  });
  s.addText(
    [
      { text: targetLabel, options: { fontSize: 16, bold: true, color: WHITE, breakLine: true } },
      { text: targetSub || "", options: { fontSize: 10.5, color: ICE_MID } },
    ],
    { x: targetX + 0.15, y, w: targetW - 0.3, h, align: "center", valign: "middle", fontFace: FONT, margin: 0 }
  );
}

function calloutBar(s, text, x, y, w, h, opts = {}) {
  const bg = opts.warn ? WARN_BG : NAVY;
  const fg = opts.warn ? WARN : WHITE;
  s.addShape("roundRect", {
    x, y, w, h, rectRadius: 0.08,
    fill: { color: bg }, line: opts.warn ? { color: "EAC79A", width: 1 } : { type: "none" },
    shadow: opts.warn ? undefined : softShadow({ opacity: 0.24, blur: 8, offset: 3 }),
  });
  s.addText(text, {
    x: x + 0.2, y, w: w - 0.4, h, fontFace: FONT, fontSize: opts.size || 16, bold: true,
    color: fg, align: "center", valign: "middle", margin: 0,
  });
}

function footNote(s, text, dark) {
  s.addText(text, {
    x: 0.55, y: H - 0.42, w: 7.6, h: 0.3, fontFace: FONT, fontSize: 8.5,
    color: dark ? "7C8CAE" : "9AA3B2", margin: 0,
  });
}

// ---------- tutorial (screen-mockup) helpers ----------

// draws a browser-window style frame; returns the content area below the top bar
function mockFrame(s, x, y, w, h, addressText) {
  s.addShape("roundRect", { x, y, w, h, rectRadius: 0.05, fill: { color: "FFFFFF" }, line: { color: "CBD2DC", width: 1.25 }, shadow: softShadow({ opacity: 0.2, blur: 10, offset: 3.5 }) });
  const barH = 0.38;
  s.addShape("roundRect", { x, y, w, h: barH, rectRadius: 0.05, fill: { color: "EEF0F3" }, line: { color: "CBD2DC", width: 1.25 } });
  s.addShape("rect", { x, y: y + barH - 0.08, w, h: 0.08, fill: { color: "EEF0F3" }, line: { type: "none" } });
  const dots = ["E0897F", "EFC077", "8DC79A"];
  dots.forEach((c, i) => s.addShape("ellipse", { x: x + 0.16 + i * 0.17, y: y + barH / 2 - 0.045, w: 0.09, h: 0.09, fill: { color: c }, line: { type: "none" } }));
  s.addShape("roundRect", { x: x + 0.65, y: y + 0.06, w: w - 1.3, h: barH - 0.12, rectRadius: 0.08, fill: { color: "FFFFFF" }, line: { color: "D8DCE3", width: 0.75 } });
  s.addText(addressText || "mail.google.com", {
    x: x + 0.65, y: y + 0.06, w: w - 1.3, h: barH - 0.12, fontFace: "Courier New", fontSize: 9,
    color: SUB, align: "center", valign: "middle", margin: 0,
  });
  return { x, y: y + barH, w, h: h - barH };
}

function screenCaption(s, x, y, w) {
  s.addText("画面イメージ（実際の画面とは異なります）", {
    x, y, w, h: 0.24, fontFace: FONT, fontSize: 8.5, italic: true, color: SUB, margin: 0,
  });
}

// a bright, bold outline ring/box to circle the important element (TV-flip style)
function spotlight(s, x, y, w, h, opts = {}) {
  s.addShape(opts.shape || "roundRect", {
    x, y, w, h, rectRadius: opts.radius != null ? opts.radius : 0.08,
    fill: { type: "none" }, line: { color: opts.color || WARN, width: opts.width || 2.75 },
  });
}

// bold "POINT" tag bar, used right under/near the mockup to call out what matters
function pointBar(s, x, y, w, h, text, opts = {}) {
  const bg = opts.bg || WARN;
  s.addShape("roundRect", { x, y, w, h, rectRadius: 0.08, fill: { color: bg }, line: { type: "none" }, shadow: softShadow({ opacity: 0.22, blur: 7, offset: 2.5 }) });
  s.addShape("roundRect", { x: x + 0.15, y: y + h / 2 - 0.145, w: 0.68, h: 0.29, rectRadius: 0.05, fill: { color: "FFFFFF" }, line: { type: "none" } });
  s.addText("POINT", { x: x + 0.15, y: y + h / 2 - 0.145, w: 0.68, h: 0.29, fontFace: FONT, fontSize: 9.5, bold: true, color: bg, align: "center", valign: "middle", margin: 0 });
  s.addText(text, { x: x + 0.98, y, w: w - 1.18, h, fontFace: FONT, fontSize: opts.size || 12.5, bold: true, color: "FFFFFF", valign: "middle", margin: 0 });
}

// small pill top-right indicating which part of the 3-part tutorial we're in
function partTag(s, text) {
  s.addShape("roundRect", { x: 6.85, y: 0.42, w: 2.6, h: 0.36, rectRadius: 0.18, fill: { color: ICE }, line: { color: ICE_MID, width: 1 }, shadow: softShadow({ opacity: 0.12, blur: 4, offset: 1.5 }) });
  s.addText(text, { x: 6.85, y: 0.42, w: 2.6, h: 0.36, fontFace: FONT, fontSize: 10, bold: true, color: NAVY_DEEP, align: "center", valign: "middle", margin: 0 });
}

// ================= build =================
const pres = newPres();
const TOTAL = 22;

// ---------- Slide 1: title ----------
{
  const s = baseSlide(pres, { dark: true });
  bgCircle(s, 9.4, 0.3, 2.6, { color: "2A4568" });
  bgCircle(s, 9.7, 0.6, 1.7, { color: "35507A" });
  s.addText("社会部内 説明会資料", {
    x: 0.6, y: 0.55, w: 6, h: 0.4, fontFace: FONT, fontSize: 13, bold: true,
    color: ICE_MID, charSpacing: 1, margin: 0,
  });
  s.addText("社会部Gmailの\n使い方が変わります", {
    x: 0.6, y: 1.5, w: 8.8, h: 1.9, fontFace: FONT, fontSize: 40, bold: true,
    color: WHITE, lineSpacing: 48, margin: 0,
  });
  s.addText("共通パスワードから「代理アクセス」へ", {
    x: 0.6, y: 3.55, w: 8.8, h: 0.55, fontFace: FONT, fontSize: 19, bold: true,
    color: ICE, margin: 0,
  });
  s.addShape("roundRect", {
    x: 0.6, y: 4.25, w: 8.4, h: 0.75, rectRadius: 0.08,
    fill: { color: "223A5E" }, line: { type: "none" },
  });
  s.addText("自分の会社Googleアカウントから、社会部のメールを利用する仕組みです。", {
    x: 0.85, y: 4.25, w: 7.9, h: 0.75, fontFace: FONT, fontSize: 13.5,
    color: WHITE, valign: "middle", margin: 0,
  });
  s.addText("確認日：2026年8月7日（出典：Gmail／Google Workspace 公式ヘルプ）", {
    x: 0.6, y: H - 0.5, w: 8, h: 0.3, fontFace: FONT, fontSize: 9,
    color: "8394B4", margin: 0,
  });
  s.addNotes("今日は、社会部Gmailの使い方が変わるお知らせです。これまで全員で共有していた共通パスワードをやめて、自分の会社Googleアカウントから社会部のメールを使う「代理アクセス」という方式に変わります。仕組みは難しくありません。今日はこの1点だけ持ち帰ってもらえれば十分です。");
}

// ---------- Slide 2: これまでの問題 ----------
{
  const s = baseSlide(pres);
  kicker(s, "01｜これまでの方式");
  title(s, "これまでは「1本の鍵を全員で共有」");

  // diagram: shared password box -> people row
  s.addShape("roundRect", {
    x: 3.1, y: 1.55, w: 3.8, h: 0.55, rectRadius: 0.08,
    fill: { color: NAVY }, line: { type: "none" }, shadow: softShadow({ opacity: 0.24, blur: 7, offset: 2.5 }),
  });
  s.addText("社会部Gmail（共通パスワード）", {
    x: 3.1, y: 1.55, w: 3.8, h: 0.55, fontFace: FONT, fontSize: 13, bold: true,
    color: WHITE, align: "center", valign: "middle", margin: 0,
  });
  s.addShape("line", {
    x: 5, y: 2.1, w: 0, h: 0.28, line: { color: ICE_MID, width: 2, endArrowType: "triangle" },
  });
  const people = ["部長", "次席", "記者A", "記者B", "記者C"];
  const pw = 1.5, pgap = 0.18;
  const totalW = pw * people.length + pgap * (people.length - 1);
  let px = (W - totalW) / 2;
  const peopleY = 2.5;
  people.forEach((label) => {
    s.addShape("roundRect", {
      x: px, y: peopleY, w: pw, h: 0.5, rectRadius: 0.06,
      fill: { color: ICE }, line: { color: ICE_MID, width: 1 }, shadow: softShadow({ opacity: 0.12, blur: 3.5, offset: 1.5 }),
    });
    s.addText(label, {
      x: px, y: peopleY, w: pw, h: 0.5, fontFace: FONT, fontSize: 12, bold: true,
      color: NAVY_DEEP, align: "center", valign: "middle", margin: 0,
    });
    px += pw + pgap;
  });
  s.addText("全員が同じ「メールアドレス＋パスワード」でログインしています", {
    x: 0.55, y: peopleY + 0.62, w: 8.9, h: 0.32, fontFace: FONT, fontSize: 12, italic: true,
    color: SUB, align: "center", margin: 0,
  });

  const problems = [
    "誰かがパスワードを変更すると、全員に影響する",
    "異動のたびに、パスワードの管理が必要になる",
    "全員が同じログイン情報を使い続けることになる",
    "本人確認や、パスワードを忘れたときの対応も複雑になる",
  ];
  let py = peopleY + 1.1;
  problems.forEach((tx) => {
    s.addShape("ellipse", { x: 0.6, y: py + 0.05, w: 0.13, h: 0.13, fill: { color: WARN }, line: { type: "none" } });
    s.addText(tx, {
      x: 0.9, y: py - 0.05, w: 8.4, h: 0.3, fontFace: FONT, fontSize: 12.5,
      color: INK, margin: 0,
    });
    py += 0.33;
  });
  footNote(s, "怖い話ではありません。「人数が増えるほど、鍵の管理が大変になる」という単純な問題です。");
  pageNum(s, 2, TOTAL);
  s.addNotes("これまでは、社会部Gmailに1つの共通パスワードがあり、部長から記者まで全員が同じログイン情報を使っていました。これ自体は長年の運用ですが、誰かがパスワードを変えると全員に影響しますし、異動のたびに管理が必要になります。危険だから今すぐ変えるという話ではなく、人数が増えるほど鍵の管理が大変になるという、単純だけれど大事な問題だと理解してください。");
}

// ---------- Slide 3: 代理アクセスとは？ ----------
{
  const s = baseSlide(pres);
  kicker(s, "02｜代理アクセスとは？");
  title(s, "自分のアカウントで、\n社会部の受信箱を開く仕組み", { size: 27, h: 1.2 });

  fanIn(pres, s, 0.6, 2.15, 8.8, 2.05,
    ["記者Aの会社アカウント", "記者Bの会社アカウント", "記者Cの会社アカウント"],
    "社会部Gmail", "の受信箱"
  );

  calloutBar(s, "社会部Gmailの共通パスワードを、一般部員が知る必要はありません", 0.6, 4.55, 8.8, 0.6, { size: 15 });
  footNote(s, "「代理アクセス」とは：自分の会社アカウントから、社会部のメールボックスを開く仕組みのことです。");
  pageNum(s, 3, TOTAL);
  s.addNotes("ここが今日一番大事なスライドです。「代理アクセス」という言葉だけ聞くと難しそうですが、意味は単純です。自分の会社Googleアカウントで、社会部のメールボックスを開けるようになる、というだけです。記者A、B、Cのように、それぞれ自分のアカウントから入っても、開く先は同じ社会部Gmailです。そして一番大事なのは、社会部Gmailの共通パスワードを、もう覚えなくていいということです。");
}

// ---------- Slide 4: 社員証のたとえ ----------
{
  const s = baseSlide(pres);
  kicker(s, "03｜たとえて言うと");
  title(s, "「社員証」で考えると簡単です");

  const colW = 4.2, colY = 1.85, colH = 2.5;
  const iconD = 1.0;
  // old
  s.addShape("roundRect", { x: 0.55, y: colY, w: colW, h: colH, rectRadius: 0.1, fill: { color: WHITE }, line: { color: "E4E7EC", width: 1 }, shadow: softShadow({ opacity: 0.14, blur: 6, offset: 2 }) });
  s.addText("これまで", { x: 0.55, y: colY + 0.2, w: colW, h: 0.35, align: "center", fontFace: FONT, fontSize: 13, bold: true, color: SUB, margin: 0 });
  iconCircle(s, 0.55 + colW / 2 - iconD / 2, colY + 0.62, iconD, "🔑", { bg: "F2F3F5" });
  s.addText("全員が同じ\nマスターキーを持つ", { x: 0.75, y: colY + 1.75, w: colW - 0.4, h: 0.65, align: "center", fontFace: FONT, fontSize: 14, bold: true, color: INK, margin: 0 });

  // new
  const x2 = 0.55 + colW + 0.5;
  s.addShape("roundRect", { x: x2, y: colY, w: colW, h: colH, rectRadius: 0.1, fill: { color: ICE }, line: { color: NAVY, width: 1.5 }, shadow: softShadow({ opacity: 0.2, blur: 7, offset: 2.5 }) });
  s.addText("これから", { x: x2, y: colY + 0.2, w: colW, h: 0.35, align: "center", fontFace: FONT, fontSize: 13, bold: true, color: NAVY_DEEP, margin: 0 });
  iconCircle(s, x2 + colW / 2 - iconD / 2, colY + 0.62, iconD, "💳", { bg: WHITE });
  s.addText("それぞれ自分の\n社員証を使う", { x: x2 + 0.2, y: colY + 1.75, w: colW - 0.4, h: 0.65, align: "center", fontFace: FONT, fontSize: 14, bold: true, color: NAVY_DEEP, margin: 0 });

  calloutBar(s, "社員証に「社会部メール室に入れる」権限だけが追加されるイメージです", 0.55, colY + colH + 0.25, 8.8, 0.6, { size: 14 });
  footNote(s, "※実際の仕組みはGoogleアカウントの利用権限です。物理的な社員証があるわけではありません。");
  pageNum(s, 4, TOTAL);
  s.addNotes("イメージしやすいように、社員証で例えてみます。これまでは、社会部のメール室に入るための合鍵を全員がコピーして持っているようなものでした。これからは、それぞれが自分の社員証をかざすと、社会部メール室にだけ入れる権限が追加される、というイメージです。実際にはGoogleアカウントの利用権限の話で、物理的な社員証があるわけではありませんが、考え方としてはこれで十分です。");
}

// shared card used by the できる/できない slides: icon in a circle, label, one-line example
function capabilityCard(s, x, y, w, h, icon, label, desc, opts = {}) {
  s.addShape("roundRect", {
    x, y, w, h, rectRadius: 0.1, fill: { color: WHITE }, line: { color: opts.border || "E4E7EC", width: 1 },
    shadow: softShadow({ opacity: 0.14, blur: 6, offset: 2 }),
  });
  const d = 0.8, cx = x + w / 2 - d / 2, cy = y + 0.24;
  iconCircle(s, cx, cy, d, icon, { bg: opts.iconBg || ICE });
  if (opts.cross) crossBadge(s, cx + d - 0.2, cy - 0.08, 0.32);
  s.addText(label, { x: x + 0.08, y: cy + d + 0.1, w: w - 0.16, h: 0.4, fontFace: FONT, fontSize: opts.labelSize || 12.5, bold: true, color: NAVY_DEEP, align: "center", margin: 0 });
  s.addText(desc, { x: x + 0.15, y: cy + d + 0.5, w: w - 0.3, h: h - (cy + d + 0.5 - y) - 0.12, fontFace: FONT, fontSize: 9.3, color: SUB, align: "center", margin: 0 });
}

// ---------- Slide 5: できること（詳細・図解） ----------
{
  const s = baseSlide(pres);
  kicker(s, "04｜できること");
  title(s, "代理アクセスで、記者は何ができる？", { size: 25 });

  const items = [
    { icon: "🔍", label: "読む・検索する", desc: "読者や取材先からの\nメールを確認・検索できる" },
    { icon: "↩️", label: "返信する", desc: "社会部として、\nそのまま返信できる" },
    { icon: "📤", label: "送る", desc: "必要な相手に、新しく\nメールを送れる" },
    { icon: "🗂️", label: "整理する", desc: "不要なメールの削除や\nラベル分けができる" },
  ];
  const cardW = 1.95, cardH = 2.55, gap = 0.25, y0 = 1.65;
  let x = (W - (cardW * items.length + gap * (items.length - 1))) / 2;
  items.forEach((it) => {
    capabilityCard(s, x, y0, cardW, cardH, it.icon, it.label, it.desc, { iconBg: ICE });
    x += cardW + gap;
  });

  calloutBar(s, "ふだんのメール業務は、ほぼそのまま行えます", 0.55, y0 + cardH + 0.22, 8.8, 0.55, { size: 14.5 });
  pageNum(s, 5, TOTAL);
  s.addNotes("代理アクセスでできることを、1つずつ見ていきます。読者や取材先からのメールを読んで検索する、社会部として返信する、新しくメールを送る、不要なメールを削除したり整理したりする。これらは、ふだん自分のGmailで行っている作業とまったく同じ感覚でできます。");
}

// ---------- Slide 6: できないこと（詳細・図解） ----------
{
  const s = baseSlide(pres);
  kicker(s, "05｜できないこと");
  title(s, "代理アクセスで、記者ができないことは？", { size: 24 });

  const items = [
    { icon: "🔑", label: "パスワード変更", desc: "社会部アカウントを\n安全に守るための仕組みです" },
    { icon: "⚙️", label: "アカウント全体の設定変更", desc: "2段階認証など、\n本体の設定は変更できません" },
    { icon: "🧩", label: "他サービスへの自動アクセス", desc: "Gmail以外は、\nそれぞれ別の許可が必要です" },
  ];
  const cardW = 2.6, cardH = 2.55, gap = 0.3, y0 = 1.65;
  let x = (W - (cardW * items.length + gap * (items.length - 1))) / 2;
  items.forEach((it) => {
    capabilityCard(s, x, y0, cardW, cardH, it.icon, it.label, it.desc, { iconBg: WARN_BG, cross: true, labelSize: 12 });
    x += cardW + gap;
  });

  calloutBar(s, "メール業務はできる。でも、アカウントそのものの管理者にはならない。", 0.55, y0 + cardH + 0.22, 8.8, 0.55, { size: 14 });
  pageNum(s, 6, TOTAL);
  s.addNotes("一方で、できないこともあります。社会部アカウントのパスワード変更、2段階認証などGoogleアカウント全体の設定変更、そしてGmail以外のサービスへの自動的なアクセスです。これらはいずれも、アカウント本体の安全を守るための仕組みで、代理人には触れさせない範囲だと考えてください。つまり、メール業務はできるけれど、アカウントそのものの管理者にはならない、ということです。");
}

// ---------- Slide 7: ここから先の流れ ----------
{
  const s = baseSlide(pres);
  kicker(s, "06｜ここから先の流れ");
  title(s, "実際の画面で、3つの場面を見ていきます", { size: 26 });

  const parts = [
    { n: "1", t: "設定編", sub: "管理担当が行う作業", who: "社会部Gmail側で\n利用者を登録する" },
    { n: "2", t: "承認編", sub: "記者が行う作業", who: "届いた招待メールを\n確認して承認する" },
    { n: "3", t: "毎日の使い方編", sub: "記者が行う作業", who: "自分のアカウントから\n社会部Gmailを開く" },
  ];
  const colW = 2.75, gap = 0.35, colY = 1.95, colH = 2.3;
  const totalW = colW * 3 + gap * 2;
  let x = (W - totalW) / 2;
  parts.forEach((p, i) => {
    s.addShape("roundRect", { x, y: colY, w: colW, h: colH, rectRadius: 0.1, fill: { color: i === 0 ? WHITE : ICE }, line: { color: i === 0 ? "E4E7EC" : ICE_MID, width: 1 }, shadow: softShadow({ opacity: 0.15, blur: 6, offset: 2 }) });
    s.addShape("ellipse", { x: x + colW / 2 - 0.28, y: colY + 0.22, w: 0.56, h: 0.56, fill: { color: NAVY }, line: { type: "none" }, shadow: softShadow({ opacity: 0.2, blur: 4, offset: 1.5 }) });
    s.addText(p.n, { x: x + colW / 2 - 0.28, y: colY + 0.22, w: 0.56, h: 0.56, fontFace: FONT, fontSize: 20, bold: true, color: WHITE, align: "center", valign: "middle", margin: 0 });
    s.addText(p.t, { x: x + 0.1, y: colY + 0.9, w: colW - 0.2, h: 0.4, fontFace: FONT, fontSize: 15, bold: true, color: NAVY_DEEP, align: "center", margin: 0 });
    s.addText(p.sub, { x: x + 0.1, y: colY + 1.28, w: colW - 0.2, h: 0.3, fontFace: FONT, fontSize: 10, color: SUB, align: "center", margin: 0 });
    s.addText(p.who, { x: x + 0.15, y: colY + 1.65, w: colW - 0.3, h: 0.6, fontFace: FONT, fontSize: 10.5, color: INK, align: "center", margin: 0 });
    if (i < 2) {
      s.addShape("line", { x: x + colW + 0.04, y: colY + colH / 2, w: gap - 0.08, h: 0, line: { color: SUB, width: 2, endArrowType: "triangle" } });
    }
    x += colW + gap;
  });

  calloutBar(s, "画面のイメージ図を見ながら、1つずつ操作を確認していきます", 0.55, 4.55, 8.8, 0.55, { size: 14 });
  pageNum(s, 7, TOTAL);
  s.addNotes("ここからは、実際の画面のイメージを見ながら、3つの場面を順番に説明します。1つ目は設定編で、管理担当が社会部Gmail側で利用者を登録する作業です。2つ目は承認編で、招待された記者がメールを確認して承認する作業です。3つ目は毎日の使い方編で、実際に自分のアカウントから社会部Gmailを開く操作です。それぞれ、誰がやる作業なのかを意識しながら見てください。");
}

// ---------- Slide 8: 設定編 STEP1 ----------
{
  const s = baseSlide(pres);
  kicker(s, "設定編（管理担当が行う作業） STEP 1 / 3");
  partTag(s, "① 設定編");
  title(s, "社会部Gmailの「設定」を開く", { y: 0.88, size: 24 });

  const F = mockFrame(s, 1.0, 1.5, 8.0, 2.55, "mail.google.com");
  s.addText("Gmail", { x: F.x + 0.25, y: F.y + 0.15, w: 1.3, h: 0.4, fontFace: FONT, fontSize: 16, bold: true, color: NAVY_DEEP, margin: 0 });
  s.addShape("roundRect", { x: F.x + 1.7, y: F.y + 0.2, w: F.w - 3.3, h: 0.34, rectRadius: 0.17, fill: { color: "F1F2F5" }, line: { type: "none" } });
  s.addText("メールを検索", { x: F.x + 1.9, y: F.y + 0.2, w: 2.5, h: 0.34, fontFace: FONT, fontSize: 9.5, color: SUB, valign: "middle", margin: 0 });
  const gx = F.x + F.w - 1.35, gy = F.y + 0.14;
  s.addText("⚙️", { x: gx, y: gy, w: 0.42, h: 0.42, fontFace: "Noto Color Emoji", fontSize: 18, align: "center", valign: "middle", margin: 0 });
  s.addShape("ellipse", { x: F.x + F.w - 0.65, y: F.y + 0.14, w: 0.42, h: 0.42, fill: { color: ICE_MID }, line: { type: "none" } });
  s.addText("社", { x: F.x + F.w - 0.65, y: F.y + 0.14, w: 0.42, h: 0.42, fontFace: FONT, fontSize: 12, bold: true, color: NAVY_DEEP, align: "center", valign: "middle", margin: 0 });
  s.addShape("line", { x: F.x, y: F.y + 0.7, w: F.w, h: 0, line: { color: "E4E7EC", width: 1 } });
  for (let i = 0; i < 3; i++) {
    s.addShape("roundRect", { x: F.x + 0.25, y: F.y + 0.85 + i * 0.42, w: F.w - 0.5, h: 0.3, rectRadius: 0.05, fill: { color: "F5F6F8" }, line: { type: "none" } });
  }
  spotlight(s, gx - 0.1, gy - 0.1, 0.62, 0.62, { shape: "ellipse" });
  screenCaption(s, F.x, F.y + F.h + 0.06, F.w);

  pointBar(s, 1.0, 4.35, 8.0, 0.5, "①ここ（歯車マーク）を押します");
  pageNum(s, 8, TOTAL);
  s.addNotes("設定編の1つ目です。管理担当が、社会部Gmailに自分でログインした状態で、画面右上にある歯車マークを押します。これが設定画面への入り口です。");
}

// ---------- Slide 9: 設定編 STEP2 ----------
{
  const s = baseSlide(pres);
  kicker(s, "設定編（管理担当が行う作業） STEP 2 / 3");
  partTag(s, "① 設定編");
  title(s, "「アカウントとインポート」タブを選ぶ", { y: 0.88, size: 24 });

  const F = mockFrame(s, 1.0, 1.5, 8.0, 2.55, "mail.google.com/settings");
  const tabs = ["全般", "ラベル", "受信トレイ", "アカウントとインポート", "フィルタ"];
  const tabW = F.w / tabs.length;
  let tx = F.x;
  let activeX = tx;
  tabs.forEach((t, i) => {
    const active = t === "アカウントとインポート";
    s.addText(t, {
      x: tx, y: F.y + 0.12, w: tabW, h: 0.34, fontFace: FONT, fontSize: active ? 10.5 : 9.5, bold: active,
      color: active ? NAVY_DEEP : SUB, align: "center", valign: "middle", margin: 0,
    });
    if (active) activeX = tx;
    tx += tabW;
  });
  s.addShape("line", { x: F.x, y: F.y + 0.5, w: F.w, h: 0, line: { color: "E4E7EC", width: 1 } });
  s.addShape("line", { x: activeX + 0.1, y: F.y + 0.49, w: tabW - 0.2, h: 0, line: { color: NAVY, width: 2.5 } });
  s.addText("アカウントにアクセス権を与える", { x: F.x + 0.3, y: F.y + 0.75, w: F.w - 0.6, h: 0.35, fontFace: FONT, fontSize: 12.5, bold: true, color: NAVY_DEEP, margin: 0 });
  s.addText("委任された人が、あなたに代わってメールを読んだり送信したりできるようになります。", {
    x: F.x + 0.3, y: F.y + 1.1, w: F.w - 0.6, h: 0.4, fontFace: FONT, fontSize: 9.5, color: SUB, margin: 0,
  });
  spotlight(s, activeX - 0.08, F.y + 0.08, tabW + 0.16, 0.42, { radius: 0.05 });
  screenCaption(s, F.x, F.y + F.h + 0.06, F.w);

  pointBar(s, 1.0, 4.35, 8.0, 0.5, "②「アカウントとインポート」のタブを選びます");
  pageNum(s, 9, TOTAL);
  s.addNotes("設定画面が開いたら、上に並んでいるタブの中から「アカウントとインポート」を選びます。ここに、メールへのアクセス権を管理する項目があります。");
}

// ---------- Slide 10: 設定編 STEP3 ----------
{
  const s = baseSlide(pres);
  kicker(s, "設定編（管理担当が行う作業） STEP 3 / 3");
  partTag(s, "① 設定編");
  title(s, "「別のアカウントを追加」から追加したい人を入力する", { y: 0.88, size: 21 });

  const F = mockFrame(s, 1.0, 1.5, 8.0, 2.55, "mail.google.com/settings");
  s.addText("アカウントにアクセス権を与える", { x: F.x + 0.3, y: F.y + 0.15, w: F.w - 0.6, h: 0.3, fontFace: FONT, fontSize: 12, bold: true, color: NAVY_DEEP, margin: 0 });
  s.addShape("roundRect", { x: F.x + 0.3, y: F.y + 0.5, w: 2.4, h: 0.4, rectRadius: 0.06, fill: { color: ICE }, line: { color: NAVY, width: 1.25 } });
  s.addText("＋ 別のアカウントを追加", { x: F.x + 0.3, y: F.y + 0.5, w: 2.4, h: 0.4, fontFace: FONT, fontSize: 10.5, bold: true, color: NAVY_DEEP, align: "center", valign: "middle", margin: 0 });
  s.addShape("line", { x: F.x + 0.3, y: F.y + 1.08, w: F.w - 0.6, h: 0, line: { color: "E4E7EC", width: 1 } });
  s.addText("追加するメールアドレス", { x: F.x + 0.3, y: F.y + 1.22, w: 2.2, h: 0.32, fontFace: FONT, fontSize: 9.5, color: SUB, valign: "middle", margin: 0 });
  s.addShape("roundRect", { x: F.x + 2.5, y: F.y + 1.18, w: 2.9, h: 0.4, rectRadius: 0.05, fill: { color: "FFFFFF" }, line: { color: "CBD2DC", width: 1 } });
  s.addText("kisha-a@example.co.jp", { x: F.x + 2.6, y: F.y + 1.18, w: 2.7, h: 0.4, fontFace: "Courier New", fontSize: 9.5, color: INK, valign: "middle", margin: 0 });
  s.addShape("roundRect", { x: F.x + 5.55, y: F.y + 1.18, w: 1.7, h: 0.4, rectRadius: 0.05, fill: { color: NAVY }, line: { type: "none" } });
  s.addText("次のステップへ", { x: F.x + 5.55, y: F.y + 1.18, w: 1.7, h: 0.4, fontFace: FONT, fontSize: 9.5, bold: true, color: "FFFFFF", align: "center", valign: "middle", margin: 0 });
  spotlight(s, F.x + 2.45, F.y + 1.13, 4.9, 0.5, { radius: 0.06 });
  screenCaption(s, F.x, F.y + F.h + 0.06, F.w);

  pointBar(s, 1.0, 4.35, 8.0, 0.5, "③メールアドレスを入力し、「次のステップへ」で招待を送ります");
  footNote(s, "※画面内のメールアドレスは例です。実際は追加したい記者のメールアドレスを入力します。");
  pageNum(s, 10, TOTAL);
  s.addNotes("「別のアカウントを追加」を押すと、メールアドレスを入力する欄が出てきます。追加したい記者のメールアドレスを入力して、「次のステップへ」を押すと、相手に招待メールが送られます。この操作は管理担当だけが行うもので、一般部員が自分で行う必要はありません。");
}

// ---------- Slide 11: 承認編 STEP1 ----------
{
  const s = baseSlide(pres);
  kicker(s, "承認編（記者が行う作業） STEP 1 / 3");
  partTag(s, "② 承認編");
  title(s, "自分のGmailに、招待メールが届く", { y: 0.88, size: 24 });

  const F = mockFrame(s, 1.0, 1.5, 8.0, 2.55, "mail.google.com");
  const rowH = 0.56;
  const rows = [
    { from: "社会部Gmail管理担当 <shakaibu@example.co.jp>", subj: "「メールの委任」の招待が届いています", hot: true },
    { from: "（他のメール）", subj: "（他のメール）", hot: false },
    { from: "（他のメール）", subj: "（他のメール）", hot: false },
  ];
  rows.forEach((r, i) => {
    const ry = F.y + 0.15 + i * (rowH + 0.08);
    s.addShape("roundRect", {
      x: F.x + 0.2, y: ry, w: F.w - 0.4, h: rowH, rectRadius: 0.05,
      fill: { color: r.hot ? ICE : "F7F8FA" }, line: { color: r.hot ? NAVY : "E4E7EC", width: r.hot ? 1.25 : 1 },
    });
    s.addText(r.from, { x: F.x + 0.4, y: ry + 0.06, w: F.w - 0.8, h: 0.26, fontFace: FONT, fontSize: r.hot ? 10.5 : 9.5, bold: r.hot, color: r.hot ? NAVY_DEEP : "B7BCC6", margin: 0 });
    s.addText(r.subj, { x: F.x + 0.4, y: ry + 0.3, w: F.w - 0.8, h: 0.24, fontFace: FONT, fontSize: r.hot ? 10 : 9, color: r.hot ? INK : "C7CBD3", margin: 0 });
    if (r.hot) spotlight(s, F.x + 0.15, ry - 0.05, F.w - 0.3, rowH + 0.1, { radius: 0.06 });
  });
  screenCaption(s, F.x, F.y + F.h + 0.06, F.w);

  pointBar(s, 1.0, 4.35, 8.0, 0.5, "①社会部からの招待メールを、受信箱の中から探します");
  pageNum(s, 11, TOTAL);
  s.addNotes("管理担当が登録を済ませると、招待された記者自身の受信箱に、社会部からの招待メールが届きます。件名には「メールの委任」に関する案内が入っています。");
}

// ---------- Slide 12: 承認編 STEP2 ----------
{
  const s = baseSlide(pres);
  kicker(s, "承認編（記者が行う作業） STEP 2 / 3");
  partTag(s, "② 承認編");
  title(s, "メールを開いて、送信元と内容を確認する", { y: 0.88, size: 24 });

  const F = mockFrame(s, 1.0, 1.5, 8.0, 2.55, "mail.google.com");
  s.addText("件名：「メールの委任」の招待が届いています", { x: F.x + 0.3, y: F.y + 0.12, w: F.w - 0.6, h: 0.3, fontFace: FONT, fontSize: 11.5, bold: true, color: NAVY_DEEP, margin: 0 });
  s.addText("From：社会部Gmail管理担当 <shakaibu@example.co.jp>", { x: F.x + 0.3, y: F.y + 0.44, w: F.w - 0.6, h: 0.26, fontFace: FONT, fontSize: 9.5, color: SUB, margin: 0 });
  s.addShape("line", { x: F.x + 0.3, y: F.y + 0.76, w: F.w - 0.6, h: 0, line: { color: "E4E7EC", width: 1 } });
  s.addText("shakaibu@example.co.jp さんが、自分の代わりにメールを\n読んだり送信したりできる人として、あなたを追加しました。", {
    x: F.x + 0.3, y: F.y + 0.88, w: F.w - 0.6, h: 0.55, fontFace: FONT, fontSize: 10, color: INK, margin: 0,
  });
  s.addShape("roundRect", { x: F.x + 0.3, y: F.y + 1.55, w: 1.9, h: 0.4, rectRadius: 0.06, fill: { color: NAVY }, line: { type: "none" } });
  s.addText("アクセスを確認", { x: F.x + 0.3, y: F.y + 1.55, w: 1.9, h: 0.4, fontFace: FONT, fontSize: 10.5, bold: true, color: "FFFFFF", align: "center", valign: "middle", margin: 0 });
  spotlight(s, F.x + 0.22, F.y + 1.48, 2.05, 0.54, { radius: 0.07 });
  screenCaption(s, F.x, F.y + F.h + 0.06, F.w);

  pointBar(s, 1.0, 4.35, 8.0, 0.5, "②送信元が「shakaibu@example.co.jp」であることを確認します");
  pageNum(s, 12, TOTAL);
  s.addNotes("届いたメールを開いたら、まず送信元が社会部の管理担当（社会部Gmailのアドレス）であることを確認してください。見覚えのない相手からの場合は、絶対に先へ進まず、社会部の管理担当に確認しましょう。内容を確認したら、「アクセスを確認」ボタンを押します。");
}

// ---------- Slide 13: 承認編 STEP3 ----------
{
  const s = baseSlide(pres);
  kicker(s, "承認編（記者が行う作業） STEP 3 / 3");
  partTag(s, "② 承認編");
  title(s, "「確認」を押せば、承認は完了", { y: 0.88, size: 24 });

  const F = mockFrame(s, 1.0, 1.5, 8.0, 2.3, "mail.google.com");
  // dim background list
  for (let i = 0; i < 3; i++) {
    s.addShape("roundRect", { x: F.x + 0.2, y: F.y + 0.15 + i * 0.35, w: F.w - 0.4, h: 0.26, rectRadius: 0.04, fill: { color: "F5F6F8" }, line: { type: "none" } });
  }
  // modal dialog
  const mw = 4.6, mh = 1.55, mx = F.x + (F.w - mw) / 2, my = F.y + 0.35;
  s.addShape("roundRect", { x: mx, y: my, w: mw, h: mh, rectRadius: 0.08, fill: { color: "FFFFFF" }, line: { color: "CBD2DC", width: 1.5 }, shadow: softShadow({ opacity: 0.28, blur: 10, offset: 3 }) });
  s.addText("確認", { x: mx + 0.25, y: my + 0.15, w: mw - 0.5, h: 0.3, fontFace: FONT, fontSize: 12.5, bold: true, color: NAVY_DEEP, margin: 0 });
  s.addText("shakaibu@example.co.jp からのメールへの\nアクセスを許可しますか？", {
    x: mx + 0.25, y: my + 0.48, w: mw - 0.5, h: 0.55, fontFace: FONT, fontSize: 10, color: INK, margin: 0,
  });
  s.addShape("roundRect", { x: mx + mw - 3.1, y: my + mh - 0.55, w: 1.35, h: 0.4, rectRadius: 0.06, fill: { color: "F1F2F5" }, line: { color: "D8DCE3", width: 1 } });
  s.addText("キャンセル", { x: mx + mw - 3.1, y: my + mh - 0.55, w: 1.35, h: 0.4, fontFace: FONT, fontSize: 10, color: SUB, align: "center", valign: "middle", margin: 0 });
  s.addShape("roundRect", { x: mx + mw - 1.6, y: my + mh - 0.55, w: 1.35, h: 0.4, rectRadius: 0.06, fill: { color: NAVY }, line: { type: "none" } });
  s.addText("確認", { x: mx + mw - 1.6, y: my + mh - 0.55, w: 1.35, h: 0.4, fontFace: FONT, fontSize: 10.5, bold: true, color: "FFFFFF", align: "center", valign: "middle", margin: 0 });
  spotlight(s, mx + mw - 1.68, my + mh - 0.63, 1.5, 0.54, { radius: 0.07 });
  screenCaption(s, F.x, F.y + F.h + 0.06, F.w);

  pointBar(s, 1.0, 4.15, 8.0, 0.5, "③「確認」を押せば、承認は完了です");
  footNote(s, "反映まで時間がかかる場合があります。すぐに表示されなくても、時間を置いて確認してください。");
  pageNum(s, 13, TOTAL);
  s.addNotes("最後に確認ダイアログが出るので、内容に間違いなければ「確認」を押します。これで承認は完了です。承認してすぐに使えないこともあるので、少し時間を置いてから次の使い方編を試してみてください。");
}

// ---------- Slide 14: 使い方編 STEP1 ----------
{
  const s = baseSlide(pres);
  kicker(s, "毎日の使い方編（記者が行う作業） STEP 1 / 4");
  partTag(s, "③ 使い方編");
  title(s, "①自分の会社Gmailを開く", { y: 0.88, size: 24 });

  const F = mockFrame(s, 1.0, 1.5, 8.0, 2.55, "mail.google.com");
  s.addText("Gmail", { x: F.x + 0.25, y: F.y + 0.15, w: 1.3, h: 0.4, fontFace: FONT, fontSize: 16, bold: true, color: NAVY_DEEP, margin: 0 });
  s.addShape("ellipse", { x: F.x + F.w - 0.65, y: F.y + 0.14, w: 0.42, h: 0.42, fill: { color: ICE_MID }, line: { type: "none" } });
  s.addText("記", { x: F.x + F.w - 0.65, y: F.y + 0.14, w: 0.42, h: 0.42, fontFace: FONT, fontSize: 12, bold: true, color: NAVY_DEEP, align: "center", valign: "middle", margin: 0 });
  s.addShape("line", { x: F.x, y: F.y + 0.7, w: F.w, h: 0, line: { color: "E4E7EC", width: 1 } });
  const subjects = ["（原稿の確認について）", "（明日の取材予定）", "（総務からのお知らせ）"];
  subjects.forEach((t, i) => {
    s.addShape("roundRect", { x: F.x + 0.25, y: F.y + 0.85 + i * 0.42, w: F.w - 0.5, h: 0.3, rectRadius: 0.05, fill: { color: "F5F6F8" }, line: { type: "none" } });
    s.addText(t, { x: F.x + 0.45, y: F.y + 0.85 + i * 0.42, w: F.w - 0.9, h: 0.3, fontFace: FONT, fontSize: 9, color: SUB, valign: "middle", margin: 0 });
  });
  screenCaption(s, F.x, F.y + F.h + 0.06, F.w);

  pointBar(s, 1.0, 4.35, 8.0, 0.5, "①いつも通り、自分の会社Gmailを開きます", { bg: NAVY });
  pageNum(s, 14, TOTAL);
  s.addNotes("毎日の使い方編です。まずはいつも通り、自分の会社Googleアカウントで自分のGmailを開きます。特別な操作は何もありません。");
}

// ---------- Slide 15: 使い方編 STEP2 ----------
{
  const s = baseSlide(pres);
  kicker(s, "毎日の使い方編（記者が行う作業） STEP 2 / 4");
  partTag(s, "③ 使い方編");
  title(s, "②右上のプロフィール画像を押す", { y: 0.88, size: 24 });

  const F = mockFrame(s, 1.0, 1.5, 8.0, 2.55, "mail.google.com");
  s.addText("Gmail", { x: F.x + 0.25, y: F.y + 0.15, w: 1.3, h: 0.4, fontFace: FONT, fontSize: 16, bold: true, color: NAVY_DEEP, margin: 0 });
  const ax = F.x + F.w - 0.65, ay = F.y + 0.14;
  s.addShape("ellipse", { x: ax, y: ay, w: 0.42, h: 0.42, fill: { color: ICE_MID }, line: { type: "none" } });
  s.addText("記", { x: ax, y: ay, w: 0.42, h: 0.42, fontFace: FONT, fontSize: 12, bold: true, color: NAVY_DEEP, align: "center", valign: "middle", margin: 0 });
  s.addShape("line", { x: F.x, y: F.y + 0.7, w: F.w, h: 0, line: { color: "E4E7EC", width: 1 } });
  for (let i = 0; i < 3; i++) {
    s.addShape("roundRect", { x: F.x + 0.25, y: F.y + 0.85 + i * 0.42, w: F.w - 0.5, h: 0.3, rectRadius: 0.05, fill: { color: "F5F6F8" }, line: { type: "none" } });
  }
  spotlight(s, ax - 0.1, ay - 0.1, 0.62, 0.62, { shape: "ellipse" });
  screenCaption(s, F.x, F.y + F.h + 0.06, F.w);

  pointBar(s, 1.0, 4.35, 8.0, 0.5, "②画面右上の、丸いプロフィール画像を押します", { bg: NAVY });
  pageNum(s, 15, TOTAL);
  s.addNotes("画面右上にある、丸いプロフィール画像を押します。ここがアカウントを切り替える入り口になります。");
}

// ---------- Slide 16: 使い方編 STEP3 ----------
{
  const s = baseSlide(pres);
  kicker(s, "毎日の使い方編（記者が行う作業） STEP 3 / 4");
  partTag(s, "③ 使い方編");
  title(s, "③一覧から「社会部Gmail」を選ぶ", { y: 0.88, size: 24 });

  const F = mockFrame(s, 1.0, 1.5, 8.0, 2.55, "mail.google.com");
  const pw = 3.6, ph = 2.1, px = F.x + F.w - pw - 0.3, py = F.y + 0.1;
  s.addShape("roundRect", { x: px, y: py, w: pw, h: ph, rectRadius: 0.08, fill: { color: "FFFFFF" }, line: { color: "CBD2DC", width: 1.25 } });
  s.addShape("ellipse", { x: px + 0.2, y: py + 0.18, w: 0.4, h: 0.4, fill: { color: ICE_MID }, line: { type: "none" } });
  s.addText("記", { x: px + 0.2, y: py + 0.18, w: 0.4, h: 0.4, fontFace: FONT, fontSize: 11, bold: true, color: NAVY_DEEP, align: "center", valign: "middle", margin: 0 });
  s.addText("記者本人のアカウント（現在ログイン中）", { x: px + 0.7, y: py + 0.18, w: pw - 0.9, h: 0.4, fontFace: FONT, fontSize: 9, bold: true, color: INK, valign: "middle", margin: 0 });
  s.addShape("line", { x: px + 0.15, y: py + 0.72, w: pw - 0.3, h: 0, line: { color: "E4E7EC", width: 1 } });
  s.addShape("roundRect", { x: px + 0.1, y: py + 0.82, w: pw - 0.2, h: 0.46, rectRadius: 0.05, fill: { color: ICE }, line: { color: NAVY, width: 1.25 } });
  s.addText("社会部Gmail", { x: px + 0.3, y: py + 0.82, w: pw - 0.6, h: 0.46, fontFace: FONT, fontSize: 11, bold: true, color: NAVY_DEEP, valign: "middle", margin: 0 });
  s.addShape("line", { x: px + 0.15, y: py + 1.4, w: pw - 0.3, h: 0, line: { color: "E4E7EC", width: 1 } });
  s.addText("別のアカウントを追加", { x: px + 0.3, y: py + 1.55, w: pw - 0.6, h: 0.35, fontFace: FONT, fontSize: 9, color: "B7BCC6", valign: "middle", margin: 0 });
  spotlight(s, px + 0.05, py + 0.77, pw - 0.1, 0.56, { radius: 0.06 });
  screenCaption(s, F.x, F.y + F.h + 0.06, F.w);

  pointBar(s, 1.0, 4.35, 8.0, 0.5, "③一覧の中から「社会部Gmail」を選びます", { bg: NAVY });
  pageNum(s, 16, TOTAL);
  s.addNotes("プロフィール画像を押すと、切り替えられるアカウントの一覧が出てきます。この中から「社会部Gmail」を選びます。承認前はこの項目自体が出てこないので、その場合は招待の承認ができているかを確認してください。");
}

// ---------- Slide 17: 使い方編 STEP4 ----------
{
  const s = baseSlide(pres);
  kicker(s, "毎日の使い方編（記者が行う作業） STEP 4 / 4");
  partTag(s, "③ 使い方編");
  title(s, "④社会部の受信箱が開く", { y: 0.88, size: 24 });

  const F = mockFrame(s, 1.0, 1.5, 8.0, 2.55, "mail.google.com");
  s.addText("社会部Gmail", { x: F.x + 0.25, y: F.y + 0.15, w: 2.0, h: 0.4, fontFace: FONT, fontSize: 15, bold: true, color: NAVY_DEEP, margin: 0 });
  s.addShape("roundRect", { x: F.x + F.w - 2.3, y: F.y + 0.17, w: 2.0, h: 0.34, rectRadius: 0.06, fill: { color: ICE }, line: { color: NAVY, width: 1 } });
  s.addText("代理アクセス中", { x: F.x + F.w - 2.3, y: F.y + 0.17, w: 2.0, h: 0.34, fontFace: FONT, fontSize: 9.5, bold: true, color: NAVY_DEEP, align: "center", valign: "middle", margin: 0 });
  s.addShape("line", { x: F.x, y: F.y + 0.68, w: F.w, h: 0, line: { color: "E4E7EC", width: 1 } });
  s.addShape("roundRect", { x: F.x + 0.25, y: F.y + 0.85, w: F.w - 0.5, h: 0.5, rectRadius: 0.05, fill: { color: ICE }, line: { color: ICE_MID, width: 1 } });
  s.addText("読者から：記事の内容について", { x: F.x + 0.45, y: F.y + 0.85, w: F.w - 0.9, h: 0.5, fontFace: FONT, fontSize: 10, bold: true, color: NAVY_DEEP, valign: "middle", margin: 0 });
  ["（他のメール）", "（他のメール）"].forEach((t, i) => {
    s.addShape("roundRect", { x: F.x + 0.25, y: F.y + 1.42 + i * 0.4, w: F.w - 0.5, h: 0.3, rectRadius: 0.05, fill: { color: "F5F6F8" }, line: { type: "none" } });
  });
  s.addShape("roundRect", { x: F.x + F.w - 1.55, y: F.y + 0.9, w: 1.15, h: 0.36, rectRadius: 0.06, fill: { color: NAVY }, line: { type: "none" } });
  s.addText("返信", { x: F.x + F.w - 1.55, y: F.y + 0.9, w: 1.15, h: 0.36, fontFace: FONT, fontSize: 10, bold: true, color: "FFFFFF", align: "center", valign: "middle", margin: 0 });
  spotlight(s, F.x + F.w - 1.62, F.y + 0.84, 1.3, 0.5, { radius: 0.06 });
  screenCaption(s, F.x, F.y + F.h + 0.06, F.w);

  pointBar(s, 1.0, 4.35, 8.0, 0.5, "④受信箱が開きます。あとはいつも通り読む・返信するだけです", { bg: NAVY });
  pageNum(s, 17, TOTAL);
  s.addNotes("社会部Gmailを選ぶと、新しいタブで社会部の受信箱が開きます。ここから先は、普段自分のGmailを使うのとまったく同じ感覚で、メールを読んだり返信したりできます。");
}

// ---------- Slide 18: 振り返り ----------
{
  const s = baseSlide(pres);
  kicker(s, "振り返り");
  title(s, "3つの作業を振り返ると…");

  const items = [
    { t: "① 設定編", who: "管理担当", note: "パスワード入力：なし\n（社会部Gmailに直接ログインするのは管理担当のみ）" },
    { t: "② 承認編", who: "記者", note: "パスワード入力：なし\n（自分のメールで「確認」を押すだけ）" },
    { t: "③ 使い方編", who: "記者", note: "パスワード入力：なし\n（自分のアカウントのまま切り替えるだけ）" },
  ];
  const colW = 2.75, gap = 0.35, colY = 1.8, colH = 2.1;
  let x = (W - (colW * 3 + gap * 2)) / 2;
  items.forEach((it) => {
    s.addShape("roundRect", { x, y: colY, w: colW, h: colH, rectRadius: 0.1, fill: { color: WHITE }, line: { color: "E4E7EC", width: 1 }, shadow: softShadow({ opacity: 0.14, blur: 6, offset: 2 }) });
    s.addText(it.t, { x: x + 0.15, y: colY + 0.18, w: colW - 0.3, h: 0.35, fontFace: FONT, fontSize: 13.5, bold: true, color: NAVY_DEEP, align: "center", margin: 0 });
    s.addText("担当：" + it.who, { x: x + 0.15, y: colY + 0.55, w: colW - 0.3, h: 0.3, fontFace: FONT, fontSize: 10, color: SUB, align: "center", margin: 0 });
    s.addShape("roundRect", { x: x + 0.2, y: colY + 0.95, w: colW - 0.4, h: 1.0, rectRadius: 0.06, fill: { color: GOOD_BG }, line: { type: "none" } });
    s.addText(it.note, { x: x + 0.32, y: colY + 1.02, w: colW - 0.64, h: 0.88, fontFace: FONT, fontSize: 9, color: NAVY_DEEP, align: "center", margin: 0 });
    x += colW + gap;
  });

  calloutBar(s, "社会部共通パスワードを入力する場面は、どの手順にもありませんでした", 0.55, 4.15, 8.8, 0.6, { size: 14.5 });
  pageNum(s, 18, TOTAL);
  s.addNotes("設定編・承認編・使い方編の3つを振り返ると、どの場面でも社会部共通パスワードを入力する場面がなかったことが分かります。これが代理アクセスの一番のポイントです。");
}

// ---------- Slide 19: 人事異動が簡単に ----------
{
  const s = baseSlide(pres);
  kicker(s, "07｜人事異動のとき");
  title(s, "人事異動が、ぐっと簡単になります");

  function flowRow(y, tag, tagColor, steps) {
    s.addText(tag, { x: 0.55, y, w: 1.1, h: 0.5, fontFace: FONT, fontSize: 12, bold: true, color: tagColor, valign: "middle", margin: 0 });
    let x = 1.75;
    const bw = 1.55, bh = 0.5;
    steps.forEach((t, i) => {
      s.addShape("roundRect", { x, y, w: bw, h: bh, rectRadius: 0.06, fill: { color: "F2F3F5" }, line: { color: "D8DCE3", width: 1 } });
      s.addText(t, { x: x + 0.05, y, w: bw - 0.1, h: bh, fontFace: FONT, fontSize: 10.5, bold: true, color: INK, align: "center", valign: "middle", margin: 0 });
      x += bw;
      if (i < steps.length - 1) {
        s.addShape("line", { x, y: y + bh / 2, w: 0.22, h: 0, line: { color: SUB, width: 1.5, endArrowType: "triangle" } });
        x += 0.22;
      }
    });
  }
  flowRow(1.85, "従来", SUB, ["異動", "パスワード変更", "全員へ連絡", "端末を再設定"]);
  flowRow(2.55, "代理\nアクセス", NAVY_DEEP, ["異動", "利用権限を削除", "新任者を追加"]);

  calloutBar(s, "「パスワード」ではなく「人」を管理する", 0.55, 3.35, 8.8, 0.65, { size: 18 });

  s.addShape("roundRect", { x: 0.55, y: 4.2, w: 8.8, h: 0.85, rectRadius: 0.08, fill: { color: WHITE }, line: { color: "E4E7EC", width: 1 }, shadow: softShadow({ opacity: 0.12, blur: 5, offset: 1.75 }) });
  s.addText("補足（管理担当者向け）：社内の設定によっては、社会部のGoogleグループを代理人として登録し、所属者の管理をさらにまとめて行える場合があります。", {
    x: 0.75, y: 4.2, w: 8.4, h: 0.85, fontFace: FONT, fontSize: 10.5, italic: true, color: SUB, valign: "middle", margin: 0,
  });
  pageNum(s, 19, TOTAL);
  s.addNotes("代理アクセスに変えると、人事異動のときが特に楽になります。これまでは、異動のたびにパスワードを変更し、残る全員に新しいパスワードを連絡し、それぞれの端末で再設定してもらう必要がありました。これからは、異動した人の利用権限を削除して、新しく来た人を追加するだけです。パスワードを管理するのではなく、人を管理するという発想の変化だと考えてください。管理担当向けの補足ですが、社内の設定次第では、Googleグループを使ってさらにまとめて管理できる場合もあります。");
}

// ---------- Slide 20: Gmailだけの仕組み ----------
{
  const s = baseSlide(pres);
  kicker(s, "08｜対象範囲の確認");
  title(s, "これはGmail（メール）だけの仕組みです");

  const boxX = 2.3, boxW = 5.4;
  s.addShape("roundRect", { x: boxX, y: 1.65, w: boxW, h: 0.5, rectRadius: 0.06, fill: { color: NAVY }, line: { type: "none" }, shadow: softShadow({ opacity: 0.24, blur: 7, offset: 2.5 }) });
  s.addText("社会部 Google 環境", { x: boxX, y: 1.65, w: boxW, h: 0.5, fontFace: FONT, fontSize: 14, bold: true, color: WHITE, align: "center", valign: "middle", margin: 0 });

  const rows = [
    { label: "Gmail", val: "代理アクセスで利用", ok: true },
    { label: "Drive", val: "共有ドライブを別に利用", ok: false },
    { label: "Calendar", val: "共有カレンダーを別に利用", ok: false },
  ];
  let ry = 2.25;
  rows.forEach((r) => {
    s.addShape("line", { x: boxX + boxW / 2, y: 2.15, w: 0, h: ry - 2.15, line: { color: ICE_MID, width: 1.5 } });
    s.addShape("roundRect", { x: boxX + 0.3, y: ry, w: 1.8, h: 0.44, rectRadius: 0.06, fill: { color: r.ok ? ICE : "F2F3F5" }, line: { color: r.ok ? NAVY : "D8DCE3", width: 1 } });
    s.addText(r.label, { x: boxX + 0.3, y: ry, w: 1.8, h: 0.44, fontFace: FONT, fontSize: 13, bold: true, color: r.ok ? NAVY_DEEP : SUB, align: "center", valign: "middle", margin: 0 });
    s.addShape("line", { x: boxX + 2.1, y: ry + 0.22, w: 0.4, h: 0, line: { color: SUB, width: 1.5, endArrowType: "triangle" } });
    s.addText(r.val, { x: boxX + 2.6, y: ry, w: boxW - 2.9, h: 0.44, fontFace: FONT, fontSize: 12.5, color: INK, valign: "middle", margin: 0 });
    ry += 0.56;
  });

  calloutBar(s, "代理アクセス＝Gmailのメールを利用するための仕組みです", 0.55, 4.15, 8.8, 0.5, { size: 15 });
  footNote(s, "「代理アクセスを設定すれば、社会部アカウントの全サービスに入れる」は誤解です。");
  pageNum(s, 20, TOTAL);
  s.addNotes("最後に誤解しやすい点を確認します。代理アクセスは、あくまでGmail、つまりメールのための仕組みです。社会部のGoogle DriveやGoogle Calendarは、これとは別に、共有ドライブや共有カレンダーという仕組みを使います。「代理アクセスを設定すれば社会部アカウントの全部のサービスに入れる」というのは誤解なので、ここははっきり伝えてください。");
}

// ---------- Slide 21: まとめ ----------
{
  const s = baseSlide(pres, { dark: true });
  bgCircle(s, -0.6, 5.9, 2.4, { color: "2A4568" });
  kicker(s, "まとめ", true);
  title(s, "覚えるのは3つだけ", { dark: true, size: 30 });

  const items = [
    "社会部共通パスワードを、全員で共有しない",
    "自分の会社Googleアカウントから、社会部Gmailを開く",
    "異動のときは、パスワードではなく利用権限を変更する",
  ];
  let y = 1.85;
  items.forEach((t, i) => {
    s.addShape("ellipse", { x: 0.6, y, w: 0.55, h: 0.55, fill: { color: "223A5E" }, line: { type: "none" }, shadow: softShadow({ opacity: 0.3, blur: 6, offset: 2 }) });
    s.addText(String(i + 1), { x: 0.6, y, w: 0.55, h: 0.55, fontFace: FONT, fontSize: 20, bold: true, color: ICE, align: "center", valign: "middle", margin: 0 });
    s.addText(t, { x: 1.35, y: y, w: 7.9, h: 0.55, fontFace: FONT, fontSize: 16, bold: true, color: WHITE, valign: "middle", margin: 0 });
    y += 0.78;
  });

  s.addShape("roundRect", { x: 0.6, y: 4.35, w: 8.8, h: 0.6, rectRadius: 0.08, fill: { color: "223A5E" }, line: { type: "none" } });
  s.addText("これが「Gmail代理アクセス」です", { x: 0.6, y: 4.35, w: 8.8, h: 0.6, fontFace: FONT, fontSize: 16, bold: true, color: WHITE, align: "center", valign: "middle", margin: 0 });

  s.addText("利用できない場合や、設定が表示されない場合は、社会部管理担当または情報システム担当へ。", {
    x: 0.6, y: 5.1, w: 8.8, h: 0.35, fontFace: FONT, fontSize: 10.5, color: "AAB8D2", align: "center", margin: 0,
  });
  pageNum(s, 21, TOTAL, true);
  s.addNotes("今日覚えていただきたいのは、この3つだけです。1つ、社会部共通パスワードを全員で共有しない。2つ、自分の会社Googleアカウントから社会部Gmailを開く。3つ、異動のときはパスワードではなく利用権限を変更する。これが「Gmail代理アクセス」です。うまく表示されない、設定が見当たらないといった場合は、社会部管理担当か情報システム担当に確認してください。以上で説明を終わります。");
}

// ---------- Slide 22 (appendix): FAQ ----------
{
  const s = baseSlide(pres);
  kicker(s, "補足｜よくある質問");
  title(s, "FAQ", { size: 26 });

  const faqs = [
    ["スマートフォンでも使える？", "代理人の追加はパソコンのみです。代理アカウントの閲覧・送信はスマホのGmailアプリでも順次利用できるようになっています（環境により異なる場合があります）。"],
    ["代理で送ったメールは、誰から送ったように見える？", "社内の設定により、代理人の名前も表示される場合と、社会部アカウントのみ表示される場合があります。"],
    ["社会部Gmailが表示されない場合は？", "招待を承認したか確認し、時間を置いて再確認してください。解決しない場合は管理担当へ。"],
    ["Google Driveも代理アクセスで使える？", "使えません。代理アクセスはGmail専用です。Driveは共有ドライブを別に利用します。"],
    ["代理人は何人まで登録できる？", "職場アカウントでは最大1,000人まで登録できます（実務上の目安として、同時に使うのは数十人程度）。"],
    ["Googleグループをまとめて代理人にできる？", "社内の設定によっては可能です。可否や方法は情報システム担当に確認してください。"],
  ];
  const colW = 4.25, colH = 1.0, gapX = 0.3, gapY = 0.18;
  let idx = 0;
  for (let r = 0; r < 3; r++) {
    for (let c = 0; c < 2; c++) {
      const [q, a] = faqs[idx++];
      const x = 0.55 + c * (colW + gapX);
      const y = 1.55 + r * (colH + gapY);
      s.addShape("roundRect", { x, y, w: colW, h: colH, rectRadius: 0.07, fill: { color: WHITE }, line: { color: "E4E7EC", width: 1 }, shadow: softShadow({ opacity: 0.12, blur: 5, offset: 1.75 }) });
      s.addText("Q. " + q, { x: x + 0.18, y: y + 0.1, w: colW - 0.36, h: 0.34, fontFace: FONT, fontSize: 10.5, bold: true, color: NAVY_DEEP, margin: 0 });
      s.addText("A. " + a, { x: x + 0.18, y: y + 0.42, w: colW - 0.36, h: colH - 0.48, fontFace: FONT, fontSize: 9, color: INK, margin: 0 });
    }
  }
  pageNum(s, 22, TOTAL);
  s.addNotes("最後によくある質問をまとめています。スマートフォンでの利用、送信者表示、社会部Gmailが表示されないときの対処、Driveが使えるかどうか、登録できる人数、Googleグループの活用といった質問です。時間があればこのページも紹介し、なければ「巻末に質問集をまとめているので、あとで見てください」と案内する程度で十分です。");
}

pres.writeFile({ fileName: "gmail-delegation-explainer.pptx" }).then(() => {
  console.log("done");
});
