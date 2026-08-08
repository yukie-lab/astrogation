"""静的殻の表面量・DEC マージン・v3 ℓ 閉包の証人(v3 §7, App B/D/E)。

注意: 本モジュールに v2 の分岐スカラーは存在しない([v2-retracted]、
conventions.md §5・L6)。ℓ=1/ℓ=0/ℓ=2 の閉包は v3 のブロック三角構造
((77),(79),(80),(81),(88))で表す。これらが認証 C3a–C3d の対象であり、
Theorem 2/4 の荷重ノードである(L8 依存グラフ)。

有理厳密評価が必要な認証(C2 の厳密ゼロ交差、C3b の判別式恒等)に対応
するため、多項式・有理式は float と fractions.Fraction の両方で動く形で書く。
s := √(1−x)、x := 2m/R ∈ (0,1)。幾何単位 G = c = 1、κ = 8π。
"""
import math

EIGHT_PI = 8.0 * math.pi
FOUR_PI = 4.0 * math.pi
SURFACE_DEC_WINDOW_MAX = 24.0 / 25.0  # [R] v3 (25)


# ---------------------------------------------------------------- アンカー
def sigma0(x: float, R: float = 1.0) -> float:
    """静的殻の表面エネルギー密度 σ₀。[R] v3 (22):

        σ₀ = (1/4πR)(1 − √(1−x))"""
    return (1.0 - math.sqrt(1.0 - x)) / (FOUR_PI * R)


def p0(x: float, R: float = 1.0) -> float:
    """静的殻の表面圧 p₀。[R] v3 (23):

        p₀ = (1/8πR)((1 − x/2)/√(1−x) − 1)"""
    return ((1.0 - 0.5 * x) / math.sqrt(1.0 - x) - 1.0) / (EIGHT_PI * R)


def dec_margin(x: float, R: float = 1.0) -> float:
    """DEC マージン σ₀ − p₀(直接形)。[R] v3 (22)-(24)。"""
    return sigma0(x, R) - p0(x, R)


def dec_margin_factorized_s(s):
    """因数分解形 8πR(σ₀−p₀)·s = −½(5s−1)(s−1)。[R] v3 (24)=(58)。

    s = √(1−x)。Fraction を渡せば有理厳密(C2 の厳密ゼロ交差:s=1/5 で 0)。"""
    half = type(s)(1) / 2 if not isinstance(s, float) else 0.5
    return -half * (5 * s - 1) * (s - 1)


def surface_dec_window(x: float) -> bool:
    """表面 DEC 窓。[R] v3 (25): surface DEC ⟺ x = 2m/R < 24/25。"""
    return 0.0 < x < SURFACE_DEC_WINDOW_MAX


def anchor_margin_M0(x: float) -> float:
    """アンカーマージン M₀ = 8πR(σ₀−p₀) = −(5s−1)(s−1)/(2s)。[R] v3 (61)。"""
    s = math.sqrt(1.0 - x)
    return -(5.0 * s - 1.0) * (s - 1.0) / (2.0 * s)


# ------------------------------------------- ℓ=1 閉包(C3a / C3c の対象)
def cos_row_jump(x: float, rho1: float, At1: float, a: float = 1.0) -> float:
    """cosϑ ジャンプ (1/a)[h_ττ]^cos の完全閉形式。[R] v3 (79):

        (1/a)[h_ττ]^cos = ((ρ₁+2)x + 2 A_t1 (1−x)^{3/2}) / (x−1)

    ρ₁ = ℓ=1 形状振幅(剛体並進ゲージ、v3 Remark 1)、A_t1 = 外部ラプス双極子。"""
    return a * ((rho1 + 2.0) * x + 2.0 * At1 * (1.0 - x) ** 1.5) / (x - 1.0)


def cos_row_partials(x: float) -> tuple[float, float]:
    """cos 行の閉形式係数。[R] v3 (77):

        ∂[h_ττ]^cos/∂ρ₁ = −x/(1−x),  ∂[h_ττ]^cos/∂A_t1 = −2√(1−x)

    両者とも (0,1) で非零 — ℓ=1 閉包(Lemma 4→Thm 2、Lemma 8→Thm 4)の荷重。"""
    return (-x / (1.0 - x), -2.0 * math.sqrt(1.0 - x))


def tilt_row_coefficient() -> float:
    """tilt 行の主係数 ∂[h_τϑ]^sin/∂w₁ = 1。[R] v3 (77) 直上(App D)。"""
    return 1.0


def redshift_jacobian(x: float, R: float = 1.0) -> float:
    """赤方偏移 Jacobian ∂_R[√f] = m/(R²√(1−x)) = x/(2R√(1−x)) ≠ 0。

    [R] v3 (77) の裏書き(App D)。f = 1 − 2m/R、x = 2m/R。"""
    return x / (2.0 * R * math.sqrt(1.0 - x))


def schur_det_J0(x: float) -> float:
    """ℓ≤1 ラプス/tilt Schur 行列式 det J₀ = (−2√(1−x))·1。[R] v3 Lemma 8((77) 系)。

    バーン中の Schur 消去の持続(det J_dyn = det J₀·[1+O(ε)])の静的因子。
    (0,1) で非零 — Thm 4 の荷重(C3c)。"""
    return cos_row_partials(x)[1] * tilt_row_coefficient()


# ------------------------------------------- ℓ=0 閉包(C3b の対象)
def breathing_slope(x):
    """呼吸モード勾配 (1/a²)∂[h_ττ]^{ℓ=0}/∂ρ₀ = −x/s² = −x/(1−x) ≠ 0。

    [R] v3 (80)。ℓ=0 モノポールジャンプの唯一の吸収先(Lemma 4→Thm 2)。
    Fraction 対応。"""
    return -x / (1 - x)


def dipole_only_quadratic_coeffs(x):
    """ρ₀ = ρ₂ = 0 と凍結し (79) の根 A_t1 = −(ρ₁+2)x/(2s³) を消去した後に
    残る 2 次方程式の係数 (A, B, C)。[R] v3 (81) 直前:

        x(4−x)·ρ₁² + 12x²·ρ₁ + 4(2x+1) = 0

    Fraction 対応(C3b の判別式恒等の有理厳密評価に使用)。"""
    return (x * (4 - x), 12 * x * x, 4 * (2 * x + 1))


def dipole_only_discriminant(x):
    """上記 2 次方程式の判別式(閉形式)。[R] v3 (81):

        Δ = 16 x (x−1) (9x² + 11x + 4) < 0 on (0,1)

    負 ⇒ 実双極子だけでは接合を閉じられない(呼吸モードの必要性)。
    Fraction 対応。"""
    return 16 * x * (x - 1) * (9 * x * x + 11 * x + 4)


# ------------------------------------------- ℓ=2 閉包(C3d の対象)
def l2_minor(x: float) -> tuple[tuple[float, float], tuple[float, float]]:
    """ℓ=2 エネルギー/ラプス minor ∂_{(ρ₂,A_t2)}([h_uu],[h_ττ])_{ℓ=2}。[R] v3 (88):

        [[−x, 0], [−x/s², −2s]]

    (列順 (ρ₂, A_t2)、s = √(1−x))。O(a²) ℓ=2 障害の消去(App E→Thm 4)。"""
    s = math.sqrt(1.0 - x)
    return ((-x, 0.0), (-x / (s * s), -2.0 * s))


def l2_minor_det(x: float) -> float:
    """ℓ=2 minor の行列式(閉形式)。[R] v3 (88): det = 2x√(1−x) ≠ 0 on (0,1)。"""
    return 2.0 * x * math.sqrt(1.0 - x)
