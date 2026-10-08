import csv
from math import pi
from pathlib import Path

from qiskit import transpile
from qiskit.transpiler import CouplingMap

from src.aqft_builder import create_aqft_threshold
from src.qft_builder import create_qft


# ============================================================
# SETTINGS
# ============================================================

qubit_sizes = [3, 4, 5, 6, 8]

output_file = Path("results/fine_threshold_results.csv")

optimization_level = 0
seed_transpiler = 42


# ============================================================
# LINEAR CONNECTIVITY
# ============================================================

def create_linear_coupling(num_qubits):

    edges = []

    for i in range(num_qubits - 1):
        edges.append([i, i + 1])
        edges.append([i + 1, i])

    return CouplingMap(edges)


# ============================================================
# DISTINCT THRESHOLDS
# ============================================================

def get_thresholds(num_qubits):

    """
    Return thresholds corresponding to the distinct
    controlled-phase angles present in the QFT.

    threshold = 0 gives the exact QFT.

    For a threshold equal to an angle, gates with
    that angle are removed because the AQFT builder
    uses:

        if angle > threshold
    """

    thresholds = [0.0]

    for distance in range(1, num_qubits):

        angle = pi / (2 ** distance)
        thresholds.append(angle)

    thresholds.sort()

    return thresholds


# ============================================================
# ERROR CALCULATION
# ============================================================

def calculate_error(exact_circuit, approximate_circuit):

    from qiskit.quantum_info import Operator

    exact_operator = Operator(exact_circuit).data
    approximate_operator = Operator(approximate_circuit).data

    dimension = 2 ** exact_circuit.num_qubits

    fidelity = (
        abs(
            (
                exact_operator.conj().T
                @ approximate_operator
            ).trace()
        ) ** 2
        / dimension ** 2
    )

    return 1 - fidelity


# ============================================================
# RUN EXPERIMENT
# ============================================================

results = []


for n in qubit_sizes:

    print()
    print("=" * 80)
    print(f"{n}-QUBIT FINE THRESHOLD SWEEP")
    print("=" * 80)

    exact_qft = create_qft(n)

    coupling_map = create_linear_coupling(n)

    thresholds = get_thresholds(n)

    for threshold in thresholds:

        aqft = create_aqft_threshold(n, threshold)

        error = calculate_error(
            exact_qft,
            aqft
        )

        transpiled = transpile(
            aqft,
            coupling_map=coupling_map,
            optimization_level=optimization_level,
            seed_transpiler=seed_transpiler
        )

        logical_two_qubit = aqft.num_nonlocal_gates()

        transpiled_two_qubit = transpiled.num_nonlocal_gates()

        swaps = transpiled.count_ops().get("swap", 0)

        logical_depth = aqft.depth()

        transpiled_depth = transpiled.depth()

        logical_gates = aqft.size()

        transpiled_gates = transpiled.size()

        results.append({
            "qubits": n,
            "threshold": threshold,
            "error": error,
            "logical_gates": logical_gates,
            "logical_depth": logical_depth,
            "logical_two_qubit": logical_two_qubit,
            "transpiled_gates": transpiled_gates,
            "transpiled_depth": transpiled_depth,
            "transpiled_two_qubit": transpiled_two_qubit,
            "swaps": swaps
        })

        print(
            f"threshold = {threshold:.10f} | "
            f"error = {error:.6f} | "
            f"logical 2Q = {logical_two_qubit:2d} | "
            f"transpiled 2Q = {transpiled_two_qubit:2d} | "
            f"SWAPs = {swaps:2d} | "
            f"depth = {transpiled_depth:3d}"
        )


# ============================================================
# SAVE CSV
# ============================================================

fieldnames = [
    "qubits",
    "threshold",
    "error",
    "logical_gates",
    "logical_depth",
    "logical_two_qubit",
    "transpiled_gates",
    "transpiled_depth",
    "transpiled_two_qubit",
    "swaps"
]


with open(output_file, "w", newline="") as file:

    writer = csv.DictWriter(
        file,
        fieldnames=fieldnames
    )

    writer.writeheader()
    writer.writerows(results)


# ============================================================
# SUMMARY
# ============================================================

print()
print("=" * 80)
print("FINE THRESHOLD SWEEP COMPLETE")
print("=" * 80)

print(f"Results saved to: {output_file}")
print(f"Total rows: {len(results)}")