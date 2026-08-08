# L1 — オラクルの確保とバージョン固定

作成日: 2026-08-08(Phase L)
取得方法: `curl -sL https://arxiv.org/pdf/<id>`(2026-08-08 実行)
検証方法: `pdfinfo` によるページ数、`pdftotext` 冒頭によるヘッダ(arXiv スタンプ)照合、
arXiv abs ページによる版履歴照合。SHA256 で固定。

## 確保済みオラクル

| # | ファイル | arXiv ID / 版 | 版日付 | 頁数 | 役割 |
|---|---|---|---|---|---|
| 1 | `papers/le_steering_v3.pdf` | 2606.22531 **v3** [gr-qc] | 2026-07-15 | 57 | **第一オラクル**(本文+付録) |
| 2 | `papers/le_steering_v2.pdf` | 2606.22531 v2 [gr-qc] | 2026-06-30 | 48 | v2↔v3 式番号対応表用 |
| 3 | `papers/le_boundary_v2.pdf` | 2605.25417 **v2** [gr-qc] | 2026-06-20 | 18 | 境界コスト論文(背景・対比) |
| 4 | `papers/le_ec_verification.pdf` | 2602.18023 **v4** [gr-qc] | 2026-06-12 | 34 | warpax 論文(独立クロスチェック経路) |
| 5 | `papers/fuzfa_2019.pdf` | 1902.03869 / PRD 99, 104081 (2019) | 2019-05-31 出版 | 18 | 点ロケット先行研究(差分の相手) |

注記:
- CLAUDE.md は 2605.25417 の版を指定していない。取得時の最新は **v2**(2026-06-20)
  だったのでこれを固定した。ファイル名は `le_boundary_v2.pdf` として版を明示。
- 2602.18023 は **v4** が最新。warpax v1.3.0(`~/research/warpax`、導入済み確認)に対応。

## 2606.22531 の版履歴(arXiv abs ページ、2026-08-08 参照)

| 版 | 提出日時 (UTC) | サイズ |
|---|---|---|
| v1 | 2026-06-21 14:42 | 395 KB |
| v2 | 2026-06-30 17:55 | 341 KB |
| v3 | 2026-07-15 01:29 | 280 KB |

arXiv コメント欄(v3): 57 pages, 4 figures, 1 table。v3 での追加内容(著者申告):
frontier 境界条件、正の宇宙定数下の運動学的拘束、分布的エネルギー正値性、
時間発展ダイナミクス、放射モード不安定性解析、最適制御機動設計。

## SHA256(版固定)

```
6ea12d3cef4e90f309753250eea69b0324502bc1feaa89c0296eec7e4b2fd45a  le_steering_v3.pdf
6f15c38f4165593679974a1c7c5efaad88abd53c6fd4edc9ea5df62b51ca18bc  le_steering_v2.pdf
2ddd4a4c022118e91afea1cb546a07420736756b6de4acc03ff510d2a3ff2275  le_boundary_v2.pdf
df9dd368a7c83726bb039e66945fbb9ebbb7e206fd22ae8b7e654c693ad44509  le_ec_verification.pdf
2732bf46e7e0a88b0baf4857af812e905dc308d0957dead021e7537e20413a91  fuzfa_2019.pdf
```

## テキスト抽出

各 PDF に対し `pdftotext`(poppler)で `papers/*.txt` を生成済み(検索用)。
式の転記は PDF 画像描画(Read)で照合する。テキスト抽出は数式が崩れるため、
式台帳の一次ソースにはしない。

## 追補(2026-08-08、EXT1 照合のための取得)

| # | ファイル | arXiv ID / 版 | 頁数 | 役割 |
|---|---|---|---|---|
| 6 | `papers/fuzfa_2020_sailing.pdf` | 2007.03530(PRR 2, 043186, 2020) | 15 | **照合用参考**(オラクルではない)。EXT1 ④ の数値検証(2500g/13kt/1500K/162日の実出典) |

SHA256: 下記(取得時固定)
35e707c5bf023273743464997d889d7653a3efcf78ea80bf24c90bbc6d9446df  fuzfa_2020_sailing.pdf
