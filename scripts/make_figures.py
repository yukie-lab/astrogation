"""Phase 1 図の生成(dataviz 準拠、日本語フォント対応)。

fig2 は results/timeopt_bracket.csv を読む(再計算しない)。
実行: /Users/yukie/miniforge3/envs/warpax/bin/python scripts/make_figures.py
"""
import csv
import math
import pathlib
import sys

REPO = pathlib.Path(__file__).resolve().parents[1]
sys.path.insert(0, str(REPO / "src"))

import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt

from astrogation import appc_floor, catalog, frontier, kinematics, units

FIG = REPO / "results" / "figures"
FIG.mkdir(parents=True, exist_ok=True)

# 参照パレット(dataviz 検証済みインスタンス)。色は実体固定(tier/行き先)。
C = {"ceiling": "#2a78d6", "effective": "#eb6834", "floor": "#1baf7a",
     "yellow": "#eda100", "magenta": "#e87ba4",
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

# ---------------------------------------------------------------- 図1: 三層
fig, ax = plt.subplots(figsize=(8.6, 4.8), dpi=150)
xs = [i / 1000 for i in range(10, 795)]
ax.plot(xs, [frontier.tier_bound(x, "ceiling") for x in xs],
        color=C["ceiling"], lw=2, label="天井 [R] min(½(1−x), (4/5−x)/2)")
ax.plot(xs, [0.5 * (1 - x) for x in xs], color=C["ceiling"], lw=1.2, ls="--",
        alpha=0.6, label="運動学的天井 ½(1−x) [R]")
ax.plot(list(frontier.G_LOWER_X), list(frontier.G_LOWER_VALUES),
        color=C["effective"], lw=2, marker="o", ms=6,
        label="g̲(x) [N](S1、範囲外は禁止)")
ax.plot(xs, [0.5 * (24 / 25 - x) for x in xs], color=C["ink2"], lw=1.0, ls=":",
        label="包絡線 ½(24/25−x) [H]")
ax.plot(xs, [appc_floor.c_floor_conservative(x) for x in xs],
        color=C["floor"], lw=2, label="床 c_cons(x) [R(A3)/STOP-pending]")
ax.plot(list(frontier.C_LOWER_X), list(frontier.C_LOWER_VALUES),
        color=C["floor"], ls="none", marker="s", ms=6, mfc="none",
        label="c(x) 論文値 (73) [R]")
ax.plot(xs, [frontier.lambda_bar_dec(x) for x in xs], color=C["magenta"],
        lw=1.2, ls="-.", label="λ̄_DEC (43)(診断・拘束使用禁止)")
ax.axvline(0.54, color=C["ink2"], lw=0.8, ls=":")
ax.plot([0.54], [0.13], marker="D", ms=7, color=C["ink"], ls="none", zorder=5)
ax.annotate("x* ≈ 0.54, λ* ≈ 0.13\n拘束レジーム交差(主結果4):\n左は薄殻 g̲ [N]、右は厚壁窓 [R] が束縛",
            xy=(0.54, 0.13), xytext=(0.56, 6e-3), fontsize=8, color=C["ink"],
            arrowprops=dict(arrowstyle="-", color=C["ink2"], lw=0.8))
ax.set_yscale("log")
ax.set_ylim(1e-6, 0.7)
ax.set_xlabel("コンパクト度 x = 2m/R")
ax.set_ylabel("λ = aR(log)")
ax.set_title("三層フロンティア: 床 [R(A3)] / 実効 [N] / 天井 [R]")
ax.legend(fontsize=7.5, loc="center left", bbox_to_anchor=(1.01, 0.5),
          framealpha=0.0)
fig.tight_layout()
fig.savefig(FIG / "fig1_tiers.png")
plt.close(fig)

# ------------------------------------------- 図2: 三層区間(CSV から読む)
rows = list(csv.DictReader(open(REPO / "results" / "timeopt_bracket.csv")))
fig, ax = plt.subplots(figsize=(7.2, 4.6), dpi=150)
for tier, label in (("floor", "床 [R(A3)/STOP-pending]"), ("effective", "実効 [N]"),
                    ("ceiling", "天井 [R](到達不能下限)")):
    ds, ts = [], []
    for d in catalog.ETA_LADDER:
        for r in rows:
            if (float(r["x0"]) == 0.3 and float(r["deta"]) == d
                    and r["tier"] == tier):
                ds.append(d)
                ts.append(float(r["T_over_R"]))
    ax.plot(ds, ts, color=C[tier], lw=2, marker="o", ms=5, label=label)
ax.axvline(math.log(3) / 3, color=C["ink2"], lw=0.8, ls=":")
ax.annotate("[N]→天井フォールバック\nη_fb = 0.366", xy=(0.40, 1e7), fontsize=8,
            color=C["ink2"])
ax.set_xscale("log")
ax.set_yscale("log")
ax.set_xlabel("Δη(log)")
ax.set_ylabel("T / R(log)")
ax.set_title("フロンティア騎乗の最短時間 — 三層区間(x₀ = 0.3)")
ax.legend(fontsize=8.5, loc="upper left")
fig.tight_layout()
fig.savefig(FIG / "fig2_timeopt_bracket.png")
plt.close(fig)

# ------------------------------------------- 図3: 表B 等高線
fig, ax = plt.subplots(figsize=(7.2, 4.6), dpi=150)
dest_colors = ["#2a78d6", "#eb6834", "#1baf7a", "#eda100"]
etas_f = [0.1 + 0.02 * i for i in range(600)]
a_geo = catalog.LAMBDA_BURN / catalog.R_REF_M
for (name, d_ly), col in zip(catalog.DESTINATIONS, dest_colors):
    D = units.ly_to_m(d_ly)
    taus = [units.s_to_yr(units.time_geo_to_s(
        kinematics.mission_times(D, e, a_geo, "arrive")["tau_ship"]))
        for e in etas_f]
    ax.plot(etas_f, taus, color=col, lw=2, label=f"{name}({d_ly:g} ly)")
ax.axhline(50, color=C["ink2"], lw=1.0, ls="--")
ax.annotate("τ = 50 yr", xy=(0.15, 62), fontsize=8.5, color=C["ink2"])
ax.set_yscale("log")
ax.set_xlabel("巡航ラピディティ η")
ax.set_ylabel("船内固有時間 τ [yr](log)")
ax.set_title("到着ミッションの船内固有時間 — 50 年等高線(表B)")
ax.legend(fontsize=8.5)
fig.tight_layout()
fig.savefig(FIG / "fig3_missions_tau.png")
plt.close(fig)

print("図 3 枚を再生成:", FIG)
