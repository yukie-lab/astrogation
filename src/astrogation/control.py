"""制御則・Tsiolkovsky 予算・n²(ϑ) 角度分布(v3 §6)。

規約(conventions.md §2): ϑ は各遅延カットの瞬間静止系で固有加速軸から測る。
前方極 ϑ=0 で n² 最小(飽和時ゼロ)、後方極 ϑ=π が排気。
引数 a は固有加速の大きさ |α| ≥ 0、mdot = ṁ ≤ 0(質量減少)。
幾何単位 G = c = 1。
"""
import math

FOUR_PI = 4.0 * math.pi


def n2(theta: float, mdot: float, m: float, a: float) -> float:
    """排気ヌルダスト振幅 n²(ϑ)。[R] v3 (13):

        4π n²(u,ϑ) = −ṁ − 3 m a cosϑ

    厳密(全次数)。摂動近似ではない。"""
    return (-mdot - 3.0 * m * a * math.cos(theta)) / FOUR_PI


def control_law_margin(mdot: float, m: float, a: float) -> float:
    """制御則マージン (−ṁ) − 3m|a|。[R] v3 (14): −ṁ ≥ 3 m |α|。

    ≥ 0 がバルク許容性 n²(ϑ) ≥ 0 ∀ϑ と同値(v3 (13)+(14)、前方極で束縛)。"""
    return -mdot - 3.0 * m * abs(a)


def saturated_mdot(m: float, a: float) -> float:
    """飽和(最小放射)質量損失率 ṁ = −3 m |α|。[R] v3 (14) の等号。"""
    return -3.0 * m * abs(a)


def tsiolkovsky_ratio(abs_alpha_integral: float) -> float:
    """Tsiolkovsky 予算 m(u_f)/m₀。[R] v3 (15):

        m(u_f)/m₀ = exp(−3 ∫ |α(u′)| du′)

    引数は ∫|α|du(直線ブーストではラピディティ利得 Δη)。"""
    return math.exp(-3.0 * abs_alpha_integral)


def moments_closed_form(mdot: float, m: float, a: float) -> tuple[float, float]:
    """モーメント恒等式(閉形式側)。[R] v3 (29)=(59):

        ∮ n² dΩ = −ṁ(光度),  −∮ n² cosϑ dΩ = m a(推力)

    返り値 (luminosity, thrust) = (−ṁ, m a)。認証 C6 はこの閉形式を
    求積(数値積分)と突き合わせる。"""
    return (-mdot, m * a)
