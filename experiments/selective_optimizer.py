from itertools import combinations
from math import pi

from qiskit import transpile
from qiskit.transpiler import CouplingMap
from qiskit.quantum_info import Operator

from src.qft_builder import create_qft


NUM_QUBITS = 5
ERROR_BUDGETS = [0.01, 0.05, 0.10, 0.20]


def calculate_error(exact, approx):
    u_exact = Operator(exact).data
    u_approx = Operator(approx).data

    dimension = 2 ** NUM_QUBITS

    fidelity = (
        abs((u_exact.conj().T @ u_approx).trace()) ** 2
        / dimension ** 2
    )

    return 1 - fidelity


def get_cp_gates(circuit):
    gates = []

    for index, instruction in enumerate(circuit.data):
        if instruction.operation.name == "cp":
            gates.append({
                "index": index,
                "control": instruction.qubits[0]._index,
                "target": instruction.qubits[1]._index,
                "angle": float(instruction.operation.params[0])
            })

    return gates


def create_selective_circuit(exact, removed_indices):
    circuit = exact.copy()

    for index in sorted(removed_indices, reverse=True):
        circuit.data.pop(index)

    return circuit


def transpile_measure(circuit):
    coupling = CouplingMap([
        [0, 1], [1, 0],
        [1, 2], [2, 1],
        [2, 3], [3, 2],
        [3, 4], [4, 3]
    ])

    transpiled = transpile(
        circuit,
        coupling_map=coupling,
        basis_gates=["u", "cx", "swap"],
        optimization_level=0,
        seed_transpiler=42
    )

    return {
        "physical_2q": transpiled.num_nonlocal_gates(),
        "swaps": transpiled.count_ops().get("swap", 0),
        "depth": transpiled.depth(),
        "total_gates": transpiled.size()
    }


def main():
    exact = create_qft(NUM_QUBITS)
    cp_gates = get_cp_gates(exact)

    candidates = []

    # Test every possible subset of the 10 controlled-phase gates.
# For 5 qubits this is only 2^10 = 1024 candidates.

    for number_removed in range(len(cp_gates) + 1):

        for selected in combinations(cp_gates, number_removed):

            removed_indices = [
                gate["index"] for gate in selected
            ]

            approx = create_selective_circuit(
                exact,
                removed_indices
            )

            error = calculate_error(exact, approx)

            hardware = transpile_measure(approx)

            candidates.append({
                "removed": number_removed,
                "error": error,
                "physical_2q": hardware["physical_2q"],
                "swaps": hardware["swaps"],
                "depth": hardware["depth"],
                "gates": [
                    f"{gate['control']}->{gate['target']}"
                    for gate in selected
                ]
            })

    print("\nSelective AQFT optimization")
    print("=" * 80)

    print(f"Total candidates tested: {len(candidates)}")

    for budget in ERROR_BUDGETS:

        valid = [
            c for c in candidates
            if c["error"] <= budget + 1e-12
        ]

        if not valid:
            print(f"\nError budget = {budget}")
            print("No valid configuration.")
            continue

        best = min(
            valid,
            key=lambda c: (
                c["physical_2q"],
                c["swaps"],
                c["depth"]
            )
        )

        print(f"\nError budget = {budget}")
        print("-" * 80)

        print(
            f"Removed gates : "
            f"{best['gates'] if best['gates'] else 'None'}"
        )

        print(f"Error         : {best['error']:.6f}")
        print(f"Physical 2Q   : {best['physical_2q']}")
        print(f"SWAPs         : {best['swaps']}")
        print(f"Depth         : {best['depth']}")
        print(f"Removed count : {best['removed']}")


if __name__ == "__main__":
    main()