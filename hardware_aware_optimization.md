# Hardware-Aware AQFT Optimization Results

## Objective

Evaluate AQFT configurations under an approximation-error constraint and select the configuration with the lowest **post-transpilation physical two-qubit gate count**.

Secondary hardware metrics are SWAP count and circuit depth.

**Optimization criterion:** minimize physical 2Q gates subject to approximation error <= error budget.

**Qubit sizes:** 3, 4, 5, 6, 8  
**Error budgets:** 0.01, 0.05, 0.10, 0.20  
**Hardware model:** linear nearest-neighbor connectivity with Qiskit transpilation.

## Final optimization table

| Qubits | Error budget | Threshold physical 2Q | Degree physical 2Q | Reduction |
|---:|---:|---:|---:|---:|
| 3 | 0.01 | 7 | 7 | 0.00% |
| 3 | 0.05 | 7 | 7 | 0.00% |
| 3 | 0.10 | 7 | 7 | 0.00% |
| 3 | 0.20 | 4 | 4 | 0.00% |
| 4 | 0.01 | 16 | 16 | 0.00% |
| 4 | 0.05 | 12 | 12 | 0.00% |
| 4 | 0.10 | 12 | 12 | 0.00% |
| 4 | 0.20 | 12 | **9** | **25.00%** |
| 5 | 0.01 | 26 | 26 | 0.00% |
| 5 | 0.05 | 26 | **21** | **19.23%** |
| 5 | 0.10 | 18 | 18 | 0.00% |
| 5 | 0.20 | 18 | 18 | 0.00% |
| 6 | 0.01 | 42 | 42 | 0.00% |
| 6 | 0.05 | 36 | 36 | 0.00% |
| 6 | 0.10 | 36 | **32** | **11.11%** |
| 6 | 0.20 | 24 | 24 | 0.00% |
| 8 | 0.01 | 72 | 72 | 0.00% |
| 8 | 0.05 | 72 | **65** | **9.72%** |
| 8 | 0.10 | 62 | 62 | 0.00% |
| 8 | 0.20 | 62 | **47** | **24.19%** |

Reduction = `(threshold physical 2Q - degree physical 2Q) / threshold physical 2Q × 100`.

## Main observations

- Degree-based selection improved post-transpilation physical two-qubit cost in **5 of 20** tested cases.
- The largest observed reduction was **25.00%** for 4 qubits at error budget 0.20.
- The 8-qubit case at error budget 0.20 produced a **24.19%** reduction, from 62 to 47 physical two-qubit gates.
- The average reduction over all 20 cases was approximately **4.46%**.
- Threshold and degree truncation produced identical hardware costs in many cases.
- The results support **hardware-aware AQFT configuration selection**, rather than a claim that one truncation method is universally superior.

## Selective pruning

Selective pruning was evaluated as a secondary experiment using the controlled-phase gates removed by the corresponding degree configuration as its candidate pool.

In most cases, the selective result matched the degree result.

**6 qubits, error budget 0.10**

| Method | Error | Physical 2Q | SWAPs | Depth |
|---|---:|---:|---:|---:|
| Degree | 0.062487 | 32 | 10 | 47 |
| Selective | 0.053449 | 32 | **8** | 49 |

Selective pruning did not reduce physical two-qubit count in this case, but it reduced SWAP count from 10 to 8 while obtaining lower approximation error. It is therefore treated as a **secondary observation**, not the primary contribution.

## Reproducibility

- Full numeric table: [`hardware_aware_optimization.csv`](../results/hardware_aware_optimization.csv)
- Experiment scripts and other result files are stored under the `experiments/` and `results/` directories.

## Interpretation

The central result is that logical AQFT resource reduction does not completely determine hardware cost. After mapping to a constrained linear architecture, routing overhead can change the relative cost of otherwise valid approximation configurations.

This motivates selecting AQFT configurations using **post-transpilation hardware cost subject to an approximation-error budget**.
