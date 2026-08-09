/*
 * physics.js — シミュレータの単一真実源(PHASE_4 物理層)。
 *
 * ここにある式はすべて認証済みカタログ(github.com/yukie-lab/astrogation、
 * tag v1.0-paper)の閉形式の移植であり、新しい物理は一つも含まれない。
 * 対応: 式台帳 L6/L14/L19/L31/L43-L48(論文 Sec. II, IV.E)。
 * 数値安定性は Python 実装(radiometry.py)と同じ半角符号化
 * v = sin^2(θ/2) を用いる(μ≈±1 の桁落ち回避)。
 * HUD・計器盤の全数値は本モジュールの出力であること(ダミー禁止)。
 * 検証: test_snapshot.html / node test_snapshot.js(P4-C20、相対 1e-10)。
 */
"use strict";

const PHYS = (() => {
  const FOUR_PI = 4 * Math.PI;

  // ---- カタログ定数(出典コメント付き) ----
  const X0 = 0.3;            // ミッション規約 A4(アンカー)
  const LAMBDA_BURN = 0.19;  // g̲(0.3) [N](A4 バーン規約)
  const M31_DETA_TOT = 24.0; // M31 到着 Δη_tot = 2η(η=12)

  // g̲(x) [N] — v3 (S1)(サンプル域 [0.1, 0.7]、線形補間)
  const G_X = [0.1, 0.2, 0.3, 0.5, 0.7];
  const G_V = [0.19, 0.20, 0.19, 0.14, 0.09];

  // c_cons(x) [R(A3)/暫定] — appc_floor.c_floor_conservative の 5 点評価
  // (全精度スナップショット。中間は表示用線形補間、域外は端点クランプ)
  const C_X = [0.1, 0.2, 0.3, 0.5, 0.7];
  const C_V = [6.21798378391627e-05, 9.349526382222707e-05,
               0.0001012029453926463, 6.751056578638111e-05,
               4.295637511263454e-06];

  // ---- 質量・コンパクト度(Tsiolkovsky、L6/(15)) ----
  const m = (eta, m0 = 1.0) => m0 * Math.exp(-3 * eta);
  const x = (eta, x0 = X0) => x0 * Math.exp(-3 * eta);

  // ---- 三層拘束(論文 Table I) ----
  // 天井 [R] = min(½(1−x), ½(4/5−x)) ≡ (4/5−x)/2(台帳 L42)
  const ceiling = (xv) => Math.min(0.5 * (1 - xv), 0.5 * (0.8 - xv));

  function interp(xs, vs, xv) {
    if (xv <= xs[0]) return vs[0];
    if (xv >= xs[xs.length - 1]) return vs[vs.length - 1];
    for (let i = 0; i < xs.length - 1; i++) {
      if (xv <= xs[i + 1]) {
        const t = (xv - xs[i]) / (xs[i + 1] - xs[i]);
        return vs[i] * (1 - t) + vs[i + 1] * t;
      }
    }
    return vs[vs.length - 1];
  }

  // 実効 [N]: 数表線形補間、域外は天井へフォールバック(PHASE_4 物理層仕様)
  const gLower = (xv) =>
    (xv < G_X[0] || xv > G_X[G_X.length - 1]) ? ceiling(xv)
                                              : interp(G_X, G_V, xv);

  // 床 [R(A3)/暫定]: 5 点線形補間(域外は端点クランプ — 表示用)
  const cCons = (xv) => interp(C_X, C_V, xv);

  const lambdaTier = (xv, tier) =>
    tier === "ceiling" ? ceiling(xv)
      : tier === "effective" ? Math.min(gLower(xv), ceiling(xv))
      : Math.min(cCons(xv), ceiling(xv));

  // ---- 静止系パターン(v3 (13)、L48) ----
  // n² = [L − 3 m a cosϑ′]/4π。飽和(L = 3ma): 3ma(1 − cosϑ′)/4π —
  // 前方(cosϑ′ = 1)で厳密ゼロ。
  const patternN2 = (L, mm, a, cosPat) => (L - 3 * mm * a * cosPat) / FOUR_PI;
  const saturatedPattern = (mm, lam, cosTheta) =>
    3 * mm * lam * (1 - cosTheta) / FOUR_PI;

  // ---- 観測者写像(半角符号化、L43-L45) ----
  // v = sin²(θ_obs/2): 目的地 0 / 側方 ½ / 出発地 1
  const invDopplerV = (v, eta) =>
    v * Math.exp(eta) + (1 - v) * Math.exp(-eta);
  const aberrateV = (v, eta) => {
    const num = v * Math.exp(eta);
    return num / (num + (1 - v) * Math.exp(-eta));
  };
  // F·D² = δ⁴·n²(ϑ′)、cosϑ′ = s·(1 − 2v′)(L44)
  function observedFluxV(L, mm, a, thrustSign, eta, v) {
    const vP = aberrateV(v, eta);
    const cz = 1 - 2 * vP;
    const cosPat = thrustSign !== 0 ? thrustSign * cz : cz;
    const n2 = patternN2(L, mm, a, cosPat);
    const invD = invDopplerV(v, eta);
    return n2 / (invD * invD * invD * invD);
  }
  // dt_obs/du = γ(1−βμ) = 1/δ(L45)。v=0 で e^(−η)(到着時間圧縮)
  const dtObsDu = (v, eta) => invDopplerV(v, eta);
  const deltaHeadOn = (eta) => Math.exp(eta);   // δ(θ=0) = e^η

  // ---- 減速フラッシュ(論文 Sec. IV.E) ----
  // F·D² = (6λ/4π)·e^(7η − 3Δη_tot)(飽和減速脚、目的地正面)
  const flashLaw = (eta, detaTot, lam = LAMBDA_BURN) =>
    (6 * lam / FOUR_PI) * Math.exp(7 * eta - 3 * detaTot);
  // 減衰スケール ~ e^(−η)/(7λ)(t_obs 単位、R=1)
  const flashDecayScale = (eta, lam = LAMBDA_BURN) =>
    Math.exp(-eta) / (7 * lam);

  // ---- 星野用の相対論(β・光行差・ドップラー — 演出層が消費) ----
  const beta = (eta) => Math.tanh(eta);
  const gammaOf = (eta) => Math.cosh(eta);

  return {
    X0, LAMBDA_BURN, M31_DETA_TOT, G_X, G_V, C_X, C_V,
    m, x, ceiling, gLower, cCons, lambdaTier,
    patternN2, saturatedPattern,
    invDopplerV, aberrateV, observedFluxV, dtObsDu, deltaHeadOn,
    flashLaw, flashDecayScale, beta, gammaOf,
  };
})();

if (typeof module !== "undefined" && module.exports) module.exports = PHYS;
