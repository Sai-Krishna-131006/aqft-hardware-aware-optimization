## Hardware-Aware AQFT Optimization

The repository also contains the final AQFT hardware-aware optimization results.

The study evaluates degree-based and threshold-based AQFT configurations under approximation-error budgets of 0.01, 0.05, 0.10, and 0.20 for 3, 4, 5, 6, and 8 qubits. Configurations are evaluated after transpilation to a linear nearest-neighbor architecture.

The primary hardware objective is minimizing physical two-qubit gates while satisfying the approximation-error constraint. SWAP count and circuit depth are secondary metrics.

See [`docs/hardware_aware_optimization.md`](docs/hardware_aware_optimization.md) for the final analysis and [`results/hardware_aware_optimization.csv`](results/hardware_aware_optimization.csv) for the complete 20-case dataset.

The degree-based method reduced physical two-qubit cost relative to threshold-based selection in 5 of 20 cases, with a maximum observed reduction of 25.00%.
