"""標準相対論運動学(表 B 用)。[R-standard] 式台帳 L39。

β = tanh η、γ = cosh η、βγ = sinh η。
双曲運動(固有加速 a 一定、幾何単位・長さ基底):
  座標時間 t = sinh(η)/a、走行距離 d = (cosh η − 1)/a、固有時間 τ = η/a
巡航: t = D/β、τ = D/(βγ)。
出典: 標準 SR(教科書級。Füzfa 2019 §II の点ロケット運動学と同型)。
論文固有の式ではないため認証は恒等式検証(P1-C9)。
"""
import math

MANEUVER_BURNS = {"flyby": 1, "arrive": 2, "roundtrip": 4}   # バーン回数
MANEUVER_LEGS = {"flyby": 1, "arrive": 1, "roundtrip": 2}    # 片道距離の本数


def beta(eta: float) -> float:
    """到達速度 β = tanh η。[R-standard]"""
    return math.tanh(eta)


def gamma(eta: float) -> float:
    """Lorentz 因子 γ = cosh η。[R-standard]"""
    return math.cosh(eta)


def beta_gamma(eta: float) -> float:
    """βγ = sinh η(固有速度)。[R-standard]"""
    return math.sinh(eta)


def burn_segment(eta: float, a: float) -> dict:
    """双曲運動セグメント(静止→ラピディティ η、固有加速 a)。[R-standard]

    幾何単位(長さ)。t = sinh(η)/a、d = (cosh η − 1)/a、τ = η/a。
    Rindler 恒等式 (d + 1/a)² − t² = 1/a² を満たす(P1-C9 で検証)。"""
    return {
        "coord_time": math.sinh(eta) / a,
        "distance": (math.cosh(eta) - 1.0) / a,
        "proper_time": eta / a,
    }


def mission_times(D: float, eta: float, a: float, maneuver: str) -> dict:
    """ミッション時間(地球座標時間・船内固有時間)。[R-standard] 表 B 用。

    D: 片道距離(幾何単位=長さ)、eta: 巡航ラピディティ、a: バーン固有加速、
    maneuver: "flyby"(加速のみ)/ "arrive"(加速+反転減速)/
    "roundtrip"(往復、各端で静止)。
    バーンは双曲運動、巡航は等速。減速バーンは加速と対称(同じ η, a)。
    排気ローブは推力の逆向き: 加速中=後方、減速中=進行方向(=目的地側)。
    戻り値: total Δη(燃料用)、t_earth、tau_ship、cruise_fraction ほか。
    バーン距離が D を超える場合 feasible=False(本カタログの a では生じない)。"""
    n_burn = MANEUVER_BURNS[maneuver]
    n_leg = MANEUVER_LEGS[maneuver]
    burns_per_leg = n_burn // n_leg
    seg = burn_segment(eta, a)
    cruise_per_leg = D - burns_per_leg * seg["distance"]
    if cruise_per_leg < 0.0:
        return {"feasible": False}
    b, bg = beta(eta), beta_gamma(eta)
    t_earth = n_burn * seg["coord_time"] + n_leg * cruise_per_leg / b
    tau_ship = n_burn * seg["proper_time"] + n_leg * cruise_per_leg / bg
    return {
        "feasible": True,
        "delta_eta_total": n_burn * eta,
        "t_earth": t_earth,
        "tau_ship": tau_ship,
        "cruise_per_leg": cruise_per_leg,
        "burn_coord_time_total": n_burn * seg["coord_time"],
        "burn_proper_time_total": n_burn * seg["proper_time"],
    }


def eta_for_proper_time(D: float, tau_target: float, a: float, maneuver: str,
                        eta_lo: float = 1e-6, eta_hi: float = 30.0,
                        iters: int = 200) -> float:
    """船内固有時間 τ_ship = tau_target を満たす巡航ラピディティ(二分法)。

    τ_ship(η) は本レンジで単調減少(巡航項支配)。[R-standard]"""
    def tau_of(eta):
        r = mission_times(D, eta, a, maneuver)
        return r["tau_ship"] if r["feasible"] else float("inf")
    lo, hi = eta_lo, eta_hi
    for _ in range(iters):
        mid = 0.5 * (lo + hi)
        if tau_of(mid) > tau_target:
            lo = mid
        else:
            hi = mid
    return 0.5 * (lo + hi)
