# tests/archaeology — [v2-retracted] 隔離区画

ここには **v2(arXiv:2606.22531v2)固有で、v3 において理論構造ごと撤回された**
数学的対象に対するテストのみを置く。

## ラベル [v2-retracted] の定義(2026-08-08 人間承認)

- 対象: v2 に存在し、v3 で**番号ずれではなく構造として削除・撤回**された式・量。
  現時点の登録: 分岐スカラー D(x) 一式(v2: Eq.55–61。v3 Remark 1 により
  「ρ₁ 決定は凍結パラメータ化の artifact(spurious)」と撤回)
- 意味: 数学的には well-defined だが、**v3 オラクルの荷重を支えていない**。
  独立検算・考古学的照合のためにのみ保持する
- 禁止: `src/astrogation/` での使用・参照は**実装レベルで禁止**
  (`tests/test_v2_retracted_guard.py` が既定で常時実行され、
  `retracted_registry.txt` のトークンを src/ から検出したら失敗する)
- 実行: 本区画のテストは既定で **skip** される。明示実行は
  `pytest --run-archaeology`

## 権威ラベル体系との関係

CLAUDE.md §5 の [R]/[N]/[H] に **[v2-retracted]** を追加する(人間承認済み)。
[v2-retracted] は成果物の数値には決して付かない(下流使用禁止のため)。
テストと文書にのみ現れる。Phase 0 で `conventions.md` に転記すること。
