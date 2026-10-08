from itertools import combinations
from math import pi
import csv
import os

from qiskit import transpile
from qiskit.transpiler import CouplingMap
from qiskit.quantum_info import Operator

from src.qft_builder import create_qft
from src.aqft_builder import create_aqft
from src.aqft_builder import create_aqft_threshold


QUBIT_SIZES = [3, 4, 5, 6, 8]

ERROR_BUDGETS = [0.01, 0.05, 0.10, 0.20]


def calculate_error(exact, approx):

    u_exact = Operator(exact).data
    u_approx = Operator(approx).data

    dimension = 2 ** approx.num_qubits

    fidelity = (
        abs(
            (u_exact.conj().T @ u_approx).trace()
        ) ** 2
        / dimension ** 2
    )

    return 1 - fidelity


def create_linear_coupling(num_qubits):

    edges = []

    for i in range(num_qubits - 1):
        edges.append([i, i + 1])
        edges.append([i + 1, i])

    return CouplingMap(edges)


def transpile_measure(circuit, coupling):

    transpiled = transpile(
        circuit,
        coupling_map=coupling,
        basis_gates=["u", "cx", "swap"],
        optimization_level=0,
        seed_transpiler=42,
    )

    return {
        "physical_2q": transpiled.num_nonlocal_gates(),
        "swaps": transpiled.count_ops().get("swap", 0),
        "depth": transpiled.depth(),
    }


def get_cp_gates(circuit):

    gates = []

    for index, instruction in enumerate(circuit.data):

        if instruction.operation.name == "cp":

            gates.append({
                "index": index,
                "control": instruction.qubits[0]._index,
                "target": instruction.qubits[1]._index,
                "angle": float(
                    instruction.operation.params[0]
                ),
            })

    return gates

def get_removed_cp_gates(exact, degree_circuit):
    """
    Return the exact CP gates removed by the degree circuit.
    This guarantees that the selective candidate pool matches
    the actual degree-based AQFT configuration.
    """

    exact_gates = get_cp_gates(exact)
    remaining_gates = get_cp_gates(degree_circuit)

    remaining_keys = {}

    for gate in remaining_gates:

        key = (
            gate["control"],
            gate["target"],
            round(gate["angle"], 12)
        )

        remaining_keys[key] = (
            remaining_keys.get(key, 0) + 1
        )

    removed = []

    for gate in exact_gates:

        key = (
            gate["control"],
            gate["target"],
            round(gate["angle"], 12)
        )

        if remaining_keys.get(key, 0) > 0:

            remaining_keys[key] -= 1

        else:

            removed.append(gate)

    return removed

def create_selective_circuit(
    exact,
    removed_indices
):

    circuit = exact.copy()

    for index in sorted(
        removed_indices,
        reverse=True
    ):
        circuit.data.pop(index)

    return circuit


def circuit_cost(
    error,
    hardware
):

    return (
        hardware["physical_2q"],
        hardware["swaps"],
        hardware["depth"],
    )


def best_valid(results, budget):

    valid = [
        r for r in results
        if r["error"] <= budget + 1e-12
    ]

    if not valid:
        return None

    return min(
        valid,
        key=lambda r: (
            r["physical_2q"],
            r["swaps"],
            r["depth"],
        )
    )


def main():

    os.makedirs(
        "results",
        exist_ok=True
    )

    final_rows = []

    for num_qubits in QUBIT_SIZES:

        print("\n")
        print("=" * 100)
        print(f"{num_qubits}-QUBIT EXPERIMENT")
        print("=" * 100)

        exact = create_qft(num_qubits)

        coupling = create_linear_coupling(
            num_qubits
        )

        cp_gates = get_cp_gates(exact)


        # =====================================================
        # DEGREE CONFIGURATIONS
        # =====================================================

        print(
            "\nGenerating degree configurations..."
        )

        degree_results = []

        max_degree = len(cp_gates)

        for degree in range(
            max_degree + 1
        ):

            circuit = create_aqft(
                num_qubits,
                degree
            )

            error = calculate_error(
                exact,
                circuit
            )

            hardware = transpile_measure(
                circuit,
                coupling
            )

            degree_results.append({
                "degree": degree,
                "error": error,
                **hardware,
            })

        # =====================================================
        # THRESHOLD CONFIGURATIONS
        # =====================================================

        print(
            "Generating threshold configurations..."
        )

        threshold_values = [
            0
        ]

        for distance in range(
            1,
            num_qubits
        ):
            threshold_values.append(
                pi / (2 ** distance)
            )

        threshold_results = []

        for threshold in threshold_values:

            circuit = create_aqft_threshold(
                num_qubits,
                threshold
            )

            error = calculate_error(
                exact,
                circuit
            )

            hardware = transpile_measure(
                circuit,
                coupling
            )

            threshold_results.append({
                "threshold": threshold,
                "error": error,
                **hardware,
            })

        # =====================================================
        # SELECTIVE SEARCH
        # =====================================================

        # Cache selective candidates so that the same subset
        # does not need to be regenerated repeatedly.

        selective_cache = {}

        print(
            "\nSelecting candidate pools from degree results..."
        )

        for budget in ERROR_BUDGETS:

            # -------------------------------------------------
            # Best degree configuration for this error budget
            # -------------------------------------------------

            best_degree = best_valid(
                [
                    {
                        **r,
                        "parameter": r["degree"]
                    }
                    for r in degree_results
                ],
                budget
            )

            # -------------------------------------------------
            # Best threshold configuration
            # -------------------------------------------------

            best_threshold = best_valid(
                [
                    {
                        **r,
                        "parameter": r["threshold"]
                    }
                    for r in threshold_results
                ],
                budget
            )

            if best_degree is None:
                print(
                    f"No valid degree configuration "
                    f"for budget {budget}"
                )
                continue

            degree_value = int(
                best_degree["degree"]
            )

            # -------------------------------------------------
            # Candidate pool
            #
            # IMPORTANT:
            # derive the pool directly from the actual degree
            # circuit rather than assuming gate ordering.
            # -------------------------------------------------

            degree_circuit = create_aqft(
                num_qubits,
                degree_value
            )

            candidate_gates = get_removed_cp_gates(
                exact,
                degree_circuit
            )

            candidate_count = (
                2 ** len(candidate_gates)
            )

            print(
                f"\nBudget {budget}"
            )

            print(
                f"Best degree = {degree_value}"
            )

            print(
                f"Degree error = "
                f"{best_degree['error']:.6f}"
            )

            print(
                f"Selective candidate gates = "
                f"{len(candidate_gates)}"
            )

            print(
                f"Selective combinations = "
                f"{candidate_count:,}"
            )

            # -------------------------------------------------
            # Search every subset of candidate gates
            # -------------------------------------------------

            selective_results = []

            for number_removed in range(
                len(candidate_gates) + 1
            ):

                for selected in combinations(
                    candidate_gates,
                    number_removed
                ):

                    removed_indices = tuple(
                        sorted(
                            gate["index"]
                            for gate in selected
                        )
                    )

                    if removed_indices in selective_cache:

                        result = selective_cache[
                            removed_indices
                        ]

                    else:

                        circuit = (
                            create_selective_circuit(
                                exact,
                                removed_indices
                            )
                        )

                        error = calculate_error(
                            exact,
                            circuit
                        )

                        hardware = (
                            transpile_measure(
                                circuit,
                                coupling
                            )
                        )

                        result = {
                            "error": error,
                            **hardware,
                            "removed": ",".join(
                                f"{gate['control']}->{gate['target']}"
                                for gate in selected
                            ),
                            "removed_count":
                                number_removed,
                        }

                        selective_cache[
                            removed_indices
                        ] = result

                    selective_results.append(
                        result
                    )

            best_selective = best_valid(
                selective_results,
                budget
            )

            # -------------------------------------------------
            # Save final comparison
            # -------------------------------------------------

            final_rows.append({
                "qubits": num_qubits,
                "error_budget": budget,

                "threshold_error":
                    best_threshold["error"],

                "threshold_2q":
                    best_threshold["physical_2q"],

                "threshold_swaps":
                    best_threshold["swaps"],

                "threshold_depth":
                    best_threshold["depth"],

                "threshold_parameter":
                    best_threshold["parameter"],

                "degree":
                    best_degree["degree"],

                "degree_error":
                    best_degree["error"],

                "degree_2q":
                    best_degree["physical_2q"],

                "degree_swaps":
                    best_degree["swaps"],

                "degree_depth":
                    best_degree["depth"],

                "selective_error":
                    best_selective["error"],

                "selective_2q":
                    best_selective["physical_2q"],

                "selective_swaps":
                    best_selective["swaps"],

                "selective_depth":
                    best_selective["depth"],

                "selective_removed":
                    best_selective["removed"],

                "selective_removed_count":
                    best_selective["removed_count"],

                "candidate_count":
                    candidate_count,
            })

            print(
                f"Best selective: "
                f"error={best_selective['error']:.6f}, "
                f"physical_2q="
                f"{best_selective['physical_2q']}, "
                f"SWAPs="
                f"{best_selective['swaps']}, "
                f"depth="
                f"{best_selective['depth']}"
            )

    # =========================================================
    # SAVE FINAL DATASET
    # =========================================================

    output_file = (
        "results/unified_final_comparison.csv"
    )

    fieldnames = list(
        final_rows[0].keys()
    )

    with open(
        output_file,
        "w",
        newline=""
    ) as f:

        writer = csv.DictWriter(
            f,
            fieldnames=fieldnames
        )

        writer.writeheader()
        writer.writerows(final_rows)

    print("\n")
    print("=" * 100)
    print("UNIFIED FINAL RESULTS")
    print("=" * 100)

    for row in final_rows:

        print(
            f"{row['qubits']}Q | "
            f"E<={row['error_budget']} | "
            f"Threshold={row['threshold_2q']} | "
            f"Degree={row['degree_2q']} | "
            f"Selective={row['selective_2q']} | "
            f"Selective error="
            f"{row['selective_error']:.6f}"
        )

    print(
        f"\nSaved to: {output_file}"
    )


if __name__ == "__main__":
    main()