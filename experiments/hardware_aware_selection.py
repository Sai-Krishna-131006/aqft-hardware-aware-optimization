import csv
from pathlib import Path


# ============================================================
# FILES
# ============================================================

input_file = Path("results/transpilation_results.csv")
output_file = Path("results/hardware_aware_selection.csv")


# ============================================================
# EXPERIMENT SETTINGS
# ============================================================

error_budgets = [0.01, 0.05, 0.10, 0.20]
qubit_sizes = [3, 4, 5, 6, 8]


# ============================================================
# READ TRANSPILATION RESULTS
# ============================================================

rows = []

with open(input_file, "r", newline="") as file:
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


# ============================================================
# HARDWARE-AWARE SELECTION
# ============================================================

selection_results = []


for budget in error_budgets:

    print()
    print("=" * 80)
    print(f"ERROR BUDGET <= {budget}")
    print("=" * 80)

    for n in qubit_sizes:

        # ----------------------------------------------------
        # Select all configurations satisfying error constraint
        # ----------------------------------------------------

        candidates = [
            row for row in rows
            if row["qubits"] == n
            and row["error"] <= budget
        ]

        if not candidates:

            print()
            print(f"{n} QUBITS")
            print("No valid configuration.")
            continue


        # ----------------------------------------------------
        # Separate degree and threshold approaches
        # ----------------------------------------------------

        degree_candidates = [
            row for row in candidates
            if row["method"] == "degree"
        ]

        threshold_candidates = [
            row for row in candidates
            if row["method"] == "threshold"
        ]


        # ----------------------------------------------------
        # Best degree configuration
        #
        # Primary objective:
        #     minimum transpiled 2Q gates
        #
        # Tie breakers:
        #     minimum SWAPs
        #     minimum depth
        # ----------------------------------------------------

        best_degree = min(
            degree_candidates,
            key=lambda row: (
                row["transpiled_two_qubit"],
                row["swaps"],
                row["transpiled_depth"]
            )
        )


        # ----------------------------------------------------
        # Best threshold configuration
        # ----------------------------------------------------

        best_threshold = min(
            threshold_candidates,
            key=lambda row: (
                row["transpiled_two_qubit"],
                row["swaps"],
                row["transpiled_depth"]
            )
        )


        # ----------------------------------------------------
        # Hardware-aware selection
        #
        # Search ALL valid configurations.
        # Choose the one with minimum physical cost.
        # ----------------------------------------------------

        hardware_aware = min(
            candidates,
            key=lambda row: (
                row["transpiled_two_qubit"],
                row["swaps"],
                row["transpiled_depth"]
            )
        )


        # ----------------------------------------------------
        # Calculate savings relative to threshold baseline
        # ----------------------------------------------------

        two_qubit_savings = (
            best_threshold["transpiled_two_qubit"]
            - hardware_aware["transpiled_two_qubit"]
        )

        if best_threshold["transpiled_two_qubit"] > 0:

            two_qubit_savings_percent = (
                two_qubit_savings
                / best_threshold["transpiled_two_qubit"]
                * 100
            )

        else:
            two_qubit_savings_percent = 0


        swap_savings = (
            best_threshold["swaps"]
            - hardware_aware["swaps"]
        )


        depth_savings = (
            best_threshold["transpiled_depth"]
            - hardware_aware["transpiled_depth"]
        )


        # ====================================================
        # PRINT RESULTS
        # ====================================================

        print()
        print(f"{n} QUBITS")
        print("-" * 80)

        print("Best threshold baseline:")
        print(
            f"  Parameter       : {best_threshold['parameter']}"
        )
        print(
            f"  Error           : {best_threshold['error']:.6f}"
        )
        print(
            f"  Physical 2Q     : {best_threshold['transpiled_two_qubit']}"
        )
        print(
            f"  SWAPs           : {best_threshold['swaps']}"
        )
        print(
            f"  Depth           : {best_threshold['transpiled_depth']}"
        )

        print()

        print("Best degree configuration:")
        print(
            f"  Degree          : {best_degree['parameter']}"
        )
        print(
            f"  Error           : {best_degree['error']:.6f}"
        )
        print(
            f"  Physical 2Q     : {best_degree['transpiled_two_qubit']}"
        )
        print(
            f"  SWAPs           : {best_degree['swaps']}"
        )
        print(
            f"  Depth           : {best_degree['transpiled_depth']}"
        )

        print()

        print("Hardware-aware selection:")
        print(
            f"  Method          : {hardware_aware['method']}"
        )
        print(
            f"  Parameter       : {hardware_aware['parameter']}"
        )
        print(
            f"  Error           : {hardware_aware['error']:.6f}"
        )
        print(
            f"  Physical 2Q     : {hardware_aware['transpiled_two_qubit']}"
        )
        print(
            f"  SWAPs           : {hardware_aware['swaps']}"
        )
        print(
            f"  Depth           : {hardware_aware['transpiled_depth']}"
        )

        print()

        print("Savings vs threshold:")
        print(
            f"  Physical 2Q     : {two_qubit_savings}"
            f" ({two_qubit_savings_percent:.2f}%)"
        )
        print(
            f"  SWAPs           : {swap_savings}"
        )
        print(
            f"  Depth           : {depth_savings}"
        )


        # ====================================================
        # SAVE RESULT
        # ====================================================

        selection_results.append({
            "error_budget": budget,
            "qubits": n,

            "threshold_parameter":
                best_threshold["parameter"],

            "threshold_error":
                best_threshold["error"],

            "threshold_physical_2q":
                best_threshold["transpiled_two_qubit"],

            "threshold_swaps":
                best_threshold["swaps"],

            "threshold_depth":
                best_threshold["transpiled_depth"],

            "degree":
                best_degree["parameter"],

            "degree_error":
                best_degree["error"],

            "degree_physical_2q":
                best_degree["transpiled_two_qubit"],

            "degree_swaps":
                best_degree["swaps"],

            "degree_depth":
                best_degree["transpiled_depth"],

            "selected_method":
                hardware_aware["method"],

            "selected_parameter":
                hardware_aware["parameter"],

            "selected_error":
                hardware_aware["error"],

            "selected_physical_2q":
                hardware_aware["transpiled_two_qubit"],

            "selected_swaps":
                hardware_aware["swaps"],

            "selected_depth":
                hardware_aware["transpiled_depth"],

            "two_qubit_savings":
                two_qubit_savings,

            "two_qubit_savings_percent":
                two_qubit_savings_percent,

            "swap_savings":
                swap_savings,

            "depth_savings":
                depth_savings
        })


# ============================================================
# WRITE CSV
# ============================================================

fieldnames = [
    "error_budget",
    "qubits",

    "threshold_parameter",
    "threshold_error",
    "threshold_physical_2q",
    "threshold_swaps",
    "threshold_depth",

    "degree",
    "degree_error",
    "degree_physical_2q",
    "degree_swaps",
    "degree_depth",

    "selected_method",
    "selected_parameter",
    "selected_error",
    "selected_physical_2q",
    "selected_swaps",
    "selected_depth",

    "two_qubit_savings",
    "two_qubit_savings_percent",
    "swap_savings",
    "depth_savings"
]


with open(output_file, "w", newline="") as file:

    writer = csv.DictWriter(
        file,
        fieldnames=fieldnames
    )

    writer.writeheader()
    writer.writerows(selection_results)


# ============================================================
# COMPLETE
# ============================================================

print()
print("=" * 80)
print("HARDWARE-AWARE SELECTION COMPLETE")
print("=" * 80)

print(f"Results saved to:")
print(output_file)

print(f"Total result rows: {len(selection_results)}")