import pandas as pd
import os


ERROR_BUDGETS = [0.01, 0.05, 0.10, 0.20]
QUBITS = [5, 6, 8]


def best_under_budget(df, budget):
    valid = df[df["error"] <= budget + 1e-12]

    if valid.empty:
        return None

    return valid.sort_values(
        ["physical_2q", "swaps", "depth"]
    ).iloc[0]


def main():

    os.makedirs("results", exist_ok=True)

    # ---------------------------------------------------------
    # Load final 5Q, 6Q and 8Q experiments
    # ---------------------------------------------------------

    files = {
        5: "results/final_5q_comparison.csv",
        6: "results/final_6q_comparison.csv",
        8: "results/final_8q_comparison.csv",
    }

    all_results = []

    for n, filename in files.items():

        df = pd.read_csv(filename)
        df["qubits"] = n

        all_results.append(df)

    combined = pd.concat(
        all_results,
        ignore_index=True
    )

    combined.to_csv(
        "results/final_all_results.csv",
        index=False
    )

    # ---------------------------------------------------------
    # Compare methods
    # ---------------------------------------------------------

    rows = []

    for n in QUBITS:

        df_n = combined[
            combined["qubits"] == n
        ]

        for budget in ERROR_BUDGETS:

            selected = {}

            for method in [
                "threshold",
                "degree",
                "selective"
            ]:

                method_df = df_n[
                    df_n["method"] == method
                ]

                best = best_under_budget(
                    method_df,
                    budget
                )

                if best is not None:
                    selected[method] = best

            if not selected:
                continue

            conventional = [
                selected[m]
                for m in ["threshold", "degree"]
                if m in selected
            ]

            conventional_best = min(
                conventional,
                key=lambda r: (
                    r["physical_2q"],
                    r["swaps"],
                    r["depth"]
                )
            )

            selective = selected.get(
                "selective"
            )

            if selective is None:
                continue

            baseline_2q = (
                conventional_best["physical_2q"]
            )

            selective_2q = (
                selective["physical_2q"]
            )

            improvement = (
                (baseline_2q - selective_2q)
                / baseline_2q
                * 100
            )

            rows.append({
                "qubits": n,
                "error_budget": budget,

                "threshold_2q":
                    selected.get(
                        "threshold",
                        {}
                    ).get(
                        "physical_2q",
                        None
                    ),

                "degree_2q":
                    selected.get(
                        "degree",
                        {}
                    ).get(
                        "physical_2q",
                        None
                    ),

                "selective_2q":
                    selective_2q,

                "conventional_best_2q":
                    baseline_2q,

                "selective_improvement_percent":
                    improvement,

                "selective_error":
                    selective["error"],

                "selective_swaps":
                    selective["swaps"],

                "conventional_best_swaps":
                    conventional_best["swaps"],

                "selective_depth":
                    selective["depth"],

                "conventional_best_depth":
                    conventional_best["depth"],
            })

    final = pd.DataFrame(rows)

    final.to_csv(
        "results/final_comparison_table.csv",
        index=False
    )

    # ---------------------------------------------------------
    # Print final table
    # ---------------------------------------------------------

    print("\n")
    print("=" * 110)
    print("FINAL SELECTIVE VS CONVENTIONAL RESULTS")
    print("=" * 110)

    print(
        final.to_string(
            index=False,
            float_format=lambda x: f"{x:.4f}"
        )
    )

    # ---------------------------------------------------------
    # Summary
    # ---------------------------------------------------------

    improvements = final[
        final["selective_improvement_percent"] > 0
    ]

    print("\n")
    print("=" * 110)
    print("SUMMARY")
    print("=" * 110)

    print(
        f"Total evaluated cases: {len(final)}"
    )

    print(
        f"Cases where selective improves "
        f"physical 2Q cost: {len(improvements)}"
    )

    if not improvements.empty:

        print(
            f"Average improvement: "
            f"{improvements['selective_improvement_percent'].mean():.2f}%"
        )

        print(
            f"Maximum improvement: "
            f"{improvements['selective_improvement_percent'].max():.2f}%"
        )

        best_case = improvements.loc[
            improvements[
                "selective_improvement_percent"
            ].idxmax()
        ]

        print(
            "\nBest case:"
        )

        print(
            f"{int(best_case['qubits'])} qubits, "
            f"error budget "
            f"{best_case['error_budget']}"
        )

        print(
            f"Improvement: "
            f"{best_case['selective_improvement_percent']:.2f}%"
        )


if __name__ == "__main__":
    main()