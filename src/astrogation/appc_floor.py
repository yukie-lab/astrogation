"""厳密下界 c(x) の定数鎖(v3 App C, (47)-(49)+(68)-(73))。式台帳 L24/L41。

印字された閉形式((48),(68),(71),(72)、r_⋆ 方程式、S_λ、κ、ϱ_Q)は忠実に実装。
NL_A / NL_B / B⋆_m は論文が手続き的にのみ記述する量(閉形式非掲載)で、
実装解釈は **ASSUMPTIONS A3** に記録(polydisc 座標 (δR, δλ=aR₀)、
distinguished boundary 上の上限、後方極軸縮約)。
polydisc 座標の検証: |L| ≥ ½(1−x) 保持条件から r_⋆ 方程式
xϱ/(1−ϱ) + 2ϱ(1+ϱ) = ½(1−x) が厳密に再導出されることを確認済み(L41)。

回帰対象: v3 (73) c(x) ≈ {8.5, 14, 17, 14, 2.0}×10⁻⁵ at x = {0.1,0.2,0.3,0.5,0.7}。
一致しない場合は STOP 報告(CLAUDE.md §8-1。定数調整による「修正」は禁止)。
規約: R₀ = 1、m = x/2 固定、後方極(束縛方向)。
"""
import cmath
import math

from .shell import anchor_margin_M0

_TWO_PI = 2.0 * math.pi


def lambda_h(x: float) -> float:
    """sub-horizon 帯 Λ_h = ¼(1−x)。[R] v3 Lemma 6。"""
    return 0.25 * (1.0 - x)


def gamma_inverse_bound(x: float) -> float:
    """ブロック対角逆写像限界 Γ(x) = max{1/x, 1/(2s³) + 1/(2s)}。[R] v3 (68)=(49)。"""
    s = math.sqrt(1.0 - x)
    return max(1.0 / x, 1.0 / (2.0 * s**3) + 1.0 / (2.0 * s))


def r_star(x: float) -> float:
    """解析半径 r_⋆(x): xϱ/(1−ϱ) + 2ϱ(1+ϱ) = ½(1−x) の (0,1) 唯一根。[R] v3 App C。

    LHS は (0,1) で狭義単調増加なので二分法で一意に決まる。"""
    target = 0.5 * (1.0 - x)

    def lhs(rho):
        return x * rho / (1.0 - rho) + 2.0 * rho * (1.0 + rho)

    lo, hi = 0.0, 1.0 - 1e-12
    for _ in range(200):
        mid = 0.5 * (lo + hi)
        if lhs(mid) < target:
            lo = mid
        else:
            hi = mid
    return 0.5 * (lo + hi)


def s_lambda(x: float) -> float:
    """ラプス行のアンカー λ-勾配 S_λ = 2x/s²。[R] v3 App C。"""
    return 2.0 * x / (1.0 - x)


def kappa(x: float) -> float:
    """κ = 1 + 2ΓS_λ。[R] v3 App C。"""
    return 1.0 + 2.0 * gamma_inverse_bound(x) * s_lambda(x)


def rho_q(x: float, lam: float) -> float:
    """Newton–Kantorovich 球半径 ϱ_Q(λ) = 2ΓS_λ·λ。[R] v3 App C。"""
    return 2.0 * gamma_inverse_bound(x) * s_lambda(x) * lam


# ------------------------------------------------------------------
# polydisc 上限(A3 解釈部)。座標: R = 1+δR、λ_e = δλ(1+δR)、
# f(R) = 1 − x/R、L = f − 2λ_e、N = 1 − λ_e。distinguished boundary
# δR = ϱe^{iθ₁}, δλ = ϱe^{iθ₂} 上でグリッド最大化(上限はモジュラス最大原理
# により境界で達成; グリッドは下からの近似なので僅かに非保守 → 収束テストで管理)。
# ------------------------------------------------------------------
_N_GRID = 96


def _boundary_sup(x: float, fn, n_grid: int = _N_GRID) -> float:
    rho = r_star(x)
    best = 0.0
    for i in range(n_grid):
        dr = rho * cmath.exp(2j * math.pi * i / n_grid)
        for j in range(n_grid):
            dl = rho * cmath.exp(2j * math.pi * j / n_grid)
            v = abs(fn(x, dr, dl))
            if v > best:
                best = v
    return best


def _nl_a_integrand(x: float, dr: complex, dl: complex) -> complex:
    """seed 正規化ラプス行(A3 読み): F_A = −L/f(R) + N²(アンカーで 0)。"""
    R = 1.0 + dr
    f = 1.0 - x / R
    lam_e = dl * R
    L = f - 2.0 * lam_e
    N = 1.0 - lam_e
    return -L / f + N * N


def nl_a(x: float, n_grid: int = _N_GRID) -> float:
    """NL_A: seed 正規化ラプス行の polydisc 上限。[A3 解釈] v3 (69) 記述部。"""
    return _boundary_sup(x, _nl_a_integrand, n_grid)


def nl_b(x: float) -> float:
    """NL_B: shape 行 2 次項 R′²(1/L−1) − Lw² + Y² の一様上限。[A3 解釈] v3 (69)-(70)。

    |Y|,|R′| ≤ ϱR₀、|w| ≤ ϱ、|1/L−1| ≤ 2/(1−x)+1、|L| ≤ (3/2)(1−x)(polydisc 上)。"""
    rho = r_star(x)
    inv_l_minus_1 = 2.0 / (1.0 - x) + 1.0
    l_max = 1.5 * (1.0 - x)
    return rho * rho * (inv_l_minus_1 + l_max + 1.0)


def _margin_integrand(x: float, dr: complex, dl: complex) -> complex:
    """後方極 frozen マージン 8πR(σ−p) = (42)/s₊ の polydisc 値(A3 読み)。"""
    R = 1.0 + dr
    x_p = x / R
    lam = dl * R
    s_plus = cmath.sqrt(1.0 - x_p - 2.0 * lam)
    val42 = 3.0 * s_plus - 3.0 + 2.5 * x_p + 7.0 * lam - s_plus * lam / (1.0 - lam)
    return val42 / s_plus


def b_star_m(x: float, n_grid: int = _N_GRID) -> float:
    """B⋆_m: polydisc 上のマージン上限。[A3 解釈] v3 (72) 記述部。"""
    return _boundary_sup(x, _margin_integrand, n_grid)


# ------------------------------------------------------------------
def m2(x: float) -> float:
    """二次変分 majorant M₂ = 2max{NL_A, NL_B}/r_⋆²。[R 構造/(A3 上限)] v3 (69)。"""
    return 2.0 * max(nl_a(x), nl_b(x)) / r_star(x) ** 2


def delta_q(x: float) -> float:
    """定量的陰関数半径 δ_Q。[R] v3 (71):

    δ_Q = min{¼(1−x), 1/(2ΓM₂κ), 2S_λ/(M₂κ²), r_⋆/κ}"""
    g = gamma_inverse_bound(x)
    m2x = m2(x)
    k = kappa(x)
    return min(
        0.25 * (1.0 - x),
        1.0 / (2.0 * g * m2x * k),
        2.0 * s_lambda(x) / (m2x * k * k),
        r_star(x) / k,
    )


def a_const(x: float) -> float:
    """線形退縮係数 A(x) = 2B⋆_m·max{ϱ_⋆, δ_Q}/(r_⋆δ_Q)。[R 構造/(A3 上限)] v3 (72)。"""
    dq = delta_q(x)
    rho_st = rho_q(x, dq)
    return 2.0 * b_star_m(x) * max(rho_st, dq) / (r_star(x) * dq)


def c_shape(x: float) -> float:
    """形状応答退縮係数 C_shape = 4A/δ_Q。[R 構造/(A3 上限)] v3 (72)。"""
    return 4.0 * a_const(x) / delta_q(x)


def c_floor_grid_principal(x: float) -> float:
    """c(x) 主読み版(grid 上限)。**診断専用**。[A3 主読み] v3 (48)。

    注意: grid 上限は真の上限の過小評価になり得るため、床としての厳密性を
    保証しない。運用は c_floor_conservative を使う。"""
    m0 = anchor_margin_M0(x)
    a = a_const(x)
    cs = c_shape(x)
    quad_root = m0 / a if cs == 0.0 else (math.sqrt(a * a + 4.0 * cs * m0) - a) / (2.0 * cs)
    return min(lambda_h(x), 0.5 * delta_q(x), quad_root)


# ------------------------------------------------------------------
# 保守化版(修正試行 2、2026-08-08): 上限を三角不等式による解析的
# **過大評価**に置換。過大評価 → M₂,A,C_shape 過大 → δ_Q,c 過小 → 床として安全。
# A3 解釈の下で c_cons(x) ≤ c_true(A3)。5 点すべてで論文 (73) 値より下
# (比 0.2–0.73)、束縛枝は x ≲ 0.7 で 2 次根(論文記述と一致)。
# 表示桁一致は 2 回の試行で未達 → STOP 報告(docs/reports/P1_STOP_c_chain.md)。
# ------------------------------------------------------------------
def nl_a_conservative(x: float) -> float:
    """NL_A の解析的過大評価: |−L/f+N²| ≤ 2λ_e/|f|_min + 2λ_e + λ_e²。[A3+保守]"""
    rho = r_star(x)
    lam_e = rho * (1.0 + rho)
    f_min = 0.5 * (1.0 - x) + 2.0 * rho * (1.0 + rho)  # r_⋆ 方程式より
    return 2.0 * lam_e / f_min + 2.0 * lam_e + lam_e * lam_e


def b_star_m_conservative(x: float) -> float:
    """B⋆_m の解析的過大評価((42)/s₊ の三角不等式)。[A3+保守]"""
    rho = r_star(x)
    lam_e = rho * (1.0 + rho)
    s_min = math.sqrt(0.5 * (1.0 - x))
    s_max = math.sqrt(1.5 * (1.0 - x))
    x_p_max = x / (1.0 - rho)
    t42 = (3.0 * s_max + 3.0 + 2.5 * x_p_max + 7.0 * lam_e
           + s_max * lam_e / (1.0 - lam_e))
    return t42 / s_min


def m2_conservative(x: float) -> float:
    return 2.0 * max(nl_a_conservative(x), nl_b(x)) / r_star(x) ** 2


def delta_q_conservative(x: float) -> float:
    g = gamma_inverse_bound(x)
    m2x = m2_conservative(x)
    k = kappa(x)
    return min(0.25 * (1.0 - x), 1.0 / (2.0 * g * m2x * k),
               2.0 * s_lambda(x) / (m2x * k * k), r_star(x) / k)


def c_floor_conservative(x: float) -> float:
    """保守化 c(x)(運用床)。[R(A3)/STOP-pending] v3 (48) 構造+保守的上限。

    A3 解釈の下で厳密な下界。(73) との表示桁一致は未達(STOP 報告中)であり、
    人間の裁定まで **[R(A3)/STOP-pending]** ラベルで運用する。"""
    dq = delta_q_conservative(x)
    rho_st = rho_q(x, dq)
    a = 2.0 * b_star_m_conservative(x) * max(rho_st, dq) / (r_star(x) * dq)
    cs = 4.0 * a / dq
    m0 = anchor_margin_M0(x)
    quad_root = (math.sqrt(a * a + 4.0 * cs * m0) - a) / (2.0 * cs)
    return min(lambda_h(x), 0.5 * dq, quad_root)


# 運用エイリアス(frontier.tier_bound が参照)
c_floor = c_floor_conservative


def branch_signature(x: float) -> tuple[int, int, int]:
    """保守化 c 鎖の束縛枝の署名(M₂の max 枝, δ_Q の argmin, c の argmin)。

    求積(timeopt)の区間分割用: 署名が変わる点は被積分関数 1/c(x(η)) の
    キンクなので、Simpson の収束次数を保つため分割点にする。"""
    s = math.sqrt(1.0 - x)
    i_gamma = 0 if 1.0 / x >= 1.0 / (2.0 * s**3) + 1.0 / (2.0 * s) else 1
    i_m2 = 0 if nl_a_conservative(x) >= nl_b(x) else 1
    g = gamma_inverse_bound(x)
    m2x = m2_conservative(x)
    k = kappa(x)
    dq_cands = (0.25 * (1.0 - x), 1.0 / (2.0 * g * m2x * k),
                2.0 * s_lambda(x) / (m2x * k * k), r_star(x) / k)
    i_dq = min(range(4), key=lambda i: dq_cands[i])
    dq = dq_cands[i_dq]
    rho_st = rho_q(x, dq)
    a = 2.0 * b_star_m_conservative(x) * max(rho_st, dq) / (r_star(x) * dq)
    cs = 4.0 * a / dq
    m0 = anchor_margin_M0(x)
    quad_root = (math.sqrt(a * a + 4.0 * cs * m0) - a) / (2.0 * cs)
    c_cands = (lambda_h(x), 0.5 * dq, quad_root)
    i_c = min(range(3), key=lambda i: c_cands[i])
    i_rho = 0 if rho_st >= dq else 1  # max{ϱ_⋆, δ_Q} の枝
    return (i_gamma, i_m2, i_dq, i_c, i_rho)


def chain_report(x: float) -> dict:
    """定数鎖の全中間量(回帰・STOP 切り分け用)。"""
    return {
        "x": x,
        "M0": anchor_margin_M0(x),
        "Lambda_h": lambda_h(x),
        "Gamma": gamma_inverse_bound(x),
        "r_star": r_star(x),
        "S_lambda": s_lambda(x),
        "kappa": kappa(x),
        "NL_A": nl_a(x),
        "NL_B": nl_b(x),
        "B_star_m": b_star_m(x),
        "M2": m2(x),
        "delta_Q": delta_q(x),
        "A": a_const(x),
        "C_shape": c_shape(x),
        "c": c_floor(x),
    }
