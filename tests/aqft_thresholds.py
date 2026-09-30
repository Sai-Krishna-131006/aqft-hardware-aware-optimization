import csv
from math import pi
from pathlib import Path

from src.aqft_builder import (
    create_aqft_threshold,
    calculate_threshold_error
)


qubit_sizes = [3, 4, 5, 6, 8]

# Thresholds are chosen from the QFT rotation angles
thresholds = [
    0,
    pi / 16,
    pi / 8,
    pi / 4,
    pi / 2
]

results_dir = Path("results")
results_dir.mkdir(exist_ok=True)

csv_file = results_dir / "aqft_threshold_results.csv"


with open(csv_file, "w", newline="") as file:

    writer = csv.writer(file)

    writer.writerow([
        "qubits",
        "threshold",
        "total_gates",
        "depth",
        "two_qubit_gates",
        "fidelity",
        "error"
    ])

    for n in qubit_sizes:

        print(f"\n{'=' * 70}")
        print(f"{n}-QUBIT THRESHOLD AQFT")
        print(f"{'=' * 70}")

        for threshold in thresholds:

            qft = create_aqft_threshold(n, threshold)

            fidelity, error = calculate_threshold_error(
                n,
                threshold
            )

            two_qubit_gates = qft.num_nonlocal_gates()

            writer.writerow([
                n,
                f"{threshold:.10f}",
                qft.size(),
                qft.depth(),
                two_qubit_gates,
                f"{fidelity:.10f}",
                f"{error:.10f}"
            ])

            print(
                f"Threshold: {threshold:.6f} | "
                f"Gates: {qft.size():2d} | "
                f"Depth: {qft.depth():2d} | "
                f"2Q Gates: {two_qubit_gates:2d} | "
                f"Fidelity: {fidelity:.6f} | "
                f"Error: {error:.6f}"
            )


print(f"\nResults saved to: {csv_file}")