"""Phase 2 署名カタログ生成(2-2, 2-3, 2-5, 2-6)。

入力: results/mission_profiles + results/timeopt_profiles(再計算禁止)。
出力: results/signatures/(プロファイル×観測配置の F(t_obs)、要約 CSV、
G3 ログ、図、スケーリング表)。
観測配置: v_obs = sin²(θ_obs/2) ∈ {0(正面=目的地), ½(側方), 1(後方=出発地)}。
G3 許容: ミッション 1e-8 / 騎乗 2e-6(台帳 L45a のクラス別文書化値)。
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

from astrogation import radiometry as rad
from astrogation import control, units

RES = REPO / "results"
SIG = RES / "signatures"
FIG = SIG / "figures"
for d in (SIG, FIG):
    d.mkdir(parents=True, exist_ok=True)

COMMIT = subprocess.run(["git", "rev-parse", "--short", "HEAD"], cwd=REPO,
                        capture_output=True, text=True).stdout.strip()
DIRTY = subprocess.run(["git", "status", "--porcelain"], cwd=REPO,
                       capture_output=True, text=True).stdout.strip() != ""
COMMIT += "+dirty" if DIRTY else ""

V_OBS = (("dest", 0.0), ("side", 0.5), ("depart", 1.0))
TOL = {"mission": 1e-8, "ride": 2e-6}
G3_FAILURES = []
rows_summary = []


def load(fp):
    d = json.loads(fp.read_text())
    if "grid" in d:
        g = d["grid"]
        n = len(g["u"])
        deta_du = []
        for i in range(n):
            if g["a"][i] == 0.0:
                deta_du.append(0.0)
            else:
                lo, hi = max(i - 1, 0), min(i + 1, n - 1)
                sgn = 1.0 if g["eta_signed"][hi] >= g["eta_signed"][lo] else -1.0
                deta_du.append(sgn * g["a"][i])
        return {"kind": "mission", "meta": d["meta"], "u": g["u"], "L": g["L"],
                "m": g["m"], "a": g["a"], "eta": g["eta_signed"],
                "thrust": g["thrust_sign"], "deta_du": deta_du,
                "deta_tot": d["meta"]["delta_eta_total"],
                "name": fp.stem}
    return {"kind": "ride", "meta": {"tier": d["tier"], "x0": d["x0"],
                                     "deta": d["deta"],
                                     "authority": d["authority"]},
            "u": d["u"], "L": d["L"], "m": d["m"], "a": d["a"],
            "eta": d["eta"], "thrust": d["thrust_sign"], "deta_du": d["lambda"],
            "deta_tot": d["deta"], "name": fp.stem}


def flux_series(p, v_obs):
    return [rad.observed_flux_v(p["L"][i], p["m"][i], p["a"][i],
                                p["thrust"][i], p["eta"][i], v_obs)
            for i in range(len(p["u"]))]


print("署名カタログ生成 ...")
files = sorted((RES / "mission_profiles").glob("*.json")) + \
    sorted((RES / "timeopt_profiles").glob("*.json"))
assert len(files) == 189
n_rows = 0
for fp in files:
    p = load(fp)
    out = {"meta": {**p["meta"], "kind": p["kind"], "commit": COMMIT,
                    "units": "幾何・R=1(ミッションは m₀=1 正規化)。"
                             "F は D=1 の δ⁴n²(SI: ×c⁵/G ÷ D_SI²)",
                    "authority": "パターン[R] 写像[R-standard] "
                                 "(騎乗 t_obs はグリッド情報限界 2e-6、L45a)"},
           "angles": {}}
    # C15(エネルギー閉合、自動適用)
    m0 = p["m"][0]
    fluence = rad.fluence_exact(p["u"], p["L"], p["m"], p["a"])
    tsi = m0 * (1.0 - control.tsiolkovsky_ratio(p["deta_tot"]))
    c15_rel = abs(fluence - tsi) / max(tsi, 1e-300)
    if c15_rel > 1e-10:
        G3_FAILURES.append((p["name"], "C15", c15_rel))
        continue
    for tag, v in V_OBS:
        mu = 1.0 - 2.0 * v
        if p["kind"] == "mission":
            t_a = rad.t_obs_mission_closed(p["u"], p["eta"], p["a"],
                                           p["thrust"], mu)
            t_b = rad.t_obs_path_u(p["u"], p["eta"], p["deta_du"], mu)
        else:
            t_a = rad.t_obs_path_u(p["u"], p["eta"], p["deta_du"], mu)
            t_b = rad.t_obs_path_eta(p["u"], p["eta"], p["deta_du"], mu)
        scale = max(1.0, abs(t_a[-1]))
        g3_rel = abs(t_a[-1] - t_b[-1]) / scale
        if g3_rel > TOL[p["kind"]]:
            G3_FAILURES.append((p["name"], f"map@{tag}", g3_rel))
            continue
        F = flux_series(p, v)
        f_peak = max(F)
        i_peak = F.index(f_peak)
        out["angles"][tag] = {
            "v_obs": v, "t_obs": t_a, "F": F,
            "F_peak": f_peak, "t_peak": t_a[i_peak],
            "g3_map_rel": g3_rel,
        }
        rows_summary.append({
            "profile": p["name"], "kind": p["kind"], "angle": tag,
            "F_peak_geo": f_peak, "t_peak_R": t_a[i_peak],
            "t_span_R": t_a[-1], "c15_rel": c15_rel, "g3_map_rel": g3_rel,
        })
        n_rows += 1
    with open(SIG / f"sig_{p['name']}.json", "w") as f:
        json.dump(out, f)

print(f"  {n_rows} 行(欠番 {len(G3_FAILURES)})")

with open(SIG / "signature_summary.csv", "w", newline="") as f:
    w = csv.DictWriter(f, fieldnames=["profile", "kind", "angle", "F_peak_geo",
                                      "t_peak_R", "t_span_R", "c15_rel",
                                      "g3_map_rel"])
    w.writeheader()
    for r in rows_summary:
        w.writerow(r)

with open(SIG / "g3_log.md", "w") as f:
    f.write("# 署名カタログ G3 ログ\n\n")
    f.write(f"生成コミット: `{COMMIT}`\n\n")
    f.write(f"- 行数: {n_rows}(189 プロファイル × 3 配置)\n")
    f.write(f"- C15 エネルギー閉合: 全プロファイル < 1e-10 で自動適用\n")
    f.write(f"- 写像 G3 許容: ミッション 1e-8 / 騎乗 2e-6(L45a)\n")
    f.write(f"- 欠番: {len(G3_FAILURES)}\n")
    worst_m = max((r["g3_map_rel"] for r in rows_summary
                   if r["kind"] == "mission"), default=0.0)
    worst_r = max((r["g3_map_rel"] for r in rows_summary
                   if r["kind"] == "ride"), default=0.0)
    f.write(f"- 写像最悪相対誤差: mission {worst_m:.2e} / ride {worst_r:.2e}\n")
    for name, tag, rel in G3_FAILURES:
        f.write(f"- 欠番: {name} {tag} {rel:.2e}\n")

if G3_FAILURES:
    print("STOP: 署名 G3 不一致", file=sys.stderr)
    sys.exit(2)

# ==================================================== スケーリング表(2-3)
print("スケーリング表 ...")
PW = units.PLANCK_POWER_SI
with open(SIG / "scaling_table.md", "w") as f:
    f.write("# 署名スケーリング表(2-3)\n\n")
    f.write(f"生成コミット: `{COMMIT}`。**観測装置の性能予測は含まない**"
            "(CLAUDE.md §7 — スケーリングと桁まで)。\n\n")
    f.write("## 錨(全て [R]/[R-standard])\n\n")
    f.write("- 静止系ピーク光度 L_peak = 1.5·x·λ·(c⁵/G)。x=0.3, λ=0.19 → "
            f"{1.5*0.3*0.19:.4f}·c⁵/G = {units.power_geo_to_si(1.5*0.3*0.19):.2e} W "
            f"= {units.power_si_to_lsun(units.power_geo_to_si(1.5*0.3*0.19)):.1e} L☉\n")
    f.write("- 受信フラックス F = δ⁴·n²·(c⁵/G)/D²(δ⁴: 相対論的ビーミング)。"
            "減速バーン正面(目的地)では δ = e^η\n")
    f.write("- 持続時間(観測者系): Δt_obs ≈ (η/λ)·R/c·⟨1/δ⟩ — R = 1 km、"
            "λ = 0.19、Δη = 0.24 で ~4 μs(正面はさらに e^(−η) 圧縮)\n\n")
    f.write("## 距離スケーリング(等方等価 L_iso = δ⁴·4π n²·c⁵/G、x=0.3・λ=0.19 飽和後方ローブ正面)\n\n")
    f.write("| η(減速正面) | δ⁴ | F·D² [W] | F@1 kpc [W/m²] | @1 Mpc | @1 Gpc |\n")
    f.write("|---|---|---|---|---|---|\n")
    L_geo = 1.5 * 0.3 * 0.19
    n2_rear = 2 * L_geo / (4 * math.pi)   # 飽和後方極 (L+3ma)/4π = 2L/4π
    for eta in (0.24, 1.0, 3.0, 5.0):
        d4 = math.exp(4 * eta)
        fd2 = d4 * n2_rear * PW
        for D_name, D_m in (("1 kpc", units.ly_to_m(3261.6)),
                            ("1 Mpc", units.ly_to_m(3.2616e6)),
                            ("1 Gpc", units.ly_to_m(3.2616e9))):
            pass
        f1 = fd2 / units.ly_to_m(3261.6) ** 2
        f2 = fd2 / units.ly_to_m(3.2616e6) ** 2
        f3 = fd2 / units.ly_to_m(3.2616e9) ** 2
        f.write(f"| {eta} | {d4:.2e} | {fd2:.2e} | {f1:.2e} | {f2:.2e} | {f3:.2e} |\n")
    f.write("\n物理錨(比較用・装置非依存): 太陽定数 1.36e3 W/m²、"
            "0 等星のボロメトリックフラックス ~2.5e-8 W/m²(桁の目安)。\n\n")
    f.write("## パラメータ化シナリオ(【シナリオ: 黒体仮定】— 仮定ラベル)\n\n")
    f.write("排気スペクトルは主張しない(ボロメトリックのみ [R])。"
            "**仮に**放射面 R = 1 km の黒体とみなすなら "
            "T = (L/4πR²σ)^¼ ≈ 8×10¹² K(硬ガンマ域)— これは仮定であり、"
            "実際のスペクトルは排気の微視物理(不主張)に依存する。\n")

# ==================================================== 図(2-6)
print("図 ...")
C = {"dest": "#2a78d6", "side": "#1baf7a", "depart": "#eb6834",
     "ink": "#0b0b0b", "ink2": "#52514e", "grid": "#e8e7e4", "bg": "#fcfcfb"}
plt.rcParams.update({
    "font.family": ["Hiragino Sans", "Hiragino Kaku Gothic ProN", "DejaVu Sans"],
    "figure.facecolor": C["bg"], "axes.facecolor": C["bg"],
    "text.color": C["ink"], "axes.edgecolor": C["ink2"],
    "axes.labelcolor": C["ink"], "xtick.color": C["ink2"],
    "ytick.color": C["ink2"], "font.size": 9.5,
    "axes.grid": True, "grid.color": C["grid"], "grid.linewidth": 0.6,
    "axes.spines.top": False, "axes.spines.right": False,
    "axes.unicode_minus": False,
})

# 図1: 到着ミッション(プロキシマ, η=1)— 左: 到着スケジュール / 右: バースト波形
sig = json.loads((SIG / "sig_mission_proxima_arrive_eta1.0.json").read_text())
fig, (axL, axR) = plt.subplots(1, 2, figsize=(9.6, 4.4), dpi=150,
                               gridspec_kw={"width_ratios": [1, 1.3]})
labels = {"dest": "目的地正面 θ=0°", "side": "側方 θ=90°",
          "depart": "出発地 θ=180°"}
for tag in ("dest", "side", "depart"):
    blk = sig["angles"][tag]
    axL.stem([blk["t_peak"]], [blk["F_peak"]], linefmt=C[tag], markerfmt="o",
             basefmt=" ")
    axL.annotate(labels[tag], xy=(blk["t_peak"], blk["F_peak"]), fontsize=8,
                 color=C[tag], xytext=(5, 5), textcoords="offset points")
axL.set_yscale("log")
axL.set_ylim(1e-5, 3.0)
axL.set_xlabel("観測者到着時間 t_obs [R]")
axL.set_ylabel("ピーク F·D²(幾何、log)")
axL.set_title("いつ・どの強さで光るか")
def _peak_run(ts, Fs):
    """ピークを含む連続非ゼロ区間(側方観測者は加速・減速の 2 バーストを見る)。"""
    i_pk = Fs.index(max(Fs))
    i0 = i_pk
    while i0 > 0 and Fs[i0 - 1] > 0:
        i0 -= 1
    i1 = i_pk
    while i1 < len(Fs) - 1 and Fs[i1 + 1] > 0:
        i1 += 1
    return i0, i1


for tag in ("dest", "side", "depart"):
    blk = sig["angles"][tag]
    ts, Fs = blk["t_obs"], blk["F"]
    i0, i1 = _peak_run(ts, Fs)
    t_loc = [t - ts[i0] for t in ts[i0:i1 + 1]]
    F_loc = [f + 1e-300 for f in Fs[i0:i1 + 1]]
    axR.plot(t_loc, F_loc, color=C[tag], lw=2, label=labels[tag])
axR.set_yscale("log")
axR.set_ylim(1e-6, 3.0)
axR.set_xlabel("バースト内相対時間 [R](SI: ×R/c — R=1 km で 3.3 μs/R)")
axR.set_title("バースト波形(加速+減速の指紋)")
axR.legend(fontsize=8)
fig.suptitle("到着ミッションの署名指紋(プロキシマ、η=1): 減速フラッシュの非対称", y=1.0)
fig.tight_layout()
fig.savefig(FIG / "sig1_lightcurve_arrive.png", bbox_inches="tight")
plt.close(fig)

# 図2: 角度パターンの進化(加速・減速、η 数点)
fig, ax = plt.subplots(figsize=(7.6, 4.6), dpi=150)
import numpy as np
thetas = np.linspace(0.0, math.pi, 400)
m_, lam_ = 1.0, 0.19
L_ = 3 * m_ * lam_
for eta, col, ls in ((0.0, "#2a78d6", "-"), (1.0, "#1baf7a", "-"),
                     (3.0, "#eda100", "-")):
    F = [rad.observed_flux_v(L_, m_, lam_, 1, eta,
                             0.5 * (1 - math.cos(t))) for t in thetas]
    ax.plot([math.degrees(t) for t in thetas], [f + 1e-300 for f in F],
            color=col, ls=ls, lw=2, label=f"加速 η={eta}")
F = [rad.observed_flux_v(L_, m_, lam_, -1, 1.0,
                         0.5 * (1 - math.cos(t))) for t in thetas]
ax.plot([math.degrees(t) for t in thetas], [f + 1e-300 for f in F],
        color="#e34948", ls="--", lw=2, label="減速 η=1(ローブ前方=目的地向き)")
ax.set_yscale("log")
ax.set_ylim(1e-5, 1e2)
ax.set_xlabel("観測角 θ_obs [deg](0 = 進行方向/目的地)")
ax.set_ylabel("F·D²(幾何単位、log)")
ax.set_title("観測者系角度パターンの進化(飽和 Kinnersley 双極子+ビーミング)")
ax.legend(fontsize=8.5)
fig.tight_layout()
fig.savefig(FIG / "sig2_pattern_evolution.png")
plt.close(fig)

# 図3: M31 到着 η=12 の減速フラッシュ(目的地正面、ズーム)
sig = json.loads((SIG / "sig_mission_m31_arrive_eta12.0.json").read_text())
blk = sig["angles"]["dest"]
ts, Fs = blk["t_obs"], blk["F"]
i_pk = Fs.index(max(Fs))
t0 = ts[i_pk]
fig, ax = plt.subplots(figsize=(7.6, 4.6), dpi=150)
pts = [(t - t0, f) for t, f in zip(ts, Fs) if t > t0 and f > 0]
ax.plot([p_[0] for p_ in pts], [p_[1] for p_ in pts], color=C["dest"], lw=2,
        marker="o", ms=3)
ax.set_xscale("log")
ax.set_yscale("log")
ax.set_xlim(1e-6, 3e2)
ax.set_ylim(1e-30, 3e4)
ax.set_xlabel("t_obs − t_peak [R、log](R = 1 km: 1e-6 R ≈ 3.3 ps)")
ax.set_ylabel("F·D²(幾何、log)")
ax.set_title("M31 到着 η=12: 目的地正面の減速フラッシュ(δ⁴ = e^(4η) 増幅、"
             f"ピーク {max(Fs):.2e})")
ax.annotate("到着時間圧縮 dt_obs/du = e^(−η):\n減衰スケール ~e^(−η)/(7λ) ≈ 5e-6 R"
            "(R=1 km で ~15 ps)\n低 η の到着(η≤1)は μs 級",
            xy=(3e-6, 1e-10), fontsize=8.5, color=C["ink2"])
fig.tight_layout()
fig.savefig(FIG / "sig3_decel_flash.png")
plt.close(fig)

print("完了: results/signatures/ 一式")
