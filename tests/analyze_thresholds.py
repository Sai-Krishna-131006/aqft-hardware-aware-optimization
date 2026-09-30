import csv
from pathlib import Path
from math import pi
import matplotlib.pyplot as plt

# --------------------------------------------------
# Paths
# --------------------------------------------------

project_dir = Path(__file__).resolve().parent.parent
results_file = project_dir / "results" / "aqft_threshold_results.csv"
plots_dir = project_dir / "plots"

plots_dir.mkdir(exist_ok=True)

# --------------------------------------------------
# Read CSV
# --------------------------------------------------

data = []

with open(results_file, "r") as file:
    reader = csv.DictReader(file)

    for row in reader:
        data.append({
            "qubits": int(row["qubits"]),
            "threshold": float(row["threshold"]),
            "two_qubit_gates": int(row["two_qubit_gates"]),
            "error": float(row["error"])
        })

qubit_sizes = [3, 4, 5, 6, 8]

# --------------------------------------------------
# Plot 1: Threshold vs Two-Qubit Gates
# --------------------------------------------------

plt.figure()

for n in qubit_sizes:
    rows = [row for row in data if row["qubits"] == n]

    thresholds = [row["threshold"] for row in rows]
    two_qubit = [row["two_qubit_gates"] for row in rows]

    plt.plot(
        thresholds,
        two_qubit,
        marker="o",
        label=f"{n} qubits"
    )

plt.xlabel("Threshold (radians)")
plt.ylabel("Two-qubit gates")
plt.title("Two-qubit gates vs AQFT threshold")
plt.legend()
plt.grid(True)

plt.savefig(
    plots_dir / "threshold_vs_two_qubit.png",
    dpi=300,
    bbox_inches="tight"
)

plt.close()


# --------------------------------------------------
# Plot 2: Threshold vs Approximation Error
# --------------------------------------------------

plt.figure()

for n in qubit_sizes:
    rows = [row for row in data if row["qubits"] == n]

    thresholds = [row["threshold"] for row in rows]
    error = [row["error"] for row in rows]

    plt.plot(
        thresholds,
        error,
        marker="o",
        label=f"{n} qubits"
    )

plt.xlabel("Threshold (radians)")
plt.ylabel("Approximation error")
plt.title("Approximation error vs AQFT threshold")
plt.legend()
plt.grid(True)

plt.savefig(
    plots_dir / "threshold_vs_error.png",
    dpi=300,
    bbox_inches="tight"
)

plt.close()


# --------------------------------------------------
# Plot 3: Two-Qubit Gates vs Approximation Error
# --------------------------------------------------

plt.figure()

for n in qubit_sizes:
    rows = [row for row in data if row["qubits"] == n]

    error = [row["error"] for row in rows]
    two_qubit = [row["two_qubit_gates"] for row in rows]

    plt.plot(
        error,
        two_qubit,
        marker="o",
        label=f"{n} qubits"
    )

plt.xlabel("Approximation error")
plt.ylabel("Two-qubit gates")
plt.title("Two-qubit gate reduction vs approximation error")
plt.legend()
plt.grid(True)

plt.savefig(
    plots_dir / "threshold_two_qubit_vs_error.png",
    dpi=300,
    bbox_inches="tight"
)

plt.close()

print("Threshold-based AQFT plots generated successfully.")