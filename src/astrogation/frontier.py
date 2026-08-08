"""天井 [R]・厚壁窓 [R]・数値フロンティア g̲(x) [N]・包絡線 [H]・診断(v3 §8/§10)。

権威ラベルの運用(conventions.md §5):
- [R] は認証合格後に拘束として使用可
- [N] g̲(x) はサンプル範囲 x ∈ [0.1, 0.7] の外で例外送出(外挿は実装レベルで不可能)
- [H] 包絡線は拘束・判定への使用禁止(表示・比較のみ)
- λ̄_DEC は診断専用。操作的フロンティア g(x) の代用禁止(L7 §B)
"""
import math

# ---------------------------------------------------------------- [R] 天井
def kinematic_ceiling(x: float) -> float:
    """運動学的天井(Λ=0)。[R] v3 (40):

        a_max R < ½(1−x)(後方極正則性 f − 2aR > 0)

    形状非依存の厳密上界。正則性の天井であり DEC フロンティアではない(Prop. 5)。"""
    return 0.5 * (1.0 - x)


def kinematic_ceiling_positive_lambda(x: float, y: float) -> float:
    """Λ > 0 の天井。[R] v3 (20):

        a R < ½(1 − x − y),  y := H²R² = (Λ/3)R²

    y = 0 で (40) に帰着(Lemma 2、厳密・全次数)。"""
    return 0.5 * (1.0 - x - y)


def x_eff(x: float, lam: float) -> float:
    """後方極実効コンパクト度 x_eff = x + 2λ。[R] v3 (40),(60)。"""
    return x + 2.0 * lam


def thick_wall_window_ok(x: float, lam: float) -> bool:
    """厚壁実現可能性(tangential-pressure 壁)。[R] v3 §10.1/10.3:

        x_eff = x + 2λ < 4/5

    窓の入れ子(v3 脚注3): 2/3(Vlasov)< 4/5(異方性弾性・厚壁)< 24/25(薄殻)。"""
    return x_eff(x, lam) < 0.8


# ------------------------------------------------------------ [N] 数値下界
class OutsideSampledRangeError(ValueError):
    """[N] 数表のサンプル範囲外アクセス(外挿禁止、CLAUDE.md §5)。"""


G_LOWER_X = (0.1, 0.2, 0.3, 0.5, 0.7)
G_LOWER_VALUES = (0.19, 0.20, 0.19, 0.14, 0.09)  # [N] v3 (S1) — スキャン分解能 ~5%


def g_lower(x: float) -> float:
    """数値フロンティア下界 g̲(x)。[N] v3 (S1):

        g̲ ≃ {0.19, 0.20, 0.19, 0.14, 0.09} at x = {0.1, 0.2, 0.3, 0.5, 0.7}

    観測者ロバスト双極子スキャンのマージンゼロ(~5% 分解能)。真のフロンティア
    g(x) の数値下界。サンプル範囲 [0.1, 0.7] 内の線形補間のみ。範囲外は
    OutsideSampledRangeError(外挿は実装レベルで不可能、x→0 の漸近は未確立)。"""
    if not (G_LOWER_X[0] <= x <= G_LOWER_X[-1]):
        raise OutsideSampledRangeError(
            f"g_lower: x={x} は [N] 数表のサンプル範囲 [{G_LOWER_X[0]}, {G_LOWER_X[-1]}] 外"
            "(外挿禁止、conventions.md §5)"
        )
    for i in range(len(G_LOWER_X) - 1):
        x0, x1 = G_LOWER_X[i], G_LOWER_X[i + 1]
        if x0 <= x <= x1:
            t = (x - x0) / (x1 - x0)
            return G_LOWER_VALUES[i] * (1.0 - t) + G_LOWER_VALUES[i + 1] * t
    raise OutsideSampledRangeError(f"g_lower: x={x}")  # 到達しない


# ------------------------------------------------------------- [H] 包絡線
def envelope_heuristic(x: float) -> float:
    """発見法的包絡線。[H] v3 (39):

        g(x) ≲ g_env(x) := ½(24/25 − x)

    Le 自身が heuristic と明記(rigid-shape 後方極を x_eff = 24/25 の静的殻と
    みなす読み)。**拘束・判定への使用禁止**(表示・比較のみ、conventions.md §5)。"""
    return 0.5 * (24.0 / 25.0 - x)


# ------------------------------------------------------- 診断(拘束使用禁止)
def lambda_bar_dec(x: float) -> float:
    """frozen-shape 軸方向閾値の静的内部推定 λ̄_DEC。[R・診断専用] v3 (43)=(62):

        λ̄_DEC(x) = (6√(16−14x) − |24−35x|)/98

    性質(v3 Lemma 5、Sturm 証明済み): (0,24/25) で正、両端点でゼロ、
    天井 ½(1−x) より厳密に下、小 x で x/4 + O(x²)。
    **警告**: 剛体形状の軸診断であり、操作的フロンティア g(x) と大域順序なし。
    拘束としての使用禁止(L7 §B)。"""
    return (6.0 * math.sqrt(16.0 - 14.0 * x) - abs(24.0 - 35.0 * x)) / 98.0


# ---------------------------------------------- [R] 厳密下界 c(x) の記録値
C_LOWER_X = (0.1, 0.2, 0.3, 0.5, 0.7)
C_LOWER_VALUES = (8.5e-5, 1.4e-4, 1.7e-4, 1.4e-4, 2.0e-5)
"""[R] v3 (73): c(x) ≈ {8.5, 14, 17, 14, 2.0}×10⁻⁵(Lemma 6 の閉形式評価値)。
g̲ より約 3 桁保守的な「厳密安全床」。定数鎖 (68)-(72) の自前再評価は
Phase 0 の範囲外(L7 §C・P0 レポート参照)— ここでは論文記録値のみ保持。"""
