"""pytest 設定: [v2-retracted] 考古学テストの既定除外。

tests/archaeology/ 配下は marker `archaeology` を持ち、既定では skip される。
明示実行: pytest --run-archaeology
"""
import pytest


def pytest_addoption(parser):
    parser.addoption(
        "--run-archaeology",
        action="store_true",
        default=False,
        help="[v2-retracted] の考古学テストを実行する(既定では skip)",
    )


def pytest_configure(config):
    config.addinivalue_line(
        "markers",
        "archaeology: [v2-retracted] v2 固有の撤回済み構造への隔離テスト(下流使用禁止)",
    )


def pytest_collection_modifyitems(config, items):
    if config.getoption("--run-archaeology"):
        return
    skip = pytest.mark.skip(
        reason="[v2-retracted] archaeology: --run-archaeology で明示実行"
    )
    for item in items:
        if "archaeology" in item.keywords:
            item.add_marker(skip)
