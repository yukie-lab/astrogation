# Phase 2 入力ファイル形式仕様(PHASE_1.md 1-7)

Phase 2(観測署名)は**このディレクトリのファイルのみ**を入力とする(再計算禁止)。
すべて JSON。u は遅延時間 = Γ の固有時間、単位は付記のとおり。
生成コミットは各ファイルの `meta.commit` / `meta_commit`(`+dirty` は
生成時に未コミット差分があったことを示す — Phase 1 ゲートコミットで確定する)。

## 1. `mission_profiles/mission_<dest>_<maneuver>_eta<η>.json`

表 B の各行に対応するフルミッション(A4 規約: 定 λ=0.19 バーン+等速巡航)。

```
meta: {
  dest, dist_ly, maneuver ∈ {flyby, arrive, roundtrip}, eta,
  delta_eta_total,          # 燃料 Δη(= バーン回数 × η)
  x0, lambda_burn, R_ref_m, # A4 規約
  u_unit: "R_ref(幾何長)",  # u の単位は R_ref。SI 秒 = u × R_ref_m / c
  authority: {fuel, kinematics, burn_lambda},  # 権威ラベル(G2)
  g3: {mass_rel, ok},       # 質量閉形式との照合(1e-8)
  commit
}
grid: {                     # 同一長の配列。区分端点は u 重複あり(不連続表現)
  u,                        # 遅延時間 [R_ref]
  a,                        # 固有加速の大きさ(= λ、R=1 単位)
  m,                        # m(u)/m₀
  x,                        # 2m(u)/R
  eta_signed,               # 符号つきラピディティ(飛行軸方向)
  L,                        # ボロメトリック光度 −ṁ = 3mλ(無次元。SI W = L×c⁵/G)
  thrust_sign               # 推力方向 ∈ {+1, 0, −1}(飛行軸基準)
}
```

**排気軸の向き履歴**(Phase 2 の主入力): 排気ローブ(後方極、n² 最大)は
**−thrust_sign 方向**。角度分布は静止系で 4πn²(ϑ) = −ṁ − 3ma·cosϑ
(ϑ は加速軸から。v3 (13) [R])。固定系ではアベレーション(v3 App A)。
巡航中(thrust_sign = 0)は L = 0(news-silent かつ物質チャネルもゼロ)。

## 2. `timeopt_profiles/ride_x<x₀>_deta<Δη>_<tier>.json`

フロンティア騎乗の単一ブーストバーン(1-4 の主結果)。

```
tier ∈ {floor, effective, ceiling}, authority(tier のラベル), x0, deta,
u[], eta[], x[], lambda[], a[], m[], L[], thrust_sign[],
segment_labels[],           # 各格子点の権威ラベル([N] / ceiling-fallback[R] 等)
fallback_eta,               # [N]→天井フォールバック点(なければ null)
arcs[],                     # 拘束アーク構造 {eta0, eta1, label, lambda0, lambda1, x0, x1}
g3: {T_rel, xend_rel, ok},  # 求積 vs ODE + 長さ縮約照合
meta_commit
```

u は R 単位(x₀ の殻半径)。**天井 tier は到達不能な下限プロファイル**
(開条件)であり、実飛行計画には使えない(権威ラベルの言葉で扱うこと)。
床 tier のラベル [R(A3)/STOP-pending] は `docs/reports/P1_STOP_c_chain.md` 参照。

## 3. 併置データ(表・ログ)

- `tableA.csv/md`, `tableB.csv/md`, `tableB_eta50.csv`: 表本体(全行ラベルつき)
- `timeopt_bracket.csv/md`: 三層 T/R(G3 誤差列つき)
- `si_layer.csv/md`: SI 換算(units.py C7 認証済み経路のみ)
- `g3_log.md`: 全行 G3 照合の総括(欠番があれば理由つき)
