"""astrogation — Le の正エネルギー warpshell 理論(arXiv:2606.22531v3)の
許容性制約つき恒星間機動カタログと観測署名のためのライブラリ。

Phase 0(検証ハーネス): units / control / shell / frontier / geodesy / bondi。
全関数の docstring に v3 式番号と権威ラベル [R]/[N]/[H] を併記(conventions.md §4-5)。
認証セット C1–C8 に合格した部品のみが Phase 1 以降で使用可(CLAUDE.md §4)。
"""
from . import bondi, control, frontier, geodesy, shell, units  # noqa: F401

__version__ = "0.1.0"
