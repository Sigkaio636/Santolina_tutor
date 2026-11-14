"""Synthetic weekly visits and sales per store (seeded, so the example is reproducible)."""
import numpy as np
import pandas as pd

rng = np.random.default_rng(7)
rows = []
for store, (visits, conv) in {"Harbour": (620, 21.0), "Old Town": (540, 17.5), "Station": (700, 12.0),
                              "Hillside": (380, 19.0), "Market": (460, 15.0), "Campus": (510, 9.5)}.items():
    for week in range(1, 27):
        v = max(50, rng.normal(visits, 60))
        rows.append({"store": store, "week": week, "visits": round(v),
                     "sales_eur": round(v * rng.normal(conv, 1.8))})
pd.DataFrame(rows).to_csv("store_weeks.csv", index=False)
print(len(rows), "rows")
