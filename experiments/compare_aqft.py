import csv
from pathlib import Path
import matplotlib.pyplot as plt

project_dir = Path(__file__).resolve().parent.parent

degree_file = project_dir / "results" / "aqft_degree_results.csv"
threshold_file = project_dir / "results" / "aqft_threshold_results.csv"

plots_dir = project_dir / "plots"
plots_dir.mkdir(exist_ok=True)


# --------------------------------------------------
# Read degree-based results
# --------------------------------------------------

degree_data = []

with open(degree_file, "r") as file:
    reader = csv.DictReader(file)

    for row in reader:
        degree_data.append({
            "qubits": int(row["qubits"]),
            "error": float(row["error"]),
            "two_qubit_gates": int(row["two_qubit_gates"])
        })


# --------------------------------------------------
# Read threshold-based results
# --------------------------------------------------

threshold_data = []

with open(threshold_file, "r") as file:
    reader = csv.DictReader(file)

    for row in reader:
        threshold_data.append({
            "qubits": int(row["qubits"]),
            "error": float(row["error"]),
            "two_qubit_gates": int(row["two_qubit_gates"])
        })


# --------------------------------------------------
# Compare methods
# --------------------------------------------------

qubit_sizes = [3, 4, 5, 6, 8]

for n in qubit_sizes:

    degree_rows = [
        row for row in degree_data
        if row["qubits"] == n
    ]

    threshold_rows = [
        row for row in threshold_data
        if row["qubits"] == n
    ]

    plt.figure()

    # Degree-based AQFT
    degree_error = [
        row["error"] for row in degree_rows
    ]

    degree_two_qubit = [
        row["two_qubit_gates"] for row in degree_rows
    ]

    plt.plot(
        degree_error,
        degree_two_qubit,
        marker="o",
        label="Degree-based AQFT"
    )

    # Threshold-based AQFT
    threshold_error = [
        row["error"] for row in threshold_rows
    ]

    threshold_two_qubit = [
        row["two_qubit_gates"] for row in threshold_rows
    ]

    plt.plot(
        threshold_error,
        threshold_two_qubit,
        marker="s",
        label="Threshold-based AQFT"
    )

    plt.xlabel("Approximation error")
    plt.ylabel("Two-qubit gates")
    plt.title(f"AQFT comparison — {n} qubits")

    plt.legend()
    plt.grid(True)

    plt.savefig(
        plots_dir / f"v1_vs_v2_{n}qubits.png",
        dpi=300,
        bbox_inches="tight"
    )

    plt.close()

# --------------------------------------------------
# Combined comparison plot
# --------------------------------------------------

plt.figure(figsize=(10, 7))

markers_degree = {
    3: "o",
    4: "s",
    5: "^",
    6: "D",
    8: "x"
}

markers_threshold = {
    3: "o",
    4: "s",
    5: "^",
    6: "D",
    8: "x"
}

for n in qubit_sizes:

    degree_rows = [
        row for row in degree_data
        if row["qubits"] == n
    ]

    threshold_rows = [
        row for row in threshold_data
        if row["qubits"] == n
    ]

    # Degree-based AQFT
    degree_error = [
        row["error"] for row in degree_rows
    ]

    degree_two_qubit = [
        row["two_qubit_gates"] for row in degree_rows
    ]

    plt.plot(
        degree_error,
        degree_two_qubit,
        marker=markers_degree[n],
        linestyle="-",
        label=f"{n}q Degree"
    )

    # Threshold-based AQFT
    threshold_error = [
        row["error"] for row in threshold_rows
    ]

    threshold_two_qubit = [
        row["two_qubit_gates"] for row in threshold_rows
    ]

    plt.plot(
        threshold_error,
        threshold_two_qubit,
        marker=markers_threshold[n],
        linestyle="--",
        label=f"{n}q Threshold"
    )


plt.xlabel("Approximation error")
plt.ylabel("Two-qubit gates")

plt.title(
    "Degree-based vs Threshold-based AQFT Across Qubit Sizes"
)

plt.legend(
    ncol=2,
    fontsize=9
)

plt.grid(True)

plt.savefig(
    plots_dir / "combined_aqft_comparison.png",
    dpi=300,
    bbox_inches="tight"
)

plt.close()

print("Combined AQFT comparison plot generated.")