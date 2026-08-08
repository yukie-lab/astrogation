"""放射計モジュール(Phase 2 タスク 2-1)。式台帳 L43–L48。

静止系パターン v3 (13) を観測者系(光行差・Doppler・遅延時間)へ写す。
入力は Phase 1 プロファイルの配列のみ(再計算禁止 — PHASE_2.md 前提)。
幾何単位・R = 1 正規化(プロファイルと同一)。θ_obs は飛行軸 +ẑ から測る
(目的地 = 0、出発地 = π)。β は符号つき(eta_signed から tanh)。

導出の要点(L44): F = δ⁴ n²/D² の δ⁴ は
  dE/dE′ = δ(光子エネルギー)× du/dt_obs = δ(到着時間圧縮)
  × dΩ′/dΩ = δ²(立体角の光行差)
の積。実験系時間あたりのレートは δ³ n²/γ(C16 が共変性で錨止め)。
"""
import math

FOUR_PI = 4.0 * math.pi


# ---------------------------------------------------------------- 基本変換
# 数値安定性(2-1 設計): β 基底の 1 − βμ は高 η で桁落ちする(η=12 で
# 相対 ~1e-6、δ⁴ が増幅)。恒等式
#   γ(1 − βμ) = cosh η − μ sinh η = ½[(1−μ)e^η + (1+μ)e^(−η)]
# (正項の和)により、全 η・全 μ で桁落ちなしに評価する(ラピディティ基底)。


# 半角符号化(v = sin²(θ/2) = (1−μ)/2 ∈ [0,1]): μ ≈ ±1 の float から
# 1∓μ を再構成する API 境界の桁落ちを根絶する。v では
#   1/δ = v e^η + (1−v) e^(−η),   v′ = v e^η / (v e^η + (1−v) e^(−η)),
#   dv_lab/dv′ = 1/den²(逆写像)
# がすべて正項のみで閉じる。カタログ角 {0°, 90°, 180°} は v ∈ {0, ½, 1} で厳密。


def inv_doppler_v(v: float, eta: float) -> float:
    """1/δ = γ(1 − βμ) の半角安定形 v e^η + (1−v) e^(−η)。[R-standard] L44。"""
    return v * math.exp(eta) + (1.0 - v) * math.exp(-eta)


def aberrate_v(v: float, eta: float) -> float:
    """光行差の半角安定形(実験系 → 静止系): v′ = v e^η / (v e^η + (1−v)e^(−η))。
    [R-standard] L43。逆写像は η → −η。dv_out/dv_in = 1/den²(C16 の Jacobian)。"""
    num = v * math.exp(eta)
    return num / (num + (1.0 - v) * math.exp(-eta))


def inv_doppler_eta(cos_theta_lab: float, eta: float) -> float:
    """1/δ = γ(1 − β cos θ) の安定形 ½[(1−μ)e^η + (1+μ)e^(−η)]。[R-standard] L44。

    注意: μ ≈ ±1 を float の μ から渡すと 1∓μ の再構成で桁落ちする。
    最ビーム配置では半角符号化 inv_doppler_v を使うこと。"""
    return 0.5 * ((1.0 - cos_theta_lab) * math.exp(eta)
                  + (1.0 + cos_theta_lab) * math.exp(-eta))


def aberrate_cos_eta(cos_theta_lab: float, eta: float) -> float:
    """光行差の安定形。[R-standard] L43:

        cos θ′_z = (μ cosh η − sinh η)/(cosh η − μ sinh η)
                 = [(μ−1)e^η + (μ+1)e^(−η)] / [(1−μ)e^η + (1+μ)e^(−η)]"""
    ep, em = math.exp(eta), math.exp(-eta)
    mu = cos_theta_lab
    return ((mu - 1.0) * ep + (mu + 1.0) * em) / ((1.0 - mu) * ep + (1.0 + mu) * em)


def aberrate_cos(cos_theta_lab: float, beta: float) -> float:
    """光行差(β 基底の参照実装 — 高 η では aberrate_cos_eta を使う)。[R-standard] L43。"""
    return (cos_theta_lab - beta) / (1.0 - beta * cos_theta_lab)


def doppler(cos_theta_lab: float, beta: float) -> float:
    """Doppler 因子(β 基底の参照実装 — 高 η では 1/inv_doppler_eta)。[R-standard] L44。"""
    gamma = 1.0 / math.sqrt(1.0 - beta * beta)
    return 1.0 / (gamma * (1.0 - beta * cos_theta_lab))


def pattern_numerator(L, m, a, cos_theta_pattern):
    """パターンの分子 L − 3 m a cos ϑ′(型を保存 — Fraction なら厳密)。[R] L48。

    C17(前方厳密ゼロ)は本関数を Fraction で評価する(4π を掛けない)。"""
    return L - 3 * m * a * cos_theta_pattern


def pattern_n2(L: float, m: float, a: float, cos_theta_pattern: float) -> float:
    """静止系パターン n²(ϑ′)。[R] v3 (13)/L48:

        n² = [L − 3 m a cos ϑ′]/4π   (L = −ṁ、a = |α| ≥ 0)

    飽和 L = 3ma で前方(cosϑ′ = 1)厳密ゼロ。巡航(L = a = 0)で恒等ゼロ。"""
    return pattern_numerator(L, m, a, cos_theta_pattern) / FOUR_PI


def observed_flux_v(L: float, m: float, a: float, thrust_sign: int,
                    eta_signed: float, v_obs: float, D: float = 1.0) -> float:
    """観測者系ボロメトリックフラックス(半角符号化、桁落ちフリー)。[R-standard+R] L44:

        F = δ⁴ · n²(ϑ′) / D²,  v_obs = sin²(θ_obs/2)(目的地 0 / 側方 ½ / 出発地 1)

    cos ϑ′ = s·(1 − 2v′)、v′ = aberrate_v(v_obs, η)。巡航(L = a = 0)は恒等ゼロ。"""
    v_p = aberrate_v(v_obs, eta_signed)
    cz = 1.0 - 2.0 * v_p
    cos_pat = thrust_sign * cz if thrust_sign != 0 else cz
    n2 = pattern_n2(L, m, a, cos_pat)
    inv_d = inv_doppler_v(v_obs, eta_signed)
    return n2 / (inv_d**4 * D * D)


def observed_flux_density(L: float, m: float, a: float, thrust_sign: int,
                          eta_signed: float, cos_theta_obs: float,
                          D: float = 1.0) -> float:
    """観測者系フラックス(μ 互換ラッパ)。最ビーム配置は observed_flux_v を推奨。"""
    return observed_flux_v(L, m, a, thrust_sign, eta_signed,
                           0.5 * (1.0 - cos_theta_obs), D)


# ------------------------------------------------ 観測者系モーメント(C16)
def lab_moments_closed_form(L: float, m: float, a: float, thrust_sign: int,
                            eta_signed: float) -> tuple[float, float]:
    """実験系の放射エネルギー/z-運動量レート(閉形式)。[R] L46:

        dE/dt_lab = Q⁰ + β Q^z,   dP^z/dt_lab = Q^z + β Q⁰
        Q^μ = (L, −s·m a)(瞬間静止系、v3 (12),(29) の成分)"""
    beta = math.tanh(eta_signed)
    q0 = L
    qz = -thrust_sign * m * a
    return (q0 + beta * qz, qz + beta * q0)


def lab_rate_density_v(L: float, m: float, a: float, thrust_sign: int,
                       eta_signed: float, v_obs: float) -> float:
    """実験系時間あたり角度密度 dE/dt_lab dΩ = δ³ n²/γ(半角符号化)。[R-standard] L44。"""
    v_p = aberrate_v(v_obs, eta_signed)
    cz = 1.0 - 2.0 * v_p
    cos_pat = thrust_sign * cz if thrust_sign != 0 else cz
    n2 = pattern_n2(L, m, a, cos_pat)
    inv_d = inv_doppler_v(v_obs, eta_signed)
    return n2 / (inv_d**3 * math.cosh(eta_signed))


def lab_rate_density(L: float, m: float, a: float, thrust_sign: int,
                     eta_signed: float, cos_theta_obs: float) -> float:
    """実験系時間あたり角度密度(μ 互換ラッパ)。"""
    return lab_rate_density_v(L, m, a, thrust_sign, eta_signed,
                              0.5 * (1.0 - cos_theta_obs))


# ------------------------------------------------ 遅延時間写像(L45、G3 二系統)

def _dtobs_integrand(eta: float, cos_theta_obs: float) -> float:
    """dt_obs/du = cosh η − μ sinh η の安定形 ½[(1−μ)e^η + (1+μ)e^(−η)]。[L45]"""
    return 0.5 * ((1.0 - cos_theta_obs) * math.exp(eta)
                  + (1.0 + cos_theta_obs) * math.exp(-eta))


def _dtobs_antiderivative(eta: float, cos_theta_obs: float) -> float:
    """∫(cosh η − μ sinh η)dη = sinh η − μ cosh η の安定形
    ½[(1−μ)e^η − (1+μ)e^(−η)]。[L45/L39](定 a バーンの閉形式用)"""
    return 0.5 * ((1.0 - cos_theta_obs) * math.exp(eta)
                  - (1.0 + cos_theta_obs) * math.exp(-eta))

def _hermite_gauss_cumulative(xs, fs, dfs, integrand, n_gauss: int = 8):
    """節点値 fs と厳密節点微分 dfs を持つ量 f(x) の 3 次 Hermite 補間の下で
    ∫ integrand(f(x)) dx を区間ごとに Gauss–Legendre で累積する。"""
    import numpy as np
    nodes, weights = np.polynomial.legendre.leggauss(n_gauss)
    out = [0.0]
    total = 0.0
    for i in range(len(xs) - 1):
        h = xs[i + 1] - xs[i]
        if h == 0.0:
            out.append(total)
            continue
        f0, f1, d0, d1 = fs[i], fs[i + 1], dfs[i], dfs[i + 1]
        acc = 0.0
        for t_, w_ in zip(nodes, weights):
            t = 0.5 * (t_ + 1.0)
            h00 = 2 * t**3 - 3 * t**2 + 1
            h10 = t**3 - 2 * t**2 + t
            h01 = -2 * t**3 + 3 * t**2
            h11 = t**3 - t**2
            f_val = h00 * f0 + h10 * h * d0 + h01 * f1 + h11 * h * d1
            acc += w_ * integrand(f_val)
        total += acc * 0.5 * h
        out.append(total)
    return out


def t_obs_path_u(u, eta_signed, deta_du, cos_theta_obs: float):
    """経路 A: u-径数。η(u) を Hermite(dη/du = 節点厳密収録値)で補間し
    dt_obs/du = cosh η − sinh η cos θ を Gauss 累積。[L45]"""
    return _hermite_gauss_cumulative(
        u, eta_signed, deta_du,
        lambda e: _dtobs_integrand(e, cos_theta_obs))


def t_obs_path_eta(u, eta_signed, deta_du, cos_theta_obs: float):
    """経路 B: η-径数。u(η) を Hermite(du/dη = 1/λ = 節点厳密)で補間し
    dt_obs/dη = [cosh η − sinh η cos θ]·(du/dη) を Gauss 累積。
    η が一定の区間(巡航)は dt_obs = (coshη − sinhη cosθ)·Δu を厳密加算。[L45]"""
    out = [0.0]
    total = 0.0
    import numpy as np
    nodes, weights = np.polynomial.legendre.leggauss(8)
    for i in range(len(u) - 1):
        e0, e1 = eta_signed[i], eta_signed[i + 1]
        du_ = u[i + 1] - u[i]
        if du_ == 0.0:
            out.append(total)
            continue
        if e1 == e0:  # 巡航/一定 η: 厳密
            total += _dtobs_integrand(e0, cos_theta_obs) * du_
            out.append(total)
            continue
        h = e1 - e0
        g0 = 1.0 / deta_du[i] if deta_du[i] != 0 else 0.0   # du/dη
        g1 = 1.0 / deta_du[i + 1] if deta_du[i + 1] != 0 else 0.0
        u0, u1 = u[i], u[i + 1]
        acc = 0.0
        for t_, w_ in zip(nodes, weights):
            t = 0.5 * (t_ + 1.0)
            # u(η) の 3 次 Hermite の微分 du/dη(節点微分 du/dη = 1/λ は厳密)
            dh00 = 6 * t**2 - 6 * t
            dh10 = 3 * t**2 - 4 * t + 1
            dh01 = -6 * t**2 + 6 * t
            dh11 = 3 * t**2 - 2 * t
            du_deta = (dh00 * u0 + dh10 * h * g0 + dh01 * u1 + dh11 * h * g1) / h
            e_val = e0 + t * h
            acc += w_ * _dtobs_integrand(e_val, cos_theta_obs) * du_deta
        total += acc * 0.5 * h
        out.append(total)
    return out


def t_obs_mission_closed(u, eta_signed, a_arr, thrust, cos_theta_obs: float):
    """ミッション型の区分閉形式(独立経路 A′): 定 a バーンは双曲運動の原始関数
        Δt_lab = (sinh η₁ − sinh η₀)/a,  Δz = (cosh η₁ − cosh η₀)/a
    (η は符号つきで単調区分)、巡航は線形。[L45/L39]"""
    out = [0.0]
    total = 0.0
    for i in range(len(u) - 1):
        du_ = u[i + 1] - u[i]
        if du_ == 0.0:
            out.append(total)
            continue
        e0, e1 = eta_signed[i], eta_signed[i + 1]
        if e1 == e0:
            total += _dtobs_integrand(e0, cos_theta_obs) * du_
        else:
            rate = (e1 - e0) / du_  # 符号つき dη/du(定 a バーンで一定)
            total += (_dtobs_antiderivative(e1, cos_theta_obs)
                      - _dtobs_antiderivative(e0, cos_theta_obs)) / rate
        out.append(total)
    return out


# ------------------------------------------------ エネルギー閉合(C15、L47)
def fluence_exact(u, L, m, a_arr) -> float:
    """∫L du の再計算禁止下の厳密求積。[R] L47:

    定 λ 区間は区間指数厳密則 ∫L du = m_i − m_{i+1}(望遠鏡和)、
    L = 0 区間は 0。m 配列との整合は節点恒等 L_i = 3 m_i a_i で別途検証。"""
    total = 0.0
    for i in range(len(u) - 1):
        if L[i] == 0.0 and L[i + 1] == 0.0:
            continue
        total += m[i] - m[i + 1]
    return total
