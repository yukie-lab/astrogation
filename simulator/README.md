# ASTROGATION シミュレータ — M31 への航海(五幕)

一隻の正エネルギー・ワープシェルが M31 へ航海する一本のシークエンス。
**本作は認証済みカタログ(`results/`、tag `v1.0-paper`)の可視化作品であり、
科学的主張は論文([DOI 10.5281/zenodo.21853092](https://doi.org/10.5281/zenodo.21853092))と
公開データが担う。**

*This is a visualization artwork built on the certified maneuver catalog;
all scientific claims live in the paper and the released data, not here.*

## 実行

```bash
cd simulator
python3 -m http.server 8000
# → http://localhost:8000/index.html
```

ES モジュールと CDN(three.js)を使うため、`file://` 直開きではなく
ローカルサーバ経由で開く。ビルド工程は不要。依存は CDN の three のみ。

- 操作: 再生/一時停止ボタン、幕 1〜5 スキップボタン、言語切替(EN/日本語)
- **初期言語は英語**(論文の英語正本主義と整合)。日本語は `?lang=ja` または
  画面トグルの明示指定のみ — ブラウザ言語の自動判定はしない(挙動を決定的に保つ)
- ディープリンク: `?act=3&t=5.5&paused=1`(幕・幕内秒・一時停止)、
  `?lang=ja`(言語)。UI 文言は ja/en 辞書、数値は言語によらず physics.js のみ
- キャッシュずれ防止: HTML のスクリプトタグは内容ハッシュのバージョンクエリ
  (`main.js?v=…` 等)付き。JS を編集したら該当タグの値を更新すること
- 物理層の自己認証: `test_snapshot.html` を開くと P4-C20 が走り緑/赤を表示
  (`node test_snapshot.js` でも同じ)。シミュレータ自身も起動時に全件を
  実行し、画面右下にバッジ表示する

## 物理と演出の境界宣言

**物理層** — `physics.js` が単一真実源。HUD・航路儀・フラッシュ計の
数値はすべてこのモジュールの出力であり、ダミー数値は存在しない。
実装式はすべて論文の閉形式(Tsiolkovsky m(η)=m₀e^(−3η)、三層フロンティア、
飽和パターン 3mλ(1−cosϑ)/4π、光行差・ドップラー写像、フラッシュ則
F∝e^(7η−3Δη_tot))の移植で、新しい物理はゼロ。スナップショット認証
P4-C20(37 件、相対 1e-10、出典 `results/` @ v1.0-paper。実天球の
船首フレームには「光行差ゼロ時に M31 方向 = 画面正面」の項を含む)が
張ってある。

**演出層** — `main.js`。以下を宣言する:

| 項目 | 扱い |
|---|---|
| 星野 | **実天球**: Yale Bright Star Catalogue 5th rev. (V/50) の V≤6.5、N=8404 星(`stars.js`、生成は `scripts/make_simulator_stars.py`)。船首方位は M31 実座標(RA 0h42.7m, Dec +41°16′)。**全星を無限遠(視差ゼロ)として扱う単純化**(このため天球は出発系・目的地系で共通)。等級→輝度・B−V→色温度の変換は演出裁量 |
| 光行差・ドップラー | η から厳密計算。**誇張倍率 1.0(誇張なし)** |
| 前方ヌル | 排気の粒子密度・輝度とも飽和パターン (1−cosϑ) に比例。前方 ϑ=0 で厳密ゼロ。幕 2 の正面カットで目視確認できる |
| ローブの向き | thrust 履歴に従う(幕 1–2 後方、幕 3–4 前方) |
| 輝度表示 | **対数トーンマッピング**。星野は δ⁴ を δ^1.15 に圧縮表示、ローブは L の対数正規化(表示レンジ [10⁻³³, 0.57])、フラッシュは対数計(下端 10⁻⁹)。線形では 30 桁のダイナミックレンジは表現不能 |
| 色 | **芸術的選択であり物理主張ではない**(排気スペクトルの主張はしない。論文と同じ自制) |
| 時間圧縮 | 対数を基本とし、実時間演出は出発・反転・到着の三箇所のみ |
| R = 1 km | フラッシュ減衰尺の秒表示(15.4 ps)と二重時計の秒換算に使う表示用シナリオ仮定(カタログ mission meta の R_ref_m と同値) |
| 二重時計 | 船内時間 τ(乗員)と地球時間 t(出発系)。バーンは閉形式 Δτ=RΔη/λ・Δt=(R/λ)Δsinh η、巡航は dτ/dt=1/cosh η の閉形式(τ=d/sinh η、t=d/tanh η)。値はすべて physics.js、完走合計はカタログ固有時間列(mission grid u 終端)と C20 で相対 1e-8 照合。**巡航の計上タイミングは幕 2 後半に対数圧縮で織り込む**(ペーシングのみ演出)。視点反転後(幕 5 後半)は非表示 |
| M31 の見かけの成長・年カウンタ | 演出ペーシング(角径・経過年の実時間表示ではない)。カウンタの到達値 2.54×10⁶ 年のみ物理定数 |

用語の対応: HUD の「座席係数 e^(2η)」(地の文では「乗客を運ぶ代価」)は
論文英語正本の **seat price**(Table II)に対応する。

観客が持ち帰る一行:
**「加速するワープ船は正面から見えない。到着だけが、閃光として届く。」**

## 引用

Le, An T. "Steering a warp drive without exotic matter." arXiv:2606.22531 (2026).
/ Maeda, Yukie. "Interstellar flight profiles and observational signatures
of positive-energy warp shells." DOI: 10.5281/zenodo.21853092 (2026).
/ 星野データ: Hoffleit, D. & Warren, W. H. Jr., *The Bright Star Catalogue,
5th Revised Edition*, Yale University Observatory (1991); VizieR カタログ
V/50 より抽出。/ three.js (MIT).
