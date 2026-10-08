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


NUM_QUBITS = 5
ERROR_BUDGETS = [0.01, 0.05, 0.10, 0.20]

THRESHOLDS = [
    0,
    pi / 16,
    pi / 8,
    pi / 4,
    pi / 2,
]


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
    coupling = CouplingMap([
        [0, 1], [1, 0],
        [1, 2], [2, 1],
        [2, 3], [3, 2],
        [3, 4], [4, 3],
    ])

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
            })

    return gates


def create_selective_circuit(exact, removed_indices):
    circuit = exact.copy()

    for index in sorted(removed_indices, reverse=True):
        circuit.data.pop(index)

    return circuit


def add_result(results, method, parameter, circuit, exact, extra=None):
    error = calculate_error(exact, circuit)
    hardware = transpile_measure(circuit)

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

    exact = create_qft(NUM_QUBITS)

    results = []

    # ---------------------------------------------------------
    # 1. Degree-based AQFT
    # ---------------------------------------------------------

    max_degree = NUM_QUBITS * (NUM_QUBITS - 1) // 2

    for degree in range(max_degree + 1):

        circuit = create_aqft(NUM_QUBITS, degree)

        add_result(
            results,
            "degree",
            degree,
            circuit,
            exact,
        )

    # ---------------------------------------------------------
    # 2. Threshold-based AQFT
    # ---------------------------------------------------------

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
            exact,
        )

    # ---------------------------------------------------------
    # 3. Selective AQFT
    #    Exhaustive search: 2^10 = 1024 candidates
    # ---------------------------------------------------------

    cp_gates = get_cp_gates(exact)

    for number_removed in range(len(cp_gates) + 1):

        for selected in combinations(
            cp_gates,
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
                    "removed_count": number_removed
                },
            )

    # ---------------------------------------------------------
    # Save raw results
    # ---------------------------------------------------------

    os.makedirs("results", exist_ok=True)

    output_file = (
        "results/final_5q_comparison.csv"
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
        f"\nSaved {len(results)} configurations to "
        f"{output_file}"
    )

    # ---------------------------------------------------------
    # Best configuration for each method/budget
    # ---------------------------------------------------------

    print("\nFINAL COMPARISON")
    print("=" * 100)

    for budget in ERROR_BUDGETS:

        print(f"\nError budget = {budget}")
        print("-" * 100)

        for method in [
            "threshold",
            "degree",
            "selective"
        ]:

            valid = [
                r for r in results
                if r["method"] == method
                and r["error"] <= budget + 1e-12
            ]

            if not valid:
                print(
                    f"{method:10s}: no valid configuration"
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
                f"physical_2q={best['physical_2q']:2d} | "
                f"SWAPs={best['swaps']:2d} | "
                f"depth={best['depth']:2d} | "
                f"parameter={best['parameter']}"
            )


if __name__ == "__main__":
    main()