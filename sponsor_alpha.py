#!/usr/bin/env python3
"""The sponsor-alpha model (report §8).

Generalizes the AI-agent finding into a repeatable lens:

  A. Earmark score per sponsor  — how concentrated a sponsor's prizes are in
     one theme, RELATIVE to that theme's corpus prize share (lift, not raw %).
  B. Themed-event premium       — a category's era-adjusted win-lift INSIDE its
     dedicated hackathon vs in general events (the open "alpha window").
  C. Decay                      — era-adjusted win-lift by time bucket for each
     earmarked category, showing peak (themed moment) -> reversion in general events.

All win-rates use prize_count>0 as the win proxy; lifts are era-adjusted against
per-time_bucket baselines to strip the cohort prize-density confound.
"""

import json
from collections import Counter, defaultdict

import pandas as pd

CSV = "ethglobal_projects_enriched.csv"
NON_SPONSOR = {"Finalist", "???", "Unknown"}

# Themed hackathons -> the theme_label they earmark.
THEMED_EVENTS = {
    "Agentic Ethereum": "AI agents & autonomous assistants",
    "ETHGlobal Trifecta - Agents": "AI agents & autonomous assistants",
    "ETHGlobal Trifecta - Zero Knowledge": "ZK identity, privacy & verifiable reputation",
    "Unite Defi": "Cross-chain atomic swaps (1inch Fusion+)",
    "NFTHack": "NFTs, collectibles & creator marketplaces",
    "NFTHack 2022": "NFTs, collectibles & creator marketplaces",
    "HackMoney": "DeFi lending, perps & collateral",
    "HackMoney 2021": "DeFi lending, perps & collateral",
    "HackFS": "Decentralized storage & content sharing",
    "HackFS 2021": "Decentralized storage & content sharing",
    "HackFS 2022": "Decentralized storage & content sharing",
    "Hack FEVM": "Decentralized storage & content sharing",
    "DAOHacks": "DAO tooling & governance",
}


def explode_prizes(df):
    """Return a long frame: one row per (project, sponsor-prize won)."""
    recs = []
    for _, r in df.iterrows():
        if pd.isna(r["prizes"]):
            continue
        for nm in str(r["prizes"]).split("; "):
            nm = nm.strip()
            if nm and nm not in NON_SPONSOR:
                recs.append({"sponsor": nm, "theme": r["theme_label"]})
    return pd.DataFrame(recs)


def main():
    df = pd.read_csv(CSV)
    df["won"] = df["prize_count"] > 0
    bucket_base = df.groupby("time_bucket")["won"].mean()

    # ---- A. earmark scores ----
    pl = explode_prizes(df)
    total = len(pl)
    theme_share = pl["theme"].value_counts() / total          # corpus prize share by theme
    spon_tot = pl["sponsor"].value_counts()
    rows = []
    for sp in spon_tot[spon_tot >= 30].index:
        sub = pl[pl["sponsor"] == sp]
        dist = sub["theme"].value_counts() / len(sub)
        lift = (dist / theme_share).dropna()
        # robust earmark: theme must hold >=15% of the sponsor's prizes AND >=8
        # of them, so a tiny-theme fluke can't masquerade as an earmark.
        counts = sub["theme"].value_counts()
        eligible = lift[(dist >= 0.15) & (counts >= 8)]
        if eligible.empty:
            eligible = lift[counts >= 8]
        if eligible.empty:
            eligible = lift
        top_theme = eligible.idxmax()
        rows.append({
            "sponsor": sp, "prizes": int(len(sub)),
            "earmark_theme": top_theme,
            "earmark_share": round(float(dist[top_theme]), 3),
            "earmark_lift": round(float(lift[top_theme]), 2),
        })
    earmark = pd.DataFrame(rows).sort_values("earmark_lift", ascending=False)
    print("=== A. SPONSOR EARMARK SCORES (lift vs theme's corpus prize share) ===")
    print("sponsor".ljust(28), "prizes".rjust(6), "lift".rjust(5), "share".rjust(6), " earmarked theme")
    for _, r in earmark.iterrows():
        flag = "EARMARK" if r.earmark_lift >= 2.0 else "       "
        print(f"{r.sponsor[:27].ljust(28)}{r.prizes:>6}{r.earmark_lift:>5.1f}x{r.earmark_share*100:>5.0f}%  {flag} {r.earmark_theme[:38]}")

    # ---- B. themed-event premium ----
    print("\n=== B. THEMED-EVENT PREMIUM (target theme: era-adj win-lift in vs out) ===")
    df["themed_target"] = df["event"].map(THEMED_EVENTS)
    premium = []
    for ev, theme in sorted(set(THEMED_EVENTS.items()), key=lambda x: x[1]):
        ev_proj = df[(df["event"] == ev) & (df["theme_label"] == theme)]
        if len(ev_proj) < 10:
            continue
        in_lift = ev_proj["won"].mean() / ev_proj["time_bucket"].map(bucket_base).mean()
        out = df[(df["event"] != ev) & (df["theme_label"] == theme)]
        out_lift = out["won"].mean() / out["time_bucket"].map(bucket_base).mean()
        premium.append((theme, ev, len(ev_proj), in_lift, out_lift))
    for theme, ev, n, il, ol in sorted(premium, key=lambda x: -x[3]):
        print(f"  {theme[:34]:<34} | {ev[:22]:<22} n={n:>3} in={il:.2f}x out={ol:.2f}x  premium {il-ol:+.2f}")

    # ---- C. decay curves ----
    print("\n=== C. DECAY: era-adjusted win-lift by time bucket (old->new) ===")
    cats = sorted(set(THEMED_EVENTS.values()))
    print("theme".ljust(34), " ".join(f"b{b}" for b in range(1, 7)))
    decay = {}
    for theme in cats:
        sub = df[df["theme_label"] == theme]
        cells = []
        series = {}
        for b in range(1, 7):
            bb = sub[sub["time_bucket"] == b]
            if len(bb) >= 10:
                lift = bb["won"].mean() / bucket_base[b]
                series[b] = round(float(lift), 2)
                cells.append(f"{lift:4.2f}")
            else:
                cells.append("   .")
        decay[theme] = series
        print(theme[:34].ljust(34), " ".join(cells))

    json.dump({"earmark": earmark.to_dict("records"),
               "themed_premium": [{"theme": t, "event": e, "n": n,
                                   "in_lift": round(il, 2), "out_lift": round(ol, 2)}
                                  for t, e, n, il, ol in premium],
               "decay_by_bucket": decay},
              open("sponsor_alpha.json", "w"), indent=2, ensure_ascii=False)
    print("\nwrote sponsor_alpha.json")


if __name__ == "__main__":
    main()
