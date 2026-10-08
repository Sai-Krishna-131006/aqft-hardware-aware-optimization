import csv
from pathlib import Path
import math
import matplotlib.pyplot as plt


# ============================================================
# FILES
# ============================================================

input_file = Path("results/hardware_tradeoff_results.csv")
output_dir = Path("plots/tradeoff")

output_dir.mkdir(parents=True, exist_ok=True)


# ============================================================
# READ CSV
# ============================================================

rows = []

with open(input_file, "r", newline="") as file:
    reader = csv.DictReader(file)

    for row in reader:
        rows.append({
            "error_budget": float(row["error_budget"]),
            "qubits": int(row["qubits"]),
            "method": row["method"],
            "parameter": float(row["parameter"]),
            "error": float(row["error"]),
            "logical_two_qubit": int(row["logical_two_qubit"]),
            "transpiled_two_qubit": int(row["transpiled_two_qubit"]),
            "swaps": int(row["swaps"]),
            "transpiled_depth": int(row["transpiled_depth"]),
            "is_overall_best": row["is_overall_best"].lower() == "true"
        })


# ============================================================
# PLOT 1
# Error Budget vs Minimum Physical 2Q Gates
# ============================================================

budgets = sorted(set(row["error_budget"] for row in rows))
qubit_sizes = sorted(set(row["qubits"] for row in rows))

plt.figure(figsize=(9, 6))

for n in qubit_sizes:

    x = []
    y = []

    for budget in budgets:

        candidates = [
            row for row in rows
            if row["qubits"] == n
            and row["error_budget"] == budget
            and row["is_overall_best"]
        ]

        if candidates:
            x.append(budget)
            y.append(candidates[0]["transpiled_two_qubit"])

    plt.plot(
        x,
        y,
        marker="o",
        label=f"{n} qubits"
    )

plt.xlabel("Maximum Allowed Approximation Error")
plt.ylabel("Minimum Transpiled 2-Qubit Gates")
plt.title("Hardware Cost vs Allowed AQFT Approximation Error")
plt.grid(True, alpha=0.3)
plt.legend()
plt.tight_layout()

plt.savefig(
    output_dir / "error_budget_vs_physical_2q.png",
    dpi=300
)

plt.close()


# ============================================================
# PLOT 2
# Approximation Error vs Physical 2Q Gates
# ============================================================

plt.figure(figsize=(9, 6))

for n in qubit_sizes:

    degree_rows = [
        row for row in rows
        if row["qubits"] == n
        and row["method"] == "degree"
    ]

    errors = [
        row["error"]
        for row in degree_rows
    ]

    physical_2q = [
        row["transpiled_two_qubit"]
        for row in degree_rows
    ]

    plt.plot(
        errors,
        physical_2q,
        marker="o",
        label=f"{n} qubits"
    )

plt.xlabel("Approximation Error")
plt.ylabel("Transpiled 2-Qubit Gates")
plt.title("Approximation Error vs Hardware 2-Qubit Cost")
plt.grid(True, alpha=0.3)
plt.legend()
plt.tight_layout()

plt.savefig(
    output_dir / "error_vs_physical_2q.png",
    dpi=300
)

plt.close()


# ============================================================
# PLOT 3
# Approximation Error vs SWAP Count
# ============================================================

plt.figure(figsize=(9, 6))

for n in qubit_sizes:

    degree_rows = [
        row for row in rows
        if row["qubits"] == n
        and row["method"] == "degree"
    ]

    errors = [
        row["error"]
        for row in degree_rows
    ]

    swaps = [
        row["swaps"]
        for row in degree_rows
    ]

    plt.plot(
        errors,
        swaps,
        marker="o",
        label=f"{n} qubits"
    )

plt.xlabel("Approximation Error")
plt.ylabel("SWAP Count")
plt.title("Approximation Error vs Routing Cost")
plt.grid(True, alpha=0.3)
plt.legend()
plt.tight_layout()

plt.savefig(
    output_dir / "error_vs_swaps.png",
    dpi=300
)

plt.close()


# ============================================================
# PLOT 4
# Logical 2Q vs Transpiled 2Q
# ============================================================

plt.figure(figsize=(9, 6))

for n in qubit_sizes:

    degree_rows = [
        row for row in rows
        if row["qubits"] == n
        and row["method"] == "degree"
    ]

    logical = [
        row["logical_two_qubit"]
        for row in degree_rows
    ]

    physical = [
        row["transpiled_two_qubit"]
        for row in degree_rows
    ]

    plt.plot(
        logical,
        physical,
        marker="o",
        label=f"{n} qubits"
    )

plt.xlabel("Logical 2-Qubit Gates")
plt.ylabel("Transpiled 2-Qubit Gates")
plt.title("Logical vs Hardware 2-Qubit Cost")
plt.grid(True, alpha=0.3)
plt.legend()
plt.tight_layout()

plt.savefig(
    output_dir / "logical_vs_physical_2q.png",
    dpi=300
)

plt.close()


# ============================================================
# SUMMARY
# ============================================================

print()
print("=" * 70)
print("HARDWARE TRADE-OFF PLOTS GENERATED")
print("=" * 70)

print(f"Input : {input_file}")
print(f"Output: {output_dir}")

print()
print("Generated plots:")

print("1. error_budget_vs_physical_2q.png")
print("2. error_vs_physical_2q.png")
print("3. error_vs_swaps.png")
print("4. logical_vs_physical_2q.png")

print()
print("Analysis complete.")