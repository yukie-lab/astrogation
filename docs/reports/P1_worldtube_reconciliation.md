# world_tube 照合報告(Phase 1 ゲート裁定 1・選択肢 3 の実施)

作成日: 2026-08-08。裁定 1(2026-08-08 人間ゲート)の条件 (a)(b)(c) に従う。

## 0. 二次オラクルの版固定

- リポジトリ: github.com/anindex/world_tube(CLAUDE.md §2 オラクル 5 として登録済み)
- 取得先: `~/research/world_tube`(warpax と同じ規約)
- **コミット固定: `1e9e3db`(2026-07-14、"Revise matching paper")**。全履歴 4 コミット
  (Initial release → Implement NK verification → Paper revision → Revise matching paper)
- MIT License(An T. Le, 2026)。README は arXiv:2606.22531 を対象と宣言、warpax ≥ 1.2 上に構築
- 注意: リポの anchor 名は「numbers shift at compile time」のため定理・式の**名前**で
  引かれるが、その一部("Prop *Status of the angular-dominance estimate*"、"g_rig")は
  **公開 v3 に存在しない名前**である。リポが対応する原稿状態は公開 v3 と完全一致しない
  可能性がある(前後いずれかはコミット履歴からは判定不能)

## 1. 主判定 — 裁定 1 条件 (c) 発動

**(68)-(73) の c(x) 定数鎖は公開著者コードに存在しない。**

検索プロトコル(再現可能): 全 *.py に対する
`NL_A / NL_B / B_star / polydisc / delta_Q / Cauchy / majorant / holomorph /
r_star / rho_Q / S_lambda / "quadratic root" / interval / 8.5e-5 / 1.7e-4`
の網羅 grep → 該当実装ゼロ(唯一のヒットは無関係な "free Cauchy data" 等)。
README の script→anchor 対応表(76–111 行)にも Lemma 6 / (48) / (73) に対応する
スクリプトが**ない**。App C 系のスクリプトは `frontier_analytics.py` /
`frontier_schauder.py` / `newton_kantorovich.py` の 3 本で、内容は frozen 展開
(M₀, c₁, c₂)・Schauder 構造・数値 NK チェックに限られる。

**したがって発見候補を昇格する(裁定 1(c))**:

> **v3 Lemma 6 の評価値 (73) c(x) ≈ {8.5, 14, 17, 14, 2.0}×10⁻⁵ は、
> 公開資料(論文本文+公開著者コード)から独立再現できない。**
> 律速は NL_A・NL_B・B⋆_m の具体形が本文(手続き記述のみ)にもコードにも
> 不在であること。

付随する未確定の緊張(過剰主張しない・二読み併記):
`frontier_analytics.py` [3] は「angular dominance は closed form を持たず
interval 全角度束縛が必要 — **g̲_rig は厳密下界に昇格しない**」と明記し、
`newton_kantorovich.py` は「η, K は浮動小数点推定であり interval 束縛ではない
— **完全に厳密な下界にはそれが必要**」と明記する。これらは frozen 診断系/
数値 NK チェックについての記述であり、Lemma 6 の c(x) と同一対象と断定は
できない。ただし、コードが厳密下界の成立に慎重な一方で v3 本文の Lemma 6 が
厳密性を主張し、その評価値の計算痕跡が公開されていない、という非対称は残る。
判断は人間の権限(CLAUDE.md §7)。

## 2. 照合で成立した相互検証(6 件)

| # | 対象 | 結果 |
|---|---|---|
| 1 | g̲ の 5 点: `worldtube.energy.FRONTIER_G` | **完全一致** {0.1: 0.19, 0.2: 0.20, 0.3: 0.19, 0.5: 0.14, 0.7: 0.09} = 我々の (S1) 転記 |
| 2 | (42) 極マージン: `_axial_margin` | **逐語一致** 3s−3+2.5x+7·sign·λ−sign·sλ/(1−sign·λ)、s=√(1−x−2·sign·λ) = 台帳 L23 |
| 3 | v3 Lemma 5 の引用値 | 我々の転記のみから独立再計算: **λ_DEC/天井 最大比 0.9931 at x = 0.6308**(v3: 0.9931 at x≈0.631)— 厳密再現 |
| 4 | λ̄_DEC の 1% 主張 | 適用域 x ∈ [24/35, 0.84] で最大 1.008%(v3 の「x ≲ 0.84 で 1% より良い」と整合。注意: 全域では小 x で比 3/4 = (44) の明示内容 — 主張の適用域を誤ると 25% に見える) |
| 5 | M₀, c₁, c₂((61) 系) | リポは sympy で紙の閉形式と一致を assert(我々の C 系転記と同型) |
| 6 | **D(x) の撤回** | `existence_ift.py` が明文で確認: "There is no closed-form 'bifurcation scalar D(x)': that object mixed the ell=0 jump ... into an ell=1 determinant and **is not the existence obstruction**" — **Phase L の発見(L2 §4.1)と C3 再定義(L6)・考古学隔離の著者側独立確認** |

## 3. 措置(裁定 1 の条件どおり)

- (a) 床 tier は **c_cons [R(A3)/STOP-pending] を継続**(カタログ・図・ラベル変更なし)
- (b) 「(73) は本文のみから再現不能」の発見候補は**記録維持** — 本照合により
  「**本文+公開コードから再現不能**」へ強化
- (c) **STOP は継続**。`P1_STOP_c_chain.md` に本報告への参照を追記済み

## 4. 人間への提案(次の一手の選択肢)

1. **著者照会**(発見候補の検証として最短: NL_A/NL_B/B⋆_m の具体形と (73) の
   計算スクリプトの所在を問う。D(x) 撤回確認・相互検証 6 件は照会の信頼性を支える)
2. 現状維持で Phase 2 へ(Phase 2 は床 tier 非依存 — L8 依存グラフ。c_cons 併記のまま)
3. 論文化時に「(73) は公開資料から再現不能、保守的独立床 c_cons を構成した」を
   結果として記載(選択肢 1 の回答があれば差し替え)
