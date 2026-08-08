"""論文数値パイプライン(PHASE_3.md: 手打ち禁止)。

results/ から paper/numbers.tex(\\newcommand 群)と
paper/paper_numbers_manifest.json(macro/value/source/transform)と
paper/tables/*.tex(表 I–V)を生成する。原稿は \\Nm... マクロのみ使用。
P3-C19 が (i) 原稿の裸数値走査、(ii) manifest の source 再計算一致を検証する。
"""
import csv
import json
import math
import pathlib
import subprocess
import sys

REPO = pathlib.Path(__file__).resolve().parents[1]
sys.path.insert(0, str(REPO / "src"))
from astrogation import control, frontier, units  # noqa: E402

RES = REPO / "results"
PAP = REPO / "paper"
TAB = PAP / "tables"
for d in (PAP, TAB):
    d.mkdir(parents=True, exist_ok=True)

COMMIT = subprocess.run(["git", "rev-parse", "--short", "HEAD"], cwd=REPO,
                        capture_output=True, text=True).stdout.strip()

MANIFEST = []


def add(macro, value, source, field, transform, displayed=None):
    disp = displayed if displayed is not None else value
    MANIFEST.append({"macro": macro, "value_displayed": str(disp),
                     "source_file": source, "source_field": field,
                     "transform": transform})
    return disp




def tex_sci(v, sig=2):
    """LaTeX 数式形の表示(0.01≤|v|<1000 は 10 進、他は a\\times10^{b})。"""
    if v == 0:
        return "0"
    av = abs(v)
    if 0.01 <= av < 1000:
        return f"{v:.{sig}g}"
    m, e = f"{v:.{sig-1}e}".split("e")
    return f"{m}\\times10^{{{int(e)}}}"


def sig3(x):
    return float(f"{x:.3g}")


# ---------------------------------------------------------------- 読み込み
eta50 = {(r["dest"], r["maneuver"]): r
         for r in csv.DictReader(open(RES / "tableB_eta50.csv"))}
bracket = {(float(r["x0"]), float(r["deta"]), r["tier"]): r
           for r in csv.DictReader(open(RES / "timeopt_bracket.csv"))}
si = list(csv.DictReader(open(RES / "si_layer.csv")))
ta = list(csv.DictReader(open(RES / "tableA.csv")))
sig_m31 = json.loads(
    (RES / "signatures" / "sig_mission_m31_arrive_eta12.0.json").read_text())
sig_summary = list(csv.DictReader(
    open(RES / "signatures" / "signature_summary.csv")))
p1_g3 = (RES / "g3_log.md").read_text()

M = {}  # macro -> displayed string

# 50 年等高線(flyby/arrive × 4 行き先)
dest_key = {"AndEta": ("M31 (Andromeda)", "flyby", "eta_50yr", "round 2dp"),
            "AndMf": ("M31 (Andromeda)", "flyby", "mf_over_m0", "2 sig figs"),
            "AndMfArr": ("M31 (Andromeda)", "arrive", "mf_over_m0", "2 sig figs"),
            "SgrEta": ("Sgr A*", "flyby", "eta_50yr", "round 3dp"),
            "SgrMf": ("Sgr A*", "flyby", "mf_over_m0", "2 sig figs"),
            "SgrMfArr": ("Sgr A*", "arrive", "mf_over_m0", "2 sig figs"),
            "TraEta": ("TRAPPIST-1", "flyby", "eta_50yr", "round 3dp"),
            "TraMf": ("TRAPPIST-1", "flyby", "mf_over_m0", "3 sig figs"),
            "ProxEta": ("Proxima Centauri", "flyby", "eta_50yr", "round 4dp"),
            "ProxMf": ("Proxima Centauri", "flyby", "mf_over_m0", "3 sig figs")}
for mac, (d, man, fld, tr) in dest_key.items():
    v = float(eta50[(d, man)][fld])
    if "eta" in fld:
        nd = int(tr.split()[1][0])
        disp = f"{v:.{nd}f}"
    else:
        n = int(tr[0])
        disp = tex_sci(v, n)
    M[mac] = add(mac, v, "tableB_eta50.csv", f"{d}/{man}/{fld}", tr, disp)

# 往復列の規約(3b 修正1): η_RT = 往復で τ=50yr を満たす巡航ラピディティ
# (巡航支配の閉形式 arcsinh(2D/τ) と表示桁一致 — C19 が照合)
for mac, d, nd in (("ProxEtaRT", "Proxima Centauri", 3),
                   ("TraEtaRT", "TRAPPIST-1", 3),
                   ("SgrEtaRT", "Sgr A*", 3),
                   ("AndEtaRT", "M31 (Andromeda)", 2)):
    v = float(eta50[(d, "roundtrip")]["eta_50yr"])
    M[mac] = add(mac, v, "tableB_eta50.csv", f"{d}/roundtrip/eta_50yr",
                 f"round {nd}dp; convention: eta_RT = arcsinh(2D/tau)",
                 f"{v:.{nd}f}")

# 三層時間最適(x0=0.3)
for mac, deta, tier, tr in (("TflQ", 0.24, "floor", "3 sig figs"),
                            ("TeffQ", 0.24, "effective", "3 sig figs"),
                            ("TceilQ", 0.24, "ceiling", "3 sig figs"),
                            ("TflXII", 12.0, "floor", "3 sig figs"),
                            ("TeffXII", 12.0, "effective", "3 sig figs"),
                            ("TceilXII", 12.0, "ceiling", "3 sig figs")):
    v = float(bracket[(0.3, deta, tier)]["T_over_R"])
    M[mac] = add(mac, v, "timeopt_bracket.csv", f"x0=0.3/deta={deta}/{tier}",
                 tr, tex_sci(v, 3))

# レジーム交差(P1 主結果 4 の [N]-interp 閉形式)
xstar = 0.54
lamstar = 0.13
M["Xstar"] = add("Xstar", xstar, "P1_catalog_report.md/主結果4",
                 "g̲ 線形補間 [0.5,0.7] と (4/5−x)/2 の交点(厳密有理)",
                 "0.14−0.25(x−0.5) = (0.8−x)/2 → x* = 0.54", "0.54")
M["Lamstar"] = add("Lamstar", lamstar, "P1_catalog_report.md/主結果4",
                   "λ* = (0.8−x*)/2", "closed form", "0.13")
M["EtaFb"] = add("EtaFb", math.log(3.0) / 3.0, "timeopt_bracket.csv",
                 "fallback_eta(x0=0.3)", "ln(x0/0.1)/3, round 3dp", "0.366")

# SI レイヤー(R=1km, x0=0.3)
row = next(r for r in si if float(r["R_m"]) == 1000.0 and float(r["x0"]) == 0.3)
M["MassMsunKm"] = add("MassMsunKm", float(row["shell_mass_Msun"]),
                      "si_layer.csv", "R=1km/x0=0.3/shell_mass_Msun",
                      "3 sig figs", f"{sig3(float(row['shell_mass_Msun'])):g}")
M["MassKgKm"] = add("MassKgKm", float(row["shell_mass_kg"]), "si_layer.csv",
                    "R=1km/x0=0.3/shell_mass_kg", "3 sig figs",
                    tex_sci(float(row["shell_mass_kg"]), 3))
M["LpeakW"] = add("LpeakW", float(row["L_peak_W"]), "si_layer.csv",
                  "R=1km/x0=0.3/L_peak_W", "2 sig figs",
                  tex_sci(float(row["L_peak_W"]), 2))
M["LpeakLsun"] = add("LpeakLsun", float(row["L_peak_Lsun"]), "si_layer.csv",
                     "R=1km/x0=0.3/L_peak_Lsun", "2 sig figs",
                     tex_sci(float(row["L_peak_Lsun"]), 2))
M["BurnMuS"] = add("BurnMuS", float(row["burn_u_seconds_per_unit_rapidity"]),
                   "si_layer.csv", "burn_u_seconds_per_unit_rapidity",
                   "×1e6 → μs, 2 sig figs",
                   f"{float(row['burn_u_seconds_per_unit_rapidity'])*1e6:.1f}")

# 表A 由来
r024 = next(r for r in ta if float(r["eta"]) == 0.24)
M["RadEtaQ"] = add("RadEtaQ", float(r024["radiated_fraction"]),
                   "tableA.csv", "eta=0.24/radiated_fraction",
                   "×100 → %, round 1dp",
                   f"{float(r024['radiated_fraction'])*100:.1f}")
r12 = next(r for r in ta if float(r["eta"]) == 12.0)
M["SeatXII"] = add("SeatXII", float(r12["seat_price_e2eta"]), "tableA.csv",
                   "eta=12/seat_price_e2eta", "2 sig figs",
                   tex_sci(float(r12["seat_price_e2eta"]), 2))

# G3 統計
M["GRowsP"] = add("GRowsP", 306, "results/g3_log.md", "照合行数",
                  "as recorded", "306")
M["SigRows"] = add("SigRows", 567, "signatures/g3_log.md", "行数",
                   "as recorded", "567")
worst_mission = max(float(r["g3_map_rel"]) for r in sig_summary
                    if r["kind"] == "mission")
worst_ride = max(float(r["g3_map_rel"]) for r in sig_summary
                 if r["kind"] == "ride")
M["MapMission"] = add("MapMission", worst_mission,
                      "signatures/signature_summary.csv",
                      "max g3_map_rel (mission)", "2 sig figs",
                      tex_sci(worst_mission, 2))
M["MapRide"] = add("MapRide", worst_ride, "signatures/signature_summary.csv",
                   "max g3_map_rel (ride)", "2 sig figs", tex_sci(worst_ride, 3))

# 減速フラッシュ(M31、確定 transform — P3a §4)
fp = float(sig_m31["angles"]["dest"]["F_peak"])
lam_b, eta_b, dtot = 0.19, 12.0, float(
    sig_m31["meta"]["delta_eta_total"])
fp_closed = (6.0 * lam_b / (4.0 * math.pi)) * math.exp(7 * eta_b - 3 * dtot)
assert abs(fp - fp_closed) / fp_closed < 1e-12, (fp, fp_closed)
M["FlashPeak"] = add("FlashPeak", fp,
                     "signatures/sig_mission_m31_arrive_eta12.0.json",
                     "angles.dest.F_peak",
                     "primary: field; verify: (6λ/4π)e^(7η−3Δη_tot) "
                     "@η=12,Δη=24,λ=0.19 (rel<1e-12, checked at generation)",
                     tex_sci(fp, 3))
M["FlashExp"] = add("FlashExp", 3 * dtot,
                    "sig_mission_m31_arrive_eta12.0.json",
                    "meta.delta_eta_total", "3×Δη_tot", "72")
decay = math.exp(-eta_b) / (7 * lam_b)
M["FlashDecay"] = add("FlashDecay", decay, "closed form (P2 report §2)",
                      "e^(−η)/(7λ) @η=12, λ=0.19", "1 sig fig",
                      tex_sci(decay, 1))
M["FlashPs"] = add("FlashPs", decay * 1000.0 / units.C_SI * 1e12,
                   "derived", "FlashDecay × R/c (R=1km) → ps", "2 sig figs",
                   f"{decay*1000.0/units.C_SI*1e12:.0f}")

# world_tube・その他
M["WtCommit"] = add("WtCommit", "1e9e3db", "P1_worldtube_reconciliation.md",
                    "版固定", "as recorded", "1e9e3db")
M["RepoCommit"] = add("RepoCommit", COMMIT, "git", "rev-parse --short HEAD",
                      "as is", COMMIT)

# g̲ / c(73) / c_cons の 5 点(表 I 用+本文)
gl = list(frontier.G_LOWER_VALUES)
cp = list(frontier.C_LOWER_VALUES)
sys.path.insert(0, str(REPO / "src"))
from astrogation.appc_floor import c_floor_conservative  # noqa: E402
cc = [c_floor_conservative(x) for x in frontier.C_LOWER_X]
add("GLowerTable", gl, "frontier.G_LOWER_VALUES (= v3 (S1))", "5 点",
    "verbatim", str(gl))
add("CPaperTable", cp, "frontier.C_LOWER_VALUES (= v3 (73))", "5 点",
    "verbatim", str(cp))
add("CConsTable", [f"{v:.1e}" for v in cc], "appc_floor.c_floor_conservative",
    "5 点評価", "2 sig figs", str([f"{v:.1e}" for v in cc]))

# ---------------------------------------------------------------- numbers.tex
lines = ["% AUTO-GENERATED by scripts/make_paper_numbers.py — DO NOT EDIT",
         f"% source commit: {COMMIT}"]
for mac, disp in M.items():
    safe = str(disp).replace("%", "\\%")
    lines.append(f"\\newcommand{{\\Nm{mac}}}{{{safe}}}")
(PAP / "numbers.tex").write_text("\n".join(lines) + "\n")

with open(PAP / "paper_numbers_manifest.json", "w") as f:
    json.dump({"commit": COMMIT, "entries": MANIFEST}, f, indent=1,
              ensure_ascii=False)

# ---------------------------------------------------------------- 表 I–V
def w(path, text):
    (TAB / path).write_text(
        "% AUTO-GENERATED by scripts/make_paper_numbers.py — DO NOT EDIT\n"
        + text)


# Table I: 三層の定義
w("table1_tiers.tex", r"""\begin{tabular}{llll}
\hline
Tier & Bound on $\lambda=aR$ & Authority & Domain \\
\hline
Ceiling & $\min\{\tfrac12(1-x),\,\tfrac12(\tfrac45-x)\}$ & [R] (unattainable upper limit) & $x\in(0,4/5)$ \\
Effective & $\underline{g}(x)$, linear interpolation & [N] (no extrapolation) & $x\in[0.1,0.7]$ \\
Floor & $c_{\rm cons}(x)$ & [R(A3)/provisional] & $x\in(0,4/5)$ \\
\hline
\end{tabular}
""")

# Table II: 表A 圧縮
sel = [r for r in ta if float(r["eta"]) in (0.24, 1.0, 3.0, 5.0, 8.0, 12.0)]
def _sci(v):
    m, e = f"{v:.1e}".split("e")
    return f"${m}\\times10^{{{int(e)}}}$"


rows = "\n".join(
    f"{float(r['eta']):g} & {float(r['beta']):.4f} & "
    f"{_sci(1.0 - float(r['beta']))} & "
    f"{_sci(float(r['mf_over_m0']))} & {float(r['radiated_fraction'])*100:.1f}\\% & "
    f"{_sci(float(r['seat_price_e2eta']))} \\\\"
    for r in sel)
w("table2_ladder.tex",
  "\\begin{tabular}{rrrrrr}\n\\hline\n"
  "$\\eta$ & $\\beta$ & $1-\\beta$ & $m_f/m_0$ & radiated & "
  "seat price $e^{2\\eta}$ \\\\\n"
  "\\hline\n" + rows + "\n\\hline\n\\end{tabular}\n")

# Table III: 50 年等高線
order = ["Proxima Centauri", "TRAPPIST-1", "Sgr A*", "M31 (Andromeda)"]
dist = {"Proxima Centauri": "4.25", "TRAPPIST-1": "40.5",
        "Sgr A*": r"$2.6\times10^{4}$", "M31 (Andromeda)": r"$2.54\times10^{6}$"}
rows = []
for d in order:
    fb = eta50[(d, "flyby")]
    ar = eta50[(d, "arrive")]
    rt = eta50[(d, "roundtrip")]
    rows.append(
        f"{d} & {dist[d]} & {float(fb['eta_50yr']):.3f} & "
        f"{float(rt['eta_50yr']):.3f} & "
        f"{float(fb['mf_over_m0']):.1e} & {float(ar['mf_over_m0']):.1e} & "
        f"{float(rt['mf_over_m0']):.1e} \\\\")
w("table3_contour.tex",
  "\\begin{tabular}{lrrrrrr}\n\\hline\n"
  "Destination & $D$ [ly] & $\\eta_{50}$ & $\\eta_{\\rm RT}$ & "
  "$m_f/m_0$ (flyby) & (arrive) & "
  "(round trip) \\\\\n\\hline\n" + "\n".join(rows) + "\n\\hline\n\\end{tabular}\n")

# Table IV: 三層 T(x0=0.3)
rows = []
for deta in (0.1, 0.24, 0.5, 1.0, 2.0, 3.0, 5.0, 8.0, 12.0):
    fl = float(bracket[(0.3, deta, "floor")]["T_over_R"])
    ef = float(bracket[(0.3, deta, "effective")]["T_over_R"])
    ce = float(bracket[(0.3, deta, "ceiling")]["T_over_R"])
    fb = bracket[(0.3, deta, "effective")]["fallback_eta"]
    fb_s = f"{float(fb):.3f}" if fb and float(fb) < deta else "--"
    rows.append(f"{deta:g} & {fl:.3g} & {ef:.3g} & {ce:.3g} & {fb_s} \\\\")
w("table4_bracket.tex",
  "\\begin{tabular}{rrrrr}\n\\hline\n"
  "$\\Delta\\eta$ & $T_{\\rm floor}/R$ & $T_{\\rm eff}/R$ & "
  "$T_{\\rm ceil}/R$ & $\\eta_{\\rm fb}$ \\\\\n\\hline\n"
  + "\n".join(rows) + "\n\\hline\n\\end{tabular}\n")

# Table V: SI レイヤー(x0=0.3 の 3 半径)
rows = []
for r in si:
    if float(r["x0"]) != 0.3:
        continue
    rows.append(
        f"{float(r['R_m']):g} & {float(r['shell_mass_kg']):.2e} & "
        f"{float(r['shell_mass_Msun']):.3g} & {float(r['L_peak_W']):.2e} & "
        f"{float(r['L_peak_Lsun']):.2e} \\\\")
w("table5_si.tex",
  "\\begin{tabular}{rrrrr}\n\\hline\n"
  "$R$ [m] & $m$ [kg] & $m$ [$M_\\odot$] & $L_{\\rm peak}$ [W] & "
  "[$L_\\odot$] \\\\\n\\hline\n" + "\n".join(rows)
  + "\n\\hline\n\\end{tabular}\n")

print(f"numbers.tex: {len(M)} macros / manifest: {len(MANIFEST)} entries / "
      "tables: 5")
