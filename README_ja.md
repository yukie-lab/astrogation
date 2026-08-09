# ASTROGATION — 正エネルギーワープシェルの恒星間飛行プロファイルと観測署名

論文(英語正本+日本語版、`paper/`)の再現パッケージ。論文中の全数値は
`results/` のカタログから機械生成され、認証スイートで検証される。

## 概要

Le の放射運動量ワープシェル(arXiv:2606.22531)に対し、許容性制約を全て課した
初の恒星間機動カタログを計算し、全機動を観測者系光度曲線に写像する。飽和加速の
厳密な前方ヌル、閉形式減衰則 $F \propto e^{7\eta-3\Delta\eta_{\rm tot}}$ に従う
減速フラッシュ、重力波静寂判別子を与える。

## 再現手順

環境: Python 3.12、numpy、scipy、pytest、matplotlib(warpax 1.3.0 入りの
conda 環境を使用。warpax はクロスチェック接続テストのみで必要)。

```
# 1. 認証スイート(C1-C19+文体 lint。1 分未満)
python -m pytest tests

# 2. カタログ再生成(機動 ~15 分、署名 ~1 分)
python scripts/make_catalog.py
python scripts/make_signatures.py

# 3. 論文数値・表・図の再生成とコンパイル
python scripts/make_paper_numbers.py
python scripts/make_figures_paper_en.py
cd paper && tectonic paper_en.tex && tectonic paper_ja.tex
```

隔離された考古学テスト([v2-retracted] 構造)は `pytest --run-archaeology`。

## 構成

`CLAUDE.md` 憲法 / `conventions.md` 規約台帳 / `ASSUMPTIONS.md` 仮定台帳 /
`docs/reports/` ゲート報告(式台帳・STOP 報告・照合)/ `src/astrogation/`
認証済みライブラリ / `tests/` 認証スイート / `results/` カタログ・署名 /
`paper/` 原稿・生成数値・表・図。

## 権威ラベル

公表数値はすべてラベルを相続する。[R] 厳密閉形式、[N] 公表数値(外挿禁止)、
[H] 発見法(表示のみ)、[R(A3)/暫定] 照合待ちの保守床(論文 Methods 参照)。

## シミュレータ

`simulator/` に、認証済みカタログの上に組んだ Three.js の航海シークエンス
がある(可視化作品。科学的主張は論文と公開データが担う —
`simulator/README.md` の境界宣言を参照)。UI は英語が既定で、日本語は
`?lang=ja` または画面トグルで明示指定する。リポジトリ直下の `index.html`
がランディングページ(英語主、日本語版は `index_ja.html`)。
公開サイト: https://yukie-lab.github.io/astrogation/(ランディング)/
https://yukie-lab.github.io/astrogation/simulator/(シミュレータ)。

## ライセンスと引用

コード: MIT。論文: CC BY 4.0。warpax と world_tube(MIT、An T. Le)を使用。
本カタログを使う場合は論文と arXiv:2606.22531 を引用のこと。
