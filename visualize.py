#!/usr/bin/env python3
"""Generate the chart set for the report (one+ per section) into charts/.

Pure matplotlib; reads the artifacts produced by the analysis pipeline.
"""

import json
import os
import re
from collections import Counter

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd

OUT = "charts"
os.makedirs(OUT, exist_ok=True)
plt.rcParams.update({"figure.dpi": 130, "font.size": 10,
                     "axes.spines.top": False, "axes.spines.right": False,
                     "axes.titleweight": "bold", "figure.autolayout": True})

INK = "#1b2a4a"; ACCENT = "#3b6ea5"; HOT = "#d1495b"; GOOD = "#2a9d8f"
GREY = "#9aa6b2"; WARM = "#e29578"
NON_SPONSOR = {"Finalist", "???", "Unknown"}

stats = json.load(open("analysis_stats.json"))
clusters = json.load(open("cluster_summaries.json"))
subs = json.load(open("subcluster_summaries.json"))
alpha8 = json.load(open("sponsor_alpha.json"))
df = pd.read_csv("ethglobal_projects_enriched.csv")
df["won"] = df["prize_count"] > 0
AI = "AI agents & autonomous assistants"


def save(fig, name, caption):
    fig.text(0.005, 0.005, caption, fontsize=7, color=GREY, ha="left", va="bottom")
    fig.savefig(f"{OUT}/{name}", bbox_inches="tight")
    plt.close(fig)
    print(f"  wrote {OUT}/{name}")


# §1 theme sizes
def chart_themes():
    c = sorted(clusters, key=lambda x: x["size"])
    fig, ax = plt.subplots(figsize=(9, 6))
    y = range(len(c))
    ax.barh(list(y), [x["size"] for x in c], color=ACCENT)
    ax.set_yticks(list(y)); ax.set_yticklabels([x["theme_label"] for x in c])
    for i, x in enumerate(c):
        ax.text(x["size"] + 8, i, f"{x['size']} ({x['share']*100:.0f}%)", va="center", fontsize=8)
    ax.set_xlabel("projects"); ax.set_xlim(0, 1300)
    ax.set_title("§1  Project themes by size (n=8,200)")
    save(fig, "01_theme_sizes.png", "ETHGlobal showcase projects · embeddings + KMeans (k=14)")


# §2 NFT→AI rotation over time
def chart_rotation():
    sb = stats["tech"]["share_by_bucket"]
    series = {"NFT / collectibles": HOT, "AI / agents": GOOD,
              "Stablecoins / payments": ACCENT, "DeFi / trading": INK,
              "DAO / governance": GREY, "x402 / agentic payments": WARM}
    x = range(1, 7)
    fig, ax = plt.subplots(figsize=(9, 5.5))
    for tag, col in series.items():
        ax.plot(list(x), [sb[str(b)][tag] * 100 for b in x], marker="o",
                color=col, lw=2.2, label=tag.split(" /")[0])
    ax.set_xticks(list(x)); ax.set_xlabel("time bucket  (oldest → newest)")
    ax.set_ylabel("% of projects in bucket")
    ax.set_title("§2  The NFT → AI rotation (tech mentions by era)")
    ax.legend(frameon=False, fontsize=8, ncol=2)
    ax.annotate("NFTs collapse", (3, 29.5), (3.1, 34), color=HOT, fontsize=8,
                arrowprops=dict(arrowstyle="->", color=HOT))
    ax.annotate("agents explode", (4, 40.5), (2.6, 41), color=GOOD, fontsize=8,
                arrowprops=dict(arrowstyle="->", color=GOOD))
    save(fig, "02_nft_ai_rotation.png", "share = % of bucket's projects whose description matches the tag")


# §3 overall tech/buzzwords
def chart_tech():
    sh = list(stats["tech"]["overall_share"].items())[:14][::-1]
    fig, ax = plt.subplots(figsize=(9, 6))
    ax.barh([t for t, _ in sh], [v * 100 for _, v in sh], color=ACCENT)
    for i, (_, v) in enumerate(sh):
        ax.text(v * 100 + 0.2, i, f"{v*100:.1f}%", va="center", fontsize=8)
    ax.set_xlabel("% of all projects"); ax.set_xlim(0, 22)
    ax.set_title("§3  Most-mentioned technologies & primitives")
    save(fig, "03_tech_overall.png", "lexicon match across all 8,200 descriptions")


# §4 outlier distribution
def chart_outliers():
    sims = df["centroid_sim"].dropna()
    thr = df.loc[df["is_outlier"], "centroid_sim"].max()
    fig, ax = plt.subplots(figsize=(9, 5))
    ax.hist(sims, bins=60, color=ACCENT)
    ax.axvline(thr, color=HOT, ls="--", lw=1.5)
    ax.text(thr, ax.get_ylim()[1] * 0.9, f"  outlier cut ≤ {thr:.2f}\n  ({int(df['is_outlier'].sum())} projects)",
            color=HOT, fontsize=8, va="top")
    ax.set_xlabel("cosine similarity to theme centroid"); ax.set_ylabel("projects")
    ax.set_title("§4  Outliers — the long tail of novelty (and junk)")
    save(fig, "04_outliers.png", "low similarity = doesn't fit any theme")


# §5 sub-themes
SUBLABELS = json.load(open("subtheme_labels.json"))


def _wrap(s, n=26):
    return s if len(s) <= n else s[:n - 1] + "…"


def chart_subthemes():
    fig, axes = plt.subplots(1, 2, figsize=(13, 4.6))
    for ax, (theme, info), col in zip(axes, subs.items(), (HOT, ACCENT)):
        sc = sorted(info["subclusters"], key=lambda s: s["size"])
        ax.barh(range(len(sc)), [s["size"] for s in sc], color=col)
        ax.set_yticks(range(len(sc)))
        ax.set_yticklabels([_wrap(SUBLABELS.get(s["subcluster"], s["subcluster"])) for s in sc],
                           fontsize=8)
        ax.set_title(theme.split(" &")[0].split(",")[0] + f"  (n={info['size']})", fontsize=10)
        ax.set_xlabel("projects")
    fig.suptitle("§5  Inside the two largest themes", fontweight="bold")
    save(fig, "05_subthemes.png", "sub-KMeans within each theme")


# §6 era-adjusted prize lift + era confound
def chart_prize_lift():
    base = df.groupby("time_bucket")["won"].mean()
    g = df.groupby("theme_label").agg(obs=("won", "mean"),
                                      exp=("time_bucket", lambda s: base[s].mean()))
    g["lift"] = g["obs"] / g["exp"]
    g = g.sort_values("lift")
    fig, ax = plt.subplots(figsize=(9, 6))
    cols = [GOOD if v >= 1 else HOT for v in g["lift"]]
    ax.barh(range(len(g)), g["lift"] - 1, left=1, color=cols)
    ax.axvline(1, color=INK, lw=1)
    ax.set_yticks(range(len(g))); ax.set_yticklabels([t[:42] for t in g.index], fontsize=8)
    for i, v in enumerate(g["lift"]):
        ax.text(v + (0.01 if v >= 1 else -0.01), i, f"{v:.2f}×", va="center",
                ha="left" if v >= 1 else "right", fontsize=8)
    ax.set_xlabel("era-adjusted win-rate lift (vs same-cohort baseline)")
    ax.set_title("§6  Which themes actually win prizes (era-adjusted)")
    save(fig, "06_prize_lift.png", "win = prize_count>0, adjusted for per-cohort prize density")

    fig, ax = plt.subplots(figsize=(8, 4.2))
    wr = df.groupby("time_bucket")["won"].mean() * 100
    ax.bar(wr.index, wr.values, color=WARM)
    for b, v in wr.items():
        ax.text(b, v + 1, f"{v:.0f}%", ha="center", fontsize=8)
    ax.set_xlabel("time bucket (oldest → newest)"); ax.set_ylabel("% projects winning ≥1 prize")
    ax.set_title("§6  The era confound: older cohorts win far more often")
    save(fig, "06b_era_confound.png", "why raw win-rates need era adjustment")


# §7 agent sponsor concentration
def chart_agent_sponsors():
    sub = df[df["theme_label"] == AI]
    c = Counter()
    for p in sub["prizes"].dropna():
        for nm in str(p).split("; "):
            nm = nm.strip()
            if nm and nm not in NON_SPONSOR:
                c[nm] += 1
    total = sum(c.values())
    top = c.most_common(10)[::-1]
    fig, ax = plt.subplots(figsize=(9, 5.5))
    cols = [HOT if n == "Coinbase Developer Platform" else ACCENT for n, _ in top]
    ax.barh([n for n, _ in top], [v for _, v in top], color=cols)
    for i, (_, v) in enumerate(top):
        ax.text(v + 1, i, f"{v}  ({v/total*100:.0f}%)", va="center", fontsize=8)
    ax.set_xlabel("agent-theme prizes won"); ax.set_xlim(0, 200)
    ax.set_title("§7  Coinbase bankrolled the agent wave")
    save(fig, "07_agent_sponsors.png", f"{total} sponsor-prizes across agent projects")


# §8 earmark scores + themed premium + decay
def chart_earmark():
    e = sorted(alpha8["earmark"], key=lambda x: x["earmark_lift"])[-16:]
    fig, ax = plt.subplots(figsize=(9, 6.5))
    cols = [HOT if x["earmark_lift"] >= 3 else GREY for x in e]
    ax.barh(range(len(e)), [x["earmark_lift"] for x in e], color=cols)
    ax.set_yticks(range(len(e)))
    ax.set_yticklabels([f"{x['sponsor'][:24]}" for x in e], fontsize=8)
    ax.axvline(3, color=INK, ls="--", lw=1)
    for i, x in enumerate(e):
        ax.text(x["earmark_lift"] + 0.2, i, f"{x['earmark_lift']:.1f}×", va="center", fontsize=8)
    ax.set_xlabel("earmark lift (theme concentration vs corpus)")
    ax.set_title("§8  Specialist (red ≥3×) vs generalist (grey) sponsors")
    save(fig, "08_earmark.png", "dashed line = specialist threshold")


def chart_premium():
    p = [t for t in alpha8["themed_premium"] if t["in_lift"] > 0]
    p = sorted(p, key=lambda t: t["in_lift"] - t["out_lift"])
    fig, ax = plt.subplots(figsize=(9, 4.6))
    prem = [t["in_lift"] - t["out_lift"] for t in p]
    cols = [GOOD if v >= 0 else HOT for v in prem]
    ax.barh(range(len(p)), prem, color=cols)
    ax.axvline(0, color=INK, lw=1)
    ax.set_yticks(range(len(p)))
    ax.set_yticklabels([f"{t['event'][:18]} → {t['theme'].split(' ')[0]}" for t in p], fontsize=8)
    ax.set_xlabel("themed-event win-lift premium (in-event − elsewhere)")
    ax.set_title("§8  Alpha window vs saturation trap")
    ax.annotate("trap", (-0.5, 0), color=HOT, fontsize=9)
    ax.annotate("open", (1.5, len(p) - 1), color=GOOD, fontsize=9)
    save(fig, "08b_themed_premium.png", "positive = themed event is an edge; negative = saturation trap")


def chart_decay():
    keys = [AI, "Cross-chain atomic swaps (1inch Fusion+)",
            "NFTs, collectibles & creator marketplaces",
            "ZK identity, privacy & verifiable reputation"]
    cols = [GOOD, HOT, WARM, ACCENT]
    d = alpha8["decay_by_bucket"]
    fig, ax = plt.subplots(figsize=(9, 5))
    for k, col in zip(keys, cols):
        ser = d.get(k, {})
        xs = sorted(int(b) for b in ser)
        ax.plot(xs, [ser[str(b)] for b in xs], marker="o", color=col, lw=2,
                label=k.split(" ")[0] if "ZK" not in k else "ZK/identity")
    ax.axhline(1, color=INK, ls="--", lw=1)
    ax.set_xlabel("time bucket (oldest → newest)"); ax.set_ylabel("era-adjusted win-lift")
    ax.set_title("§8  Decay: the edge reverts once a category goes mainstream")
    ax.legend(frameon=False, fontsize=8)
    save(fig, "08c_decay.png", "1.0 = no edge vs cohort baseline")


# §9 forward alpha forecast
def chart_forecast():
    f = pd.read_csv("alpha_forecast.csv")
    f = f[f["earmarked_usd_exp"] > 0].sort_values("alpha_index")
    palette = {"OPEN": GOOD, "CROWD": WARM, "TRAP": HOT, "COOL": "#6a4c93", "Thin": GREY}
    def col(lbl):
        for k, c in palette.items():
            if lbl.upper().startswith(k.upper()):
                return c
        return GREY
    fig, ax = plt.subplots(figsize=(10, 4))
    ax.barh(range(len(f)), f["alpha_index"], color=[col(l) for l in f["label"]])
    ax.set_yticks(range(len(f)))
    ax.set_yticklabels([c[:38] for c in f["category"]], fontsize=8)
    for i, (_, r) in enumerate(f.iterrows()):
        ax.text(r["alpha_index"] + 1, i, r["label"].split(" —")[0], va="center", fontsize=8)
    ax.set_xlabel("forward alpha index (specialist $ × win-conversion health)")
    ax.set_xlim(0, 125)
    ax.set_title("§9  Forecast — only specialist-backed categories shown")
    save(fig, "09_alpha_forecast.png", "upcoming general events; predicted sponsors. See §9 caveats.")


if __name__ == "__main__":
    print("Generating charts...")
    chart_themes(); chart_rotation(); chart_tech(); chart_outliers()
    chart_subthemes(); chart_prize_lift(); chart_agent_sponsors()
    chart_earmark(); chart_premium(); chart_decay(); chart_forecast()
    print(f"Done. {len(os.listdir(OUT))} files in {OUT}/")
