"""時間最適(フロンティア騎乗)— v3 Theorem 8(ii)/§12.1、式台帳 L38。

min-time は測地線(単一ブースト)を飽和フロンティアで走行:
    T = R ∫₀^{Δη} dη′ / λ_tier(x(η′)),   x(η′) = x₀ e^(−3η′)
本モジュールは R = 1 正規化(T は R 単位。SI 換算は units.py 経由)。

- 経路 A(閉形式求積): 上式を区間分割 Simpson で評価(長さ縮約恒等式を使用)
- 経路 B(独立 ODE): u を独立変数に (η, x) を連立 RK4(x(η) 閉形式は不使用)。
  T と x_end の両方を照合 → 時間写像と長さ縮約の G3 二経路(認証 P1-C10)
- [N] 実効 tier は x < 0.1 で [R] 天井にフォールバック(PHASE_1.md 1-4)。
  フォールバック点 η_fb = ln(x₀/0.1)/3 を記録し、積分区間を分割する
- 全 tier で主拘束(天井)を併課: λ = tier_operative(frontier.py)
- 天井 tier の T は**到達不能な下限**(開条件)。ラベルは tier を相続
"""
import math

from .frontier import TIER_AUTHORITY, g_lower, tier_bound

G_LOWER_X_MIN = 0.1


def lambda_ride(x: float, tier: str) -> tuple[float, str]:
    """騎乗 λ(運用値)とその区間ラベル。[N] tier は x < 0.1 で天井へフォールバック。"""
    ceil = tier_bound(x, "ceiling")
    if tier == "effective":
        if x < G_LOWER_X_MIN:
            return ceil, "ceiling-fallback[R]"
        return min(g_lower(x), ceil), TIER_AUTHORITY["effective"]
    if tier == "ceiling":
        return ceil, TIER_AUTHORITY["ceiling"]
    if tier == "floor":
        return min(tier_bound(x, "floor"), ceil), TIER_AUTHORITY["floor"]
    raise ValueError(tier)


def fallback_eta(x0: float, tier: str) -> float | None:
    """[N] tier のフォールバック点 η_fb = ln(x₀/0.1)/3(x₀ > 0.1 のとき)。"""
    if tier == "effective" and x0 > G_LOWER_X_MIN:
        return math.log(x0 / G_LOWER_X_MIN) / 3.0
    return None


def _breakpoints(x0: float, deta: float, tier: str) -> list[float]:
    """被積分関数の折れ点で区間分割(Simpson の収束次数を保つ)。

    - effective: フォールバック点+g̲ 数表の節点
    - floor: c 鎖の min/max 枝切替点(branch_signature の変化点を二分法で特定)"""
    pts = {0.0, deta}
    fb = fallback_eta(x0, tier)
    if fb is not None and 0.0 < fb < deta:
        pts.add(fb)
    if tier == "effective":
        for xn in (0.1, 0.2, 0.3, 0.5, 0.7):  # 数表節点(線形補間の折れ)
            if xn < x0:
                e = math.log(x0 / xn) / 3.0
                if 0.0 < e < deta:
                    pts.add(e)
    if tier == "floor":
        from .appc_floor import branch_signature
        n_scan = 1024
        sig_prev = branch_signature(x0)
        for i in range(1, n_scan + 1):
            eta = deta * i / n_scan
            sig = branch_signature(x0 * math.exp(-3.0 * eta))
            if sig != sig_prev:
                lo, hi = deta * (i - 1) / n_scan, eta
                for _ in range(60):
                    mid = 0.5 * (lo + hi)
                    if branch_signature(x0 * math.exp(-3.0 * mid)) == sig_prev:
                        lo = mid
                    else:
                        hi = mid
                pts.add(0.5 * (lo + hi))
                sig_prev = sig
    return sorted(pts)


def _g_lower_edge(xx: float) -> float:
    """区間端の浮動小数点丸め(≤1e-9)のみ吸収する g̲ 評価。

    これは外挿ではない: 区間は構成上 [0.1, 0.7] 内にあり、丸めで境界の
    1 ulp 外に落ちた端点のみクランプする。それ以外は例外を維持(外挿禁止)。"""
    if G_LOWER_X_MIN - 1e-9 <= xx < G_LOWER_X_MIN:
        xx = G_LOWER_X_MIN
    elif 0.7 < xx <= 0.7 + 1e-9:
        xx = 0.7
    return g_lower(xx)


def _segment_lambda_fn(x_mid: float, tier: str):
    """区間の枝を中点で固定した λ(x) 関数(不連続点の混在サンプリング防止)。"""
    if tier == "effective" and x_mid < G_LOWER_X_MIN:
        return (lambda xx: tier_bound(xx, "ceiling")), "ceiling-fallback[R]"
    if tier == "effective":
        return (lambda xx: min(_g_lower_edge(xx), tier_bound(xx, "ceiling"))), \
            TIER_AUTHORITY["effective"]
    if tier == "ceiling":
        return (lambda xx: tier_bound(xx, "ceiling")), TIER_AUTHORITY["ceiling"]
    return (lambda xx: min(tier_bound(xx, "floor"), tier_bound(xx, "ceiling"))), \
        TIER_AUTHORITY["floor"]


def ride_time_quadrature(x0: float, deta: float, tier: str,
                         n_per_seg: int = 4096) -> dict:
    """経路 A: T/R = ∫ dη/λ の区間分割 Simpson(区間ごとに枝固定)。[L38]

    返り値: T(R 単位)、arcs(拘束アーク構造)、fallback_eta。"""
    pts = _breakpoints(x0, deta, tier)
    total = 0.0
    arcs = []
    for k in range(len(pts) - 1):
        e0, e1 = pts[k], pts[k + 1]
        x_mid = x0 * math.exp(-3.0 * 0.5 * (e0 + e1))
        lam_fn, label = _segment_lambda_fn(x_mid, tier)
        # 長スパン区間は分解能を比例強化(1/λ ~ e^{3η} の指数成長に対応)
        n = max(n_per_seg, n_per_seg * int(math.ceil(e1 - e0)))
        n = n if n % 2 == 0 else n + 1
        h = (e1 - e0) / n
        s = 0.0
        for i in range(n + 1):
            eta = e0 + i * h
            w = 1.0 if i in (0, n) else (4.0 if i % 2 else 2.0)
            s += w / lam_fn(x0 * math.exp(-3.0 * eta))
        total += s * h / 3.0
        arcs.append({"eta0": e0, "eta1": e1, "label": label,
                     "lambda0": lam_fn(x0 * math.exp(-3.0 * e0)),
                     "lambda1": lam_fn(x0 * math.exp(-3.0 * e1)),
                     "x0": x0 * math.exp(-3.0 * e0),
                     "x1": x0 * math.exp(-3.0 * e1)})
    return {"T": total, "arcs": arcs, "fallback_eta": fallback_eta(x0, tier),
            "tier": tier, "x0": x0, "deta": deta}


def ride_time_ode(x0: float, deta: float, tier: str, n_steps: int = 50_000) -> dict:
    """経路 B: du を独立変数に (η, x) を RK4 連立(x(η) 閉形式不使用)。[G3]

    停止: η ≥ Δη(3 次エルミート補間で交差時刻)。x_end も返す
    (長さ縮約 x₀e^(−3Δη) との照合は呼び出し側=認証 P1-C10)。
    [N] tier の x = 0.1 フォールバック不連続はイベント検出(ステップ二分)で
    横断する(閉形式の η_fb は不使用 — 独立性を保つ)。"""
    # 粗い T 見積り(ステップ幅選定のみに使用; 値の照合には不使用)
    rough = 0.0
    m_coarse = 64
    for i in range(m_coarse):
        eta = deta * (i + 0.5) / m_coarse
        lam, _ = lambda_ride(x0 * math.exp(-3.0 * eta), tier)
        rough += (deta / m_coarse) / lam
    h_full = 1.25 * rough / n_steps

    def rhs(state):
        eta, x = state
        lam, _ = lambda_ride(x, tier)
        return (lam, -3.0 * x * lam)  # dη/du, dx/du(R = 1)

    def rk4(eta, x, h):
        k1 = rhs((eta, x))
        k2 = rhs((eta + 0.5 * h * k1[0], x + 0.5 * h * k1[1]))
        k3 = rhs((eta + 0.5 * h * k2[0], x + 0.5 * h * k2[1]))
        k4 = rhs((eta + h * k3[0], x + h * k3[1]))
        return (eta + h * (k1[0] + 2 * k2[0] + 2 * k3[0] + k4[0]) / 6.0,
                x + h * (k1[1] + 2 * k2[1] + 2 * k3[1] + k4[1]) / 6.0,
                k1[0])

    def rk4_pre_event(eta, x, h):
        """事前枝([N] g̲)を凍結した RK4。イベント着地ステップ専用。

        着地ステップは構成上、区間全体が事前枝(x ≥ 0.1)なので、
        RK4 段が丸めで x < 0.1 に踏み込んでも枝をクランプ評価する
        (枝混在による O(h) 誤差の除去 — これは真の力学と厳密に一致)。"""
        def rhs_f(state):
            e, xx = state
            xc = xx if xx >= G_LOWER_X_MIN else G_LOWER_X_MIN
            lam = min(_g_lower_edge(xc), tier_bound(xc, "ceiling"))
            return (lam, -3.0 * xx * lam)
        k1 = rhs_f((eta, x))
        k2 = rhs_f((eta + 0.5 * h * k1[0], x + 0.5 * h * k1[1]))
        k3 = rhs_f((eta + 0.5 * h * k2[0], x + 0.5 * h * k2[1]))
        k4 = rhs_f((eta + h * k3[0], x + h * k3[1]))
        return (eta + h * (k1[0] + 2 * k2[0] + 2 * k3[0] + k4[0]) / 6.0,
                x + h * (k1[1] + 2 * k2[1] + 2 * k3[1] + k4[1]) / 6.0,
                k1[0])

    has_event = tier == "effective" and x0 > G_LOWER_X_MIN
    # 適応ステップ: η 進行量をキャップ(床 tier では λ が x とともに桁で
    # 減衰するため、固定 h では 1 ステップ内で λ が数桁変わり不安定になる。
    # キャップは現在の λ のみ使用 — x(η) 閉形式は不使用)
    eta_cap = 1.5 * deta / n_steps
    u, eta, x = 0.0, 0.0, x0
    prev = None
    for _ in range(24 * n_steps):
        lam_now, _ = lambda_ride(x, tier)
        h = min(h_full, eta_cap / lam_now)
        eta_n, x_n, f0 = rk4(eta, x, h)
        if has_event and x > G_LOWER_X_MIN and x_n < G_LOWER_X_MIN:
            # イベント: x = 0.1 横断。事前枝凍結 RK4 でステップ幅を二分し着地
            lo, hi = 0.0, h
            for _ in range(60):
                mid = 0.5 * (lo + hi)
                _, x_try, _ = rk4_pre_event(eta, x, mid)
                if x_try > G_LOWER_X_MIN:
                    lo = mid
                else:
                    hi = mid
            h = 0.5 * (lo + hi)
            eta_n, x_n, f0 = rk4_pre_event(eta, x, h)
            # 着地後、以後の RK4 段が fallback 枝を拾うよう相対 1e-13 内側へ
            x_n = G_LOWER_X_MIN * (1.0 - 1e-13)
        prev = (u, eta, x, f0, h)
        u, eta, x = u + h, eta_n, x_n
        if eta >= deta:
            break
    else:
        raise RuntimeError("ride_time_ode: ステップ上限到達(設計見直し要)")
    # 3 次エルミート補間で η = Δη の交差時刻(最終ステップ幅 h_last を使用)
    u0, e0, x0_, f0, h_last = prev
    f1 = rhs((eta, x))[0]
    a_, b_ = e0, f0 * h_last
    c_ = 3.0 * (eta - e0) - h_last * (2.0 * f0 + f1)
    d_ = -2.0 * (eta - e0) + h_last * (f0 + f1)
    th_lo, th_hi = 0.0, 1.0
    for _ in range(80):
        th = 0.5 * (th_lo + th_hi)
        val = a_ + b_ * th + c_ * th * th + d_ * th**3
        if val < deta:
            th_lo = th
        else:
            th_hi = th
    th = 0.5 * (th_lo + th_hi)
    u_cross = u0 + th * h_last
    # x も同次数で補間
    g0 = rhs((e0, x0_))[1]
    g1 = rhs((eta, x))[1]
    xa, xb = x0_, g0 * h_last
    xc = 3.0 * (x - x0_) - h_last * (2.0 * g0 + g1)
    xd = -2.0 * (x - x0_) + h_last * (g0 + g1)
    x_cross = xa + xb * th + xc * th * th + xd * th**3
    return {"T": u_cross, "x_end": x_cross}


def ride_profile(x0: float, deta: float, tier: str, n: int = 2000) -> dict:
    """騎乗プロファイル(Phase 2 出力用の u 格子つき)。

    η 一様格子、u は累積 Simpson。R = 1、m = xR/2、L = −ṁ = 3mλ = 1.5xλ。
    排気ローブは後方極(推力 +z の逆)。thrust_sign = +1(単一ブースト)。"""
    if n % 2:
        n += 1
    etas = [deta * i / n for i in range(n + 1)]
    lams, labels = [], []
    for e in etas:
        lam, lab = lambda_ride(x0 * math.exp(-3.0 * e), tier)
        lams.append(lam)
        labels.append(lab)
    u = [0.0]
    for i in range(1, n + 1):  # 台形累積(格子出力用; 認証は Simpson/ODE で別途)
        u.append(u[-1] + 0.5 * (etas[i] - etas[i - 1]) * (1.0 / lams[i] + 1.0 / lams[i - 1]))
    xs = [x0 * math.exp(-3.0 * e) for e in etas]
    ms = [0.5 * x for x in xs]
    lum = [1.5 * x * lam for x, lam in zip(xs, lams)]
    return {
        "tier": tier, "authority": TIER_AUTHORITY[tier], "x0": x0, "deta": deta,
        "u": u, "eta": etas, "x": xs, "lambda": lams, "a": lams,  # R=1: a=λ
        "m": ms, "L": lum, "thrust_sign": [1] * (n + 1),
        "segment_labels": labels, "fallback_eta": fallback_eta(x0, tier),
    }
