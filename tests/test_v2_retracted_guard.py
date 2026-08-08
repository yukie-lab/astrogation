"""[v2-retracted] ガード(既定で常時実行)。

tests/archaeology/retracted_registry.txt に登録されたトークンが
src/ 配下の Python ソースに現れたら失敗する。撤回された v2 構造
(分岐スカラー D(x) 等)の下流使用をビルド時に禁止するのが目的。
src/ が未作成(Phase 0 以前)の間は自明に成立する。
"""
from pathlib import Path

REPO = Path(__file__).resolve().parents[1]
REGISTRY = REPO / "tests" / "archaeology" / "retracted_registry.txt"


def load_tokens():
    tokens = []
    for line in REGISTRY.read_text(encoding="utf-8").splitlines():
        line = line.strip()
        if line and not line.startswith("#"):
            tokens.append(line.lower())
    return tokens


def test_registry_exists_and_nonempty():
    assert REGISTRY.exists(), "retracted_registry.txt が存在しない"
    assert load_tokens(), "登録簿が空:[v2-retracted] ガードが機能しない"


def test_no_retracted_symbols_in_src():
    src = REPO / "src"
    if not src.exists():
        return  # Phase 0 以前: src 未作成
    tokens = load_tokens()
    hits = []
    for path in src.rglob("*.py"):
        text = path.read_text(encoding="utf-8", errors="ignore").lower()
        for tok in tokens:
            if tok in text:
                hits.append(f"{path.relative_to(REPO)}: '{tok}'")
    assert not hits, (
        "[v2-retracted] 撤回済み構造が src/ で使用されている:\n" + "\n".join(hits)
    )
