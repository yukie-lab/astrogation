# PHASE 0 — 検証ハーネス

> 前提: Phase L ゲート承認済み。式台帳(L2)が唯一の式の供給源。
> このフェーズで**新しい物理計算はしない**。ミッションプロファイルの
> 積分も、署名計算も、Phase 1 以降の仕事である。

## 目的

論文の閉形式群を小さな Python ライブラリとして実装し、
**論文記載の数値を再現する認証テスト(CLAUDE.md §4 の C1〜C6)を
全緑にする。** ここで作る「認証済みの部品」だけが Phase 1 以降で
使用を許される。

## タスク

### 0-1. conventions.md の作成
CLAUDE.md §3 の骨格を実体化する。単位換算モジュール
(`src/astrogation/units.py`)を先に書き、幾何単位 ↔ SI ↔ 天文単位
(ly, yr, M☉)の往復テストを付ける。

### 0-2. ライブラリ骨格
```
src/astrogation/
  units.py        # 単位換算(一元管理)
  control.py      # 制御則・Tsiolkovsky・n²(θ) 角度分布
  shell.py        # 静的殻 σ₀/p₀・DEC マージン・D(x)
  frontier.py     # 天井 [R]・厚壁窓 [R]・g̲(x) 数表 [N]・包絡線 [H]
  geodesy.py      # H³ 距離・測地線・ラピディティ
  bondi.py        # Bondi 予算(閉形式)+ warpax クロスチェック接続
```
- 全関数の docstring に **v3 式番号と権威ラベル**を併記
- `frontier.py` の g̲(x) は式台帳の数表のみを補間(範囲外は例外を送出。
  外挿は実装レベルで不可能にする)

### 0-3. 認証テストスイート
`tests/test_certification.py` に C1〜C6 を実装(CLAUDE.md §4 の表と
許容誤差に従う)。追加で:

- **C7(単位往復)**: 幾何単位 ↔ SI の往復で相対誤差 < 1e-12
- **C8(G3 二経路・初回)**: Tsiolkovsky を閉形式 vs 制御則 ODE 積分で
  一致確認(相対 < 1e-8)。warpax.bondi との突合は接続のみ確認し、
  本格運用は Phase 1

### 0-4. 認証レポート
`docs/reports/P0_certification.md`: 各認証の対象式(v3 番号)・
論文記載値・計算値・誤差・判定を一表に。pytest 出力を添付。

## 完了定義(DoD)

- [ ] conventions.md 完成(人間承認待ち状態で提出)
- [ ] pytest 全緑(C1〜C8)
- [ ] P0_certification.md
- [ ] ASSUMPTIONS.md 初版(このフェーズで置いた仮定があれば。
      無ければ「なし」と明記したファイルを作る)
- [ ] 新規物理計算ゼロ(自己申告ではなくコードレビューで確認可能に)

## このフェーズ特有の STOP

- C4(App K ≈51% 再現)が 2 回の修正で合わない
  → 式台帳・規約・論文本文のどこに原因があり得るかの切り分け表を
  付けて報告。**定数を調整して合わせることを固く禁ずる**
- 論文内の数値同士が矛盾して見える → 発見候補として報告(CLAUDE.md §8-3)

## 環境

- Python 3.12 / numpy / scipy / pytest(既存 conda 環境で可。
  新規環境構築は不要)
- GPU 不要。JAX 不要(必要と感じたら、それは設計が重すぎる兆候)
- warpax は導入済みの `~/research/warpax` を import して使う
- 実行時間の目安: テストスイート全体で 1 分未満。超えるなら STOP して
  設計を見直す
