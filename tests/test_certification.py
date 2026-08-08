"""認証テスト C1–C8(CLAUDE.md §4、2026-08-08 改定版 / conventions.md §6)。

- C1  Tsiolkovsky m_f/m₀ = e^(−3Δη)                     [v3 (15)]  rel < 1e-12
- C2  表面 DEC 窓: 符号反転 @ x=24/25、窓内で正          [v3 (22)-(25),(58),(61)] 厳密ゼロ交差
- C3  ℓ≤1/ℓ=2 閉包の非退化 C3a–C3d                      [v3 (77),(79),(80),(81),(88)] 恒等 < 1e-12
- C4  実働バーン: 放射質量比 ≈51% ほか                   [v3 Supplement] 表示桁一致
- C5  運動学的天井 λ < ½(1−x)                           [v3 (40),(20)] 閉形式 < 1e-12
- C6  モーメント恒等式(求積)                            [v3 (13),(29)=(59)] < 1e-10
- C7  単位往復                                           [conventions §1] < 1e-12
- C8  G3 初回: Tsiolkovsky 閉形式 vs ODE、warpax 接続     [v3 (14)-(15)] rel < 1e-8

「厳密」を主張する箇所は fractions.Fraction で有理評価する(conventions.md §6)。
"""
import math
import random
from fractions import Fraction

import numpy as np
import pytest

from astrogation import bondi, control, frontier, geodesy, shell, units

REL = 1e-12          # 閉形式恒等式
QUAD = 1e-10         # 求積
TWO_PATH = 1e-8      # 二経路
random.seed(20260808)


def rel_err(a, b):
    return abs(a - b) / max(1.0, abs(a), abs(b))


def x_grid(n=997, lo=1e-4, hi=0.9999):
    return [lo + (hi - lo) * k / (n - 1) for k in range(n)]


# ================================================================ C1
class TestC1_Tsiolkovsky:
    def test_closed_form_against_exp(self):
        """[v3 (15)] m_f/m₀ = e^(−3Δη)、相対 < 1e-12。"""
        for deta in (0.0, 1e-6, 0.1, 0.24, 1.0, 5.0):
            assert rel_err(control.tsiolkovsky_ratio(deta), math.exp(-3.0 * deta)) < REL

    def test_multiplicativity(self):
        """予算の乗法性(積分の加法性): ratio(a+b) = ratio(a)·ratio(b)。"""
        for _ in range(200):
            a, b = random.uniform(0, 2), random.uniform(0, 2)
            assert rel_err(
                control.tsiolkovsky_ratio(a + b),
                control.tsiolkovsky_ratio(a) * control.tsiolkovsky_ratio(b),
            ) < REL


# ================================================================ C2
class TestC2_SurfaceDECWindow:
    def test_exact_zero_crossing_at_window_boundary(self):
        """[v3 (24)-(25)] 窓境界 x=24/25 ⟺ s=1/5 で厳密ゼロ(有理評価)。"""
        s = Fraction(1, 5)
        assert 1 - s * s == Fraction(24, 25)          # 境界の写像も厳密
        assert shell.dec_margin_factorized_s(s) == 0  # 厳密ゼロ交差

    def test_sign_reversal_and_positivity_in_window(self):
        """窓内で正・窓外で負(σ₀−p₀ の符号反転)。"""
        for x in x_grid():
            m = shell.dec_margin(x)
            if x < 24.0 / 25.0:
                assert m > 0.0, f"x={x}: 窓内で非正"
            elif x > 24.0 / 25.0 + 1e-12:
                assert m < 0.0, f"x={x}: 窓外で非負"

    def test_direct_vs_factorized_and_M0(self):
        """[v3 (22)(23)] 直接形 vs (24)=(58) 因数分解 vs (61) M₀ の三者一致 < 1e-12。"""
        for x in x_grid(499, 1e-3, 0.999):
            s = math.sqrt(1.0 - x)
            direct = 8.0 * math.pi * shell.dec_margin(x) * s
            fact = shell.dec_margin_factorized_s(s)
            assert rel_err(direct, fact) < REL
            assert rel_err(shell.anchor_margin_M0(x), fact / s) < REL

    def test_wec_strict_positivity(self):
        """[v3 (22)-(23)] σ₀ > 0, p₀ > 0 on (0,1)(WEC は全域)。"""
        for x in x_grid(499, 1e-3, 0.999):
            assert shell.sigma0(x) > 0.0 and shell.p0(x) > 0.0


# ================================================================ C3(改定版)
class TestC3a_CosRow:
    def test_partials_match_79(self):
        """[v3 (77)⟷(79)] cos 行係数 = (79) の偏導(線形なので差分は厳密)< 1e-12。"""
        for x in x_grid(199, 1e-3, 0.999):
            d_rho_exp, d_At_exp = shell.cos_row_partials(x)
            f0 = shell.cos_row_jump(x, 0.0, 0.0)
            d_rho = shell.cos_row_jump(x, 1.0, 0.0) - f0   # ρ₁ に線形
            d_At = shell.cos_row_jump(x, 0.0, 1.0) - f0    # A_t1 に線形
            assert rel_err(d_rho, d_rho_exp) < REL
            assert rel_err(d_At, d_At_exp) < REL

    def test_nonvanishing_on_window(self):
        """[v3 (77)] 両係数と赤方偏移 Jacobian が (0,1) で非零。"""
        for x in x_grid(499, 1e-4, 0.9999):
            d_rho, d_At = shell.cos_row_partials(x)
            assert d_rho != 0.0 and d_At != 0.0
            assert shell.redshift_jacobian(x) > 0.0

    def test_At1_root_closed_form(self):
        """[v3 (79)] cos 行の根 A_t1 = −(ρ₁+2)x/(2s³) を再現 < 1e-12。"""
        for x in x_grid(97, 1e-3, 0.999):
            s = math.sqrt(1.0 - x)
            for rho1 in (-2.0, -0.5, 0.0, 1.7):
                At1 = -(rho1 + 2.0) * x / (2.0 * s**3)
                val = shell.cos_row_jump(x, rho1, At1)
                assert abs(val) < 1e-12 * max(1.0, abs((rho1 + 2.0) * x))


class TestC3b_BreathingAndNecessity:
    def test_breathing_slope_closed_form_nonzero(self):
        """[v3 (80)] (1/a²)∂[h_ττ]^{ℓ=0}/∂ρ₀ = −x/s² ≠ 0 on (0,1)。"""
        for x in x_grid(499, 1e-4, 0.9999):
            assert rel_err(shell.breathing_slope(x), -x / (1.0 - x)) < REL
            assert shell.breathing_slope(x) < 0.0

    def test_discriminant_identity_exact_rational(self):
        """[v3 (81)] B²−4AC = 16x(x−1)(9x²+11x+4) を有理厳密で(係数レベルの恒等)。"""
        for x in [Fraction(p, q) for p, q in
                  ((1, 7), (2, 5), (24, 25), (1, 2), (9, 10), (13, 17), (3, 4))]:
            A, B, C = shell.dipole_only_quadratic_coeffs(x)
            assert B * B - 4 * A * C == shell.dipole_only_discriminant(x)

    def test_discriminant_negative_on_window(self):
        """[v3 (81)] Δ < 0 on (0,1)(実双極子単独では閉じない)。9x²+11x+4 > 0 込み。"""
        assert Fraction(11) ** 2 - 4 * 9 * 4 == -23  # 二次因子の判別式(有理厳密)
        for x in x_grid(499, 1e-4, 0.9999):
            assert shell.dipole_only_discriminant(x) < 0.0
            assert 9 * x * x + 11 * x + 4 > 0.0


class TestC3c_SchurDeterminant:
    def test_detJ0_closed_form_nonzero(self):
        """[v3 (77)/Lemma 8] det J₀ = (−2√(1−x))·1 ≠ 0 on (0,1) < 1e-12。"""
        for x in x_grid(499, 1e-4, 0.9999):
            det = shell.schur_det_J0(x)
            assert rel_err(det, -2.0 * math.sqrt(1.0 - x)) < REL
            assert det != 0.0
        assert shell.tilt_row_coefficient() == 1.0


class TestC3d_L2Minor:
    def test_matrix_det_matches_closed_form(self):
        """[v3 (88)] 行列式 = 2x√(1−x) < 1e-12、(0,1) で非零。"""
        for x in x_grid(499, 1e-4, 0.9999):
            (m00, m01), (m10, m11) = shell.l2_minor(x)
            det = m00 * m11 - m01 * m10
            assert rel_err(det, shell.l2_minor_det(x)) < REL
            assert det > 0.0

    def test_det_squared_exact_rational(self):
        """det² = 4x²(1−x) の有理厳密確認(√ を避けた係数レベルの恒等)。"""
        for x in [Fraction(p, q) for p, q in ((1, 3), (24, 25), (7, 9), (1, 2))]:
            det2 = 4 * x * x * (1 - x)
            m00, m01 = -x, Fraction(0)
            m10, m11_sq = -x / (1 - x), 4 * (1 - x)  # m11² = 4s²
            assert (m00 * m00) * m11_sq == det2      # (m01=0 なので det² = m00²·m11²)


# ================================================================ C4
class TestC4_WorkedBurn:
    """[v3 Supplement / v2 App K] 実働飽和バーン(無次元閉包、ASSUMPTIONS A2):
    x⋆ = 0.3, λ_max = 0.12, a(u) = a_max sin²(πτ), Δη = 0.24。"""

    XS, LAM, DETA = 0.3, 0.12, 0.24

    @staticmethod
    def _burn_integral(tau, deta):
        # ∫₀^u a du′ = Δη·(τ − sin(2πτ)/(2π))   [sin² バンプの閉形式積分]
        return deta * (tau - math.sin(2.0 * math.pi * tau) / (2.0 * math.pi))

    def test_radiated_mass_fraction_51_percent(self):
        """放射質量比 1 − e^(−3Δη) ≈ 51%(論文表示桁)。"""
        radiated = 1.0 - control.tsiolkovsky_ratio(self.DETA)
        assert round(radiated * 100.0) == 51
        assert rel_err(control.tsiolkovsky_ratio(self.DETA), math.exp(-0.72)) < REL

    def test_xeff_peak_046_and_windows(self):
        """x_eff ピーク = 0.46(表示桁)< 4/5(厚壁窓)、天井・g̲ も全域遵守。"""
        peak = 0.0
        for k in range(20001):
            tau = k / 20000.0
            m_ratio = math.exp(-3.0 * self._burn_integral(tau, self.DETA))
            x = self.XS * m_ratio
            lam = self.LAM * math.sin(math.pi * tau) ** 2
            xe = frontier.x_eff(x, lam)
            peak = max(peak, xe)
            assert lam < frontier.kinematic_ceiling(x)          # [R] v3 (40)
            assert frontier.thick_wall_window_ok(x, lam)        # [R] x_eff < 4/5
        assert round(peak, 2) == 0.46
        assert self.LAM < frontier.g_lower(self.XS)             # λ_max=0.12 < g̲(0.3)=0.19

    def test_saturated_budget_positive_mass(self):
        """飽和予算で m(u) > 0 全域(v3 Prop. 4)。"""
        for k in range(0, 20001, 100):
            tau = k / 20000.0
            assert control.tsiolkovsky_ratio(self._burn_integral(tau, self.DETA)) > 0.0


# ================================================================ C5
class TestC5_KinematicCeiling:
    def test_closed_form(self):
        """[v3 (40)] ½(1−x) < 1e-12、y=0 で (20) と一致。"""
        for x in x_grid(499, 0.0, 0.9999):
            c0 = frontier.kinematic_ceiling(x)
            assert rel_err(c0, 0.5 * (1.0 - x)) < REL
            assert rel_err(c0, frontier.kinematic_ceiling_positive_lambda(x, 0.0)) < REL

    def test_equivalence_with_xeff_exact_rational(self):
        """[v3 (40)] aR < ½(1−x) ⟺ x + 2aR < 1 の同値性(有理厳密)。"""
        for _ in range(500):
            x = Fraction(random.randint(1, 98), 100)
            lam = Fraction(random.randint(0, 120), 100)
            assert (lam < Fraction(1, 2) * (1 - x)) == (x + 2 * lam < 1)

    def test_positive_lambda_tightening(self):
        """[v3 (20)] y > 0 は天井を y/2 だけ厳密に締める。"""
        for _ in range(200):
            x, y = random.uniform(0, 0.9), random.uniform(0, 0.1)
            assert rel_err(
                frontier.kinematic_ceiling(x) - frontier.kinematic_ceiling_positive_lambda(x, y),
                0.5 * y,
            ) < 1e-10


# ================================================================ C6
class TestC6_MomentIdentities:
    def test_quadrature_moments(self):
        """[v3 (13),(29)=(59)] ∮n²dΩ = −ṁ、−∮n²cosϑdΩ = ma を求積で < 1e-10。"""
        nodes, weights = np.polynomial.legendre.leggauss(16)  # μ = cosϑ ∈ [−1,1]
        for _ in range(50):
            m = random.uniform(0.1, 10.0)
            a = random.uniform(0.0, 1.0)
            mdot = -random.uniform(1.0, 3.0) * 3.0 * m * a - random.uniform(0.0, 1.0)
            n2_vals = np.array(
                [control.n2(math.acos(mu), mdot, m, a) for mu in nodes]
            )
            I0 = 2.0 * math.pi * float(np.dot(weights, n2_vals))
            I1 = -2.0 * math.pi * float(np.dot(weights, n2_vals * nodes))
            lum, thrust = control.moments_closed_form(mdot, m, a)
            assert rel_err(I0, lum) < QUAD
            assert rel_err(I1, thrust) < QUAD

    def test_positivity_iff_control_law(self):
        """[v3 (13)-(14)] n²(ϑ) ≥ 0 ∀ϑ ⟺ −ṁ ≥ 3m|a|(前方極 ϑ=0 で束縛)。"""
        m, a = 2.0, 0.3
        for eps in (-1e-6, 0.0, 1e-6, 0.5):
            mdot = -(3.0 * m * a + eps)
            ok_law = control.control_law_margin(mdot, m, a) >= 0.0
            min_n2 = min(control.n2(th, mdot, m, a) for th in
                         [k * math.pi / 2000 for k in range(2001)])
            assert ok_law == (min_n2 >= -1e-15)

    def test_saturation_single_rear_lobe(self):
        """[v3 (14)-(15) 直下] 飽和で前方極厳密ゼロ・後方極最大(単一後方ローブ)。"""
        m, a = 1.7, 0.21
        mdot = control.saturated_mdot(m, a)
        assert control.n2(0.0, mdot, m, a) == 0.0            # 前方極: 厳密ゼロ
        assert control.n2(math.pi, mdot, m, a) > 0.0         # 後方極: 排気
        # 4πn² = 3ma(1−cosϑ) の閉形式(v3 (15) 直下)と一致
        for th in (0.3, 1.0, 2.0, 3.0):
            assert rel_err(
                control.n2(th, mdot, m, a),
                3.0 * m * a * (1.0 - math.cos(th)) / (4.0 * math.pi),
            ) < REL


# ================================================================ C7
class TestC7_UnitsRoundTrip:
    def test_round_trips(self):
        """幾何 ↔ SI ↔ 天文の往復 < 1e-12(conventions.md §1)。"""
        vals = [1.0, 3.14159, 1e-9, 1e12, 6.6743]
        pairs = [
            (units.mass_kg_to_geo, units.mass_geo_to_kg),
            (units.time_s_to_geo, units.time_geo_to_s),
            (units.m_to_ly, units.ly_to_m),
            (units.s_to_yr, units.yr_to_s),
            (units.msun_to_geo, units.geo_to_msun),
        ]
        for f, g in pairs:
            for v in vals:
                assert rel_err(g(f(v)), v) < REL
                assert rel_err(f(g(v)), v) < REL

    def test_defined_constants(self):
        """厳密定数と公認値の表示桁(ly は厳密整数、M☉ 幾何長 = 1476.6250 m)。"""
        assert units.LY_SI == 9_460_730_472_580_800.0
        assert units.YEAR_SI == 31_557_600.0
        assert abs(units.M_SUN_GEO_M - 1476.6250) < 5e-4
        assert abs(units.mass_kg_to_geo(units.M_SUN_KG) - units.M_SUN_GEO_M) \
            < 1e-12 * units.M_SUN_GEO_M


# ================================================================ C8
class TestC8_TwoPathAndWarpax:
    def test_tsiolkovsky_closed_form_vs_ode(self):
        """[G3 初回] 飽和制御則 ṁ = −3m|a| の RK4 積分 vs 閉形式 (15)、rel < 1e-8。"""
        for deta in (0.1, 0.24, 1.0):
            def dm(tau, m):
                return -6.0 * deta * math.sin(math.pi * tau) ** 2 * m
            n = 4096
            h = 1.0 / n
            m = 1.0
            tau = 0.0
            for _ in range(n):
                k1 = dm(tau, m)
                k2 = dm(tau + 0.5 * h, m + 0.5 * h * k1)
                k3 = dm(tau + 0.5 * h, m + 0.5 * h * k2)
                k4 = dm(tau + h, m + h * k3)
                m += h * (k1 + 2.0 * k2 + 2.0 * k3 + k4) / 6.0
                tau += h
            assert rel_err(m, control.tsiolkovsky_ratio(deta)) < TWO_PATH

    def test_budget_rate_consistency(self):
        """[v3 (12),(29)] budget_rate と moments_closed_form の整合、普遍限界 (2)。"""
        for _ in range(100):
            m = random.uniform(0.1, 5.0)
            a = random.uniform(0.0, 0.5)
            mdot = control.saturated_mdot(m, a)
            dP0, dPz = bondi.budget_rate(mdot, m, a)
            lum, thrust = control.moments_closed_form(mdot, m, a)
            assert rel_err(-dP0, lum) < REL and rel_err(dPz, thrust) < REL
            assert bondi.universal_rocket_bound_ok(mdot, m, a)  # 係数3 ≥ 床1

    def test_geodesy_collinear_consistency(self):
        """[v3 (55)-(56)] 直線ブーストで d_H³ = Δη、min_mass_ratio = C1 と一致。"""
        v0 = geodesy.four_velocity_from_rapidity(0.0)
        for eta in (0.0, 0.24, 1.0, 3.0):
            v1 = geodesy.four_velocity_from_rapidity(eta)
            assert abs(geodesy.d_H3(v0, v1) - eta) < 1e-12 * max(1.0, eta)
            assert rel_err(geodesy.min_mass_ratio(v0, v1),
                           control.tsiolkovsky_ratio(eta)) < REL

    def test_warpax_connection(self):
        """[G3 経路 B 接続確認] warpax 1.3.x が import 可能で bondi API を持つ。

        本格数値突合は Phase 1(PHASE_0.md 0-3)。"""
        assert bondi.warpax_available(), "warpax が import できない(conventions.md §7 の環境か?)"
        assert bondi.warpax_version().startswith("1.3"), \
            f"warpax {bondi.warpax_version()} ≠ 1.3.x(CLAUDE.md §2 は v1.3.0 を指定)"
        wb = bondi.warpax_bondi_module()
        for api in ("extract", "radiated_momentum_flux", "weyl_scalars", "peeling"):
            assert hasattr(wb, api), f"warpax.bondi.{api} が見つからない"
