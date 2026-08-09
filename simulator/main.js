/*
 * main.js — 演出層(PHASE_4)。
 *
 * 物理量は一つ残らず window.PHYS(physics.js、P4-C20 認証済み)から取る。
 * このファイルにあるのは時間圧縮・カメラ・配色・トーンマッピングという
 * 「見せ方」だけであり、以下の仲裁規則を実装で固定する:
 *   - 前方ヌル: ローブの輝度・粒子密度は飽和パターン (1−cosϑ) に比例
 *     (ϑ=0 で厳密ゼロ)。ダミー発光なし
 *   - ローブの向きは thrust 履歴(幕1-2: 後方 / 幕3-4: 前方)
 *   - 星野の光行差・ドップラーは η から厳密に計算(誇張倍率 1.0)
 *   - 輝度は対数圧縮で表示(README に宣言。色は演出であり物理主張ではない)
 *   - 実時間演出は 出発・反転・到着 の三箇所のみ、他は対数圧縮
 */
import * as THREE from "three";

const P = window.PHYS;

/* ================= C20 バッジ(起動時に実認証を走らせる) ================= */
const rs = window.SNAPSHOT_RUN();
const c20Fails = rs.filter(r => !r.pass).length;
const badge = document.getElementById("c20-badge");
badge.textContent = c20Fails === 0 ? `${rs.length}/${rs.length} 緑` : `${c20Fails} 赤`;
badge.className = c20Fails === 0 ? "green" : "red";

/* ================= 演出定数(自由領域) ================= */
const CFG = {
  starCount: 4200, skyR: 820,
  exhaustCount: 900, lobeLen: 7.0,
  lumFloorLog: Math.log(1e-33), lumCeilLog: Math.log(0.57), // L 表示正規化域
  flashLogFloor: -9,                                        // F 対数計の下端
  colBg: 0x04050a,
};

/* ================= 五幕タイムライン ================= */
const ACTS = [
  { no: "ACT I",   name: "出 発", dur: 15 },
  { no: "ACT II",  name: "巡 航", dur: 30 },
  { no: "ACT III", name: "反 転", dur: 7 },
  { no: "ACT IV",  name: "減 速", dur: 26 },
  { no: "ACT V",   name: "到 着 / 視 点 反 転", dur: 30 },
];
const TOTAL = ACTS.reduce((s, a) => s + a.dur, 0);

const clamp01 = (v) => Math.max(0, Math.min(1, v));
const smooth = (v) => { v = clamp01(v); return v * v * (3 - 2 * v); };
const lerp = (a, b, t) => a + (b - a) * t;

// 幕ごとの物理状態(η は現在ラピディティ、spent は総燃焼 Δη)
function stateAt(act, t) {
  const LAM = P.LAMBDA_BURN;
  if (act === 0) {                          // 出発(実時間)
    const ign = smooth((t - 1.6) / 3.2);    // 点火ランプ
    const eta = 0.35 * Math.pow(smooth((t - 2.2) / 12.4), 1.6);
    return { eta, spent: eta, s: 1, lam: LAM * ign, mode: "ship" };
  }
  if (act === 1) {                          // 巡航(対数圧縮: η 0.35→12)
    const u = smooth(t / ACTS[1].dur);
    const eta = 0.35 * Math.pow(12 / 0.35, u);
    return { eta, spent: eta, s: 1, lam: LAM, mode: "ship" };
  }
  if (act === 2) {                          // 反転(実時間)
    const f = t / ACTS[2].dur;
    let s = 1, lam = LAM;
    if (f < 0.42) { s = 1; lam = LAM * (1 - f / 0.42); }
    else if (f < 0.58) { s = 0; lam = 0; }
    else { s = -1; lam = LAM * smooth((f - 0.58) / 0.42); }
    return { eta: 12, spent: 12, s, lam, mode: "ship" };
  }
  if (act === 3) {                          // 減速(対数圧縮: η 12→0.02)
    const u = smooth(t / ACTS[3].dur);
    const eta = 12 * Math.pow(0.02 / 12, u);
    return { eta, spent: 12 + (12 - eta), s: -1, lam: LAM, mode: "ship" };
  }
  // 幕 5: 到着(実時間)→ 視点反転(目的地観測者)
  if (t < 4) {
    const w = smooth(t / 4);
    const eta = 0.02 * (1 - w);
    return { eta, spent: 24 - eta, s: -1, lam: LAM * (1 - w), mode: "ship" };
  }
  if (t < 12) {                             // 暗黒の 250 万年(圧縮)
    return { eta: 0, spent: 24, s: 0, lam: 0, mode: "dest",
             wait: clamp01((t - 4.6) / 6.4) };
  }
  // フラッシュ・リプレイ(対数時間: 減速脚 η_r 12→7.4 を再生)
  const w = clamp01((t - 12.5) / 12.0);
  const etaR = 12 - 4.6 * Math.pow(w, 0.65);
  return { eta: 0, spent: 24, s: 0, lam: 0, mode: "dest",
           replay: true, etaR, wait: 1 };
}

/* ================= 字幕 ================= */
const CAPTIONS = [
  { a: 0, t0: 1.0, t1: 5.5,  txt: "アンドロメダ座大銀河 M31 — 二百五十万光年。" },
  { a: 0, t0: 7.0, t1: 13.5, txt: "飽和バーン点火。質量を光に変えて進む。燃えるのは後方だけ。" },
  { a: 1, t0: 1.0, t1: 6.0,  txt: "η が昇る。星野が前方へ絞られていく。" },
  { a: 1, t0: 8.5, t1: 14.0, txt: "正面は、厳密に暗い。加速するワープ船は前から見えない。" },
  { a: 1, t0: 21.0, t1: 27.0, txt: "座席の値段は e²ᵑ で嵩む。それでも星は近づく。" },
  { a: 2, t0: 0.6, t1: 6.2,  txt: "反転。ここからは、目的地に向かって焚く。" },
  { a: 3, t0: 2.0, t1: 8.0,  txt: "質量は e⁻⁷² へ。フロンティアは広がり続ける。" },
  { a: 3, t0: 15.0, t1: 21.0, txt: "船はもう、ほとんど光だけでできている。" },
  { a: 4, t0: 0.4, t1: 3.6,  txt: "到着。M31 の静かな重力場へ。" },
  { a: 4, t0: 5.0, t1: 11.5, txt: "視点反転 — 目的地の観測者は、二百五十万年、何も見ていない。" },
  { a: 4, t0: 13.0, t1: 17.5, txt: "そして —" },
  { a: 4, t0: 18.5, t1: 23.5, txt: "F ∝ e⁷ᵑ⁻⁷² 。ピコ秒の閃光だけが、航海のすべてを語る。" },
  { a: 4, t0: 25.0, t1: 29.6,
    txt: "加速するワープ船は正面から見えない。到着だけが、閃光として届く。" },
];

/* ================= シーン ================= */
const stage = document.getElementById("stage");
const renderer = new THREE.WebGLRenderer({ antialias: true });
renderer.setPixelRatio(Math.min(devicePixelRatio, 2));
renderer.setSize(innerWidth, innerHeight);
renderer.toneMapping = THREE.ACESFilmicToneMapping;
stage.appendChild(renderer.domElement);

const scene = new THREE.Scene();
scene.background = new THREE.Color(CFG.colBg);
const camera = new THREE.PerspectiveCamera(58, innerWidth / innerHeight, 0.05, 4000);
scene.add(new THREE.AmbientLight(0x404a5a, 0.5));

/* ---- 星野(InstancedMesh、光行差・ドップラーは η から厳密) ---- */
// v = sin²(θ/2) を一様乱数に取ると方向は球面一様になる
const stars = { v0: [], phi: [], lum: [], tint: [] };
for (let i = 0; i < CFG.starCount; i++) {
  stars.v0.push(Math.random());
  stars.phi.push(Math.random() * Math.PI * 2);
  stars.lum.push(0.35 + 0.65 * Math.pow(Math.random(), 2.2));
  const w = Math.random();                  // 温度前処理(演出)
  stars.tint.push(new THREE.Color().setHSL(
    w < 0.6 ? 0.60 : (w < 0.85 ? 0.12 : 0.02),
    0.25 * Math.random(), 0.92));
}
const starGeo = new THREE.SphereGeometry(1.0, 6, 4);
const starMat = new THREE.MeshBasicMaterial({ color: 0xffffff });
const starMesh = new THREE.InstancedMesh(starGeo, starMat, CFG.starCount);
starMesh.instanceMatrix.setUsage(THREE.DynamicDrawUsage);
scene.add(starMesh);
const dummy = new THREE.Object3D();
const cTmp = new THREE.Color();

function updateStars(eta) {
  for (let i = 0; i < CFG.starCount; i++) {
    // 見かけ方向: v_app = aberrate(v_lab, −η)(前方収束)。誇張倍率 1.0
    const vApp = P.aberrateV(stars.v0[i], -eta);
    const delta = P.invDopplerV(vApp, -eta);      // δ = γ(1+βμ_app)
    const cosT = 1 - 2 * vApp;
    const sinT = 2 * Math.sqrt(Math.max(0, vApp * (1 - vApp)));
    const ph = stars.phi[i];
    dummy.position.set(CFG.skyR * sinT * Math.cos(ph),
                       CFG.skyR * sinT * Math.sin(ph),
                       CFG.skyR * cosT);
    const sc = 1.5 + 1.3 * stars.lum[i];
    dummy.scale.setScalar(sc);
    dummy.updateMatrix();
    starMesh.setMatrixAt(i, dummy.matrix);
    // 輝度: 物理は δ⁴ — 表示は対数圧縮(README 宣言)。色相は演出
    const bf = Math.min(2.6, Math.max(0.05, Math.pow(delta, 1.15)));
    const shift = 0.5 + 0.5 * Math.tanh(0.9 * Math.log(delta));
    cTmp.copy(stars.tint[i]).multiplyScalar(stars.lum[i] * bf);
    cTmp.r = lerp(cTmp.r * 1.25, cTmp.r * 0.75, shift);
    cTmp.b = lerp(cTmp.b * 0.72, cTmp.b * 1.30, shift);
    starMesh.setColorAt(i, cTmp);
  }
  starMesh.instanceMatrix.needsUpdate = true;
  if (starMesh.instanceColor) starMesh.instanceColor.needsUpdate = true;
}
updateStars(0);

/* ---- 船体(ワープシェル) ---- */
const ship = new THREE.Group();
const shell = new THREE.Mesh(
  new THREE.SphereGeometry(1, 48, 32),
  new THREE.MeshStandardMaterial({ color: 0x141c28, metalness: 0.85,
    roughness: 0.32, emissive: 0x060a12 }));
const rim = new THREE.Mesh(
  new THREE.SphereGeometry(1.045, 48, 32),
  new THREE.MeshBasicMaterial({ color: 0x2a4a66, transparent: true,
    opacity: 0.16, side: THREE.BackSide, blending: THREE.AdditiveBlending }));
const ring = new THREE.Mesh(
  new THREE.TorusGeometry(1.42, 0.018, 12, 96),
  new THREE.MeshBasicMaterial({ color: 0x7dd3fc, transparent: true, opacity: 0.5 }));
ship.add(shell, rim, ring);
scene.add(ship);

/* ---- 排気ローブ(密度・輝度 ∝ 飽和パターン 1−cosϑ — 前方は厳密ゼロ) ---- */
function softDotTexture() {
  const cv = document.createElement("canvas"); cv.width = cv.height = 64;
  const g2 = cv.getContext("2d");
  const gr = g2.createRadialGradient(32, 32, 1, 32, 32, 32);
  gr.addColorStop(0, "rgba(255,255,255,1)");
  gr.addColorStop(0.35, "rgba(255,255,255,0.45)");
  gr.addColorStop(1, "rgba(255,255,255,0)");
  g2.fillStyle = gr; g2.fillRect(0, 0, 64, 64);
  return new THREE.CanvasTexture(cv);
}
const ex = { cos: [], phi: [], p: [], spd: [] };
for (let i = 0; i < CFG.exhaustCount; i++) {
  ex.cos.push(1 - 2 * Math.sqrt(Math.random()));  // 密度 ∝ (1−cosϑ)
  ex.phi.push(Math.random() * Math.PI * 2);
  ex.p.push(Math.random());
  ex.spd.push(0.5 + Math.random());
}
const exGeo = new THREE.BufferGeometry();
const exPos = new Float32Array(CFG.exhaustCount * 3);
const exCol = new Float32Array(CFG.exhaustCount * 3);
exGeo.setAttribute("position",
  new THREE.BufferAttribute(exPos, 3).setUsage(THREE.DynamicDrawUsage));
exGeo.setAttribute("color",
  new THREE.BufferAttribute(exCol, 3).setUsage(THREE.DynamicDrawUsage));
const exMesh = new THREE.Points(exGeo, new THREE.PointsMaterial({
  size: 0.30, map: softDotTexture(), vertexColors: true, transparent: true,
  blending: THREE.AdditiveBlending, depthWrite: false }));
exMesh.frustumCulled = false;
scene.add(exMesh);
// ローブ基部のコア光(スプライト)+ 船体を照らす光
const exCore = new THREE.Sprite(new THREE.SpriteMaterial({
  map: flareTexture(), transparent: true, depthWrite: false,
  blending: THREE.AdditiveBlending, color: 0xffd9a0 }));
exCore.visible = false;
scene.add(exCore);
const exLight = new THREE.PointLight(0xffc36b, 0, 40, 2.0);
scene.add(exLight);
const cHot = new THREE.Color(1.0, 0.78, 0.42);
const cCool = new THREE.Color(0.72, 0.26, 0.07);

function updateExhaust(st, dt) {
  const L = 3 * P.m(st.spent) * (st.lam);        // L = 3mλ(飽和、R=1)
  // 表示輝度は L の対数正規化(README 宣言)— HUD は真値を表示する
  const g = L > 0
    ? clamp01((Math.log(L) - CFG.lumFloorLog) / (CFG.lumCeilLog - CFG.lumFloorLog))
    : 0;
  const axis = st.s;                              // 加速軸 = s·(+z)
  for (let i = 0; i < CFG.exhaustCount; i++) {
    const j = i * 3;
    if (g <= 0 || axis === 0) {
      exCol[j] = exCol[j + 1] = exCol[j + 2] = 0;
      exPos[j] = 0; exPos[j + 1] = 0; exPos[j + 2] = 0;
      continue;
    }
    ex.p[i] = (ex.p[i] + dt * 0.5 * ex.spd[i]) % 1;
    const d = ex.p[i];
    const cosT = ex.cos[i], sinT = Math.sqrt(Math.max(0, 1 - cosT * cosT));
    const ph = ex.phi[i];
    const r = 1.3 + d * CFG.lobeLen;
    // ϑ は加速軸から測る(排気は cosϑ→−1 側に集中、前方は密度・輝度とも 0)
    exPos[j] = r * sinT * Math.cos(ph);
    exPos[j + 1] = r * sinT * Math.sin(ph);
    exPos[j + 2] = axis * r * cosT;
    const shape = (1 - ex.cos[i]) / 2;            // ∝ 飽和パターン
    const b = 0.5 * g * shape * (1 - d * 0.8);
    cTmp.copy(cHot).lerp(cCool, d * d).multiplyScalar(b);
    exCol[j] = cTmp.r; exCol[j + 1] = cTmp.g; exCol[j + 2] = cTmp.b;
  }
  exGeo.attributes.position.needsUpdate = true;
  exGeo.attributes.color.needsUpdate = true;
  // コア光と排気照明(幕 3 以降は前方=目的地側から焚く)
  exCore.visible = g > 0 && axis !== 0;
  if (exCore.visible) {
    exCore.position.set(0, 0, -axis * 1.75);
    const cs = 2.3 * (0.35 + 0.65 * g);
    exCore.scale.set(cs, cs, 1);
    const dCam = camera.position.distanceTo(exCore.position);
    exCore.material.opacity = 0.55 * g * clamp01((dCam - 1.0) / 2.2);
  }
  exLight.intensity = 14 * g;
  exLight.position.set(0, 0, -st.s * 3.0);
  exLight.color.copy(cHot);
}

/* ---- M31 / 天の川 / フラッシュ(スプライト、テクスチャは手続き生成) ---- */
function galaxyTexture(coreCol, haloCol) {
  const cv = document.createElement("canvas"); cv.width = cv.height = 256;
  const g2 = cv.getContext("2d");
  g2.translate(128, 128); g2.rotate(-0.5); g2.scale(1, 0.42);
  const gr = g2.createRadialGradient(0, 0, 4, 0, 0, 120);
  gr.addColorStop(0, coreCol); gr.addColorStop(0.35, haloCol);
  gr.addColorStop(1, "rgba(0,0,0,0)");
  g2.fillStyle = gr; g2.fillRect(-128, -304, 256, 608);
  return new THREE.CanvasTexture(cv);
}
function flareTexture() {
  const cv = document.createElement("canvas"); cv.width = cv.height = 256;
  const g2 = cv.getContext("2d");
  const gr = g2.createRadialGradient(128, 128, 2, 128, 128, 128);
  gr.addColorStop(0, "rgba(255,252,240,1)");
  gr.addColorStop(0.18, "rgba(255,222,150,0.85)");
  gr.addColorStop(0.5, "rgba(255,170,80,0.25)");
  gr.addColorStop(1, "rgba(0,0,0,0)");
  g2.fillStyle = gr; g2.fillRect(0, 0, 256, 256);
  return new THREE.CanvasTexture(cv);
}
const m31 = new THREE.Sprite(new THREE.SpriteMaterial({
  map: galaxyTexture("rgba(235,238,255,0.95)", "rgba(150,160,255,0.35)"),
  transparent: true, depthWrite: false }));
m31.position.set(0, 6, CFG.skyR * 0.985);
scene.add(m31);
const mw = new THREE.Sprite(new THREE.SpriteMaterial({
  map: galaxyTexture("rgba(255,246,225,0.9)", "rgba(210,190,255,0.30)"),
  transparent: true, depthWrite: false }));
mw.position.set(0, 4, CFG.skyR * 0.985); mw.scale.set(46, 46, 1);
mw.visible = false;
scene.add(mw);
const flash = new THREE.Sprite(new THREE.SpriteMaterial({
  map: flareTexture(), transparent: true, depthWrite: false,
  blending: THREE.AdditiveBlending }));
flash.position.set(0, 4, CFG.skyR * 0.97);
flash.scale.set(0.001, 0.001, 1); flash.visible = false;
scene.add(flash);

/* ================= カメラ演出 ================= */
const V = (x, y, z) => new THREE.Vector3(x, y, z);
function camKeys(act, t, st) {
  // 各幕のキーフレーム(pos, look)。返り値 {pos, look}
  if (act === 0) {
    const u = smooth(t / ACTS[0].dur);
    return { pos: V(lerp(6.4, 5.2, u), lerp(2.6, 1.9, u), lerp(-8.2, -6.6, u)),
             look: V(0, 0, -1.5) };
  }
  if (act === 1) {
    if (t < 8) {          // 後方→機首へ回り込む
      const u = smooth(t / 8);
      const ang = lerp(-2.55, -0.12, u), r = lerp(5.2, 6.3, u);
      return { pos: V(r * Math.sin(ang) * -1, lerp(1.2, 0.35, u), r * Math.cos(ang) * -1),
               look: V(0, 0, 0) };
    }
    if (t < 12.5) {       // 真正面 — 前方ヌルの目視確認カット
      const u = smooth((t - 8) / 4.5);
      return { pos: V(lerp(0.75, 0.0, u), lerp(0.35, 0.18, u), lerp(6.3, 6.6, u)),
               look: V(0, 0, 0) };
    }
    // 艦橋(船体前面、前方視界クリア)へカット、以降は微揺動
    const w = t - 12.5;
    return { pos: V(Math.sin(w * 0.21) * 0.1, 0.55 + Math.sin(w * 0.13) * 0.04, 1.42),
             look: V(0, 0.6, 200), cut: t < 12.62 };
  }
  if (act === 2) {
    const u = smooth(t / ACTS[2].dur);
    return { pos: V(lerp(5.6, 4.6, u), lerp(1.1, 0.7, u), lerp(0.6, -0.8, u)),
             look: V(0, 0, 0), cut: t < 0.12 };
  }
  if (act === 3) {
    const w = t;
    return { pos: V(Math.sin(w * 0.17) * 0.1, 0.55, 1.42),
             look: V(0, 0.6, 200), cut: t < 0.12 };
  }
  // 幕 5
  if (st.mode === "ship") {
    const u = smooth(t / 4);
    return { pos: V(lerp(6.6, 7.8, u), lerp(2.2, 2.7, u), lerp(4.6, 6.4, u)),
             look: V(0, 0, 0), cut: t < 0.12 };
  }
  return { pos: V(0, 0, 0), look: V(0, 4, CFG.skyR), cut: t < 4.15 };
}

/* ================= HUD(全数値 physics.js) ================= */
const $ = (id) => document.getElementById(id);
const sci = (v) => {
  if (v === 0) return "0";
  if (v >= 0.01 && v < 1e4) return v.toPrecision(3);
  const e = Math.floor(Math.log10(Math.abs(v)));
  return (v / Math.pow(10, e)).toFixed(2) + "×10" + supExp(e);
};
function supExp(e) {
  const S = { "-": "⁻", 0: "⁰", 1: "¹", 2: "²", 3: "³", 4: "⁴",
              5: "⁵", 6: "⁶", 7: "⁷", 8: "⁸", 9: "⁹" };
  return String(e).split("").map(c => S[c]).join("");
}
const LADDER_ETAS = [0.24, 2.0, 6.0, 12.0];
const ladderEl = $("ladder");
for (const et of LADDER_ETAS) {
  const d = document.createElement("div");
  d.className = "lrow"; d.dataset.eta = et;
  d.innerHTML = `<span>η = ${et}</span><b class="mono">${sci(P.seatPrice(et))}</b>`;
  ladderEl.appendChild(d);
}
$("hud-dist").textContent = (P.M31_DIST_LY / 1e6).toFixed(2) + "×10⁶ ly";
$("hud-eta50").textContent = P.etaFifty(P.M31_DIST_LY, P.TAU_LIFETIME_YR).toFixed(2);
$("hud-mf").textContent = sci(P.m(P.M31_DETA_TOT));

function updateHUD(st) {
  $("hud-eta").textContent = st.eta.toFixed(3);
  const b = P.beta(st.eta);
  // 表示恒等: 1−tanhη = 2e^(−2η)/(1+e^(−2η))(桁落ちしない形)
  $("hud-beta").textContent = b < 0.999999 ? b.toFixed(6)
    : "1−" + sci(2 * Math.exp(-2 * st.eta) / (1 + Math.exp(-2 * st.eta)));
  $("hud-m").textContent = sci(P.m(st.spent));
  const xNow = P.x(st.spent);
  $("hud-x").textContent = sci(xNow);
  $("hud-lam").textContent = st.lam.toFixed(3);
  const ceil = P.ceiling(xNow);
  const eff = P.lambdaTier(xNow, "effective");
  const flo = P.lambdaTier(xNow, "floor");
  const pct = (v) => clamp01(v / 0.4) * 100;
  $("tick-ceil").style.left = pct(ceil) + "%";
  $("tick-eff").style.left = pct(eff) + "%";
  $("tick-floor").style.left = pct(flo) + "%";
  $("lam-dot").style.left = `calc(${pct(st.lam)}% - 4px)`;
  $("hud-price").textContent = sci(P.seatPrice(st.eta));
  let best = 0;
  for (let i = 0; i < LADDER_ETAS.length; i++) {
    if (Math.abs(LADDER_ETAS[i] - st.eta) < Math.abs(LADDER_ETAS[best] - st.eta)) best = i;
  }
  ladderEl.querySelectorAll(".lrow").forEach((el, i) =>
    el.classList.toggle("hot", i === best && st.mode === "ship"));
}

/* ---- フラッシュ計(幕 5)---- */
const fmEl = $("flashmeter");
function updateFlash(st) {
  const replaying = !!st.replay;
  fmEl.style.display = replaying ? "block" : "none";
  flash.visible = replaying;
  if (!replaying) { flash.scale.set(0.001, 0.001, 1); return; }
  const F = P.flashLaw(st.etaR, P.M31_DETA_TOT);
  const Fpk = P.flashLaw(12, P.M31_DETA_TOT);
  const o = clamp01((Math.log10(F) - CFG.flashLogFloor) /
                    (Math.log10(Fpk) - CFG.flashLogFloor));
  const s = 6 + 340 * Math.pow(o, 2.6);
  flash.scale.set(s, s, 1);
  flash.material.opacity = Math.pow(o, 1.4);
  $("fm-val").textContent = sci(F);
  $("fm-bar").style.width = (o * 100).toFixed(1) + "%";
  $("fm-tau").textContent =
    (P.flashDecaySeconds(12, 1000) * 1e12).toFixed(1) + " ps";
}

/* ================= 再生制御 ================= */
let playhead = 0, playing = true, lastNow = performance.now();
const qp = new URLSearchParams(location.search);
if (qp.has("act")) {
  const ai = Math.max(1, Math.min(5, +qp.get("act"))) - 1;
  playhead = ACTS.slice(0, ai).reduce((s, a) => s + a.dur, 0) + (+qp.get("t") || 0);
  if (qp.get("paused") === "1") playing = false;
}
function actOf(ph) {
  let acc = 0;
  for (let i = 0; i < ACTS.length; i++) {
    if (ph < acc + ACTS[i].dur) return { i, t: ph - acc };
    acc += ACTS[i].dur;
  }
  return { i: ACTS.length - 1, t: ACTS[ACTS.length - 1].dur - 1e-4 };
}
$("btn-play").onclick = () => {
  playing = !playing;
  $("btn-play").textContent = playing ? "⏸ 一時停止" : "⏵ 再生";
};
document.querySelectorAll("#controls button[data-act]").forEach(b => {
  b.onclick = () => {
    playhead = ACTS.slice(0, +b.dataset.act).reduce((s, a) => s + a.dur, 0);
    playing = true; $("btn-play").textContent = "⏸ 一時停止";
  };
});

const titleNo = document.querySelector("#act-title .no");
const titleName = document.querySelector("#act-title .name");
const capEl = $("caption");
let curActShown = -1, curCap = "";

/* ================= メインループ ================= */
function frame(now) {
  const dt = Math.min(0.05, (now - lastNow) / 1000);
  lastNow = now;
  if (playing) playhead = (playhead + dt) % TOTAL;
  const { i: act, t } = actOf(playhead);
  const st = stateAt(act, t);

  // 幕タイトル
  let actChanged = false;
  if (act !== curActShown) {
    actChanged = true;
    curActShown = act;
    titleNo.textContent = ACTS[act].no;
    titleName.textContent = ACTS[act].name;
    document.querySelectorAll("#controls button[data-act]").forEach(b =>
      b.classList.toggle("on", +b.dataset.act === act));
  }
  // 字幕
  let cap = "";
  for (const c of CAPTIONS) if (c.a === act && t >= c.t0 && t <= c.t1) cap = c.txt;
  if (st.mode === "dest" && !st.replay && st.wait !== undefined && !cap) {
    const yr = st.wait * P.M31_DIST_LY;
    cap = "経過 " + Math.round(yr).toLocaleString("ja-JP") + " 年 … 受信フラックス 0";
  }
  if (cap !== curCap) {
    curCap = cap;
    if (cap) { capEl.textContent = cap; capEl.classList.add("show"); }
    else capEl.classList.remove("show");
  }

  // シーン更新
  const shipMode = st.mode === "ship";
  ship.visible = shipMode; exMesh.visible = shipMode;
  m31.visible = shipMode; mw.visible = !shipMode;
  updateStars(shipMode ? st.eta : 0);
  if (shipMode) {
    updateExhaust(st, dt);
    const gs = lerp(22, 190, smooth(Math.pow(st.spent / 24, 0.55)));
    m31.scale.set(gs, gs, 1);
    ring.rotation.z += dt * 0.15;
  } else {
    exLight.intensity = 0;
  }
  updateFlash(st);
  updateHUD(st);

  // カメラ
  const ck = camKeys(act, t, st);
  if (actChanged || ck.cut) { camera.position.copy(ck.pos); }
  else { camera.position.lerp(ck.pos, 1 - Math.pow(0.0018, dt)); }
  camera.lookAt(ck.look);

  $("progress").style.width = (playhead / TOTAL * 100).toFixed(2) + "%";
  renderer.render(scene, camera);
  requestAnimationFrame(frame);
}
requestAnimationFrame(frame);

addEventListener("resize", () => {
  camera.aspect = innerWidth / innerHeight;
  camera.updateProjectionMatrix();
  renderer.setSize(innerWidth, innerHeight);
});
