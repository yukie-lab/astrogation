# P3 — リリース記録(F7)

記録日: 2026-08-09(JST)。

## 公開物

| 項目 | 値 |
|---|---|
| **論文 DOI** | https://doi.org/10.5281/zenodo.21853092 |
| 論文 Zenodo レコード | https://zenodo.org/records/21853092 |
| **コード DOI** | https://doi.org/10.5281/zenodo.21853406 |
| コード Zenodo レコード | https://zenodo.org/records/21853406 |
| 公開日時 | **2026-08-08(UTC)** Published、Version **v1.0-paper** |
| GitHub | https://github.com/yukie-lab/astrogation(Public) |
| リリースタグ | `v1.0-paper` → コミット **e71975337e1a5afdf9e0586312751932801eaf40**(短縮 `e719753`) |
| 収録 PDF | `paper/paper_en.pdf`(英語正本)/ `paper/paper_ja.pdf`(日本語版)— DOI 注入済み 01:49 JST 再コンパイル版 |
| 著者 | Yukie Maeda(前田 幸枝)、Independent Researcher, Tokyo、ORCID 0009-0005-3401-9230 |
| ライセンス | 論文 CC BY 4.0 / コード MIT |

## 状態

- F1〜F5(Zenodo draft → DOI 注入+タグ → Public 化 → コード DOI → Publish)
  **完了**
- **F6(Jxiv 日本語版投入)は未実施** — 実施時に本記録へ Jxiv ID を追記する
- F8(床 tier 裁定解決時の改訂): 該当なし(c 鎖 STOP 継続中。解決時は
  results/ 再生成 → make_paper_numbers.py → 再コンパイル → Zenodo 新版)

## 整合性の注記

論文本文の Data availability は「pinned at tag `v1.0-paper`」のタグ参照
方式であり、タグは DOI 記入済みソースを含むコミット `e719753` に解決する
(自己整合)。公開監査証跡はコミット履歴(Phase L〜3 の全ゲートコミット)
として GitHub 上で追跡可能。
