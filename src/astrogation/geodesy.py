"""H³(速度双曲面)の距離・ラピディティ・双曲弧長(v3 §12.1, App G.1)。

H³ = {v : v·v = −1, v⁰ > 0} ≅ SO⁺(3,1)/SO(3)、誘導計量は曲率 −1。
計量符号 (−,+,+,+)(conventions.md §1)。G3 二経路の経路 A(閉形式)。
"""
import math

def minkowski_dot(v, w) -> float:
    """Minkowski 内積 v·w = −v⁰w⁰ + v⃗·w⃗(符号 (−,+,+,+))。[R] 規約。"""
    return -v[0] * w[0] + v[1] * w[1] + v[2] * w[2] + v[3] * w[3]


def d_H3(v0, v1) -> float:
    """H³ 測地距離。[R] v3 (56):

        d_H³(v₀,v₁) = arccosh(−v₀·v₁)

    v₀, v₁ は単位時間的未来向き四元速度。G3 経路 A(経路 B は ODE 弧長、Phase 1)。"""
    c = -minkowski_dot(v0, v1)
    if c < 1.0:
        c = 1.0  # 丸め保護(単位四元速度なら c ≥ 1)
    return math.acosh(c)


def min_log_fuel(v0, v1) -> float:
    """最小 log 燃料 C_min = 3 d_H³(v₀,v₁)。[R] v3 (56)(Theorem 6)。

    news-silent 級の自由プロファイル最適値。ブースト測地線が唯一の最小化子。"""
    return 3.0 * d_H3(v0, v1)


def min_mass_ratio(v0, v1) -> float:
    """最小放射での質量比 m_f/m₀ = exp(−3 d_H³)。[R] v3 (56)。"""
    return math.exp(-min_log_fuel(v0, v1))


def four_velocity_from_rapidity(eta: float, nx: float = 1.0, ny: float = 0.0,
                                nz: float = 0.0) -> tuple[float, float, float, float]:
    """ラピディティ η・方向 n̂ の単位四元速度 (cosh η, sinh η·n̂)。[R] 運動学。

    直線ブーストでは d_H³ = Δη(v3 (55) 直下: 双曲弧長 = ∫|a|dτ)。"""
    n = math.sqrt(nx * nx + ny * ny + nz * nz)
    sh = math.sinh(eta)
    return (math.cosh(eta), sh * nx / n, sh * ny / n, sh * nz / n)


def hyperbolic_length_of_rapidity_path(abs_a_of_tau, tau0: float, tau1: float,
                                       n: int = 4096) -> float:
    """双曲弧長 L_H³[v] = ∫|a|dτ の単純求積(Simpson)。[R] v3 (55)。

    Phase 1 の G3 経路 B(測地線 ODE 弧長)への接続点。"""
    if n % 2:
        n += 1
    h = (tau1 - tau0) / n
    s = abs_a_of_tau(tau0) + abs_a_of_tau(tau1)
    for k in range(1, n):
        s += (4.0 if k % 2 else 2.0) * abs_a_of_tau(tau0 + k * h)
    return s * h / 3.0
