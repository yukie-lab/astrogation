/*
 * P4-C20 — スナップショット認証(PHASE_4 物理層)。
 *
 * results/ の代表行(全精度で転記)と physics.js の閉形式出力を
 * 相対 1e-10 で照合する。緑になるまで描画コードを書いてはならない。
 * 実行: `node test_snapshot.js`(CI/手元)または test_snapshot.html(ブラウザ)。
 *
 * スナップショットの出典(リポジトリ tag v1.0-paper の results/):
 *  - signatures/sig_mission_m31_arrive_eta12.0.json(dest/side/depart の
 *    F_peak と、そのピーク節点の mission grid 状態タプル)
 *  - signatures/sig_mission_proxima_arrive_eta1.0.json(同上 — 論文 Fig.4)
 *  - mission_profiles/mission_m31_arrive_eta12.0.json(m_f・x 履歴)
 *  - paper/numbers.tex の FlashPeak/FlashDecay 系(閉形式検証値)
 *  - appc_floor.c_floor_conservative の 5 点(physics.js 埋込値と同一系列)
 */
"use strict";
const P = (typeof PHYS !== "undefined") ? PHYS : require("./physics.js");

const SNAP = {
  m31: {
    detaTot: 24.0,
    m_f: 5.380186160021139e-32,          // grid m 終端(= e^(−72))
    x_f: 1.6140558480063416e-32,         // grid x 終端(= 0.3e^(−72))
    x_after_accel: 6.958568490730708e-17, // grid x[101](= 0.3e^(−36))
    dest:   { F: 14764.840852748175,
              s: [1.3221280132388348e-16, 2.3195228302435696e-16, 0.19, -1, 12.0] },
    side:   { F: 0.04535915878119018,
              s: [0.5700000000000001, 1.0, 0.19, 1, 0.0] },
    depart: { F: 0.09071831756238036,
              s: [0.5700000000000001, 1.0, 0.19, 1, 0.0] },
    flashDecayScale: 4.619708536336999e-06, // e^(−12)/(7·0.19)
    deltaHeadOn12: 162754.79141900392,      // e^12
  },
  proxima: {
    detaTot: 2.0,
    m_f: 0.0024787521766663585,          // e^(−6)
    dest:   { F: 0.24659795413819555,
              s: [0.02837862896968245, 0.049787068367863944, 0.19, -1, 1.0] },
    side:   { F: 0.04535915878119018,
              s: [0.5700000000000001, 1.0, 0.19, 1, 0.0] },
    depart: { F: 0.09071831756238036,
              s: [0.5700000000000001, 1.0, 0.19, 1, 0.0] },
  },
  tiers: {
    gNodes: [[0.1, 0.19], [0.2, 0.20], [0.3, 0.19], [0.5, 0.14], [0.7, 0.09]],
    ceiling03: 0.25,                     // (0.8−0.3)/2
    cNodes: [[0.1, 6.21798378391627e-05], [0.2, 9.349526382222707e-05],
             [0.3, 0.0001012029453926463], [0.5, 6.751056578638111e-05],
             [0.7, 4.295637511263454e-06]],
  },
};

const TOL = 1e-10;
const results = [];
function check(name, got, want, tol = TOL) {
  const scale = Math.max(1e-300, Math.abs(want));
  const rel = Math.abs(got - want) / scale;
  results.push({ name, got, want, rel, pass: rel <= tol });
}
function checkExactZero(name, got) {
  results.push({ name, got, want: 0, rel: Math.abs(got), pass: got === 0 });
}

function run() {
  results.length = 0;
  const vOf = { dest: 0.0, side: 0.5, depart: 1.0 };

  // --- 質量・コンパクト度履歴(M31・プロキシマ)
  check("m31: m(24) = m_f", P.m(SNAP.m31.detaTot), SNAP.m31.m_f);
  check("m31: x(24) = x_f", P.x(SNAP.m31.detaTot), SNAP.m31.x_f);
  check("m31: x(12) = 加速後", P.x(12.0), SNAP.m31.x_after_accel);
  check("proxima: m(2) = m_f", P.m(SNAP.proxima.detaTot), SNAP.proxima.m_f);

  // --- 観測者写像: 署名カタログのピーク行を状態タプルから再現
  for (const ds of ["m31", "proxima"]) {
    for (const tag of ["dest", "side", "depart"]) {
      const { F, s } = SNAP[ds][tag];
      const got = P.observedFluxV(s[0], s[1], s[2], s[3], s[4], vOf[tag]);
      check(`${ds}/${tag}: F_peak 再現`, got, F);
    }
  }

  // --- 減速フラッシュ: 閉形式則がカタログピークと一致(二経路)
  check("m31: flashLaw(12, 24) = F_peak(dest)",
        P.flashLaw(12.0, SNAP.m31.detaTot), SNAP.m31.dest.F);
  check("m31: 減衰スケール e^(−η)/(7λ)",
        P.flashDecayScale(12.0), SNAP.m31.flashDecayScale);
  check("m31: δ(θ=0) = e^12", P.deltaHeadOn(12.0), SNAP.m31.deltaHeadOn12);

  // --- 前方ヌル(仲裁規則の物理側): 飽和加速は正面で厳密ゼロ
  checkExactZero("前方ヌル: saturatedPattern(cos=1)",
                 P.saturatedPattern(1.0, 0.19, 1.0));
  checkExactZero("前方ヌル: observedFluxV(飽和, s=+1, v=0)",
                 P.observedFluxV(3 * 1.0 * 0.19, 1.0, 0.19, 1, 5.0, 0.0));
  checkExactZero("巡航消灯: observedFluxV(L=0, a=0)",
                 P.observedFluxV(0.0, 0.5, 0.0, 0, 2.0, 0.3));

  // --- 三層
  for (const [xv, gv] of SNAP.tiers.gNodes) {
    check(`g̲(${xv}) 数表`, P.gLower(xv), gv, 1e-14);
  }
  check("ceiling(0.3)", P.ceiling(0.3), SNAP.tiers.ceiling03, 1e-14);
  for (const [xv, cv] of SNAP.tiers.cNodes) {
    check(`c_cons(${xv}) 5 点`, P.cCons(xv), cv, 1e-14);
  }
  check("g̲ 域外フォールバック(x=0.05 → 天井)",
        P.gLower(0.05), P.ceiling(0.05), 1e-14);

  // --- 計器盤カタログ量(HUD 供給値の認証)
  // η₅₀(M31)= arcsinh(2.54e6/50)。カタログ CSV 値(バーン補正込み)と
  // 巡航支配閉形式の一致は論文 C14/C19 で確立済み — ここでは転記値と照合
  check("HUD: etaFifty(M31, 50yr)", P.etaFifty(P.M31_DIST_LY, 50.0),
        11.52879881422351, 1e-10);
  check("HUD: seatPrice(0.24) = e^0.48", P.seatPrice(0.24),
        1.6160744021928936, 1e-12);
  // 減衰の SI 換算(R=1 km で ~15 ps — 論文 Sec. IV.E の表示値スケール)
  check("HUD: flashDecaySeconds(12, 1 km)", P.flashDecaySeconds(12.0, 1000.0),
        1.5409688980024305e-11, 1e-12);

  // --- 到着時間圧縮の恒等: dt_obs/du(v=0) = e^(−η) = 1/δ
  check("dt_obs/du(0, 12) = e^(−12)", P.dtObsDu(0.0, 12.0),
        1.0 / SNAP.m31.deltaHeadOn12, 1e-12);

  return results;
}

if (typeof module !== "undefined" && require.main === module) {
  const rs = run();
  let fail = 0;
  for (const r of rs) {
    if (!r.pass) fail++;
    console.log(`${r.pass ? "PASS" : "FAIL"}  ${r.name}` +
                (r.pass ? "" : `  got=${r.got} want=${r.want} rel=${r.rel}`));
  }
  console.log(`\nP4-C20: ${rs.length - fail}/${rs.length} passed` +
              (fail ? `  (${fail} FAILED)` : "  — ALL GREEN"));
  process.exit(fail ? 1 : 0);
}
if (typeof window !== "undefined") window.SNAPSHOT_RUN = run;
