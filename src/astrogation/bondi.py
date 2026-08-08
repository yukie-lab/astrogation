"""Bondi 予算(閉形式)+ warpax クロスチェック接続(v3 §6.1, App G)。

G3 二経路(conventions.md / ASSUMPTIONS A1-5):
- 経路 A(本モジュール): 閉形式 v3 (12)+(29)
- 経路 B: warpax.bondi(arXiv:2602.18023 の観測者ロバスト枠組み)
Phase 0 では経路 B は「接続確認」のみ(C8)。本格突合は Phase 1。
"""
import math


def budget_rate(mdot: float, m: float, a: float) -> tuple[float, float]:
    """Bondi 四元運動量の変化率(瞬間静止系、加速軸 = z)。[R] v3 (12)+(29):

        dP⁰_B/du = ṁ(≤ 0),   dP^z_B/du = m a(推力、前方向き)

    P^μ_B = m(u) v^μ(u)(Bonnor 値、v3 Cor. 5 — 好カットで超並進非依存)。
    返り値 (dP0_du, dPz_du) = (mdot, m·a)。"""
    return (mdot, m * a)


def universal_rocket_bound_ok(mdot: float, m: float, a: float) -> bool:
    """普遍ロケット限界(静止系形)。[R] v3 (2): −ṁ_B ≥ |P⃗̇_B| = m|a|。

    制御則 (14) はこの床の 3 倍(news-silent 双極子のコリメーション罰、v3 (95))。"""
    return -mdot >= m * abs(a)


# ------------------------------------------------- warpax 接続(C8 用)
def warpax_available() -> bool:
    """warpax(経路 B)が import 可能か。"""
    try:
        import warpax  # noqa: F401
        return True
    except Exception:
        return False


def warpax_bondi_module():
    """warpax.bondi モジュールを返す(C8 接続確認用)。

    期待 API(2026-08-08 確認、warpax 1.3.0): extract, radiated_momentum_flux,
    weyl_scalars, peeling ほか。本格運用(数値突合)は Phase 1。"""
    import warpax.bondi
    return warpax.bondi


def warpax_version() -> str:
    import warpax
    return warpax.__version__
