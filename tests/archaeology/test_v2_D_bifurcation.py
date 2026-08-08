"""[v2-retracted] v2 分岐スカラー D(x) の考古学テスト(隔離区画)。

対象: arXiv:2606.22531 **v2** Eqs. (55)-(61)。
v3 では Remark 1 により撤回された(ρ₁ は純ゲージ、v2 の D(x) による
ρ₁ 決定は凍結パラメータ化の artifact)。本テストは v3 の荷重を一切
支えない。v2→v3 改訂の独立検算・歴史的照合のためにのみ保持する。
下流(src/)での使用は tests/test_v2_retracted_guard.py が禁止する。

規約: s = sqrt(1-x), x = 2m/R ∈ (0, 24/25) ⇔ s ∈ (1/5, 1)。
閉形式のみ(数値積分なし)。許容誤差は CLAUDE.md §4 の原則に従い 1e-12。
"""
import math

import pytest

pytestmark = pytest.mark.archaeology

TOL = 1e-12


def D_rational(s):
    """v2 (58) 第1形: D = (s^5 - 6s^4 - s^3 + 6s^2 - 4) / (3 s^3)."""
    return (s**5 - 6 * s**4 - s**3 + 6 * s**2 - 4) / (3 * s**3)


def D_expanded(s):
    """v2 (58) 第2形: D = s^2/3 - 2s - 1/3 + 2/s - 4/(3 s^3)."""
    return s**2 / 3 - 2 * s - 1.0 / 3 + 2 / s - 4 / (3 * s**3)


def Q_poly(s):
    """v2 (59): Q(s) = s^4 - 5s^3 - 2s^2 + 4s + 4."""
    return s**4 - 5 * s**3 - 2 * s**2 + 4 * s + 4


def s_grid(n=2001, lo=0.2, hi=1.0):
    """(1/5, 1) の開区間内グリッド(端点は別途扱う)。"""
    return [lo + (hi - lo) * (k + 0.5) / n for k in range(n)]


def test_v2_58_two_closed_forms_agree():
    """v2 (58) の有理形と展開形の一致(相対 1e-12)。"""
    for s in s_grid():
        a, b = D_rational(s), D_expanded(s)
        assert abs(a - b) <= TOL * max(1.0, abs(a))


def test_v2_59_factorization_identity():
    """v2 (59): D + 4/3 = (s-1) Q(s) / (3 s^3)(相対 1e-12)。"""
    for s in s_grid():
        lhs = D_rational(s) + 4.0 / 3
        rhs = (s - 1) * Q_poly(s) / (3 * s**3)
        assert abs(lhs - rhs) <= TOL * max(1.0, abs(lhs))


def test_v2_60_bound_sign_and_limit():
    """v2 (60): D(x) < -4/3 on (0, 24/25)(実は (0,1))、|D| >= 4/3、
    下界 4/3 は x -> 0+ (s -> 1-) でのみ漸近到達(s=1 で厳密に -4/3)。"""
    for s in s_grid():
        d = D_rational(s)
        assert d < -4.0 / 3
        assert abs(d) >= 4.0 / 3
    assert abs(D_rational(1.0) + 4.0 / 3) <= TOL


def test_v2_59_Q_positivity_on_window():
    """v2 (60) の根拠: Q > 0 on [0,1](端点 Q(0)=4, Q(1)=2、単峰)。"""
    assert abs(Q_poly(0.0) - 4.0) <= TOL
    assert abs(Q_poly(1.0) - 2.0) <= TOL
    for k in range(2001):
        s = k / 2000.0
        assert Q_poly(s) > 0


def test_v2_61_monotonicity_identity_and_positivity():
    """v2 (61): s^4 dD/ds = (2/3)s^5 - 2s^4 - 2s^2 + 4
    = 2(s^2+2)(1-s^2) + (2/3)s^5 > 0 on (0,1] — |D| は x に単調増加。"""
    for s in s_grid():
        lhs = (2.0 / 3) * s**5 - 2 * s**4 - 2 * s**2 + 4
        rhs = 2 * (s**2 + 2) * (1 - s**2) + (2.0 / 3) * s**5
        assert abs(lhs - rhs) <= TOL * max(1.0, abs(lhs))
        assert rhs > 0
        # 解析微分との一致(独立検算)
        dD = 2 * s / 3 - 2 - 2 / s**2 + 4 / s**4
        assert abs(s**4 * dD - lhs) <= 1e-10 * max(1.0, abs(lhs))


def test_window_endpoint_mapping():
    """x ∈ (0, 24/25) ⇔ s ∈ (1/5, 1) の写像確認。"""
    assert abs(math.sqrt(1 - 24.0 / 25) - 0.2) <= TOL
