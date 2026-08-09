/*
 * skyframe.js — 実天球 → 船首フレームの座標変換(Phase 4 改訂 (1))。
 *
 * 船首方位は M31 の実座標(RA 0h42.7m, Dec +41°16′ — 指示書指定値)。
 * 変換は純幾何(回転のみ)で、物理は含まない。全星を無限遠(視差ゼロ)
 * として扱う単純化は README の境界宣言に記載。
 * 出力は physics.js の観測者写像と同じ半角符号化:
 *   v = sin²(θ/2)(θ は船首からの角、M31 が v = 0 の前方極)
 *   φ = 船首まわりの方位(screen up = 天の北極の射影)
 * 認証: P4-C20 に「光行差ゼロ時に M31 方向が画面正面と一致」の項がある。
 */
"use strict";

const SKY = (() => {
  const D2R = Math.PI / 180;
  const M31_RA_DEG = 15.0 * (0 + 42.7 / 60.0);   // 0h42.7m = 10.675°
  const M31_DEC_DEG = 41.0 + 16.0 / 60.0;        // +41°16′ = 41.2667°

  const unitVec = (raDeg, decDeg) => {
    const a = raDeg * D2R, d = decDeg * D2R;
    return [Math.cos(d) * Math.cos(a), Math.cos(d) * Math.sin(a), Math.sin(d)];
  };
  const dot = (u, w) => u[0] * w[0] + u[1] * w[1] + u[2] * w[2];
  const cross = (u, w) => [u[1] * w[2] - u[2] * w[1],
                           u[2] * w[0] - u[0] * w[2],
                           u[0] * w[1] - u[1] * w[0]];
  const norm = (u) => {
    const n = Math.hypot(u[0], u[1], u[2]);
    return [u[0] / n, u[1] / n, u[2] / n];
  };

  // 船首基底: f = M31 方向(前方 +z)、e2 = 天の北極の射影(screen up)、
  // e1 = e2 × f(screen right、右手系)
  const f = norm(unitVec(M31_RA_DEG, M31_DEC_DEG));
  const pole = [0, 0, 1];
  const e2 = norm([pole[0] - dot(pole, f) * f[0],
                   pole[1] - dot(pole, f) * f[1],
                   pole[2] - dot(pole, f) * f[2]]);
  const e1 = norm(cross(e2, f));

  // 実天球座標 → {v, phi}(半角符号化+方位)
  function shipFrameVPhi(raDeg, decDeg) {
    const s = unitVec(raDeg, decDeg);
    const cz = Math.max(-1, Math.min(1, dot(s, f)));
    return { v: (1 - cz) / 2, phi: Math.atan2(dot(s, e2), dot(s, e1)) };
  }

  return { M31_RA_DEG, M31_DEC_DEG, shipFrameVPhi };
})();

if (typeof module !== "undefined" && module.exports) module.exports = SKY;
if (typeof window !== "undefined") window.SKY = SKY;
