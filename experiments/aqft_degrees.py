import csv
from pathlib import Path
from src.aqft_builder import create_aqft, calculate_approximation_error

results_dir = Path("results")
results_dir.mkdir(exist_ok=True)

qubit_sizes = [3, 4, 5, 6, 8]

csv_file = results_dir / "aqft_degree_results.csv"


with open(csv_file, "w", newline="") as file:

    writer = csv.writer(file)

    # CSV header
    writer.writerow([
        "qubits",
        "degree",
        "total_gates",
        "depth",
        "two_qubit_gates",
        "fidelity",
        "error"
    ])

    for n in qubit_sizes:

        max_degree = n * (n - 1) // 2

        print(f"\n{'=' * 70}")
        print(f"{n}-QUBIT AQFT")
        print(f"{'=' * 70}")

        for degree in range(max_degree + 1):

            qft = create_aqft(n, degree)

            fidelity, error = calculate_approximation_error(n, degree)

            two_qubit_gates = qft.num_nonlocal_gates()

            # Write result to CSV
            writer.writerow([
                n,
                degree,
                qft.size(),
                qft.depth(),
                two_qubit_gates,
                f"{fidelity:.10f}",
                f"{error:.10f}"
            ])

            # Print result to terminal
            print(
                f"Degree: {degree:2d} | "
                f"Gates: {qft.size():2d} | "
                f"Depth: {qft.depth():2d} | "
                f"2Q Gates: {two_qubit_gates:2d} | "
                f"Fidelity: {fidelity:.6f} | "
                f"Error: {error:.6f}"
            )


print(f"\nResults saved to: {csv_file}")