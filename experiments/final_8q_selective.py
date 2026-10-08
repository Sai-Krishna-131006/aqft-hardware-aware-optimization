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


NUM_QUBITS = 8

ERROR_BUDGETS = [0.01, 0.05, 0.10, 0.20]

THRESHOLDS = [
    0,
    pi / 64,
    pi / 32,
    pi / 16,
    pi / 8,
    pi / 4,
    pi / 2,
]

# Only selectively search these small-angle rotations.
SELECTIVE_MAX_ANGLE = pi / 16


def calculate_error(exact, approx):

    u_exact = Operator(exact).data
    u_approx = Operator(approx).data

    dimension = 2 ** NUM_QUBITS

    fidelity = (
        abs((u_exact.conj().T @ u_approx).trace()) ** 2
        / dimension ** 2
    )

    return 1 - fidelity


def transpile_measure(circuit):

    edges = []

    for i in range(NUM_QUBITS - 1):
        edges.append([i, i + 1])
        edges.append([i + 1, i])

    coupling = CouplingMap(edges)

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


def add_result(
    results,
    method,
    parameter,
    circuit,
    exact,
    extra=None
):

    error = calculate_error(
        exact,
        circuit
    )

    hardware = transpile_measure(
        circuit
    )

    row = {
        "method": method,
        "parameter": parameter,
        "error": error,
        "logical_2q": circuit.num_nonlocal_gates(),
        "physical_2q": hardware["physical_2q"],
        "swaps": hardware["swaps"],
        "depth": hardware["depth"],
    }

    if extra:
        row.update(extra)

    results.append(row)


def main():

    exact = create_qft(
        NUM_QUBITS
    )

    results = []

    # =========================================================
    # 1. DEGREE
    # =========================================================

    print(
        "Generating degree configurations..."
    )

    max_degree = (
        NUM_QUBITS
        * (NUM_QUBITS - 1)
        // 2
    )

    for degree in range(
        max_degree + 1
    ):

        circuit = create_aqft(
            NUM_QUBITS,
            degree
        )

        add_result(
            results,
            "degree",
            degree,
            circuit,
            exact
        )

    # =========================================================
    # 2. THRESHOLD
    # =========================================================

    print(
        "Generating threshold configurations..."
    )

    for threshold in THRESHOLDS:

        circuit = create_aqft_threshold(
            NUM_QUBITS,
            threshold
        )

        add_result(
            results,
            "threshold",
            threshold,
            circuit,
            exact
        )

    # =========================================================
    # 3. SELECTIVE
    #
    # Only small-angle gates <= pi/16.
    # =========================================================

    cp_gates = get_cp_gates(
        exact
    )

    selective_gates = [
        gate
        for gate in cp_gates
        if gate["angle"]
        <= SELECTIVE_MAX_ANGLE
    ]

    print(
        "\nSelective candidate gates:"
    )

    for gate in selective_gates:

        print(
            f"{gate['control']}->{gate['target']} "
            f"angle={gate['angle']:.6f}"
        )

    print(
        f"\nNumber of selectable gates: "
        f"{len(selective_gates)}"
    )

    total_candidates = (
        2 ** len(selective_gates)
    )

    print(
        f"Selective candidates: "
        f"{total_candidates:,}"
    )

    candidate_number = 0

    # Exhaustive search over ONLY
    # the small-angle subset.

    for number_removed in range(
        len(selective_gates) + 1
    ):

        for selected in combinations(
            selective_gates,
            number_removed
        ):

            removed_indices = [
                gate["index"]
                for gate in selected
            ]

            circuit = create_selective_circuit(
                exact,
                removed_indices
            )

            removed_names = ",".join(
                f"{gate['control']}->{gate['target']}"
                for gate in selected
            )

            add_result(
                results,
                "selective",
                removed_names,
                circuit,
                exact,
                {
                    "removed_count":
                        number_removed
                }
            )

            candidate_number += 1

            if (
                candidate_number % 1000 == 0
            ):

                print(
                    f"Processed "
                    f"{candidate_number:,}/"
                    f"{total_candidates:,}"
                )

    # =========================================================
    # SAVE
    # =========================================================

    os.makedirs(
        "results",
        exist_ok=True
    )

    output_file = (
        "results/final_8q_comparison.csv"
    )

    fieldnames = [
        "method",
        "parameter",
        "error",
        "logical_2q",
        "physical_2q",
        "swaps",
        "depth",
        "removed_count",
    ]

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

        for row in results:

            if "removed_count" not in row:
                row["removed_count"] = ""

            writer.writerow(row)

    print(
        f"\nSaved {len(results):,} configurations to "
        f"{output_file}"
    )

    # =========================================================
    # FINAL COMPARISON
    # =========================================================

    print("\n")
    print("=" * 110)
    print("FINAL 8-QUBIT COMPARISON")
    print("=" * 110)

    for budget in ERROR_BUDGETS:

        print(
            f"\nError budget = {budget}"
        )

        print("-" * 110)

        for method in [
            "threshold",
            "degree",
            "selective"
        ]:

            valid = [
                r
                for r in results
                if r["method"] == method
                and r["error"]
                    <= budget + 1e-12
            ]

            if not valid:

                print(
                    f"{method:10s} | "
                    "No valid configuration"
                )

                continue

            best = min(
                valid,
                key=lambda r: (
                    r["physical_2q"],
                    r["swaps"],
                    r["depth"],
                )
            )

            print(
                f"{method:10s} | "
                f"error={best['error']:.6f} | "
                f"physical_2q="
                f"{best['physical_2q']:2d} | "
                f"SWAPs="
                f"{best['swaps']:2d} | "
                f"depth="
                f"{best['depth']:2d} | "
                f"parameter="
                f"{best['parameter']}"
            )


if __name__ == "__main__":
    main()