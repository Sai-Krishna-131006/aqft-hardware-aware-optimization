import csv
from pathlib import Path

results_file = Path("results/transpilation_results.csv")
output_file = Path("results/hardware_tradeoff_results.csv")

error_budgets = [0.01, 0.05, 0.10, 0.20]
qubit_sizes = [3, 4, 5, 6, 8]

# ---------------------------------------------------------
# Read original transpilation results
# ---------------------------------------------------------

rows = []

with open(results_file, "r", newline="") as file:
    reader = csv.DictReader(file)

    for row in reader:
        rows.append({
            "qubits": int(row["qubits"]),
            "method": row["method"],
            "parameter": float(row["parameter"]),
            "error": float(row["error"]),
            "logical_two_qubit": int(row["logical_two_qubit"]),
            "transpiled_two_qubit": int(row["transpiled_two_qubit"]),
            "swaps": int(row["swaps"]),
            "transpiled_depth": int(row["transpiled_depth"])
        })


# ---------------------------------------------------------
# Analyze each error budget
# ---------------------------------------------------------

tradeoff_results = []

for budget in error_budgets:

    print("\n" + "=" * 80)
    print(f"ERROR BUDGET <= {budget}")
    print("=" * 80)

    for n in qubit_sizes:

        candidates = [
            row for row in rows
            if row["qubits"] == n
            and row["error"] <= budget
        ]

        if not candidates:
            print(f"\n{n} QUBITS")
            print("No configuration satisfies this error budget.")
            continue

        # Separate degree and threshold candidates
        degree_candidates = [
            row for row in candidates
            if row["method"] == "degree"
        ]

        threshold_candidates = [
            row for row in candidates
            if row["method"] == "threshold"
        ]

        # -------------------------------------------------
        # Best degree configuration
        # -------------------------------------------------

        best_degree = None

        if degree_candidates:
            best_degree = min(
                degree_candidates,
                key=lambda row: (
                    row["transpiled_two_qubit"],
                    row["swaps"],
                    row["transpiled_depth"]
                )
            )

        # -------------------------------------------------
        # Best threshold configuration
        # -------------------------------------------------

        best_threshold = None

        if threshold_candidates:
            best_threshold = min(
                threshold_candidates,
                key=lambda row: (
                    row["transpiled_two_qubit"],
                    row["swaps"],
                    row["transpiled_depth"]
                )
            )

        # -------------------------------------------------
        # Overall best configuration
        # -------------------------------------------------

        overall_best = min(
            candidates,
            key=lambda row: (
                row["transpiled_two_qubit"],
                row["swaps"],
                row["transpiled_depth"]
            )
        )

        print(f"\n{n} QUBITS")
        print("-" * 80)

        if best_degree:
            print("Best degree configuration:")
            print(f"  Degree             : {int(best_degree['parameter'])}")
            print(f"  Error              : {best_degree['error']:.6f}")
            print(f"  Logical 2Q         : {best_degree['logical_two_qubit']}")
            print(f"  Transpiled 2Q      : {best_degree['transpiled_two_qubit']}")
            print(f"  SWAPs              : {best_degree['swaps']}")
            print(f"  Transpiled depth   : {best_degree['transpiled_depth']}")

        if best_threshold:
            print("\nBest threshold configuration:")
            print(f"  Threshold          : {best_threshold['parameter']}")
            print(f"  Error              : {best_threshold['error']:.6f}")
            print(f"  Logical 2Q         : {best_threshold['logical_two_qubit']}")
            print(f"  Transpiled 2Q      : {best_threshold['transpiled_two_qubit']}")
            print(f"  SWAPs              : {best_threshold['swaps']}")
            print(f"  Transpiled depth   : {best_threshold['transpiled_depth']}")

        print("\nOverall best:")

        if overall_best["method"] == "degree":
            print(
                f"  Method             : degree\n"
                f"  Parameter          : {int(overall_best['parameter'])}"
            )
        else:
            print(
                f"  Method             : threshold\n"
                f"  Parameter          : {overall_best['parameter']}"
            )

        print(f"  Error              : {overall_best['error']:.6f}")
        print(f"  Transpiled 2Q      : {overall_best['transpiled_two_qubit']}")
        print(f"  SWAPs              : {overall_best['swaps']}")
        print(f"  Transpiled depth   : {overall_best['transpiled_depth']}")

        # -------------------------------------------------
        # Save every eligible configuration to CSV
        # -------------------------------------------------

        for candidate in candidates:

            is_best = (
                candidate["method"] == overall_best["method"]
                and candidate["parameter"] == overall_best["parameter"]
            )

            tradeoff_results.append({
                "error_budget": budget,
                "qubits": n,
                "method": candidate["method"],
                "parameter": candidate["parameter"],
                "error": candidate["error"],
                "logical_two_qubit": candidate["logical_two_qubit"],
                "transpiled_two_qubit": candidate["transpiled_two_qubit"],
                "swaps": candidate["swaps"],
                "transpiled_depth": candidate["transpiled_depth"],
                "is_overall_best": is_best
            })


# ---------------------------------------------------------
# Save CSV
# ---------------------------------------------------------

fieldnames = [
    "error_budget",
    "qubits",
    "method",
    "parameter",
    "error",
    "logical_two_qubit",
    "transpiled_two_qubit",
    "swaps",
    "transpiled_depth",
    "is_overall_best"
]

with open(output_file, "w", newline="") as file:

    writer = csv.DictWriter(
        file,
        fieldnames=fieldnames
    )

    writer.writeheader()
    writer.writerows(tradeoff_results)


print("\n" + "=" * 80)
print("TRADE-OFF ANALYSIS COMPLETE")
print("=" * 80)
print(f"Results saved to: {output_file}")
print(f"Total CSV rows: {len(tradeoff_results)}")