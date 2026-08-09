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

- 操作: 再生/一時停止ボタン、幕 1〜5 スキップボタン
- ディープリンク: `?act=3&t=5.5&paused=1`(幕・幕内秒・一時停止)
- 物理層の自己認証: `test_snapshot.html` を開くと P4-C20 が走り緑/赤を表示
  (`node test_snapshot.js` でも同じ)。シミュレータ自身も起動時に全件を
  実行し、画面右下にバッジ表示する

## 物理と演出の境界宣言

**物理層** — `physics.js` が単一真実源。HUD・航路儀・フラッシュ計の
数値はすべてこのモジュールの出力であり、ダミー数値は存在しない。
実装式はすべて論文の閉形式(Tsiolkovsky m(η)=m₀e^(−3η)、三層フロンティア、
飽和パターン 3mλ(1−cosϑ)/4π、光行差・ドップラー写像、フラッシュ則
F∝e^(7η−3Δη_tot))の移植で、新しい物理はゼロ。スナップショット認証
P4-C20(32 件、相対 1e-10、出典 `results/` @ v1.0-paper)が張ってある。

**演出層** — `main.js`。以下を宣言する:

| 項目 | 扱い |
|---|---|
| 光行差・ドップラー | η から厳密計算。**誇張倍率 1.0(誇張なし)** |
| 前方ヌル | 排気の粒子密度・輝度とも飽和パターン (1−cosϑ) に比例。前方 ϑ=0 で厳密ゼロ。幕 2 の正面カットで目視確認できる |
| ローブの向き | thrust 履歴に従う(幕 1–2 後方、幕 3–4 前方) |
| 輝度表示 | **対数トーンマッピング**。星野は δ⁴ を δ^1.15 に圧縮表示、ローブは L の対数正規化(表示レンジ [10⁻³³, 0.57])、フラッシュは対数計(下端 10⁻⁹)。線形では 30 桁のダイナミックレンジは表現不能 |
| 色 | **芸術的選択であり物理主張ではない**(排気スペクトルの主張はしない。論文と同じ自制) |
| 時間圧縮 | 対数を基本とし、実時間演出は出発・反転・到着の三箇所のみ |
| R = 1 km | フラッシュ減衰尺の秒表示(15.4 ps)に使う表示用シナリオ仮定 |
| M31 の見かけの成長・年カウンタ | 演出ペーシング(角径・経過年の実時間表示ではない)。カウンタの到達値 2.54×10⁶ 年のみ物理定数 |

観客が持ち帰る一行:
**「加速するワープ船は正面から見えない。到着だけが、閃光として届く。」**

## 引用

Le, An T. "Steering a warp drive without exotic matter." arXiv:2606.22531 (2026).
/ Maeda, Yukie. "Interstellar flight profiles and observational signatures
of positive-energy warp shells." DOI: 10.5281/zenodo.21853092 (2026).
/ three.js (MIT).
