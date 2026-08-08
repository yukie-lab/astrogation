# P3 — 公開手順チェックリスト(人間用)

作成日: 2026-08-09。3c 成果物。上から順に実施する。
機械側の前提はすべて緑(C1–C19+lint+両言語同一性、コンパイル済み PDF 2 本)。

## A. 原稿の最終記入(人間のみが埋められる項目)

- [x] `paper/paper_en.tex` と `paper/paper_ja.tex` の著者名と ORCID を記入
      (2026-08-09 完了: Yukie Maeda / 前田 幸枝(Yukie Maeda)、ORCID 0009-0005-3401-9230)
- [x] 記入後に両 PDF を再コンパイル(2026-08-09 完了)

## B. リポジトリ公開(GitHub)

- [ ] 公開リポジトリを作成し、main を push
- [ ] **リリースコミットの確定**: 公開直前の最終コミットハッシュを
      Data availability の「[commit hash injected at release]」
      (JA 版は「[リリース時注入のコミットハッシュ]」)に記入し、
      再コンパイルして、そのコミットをリリースコミットとする
      (3b 修正 3 の手順化。ハッシュ記入コミット自体を tag 対象にする)
- [ ] タグ `v1.0-paper` を作成し push

## C. Zenodo

- [ ] GitHub 連携でタグ `v1.0-paper` からコード DOI を発行
- [ ] 論文アップロード(paper_en.pdf / paper_ja.pdf)を作成し、
      `paper/publication_metadata.md` の書誌を転記(抄録は tex からコピー)
- [ ] 発行された DOI と GitHub URL を両 tex の Data availability の
      「[GitHub URL, Zenodo DOI to be minted at release]」に記入 → 再コンパイル
      → 同一リリースに PDF を差し替え(Zenodo は版の更新が可能)

## D. Jxiv

- [ ] `publication_metadata.md` の Jxiv 欄に従い日本語版を投入
      (所属 Independent Researcher / AI 利用申告は Methods のとおり)

## E. 事後

- [ ] リリース情報(DOI・URL・タグ)を `docs/reports/` に記録するコミット
- [ ] 床 tier 裁定(c 鎖 STOP)が将来解決した場合の改訂手順: results/ 再生成
      → make_paper_numbers.py → 再コンパイル → Zenodo 新版

## 注意(憲法遵守)

- 数値の手修正は全段階で禁止(修正が必要なら Phase 1/2 の管轄で STOP 報告)
- 査読誌への投稿はこのチェックリストの範囲外(PHASE_3.md の禁止事項)
