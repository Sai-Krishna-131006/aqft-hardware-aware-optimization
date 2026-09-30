import csv
from pathlib import Path

import matplotlib.pyplot as plt


# Read CSV data
csv_file = Path("results/aqft_degree_results.csv")

data = []

with open(csv_file, newline="") as file:
    reader = csv.DictReader(file)

    for row in reader:
        data.append({
            "qubits": int(row["qubits"]),
            "degree": int(row["degree"]),
            "total_gates": int(row["total_gates"]),
            "depth": int(row["depth"]),
            "two_qubit_gates": int(row["two_qubit_gates"]),
            "fidelity": float(row["fidelity"]),
            "error": float(row["error"])
        })


# Create plots folder
plots_dir = Path("plots")
plots_dir.mkdir(exist_ok=True)


# Plot 1: Total gates vs degree
plt.figure()

for n in [3, 4, 5, 6, 8]:
    rows = [row for row in data if row["qubits"] == n]

    degrees = [row["degree"] for row in rows]
    gates = [row["total_gates"] for row in rows]

    plt.plot(degrees, gates, marker="o", label=f"{n} qubits")

plt.xlabel("Approximation degree")
plt.ylabel("Total gates")
plt.title("Total gates vs approximation degree")
plt.legend()
plt.grid(True)

plt.savefig(plots_dir / "gate_count_vs_degree.png", dpi=300)
plt.close()


# Plot 2: Two-qubit gates vs degree
plt.figure()

for n in [3, 4, 5, 6, 8]:
    rows = [row for row in data if row["qubits"] == n]

    degrees = [row["degree"] for row in rows]
    two_qubit = [row["two_qubit_gates"] for row in rows]

    plt.plot(degrees, two_qubit, marker="o", label=f"{n} qubits")

plt.xlabel("Approximation degree")
plt.ylabel("Two-qubit gates")
plt.title("Two-qubit gates vs approximation degree")
plt.legend()
plt.grid(True)

plt.savefig(plots_dir / "two_qubit_vs_degree.png", dpi=300)
plt.close()


# Plot 3: Depth vs degree
plt.figure()

for n in [3, 4, 5, 6, 8]:
    rows = [row for row in data if row["qubits"] == n]

    degrees = [row["degree"] for row in rows]
    depth = [row["depth"] for row in rows]

    plt.plot(degrees, depth, marker="o", label=f"{n} qubits")

plt.xlabel("Approximation degree")
plt.ylabel("Circuit depth")
plt.title("Circuit depth vs approximation degree")
plt.legend()
plt.grid(True)

plt.savefig(plots_dir / "depth_vs_degree.png", dpi=300)
plt.close()


# Plot 4: Error vs degree
plt.figure()

for n in [3, 4, 5, 6, 8]:
    rows = [row for row in data if row["qubits"] == n]

    degrees = [row["degree"] for row in rows]
    error = [row["error"] for row in rows]

    plt.plot(degrees, error, marker="o", label=f"{n} qubits")

plt.xlabel("Approximation degree")
plt.ylabel("Approximation error")
plt.title("Approximation error vs approximation degree")
plt.legend()
plt.grid(True)

plt.savefig(plots_dir / "error_vs_degree.png", dpi=300)
plt.close()

# Plot 5: Two-qubit gates vs approximation error
plt.figure()

for n in [3, 4, 5, 6, 8]:
    rows = [row for row in data if row["qubits"] == n]

    error = [row["error"] for row in rows]
    two_qubit = [row["two_qubit_gates"] for row in rows]

    plt.plot(error, two_qubit, marker="o", label=f"{n} qubits")

plt.xlabel("Approximation error")
plt.ylabel("Two-qubit gates")
plt.title("Two-qubit gate reduction vs approximation error")
plt.legend()
plt.grid(True)

plt.savefig(plots_dir / "two_qubit_vs_error.png", dpi=300)
plt.close()

print("Plots generated successfully.")
print(f"Saved to: {plots_dir}")