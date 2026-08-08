# P3 — 公開手順チェックリスト(人間用)

作成日: 2026-08-09。3c 成果物。上から順に実施する。
機械側の前提はすべて緑(C1–C19+lint+両言語同一性、コンパイル済み PDF 2 本)。

## A. 原稿の最終記入(人間のみが埋められる項目)

- [x] `paper/paper_en.tex` と `paper/paper_ja.tex` の著者名と ORCID を記入
      (2026-08-09 完了: Yukie Maeda / 前田 幸枝(Yukie Maeda)、ORCID 0009-0005-3401-9230)
- [x] 記入後に両 PDF を再コンパイル(2026-08-09 完了)

## B. リポジトリ公開(GitHub)— 操作手順

- [ ] B1. https://github.com/new を開く → Repository name: `astrogation`(任意)、
      Public、README/ライセンスは**追加しない**(ローカルに既存)→ Create
- [ ] B2. ターミナルで(リポジトリ直下):
      `git remote add origin https://github.com/<ユーザー名>/astrogation.git`
      → `git push -u origin main`
- [ ] B3. **リリースコミットの注入**: 現在の最終コミット(Phase 3 ゲート
      `12f9cfd`)のハッシュを、`paper/paper_en.tex` の
      「[commit hash injected at release]」と `paper/paper_ja.tex` の
      「[リリース時注入のコミットハッシュ]」に記入(同時に B2 の GitHub URL を
      「[GitHub URL, ...]」の GitHub 部分に記入)
- [ ] B4. 再コンパイル: `cd paper && tectonic paper_en.tex && tectonic paper_ja.tex`
- [ ] B5. `git add -A && git commit -m "release: inject GitHub URL and content
      commit 12f9cfd"` → `git push`
- [ ] B6. タグ付け: `git tag v1.0-paper && git push origin v1.0-paper`

## C. Zenodo — 操作手順

- [ ] C1. https://zenodo.org にログイン(GitHub アカウント連携可)
- [ ] C2. コード DOI: https://zenodo.org/account/settings/github/ を開き、
      `astrogation` リポジトリのスイッチを ON → GitHub 側で
      https://github.com/<ユーザー名>/astrogation/releases/new → タグ
      `v1.0-paper` を選択 → Publish release → 数分後 Zenodo にコード DOI が
      自動発行される(Zenodo の GitHub ページで確認)
- [ ] C3. 論文 DOI: https://zenodo.org/uploads/new → ファイルに
      `paper/paper_en.pdf` と `paper/paper_ja.pdf` をドラッグ →
      Resource type: Publication / Preprint → タイトル・著者
      (Maeda, Yukie / ORCID 0009-0005-3401-9230)・抄録(EN は
      paper_en.tex、JA は paper_ja.tex からコピー)・キーワード・
      License: CC BY 4.0 を `paper/publication_metadata.md` から転記 →
      Related works に arXiv:2606.22531 と C2 のコード DOI を追加 →
      **Save draft のまま Publish は保留**(DOI は予約表示される)
- [ ] C4. C3 の予約 DOI を両 tex の「[... Zenodo DOI to be minted at release]」
      (JA: 「[... Zenodo DOI はリリース時発行]」)に記入 → 再コンパイル →
      draft の PDF 2 本を差し替え → **Publish**
- [ ] C5. `git add -A && git commit -m "release: inject Zenodo DOIs"` → push
      (このコミットはタグ後のメタデータ追記であり、内容コミットは 12f9cfd の
      まま — Data availability の記述と整合)

## D. Jxiv — 操作手順

- [ ] D1. https://jxiv.jst.go.jp/ → 右上「ログイン」(未登録なら
      アカウント作成。所属は「なし(個人)/ Independent Researcher」)
- [ ] D2. 「新規投稿」→ 原稿ファイル: `paper/paper_ja.pdf`
- [ ] D3. 書誌入力: 氏名欄 姓=**前田** 名=**幸枝** / 英語表記 姓=**Maeda**
      名=**Yukie** / ORCID **0009-0005-3401-9230** / 所属 = Independent
      Researcher, Tokyo / 分野 = 物理学 / タイトル・抄録(JA)=
      publication_metadata.md のとおり
- [ ] D4. 利益相反: なし / 資金: なし / **AI 利用の申告**: 「計算・実装・
      起草は Claude(Fable 5, Anthropic)が人間ゲート付きプロトコルの下で
      実施(詳細は本文 Methods)」と記入
- [ ] D5. 関連情報に Zenodo DOI(英語正本)と GitHub URL を記載 → 投稿

## E. 事後

- [ ] E1. リリース情報(コード DOI・論文 DOI・GitHub URL・タグ)を
      `docs/reports/P3_release_record.md` に記録してコミット
- [ ] E2. 床 tier 裁定(c 鎖 STOP)が将来解決した場合: results/ 再生成 →
      `make_paper_numbers.py` → 再コンパイル → Zenodo 新版(DOI は版管理される)

## 注意(憲法遵守)

- 数値の手修正は全段階で禁止(修正が必要なら Phase 1/2 の管轄で STOP 報告)
- 査読誌への投稿はこのチェックリストの範囲外(PHASE_3.md の禁止事項)
