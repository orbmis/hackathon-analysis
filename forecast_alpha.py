#!/usr/bin/env python3
"""§9 forward-looking alpha forecast for upcoming ETHGlobal hackathons.

Operationalizes the §8 playbook into a forward signal:
  open alpha = earmarked specialist $ likely on the table, chasing FEW builders,
               in a category with positive momentum.

Inputs:
  event_meta.csv / event_sponsors.csv  (scraped dates + per-sponsor $ pools)
  sponsor_alpha.json                   (§8 earmark map: specialist -> category)
  ethglobal_projects_enriched.csv      (category supply + win-lift momentum)

Outputs:
  sponsor_recurrence.csv  sponsor, p_present, avg_usd, earmark_category
  alpha_forecast.csv      category, earmarked_usd, supply_pct, momentum, alpha_index, label
  alpha_forecast.json     everything + per-upcoming-event headline sponsors
"""

import csv
import json
from collections import defaultdict

import numpy as np
import pandas as pd

TODAY = "2026-06-10"
GENERAL_MIN_SPONSORS = 15   # exclude tiny themed mini-events from recurrence
RECENT_N = 8                # recency window of recent general events
EARMARK_MIN_LIFT = 3.0      # §8 threshold for a "specialist" sponsor

UPCOMING_NAMES = {
    "newyork2026": "ETHGlobal New York 2026", "lisbon2026": "ETHGlobal Lisbon 2026",
    "ethonline2026": "ETHOnline 2026", "tokyo2026": "ETHGlobal Tokyo 2026",
    "mumbai": "ETHGlobal Mumbai",
}


def recurrence(meta, spon):
    """Recency-weighted P(sponsor at next general event) + avg $ when present."""
    general = meta[(meta.status == "past") & (meta.n_sponsors >= GENERAL_MIN_SPONSORS)]
    general = general.sort_values("start_date").drop_duplicates("slug")
    recent = general.tail(RECENT_N)
    slugs = list(recent.slug)
    # linear recency weights (oldest .. newest of the window)
    w = {s: i + 1 for i, s in enumerate(slugs)}
    wsum = sum(w.values())
    present = defaultdict(float)
    usd = defaultdict(list)
    for _, r in spon[spon.slug.isin(slugs)].iterrows():
        present[r.sponsor] += w[r.slug]
        usd[r.sponsor].append(r.prize_usd)
    rows = []
    for sp in present:
        rows.append({"sponsor": sp,
                     "p_present": round(present[sp] / wsum, 3),
                     "avg_usd": int(np.mean(usd[sp]))})
    return pd.DataFrame(rows).sort_values("p_present", ascending=False), slugs


def category_dynamics(enriched):
    """Per-theme current supply share + era-adjusted win-lift momentum."""
    df = pd.read_csv(enriched)
    df["won"] = df["prize_count"] > 0
    base = df.groupby("time_bucket")["won"].mean()
    out = {}
    for theme, g in df.groupby("theme_label"):
        recent = g[g.time_bucket == 6]
        supply = len(recent) / len(df[df.time_bucket == 6])
        lifts = []
        for b in (4, 5, 6):
            bb = g[g.time_bucket == b]
            lifts.append(bb["won"].mean() / base[b] if len(bb) >= 8 else np.nan)
        lifts = [x for x in lifts if not np.isnan(x)]
        momentum = (lifts[-1] - lifts[0]) if len(lifts) >= 2 else 0.0
        out[theme] = {"supply_pct": round(supply * 100, 1),
                      "recent_winlift": round(lifts[-1], 2) if lifts else None,
                      "momentum": round(float(momentum), 2)}
    return out


def main():
    meta = pd.read_csv("event_meta.csv")
    spon = pd.read_csv("event_sponsors.csv")
    alpha8 = json.load(open("sponsor_alpha.json"))
    dyn = category_dynamics("ethglobal_projects_enriched.csv")

    rec, window = recurrence(meta, spon)
    print(f"Recurrence window (recent general events): {window}\n")

    # specialist sponsor -> earmarked category (from §8)
    specialists = {e["sponsor"]: e["earmark_theme"]
                   for e in alpha8["earmark"] if e["earmark_lift"] >= EARMARK_MIN_LIFT}
    rec["earmark_category"] = rec["sponsor"].map(specialists).fillna("")
    rec.to_csv("sponsor_recurrence.csv", index=False)
    print("=== Top sponsors by P(present at next general event) ===")
    for _, r in rec.head(15).iterrows():
        tag = f"  ->EARMARKS {r.earmark_category}" if r.earmark_category else ""
        print(f"  {r.sponsor[:30]:<30} P={r.p_present:.2f}  ${r.avg_usd:>6,}{tag}")

    # expected earmarked $ per category = sum over present specialists
    pmap = dict(zip(rec.sponsor, rec.p_present))
    umap = dict(zip(rec.sponsor, rec.avg_usd))
    cat_usd = defaultdict(float)
    cat_sponsors = defaultdict(list)
    for sp, cat in specialists.items():
        p = pmap.get(sp, 0.0)
        if p > 0:
            cat_usd[cat] += p * umap.get(sp, 0)
            cat_sponsors[cat].append((sp, p, umap.get(sp, 0)))

    # §8 themed-event premium as a TRAP detector: a category whose win-lift fell
    # INSIDE its own themed event (in < out) re-saturates whenever its sponsor
    # brings the bounty, so idle low supply is a mirage, not an opening. Use the
    # LARGEST-SAMPLE themed event per category, and ignore in_lift==0 (those are
    # §8's flagged data gaps for pre-2023 events, not real zeros).
    best = {}
    for t in alpha8.get("themed_premium", []):
        if t["in_lift"] <= 0:
            continue
        if t["theme"] not in best or t["n"] > best[t["theme"]]["n"]:
            best[t["theme"]] = t
    trap = {th: round(t["in_lift"] - t["out_lift"], 2) for th, t in best.items()}

    # alpha = earmarked $ * health, where health rewards categories that actually
    # CONVERT $ into wins (recent win-lift + momentum) and damps saturated/trap ones.
    rowsf = []
    for cat, d in dyn.items():
        usd = cat_usd.get(cat, 0.0)
        wl = d["recent_winlift"] if d["recent_winlift"] is not None else 1.0
        mom_mult = 1 + max(min(d["momentum"], 0.5), -0.5)          # [0.5, 1.5]
        sat_mult = 1 / (1 + max(d["supply_pct"] - 8, 0) / 8)        # penalize >8% supply
        health = max(min(wl, 1.4), 0.2) * mom_mult * sat_mult
        trap_prem = trap.get(cat, 0.0)
        if trap_prem < -0.3:                                       # demonstrated trap
            health *= 0.25
        rowsf.append({"category": cat, "earmarked_usd_exp": int(usd),
                      "supply_pct": d["supply_pct"], "recent_winlift": d["recent_winlift"],
                      "momentum": d["momentum"], "trap_premium": round(trap_prem, 2),
                      "raw": usd * health, "specialists": cat_sponsors.get(cat, [])})
    mx = max((r["raw"] for r in rowsf), default=1) or 1
    for r in rowsf:
        r["alpha_index"] = round(100 * r["raw"] / mx, 1)
        if r["earmarked_usd_exp"] == 0:
            r["label"] = "No specialist $ (no sponsor edge)"
        elif r["trap_premium"] < -0.3:
            r["label"] = "TRAP — re-saturates under its bounty (§8)"
        elif r["momentum"] <= -0.2:
            r["label"] = "COOLING — edge decaying"
        elif r["supply_pct"] >= 12:
            r["label"] = "CROWDED — $ present but saturated"
        elif r["earmarked_usd_exp"] >= 5000 and r["alpha_index"] >= 50:
            r["label"] = "OPEN — $ present, converting, not crowded"
        else:
            r["label"] = "Thin — weak/▾ specialist $"
    rowsf.sort(key=lambda r: -r["alpha_index"])

    print("\n=== CATEGORY ALPHA INDEX (applies to upcoming general events) ===")
    print(f"{'category':<46}{'idx':>5}{'$exp':>9}{'supply%':>8}{'mom':>6}  label")
    for r in rowsf:
        print(f"{r['category'][:45]:<46}{r['alpha_index']:>5.0f}{r['earmarked_usd_exp']:>9,}"
              f"{r['supply_pct']:>7.1f}%{r['momentum']:>6.2f}  {r['label']}")

    with open("alpha_forecast.csv", "w", newline="") as f:
        w = csv.writer(f)
        w.writerow(["category", "alpha_index", "earmarked_usd_exp", "supply_pct",
                    "recent_winlift", "momentum", "label"])
        for r in rowsf:
            w.writerow([r["category"], r["alpha_index"], r["earmarked_usd_exp"],
                        r["supply_pct"], r["recent_winlift"], r["momentum"], r["label"]])

    upcoming = meta[meta.status == "upcoming"].sort_values("start_date")
    upcoming_out = []
    likely = rec[rec.p_present >= 0.5]
    for _, e in upcoming.iterrows():
        heads = [(s.sponsor, s.earmark_category) for _, s in likely.iterrows() if s.earmark_category]
        upcoming_out.append({"event": UPCOMING_NAMES.get(e.slug, e.slug),
                             "slug": e.slug, "date": e.start_date,
                             "predicted_specialist_sponsors": heads[:8],
                             "top_alpha_categories": [r["category"] for r in rowsf[:3]]})

    json.dump({"today": TODAY, "recurrence_window": window,
               "category_alpha": rowsf, "upcoming": upcoming_out},
              open("alpha_forecast.json", "w"), indent=2, default=str)
    print("\n=== UPCOMING EVENTS ===")
    for u in upcoming_out:
        print(f"  {u['date']}  {u['event']}")
    print("\nwrote sponsor_recurrence.csv, alpha_forecast.csv, alpha_forecast.json")


if __name__ == "__main__":
    main()
