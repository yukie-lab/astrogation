# P3 — 公開手順チェックリスト(人間用)

作成日: 2026-08-09。3c 成果物。上から順に実施する。
機械側の前提はすべて緑(C1–C19+lint+両言語同一性、コンパイル済み PDF 2 本)。

## A. 原稿の最終記入(人間のみが埋められる項目)

- [x] `paper/paper_en.tex` と `paper/paper_ja.tex` の著者名と ORCID を記入
      (2026-08-09 完了: Yukie Maeda / 前田 幸枝(Yukie Maeda)、ORCID 0009-0005-3401-9230)
- [x] 記入後に両 PDF を再コンパイル(2026-08-09 完了)

## B. 準備段階(2026-08-09 実行済み — 記録)

- [x] B1. リポジトリは **Private で作成済み**: https://github.com/yukie-lab/astrogation
      (**Public 化スイッチは最終手順 F3 へ移動** — 公開イベント時に人間が実施)
- [x] B2. `git remote add origin https://github.com/yukie-lab/astrogation.git`
      → `git push -u origin main`(認証は gh keyring で通過、プロンプトなし)
- [x] B3. 両 tex へ GitHub URL と **タグ参照方式**の固定記述を注入
      (EN: "pinned at tag `v1.0-paper` … (the tag resolves to the release
      commit)" / JA: 「タグ `v1.0-paper`(タグがリリースコミットに解決される)
      に固定」)。ハッシュ直書きは撤廃 — 注入コミット自身を指せない循環を、
      タグ解決参照で回避
- [x] B4. 再コンパイル+テスト緑 → コミット `b04aa3c`
      "release: inject repo URL and commit" → push 済み
- [ ] B5. **タグはまだ打っていない**(F2 で最終コミットに打つ)

## F. 最終公開シーケンス(B/C 統合 — 人間実行、上から順に)

- [ ] F1. **Zenodo 論文 draft**: https://zenodo.org/uploads/new →
      `paper/paper_en.pdf`・`paper/paper_ja.pdf` をアップロード →
      Resource type: Publication/Preprint → 書誌を
      `paper/publication_metadata.md` から転記(著者 Maeda, Yukie /
      ORCID 0009-0005-3401-9230、抄録は各 tex からコピー、License CC BY 4.0、
      Related works に arXiv:2606.22531)→ **Save draft**(DOI が予約表示される)
- [ ] F2. **DOI 注入と最終コミット・タグ**: 予約 DOI を両 tex の
      「[Zenodo DOI to be minted at release]」(JA:「[Zenodo DOI は
      リリース時発行]」)に記入 → `cd paper && tectonic paper_en.tex &&
      tectonic paper_ja.tex` → `git add -A && git commit -m "release: inject
      Zenodo DOI"` → `git push` → **`git tag v1.0-paper && git push origin
      v1.0-paper`**(タグは DOI 記入済みの最終コミットに載る — tex の
      タグ参照が自己整合する)
- [ ] F3. **Public 化**: https://github.com/yukie-lab/astrogation/settings →
      General 最下部 Danger Zone → Change repository visibility → Public
- [ ] F4. **コード DOI**: https://zenodo.org/account/settings/github/ で
      `yukie-lab/astrogation` を ON →
      https://github.com/yukie-lab/astrogation/releases/new → タグ
      `v1.0-paper` を選択 → Publish release → 数分後にコード DOI が自動発行
- [ ] F5. **Zenodo Publish**: F1 の draft に戻り、F2 で再コンパイルした
      PDF 2 本へ差し替え → Related works に F4 のコード DOI を追記 →
      **Publish**(論文 DOI 確定)
- [ ] F6. **Jxiv**: https://jxiv.jst.go.jp/ → ログイン(未登録なら作成。
      所属 = Independent Researcher)→ 新規投稿 → `paper/paper_ja.pdf` →
      氏名欄 姓=前田 名=幸枝 / 英語表記 姓=Maeda 名=Yukie /
      ORCID 0009-0005-3401-9230 / 分野=物理学 / 抄録 JA =
      publication_metadata.md → 利益相反なし・資金なし・AI 利用申告
      (「計算・実装・起草は Claude(Fable 5, Anthropic)、人間ゲート付き
      プロトコル。詳細は Methods」)→ 関連情報に論文 DOI・GitHub URL → 投稿
- [ ] F7. **記録**: コード DOI・論文 DOI・タグ・公開日を
      `docs/reports/P3_release_record.md` に記録し、コミット+push
- [ ] F8. 床 tier 裁定(c 鎖 STOP)が将来解決した場合: results/ 再生成 →
      `make_paper_numbers.py` → 再コンパイル → Zenodo 新版(DOI は版管理)

## 注意(憲法遵守)

- 数値の手修正は全段階で禁止(修正が必要なら Phase 1/2 の管轄で STOP 報告)
- 査読誌への投稿はこのチェックリストの範囲外(PHASE_3.md の禁止事項)
