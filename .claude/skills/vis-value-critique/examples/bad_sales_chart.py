"""A deliberately bad matplotlib chart used to test the inspectors and as the worked
example in example_critique.md. Quarterly sales of five product lines, plus a pie of
market share. Every problem here is intentional."""
import matplotlib.pyplot as plt
import numpy as np

products = ["Widgets", "Gadgets", "Gizmos", "Doodads", "Thingamajigs", "Whatsits",
            "Doohickeys", "Sprockets"]
sales = np.array([412, 398, 421, 405, 390, 417, 402, 409])          # k€
growth = np.array([2.1, -0.4, 3.0, 1.2, -1.1, 2.6, 0.3, 1.8])       # %

fig, ax = plt.subplots(figsize=(7, 4))
colors = plt.cm.jet(np.linspace(0, 1, len(products)))
bars = ax.bar(products, sales, color=colors, edgecolor="black", linewidth=1.5)
ax.set_ylim(385, 425)                       # truncated axis on bars
ax.set_xlabel("product_name")
ax.set_ylabel("sales_k")
ax.grid(True, color="black", linewidth=1.2)
ax.set_facecolor("#ffe9c6")
plt.setp(ax.get_xticklabels(), rotation=60)
ax.legend(bars, products, fontsize=7, loc="upper right")

ax2 = ax.twinx()                            # dual axis
ax2.plot(products, growth, color="green", marker="o", linewidth=2, label="growth")
ax2.plot(products, growth * 0.9, color="red", marker="s", linewidth=2, label="target")
ax2.set_ylabel("growth")
ax2.legend(fontsize=7, loc="upper left")

fig2, axp = plt.subplots(figsize=(5, 5))
share = [31, 22, 14, 11, 8, 6, 5, 3]
axp.pie(share, labels=products, startangle=30, explode=[0.1] + [0] * 7, shadow=True,
        colors=plt.cm.Set1(np.linspace(0, 1, 8)))

plt.show()
