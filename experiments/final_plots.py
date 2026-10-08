import pandas as pd
import matplotlib.pyplot as plt
import os


df = pd.read_csv(
    "results/final_comparison_table.csv"
)

os.makedirs(
    "plots/final",
    exist_ok=True
)


# ============================================================
# Plot 1: Physical 2Q vs error budget
# ============================================================

for qubits in sorted(df["qubits"].unique()):

    data = df[df["qubits"] == qubits]

    plt.figure()

    plt.plot(
        data["error_budget"],
        data["threshold_2q"],
        marker="o",
        label="Threshold"
    )

    plt.plot(
        data["error_budget"],
        data["degree_2q"],
        marker="o",
        label="Degree"
    )

    plt.plot(
        data["error_budget"],
        data["selective_2q"],
        marker="o",
        label="Selective"
    )

    plt.xlabel("Allowed approximation error")
    plt.ylabel("Physical two-qubit gates")

    plt.title(
        f"{qubits}-qubit AQFT: Hardware Cost vs Error Budget"
    )

    plt.legend()
    plt.grid(True)

    plt.savefig(
        f"plots/final/physical_2q_{qubits}q.png",
        dpi=300,
        bbox_inches="tight"
    )

    plt.close()


# ============================================================
# Plot 2: Selective improvement
# ============================================================

plt.figure()

for qubits in sorted(df["qubits"].unique()):

    data = df[df["qubits"] == qubits]

    plt.plot(
        data["error_budget"],
        data["selective_improvement_percent"],
        marker="o",
        label=f"{qubits} qubits"
    )

plt.axhline(
    0,
    linestyle="--"
)

plt.xlabel("Allowed approximation error")
plt.ylabel(
    "Selective improvement in physical 2Q gates (%)"
)

plt.title(
    "Selective Pruning Improvement over Best Conventional Method"
)

plt.legend()
plt.grid(True)

plt.savefig(
    "plots/final/selective_improvement.png",
    dpi=300,
    bbox_inches="tight"
)

plt.close()


# ============================================================
# Plot 3: SWAP comparison
# ============================================================

plt.figure()

for qubits in sorted(df["qubits"].unique()):

    data = df[df["qubits"] == qubits]

    plt.plot(
        data["error_budget"],
        data["conventional_best_swaps"],
        marker="o",
        label=f"{qubits}Q conventional"
    )

    plt.plot(
        data["error_budget"],
        data["selective_swaps"],
        marker="x",
        linestyle="--",
        label=f"{qubits}Q selective"
    )

plt.xlabel("Allowed approximation error")
plt.ylabel("SWAP gates")

plt.title(
    "Routing Cost: Selective vs Conventional Pruning"
)

plt.legend()
plt.grid(True)

plt.savefig(
    "plots/final/swap_comparison.png",
    dpi=300,
    bbox_inches="tight"
)

plt.close()


print("\nFinal plots generated:")
print("plots/final/physical_2q_5q.png")
print("plots/final/physical_2q_6q.png")
print("plots/final/physical_2q_8q.png")
print("plots/final/selective_improvement.png")
print("plots/final/swap_comparison.png")