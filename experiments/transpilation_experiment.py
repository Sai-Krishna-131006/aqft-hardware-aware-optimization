import csv
from math import pi
from pathlib import Path

from qiskit import transpile
from qiskit.transpiler import CouplingMap

from src.aqft_builder import (
    create_aqft,
    create_aqft_threshold,
    calculate_approximation_error,
    calculate_threshold_error
)


# --------------------------------------------------
# Configuration
# --------------------------------------------------

qubit_sizes = [3, 4, 5, 6, 8]

results_file = Path("results/transpilation_results.csv")

results = []


# --------------------------------------------------
# Run one experiment
# --------------------------------------------------

def run_experiment(n, method, parameter, circuit, error, coupling):

    # Logical metrics
    logical_gates = circuit.size()
    logical_depth = circuit.depth()
    logical_two_qubit = circuit.num_nonlocal_gates()

    # Transpile to linear hardware
    transpiled = transpile(
        circuit,
        coupling_map=coupling,
        optimization_level=0,
        basis_gates=["u", "cx", "swap"],
        seed_transpiler=42
    )

    # Transpiled metrics
    transpiled_gates = transpiled.size()
    transpiled_depth = transpiled.depth()
    transpiled_two_qubit = transpiled.num_nonlocal_gates()

    # Number of SWAP gates
    swap_count = transpiled.count_ops().get("swap", 0)

    # Store result
    results.append({
        "qubits": n,
        "method": method,
        "parameter": parameter,
        "error": error,
        "logical_gates": logical_gates,
        "logical_depth": logical_depth,
        "logical_two_qubit": logical_two_qubit,
        "transpiled_gates": transpiled_gates,
        "transpiled_depth": transpiled_depth,
        "transpiled_two_qubit": transpiled_two_qubit,
        "swaps": swap_count
    })

    print(
        f"{method:10} | "
        f"Parameter: {str(parameter):8} | "
        f"Error: {error:.6f} | "
        f"Logical 2Q: {logical_two_qubit:2} | "
        f"Transpiled 2Q: {transpiled_two_qubit:2} | "
        f"Depth: {transpiled_depth:2} | "
        f"SWAPs: {swap_count:2}"
    )


# --------------------------------------------------
# Run experiments for each qubit size
# --------------------------------------------------

for n in qubit_sizes:

    print("\n" + "=" * 80)
    print(f"{n}-QUBIT HARDWARE-AWARE AQFT EXPERIMENT")
    print("=" * 80)

    # --------------------------------------------------
    # Linear hardware topology
    # --------------------------------------------------

    coupling = CouplingMap(
        [
            [i, i + 1]
            for i in range(n - 1)
        ]
        +
        [
            [i + 1, i]
            for i in range(n - 1)
        ]
    )

    # --------------------------------------------------
    # Degree-based AQFT
    # --------------------------------------------------

    print("\nDEGREE-BASED AQFT")
    print("-" * 80)

    # Total number of controlled-phase gates in exact QFT
    max_degree = n * (n - 1) // 2

    for degree in range(max_degree + 1):

        circuit = create_aqft(n, degree)

        fidelity, error = calculate_approximation_error(
            n,
            degree
        )

        run_experiment(
            n,
            "degree",
            degree,
            circuit,
            error,
            coupling
        )

    # --------------------------------------------------
    # Threshold-based AQFT
    # --------------------------------------------------

    print("\nTHRESHOLD-BASED AQFT")
    print("-" * 80)

    thresholds = [
        0,
        pi / 16,
        pi / 8,
        pi / 4,
        pi / 2
    ]

    for threshold in thresholds:

        circuit = create_aqft_threshold(
            n,
            threshold
        )

        fidelity, error = calculate_threshold_error(
            n,
            threshold
        )

        run_experiment(
            n,
            "threshold",
            threshold,
            circuit,
            error,
            coupling
        )


# --------------------------------------------------
# Save results
# --------------------------------------------------

with open(results_file, "w", newline="") as file:

    writer = csv.DictWriter(
        file,
        fieldnames=[
            "qubits",
            "method",
            "parameter",
            "error",
            "logical_gates",
            "logical_depth",
            "logical_two_qubit",
            "transpiled_gates",
            "transpiled_depth",
            "transpiled_two_qubit",
            "swaps"
        ]
    )

    writer.writeheader()
    writer.writerows(results)


print("\n" + "=" * 80)
print("Results saved to:")
print(results_file)
print("=" * 80)