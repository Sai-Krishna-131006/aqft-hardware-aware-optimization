import csv
from pathlib import Path


degree_file = Path("results/transpilation_results.csv")
threshold_file = Path("results/fine_threshold_results.csv")

output_file = Path("results/truncation_comparison.csv")


# ============================================================
# READ DEGREE RESULTS
# ============================================================

degree_rows = []

with open(degree_file, "r", newline="") as file:
    reader = csv.DictReader(file)

    for row in reader:
        if row["method"] != "degree":
            continue

        degree_rows.append({
            "qubits": int(row["qubits"]),
            "degree": int(float(row["parameter"])),
            "error": float(row["error"]),
            "logical_two_qubit": int(row["logical_two_qubit"]),
            "transpiled_two_qubit": int(row["transpiled_two_qubit"]),
            "swaps": int(row["swaps"]),
            "transpiled_depth": int(row["transpiled_depth"])
        })


# ============================================================
# READ FINE THRESHOLD RESULTS
# ============================================================

threshold_rows = []

with open(threshold_file, "r", newline="") as file:
    reader = csv.DictReader(file)

    for row in reader:

        threshold_rows.append({
            "qubits": int(row["qubits"]),
            "threshold": float(row["threshold"]),
            "error": float(row["error"]),
            "logical_two_qubit": int(row["logical_two_qubit"]),
            "transpiled_two_qubit": int(row["transpiled_two_qubit"]),
            "swaps": int(row["swaps"]),
            "transpiled_depth": int(row["transpiled_depth"])
        })


# ============================================================
# COMPARE
# ============================================================

comparison = []


for n in sorted(set(row["qubits"] for row in degree_rows)):

    degree_data = [
        row for row in degree_rows
        if row["qubits"] == n
    ]

    threshold_data = [
        row for row in threshold_rows
        if row["qubits"] == n
    ]

    print()
    print("=" * 80)
    print(f"{n} QUBITS")
    print("=" * 80)

    print(
        f"Degree configurations   : {len(degree_data)}"
    )

    print(
        f"Threshold configurations: {len(threshold_data)}"
    )

    print()

    # --------------------------------------------------------
    # Compare every degree against threshold candidates
    # --------------------------------------------------------

    for degree in degree_data:

        matching = [
            row for row in threshold_data
            if (
                row["logical_two_qubit"]
                == degree["logical_two_qubit"]
            )
        ]

        if matching:

            # There should normally be one matching
            # threshold configuration for each truncation.

            best_match = min(
                matching,
                key=lambda row: abs(
                    row["error"] - degree["error"]
                )
            )

            error_difference = abs(
                degree["error"]
                - best_match["error"]
            )

            physical_difference = (
                degree["transpiled_two_qubit"]
                - best_match["transpiled_two_qubit"]
            )

            same_circuit_metrics = (
                error_difference < 1e-10
                and physical_difference == 0
                and degree["swaps"] == best_match["swaps"]
                and degree["transpiled_depth"]
                == best_match["transpiled_depth"]
            )

            comparison.append({
                "qubits": n,
                "degree": degree["degree"],
                "threshold": best_match["threshold"],
                "degree_error": degree["error"],
                "threshold_error": best_match["error"],
                "error_difference": error_difference,
                "degree_physical_2q":
                    degree["transpiled_two_qubit"],
                "threshold_physical_2q":
                    best_match["transpiled_two_qubit"],
                "degree_swaps":
                    degree["swaps"],
                "threshold_swaps":
                    best_match["swaps"],
                "degree_depth":
                    degree["transpiled_depth"],
                "threshold_depth":
                    best_match["transpiled_depth"],
                "same_metrics":
                    same_circuit_metrics
            })


# ============================================================
# PRINT COMPARISON
# ============================================================

print()
print("=" * 80)
print("DEGREE vs THRESHOLD COMPARISON")
print("=" * 80)

for row in comparison:

    print(
        f"{row['qubits']}Q | "
        f"degree={row['degree']:2d} | "
        f"threshold={row['threshold']:.6f} | "
        f"error diff={row['error_difference']:.2e} | "
        f"physical 2Q="
        f"{row['degree_physical_2q']:2d}/"
        f"{row['threshold_physical_2q']:2d} | "
        f"same={row['same_metrics']}"
    )


# ============================================================
# SUMMARY
# ============================================================

total = len(comparison)

same = sum(
    1
    for row in comparison
    if row["same_metrics"]
)

print()
print("=" * 80)
print("SUMMARY")
print("=" * 80)

print(f"Comparable configurations : {total}")
print(f"Matching configurations   : {same}")

if total > 0:

    percentage = (
        same / total * 100
    )

    print(
        f"Matching percentage       : "
        f"{percentage:.2f}%"
    )


# ============================================================
# SAVE CSV
# ============================================================

fieldnames = [
    "qubits",
    "degree",
    "threshold",
    "degree_error",
    "threshold_error",
    "error_difference",
    "degree_physical_2q",
    "threshold_physical_2q",
    "degree_swaps",
    "threshold_swaps",
    "degree_depth",
    "threshold_depth",
    "same_metrics"
]


with open(output_file, "w", newline="") as file:

    writer = csv.DictWriter(
        file,
        fieldnames=fieldnames
    )

    writer.writeheader()
    writer.writerows(comparison)


print()
print(f"Comparison saved to: {output_file}")