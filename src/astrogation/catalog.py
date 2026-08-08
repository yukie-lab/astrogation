"""航路カタログ生成(PHASE_1.md 1-2〜1-7)。

全行に G3 二経路照合を適用(相対 1e-8 超は欠番+理由記録、1 行でも STOP)。
全数値に権威ラベル。式の供給源は式台帳 L2(+Phase 1 追記 L38-L42)のみ。
無次元部は R = 1 正規化。SI 換算は units.py のみ(C7 認証済み)。
"""
import json
import math

import numpy as np

from . import control, frontier, geodesy, kinematics, timeopt, units

G3_TOL = 1e-8

ETA_LADDER = (0.1, 0.24, 0.5, 1.0, 2.0, 3.0, 5.0, 8.0, 12.0)

DESTINATIONS = (  # conventions.md §8(PHASE_1.md 指示で固定)
    ("Proxima Centauri", 4.25),
    ("TRAPPIST-1", 40.5),
    ("Sgr A*", 2.6e4),
    ("M31 (Andromeda)", 2.54e6),
)
MANEUVERS = ("flyby", "arrive", "roundtrip")

# A4: 表B バーン規約 — λ_burn = g̲(0.3) = 0.19 [N] @ x₀ = 0.3、R_ref = 1 km
X0_MISSION = 0.3
LAMBDA_BURN = 0.19
R_REF_M = 1000.0


# ================================================================ 表A
def table_a_rows():
    """表A: ラピディティ階段(行き先非依存、全行 [R])。G3 込み。"""
    rows = []
    for eta in ETA_LADDER:
        ratio = control.tsiolkovsky_ratio(eta)          # [R] (15)
        # --- G3 経路B: 飽和制御則 ODE(sin² バーン、RK4)。
        # ステップ数は減衰率に比例(η=12 で e^(−36) — 固定 4000 では不足)
        n = int(4000 * max(1.0, eta))
        h = 1.0 / n
        m = 1.0
        for i in range(n):
            tau = i * h

            def dm(t, mm, _e=eta):
                return -6.0 * _e * math.sin(math.pi * t) ** 2 * mm

            k1 = dm(tau, m)
            k2 = dm(tau + h / 2, m + h * k1 / 2)
            k3 = dm(tau + h / 2, m + h * k2 / 2)
            k4 = dm(tau + h, m + h * k3)
            m += h * (k1 + 2 * k2 + 2 * k3 + k4) / 6.0
        g3_mass = abs(m - ratio) / max(ratio, 1e-300)
        # --- G3: H³ 距離(arccosh vs Δη)
        v0 = geodesy.four_velocity_from_rapidity(0.0)
        v1 = geodesy.four_velocity_from_rapidity(eta)
        g3_dist = abs(geodesy.d_H3(v0, v1) - eta) / max(eta, 1e-300)
        g3_ok = g3_mass < G3_TOL and g3_dist < G3_TOL
        rows.append({
            "eta": eta,
            "beta": kinematics.beta(eta),
            "gamma": kinematics.gamma(eta),
            "mf_over_m0": ratio,                        # [R]
            "radiated_fraction": 1.0 - ratio,           # [R]
            "ideal_photon_mf_m0": math.exp(-eta),       # [R] L40
            "seat_price_e2eta": math.exp(2.0 * eta),    # [R] L40
            "authority": "[R]",
            "g3": {"mass_rel": g3_mass, "dist_rel": g3_dist, "ok": g3_ok},
        })
    return rows


# ================================================================ 表B
def _numeric_mission(D, eta, a, maneuver, n_seg=4096):
    """G3 経路B: 固有時 Simpson で軌道積分(区分ごとに滑らか)。"""
    seg = kinematics.burn_segment(eta, a)
    closed = kinematics.mission_times(D, eta, a, maneuver)
    legs = kinematics.MANEUVER_LEGS[maneuver]
    burns_per_leg = kinematics.MANEUVER_BURNS[maneuver] // legs
    tau_b = seg["proper_time"]
    tau_c = closed["cruise_per_leg"] / kinematics.beta_gamma(eta)

    def simpson(fn, t0, t1, n=n_seg):
        xs = np.linspace(t0, t1, n + 1)
        ys = fn(xs)
        w = np.ones(n + 1)
        w[1:-1:2] = 4.0
        w[2:-1:2] = 2.0
        return float(np.dot(w, ys)) * (t1 - t0) / (3.0 * n)

    t = x_cov = 0.0
    # 加速バーン
    t += simpson(lambda tt: np.cosh(a * tt), 0.0, tau_b)
    x_cov += simpson(lambda tt: np.sinh(a * tt), 0.0, tau_b)
    # 巡航
    t += math.cosh(eta) * tau_c
    x_cov += math.sinh(eta) * tau_c
    if burns_per_leg == 2:  # 減速
        t += simpson(lambda tt: np.cosh(eta - a * tt), 0.0, tau_b)
        x_cov += simpson(lambda tt: np.sinh(eta - a * tt), 0.0, tau_b)
    tau_leg = burns_per_leg * tau_b + tau_c
    return legs * t, legs * tau_leg, x_cov


def table_b_rows():
    """表B: ミッション表(4 行き先 × 3 機動型 × η 階段)。G3 込み。"""
    a_geo = LAMBDA_BURN / R_REF_M  # [1/m](A4 規約)
    rows = []
    for name, d_ly in DESTINATIONS:
        D = units.ly_to_m(d_ly)
        for man in MANEUVERS:
            for eta in ETA_LADDER:
                closed = kinematics.mission_times(D, eta, a_geo, man)
                if not closed["feasible"]:
                    rows.append({"dest": name, "maneuver": man, "eta": eta,
                                 "feasible": False})
                    continue
                t_num, tau_num, x_num = _numeric_mission(D, eta, a_geo, man)
                g3_t = abs(t_num - closed["t_earth"]) / closed["t_earth"]
                g3_tau = abs(tau_num - closed["tau_ship"]) / closed["tau_ship"]
                g3_d = abs(x_num - D) / D
                g3_ok = max(g3_t, g3_tau, g3_d) < G3_TOL
                deta_tot = closed["delta_eta_total"]
                rows.append({
                    "dest": name, "dist_ly": d_ly, "maneuver": man, "eta": eta,
                    "feasible": True,
                    "delta_eta_total": deta_tot,
                    "mf_over_m0": control.tsiolkovsky_ratio(deta_tot),   # [R]
                    "t_earth_yr": units.s_to_yr(
                        units.time_geo_to_s(closed["t_earth"])),
                    "tau_ship_yr": units.s_to_yr(
                        units.time_geo_to_s(closed["tau_ship"])),
                    "burn_t_earth_s": units.time_geo_to_s(
                        closed["burn_coord_time_total"]),
                    "authority": "燃料[R] 時間[R-standard] バーンa[N]@x0=0.3",
                    "g3": {"t_rel": g3_t, "tau_rel": g3_tau, "dist_rel": g3_d,
                           "ok": g3_ok},
                })
    return rows


def eta50_rows(tau_years=50.0):
    """固有時間 τ = 50 yr の等高線(行き先 × 機動型ごとの η しきい値)。"""
    a_geo = LAMBDA_BURN / R_REF_M
    tau_target = units.time_s_to_geo(units.yr_to_s(tau_years))
    out = []
    for name, d_ly in DESTINATIONS:
        D = units.ly_to_m(d_ly)
        for man in MANEUVERS:
            eta50 = kinematics.eta_for_proper_time(D, tau_target, a_geo, man)
            deta = kinematics.MANEUVER_BURNS[man] * eta50
            out.append({
                "dest": name, "maneuver": man, "eta_50yr": eta50,
                "delta_eta_total": deta,
                "mf_over_m0": control.tsiolkovsky_ratio(deta),
                "authority": "[R-standard]+[R]",
            })
    return out


# ==================================================== 時間最適(1-4)
TIMEOPT_X0 = (0.3, 0.5, 0.7)
TIERS = ("floor", "effective", "ceiling")


def timeopt_rows(ode_steps=50_000):
    """フロンティア騎乗 T/R(三層×x₀×Δη)。G3(求積 vs ODE+長さ縮約)込み。"""
    rows = []
    for x0 in TIMEOPT_X0:
        for deta in ETA_LADDER:
            for tier in TIERS:
                qa = timeopt.ride_time_quadrature(x0, deta, tier)
                ode = timeopt.ride_time_ode(x0, deta, tier, n_steps=ode_steps)
                g3_t = abs(qa["T"] - ode["T"]) / qa["T"]
                g3_x = abs(ode["x_end"] - x0 * math.exp(-3.0 * deta)) / \
                    (x0 * math.exp(-3.0 * deta))
                rows.append({
                    "x0": x0, "deta": deta, "tier": tier,
                    "T_over_R": qa["T"],
                    "authority": frontier.TIER_AUTHORITY[tier],
                    "fallback_eta": qa["fallback_eta"],
                    "n_arcs": len(qa["arcs"]),
                    "arcs": qa["arcs"],
                    "g3": {"T_rel": g3_t, "xend_rel": g3_x,
                           "ok": max(g3_t, g3_x) < G3_TOL},
                })
    return rows


# ==================================================== ミッションプロファイル(1-7)
def mission_profile(name, d_ly, eta, maneuver, n_burn=101):
    """Phase 2 入力プロファイル(u 格子、A4 規約バーン)。u は R_ref 単位の幾何長。"""
    a = LAMBDA_BURN / R_REF_M
    D = units.ly_to_m(d_ly)
    closed = kinematics.mission_times(D, eta, a, maneuver)
    if not closed["feasible"]:
        return None
    legs = kinematics.MANEUVER_LEGS[maneuver]
    burns_per_leg = kinematics.MANEUVER_BURNS[maneuver] // legs
    u_burn = eta / (LAMBDA_BURN / 1.0)  # Γ 固有時間 = η/a、R_ref 単位: η/λ
    tau_c_geo = closed["cruise_per_leg"] / kinematics.beta_gamma(eta)
    u_cruise = tau_c_geo / R_REF_M      # R_ref 単位
    # 排気向き(推力符号): 加速 +1 / 減速 −1;復路はアウトバウンド軸基準で反転
    plan = []
    for leg in range(legs):
        sgn = 1 if leg == 0 else -1
        plan.append(("burn", +1 * sgn))
        plan.append(("cruise", 0))
        if burns_per_leg == 2:
            plan.append(("burn", -1 * sgn))
    u_grid, a_arr, m_arr, x_arr, eta_arr, lum, thrust = [], [], [], [], [], [], []
    u_now, m_now, eta_now = 0.0, 1.0, 0.0
    x_now = X0_MISSION
    for kind, sgn in plan:
        if kind == "burn":
            for i in range(n_burn):
                f = i / (n_burn - 1)
                du = u_burn * f
                eta_loc = LAMBDA_BURN * du  # |dη/du| = λ(R=1 単位)
                m_i = m_now * math.exp(-3.0 * eta_loc)
                u_grid.append(u_now + du)
                a_arr.append(LAMBDA_BURN)
                m_arr.append(m_i)
                x_arr.append(x_now * math.exp(-3.0 * eta_loc))
                eta_arr.append(eta_now + sgn * eta_loc if sgn != 0 else eta_now)
                lum.append(3.0 * m_i * LAMBDA_BURN)   # L = −ṁ = 3mλ(R=1)
                thrust.append(sgn)
            u_now += u_burn
            m_now *= math.exp(-3.0 * eta)
            x_now *= math.exp(-3.0 * eta)
            eta_now = eta_arr[-1]
        else:
            for du in (0.0, u_cruise):
                u_grid.append(u_now + du)
                a_arr.append(0.0)
                m_arr.append(m_now)
                x_arr.append(x_now)
                eta_arr.append(eta_now)
                lum.append(0.0)
                thrust.append(0)
            u_now += u_cruise
    # G3: 質量閉形式照合
    mf_closed = control.tsiolkovsky_ratio(closed["delta_eta_total"])
    g3_m = abs(m_now - mf_closed) / mf_closed
    return {
        "meta": {
            "dest": name, "dist_ly": d_ly, "maneuver": maneuver, "eta": eta,
            "delta_eta_total": closed["delta_eta_total"],
            "x0": X0_MISSION, "lambda_burn": LAMBDA_BURN, "R_ref_m": R_REF_M,
            "u_unit": "R_ref(幾何長)", "assumption": "A4",
            "authority": {"fuel": "[R]", "kinematics": "[R-standard]",
                          "burn_lambda": "[N]@x0=0.3(x<0.1 は天井[R]で許容)"},
            "g3": {"mass_rel": g3_m, "ok": g3_m < G3_TOL},
        },
        "grid": {"u": u_grid, "a": a_arr, "m": m_arr, "x": x_arr,
                 "eta_signed": eta_arr, "L": lum, "thrust_sign": thrust},
    }


# ==================================================== SI レイヤー(1-5)
def si_layer_rows():
    """R = 100 m / 1 km / 10 km の換算列。units.py(C7 認証済み)のみ使用。"""
    rows = []
    for r_m in (100.0, 1000.0, 10000.0):
        for x0 in TIMEOPT_X0:
            m_geo = 0.5 * x0 * r_m
            m_kg = units.mass_geo_to_kg(m_geo)
            lam = frontier.tier_operative(x0, "effective")
            l_geo = 1.5 * x0 * lam                     # L = 3mλ/R = 1.5xλ [R]
            l_si = units.power_geo_to_si(l_geo)
            rows.append({
                "R_m": r_m, "x0": x0,
                "shell_mass_kg": m_kg,
                "shell_mass_Mearth": units.kg_to_mearth(m_kg),
                "shell_mass_Msun": units.kg_to_msun(m_kg),
                "lambda_eff": lam,
                "L_peak_W": l_si,
                "L_peak_Lsun": units.power_si_to_lsun(l_si),
                "burn_u_seconds_per_unit_rapidity":
                    units.time_geo_to_s(r_m / lam),
                "authority": "質量[R]×換算[R] / L: x₀,λ[N]併課[R] / 換算[R]",
            })
    return rows
