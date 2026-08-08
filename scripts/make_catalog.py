"""Phase 1 カタログ一式の生成(PHASE_1.md 1-2〜1-7)。

実行: /Users/yukie/miniforge3/envs/warpax/bin/python scripts/make_catalog.py
出力: results/ 以下(表A/表B/η50/時間最適/ミッションプロファイル/SI/G3ログ/図)。
G3 不一致行は欠番+理由記録、1 行でも発生したら STOP(exit 2)。
"""
import csv
import json
import math
import pathlib
import subprocess
import sys

REPO = pathlib.Path(__file__).resolve().parents[1]
sys.path.insert(0, str(REPO / "src"))

import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt

from astrogation import appc_floor, catalog, frontier, kinematics, timeopt, units

RES = REPO / "results"
FIG = RES / "figures"
PROF_T = RES / "timeopt_profiles"
PROF_M = RES / "mission_profiles"
for d in (RES, FIG, PROF_T, PROF_M):
    d.mkdir(parents=True, exist_ok=True)


def git_state():
    h = subprocess.run(["git", "rev-parse", "HEAD"], cwd=REPO,
                       capture_output=True, text=True).stdout.strip()
    dirty = subprocess.run(["git", "status", "--porcelain"], cwd=REPO,
                           capture_output=True, text=True).stdout.strip() != ""
    return h + ("+dirty" if dirty else "")


COMMIT = git_state()
G3_FAILURES = []


def write_csv(path, rows, fields):
    with open(path, "w", newline="") as f:
        w = csv.DictWriter(f, fieldnames=fields, extrasaction="ignore")
        w.writeheader()
        for r in rows:
            w.writerow(r)


# ================================================================ 表A
print("表A ...")
ta = catalog.table_a_rows()
for r in ta:
    if not r["g3"]["ok"]:
        G3_FAILURES.append(("tableA", r["eta"], r["g3"]))
write_csv(RES / "tableA.csv", [
    {**r, "g3_mass_rel": r["g3"]["mass_rel"], "g3_dist_rel": r["g3"]["dist_rel"]}
    for r in ta],
    ["eta", "beta", "gamma", "mf_over_m0", "radiated_fraction",
     "ideal_photon_mf_m0", "seat_price_e2eta", "authority",
     "g3_mass_rel", "g3_dist_rel"])
with open(RES / "tableA.md", "w") as f:
    f.write("# 表A — ラピディティ階段(行き先非依存・全行 [R])\n\n")
    f.write(f"生成コミット: `{COMMIT}`。燃料は距離非依存(L6/(15))。"
            "Füzfa 比較: 理想光子ロケット e^(−η)、座席の値段 = e^(2η)(L40)。\n\n")
    f.write("| η | β | γ | m_f/m₀ | 放射率 | 理想 e^(−η) | 座席の値段 e^(2η) |\n")
    f.write("|---|---|---|---|---|---|---|\n")
    for r in ta:
        f.write(f"| {r['eta']} | {r['beta']:.6f} | {r['gamma']:.4f} "
                f"| {r['mf_over_m0']:.3e} | {r['radiated_fraction']*100:.1f}% "
                f"| {r['ideal_photon_mf_m0']:.3e} | {r['seat_price_e2eta']:.3e} |\n")
    f.write("\n全行 [R]・G3 照合済(質量: 閉形式 vs ODE、距離: arccosh vs Δη)。\n")

# ================================================================ 表B
print("表B ...")
tb = catalog.table_b_rows()
for r in tb:
    if r.get("feasible") and not r["g3"]["ok"]:
        G3_FAILURES.append(("tableB", (r["dest"], r["maneuver"], r["eta"]), r["g3"]))
write_csv(RES / "tableB.csv", [
    {**r, **{f"g3_{k}": v for k, v in r.get("g3", {}).items()}}
    for r in tb if r.get("feasible")],
    ["dest", "dist_ly", "maneuver", "eta", "delta_eta_total", "mf_over_m0",
     "t_earth_yr", "tau_ship_yr", "burn_t_earth_s", "authority",
     "g3_t_rel", "g3_tau_rel", "g3_dist_rel"])
e50 = catalog.eta50_rows()
write_csv(RES / "tableB_eta50.csv", e50,
          ["dest", "maneuver", "eta_50yr", "delta_eta_total", "mf_over_m0",
           "authority"])
with open(RES / "tableB.md", "w") as f:
    f.write("# 表B — ミッション表(4 行き先 × 3 機動型 × η 階段)\n\n")
    f.write(f"生成コミット: `{COMMIT}`。バーン規約 A4(λ=0.19 [N]@x₀=0.3、"
            "R_ref=1 km — バーン時間は全行で数秒以下、時間は巡航支配)。\n\n")
    for name, d_ly in catalog.DESTINATIONS:
        f.write(f"\n## {name}({d_ly} ly)\n\n")
        f.write("| 機動 | η | Δη計 | m_f/m₀ | 地球時間 [yr] | 船内時間 [yr] |\n")
        f.write("|---|---|---|---|---|---|\n")
        for r in tb:
            if r.get("dest") == name and r.get("feasible"):
                f.write(f"| {r['maneuver']} | {r['eta']} | {r['delta_eta_total']}"
                        f" | {r['mf_over_m0']:.3e} | {r['t_earth_yr']:.4g} "
                        f"| {r['tau_ship_yr']:.4g} |\n")
    f.write("\n## 固有時間 50 年の等高線(η しきい値)\n\n")
    f.write("| 行き先 | 機動 | η(τ=50yr) | Δη計 | m_f/m₀ |\n|---|---|---|---|---|\n")
    for r in e50:
        f.write(f"| {r['dest']} | {r['maneuver']} | {r['eta_50yr']:.3f} "
                f"| {r['delta_eta_total']:.3f} | {r['mf_over_m0']:.3e} |\n")

# ==================================================== 時間最適(1-4)
print("時間最適(81 プロファイル、G3 ODE 込み — 数分)...")
to_rows = catalog.timeopt_rows()
for r in to_rows:
    if not r["g3"]["ok"]:
        G3_FAILURES.append(("timeopt", (r["x0"], r["deta"], r["tier"]), r["g3"]))
write_csv(RES / "timeopt_bracket.csv", [
    {**r, "g3_T_rel": r["g3"]["T_rel"], "g3_xend_rel": r["g3"]["xend_rel"]}
    for r in to_rows],
    ["x0", "deta", "tier", "T_over_R", "authority", "fallback_eta", "n_arcs",
     "g3_T_rel", "g3_xend_rel"])
for r in to_rows:
    prof = timeopt.ride_profile(r["x0"], r["deta"], r["tier"], n=800)
    prof["meta_commit"] = COMMIT
    prof["g3"] = r["g3"]
    prof["arcs"] = r["arcs"]
    name = f"ride_x{r['x0']:.1f}_deta{r['deta']}_{r['tier']}.json"
    with open(PROF_T / name, "w") as f:
        json.dump(prof, f)

# 三層区間の md(x₀=0.3 の代表)
with open(RES / "timeopt_bracket.md", "w") as f:
    f.write("# 時間最適プロファイル — 三層区間(フロンティア騎乗、v3 Thm 8(ii))\n\n")
    f.write(f"生成コミット: `{COMMIT}`。T は R 単位(SI: ×R/c)。"
            "床 [R(A3)/STOP-pending] ≥ 実効 [N] ≥ 天井 [R](天井は到達不能下限)。\n\n")
    f.write("## x₀ = 0.3\n\n| Δη | T_floor/R | T_eff/R | T_ceil/R | η_fb |\n"
            "|---|---|---|---|---|\n")
    for deta in catalog.ETA_LADDER:
        row = {r["tier"]: r for r in to_rows
               if r["x0"] == 0.3 and r["deta"] == deta}
        fb = row["effective"]["fallback_eta"]
        fb_s = f"{fb:.3f}" if (fb is not None and fb < deta) else "—"
        f.write(f"| {deta} | {row['floor']['T_over_R']:.4g} "
                f"| {row['effective']['T_over_R']:.4g} "
                f"| {row['ceiling']['T_over_R']:.4g} | {fb_s} |\n")

# ==================================================== ミッションプロファイル(1-7)
print("ミッションプロファイル ...")
n_prof = 0
for name, d_ly in catalog.DESTINATIONS:
    for man in catalog.MANEUVERS:
        for eta in catalog.ETA_LADDER:
            p = catalog.mission_profile(name, d_ly, eta, man)
            if p is None:
                continue
            if not p["meta"]["g3"]["ok"]:
                G3_FAILURES.append(("mission", (name, man, eta), p["meta"]["g3"]))
            p["meta"]["commit"] = COMMIT
            fn = (f"mission_{name.split()[0].replace('*','').lower()}"
                  f"_{man}_eta{eta}.json")
            with open(PROF_M / fn, "w") as f:
                json.dump(p, f)
            n_prof += 1
print(f"  {n_prof} ファイル")

# ==================================================== SI レイヤー(1-5)
print("SI レイヤー ...")
si = catalog.si_layer_rows()
write_csv(RES / "si_layer.csv", si,
          ["R_m", "x0", "shell_mass_kg", "shell_mass_Mearth", "shell_mass_Msun",
           "lambda_eff", "L_peak_W", "L_peak_Lsun",
           "burn_u_seconds_per_unit_rapidity", "authority"])
with open(RES / "si_layer.md", "w") as f:
    f.write("# SI 正直レイヤー(R = 100 m / 1 km / 10 km)\n\n")
    f.write("換算は units.py(C7 認証済み)のみ。L_peak = 1.5 x λ(飽和・実効 tier)。\n\n")
    f.write("| R | x₀ | 殻質量 [kg] | [M⊕] | [M☉] | L_peak [W] | [L☉] |\n")
    f.write("|---|---|---|---|---|---|---|\n")
    for r in si:
        f.write(f"| {r['R_m']:.0f} m | {r['x0']} | {r['shell_mass_kg']:.2e} "
                f"| {r['shell_mass_Mearth']:.3g} | {r['shell_mass_Msun']:.3g} "
                f"| {r['L_peak_W']:.2e} | {r['L_peak_Lsun']:.2e} |\n")

# ==================================================== G3 ログ(1-6)
n_total = len(ta) + sum(1 for r in tb if r.get("feasible")) + len(to_rows) + n_prof
with open(RES / "g3_log.md", "w") as f:
    f.write("# G3 照合ログ(全行二経路、許容 1e-8)\n\n")
    f.write(f"生成コミット: `{COMMIT}`\n\n")
    f.write(f"- 照合行数: {n_total}(表A {len(ta)} / 表B "
            f"{sum(1 for r in tb if r.get('feasible'))} / 時間最適 {len(to_rows)} "
            f"/ ミッション {n_prof})\n")
    f.write(f"- 不一致(欠番): {len(G3_FAILURES)}\n")
    worst = {}
    for r in ta:
        worst["tableA_mass"] = max(worst.get("tableA_mass", 0), r["g3"]["mass_rel"])
    for r in tb:
        if r.get("feasible"):
            worst["tableB_t"] = max(worst.get("tableB_t", 0), r["g3"]["t_rel"])
            worst["tableB_tau"] = max(worst.get("tableB_tau", 0), r["g3"]["tau_rel"])
    for r in to_rows:
        worst["timeopt_T"] = max(worst.get("timeopt_T", 0), r["g3"]["T_rel"])
        worst["timeopt_xend"] = max(worst.get("timeopt_xend", 0), r["g3"]["xend_rel"])
    f.write("- 最悪相対誤差: " +
            ", ".join(f"{k}={v:.2e}" for k, v in sorted(worst.items())) + "\n")
    if G3_FAILURES:
        f.write("\n## 欠番一覧\n\n")
        for tag, key, g3 in G3_FAILURES:
            f.write(f"- {tag} {key}: {g3}\n")

if G3_FAILURES:
    print(f"STOP: G3 不一致 {len(G3_FAILURES)} 行(CLAUDE.md §8-2)", file=sys.stderr)
    sys.exit(2)

# ==================================================== 図(make_figures.py に委譲)
print("図 ...")
import subprocess
subprocess.run([sys.executable, str(REPO / "scripts" / "make_figures.py")],
               check=True)

print("完了: results/ 一式生成")
