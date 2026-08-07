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
    fill: { color: ICE }, line: { color: ICE_MID, width: 1 },
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
    fill: { color: NAVY }, line: { type: "none" },
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

// ================= build =================
const pres = newPres();
const TOTAL = 12;

// ---------- Slide 1: title ----------
{
  const s = baseSlide(pres, { dark: true });
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
    fill: { color: NAVY }, line: { type: "none" },
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
      fill: { color: ICE }, line: { color: ICE_MID, width: 1 },
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
  // old
  s.addShape("roundRect", { x: 0.55, y: colY, w: colW, h: colH, rectRadius: 0.1, fill: { color: "F2F3F5" }, line: { color: "D8DCE3", width: 1 } });
  s.addText("これまで", { x: 0.55, y: colY + 0.2, w: colW, h: 0.35, align: "center", fontFace: FONT, fontSize: 13, bold: true, color: SUB, margin: 0 });
  s.addText("🔑", { x: 0.55, y: colY + 0.6, w: colW, h: 0.9, align: "center", fontFace: "Noto Color Emoji", fontSize: 40, margin: 0 });
  s.addText("全員が同じ\nマスターキーを持つ", { x: 0.75, y: colY + 1.55, w: colW - 0.4, h: 0.8, align: "center", fontFace: FONT, fontSize: 14, bold: true, color: INK, margin: 0 });

  // new
  const x2 = 0.55 + colW + 0.5;
  s.addShape("roundRect", { x: x2, y: colY, w: colW, h: colH, rectRadius: 0.1, fill: { color: ICE }, line: { color: NAVY, width: 1.5 } });
  s.addText("これから", { x: x2, y: colY + 0.2, w: colW, h: 0.35, align: "center", fontFace: FONT, fontSize: 13, bold: true, color: NAVY_DEEP, margin: 0 });
  s.addText("💳", { x: x2, y: colY + 0.6, w: colW, h: 0.9, align: "center", fontFace: "Noto Color Emoji", fontSize: 40, margin: 0 });
  s.addText("それぞれ自分の\n社員証を使う", { x: x2 + 0.2, y: colY + 1.55, w: colW - 0.4, h: 0.8, align: "center", fontFace: FONT, fontSize: 14, bold: true, color: NAVY_DEEP, margin: 0 });

  calloutBar(s, "社員証に「社会部メール室に入れる」権限だけが追加されるイメージです", 0.55, colY + colH + 0.25, 8.8, 0.6, { size: 14 });
  footNote(s, "※実際の仕組みはGoogleアカウントの利用権限です。物理的な社員証があるわけではありません。");
  pageNum(s, 4, TOTAL);
  s.addNotes("イメージしやすいように、社員証で例えてみます。これまでは、社会部のメール室に入るための合鍵を全員がコピーして持っているようなものでした。これからは、それぞれが自分の社員証をかざすと、社会部メール室にだけ入れる権限が追加される、というイメージです。実際にはGoogleアカウントの利用権限の話で、物理的な社員証があるわけではありませんが、考え方としてはこれで十分です。");
}

// ---------- Slide 5: できる/できない ----------
{
  const s = baseSlide(pres);
  kicker(s, "04｜できること・できないこと");
  title(s, "代理アクセスすると何ができる？");

  const colY = 1.75, colH = 3.0, colW = 4.2;
  // can
  s.addShape("roundRect", { x: 0.55, y: colY, w: colW, h: colH, rectRadius: 0.1, fill: { color: GOOD_BG }, line: { type: "none" } });
  s.addText("できる（一般部員）", { x: 0.8, y: colY + 0.2, w: colW - 0.5, h: 0.4, fontFace: FONT, fontSize: 15, bold: true, color: NAVY_DEEP, margin: 0 });
  const can = ["社会部宛てのメールを読む・検索する", "メールに返信する", "社会部Gmailからメールを送る", "メールを削除する・整理する"];
  let cy = colY + 0.75;
  can.forEach((t) => {
    s.addText("✓", { x: 0.8, y: cy, w: 0.4, h: 0.4, fontFace: FONT, fontSize: 16, bold: true, color: NAVY, margin: 0 });
    s.addText(t, { x: 1.2, y: cy, w: colW - 0.85, h: 0.5, fontFace: FONT, fontSize: 13, color: INK, valign: "top", margin: 0 });
    cy += 0.56;
  });

  // cannot
  const x2 = 0.55 + colW + 0.5;
  s.addShape("roundRect", { x: x2, y: colY, w: colW, h: colH, rectRadius: 0.1, fill: { color: WARN_BG }, line: { type: "none" } });
  s.addText("できない", { x: x2 + 0.25, y: colY + 0.2, w: colW - 0.5, h: 0.4, fontFace: FONT, fontSize: 15, bold: true, color: WARN, margin: 0 });
  const cannot = ["社会部アカウントのパスワード変更", "Googleアカウント全体の設定変更", "Gmail以外のサービスを自動的にすべて使うこと"];
  cy = colY + 0.75;
  cannot.forEach((t) => {
    s.addText("×", { x: x2 + 0.25, y: cy, w: 0.4, h: 0.4, fontFace: FONT, fontSize: 16, bold: true, color: WARN, margin: 0 });
    s.addText(t, { x: x2 + 0.65, y: cy, w: colW - 0.9, h: 0.6, fontFace: FONT, fontSize: 13, color: INK, valign: "top", margin: 0 });
    cy += 0.62;
  });

  calloutBar(s, "メール業務はできる。でも、社会部アカウントそのものの管理者になるわけではない。", 0.55, colY + colH + 0.25, 8.8, 0.55, { size: 13.5 });
  pageNum(s, 5, TOTAL);
  s.addNotes("代理アクセスでできることは、普段のメール業務とほぼ同じです。読む、検索する、返信する、送る、削除する、整理する。これで十分仕事はできます。一方でできないこともあります。社会部アカウントのパスワード変更や、Googleアカウント全体の設定変更です。つまり、メール業務はできるけれど、社会部アカウントそのものの管理者になるわけではない、という点を覚えてください。");
}

// ---------- Slide 6: 毎日の使い方 ----------
{
  const s = baseSlide(pres);
  kicker(s, "05｜毎日の使い方");
  title(s, "毎日はどう使う？（4ステップ）");

  const steps = [
    { n: "1", t: "自分の会社Gmail\nを開く" },
    { n: "2", t: "右上の\nプロフィール画像を押す" },
    { n: "3", t: "「社会部Gmail\n（代理）」を選ぶ" },
    { n: "4", t: "社会部の受信箱が開く\n（通常のGmailとほぼ同じ）" },
  ];
  const boxW = 1.95, boxH = 1.35, gap = 0.28, arrowW = 0.3;
  const totalW = boxW * 4 + gap * 3 + arrowW * 3;
  let x = (W - totalW) / 2;
  const y = 1.65;
  steps.forEach((st, i) => {
    s.addShape("roundRect", { x, y, w: boxW, h: boxH, rectRadius: 0.1, fill: { color: ICE }, line: { color: ICE_MID, width: 1 } });
    s.addShape("ellipse", { x: x + boxW / 2 - 0.22, y: y + 0.15, w: 0.44, h: 0.44, fill: { color: NAVY }, line: { type: "none" } });
    s.addText(st.n, { x: x + boxW / 2 - 0.22, y: y + 0.15, w: 0.44, h: 0.44, fontFace: FONT, fontSize: 16, bold: true, color: WHITE, align: "center", valign: "middle", margin: 0 });
    s.addText(st.t, { x: x + 0.08, y: y + 0.68, w: boxW - 0.16, h: 0.75, fontFace: FONT, fontSize: 11.5, bold: true, color: INK, align: "center", valign: "top", margin: 0 });
    x += boxW + gap;
    if (i < 3) {
      s.addShape("line", { x, y: y + boxH / 2, w: arrowW, h: 0, line: { color: NAVY, width: 2.5, endArrowType: "triangle" } });
      x += arrowW + gap - gap; // arrow occupies its own gap slot
    }
  });

  // screen mockup
  const mx = 1.3, my = 3.3, mw = 7.4, mh = 1.15;
  s.addShape("roundRect", { x: mx, y: my, w: mw, h: mh, rectRadius: 0.08, fill: { color: "F5F6F8" }, line: { color: "D8DCE3", width: 1 } });
  s.addShape("rect", { x: mx, y: my, w: mw, h: 0.34, fill: { color: WHITE }, line: { color: "D8DCE3", width: 0.75 } });
  s.addShape("ellipse", { x: mx + mw - 0.55, y: my + 0.06, w: 0.22, h: 0.22, fill: { color: ICE_MID }, line: { type: "none" } });
  s.addText("Gmail － 画面イメージ（実際の画面とは異なります）", {
    x: mx + 0.15, y: my, w: mw - 1, h: 0.34, fontFace: FONT, fontSize: 9.5, italic: true, color: SUB, valign: "middle", margin: 0,
  });
  s.addText("社会部Gmail（代理）", {
    x: mx + 0.3, y: my + 0.5, w: mw - 0.6, h: 0.35, fontFace: FONT, fontSize: 14, bold: true, color: NAVY_DEEP, margin: 0,
  });
  s.addText("受信箱  ｜  すべてのメール  ｜  送信済み", {
    x: mx + 0.3, y: my + 0.85, w: mw - 0.6, h: 0.3, fontFace: FONT, fontSize: 10.5, color: SUB, margin: 0,
  });

  calloutBar(s, "社会部共通パスワードの入力は、原則不要です", 1.3, 4.65, 7.4, 0.5, { size: 15 });
  pageNum(s, 6, TOTAL);
  s.addNotes("毎日の使い方はとてもシンプルです。自分の会社Gmailを開いて、右上のプロフィール画像を押して、一覧から「社会部Gmail(代理)」を選ぶ。それだけで社会部の受信箱が開いて、あとはいつも通りのGmailと同じように使えます。ここで見ている画面はイメージ図で、実際の画面とは多少異なりますが、操作の流れは変わりません。そして一番伝えたいのは、社会部共通パスワードを入力する場面は、原則ないということです。");
}

// ---------- Slide 7: 最初だけ必要な作業 ----------
{
  const s = baseSlide(pres);
  kicker(s, "06｜最初だけ必要な作業");
  title(s, "使い始める前に、1回だけの準備");

  const colY = 1.85, colH = 2.9, colW = 4.2;
  s.addShape("roundRect", { x: 0.55, y: colY, w: colW, h: colH, rectRadius: 0.1, fill: { color: ICE }, line: { type: "none" } });
  s.addText("一般部員がすること", { x: 0.8, y: colY + 0.2, w: colW - 0.5, h: 0.4, fontFace: FONT, fontSize: 15, bold: true, color: NAVY_DEEP, margin: 0 });
  const gen = ["管理担当から招待メールが届く", "招待メールを開く", "内容を確認して承認する", "そのまま利用を開始する"];
  let cy = colY + 0.75;
  gen.forEach((t, i) => {
    s.addShape("ellipse", { x: 0.8, y: cy, w: 0.34, h: 0.34, fill: { color: NAVY }, line: { type: "none" } });
    s.addText(String(i + 1), { x: 0.8, y: cy, w: 0.34, h: 0.34, fontFace: FONT, fontSize: 12, bold: true, color: WHITE, align: "center", valign: "middle", margin: 0 });
    s.addText(t, { x: 1.25, y: cy - 0.03, w: colW - 0.9, h: 0.45, fontFace: FONT, fontSize: 12.5, color: INK, valign: "middle", margin: 0 });
    cy += 0.52;
  });

  const x2 = 0.55 + colW + 0.5;
  s.addShape("roundRect", { x: x2, y: colY, w: colW, h: colH, rectRadius: 0.1, fill: { color: "F2F3F5" }, line: { type: "none" } });
  s.addText("管理担当がすること", { x: x2 + 0.25, y: colY + 0.2, w: colW - 0.5, h: 0.4, fontFace: FONT, fontSize: 15, bold: true, color: SUB, margin: 0 });
  s.addText("社会部Gmail側の設定で、\n利用する人を登録するだけです。", {
    x: x2 + 0.25, y: colY + 0.85, w: colW - 0.5, h: 1.0, fontFace: FONT, fontSize: 13, color: INK, margin: 0,
  });
  s.addText("詳しい設定手順は巻末の補足ページを\n参照してください。", {
    x: x2 + 0.25, y: colY + 1.9, w: colW - 0.5, h: 0.8, fontFace: FONT, fontSize: 11, italic: true, color: SUB, margin: 0,
  });

  footNote(s, "招待には期限があり、承認後の反映まで時間がかかる場合があります。");
  pageNum(s, 7, TOTAL);
  s.addNotes("使い始める前に、最初の1回だけ準備が必要です。一般部員がすることは、管理担当から届く招待メールを開いて、承認するだけです。承認すれば、その日から自分のアカウントで利用を開始できます。管理担当の側は、社会部Gmailの設定画面で利用する人を登録する作業がありますが、これは一般部員が気にする必要はありません。招待には期限があるので、届いたら早めに承認してください。");
}

// ---------- Slide 8: 人事異動が簡単に ----------
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

  s.addShape("roundRect", { x: 0.55, y: 4.2, w: 8.8, h: 0.85, rectRadius: 0.08, fill: { color: "F7F8FA" }, line: { color: "E4E7EC", width: 1 } });
  s.addText("補足（管理担当者向け）：社内の設定によっては、社会部のGoogleグループを代理人として登録し、所属者の管理をさらにまとめて行える場合があります。", {
    x: 0.75, y: 4.2, w: 8.4, h: 0.85, fontFace: FONT, fontSize: 10.5, italic: true, color: SUB, valign: "middle", margin: 0,
  });
  pageNum(s, 8, TOTAL);
  s.addNotes("代理アクセスに変えると、人事異動のときが特に楽になります。これまでは、異動のたびにパスワードを変更し、残る全員に新しいパスワードを連絡し、それぞれの端末で再設定してもらう必要がありました。これからは、異動した人の利用権限を削除して、新しく来た人を追加するだけです。パスワードを管理するのではなく、人を管理するという発想の変化だと考えてください。管理担当向けの補足ですが、社内の設定次第では、Googleグループを使ってさらにまとめて管理できる場合もあります。");
}

// ---------- Slide 9: Gmailだけの仕組み ----------
{
  const s = baseSlide(pres);
  kicker(s, "08｜対象範囲の確認");
  title(s, "これはGmail（メール）だけの仕組みです");

  const boxX = 2.3, boxW = 5.4;
  s.addShape("roundRect", { x: boxX, y: 1.65, w: boxW, h: 0.5, rectRadius: 0.06, fill: { color: NAVY }, line: { type: "none" } });
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
  pageNum(s, 9, TOTAL);
  s.addNotes("最後に誤解しやすい点を確認します。代理アクセスは、あくまでGmail、つまりメールのための仕組みです。社会部のGoogle DriveやGoogle Calendarは、これとは別に、共有ドライブや共有カレンダーという仕組みを使います。「代理アクセスを設定すれば社会部アカウントの全部のサービスに入れる」というのは誤解なので、ここははっきり伝えてください。");
}

// ---------- Slide 10: まとめ ----------
{
  const s = baseSlide(pres, { dark: true });
  kicker(s, "まとめ", true);
  title(s, "覚えるのは3つだけ", { dark: true, size: 30 });

  const items = [
    "社会部共通パスワードを、全員で共有しない",
    "自分の会社Googleアカウントから、社会部Gmailを開く",
    "異動のときは、パスワードではなく利用権限を変更する",
  ];
  let y = 1.85;
  items.forEach((t, i) => {
    s.addShape("ellipse", { x: 0.6, y, w: 0.55, h: 0.55, fill: { color: "223A5E" }, line: { type: "none" } });
    s.addText(String(i + 1), { x: 0.6, y, w: 0.55, h: 0.55, fontFace: FONT, fontSize: 20, bold: true, color: ICE, align: "center", valign: "middle", margin: 0 });
    s.addText(t, { x: 1.35, y: y, w: 7.9, h: 0.55, fontFace: FONT, fontSize: 16, bold: true, color: WHITE, valign: "middle", margin: 0 });
    y += 0.78;
  });

  s.addShape("roundRect", { x: 0.6, y: 4.35, w: 8.8, h: 0.6, rectRadius: 0.08, fill: { color: "223A5E" }, line: { type: "none" } });
  s.addText("これが「Gmail代理アクセス」です", { x: 0.6, y: 4.35, w: 8.8, h: 0.6, fontFace: FONT, fontSize: 16, bold: true, color: WHITE, align: "center", valign: "middle", margin: 0 });

  s.addText("利用できない場合や、設定が表示されない場合は、社会部管理担当または情報システム担当へ。", {
    x: 0.6, y: 5.1, w: 8.8, h: 0.35, fontFace: FONT, fontSize: 10.5, color: "AAB8D2", align: "center", margin: 0,
  });
  pageNum(s, 10, TOTAL, true);
  s.addNotes("今日覚えていただきたいのは、この3つだけです。1つ、社会部共通パスワードを全員で共有しない。2つ、自分の会社Googleアカウントから社会部Gmailを開く。3つ、異動のときはパスワードではなく利用権限を変更する。これが「Gmail代理アクセス」です。うまく表示されない、設定が見当たらないといった場合は、社会部管理担当か情報システム担当に確認してください。以上で説明を終わります。");
}

// ---------- Slide 11 (appendix): 管理担当者向け補足 ----------
{
  const s = baseSlide(pres);
  kicker(s, "補足｜管理担当者向け");
  title(s, "補足：初期設定とGoogleグループの活用", { size: 24 });

  const items = [
    ["初期設定（情報システム担当）", "Google管理コンソールで「メールの委任」を組織内向けに有効にします。"],
    ["利用者の登録（主担当・副担当）", "社会部Gmailの設定画面から、利用する人を1人ずつ追加します。"],
    ["Googleグループの活用（環境による）", "組織内であれば、Googleグループを代理人として追加できる場合があります。所属者へまとめて利用権限を与えられます。"],
    ["異動時の対応", "異動者の削除と、新任者の追加を、その都度行います。"],
    ["登録できる人数の目安", "職場アカウントでは代理人を多数登録できますが、実務上の目安として同時に使う人数は数十人程度です。"],
  ];
  let y = 1.55;
  items.forEach(([h, b]) => {
    s.addText(h, { x: 0.55, y, w: 8.9, h: 0.3, fontFace: FONT, fontSize: 13, bold: true, color: NAVY_DEEP, margin: 0 });
    s.addText(b, { x: 0.55, y: y + 0.3, w: 8.9, h: 0.32, fontFace: FONT, fontSize: 11, color: INK, margin: 0 });
    y += 0.68;
  });
  footNote(s, "社内のGoogle Workspace設定により、実際の操作画面・利用条件が異なる場合があります。");
  pageNum(s, 11, TOTAL);
  s.addNotes("ここからは巻末の補足です。管理担当者・情報システム担当者向けの内容なので、一般部員向けの説明会では読み上げなくて構いません。初期設定は情報システム担当がGoogle管理コンソールで行い、利用者の登録は主担当・副担当が社会部Gmail側で行います。Googleグループの活用や人数の目安は、社内のGoogle Workspace設定によって条件が異なるため、必要に応じて情報システム担当に確認してください。");
}

// ---------- Slide 12 (appendix): FAQ ----------
{
  const s = baseSlide(pres);
  kicker(s, "補足｜よくある質問");
  title(s, "FAQ", { size: 26 });

  const faqs = [
    ["スマートフォンでも使える？", "代理人の追加はパソコンのみです。代理アカウントの閲覧・送信はスマホのGmailアプリでも順次利用できるようになっています（環境により異なる場合があります）。"],
    ["代理で送ったメールは、誰から送ったように見える？", "社内の設定により、代理人の名前も表示される場合と、社会部アカウントのみ表示される場合があります。"],
    ["社会部Gmailが表示されない場合は？", "招待を承認したか確認し、時間を置いて再確認してください。解決しない場合は管理担当へ。"],
    ["Google Driveも代理アクセスで使える？", "使えません。代理アクセスはGmail専用です。Driveは共有ドライブを別に利用します。"],
  ];
  const colW = 4.25, colH = 1.55, gapX = 0.3, gapY = 0.25;
  let idx = 0;
  for (let r = 0; r < 2; r++) {
    for (let c = 0; c < 2; c++) {
      const [q, a] = faqs[idx++];
      const x = 0.55 + c * (colW + gapX);
      const y = 1.65 + r * (colH + gapY);
      s.addShape("roundRect", { x, y, w: colW, h: colH, rectRadius: 0.08, fill: { color: "F7F8FA" }, line: { color: "E4E7EC", width: 1 } });
      s.addText("Q. " + q, { x: x + 0.2, y: y + 0.15, w: colW - 0.4, h: 0.5, fontFace: FONT, fontSize: 12, bold: true, color: NAVY_DEEP, margin: 0 });
      s.addText("A. " + a, { x: x + 0.2, y: y + 0.62, w: colW - 0.4, h: colH - 0.75, fontFace: FONT, fontSize: 10.5, color: INK, margin: 0 });
    }
  }
  pageNum(s, 12, TOTAL);
  s.addNotes("最後によくある質問をまとめています。スマートフォンでの利用、送信者表示、社会部Gmailが表示されないときの対処、Driveが使えるかどうか、といった質問です。時間があればこのページも紹介し、なければ「巻末に質問集をまとめているので、あとで見てください」と案内する程度で十分です。");
}

pres.writeFile({ fileName: "gmail-delegation-explainer.pptx" }).then(() => {
  console.log("done");
});
