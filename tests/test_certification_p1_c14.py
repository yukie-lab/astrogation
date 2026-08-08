"""P1-C14: 50 年等高線の仕様回帰テスト(2026-08-08 ゲート追加作業 1)。

results/tableB_eta50.csv の**全行**について、記載された η と行き先距離 D から
τ_ship を逆算し、仕様値 τ = 50 yr に一致することを検証する。
背景: P1 レポート初版で Sgr A* 行が τ=100 yr 相当の η=6.25 と誤記された
(ファイルは正しかった — 転記誤り)。本テストはファイル自体を仕様に釘付けし、
以後の成果物はファイルからの転記のみとする。
"""
import csv
import math
import pathlib

import pytest

from astrogation import catalog, control, kinematics, units

CSV = pathlib.Path(__file__).resolve().parents[1] / "results" / "tableB_eta50.csv"
TAU_SPEC_YR = 50.0


def _rows():
    if not CSV.exists():
        pytest.skip("results/tableB_eta50.csv 未生成(scripts/make_catalog.py を先に実行)")
    return list(csv.DictReader(open(CSV)))


class TestC14_Eta50SpecRegression:
    def test_all_rows_hit_50yr(self):
        """記載 η と D から τ_ship を逆算 → 50.000 yr(相対 < 1e-9)。"""
        dist = dict(catalog.DESTINATIONS)
        a_geo = catalog.LAMBDA_BURN / catalog.R_REF_M
        rows = _rows()
        assert len(rows) == len(catalog.DESTINATIONS) * len(catalog.MANEUVERS)
        for r in rows:
            D = units.ly_to_m(dist[r["dest"]])
            eta = float(r["eta_50yr"])
            res = kinematics.mission_times(D, eta, a_geo, r["maneuver"])
            tau_yr = units.s_to_yr(units.time_geo_to_s(res["tau_ship"]))
            assert abs(tau_yr - TAU_SPEC_YR) / TAU_SPEC_YR < 1e-9, \
                (r["dest"], r["maneuver"], eta, tau_yr)

    def test_fuel_and_deta_consistency(self):
        """Δη計 = バーン回数 × η、m_f/m₀ = e^(−3Δη計)(相対 < 1e-10)。"""
        for r in _rows():
            eta = float(r["eta_50yr"])
            deta = float(r["delta_eta_total"])
            n_burn = kinematics.MANEUVER_BURNS[r["maneuver"]]
            assert abs(deta - n_burn * eta) < 1e-9 * max(1.0, deta)
            mf = float(r["mf_over_m0"])
            assert abs(mf - control.tsiolkovsky_ratio(deta)) < 1e-10 * max(mf, 1e-300)

    def test_audited_sgr_a_star_values(self):
        """監査で確定した Sgr A* の正値(表示桁)をデータとして固定。"""
        for r in _rows():
            if r["dest"] == "Sgr A*" and r["maneuver"] == "flyby":
                assert round(float(r["eta_50yr"]), 3) == 6.947
                assert f"{float(r['mf_over_m0']):.1e}" == "8.9e-10"
            if r["dest"] == "Sgr A*" and r["maneuver"] == "arrive":
                assert f"{float(r['mf_over_m0']):.1e}" == "7.9e-19"
