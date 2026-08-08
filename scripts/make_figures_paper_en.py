"""論文用 EN 図(6 枚)を paper/figures/ に生成(データ経路は日本語版と同一)。

fig1←missions_tau / fig2←tiers / fig3←timeopt_bracket / fig4←sig1 / fig5←sig2 /
fig6←sig3。ラベル文字列のみ英語化(P3a §3: データ不変)。
"""
import csv
import json
import math
import pathlib
import sys

REPO = pathlib.Path(__file__).resolve().parents[1]
sys.path.insert(0, str(REPO / "src"))

import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt

from astrogation import appc_floor, catalog, frontier, kinematics, radiometry as rad, units

RES = REPO / "results"
OUT = REPO / "paper" / "figures"
OUT.mkdir(parents=True, exist_ok=True)

C = {"ceiling": "#2a78d6", "effective": "#eb6834", "floor": "#1baf7a",
     "yellow": "#eda100", "magenta": "#e87ba4",
     "dest": "#2a78d6", "side": "#1baf7a", "depart": "#eb6834",
     "ink": "#0b0b0b", "ink2": "#52514e", "grid": "#e8e7e4", "bg": "#ffffff"}
plt.rcParams.update({
    "font.family": ["DejaVu Sans"],
    "figure.facecolor": C["bg"], "axes.facecolor": C["bg"],
    "text.color": C["ink"], "axes.edgecolor": C["ink2"],
    "axes.labelcolor": C["ink"], "xtick.color": C["ink2"],
    "ytick.color": C["ink2"], "font.size": 9.5,
    "axes.grid": True, "grid.color": C["grid"], "grid.linewidth": 0.6,
    "axes.spines.top": False, "axes.spines.right": False,
    "axes.unicode_minus": False,
})

# ---- Fig 1: 50-yr contour (missions tau vs eta)
fig, ax = plt.subplots(figsize=(7.2, 4.4), dpi=200)
dest_colors = ["#2a78d6", "#eb6834", "#1baf7a", "#eda100"]
etas_f = [0.1 + 0.02 * i for i in range(600)]
a_geo = catalog.LAMBDA_BURN / catalog.R_REF_M
for (name, d_ly), col in zip(catalog.DESTINATIONS, dest_colors):
    D = units.ly_to_m(d_ly)
    taus = [units.s_to_yr(units.time_geo_to_s(
        kinematics.mission_times(D, e, a_geo, "arrive")["tau_ship"]))
        for e in etas_f]
    ax.plot(etas_f, taus, color=col, lw=2, label=f"{name} ({d_ly:g} ly)")
ax.axhline(50, color=C["ink2"], lw=1.0, ls="--")
ax.annotate(r"$\tau$ = 50 yr", xy=(0.15, 62), fontsize=8.5, color=C["ink2"])
ax.set_yscale("log")
ax.set_xlabel(r"cruise rapidity $\eta$")
ax.set_ylabel(r"ship proper time $\tau$ [yr] (log)")
ax.legend(fontsize=8.5)
fig.tight_layout()
fig.savefig(OUT / "fig1_contour.png")
plt.close(fig)

# ---- Fig 2: three-tier frontier
fig, ax = plt.subplots(figsize=(8.4, 4.6), dpi=200)
xs = [i / 1000 for i in range(10, 795)]
ax.plot(xs, [frontier.tier_bound(x, "ceiling") for x in xs],
        color=C["ceiling"], lw=2,
        label=r"ceiling [R] $\min\{\frac{1}{2}(1-x),\frac{1}{2}(\frac{4}{5}-x)\}$")
ax.plot(xs, [0.5 * (1 - x) for x in xs], color=C["ceiling"], lw=1.2, ls="--",
        alpha=0.6, label=r"kinematic ceiling $\frac{1}{2}(1-x)$ [R]")
ax.plot(list(frontier.G_LOWER_X), list(frontier.G_LOWER_VALUES),
        color=C["effective"], lw=2, marker="o", ms=6,
        label=r"$\underline{g}(x)$ [N] (no extrapolation)")
ax.plot(xs, [0.5 * (24 / 25 - x) for x in xs], color=C["ink2"], lw=1.0, ls=":",
        label=r"envelope $\frac{1}{2}(\frac{24}{25}-x)$ [H]")
ax.plot(xs, [appc_floor.c_floor_conservative(x) for x in xs],
        color=C["floor"], lw=2,
        label=r"floor $c_{\rm cons}(x)$ [R(A3)/provisional]")
ax.plot(list(frontier.C_LOWER_X), list(frontier.C_LOWER_VALUES),
        color=C["floor"], ls="none", marker="s", ms=6, mfc="none",
        label=r"$c(x)$ as printed, Eq.(73) [R]")
ax.plot(xs, [frontier.lambda_bar_dec(x) for x in xs], color=C["magenta"],
        lw=1.2, ls="-.",
        label=r"$\bar\lambda_{\rm DEC}$ (diagnostic only)")
ax.axvline(0.54, color=C["ink2"], lw=0.8, ls=":")
ax.plot([0.54], [0.13], marker="D", ms=7, color=C["ink"], ls="none", zorder=5)
ax.annotate("$x^*\\approx0.54$, $\\lambda^*\\approx0.13$\n"
            "constraint-regime crossover:\n"
            "thin-shell [N] binds left, thick-wall [R] right",
            xy=(0.54, 0.13), xytext=(0.56, 6e-3), fontsize=8, color=C["ink"],
            arrowprops=dict(arrowstyle="-", color=C["ink2"], lw=0.8))
ax.set_yscale("log")
ax.set_ylim(1e-6, 0.7)
ax.set_xlabel(r"compactness $x = 2m/R$")
ax.set_ylabel(r"$\lambda = aR$ (log)")
ax.legend(fontsize=7.2, loc="center left", bbox_to_anchor=(1.01, 0.5),
          framealpha=0.0)
fig.tight_layout()
fig.savefig(OUT / "fig2_tiers.png", bbox_inches="tight")
plt.close(fig)

# ---- Fig 3: time-optimal bracket (from CSV)
rows = list(csv.DictReader(open(RES / "timeopt_bracket.csv")))
fig, ax = plt.subplots(figsize=(7.2, 4.4), dpi=200)
for tier, label in (("floor", "floor [R(A3)/provisional]"),
                    ("effective", "effective [N]"),
                    ("ceiling", "ceiling [R] (unattainable lower bound)")):
    ds, ts = [], []
    for d in catalog.ETA_LADDER:
        for r in rows:
            if (float(r["x0"]) == 0.3 and float(r["deta"]) == d
                    and r["tier"] == tier):
                ds.append(d)
                ts.append(float(r["T_over_R"]))
    ax.plot(ds, ts, color=C[tier], lw=2, marker="o", ms=5, label=label)
ax.axvline(math.log(3) / 3, color=C["ink2"], lw=0.8, ls=":")
ax.annotate("[N]$\\to$ceiling fallback\n$\\eta_{\\rm fb}=0.366$",
            xy=(0.40, 1e7), fontsize=8, color=C["ink2"])
ax.set_xscale("log")
ax.set_yscale("log")
ax.set_xlabel(r"$\Delta\eta$ (log)")
ax.set_ylabel(r"$T/R$ (log)")
ax.legend(fontsize=8.5, loc="upper left")
fig.tight_layout()
fig.savefig(OUT / "fig3_bracket.png")
plt.close(fig)

# ---- Fig 4: arrival-mission fingerprint (schedule + burst shapes)
sig = json.loads(
    (RES / "signatures" / "sig_mission_proxima_arrive_eta1.0.json").read_text())
labels = {"dest": r"destination, $\theta=0^\circ$",
          "side": r"side-on, $\theta=90^\circ$",
          "depart": r"departure, $\theta=180^\circ$"}
fig, (axL, axR) = plt.subplots(1, 2, figsize=(9.6, 4.2), dpi=200,
                               gridspec_kw={"width_ratios": [1, 1.3]})
for tag in ("dest", "side", "depart"):
    blk = sig["angles"][tag]
    axL.stem([blk["t_peak"]], [blk["F_peak"]], linefmt=C[tag], markerfmt="o",
             basefmt=" ")
    axL.annotate(labels[tag], xy=(blk["t_peak"], blk["F_peak"]), fontsize=8,
                 color=C[tag], xytext=(5, 5), textcoords="offset points")
axL.set_yscale("log")
axL.set_ylim(1e-5, 3.0)
axL.set_xlabel(r"observer arrival time $t_{\rm obs}$ [R]")
axL.set_ylabel(r"peak $F\,D^2$ (geometric, log)")
axL.set_title("when and how bright")


def peak_run(ts, Fs):
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
    i0, i1 = peak_run(ts, Fs)
    axR.plot([t - ts[i0] for t in ts[i0:i1 + 1]],
             [f + 1e-300 for f in Fs[i0:i1 + 1]],
             color=C[tag], lw=2, label=labels[tag])
axR.set_yscale("log")
axR.set_ylim(1e-6, 3.0)
axR.set_xlabel(r"time within burst [R] ($R$=1 km: 3.3 $\mu$s per $R$)")
axR.set_title("burst waveforms")
axR.legend(fontsize=8)
fig.tight_layout()
fig.savefig(OUT / "fig4_fingerprint.png", bbox_inches="tight")
plt.close(fig)

# ---- Fig 5: observer-frame pattern evolution
fig, ax = plt.subplots(figsize=(7.2, 4.4), dpi=200)
import numpy as np
thetas = np.linspace(0.0, math.pi, 400)
m_, lam_ = 1.0, 0.19
L_ = 3 * m_ * lam_
for eta, col in ((0.0, "#2a78d6"), (1.0, "#1baf7a"), (3.0, "#eda100")):
    F = [rad.observed_flux_v(L_, m_, lam_, 1, eta,
                             0.5 * (1 - math.cos(t))) for t in thetas]
    ax.plot([math.degrees(t) for t in thetas], [f + 1e-300 for f in F],
            color=col, lw=2, label=rf"acceleration, $\eta={eta:g}$")
F = [rad.observed_flux_v(L_, m_, lam_, -1, 1.0,
                         0.5 * (1 - math.cos(t))) for t in thetas]
ax.plot([math.degrees(t) for t in thetas], [f + 1e-300 for f in F],
        color="#e34948", ls="--", lw=2,
        label=r"deceleration, $\eta=1$ (lobe forward)")
ax.set_yscale("log")
ax.set_ylim(1e-5, 1e2)
ax.set_xlabel(r"observer angle $\theta_{\rm obs}$ [deg] (0 = direction of motion)")
ax.set_ylabel(r"$F\,D^2$ (geometric, log)")
ax.legend(fontsize=8.5)
fig.tight_layout()
fig.savefig(OUT / "fig5_pattern.png")
plt.close(fig)

# ---- Fig 6: M31 deceleration flash (log-t zoom)
sig = json.loads(
    (RES / "signatures" / "sig_mission_m31_arrive_eta12.0.json").read_text())
blk = sig["angles"]["dest"]
ts, Fs = blk["t_obs"], blk["F"]
t0 = ts[Fs.index(max(Fs))]
fig, ax = plt.subplots(figsize=(7.2, 4.4), dpi=200)
pts = [(t - t0, f) for t, f in zip(ts, Fs) if t > t0 and f > 0]
ax.plot([p_[0] for p_ in pts], [p_[1] for p_ in pts], color=C["dest"], lw=2,
        marker="o", ms=3)
ax.set_xscale("log")
ax.set_yscale("log")
ax.set_xlim(1e-6, 3e2)
ax.set_ylim(1e-30, 3e4)
ax.set_xlabel(r"$t_{\rm obs} - t_{\rm peak}$ [R, log] ($R$=1 km: $10^{-6}R \approx 3.3$ ps)")
ax.set_ylabel(r"$F\,D^2$ (geometric, log)")
ax.annotate("arrival-time compression $dt_{\\rm obs}/du = e^{-\\eta}$:\n"
            "decay scale $\\sim e^{-\\eta}/(7\\lambda) \\approx 5\\times10^{-6}R$"
            " ($\\sim$15 ps at $R$=1 km)\nlow-$\\eta$ arrivals are $\\mu$s-scale",
            xy=(3e-6, 1e-10), fontsize=8.5, color=C["ink2"])
fig.tight_layout()
fig.savefig(OUT / "fig6_flash.png")
plt.close(fig)

print("EN figures: 6 ->", OUT)
