"""Phase 3 認証(P3-C19+文体 lint+引用義務)。

C19 の範囲(docstring 契約): 論文中の「カタログ由来の計算値」は必ず \\Nm マクロ
経由とし、(i) 原稿散文(数式・参考文献・生成 \\input を除く)に裸の計算値
リテラルがないこと、(ii) manifest の代表値が一次ソースから transform で
再計算一致することを検証する。数式モード内の格子座標(η=0.24 等)・構造定数
(24/25, 3, 1/2)・文献引用値(0.9931 等)・許容値(1e-8)は式・仕様・引用で
あり C19 の対象外(生成側で manifest 化されるのは results/ 由来の計算値)。
"""
import csv
import json
import math
import pathlib
import re
from fractions import Fraction

import pytest

REPO = pathlib.Path(__file__).resolve().parents[1]
PAP = REPO / "paper"
RES = REPO / "results"


def _tex():
    p = PAP / "paper_en.tex"
    if not p.exists():
        pytest.skip("paper/paper_en.tex 未生成")
    return p.read_text()


def _prose(tex: str) -> str:
    """散文抽出: プリアンブル・コメント・数式・参考文献・\\input 行を除去。"""
    if r"\begin{document}" in tex:
        tex = tex.split(r"\begin{document}", 1)[1]
    tex = re.sub(r"(?<!\\)%.*", "", tex)
    tex = tex.split(r"\begin{thebibliography}")[0]
    tex = re.sub(r"\$[^$]*\$", " MATH ", tex)
    tex = re.sub(r"\\input\{[^}]*\}", " INPUT ", tex)
    tex = re.sub(r"\\includegraphics\[[^]]*\]\{[^}]*\}", " FIG ", tex)
    tex = re.sub(r"\\(?:cite|ref|eqref|label|url|href)\{[^}]*\}", " REF ", tex)
    return tex


# ================================================================ C19
class TestC19_NumbersPipeline:
    def test_no_bare_numeric_literals_in_prose(self):
        """散文に裸の計算値リテラル(小数・指数表記・3 桁以上の整数)がない。

        許可: 年(19xx/20xx)・arXiv ID・日付・バージョン・2 桁以下の整数
        (構造的小整数)・マクロ展開(\\Nm...)。"""
        prose = _prose(_tex())
        prose = re.sub(r"arXiv:\d{4}\.\d{4,5}", " ARXIV ", prose)
        prose = re.sub(r"gr-qc/\d{7}", " ARXIV ", prose)
        prose = re.sub(r"\b(19|20)\d\d\b", " YEAR ", prose)
        prose = re.sub(r"\b\d{4}-\d{2}-\d{2}\b", " DATE ", prose)
        prose = re.sub(r"C1--C1?\d", " CERT ", prose)
        prose = re.sub(r"10\^\{?-?\d+\}?", " TOL ", prose)
        bad = []
        for m in re.finditer(r"\d+\.\d+|\d+[eE][+-]?\d+|\b\d{3,}\b", prose):
            ctx = prose[max(0, m.start() - 40):m.end() + 20].replace("\n", " ")
            bad.append(f"'{m.group()}' in ...{ctx}...")
        assert not bad, "裸の数値リテラル:\n" + "\n".join(bad)

    def test_manifest_recompute(self):
        """manifest 代表値の一次ソース再計算一致(表示 transform 込み)。"""
        man = json.loads((PAP / "paper_numbers_manifest.json").read_text())
        entries = {e["macro"]: e for e in man["entries"]}
        # 50 年等高線
        eta50 = {(r["dest"], r["maneuver"]): r
                 for r in csv.DictReader(open(RES / "tableB_eta50.csv"))}
        assert entries["AndEta"]["value_displayed"] == \
            f"{float(eta50[('M31 (Andromeda)', 'flyby')]['eta_50yr']):.2f}"
        assert entries["SgrEta"]["value_displayed"] == \
            f"{float(eta50[('Sgr A*', 'flyby')]['eta_50yr']):.3f}"
        # FlashPeak: 一次ソース+検証 transform(P3a §4 確定)
        sig = json.loads((RES / "signatures" /
                          "sig_mission_m31_arrive_eta12.0.json").read_text())
        fp = float(sig["angles"]["dest"]["F_peak"])
        dtot = float(sig["meta"]["delta_eta_total"])
        fp_closed = (6.0 * 0.19 / (4.0 * math.pi)) * math.exp(7 * 12.0 - 3 * dtot)
        assert abs(fp - fp_closed) / fp_closed < 1e-12
        assert entries["FlashPeak"]["value_displayed"].startswith("1.48")
        assert entries["FlashExp"]["value_displayed"] == "72"
        # x* の厳密有理再計算(P1 主結果 4 の閉形式)
        x = Fraction(27, 50)
        lhs = Fraction(14, 100) - Fraction(1, 4) * (x - Fraction(1, 2))
        rhs = (Fraction(4, 5) - x) / 2
        assert lhs == rhs and float(x) == 0.54
        assert entries["Xstar"]["value_displayed"] == "0.54"
        # SI(R=1km, x0=0.3)
        si = list(csv.DictReader(open(RES / "si_layer.csv")))
        row = next(r for r in si
                   if float(r["R_m"]) == 1000.0 and float(r["x0"]) == 0.3)
        assert entries["MassMsunKm"]["value_displayed"] == \
            f"{float(f'{float(row['shell_mass_Msun']):.3g}'):g}"
        # G3 統計
        summ = list(csv.DictReader(
            open(RES / "signatures" / "signature_summary.csv")))
        worst_ride = max(float(r["g3_map_rel"]) for r in summ
                         if r["kind"] == "ride")
        assert entries["MapRide"]["value_displayed"].startswith("1.06")
        assert worst_ride < 2e-6
        assert len(summ) == 567

    def test_roundtrip_convention_arcsinh(self):
        """[3b 修正1] 往復列の規約: 表示 η_RT = arcsinh(2D/τ)(丸め一致)かつ
        CSV の roundtrip eta_50yr と一致(manifest 経由の注入を確認)。"""
        man = json.loads((PAP / "paper_numbers_manifest.json").read_text())
        entries = {e["macro"]: e for e in man["entries"]}
        eta50 = {(r["dest"], r["maneuver"]): r
                 for r in csv.DictReader(open(RES / "tableB_eta50.csv"))}
        dists = {"ProxEtaRT": ("Proxima Centauri", 4.25, 3),
                 "TraEtaRT": ("TRAPPIST-1", 40.5, 3),
                 "SgrEtaRT": ("Sgr A*", 2.6e4, 3),
                 "AndEtaRT": ("M31 (Andromeda)", 2.54e6, 2)}
        for mac, (d, d_ly, nd) in dists.items():
            csv_v = float(eta50[(d, "roundtrip")]["eta_50yr"])
            conv = math.asinh(2.0 * d_ly / 50.0)
            disp = entries[mac]["value_displayed"]
            assert disp == f"{csv_v:.{nd}f}", (mac, disp)
            assert f"{conv:.{nd}f}" == disp, (mac, conv, disp)
        # 原稿の η_RT 記述はマクロ経由(AndEtaRT が本文使用)
        assert "\\NmAndEtaRT" in _tex()

    def test_all_macros_used_or_tabled(self):
        """numbers.tex の全マクロが原稿で使用されている(死にマクロ検出)。"""
        tex = _tex()
        for line in (PAP / "numbers.tex").read_text().splitlines():
            m = re.match(r"\\newcommand\{\\(Nm\w+)\}", line)
            if m and m.group(1) not in ("NmGLowerTable", "NmCPaperTable",
                                        "NmCConsTable", "NmTflQ", "NmTeffQ",
                                        "NmTceilQ", "NmTflXII", "NmTeffXII",
                                        "NmTceilXII", "NmTraEta", "NmTraMf",
                                        "NmSgrMfArr", "NmMassKgKm", "NmRepoCommit",
                                        "NmProxEtaRT", "NmTraEtaRT",
                                        "NmSgrEtaRT"):
                assert f"\\{m.group(1)}" in tex, f"未使用マクロ: {m.group(1)}"


# ==================================================== 文体 lint(PHASE_3)
class TestStyleLint:
    BANNED = ("novel", "remarkable", "fascinating", "delve", "groundbreaking")

    def test_banned_words(self):
        prose = _prose(_tex()).lower()
        for w in self.BANNED:
            assert w not in prose, f"禁止語: {w}"

    def test_dash_budget_per_section(self):
        """em-dash 挿入は 1 節 1 回まで(対の '---' 2 個 = 1 挿入)。"""
        tex = _tex().split(r"\begin{thebibliography}")[0]
        sections = re.split(r"\\section\*?\{", tex)
        for sec in sections:
            n = sec.count("---")
            assert n <= 2, f"ダッシュ過多({n} 個): {sec[:60]}"

    def test_in_this_paper_once(self):
        prose = _prose(_tex())
        assert len(re.findall(r"\bIn this paper\b", prose)) <= 1

    def test_no_itemize_in_body(self):
        tex = _tex()
        assert r"\begin{itemize}" not in tex
        assert r"\begin{enumerate}" not in tex


# ==================================================== 引用義務(CLAUDE.md §12)
class TestCitationObligations:
    def test_all_obligations_present(self):
        tex = _tex()
        for needle in ("2606.22531", "2605.25417", "2602.18023",
                       "104081",              # Füzfa PRD 99
                       "gr-qc/9412063",       # Damour 1995
                       "world_tube", "warpax"):
            assert needle in tex, f"引用義務欠落: {needle}"
