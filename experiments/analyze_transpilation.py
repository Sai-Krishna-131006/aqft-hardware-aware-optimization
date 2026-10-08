import csv
from pathlib import Path
import matplotlib.pyplot as plt


# --------------------------------------------------
# Configuration
# --------------------------------------------------

input_file = Path("results/transpilation_results.csv")
output_dir = Path("plots/transpilation")

output_dir.mkdir(parents=True, exist_ok=True)


# --------------------------------------------------
# Read CSV
# --------------------------------------------------

rows = []

with open(input_file, "r", newline="") as file:

    reader = csv.DictReader(file)

    for row in reader:

        rows.append({
            "qubits": int(row["qubits"]),
            "method": row["method"],
            "parameter": float(row["parameter"]),
            "error": float(row["error"]),

            "logical_gates": int(row["logical_gates"]),
            "logical_depth": int(row["logical_depth"]),
            "logical_two_qubit": int(row["logical_two_qubit"]),

            "transpiled_gates": int(row["transpiled_gates"]),
            "transpiled_depth": int(row["transpiled_depth"]),
            "transpiled_two_qubit": int(row["transpiled_two_qubit"]),

            "swaps": int(row["swaps"])
        })


print(f"Loaded {len(rows)} rows")


# --------------------------------------------------
# Plot 1
# Approximation Error vs Transpiled 2-Qubit Gates
# --------------------------------------------------

plt.figure(figsize=(9, 6))

for n in [3, 4, 5, 6, 8]:

    data = [
        row for row in rows
        if row["qubits"] == n
        and row["method"] == "degree"
    ]

    plt.plot(
        [row["error"] for row in data],
        [row["transpiled_two_qubit"] for row in data],
        marker="o",
        label=f"{n} qubits"
    )

plt.xlabel("Approximation Error")
plt.ylabel("Transpiled 2-Qubit Gates")
plt.title("Approximation Error vs Transpiled 2-Qubit Gates")

plt.grid(True)
plt.legend()
plt.tight_layout()

plt.savefig(
    output_dir / "error_vs_transpiled_2q.png",
    dpi=300
)

plt.close()


# --------------------------------------------------
# Plot 2
# Approximation Error vs SWAP Count
# --------------------------------------------------

plt.figure(figsize=(9, 6))

for n in [3, 4, 5, 6, 8]:

    data = [
        row for row in rows
        if row["qubits"] == n
        and row["method"] == "degree"
    ]

    plt.plot(
        [row["error"] for row in data],
        [row["swaps"] for row in data],
        marker="o",
        label=f"{n} qubits"
    )

plt.xlabel("Approximation Error")
plt.ylabel("SWAP Count")
plt.title("Approximation Error vs SWAP Count")

plt.grid(True)
plt.legend()
plt.tight_layout()

plt.savefig(
    output_dir / "error_vs_swaps.png",
    dpi=300
)

plt.close()


# --------------------------------------------------
# Plot 3
# Logical vs Transpiled 2-Qubit Gates
# --------------------------------------------------

plt.figure(figsize=(9, 6))

for n in [3, 4, 5, 6, 8]:

    data = [
        row for row in rows
        if row["qubits"] == n
        and row["method"] == "degree"
    ]

    plt.plot(
        [row["logical_two_qubit"] for row in data],
        [row["transpiled_two_qubit"] for row in data],
        marker="o",
        label=f"{n} qubits"
    )

plt.xlabel("Logical 2-Qubit Gates")
plt.ylabel("Transpiled 2-Qubit Gates")
plt.title("Logical vs Transpiled 2-Qubit Gates")

plt.grid(True)
plt.legend()
plt.tight_layout()

plt.savefig(
    output_dir / "logical_vs_transpiled_2q.png",
    dpi=300
)

plt.close()

# --------------------------------------------------
# Plot 4
# Logical Depth vs Transpiled Depth
# --------------------------------------------------

plt.figure(figsize=(9, 6))

for n in [3, 4, 5, 6, 8]:

    data = [
        row for row in rows
        if row["qubits"] == n
        and row["method"] == "degree"
    ]

    # Read logical depth directly from CSV
    logical_depth = [
        int(row["logical_depth"])
        for row in data
    ]

    transpiled_depth = [
        int(row["transpiled_depth"])
        for row in data
    ]

    plt.plot(
        logical_depth,
        transpiled_depth,
        marker="o",
        label=f"{n} qubits"
    )

plt.xlabel("Logical Circuit Depth")
plt.ylabel("Transpiled Circuit Depth")
plt.title("Logical vs Transpiled Circuit Depth")

plt.grid(True)
plt.legend()
plt.tight_layout()

plt.savefig(
    output_dir / "logical_vs_transpiled_depth.png",
    dpi=300
)

plt.close()

# --------------------------------------------------
# Finished
# --------------------------------------------------

print("\nPlots generated successfully.")

print(output_dir / "error_vs_transpiled_2q.png")
print(output_dir / "error_vs_swaps.png")
print(output_dir / "logical_vs_transpiled_2q.png")
print(output_dir / "logical_vs_transpiled_depth.png")