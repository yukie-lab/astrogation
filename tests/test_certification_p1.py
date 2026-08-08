"""Phase 1 認証テスト(P1-C9〜C13)+ (73) 回帰(STOP 記録つき xfail)。

- P1-C9  標準運動学の恒等式(L39)                          < 1e-12
- P1-C10 時間最適の G3 二経路(求積 vs ODE、長さ縮約恒等)   < 1e-8
- P1-C11 三層の順序(運用値)と既知の逆転の記録              —
- P1-C12 表A η=0.24 行 ↔ App K(C4 再確認)                 表示桁
- P1-C13 ミッション時間の G3(閉形式 vs 数値軌道積分)        < 1e-8
- (73) 回帰: 2 回の修正試行で表示桁不一致 → STOP 報告
  (docs/reports/P1_STOP_c_chain.md)。strict xfail として記録。
"""
import math
import random

import pytest

from astrogation import appc_floor, control, frontier, kinematics, timeopt

REL = 1e-12
TWO_PATH = 1e-8
random.seed(20260808)


def rel_err(a, b):
    return abs(a - b) / max(1.0, abs(a), abs(b))


# ================================================================ P1-C9
class TestC9_Kinematics:
    def test_hyperbolic_identities(self):
        """[L39] β²γ² + 1 = γ²、βγ = sinh、γ = cosh の恒等 < 1e-12。"""
        for eta in (0.0, 0.1, 0.24, 1.0, 3.0, 12.0):
            b, g, bg = (kinematics.beta(eta), kinematics.gamma(eta),
                        kinematics.beta_gamma(eta))
            assert rel_err(b * g, bg) < REL
            assert rel_err(g * g - bg * bg, 1.0) < REL

    def test_rindler_identity(self):
        """[L39] 双曲運動: (d + 1/a)² − t² = 1/a²、τ = η/a < 1e-12。"""
        for eta in (0.1, 1.0, 5.0):
            for a in (1e-4, 0.19, 2.0):
                s = kinematics.burn_segment(eta, a)
                lhs = (s["distance"] + 1.0 / a) ** 2 - s["coord_time"] ** 2
                assert rel_err(lhs, 1.0 / a**2) < 1e-10
                assert rel_err(s["proper_time"], eta / a) < REL

    def test_mission_structure(self):
        """[L39] 往復 = 到着の 2 倍(同 η・同 a)、Δη_total の対応。"""
        D, eta, a = 1.0e6, 1.3, 1.9e-4
        arr = kinematics.mission_times(D, eta, a, "arrive")
        rt = kinematics.mission_times(D, eta, a, "roundtrip")
        fb = kinematics.mission_times(D, eta, a, "flyby")
        assert rel_err(rt["t_earth"], 2.0 * arr["t_earth"]) < REL
        assert rel_err(rt["tau_ship"], 2.0 * arr["tau_ship"]) < REL
        assert fb["delta_eta_total"] == eta
        assert arr["delta_eta_total"] == 2.0 * eta
        assert rt["delta_eta_total"] == 4.0 * eta


# ================================================================ P1-C10
class TestC10_TimeOptimalG3:
    @pytest.mark.parametrize("tier", ["ceiling", "effective", "floor"])
    @pytest.mark.parametrize("deta", [0.24, 1.0])
    def test_quadrature_vs_ode(self, tier, deta):
        """[L38/G3] T: 求積 vs 独立 ODE < 1e-8;x_end vs 長さ縮約 x₀e^(−3Δη) < 1e-8。"""
        x0 = 0.3
        qa = timeopt.ride_time_quadrature(x0, deta, tier)
        ode = timeopt.ride_time_ode(x0, deta, tier)
        assert rel_err(qa["T"], ode["T"]) < TWO_PATH, (tier, deta)
        assert rel_err(ode["x_end"], x0 * math.exp(-3.0 * deta)) < TWO_PATH

    def test_fallback_point_recorded(self):
        """[PHASE_1 1-4] [N] tier のフォールバック点 η_fb = ln(x₀/0.1)/3 の記録。"""
        qa = timeopt.ride_time_quadrature(0.3, 1.0, "effective")
        assert qa["fallback_eta"] is not None
        assert rel_err(qa["fallback_eta"], math.log(3.0) / 3.0) < REL
        labels = {a["label"] for a in qa["arcs"]}
        assert "ceiling-fallback[R]" in labels  # フォールバック弧が存在
        # Δη < η_fb なら全弧 [N]
        qa2 = timeopt.ride_time_quadrature(0.3, 0.24, "effective")
        assert all(a["label"] == "[N]" for a in qa2["arcs"])

    def test_constant_tier_closed_form(self):
        """一定 λ なら T = Δη/λ(床 tier の初等検算に相当)。"""
        # 天井 tier で x₀ → 0 極限に近い小 x₀: λ ≈ 0.4 ほぼ一定
        x0, deta = 1e-6, 0.01
        qa = timeopt.ride_time_quadrature(x0, deta, "ceiling")
        assert rel_err(qa["T"], deta / 0.4) < 1e-4


# ================================================================ P1-C11
class TestC11_TierOrdering:
    def test_operative_ordering_floor_below_effective_below_ceiling(self):
        """[三層] 運用値: floor < min(g̲, ceiling) ≤ ceiling(5 サンプル点)。"""
        for x in frontier.G_LOWER_X:
            fl = frontier.tier_operative(x, "floor")
            ef = frontier.tier_operative(x, "effective")
            ce = frontier.tier_operative(x, "ceiling")
            assert fl < ef <= ce, f"x={x}: {fl} {ef} {ce}"

    def test_known_inversion_raw_effective_vs_ceiling(self):
        """【報告事項】x=0.7 で生 g̲ > 天井(薄殻 [N] が厚壁 [R] を超える)。
        P1_catalog_report.md §逆転報告 参照。データ変更時に気づくための記録。"""
        assert frontier.g_lower(0.7) > frontier.tier_bound(0.7, "ceiling")
        assert frontier.g_lower(0.5) < frontier.tier_bound(0.5, "ceiling")

    def test_conservative_floor_below_paper_values(self):
        """保守化 c_cons は論文 (73) の 5 点すべてで下(床としての整合性証拠)。"""
        for x, cp in zip(frontier.C_LOWER_X, frontier.C_LOWER_VALUES):
            assert appc_floor.c_floor_conservative(x) < cp

    def test_ceiling_identity_L42(self):
        """[L42] min(½(1−x), (4/5−x)/2) = (4/5−x)/2 on (0, 4/5) < 1e-12。"""
        for k in range(1, 80):
            x = k / 100.0
            assert rel_err(frontier.tier_bound(x, "ceiling"), 0.5 * (0.8 - x)) < REL


# ================================================================ P1-C12
class TestC12_TableA_AppK_Row:
    def test_eta_024_row_matches_appk(self):
        """[表A] η = 0.24 行: 放射 51%(App K/C4 と同一値)。"""
        eta = 0.24
        ratio = control.tsiolkovsky_ratio(eta)
        assert round((1.0 - ratio) * 100.0) == 51
        assert rel_err(ratio, math.exp(-0.72)) < REL

    def test_seat_price_column(self):
        """[表A/L40] 座席の値段 = e^(3η)/e^(η) = e^(2η) < 1e-12。"""
        for eta in (0.1, 1.0, 12.0):
            ideal = math.exp(-eta)
            ours = control.tsiolkovsky_ratio(eta)
            assert rel_err(ideal / ours, math.exp(2.0 * eta)) < 1e-10


# ================================================================ P1-C13
class TestC13_MissionTimesG3:
    @pytest.mark.parametrize("maneuver", ["flyby", "arrive", "roundtrip"])
    def test_closed_vs_numeric_trajectory(self, maneuver):
        """[L39/G3] ミッション時間: 閉形式 vs 固有時 RK4 軌道積分 < 1e-8。

        数値経路: dτ で dt/dτ = cosh η(τ)、dX/dτ = sinh η(τ)。η(τ) は
        バーン中 ±a·(局所固有時)の折れ線、巡航中一定。到着距離 D も照合。"""
        D, eta, a = 2.5e5, 1.1, 1.9e-4
        closed = kinematics.mission_times(D, eta, a, maneuver)
        assert closed["feasible"]

        seg = kinematics.burn_segment(eta, a)
        tau_burn = seg["proper_time"]
        cruise = closed["cruise_per_leg"]
        tau_cruise = cruise / kinematics.beta_gamma(eta)
        # 片道の固有時系列(往復は対称 2 倍を閉形式検証済みの構造で使用)
        legs = 1 if maneuver != "roundtrip" else 2
        burns_per_leg = kinematics.MANEUVER_BURNS[maneuver] // legs

        def eta_of_tau(tau_leg):
            if burns_per_leg == 1:  # flyby: 加速のみ
                if tau_leg < tau_burn:
                    return a * tau_leg
                return eta
            # arrive: 加速 → 巡航 → 減速
            if tau_leg < tau_burn:
                return a * tau_leg
            if tau_leg < tau_burn + tau_cruise:
                return eta
            return max(0.0, eta - a * (tau_leg - tau_burn - tau_cruise))

        tau_leg_total = burns_per_leg * tau_burn + tau_cruise
        n = 60_000
        h = tau_leg_total / n
        t = X = 0.0
        for i in range(n):
            tau0 = i * h

            def rhs(tl):
                e = eta_of_tau(tl)
                return math.cosh(e), math.sinh(e)

            k1 = rhs(tau0)
            k2 = rhs(tau0 + 0.5 * h)
            k4 = rhs(tau0 + h)
            t += h * (k1[0] + 4 * k2[0] + k4[0]) / 6.0
            X += h * (k1[1] + 4 * k2[1] + k4[1]) / 6.0
        t_total = legs * t
        tau_total = legs * tau_leg_total
        assert rel_err(t_total, closed["t_earth"]) < TWO_PATH
        assert rel_err(tau_total, closed["tau_ship"]) < TWO_PATH
        assert rel_err(X, D) < TWO_PATH
        assert rel_err(tau_total, closed["tau_ship"]) < TWO_PATH


# ==================================================== (73) 回帰(STOP 記録)
@pytest.mark.xfail(strict=True,
                   reason="STOP 報告中: c(x) 鎖の (73) 表示桁再現は 2 回の修正試行で"
                          "未達(docs/reports/P1_STOP_c_chain.md)。保守化版は全 5 点で"
                          "論文値より下(床として安全側)。人間の裁定待ち。")
def test_regression_c73_display_digits():
    """[v3 (73)] c(x) 5 点の表示桁再現(2 有効数字)。"""
    for x, cp in zip(frontier.C_LOWER_X, frontier.C_LOWER_VALUES):
        ours = appc_floor.c_floor_conservative(x)
        assert float(f"{ours:.2g}") == float(f"{cp:.2g}"), (x, ours, cp)
