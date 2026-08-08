"""単位換算の一元管理モジュール(conventions.md §1)。

幾何単位系 G = c = 1(基底 = 長さ[m])↔ SI ↔ 天文単位(ly, yr, M☉)。
本モジュールは定義値・公認値のみを含み、物理式は含まない。
他モジュールでの換算定数の直書きは規約違反(conventions.md §1)。

定数の出典:
- C_SI: SI 定義値(厳密)
- G_SI: CODATA 2018
- GM_SUN_SI: IAU 2015 nominal solar mass parameter(定義的公認値)
- YEAR_SI: Julian year = 365.25 d(厳密)/ LY_SI = c·yr(厳密)
"""

C_SI = 299_792_458.0                # m/s(厳密)
G_SI = 6.674_30e-11                 # m^3 kg^-1 s^-2(CODATA 2018)
GM_SUN_SI = 1.327_124_400_18e20     # m^3 s^-2(IAU 2015 nominal)
YEAR_SI = 31_557_600.0              # s(厳密: 365.25 * 86400)
LY_SI = C_SI * YEAR_SI              # m(厳密: 9_460_730_472_580_800)

M_SUN_KG = GM_SUN_SI / G_SI         # kg(G の不確かさを相続)
M_SUN_GEO_M = GM_SUN_SI / C_SI**2   # m(幾何長。厳密系では ≈ 1476.6250 m)


# --- 質量: SI kg ↔ 幾何長 m ---
def mass_kg_to_geo(m_kg: float) -> float:
    """m_geo[m] = G m/c²。"""
    return G_SI * m_kg / C_SI**2


def mass_geo_to_kg(m_geo: float) -> float:
    return m_geo * C_SI**2 / G_SI


# --- 時間: SI s ↔ 幾何長 m ---
def time_s_to_geo(t_s: float) -> float:
    """t_geo[m] = c t。"""
    return C_SI * t_s


def time_geo_to_s(t_geo: float) -> float:
    return t_geo / C_SI


# --- 長さ: m ↔ ly / 時間: s ↔ yr ---
def m_to_ly(x_m: float) -> float:
    return x_m / LY_SI


def ly_to_m(x_ly: float) -> float:
    return x_ly * LY_SI


def s_to_yr(t_s: float) -> float:
    return t_s / YEAR_SI


def yr_to_s(t_yr: float) -> float:
    return t_yr * YEAR_SI


# --- 太陽質量 ---
def msun_to_geo(n_msun: float) -> float:
    """M☉ 個数 → 幾何長[m]。"""
    return n_msun * M_SUN_GEO_M


def geo_to_msun(m_geo: float) -> float:
    return m_geo / M_SUN_GEO_M


# --- 電力・光度(Phase 1 追加。SI 正直レイヤー用)---
PLANCK_POWER_SI = C_SI**5 / G_SI     # W — 幾何単位の無次元パワー → SI(c⁵/G)
L_SUN_SI = 3.828e26                  # W(IAU 2015 nominal solar luminosity)
GM_EARTH_SI = 3.986_004_418e14       # m³ s⁻²(IAU nominal geocentric grav. param.)
M_EARTH_KG = GM_EARTH_SI / G_SI      # kg(G の不確かさを相続)


def power_geo_to_si(p_geo: float) -> float:
    """幾何単位の無次元パワー(dm/du、長さ/長さ)→ W。P_SI = p·c⁵/G。"""
    return p_geo * PLANCK_POWER_SI


def power_si_to_geo(p_si: float) -> float:
    return p_si / PLANCK_POWER_SI


def power_si_to_lsun(p_si: float) -> float:
    """W → 太陽光度 L☉。"""
    return p_si / L_SUN_SI


def kg_to_mearth(m_kg: float) -> float:
    return m_kg / M_EARTH_KG


def kg_to_msun(m_kg: float) -> float:
    return m_kg / M_SUN_KG
