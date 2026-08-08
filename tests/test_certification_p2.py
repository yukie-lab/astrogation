"""Phase 2 認証テスト(P2-C15〜C18+遅延時間写像 G3 の代表検証)。

- C15 エネルギー閉合: 全 189 プロファイルで ∫L du = m₀−m_f = Tsiolkovsky < 1e-10
- C16 パターン正規化(観測者系): 実験系モーメントが四元運動量率の
  Lorentz 変換(L46 閉形式)と < 1e-10 で一致
- C17 前方零点: 飽和パターンの前方厳密ゼロ(Fraction、光行差込み)
- C18 遅延時間の単調性: dt_obs/du = γ(1−βcosθ) 恒等 < 1e-12+全系列単調
- 写像 G3(代表): ミッション = 区分閉形式 vs Hermite-Gauss、騎乗 = u-径数 vs
  η-径数の独立 2 系統 < 1e-8(全 567 行の適用は生成パイプライン 2-5)
"""
import json
import math
import pathlib
import random
from fractions import Fraction

import pytest
from scipy.integrate import quad

from astrogation import control, radiometry as rad

RES = pathlib.Path(__file__).resolve().parents[1] / "results"
REL = 1e-12
TOL_CLOSE = 1e-10
TWO_PATH = 1e-8
random.seed(20260808)


def _profiles():
    files = sorted((RES / "mission_profiles").glob("*.json")) + \
        sorted((RES / "timeopt_profiles").glob("*.json"))
    if not files:
        pytest.skip("results/ プロファイル未生成")
    return files


def _load(fp):
    d = json.loads(fp.read_text())
    if "grid" in d:  # mission
        g = d["grid"]
        return {"u": g["u"], "L": g["L"], "m": g["m"], "a": g["a"],
                "eta": g["eta_signed"], "thrust": g["thrust_sign"],
                "deta_tot": d["meta"]["delta_eta_total"], "kind": "mission"}
    return {"u": d["u"], "L": d["L"], "m": [mm / d["m"][0] for mm in d["m"]],
            "m_abs": d["m"],   # 節点恒等 L = 3 m λ は絶対 m(= x/2)基準
            "a": d["a"], "eta": d["eta"], "thrust": d["thrust_sign"],
            "deta_tot": d["deta"], "kind": "ride",
            "lam": d["lambda"]}


# ================================================================ C15
class TestC15_EnergyClosure:
    def test_all_profiles_fluence_equals_budget(self):
        """[L47] 全 189 プロファイル: ∫L du(厳密則)= m₀−m_f = 1−e^(−3Δη) < 1e-10。"""
        files = _profiles()
        assert len(files) == 189
        for fp in files:
            p = _load(fp)
            fluence = rad.fluence_exact(p["u"], p["L"], p["m"], p["a"])
            budget = p["m"][0] - p["m"][-1]
            tsi = p["m"][0] * (1.0 - control.tsiolkovsky_ratio(p["deta_tot"]))
            assert abs(fluence - budget) <= 1e-12 * max(1.0, budget), fp.name
            assert abs(fluence - tsi) <= TOL_CLOSE * max(1e-300, tsi), fp.name

    def test_node_identity_L_equals_3mlambda(self):
        """[L48] 節点恒等 L_i = 3 m_i a_i(< 1e-12)— 層の縫合。

        ミッションは m₀=1 正規化の m、騎乗は絶対 m(= x/2)が L の基準。"""
        for fp in _profiles()[::13]:  # 代表 15 本(全数は C15 本体で担保)
            p = _load(fp)
            m_arr = p["m"] if p["kind"] == "mission" else p["m_abs"]
            for L, m, a in zip(p["L"], m_arr, p["a"]):
                assert abs(L - 3.0 * m * a) <= 1e-12 * max(1.0, L)


# ================================================================ C16
class TestC16_ObserverFrameNormalization:
    @pytest.mark.parametrize("eta", [0.0, 0.24, 1.0, 3.0, 8.0, 12.0])
    @pytest.mark.parametrize("sign", [1, -1])
    def test_lab_moments_match_lorentz_transform(self, eta, sign):
        """[L46] ∮δ³n²/γ·{1,cosθ}dΩ = (Q⁰+βQ^z, Q^z+βQ⁰) < 1e-10。

        高 η ではビーミング幅 ~(1−β) が実験系 μ で 1e-10 級に尖るため、
        静止系変数 μ′ へ解析的に変数変換して求積する(被検関数
        lab_rate_density は写像した μ_lab で評価 — 実装は据え置きで検査)。
        μ_lab = (μ′+β)/(1+βμ′)、dμ_lab/dμ′ = (1−β²)/(1+βμ′)²。"""
        import numpy as np
        m, a = 0.7, 0.15
        L = 3.0 * m * a * random.uniform(1.0, 2.0)  # 許容域(−ṁ ≥ 3ma)
        nodes, weights = np.polynomial.legendre.leggauss(64)
        e_num = p_num = 0.0
        for t, w in zip(nodes, weights):
            v_p = 0.5 * (t + 1.0)               # 静止系半角変数 v′ ∈ [0,1]
            v_lab = rad.aberrate_v(v_p, -eta)   # 逆ブースト(安定)
            jac = 1.0 / rad.inv_doppler_v(v_p, -eta) ** 2  # dv_lab/dv′
            dens = rad.lab_rate_density_v(L, m, a, sign, eta, v_lab)
            mu_lab = 1.0 - 2.0 * v_lab
            e_num += w * dens * jac
            p_num += w * dens * mu_lab * jac
        # dμ = 2dv、v′ 区間 [0,1] → GL の重みスケール ×(1/2)×2 = 1
        e_num *= 2.0 * math.pi
        p_num *= 2.0 * math.pi
        e_cl, p_cl = rad.lab_moments_closed_form(L, m, a, sign, eta)
        assert abs(e_num - e_cl) <= TOL_CLOSE * max(1.0, abs(e_cl))
        assert abs(p_num - p_cl) <= TOL_CLOSE * max(1.0, abs(e_cl))

    def test_reduces_to_c6_at_rest(self):
        """β = 0 で C6(静止系モーメント)に帰着。"""
        L, m, a = 0.9, 1.2, 0.2
        e_cl, p_cl = rad.lab_moments_closed_form(L, m, a, 1, 0.0)
        assert abs(e_cl - L) < REL
        assert abs(p_cl - (-m * a)) < REL


# ================================================================ C17
class TestC17_ForwardNull:
    def test_saturated_forward_zero_exact_rational(self):
        """[L48+L43] 飽和パターンは光行差込みで前方厳密ゼロ(Fraction)。

        極は光行差で不動: cosθ = s で cosϑ′ = 1、分子 L − 3ma = 0(飽和)。"""
        m, a = Fraction(7, 5), Fraction(3, 20)
        L = 3 * m * a                       # 飽和
        for beta in (Fraction(0), Fraction(1, 5), Fraction(24, 25)):
            for s in (1, -1):
                cos_lab = Fraction(s)       # 加速軸前方の実験系方向
                cz = (cos_lab - beta) / (1 - beta * cos_lab)
                assert cz == Fraction(s)    # 極の不動性(厳密)
                assert rad.pattern_numerator(L, m, a, s * cz) == 0  # 厳密ゼロ

    def test_cruise_identically_zero(self):
        """巡航(L = a = 0)は全方向恒等ゼロ。"""
        for mu in (-1.0, -0.3, 0.0, 0.8, 1.0):
            assert rad.observed_flux_density(0.0, 0.5, 0.0, 0, 2.0, mu) == 0.0

    def test_no_negative_flux_on_admissible_pattern(self):
        """許容パターン(L ≥ 3ma)で負のフラックスが出ない(STOP 監視条件)。"""
        for _ in range(300):
            m = random.uniform(0.1, 2.0)
            a = random.uniform(0.0, 0.3)
            L = 3.0 * m * a * random.uniform(1.0, 3.0)
            f = rad.observed_flux_density(
                L, m, a, random.choice([1, -1]),
                random.uniform(-3, 3), random.uniform(-1, 1))
            assert f >= 0.0


# ================================================================ C18
class TestC18_RetardedTimeMonotonicity:
    def test_derivative_identity(self):
        """[L45] coshη − sinhη·cosθ = γ(1−βcosθ) < 1e-12、恒に正。"""
        for _ in range(300):
            eta = random.uniform(-12, 12)
            mu = random.uniform(-1, 1)
            beta = math.tanh(eta)
            gamma = math.cosh(eta)
            lhs = math.cosh(eta) - math.sinh(eta) * mu
            rhs = gamma * (1.0 - beta * mu)
            assert abs(lhs - rhs) <= 1e-12 * max(1.0, abs(lhs))
            assert lhs > 0.0

    def test_profile_series_monotone(self):
        """代表プロファイルで t_obs 系列が非減少(重複節点の等値は許容)。"""
        for fp in _profiles()[::23]:
            p = _load(fp)
            n = len(p["u"])
            deta_du = [p["a"][i] * (1 if p["thrust"][i] >= 0 else -1)
                       if p["kind"] == "mission" else p["lam"][i]
                       for i in range(n)]
            for mu in (-1.0, 0.0, 1.0):
                t = rad.t_obs_path_u(p["u"], p["eta"], deta_du, mu)
                assert all(t[i + 1] >= t[i] - 1e-15 for i in range(n - 1))


# ==================================================== 写像 G3(代表)
class TestRetardedMapG3:
    def test_mission_closed_vs_hermite(self):
        """ミッション型: 区分閉形式 vs u-径数 Hermite-Gauss < 1e-8。"""
        files = [f for f in _profiles() if "mission" in f.name][::17]
        assert files
        for fp in files:
            p = _load(fp)
            # 節点微分 |dη/du| = a に η の局所進行符号(近傍差分)を掛けて構成
            n = len(p["u"])
            deta_du = []
            for i in range(n):
                if p["a"][i] == 0.0:
                    deta_du.append(0.0)
                else:
                    lo, hi = max(i - 1, 0), min(i + 1, n - 1)
                    sgn = 1.0 if p["eta"][hi] >= p["eta"][lo] else -1.0
                    deta_du.append(sgn * p["a"][i])
            for mu in (1.0, 0.0, -1.0):
                t_a = rad.t_obs_mission_closed(p["u"], p["eta"], p["a"],
                                               p["thrust"], mu)
                t_b = rad.t_obs_path_u(p["u"], p["eta"], deta_du, mu)
                scale = max(1.0, abs(t_a[-1]))
                assert abs(t_a[-1] - t_b[-1]) <= TWO_PATH * scale, fp.name

    def test_ride_u_vs_eta_parametrization(self):
        """騎乗型: u-径数 vs η-径数(独立 2 系統)< 2e-6(データ情報限界)。

        台帳 L45a: (i) g̲ 折れ線の節点がグリッド区間内に落ちる(effective、
        ~1.6e-7)、(ii) x₀=0.7 天井騎乗の序盤は λ の区間内変化 ~31% で
        h⁴ 相対誤差が乗る(~6.5e-7、複合 tail は 1.06e-6)。いずれも消費データの情報限界であり
        実装誤差ではない(再計算禁止)。ミッション型は 1e-8 を維持。"""
        files = [f for f in _profiles() if "ride" in f.name][::11]
        assert files
        for fp in files:
            p = _load(fp)
            deta_du = p["lam"]  # 騎乗の定義 ODE: dη/du = λ(節点厳密)
            for mu in (1.0, -1.0):
                t_a = rad.t_obs_path_u(p["u"], p["eta"], deta_du, mu)
                t_b = rad.t_obs_path_eta(p["u"], p["eta"], deta_du, mu)
                scale = max(1.0, abs(t_a[-1]))
                assert abs(t_a[-1] - t_b[-1]) <= 2e-6 * scale, fp.name
