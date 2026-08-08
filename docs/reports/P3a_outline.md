# P3a — 論文アウトライン(3a ゲート提出物)

作成日: 2026-08-09。英語正本の骨格。各節: **主張 1 行** / 使用成果物 / 注入数値。
文体規則(PHASE_3.md)適用済み: 自己評価形容詞なし・新規性は検索事実で記述・
(73) は事実記述のみ・装置予測なし。

## 0. タイトル候補(英語正本)

- **A(推奨)**: *Interstellar flight profiles and observational signatures of
  positive-energy warp shells*
- B: *Admissibility-constrained maneuver catalogs for the radiative momentum
  warpshell, with light curves and a gravitational-wave silence discriminator*
- C: *Timetables for a positive-energy warp shell: constrained interstellar
  maneuvers and their transients*

日本語版(3c): 「正エネルギーワープシェルの恒星間飛行プロファイルと観測署名」

著者: 単著(Independent Researcher, Tokyo)+ ORCID【人間入力: チェックリスト項目】。

## 1. Abstract(6 文の設計)

1. 文脈: 加速する正エネルギー warpshell の存在は確立された(Le 2026)が、
   その許容性制約の下での実恒星間航路は計算されていなかった
2. 検索事実: 被引用スキャン・全文精読・公開著者コード検査の系統的検索で
   該当計算の不在を確認した(日付つき)
3. 成果 1: 拘束全課の航路カタログ(ラピディティ階段・50 年等高線
   {M31Eta50}・質量比 {M31MfFlyby}・三層時間最適と交差 x* = {XStar})
4. 成果 2: 署名カタログ(前方厳密ヌル → 減速フラッシュ δ⁴ = e^(4η)、
   一般減衰則 **F ∝ e^(7η−3Δη_tot)**(M31 到着 Δη_tot = 24 で e^(7η−72) を実例化)、
   ps 級時間構造、GW 静寂判別子)
5. 方法: 認証 C1–C18・二経路 G3({G3RowsTotal} 行・欠番ゼロ)・権威ラベル・
   人間ゲート付き AI プロトコル。world_tube との相互検証 6 件と (73) の
   再現性ギャップ(事実記述)
6. 公開: 全カタログ・コード・再現手順(Zenodo/GitHub、機械注入数値)

## 2. 節構成(主張 1 行+成果物対応)

### §1 Introduction
**主張**: 「殻構造の証明系譜と点質量軌道計算の系譜は接続されておらず、
系統的検索でも接続した研究は存在しない — 本論文がその計算を実行する。」
- 1.1 系譜: Alcubierre [R1] → no-go 群(SSV・Lobo–Visser・Pfenning–Ford)→
  Bobrick–Martire → Warp Factory(Fuchs/Helmerich)→ Füzfa(点ロケット軌道)
  → Le(存在定理+コスト法則)。Lentz 反証の帰属は **SSV [3] + Celmaster–
  Rubin [15] の二段**(EXT1 ③ の確定形)
- 1.2 検索事実(新規性): L3(Semantic Scholar/INSPIRE 被引用 0、クエリ・
  日付記録)+ v3 全文の "interstellar"/"future work" 全出現照合(EXT1 ①)+
  world_tube 全走査。**使用禁止表現を含まない**: 「不在の系統的確認」として記述
- 1.3 貢献 4 点(素の列挙): (i) 拘束全課カタログ、(ii) 三層時間最適と
  レジーム交差、(iii) 署名カタログと GW 判別子、(iv) 検証方法論と
  相互検証・再現性ギャップの記録
- 使用: なし(引用のみ)

### §2 Framework(引用ベース要約 — 再導出なし)
**主張**: 「Le の閉形式群(制御則・予算・天井・窓)と数値フロンティアを、
権威ラベル [R]/[N]/[H] の相続制度の下で拘束体系として採用する。」
- 2.1 radiative momentum warpshell の要約(v3 (13)(14)(15)(25)(40)、§10 窓)
- 2.2 三層拘束: 床 c_cons [R(A3)/暫定]・実効 g̲ [N]・天井 min(½(1−x),(4/5−x)/2) [R]
- **Table I**: 三層の定義・ラベル・定義域(results/timeopt_bracket 由来の定義部
  + g̲/c 数表)
- 注入: g̲ 5 点 {GLowerTable}、c(73) 5 点 {CPaperTable}、c_cons 5 点 {CConsTable}

### §3 Methods
**主張**: 「全数値は認証済み部品と二経路照合から機械注入され、AI の全作業は
人間ゲートで裁定された。」
- 3.1 オラクル制・式台帳・認証 C1–C18・G3(許容と実測: {G3WorstTable})・
  数値パイプライン(manifest、P3-C19)。**騎乗クラスの写像 G3 許容 2e-6 は
  明示開示する**: 理由 = 消費データのグリッド情報限界(g̲ 折れ線の節点が
  グリッド区間内に落ちるキンク+序盤 λ 勾配の複合、再計算禁止下)であり
  実装誤差ではない。**2026-08-09 人間ゲートで事後承認**(CLAUDE.md §6 の
  許容誤差変更規定)— 論文でもこの二点(機構と人間裁定)を記載する
- 3.2 **AI 開示段落**(1 段落、事実形): 計算・実装・起草は Claude(Fable 5,
  Anthropic)が人間ゲート付きプロトコルで実施。各フェーズ成果物は明示的
  ゲートで人間が承認。数値は手打ちゼロ(機械注入+照合テスト)
- 3.3 検証実績: world_tube(コミット {WtCommit} 固定)との相互検証 6 件
  (FRONTIER_G 一致・(42) 逐語一致・Lemma 5 の 0.9931@0.631 独立再現・
  1% 主張の適用域確認・M₀c₁c₂・**v2→v3 の D(x) 撤回の著者側確認**)。
  **(73)**: 「本文と公開コードから独立再現できなかった(必要な上限 3 量が
  いずれにも閉形式で与えられていない)。保守的独立床 c_cons を構成し、
  暫定ラベルで運用した」— 誤り断定なし、裁定継続の明記
- 使用: `P1_worldtube_reconciliation.md`・`P1_STOP_c_chain.md` の内容

### §4 Results(4 小節)
- **4.1 ラピディティ階段** — 主張: 「燃料は距離非依存で、乗客殻の座席の値段は
  理想光子ロケット比 e^(2η) である。」
  **Table II** ← tableA.csv(η ∈ {0.24, 1, 3, 5, 8, 12} に圧縮)。
  注入: {Eta024Radiated}=51.3%、{SeatPriceEta12}
- **4.2 ミッション表と 50 年等高線** — 主張: 「寿命内条件は閉形式運動学で
  等高線化でき、M31 flyby は η = {M31Eta50}・質量比 {M31MfFlyby}、
  到着型は指数が倍化する。」
  **Table III** ← tableB_eta50.csv(4 行き先 × 3 機動)。**Fig. 1** ←
  fig3_missions_tau(EN 版再生成)。注入: 等高線 12 値
- **4.3 三層時間最適とレジーム交差** — 主張: 「min-time は全区間拘束弧の
  フロンティア騎乗であり、操作的拘束は x* = {XStar} で薄殻 [N] から
  厚壁 [R] に切り替わる。我々の知る限り(§1.2 の系統的検索の範囲で)
この交差の定量化は本カタログが初である(to our knowledge 形で記述)。」
  **Fig. 2** ← fig1_tiers、**Fig. 3** ← fig2_timeopt_bracket、
  **Table IV** ← timeopt_bracket.csv(x₀ = 0.3)。
  注入: {EtaFallback}=ln(x₀/0.1)/3、床/実効/天井 T 値、{XStar}, {LamStar}
- **4.4 SI レイヤー** — 主張: 「R = 1 km・x₀ = 0.3 の殻は {ShellMassMsun} M☉ で、
  実効騎乗ピーク光度は {LPeakW} W = {LPeakLsun} L☉、バーン時間は μs 級。」
  **Table V** ← si_layer.csv。注入: 質量 3 点・光度・バーン時間
- **4.5 観測署名** — 主張: 「飽和加速は前方厳密ヌル(Fraction 認証)で、
  到着減速は δ⁴ = e^(4η) 増幅・e^(−η) 時間圧縮のフラッシュ
  (一般則 F ∝ e^(7η−3Δη_tot) [導出: m = e^(3η−3Δη_tot) × δ⁴。
  M31 Δη_tot = 24 で e^(7η−72)]、高 η で ps 級)として現れる。」
  **Fig. 4** ← sig1、**Fig. 5** ← sig2、**Fig. 6** ← sig3。
  注入: {M31FlashPeak}、{FlashDecayR}(変換規則: e^(−η)/(7λ)、manifest 記録)、
  {SigRows}=567・写像 G3 実測
- **4.6 GW 静寂判別子** — 主張: 「純双極子機動は Ψ₄ 厳密静寂であり、
  『測光過渡+GW 無検出』が反証可能な予言、同時に機動純度の検査である。」
  引用: v3 Thm 5/App H・Damour 1995・(94)。対比: Clough et al.(崩壊バースト)

### §5 Discussion
**主張**: 「本カタログの適用限界は権威ラベルが機械的に示し、時間-光度平面で
既知過渡と幾何的に重ならない。」
- 5.1 限界: 加速厚壁は v3 自身の future work(この文脈でのみ使用可 —
  実在する v3 の記述)・[N] 定義域 x ∈ [0.1, 0.7]・ボロメトリック限定・
  床 tier 裁定継続・仮定 A2–A5 の列挙
- 5.2 時間-光度平面: μs–ps・単発・GW 無音・前方ヌル→フラッシュ対 —
  物理的特徴の対比(装置予測なし)
- 5.3 技術署名の示唆(TECHNOSIGNATURE_SUMMARY の範囲)
- 5.4 (73) ギャップの再掲+照合への招待(事実形)

### §6 Data availability / §7 Acknowledgments
- Zenodo DOI【3c で取得】・GitHub・コミットハッシュ・再現手順(認証スイート)
- 謝辞: warpax / world_tube(MIT、An T. Le)・AI 支援明記。引用義務: CLAUDE.md
  §12 全件+Damour 1995(EXT1 ⑥ 追加済み)

## 3. 図表の最終対応(6 図 5 表)

| 論文 | 出典(results/) | 3b 作業 |
|---|---|---|
| Fig.1 | figures/fig3_missions_tau.png | EN ラベル版を同スクリプトで再生成(データ不変) |
| Fig.2 | figures/fig1_tiers.png | 同上(x* 注記込み) |
| Fig.3 | figures/fig2_timeopt_bracket.png | 同上 |
| Fig.4–6 | signatures/figures/sig1–3 | 同上 |
| Table I–V | 三層定義 / tableA / tableB_eta50 / timeopt_bracket / si_layer | CSV → 生成 LaTeX |

図の再生成は**ラベル文字列のみ**の変更(スクリプトの label 引数化。データ経路
不変 — P3-C19 が図キャプション数値も manifest 照合)。

## 4. 数値マニフェスト設計(P3-C19)

`scripts/make_paper_numbers.py` が results/ から `paper_numbers_manifest.json` と
`paper/numbers.tex`(\newcommand 群)を生成する。原稿は \Nm〜 マクロのみ使用。
- エントリ形式: {macro, value_displayed, source_file, source_field, transform}
  (transform 例: "round(η,2)"、"×c⁵/G→W 2桁"、"e^(−η)/(7λ) [P2 §2 の閉形式]")
- P3-C19: (i) 原稿 .tex に裸の数値リテラルがないこと(正規表現走査、
  例外リスト: 式番号・参照番号・年)、(ii) manifest の全値が source から
  transform で再計算一致すること
- 主要マクロ(抜粋 25 件): M31Eta50=11.53, M31MfFlyby=1.0e-15,
  SgrEta50=6.947, XStar=0.54, LamStar=0.13, EtaFallback=0.366,
  LPeakW=3.1e51, LPeakLsun=8.1e24, ShellMassMsun=0.102,
  Eta024Radiated=51.3%, TFloor024=2.58e3, TEff024=1.22, TCeil024=0.824,
  G3RowsP1=306, SigRows=567, MapWorstMission=5.0e-15, MapWorstRide=1.06e-6,
  FlashDecayR≈5e-6, WtCommit=1e9e3db, GLower/CPaper/CCons 各 5 点,
  FlashExpM31=72(transform: 3×delta_eta_total)
- **M31FlashPeak の transform(確定)**: 一次ソース =
  `signatures/sig_mission_m31_arrive_eta12.0.json` → angles.dest.F_peak、
  表示 = 3 有効数字(1.48e4)。**検証 transform** = 閉形式
  (6λ/4π)·e^(7η−3Δη_tot)|_{η=12, Δη_tot=24, λ=0.19}(グリッドのピーク節点は
  バーン開始 η=12 に一致するため相対 <1e-12 で一致すべき)— manifest に
  一次ソースと検証 transform の両方を記録し、P3-C19 が両者を照合する

## 5. 固定文言(3b で逐語使用する承認対象)

1. **新規性(EN)**: "A systematic search — a citation scan of
   arXiv:2606.22531 (Semantic Scholar and INSPIRE-HEP, 2026-08-08, zero
   citing records), a full-text survey of v3, and an inspection of the
   author's public reproduction code at commit {WtCommit} — found no
   published computation of interstellar flight profiles under the shell's
   admissibility constraints."(ダッシュ使用は本節 1 回のみの割当)
2. **(73) ギャップ(EN)**: "The evaluated floor values of Eq. (73) could not
   be independently reproduced from the paper text and the public code; the
   three suprema they require are described procedurally in both sources but
   given in closed form in neither. We therefore constructed a conservative
   independent floor and label it provisionally."
3. **AI 開示(EN)**: "All computations, implementations, and manuscript
   drafting were performed by Claude (Fable 5, Anthropic) under a
   human-gated protocol: every phase deliverable was reviewed and approved
   at explicit human decision gates, all numerical claims are
   machine-injected from the certified catalogs, and tolerance changes were
   themselves human-gate items."

4. **x* 第一主張のヘッジ(EN)**: "To our knowledge, within the scope of
   the systematic search described in Sec. I, this crossover has not been
   quantified before."(x* の初出主張は必ずこの形+§1.2 参照で書く。
   無限定の "first" は使用しない)

## 6. リスクと 3b への注意

- 禁止語スキャン対象: novel/remarkable/fascinating/delve/groundbreaking +
  ダッシュ頻度(1 節 1 回)+ "In this paper" 重複 — 3b で lint スクリプト化
- 「future work」は **v3 自身の記述の引用としてのみ**使用可(加速厚壁・
  O(μ²)・回転軸)。航路計算の文脈では全面禁止(EXT1 ①)
- STOP 監視: 執筆中に権威ラベル無き主張が必要になったら停止(PHASE_3.md)

---

**承認をお願いします**: (a) タイトル候補(推奨 A)、(b) 節構成と主張行、
(c) 図表対応、(d) manifest 設計、(e) 固定文言 1–3。
