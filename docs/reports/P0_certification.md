# P0 — 認証レポート(Phase 0 ゲート成果物)

作成日: 2026-08-08。
環境: conda env `warpax`(Python 3.12.13 / numpy 2.4.6 / pytest 9.1.1 / warpax 1.3.0)。
実行: `/Users/yukie/miniforge3/envs/warpax/bin/python -m pytest tests`
結果: **40 passed, 6 skipped(考古学=既定 skip)、4.57 s**(制約 < 1 分)。
`--run-archaeology` 込みでは **46 passed**。

## 1. 認証一覧(C1–C8)

| ID | 対象式(v3) | 論文記載値/主張 | 計算値/検証法 | 実測誤差 | 判定 |
|---|---|---|---|---|---|
| C1 | (15) Tsiolkovsky | m_f/m₀ = e^(−3Δη) | `control.tsiolkovsky_ratio` vs `exp`;乗法性 | **0.0**(< 1e-12) | **PASS** |
| C2 | (22)-(25),(58),(61) | 窓境界 x=24/25 で符号反転・窓内で正 | **Fraction 有理評価で s=1/5 において厳密ゼロ**;グリッド全域符号;直接形/因数分解/M₀ 三者一致 | 厳密 0 / ~1e-16 | **PASS** |
| C3a | (77),(79) | cos行 = (−x/(1−x), −2√(1−x))、(0,1) で非零 | (79) の線形差分と閉形式の一致;A_t1 根 −(ρ₁+2)x/(2s³) 再現;∂_R√f > 0 | < 1e-15 | **PASS** |
| C3b | (80),(81) | 呼吸勾配 −x/s² ≠ 0;判別式 16x(x−1)(9x²+11x+4) < 0 | **Fraction で B²−4AC 恒等を厳密確認**(7 有理点);グリッド負値;9x²+11x+4 の判別式 = −23(厳密) | 厳密 0 | **PASS** |
| C3c | (77)/Lemma 8 | det J₀ = −2√(1−x) ≠ 0 | 積構造(cos行 × tilt行 1)と閉形式一致 | ~1e-16 | **PASS** |
| C3d | (88) | ℓ=2 minor det = 2x√(1−x) ≠ 0 | 行列式 vs 閉形式;**det² = 4x²(1−x) を Fraction で厳密確認** | 厳密 0 / ~1e-16 | **PASS** |
| C4 | Supplement(v2 App K) | 放射質量比 ≈**51%**、x_eff^peak = **0.46** < 4/5、λ_max = 0.12 < g̲(0.3) | 無次元閉包(A2): radiated = 0.513248 → **51%**;peak = 0.459709 → **0.46**;バーン全域で天井・厚壁窓・g̲ 遵守 | 表示桁一致 | **PASS** |
| C5 | (40),(20) | λ < ½(1−x);Λ>0 で ½(1−x−y) | 閉形式一致;**aR < ½(1−x) ⟺ x+2aR < 1 を Fraction で厳密同値確認**(500 有理点);y による締め = y/2 | 厳密 / < 1e-12 | **PASS** |
| C6 | (13),(29)=(59) | ∮n²dΩ = −ṁ、−∮n²cosϑdΩ = ma | Gauss–Legendre 16 点求積 vs 閉形式(50 組);n²≥0 ⟺ 制御則の同値;飽和時 4πn² = 3ma(1−cosϑ)、前方極**厳密ゼロ** | **7.0e-16**(< 1e-10) | **PASS** |
| C7 | conventions §1 | 幾何↔SI↔天文の往復 | 5 換算対 × 5 値の双方向往復;ly = 9 460 730 472 580 800 m(厳密一致);GM☉/c² = 1476.625038 ≈ 1476.6250 m | < 1e-15 | **PASS** |
| C8 | (14)-(15) G3 初回 | 閉形式 vs 制御則 ODE;warpax 接続 | 飽和則 RK4(N=4096)vs e^(−3Δη):**5.6e-14**(< 1e-8);budget_rate↔moments 整合;直線 d_H³ = Δη;**warpax 1.3.0 import 成功、bondi API(extract, radiated_momentum_flux, weyl_scalars, peeling)確認** | 5.6e-14 | **PASS** |

補助認証(認証セット外、L2 §5/L8 §5 の提案分):
λ̄_DEC (43) の**端点厳密ゼロ**(x=0: 6·4−24=0、x=24/25: radicand=(8/5)² → 6·8/5−48/5=0、
Fraction 厳密)・窓内正値・天井未満・小 x 傾き 1/4 (44)・枝替わり点 24/35 の連続性;
g̲ (S1) 5 点の厳密転記と**範囲外例外**(外挿の実装レベル禁止)・包絡線 (39) 尊重;
c(x) (73) 記録値の転記と g̲ 比 ~10⁻³ の関係 — **全 PASS**。

## 2. 指示書からの逸脱(要記録)

**PHASE_0.md 0-2 の `shell.py` 仕様に「D(x)」が含まれるが、実装しなかった。**
根拠: PHASE_0.md は C3 再定義(2026-08-08 人間承認、L6・改定 CLAUDE.md §4)より
前に書かれており、D(x) は [v2-retracted](v3 に対応構造なし・下流使用禁止)。
`shell.py` は代わりに v3 の ℓ 閉包証人((77),(79),(80),(81),(88))を実装した。
ガード `tests/test_v2_retracted_guard.py` が src/ 全体で不使用を機械的に確認している
(guard PASS)。

## 3. 新規物理計算ゼロの確認(DoD)

src/ の全関数は式台帳 L2 の閉形式の転記のみ(docstring に v3 式番号と権威ラベルを
併記、コードレビューで対照可能)。数値積分は認証テスト内のみで、いずれも
PHASE_0.md が明示的に要求するもの(C6 求積、C8 ODE、C4 の Supplement 再現)。
c(x) の定数鎖 (68)-(72) の自前再評価は行っていない(L7 §C の判断どおり記録値のみ、
`frontier.C_LOWER_VALUES`)。

## 4. DoD チェック

- [x] conventions.md 完成 — **提出済み・人間承認待ち**
- [x] pytest 全緑(C1–C8)— 40 passed + 考古学 6(明示実行で 46 passed)、4.57 s
- [x] P0_certification.md(本書)
- [x] ASSUMPTIONS.md — A1(検証範囲声明)+ **A2(実働バーンの無次元閉包)** を登録。
      Phase 0 で置いた仮定は A2 のみ
- [x] 新規物理計算ゼロ(§3)

## 5. STOP 事由

該当なし。C4 は初回一致(修正 0 回)。論文数値間の矛盾は検出されず
(51% ↔ e^(−0.72) = 0.48675 の整合、0.46 ↔ 無次元閉包の再計算一致を含む)。

## 6. pytest 出力(全 46 項目)

```
tests/archaeology/test_v2_D_bifurcation.py::test_v2_58_two_closed_forms_agree SKIPPED*
tests/archaeology/test_v2_D_bifurcation.py::test_v2_59_factorization_identity SKIPPED*
tests/archaeology/test_v2_D_bifurcation.py::test_v2_60_bound_sign_and_limit SKIPPED*
tests/archaeology/test_v2_D_bifurcation.py::test_v2_59_Q_positivity_on_window SKIPPED*
tests/archaeology/test_v2_D_bifurcation.py::test_v2_61_monotonicity_identity_and_positivity SKIPPED*
tests/archaeology/test_v2_D_bifurcation.py::test_window_endpoint_mapping SKIPPED*
tests/test_auxiliary_diagnostics.py::TestLambdaBarDEC::test_endpoint_exact_zeros_rational PASSED
tests/test_auxiliary_diagnostics.py::TestLambdaBarDEC::test_positive_and_below_ceiling_on_window PASSED
tests/test_auxiliary_diagnostics.py::TestLambdaBarDEC::test_small_x_slope_one_quarter PASSED
tests/test_auxiliary_diagnostics.py::TestLambdaBarDEC::test_crossover_at_24_over_35 PASSED
tests/test_auxiliary_diagnostics.py::TestGLowerGuards::test_nodes_exact PASSED
tests/test_auxiliary_diagnostics.py::TestGLowerGuards::test_out_of_range_raises PASSED
tests/test_auxiliary_diagnostics.py::TestGLowerGuards::test_respects_heuristic_envelope PASSED
tests/test_auxiliary_diagnostics.py::TestCLowerRecord::test_paper_values_recorded PASSED
tests/test_certification.py::TestC1_Tsiolkovsky::test_closed_form_against_exp PASSED
tests/test_certification.py::TestC1_Tsiolkovsky::test_multiplicativity PASSED
tests/test_certification.py::TestC2_SurfaceDECWindow::test_exact_zero_crossing_at_window_boundary PASSED
tests/test_certification.py::TestC2_SurfaceDECWindow::test_sign_reversal_and_positivity_in_window PASSED
tests/test_certification.py::TestC2_SurfaceDECWindow::test_direct_vs_factorized_and_M0 PASSED
tests/test_certification.py::TestC2_SurfaceDECWindow::test_wec_strict_positivity PASSED
tests/test_certification.py::TestC3a_CosRow::test_partials_match_79 PASSED
tests/test_certification.py::TestC3a_CosRow::test_nonvanishing_on_window PASSED
tests/test_certification.py::TestC3a_CosRow::test_At1_root_closed_form PASSED
tests/test_certification.py::TestC3b_BreathingAndNecessity::test_breathing_slope_closed_form_nonzero PASSED
tests/test_certification.py::TestC3b_BreathingAndNecessity::test_discriminant_identity_exact_rational PASSED
tests/test_certification.py::TestC3b_BreathingAndNecessity::test_discriminant_negative_on_window PASSED
tests/test_certification.py::TestC3c_SchurDeterminant::test_detJ0_closed_form_nonzero PASSED
tests/test_certification.py::TestC3d_L2Minor::test_matrix_det_matches_closed_form PASSED
tests/test_certification.py::TestC3d_L2Minor::test_det_squared_exact_rational PASSED
tests/test_certification.py::TestC4_WorkedBurn::test_radiated_mass_fraction_51_percent PASSED
tests/test_certification.py::TestC4_WorkedBurn::test_xeff_peak_046_and_windows PASSED
tests/test_certification.py::TestC4_WorkedBurn::test_saturated_budget_positive_mass PASSED
tests/test_certification.py::TestC5_KinematicCeiling::test_closed_form PASSED
tests/test_certification.py::TestC5_KinematicCeiling::test_equivalence_with_xeff_exact_rational PASSED
tests/test_certification.py::TestC5_KinematicCeiling::test_positive_lambda_tightening PASSED
tests/test_certification.py::TestC6_MomentIdentities::test_quadrature_moments PASSED
tests/test_certification.py::TestC6_MomentIdentities::test_positivity_iff_control_law PASSED
tests/test_certification.py::TestC6_MomentIdentities::test_saturation_single_rear_lobe PASSED
tests/test_certification.py::TestC7_UnitsRoundTrip::test_round_trips PASSED
tests/test_certification.py::TestC7_UnitsRoundTrip::test_defined_constants PASSED
tests/test_certification.py::TestC8_TwoPathAndWarpax::test_tsiolkovsky_closed_form_vs_ode PASSED
tests/test_certification.py::TestC8_TwoPathAndWarpax::test_budget_rate_consistency PASSED
tests/test_certification.py::TestC8_TwoPathAndWarpax::test_geodesy_collinear_consistency PASSED
tests/test_certification.py::TestC8_TwoPathAndWarpax::test_warpax_connection PASSED
tests/test_v2_retracted_guard.py::test_registry_exists_and_nonempty PASSED
tests/test_v2_retracted_guard.py::test_no_retracted_symbols_in_src PASSED

40 passed, 6 skipped in 4.57s   (* = [v2-retracted] 考古学、--run-archaeology で 46 passed)
```
