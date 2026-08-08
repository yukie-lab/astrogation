"""補助認証(L2 §5 提案・L8 §5): 診断量と [N]/[H] ガードの検証。

認証 C1–C8 の外side。λ̄_DEC(v3 Lemma 5)は診断専用 — ここでの検証は
「診断として正しく実装されている」ことの確認であり、拘束としての使用を
正当化しない(L7 §B、conventions.md §5)。
"""
import math
from fractions import Fraction

import pytest

from astrogation import frontier


class TestLambdaBarDEC:
    def test_endpoint_exact_zeros_rational(self):
        """[v3 (43)] 端点 x=0, 24/25 で厳密ゼロ(radicand が有理平方、有理評価)。"""
        # x = 0: 6√16 − |24| = 24 − 24 = 0
        assert Fraction(16) == Fraction(4) ** 2
        assert 6 * Fraction(4) - abs(Fraction(24)) == 0
        # x = 24/25: 16 − 14·(24/25) = 64/25 = (8/5)²; |24 − 35·24/25| = 48/5
        x = Fraction(24, 25)
        radicand = 16 - 14 * x
        assert radicand == Fraction(8, 5) ** 2
        assert 6 * Fraction(8, 5) - abs(24 - 35 * x) == 0
        # float 実装も同じ端点で ~0
        assert abs(frontier.lambda_bar_dec(0.0)) < 1e-14
        assert abs(frontier.lambda_bar_dec(24.0 / 25.0)) < 1e-14

    def test_positive_and_below_ceiling_on_window(self):
        """[v3 Lemma 5] (0, 24/25) で正、天井 ½(1−x) より厳密に下。"""
        for k in range(1, 960):
            x = k / 1000.0
            lb = frontier.lambda_bar_dec(x)
            assert lb > 0.0, f"x={x}"
            assert lb < frontier.kinematic_ceiling(x), f"x={x}"

    def test_small_x_slope_one_quarter(self):
        """[v3 (44)] λ̄_DEC = x/4 + O(x²)。"""
        x = 1e-6
        assert abs(frontier.lambda_bar_dec(x) / x - 0.25) < 1e-4

    def test_crossover_at_24_over_35(self):
        """[v3 (43)] |24−35x| の枝替わり点 x = 24/35 で連続。"""
        xc = 24.0 / 35.0
        left = frontier.lambda_bar_dec(xc - 1e-9)
        right = frontier.lambda_bar_dec(xc + 1e-9)
        assert abs(left - right) < 1e-8


class TestGLowerGuards:
    def test_nodes_exact(self):
        """[N] v3 (S1) の 5 点を厳密再現。"""
        for x, g in zip(frontier.G_LOWER_X, frontier.G_LOWER_VALUES):
            assert frontier.g_lower(x) == g

    def test_out_of_range_raises(self):
        """[N] サンプル範囲外は例外(外挿は実装レベルで不可能、CLAUDE.md §5)。"""
        for x in (0.0, 0.05, 0.0999, 0.7001, 0.9, 24.0 / 25.0):
            with pytest.raises(frontier.OutsideSampledRangeError):
                frontier.g_lower(x)

    def test_respects_heuristic_envelope(self):
        """[v3 (S1) 本文] 各 g̲ 値は包絡線 (39) を尊重([H] は比較のみに使用)。"""
        for x, g in zip(frontier.G_LOWER_X, frontier.G_LOWER_VALUES):
            assert g <= frontier.envelope_heuristic(x) + 1e-12


class TestCLowerRecord:
    def test_paper_values_recorded(self):
        """[v3 (73)] c(x) 記録値の転記確認(再導出は Phase 0 範囲外、L7 §C)。"""
        assert frontier.C_LOWER_X == (0.1, 0.2, 0.3, 0.5, 0.7)
        assert frontier.C_LOWER_VALUES == (8.5e-5, 1.4e-4, 1.7e-4, 1.4e-4, 2.0e-5)
        # 数値下界 g̲ より約3桁保守的(v3 App C 本文の関係の確認)
        for x, c in zip(frontier.C_LOWER_X, frontier.C_LOWER_VALUES):
            assert c < frontier.g_lower(x) / 100.0
