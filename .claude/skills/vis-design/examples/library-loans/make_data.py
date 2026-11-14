"""Synthetic dataset for the worked example: public-library loans, 2019–2024."""
import csv
import datetime as dt
import random

random.seed(11)
branches = ["Central", "Riverside", "Hillcrest", "Old Town", "Harbour", "Northgate", "Southfield",
            "Westbrook", "Eastwood", "Parkside", "University", "Market Square"]
weights = [9, 6, 5, 4, 4, 3, 3, 3, 2, 2, 5, 3]
genres = ["fiction", "non-fiction", "children", "comics", "science", "history"]
with open("loans.csv", "w", newline="") as fh:
    w = csv.writer(fh)
    w.writerow(["loan_date", "branch_code", "branch", "genre", "days_on_loan", "returned_late"])
    for i in range(6000):
        d = dt.date(2019, 1, 1) + dt.timedelta(days=random.randint(0, 365 * 6 - 1))
        b = random.choices(range(len(branches)), weights=weights)[0]
        days = max(1, int(random.gauss(18, 7)))
        w.writerow([d.strftime("%d/%m/%Y"), f"{b+1:03d}", branches[b], random.choice(genres), days, "yes" if days > 28 else "no"])
print("wrote loans.csv")
