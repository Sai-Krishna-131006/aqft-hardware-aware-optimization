from math import pi
from qiskit import transpile
from qiskit.transpiler import CouplingMap
from qiskit.quantum_info import Operator
from itertools import combinations
from src.qft_builder import create_qft


NUM_QUBITS = 5


def fidelity_error(exact_circuit, approx_circuit):
    exact_operator = Operator(exact_circuit).data
    approx_operator = Operator(approx_circuit).data

    dimension = 2 ** NUM_QUBITS

    fidelity = (
        abs(
            (exact_operator.conj().T @ approx_operator).trace()
        ) ** 2
        / dimension ** 2
    )

    return 1 - fidelity


def get_cp_gates(circuit):
    gates = []

    for index, instruction in enumerate(circuit.data):
        operation = instruction.operation

        if operation.name == "cp":
            control = instruction.qubits[0]._index
            target = instruction.qubits[1]._index
            angle = float(operation.params[0])

            gates.append(
                {
                    "index": index,
                    "control": control,
                    "target": target,
                    "angle": angle,
                }
            )

    return gates


def create_selective_circuit(exact_circuit, removed_indices):
    circuit = exact_circuit.copy()

    # Remove gates in reverse order so indices remain valid.
    for index in sorted(removed_indices, reverse=True):
        circuit.data.pop(index)

    return circuit


def transpile_and_measure(circuit):
    coupling = CouplingMap(
        [
            [0, 1],
            [1, 0],
            [1, 2],
            [2, 1],
            [2, 3],
            [3, 2],
            [3, 4],
            [4, 3],
        ]
    )

    transpiled = transpile(
        circuit,
        coupling_map=coupling,
        basis_gates=["u", "cx", "swap"],
        optimization_level=0,
        seed_transpiler=42,
    )

    return (
        transpiled.size(),
        transpiled.depth(),
        transpiled.num_nonlocal_gates(),
        transpiled.count_ops().get("swap", 0),
    )


def main():
    exact = create_qft(NUM_QUBITS)

    cp_gates = get_cp_gates(exact)

    print("\nExact QFT controlled-phase gates:")
    print("-" * 70)

    for gate in cp_gates:
        print(
            f"index={gate['index']:2d} | "
            f"{gate['control']} -> {gate['target']} | "
            f"angle={gate['angle']:.6f}"
        )

    print("\nSelective-gate experiments")
    print("=" * 70)

    # Group gates by angle.
    angle_groups = {}

    for gate in cp_gates:
        angle = gate["angle"]
        angle_groups.setdefault(angle, []).append(gate)

    results = []

    # Only test groups where multiple gates have the same angle.
    for angle, gates in sorted(angle_groups.items(), reverse=True):

        if len(gates) < 2:
            continue

        print(f"\nAngle = {angle:.6f}")
        print(f"Number of gates with this angle = {len(gates)}")

        # ---------------------------------------------------------
        # Remove TWO gates from the same-angle group
        # ---------------------------------------------------------

        for gate1, gate2 in combinations(gates, 2):

            removed_indices = [
                gate1["index"],
                gate2["index"]
            ]

            approx = create_selective_circuit(
                exact,
                removed_indices
            )

            error = fidelity_error(exact, approx)

            (
                total_gates,
                depth,
                two_qubit,
                swaps,
            ) = transpile_and_measure(approx)

            print(
                f"Removed "
                f"{gate1['control']}->{gate1['target']} + "
                f"{gate2['control']}->{gate2['target']} | "
                f"error={error:.6f} | "
                f"logical_2Q={approx.num_nonlocal_gates()} | "
                f"physical_2Q={two_qubit} | "
                f"SWAPs={swaps} | "
                f"depth={depth}"
            )

    print("\n" + "=" * 70)
    print("INTERPRETATION")
    print("=" * 70)

    if not results:
        print("No repeated-angle controlled-phase gates found.")
        return

    print(
        "\nWe tested whether removing different gates having the same "
        "rotation angle changes the post-transpilation hardware cost."
    )


if __name__ == "__main__":
    main()