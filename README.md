# Hardware-Aware Approximate Quantum Fourier Transform Optimization

## Overview

This project studies the optimization of the **Quantum Fourier Transform (QFT)** using **Approximate Quantum Fourier Transform (AQFT)** techniques under hardware connectivity constraints.

The exact QFT contains controlled-phase rotations with progressively smaller rotation angles. AQFT reduces circuit resources by removing selected small-angle controlled-phase rotations, introducing approximation error in exchange for lower circuit cost.

The main research question is:

> **How does the choice of AQFT approximation level affect hardware resource savings and approximation error before and after hardware-constrained transpilation?**

The study evaluates AQFT for:

- 3 qubits
- 4 qubits
- 5 qubits
- 6 qubits
- 8 qubits

The circuits are transpiled to a **linear nearest-neighbor (LNN)** architecture to study the effect of limited qubit connectivity and routing overhead.

---

## Research Objective

The main optimization problem is formulated as:

$$
\min C_{\text{hardware}}
\quad \text{subject to} \quad
E_{\text{approx}} \leq E_{\max}
$$

where:

- $C_{\text{hardware}}$ = hardware-level circuit cost
- $E_{\text{approx}}$ = approximation error introduced by AQFT
- $E_{\max}$ = maximum acceptable approximation error

The primary hardware cost used in this work is the number of physical two-qubit gates after transpilation:

$$
C_{\text{hardware}} = N_{2Q}^{\text{physical}}
$$

SWAP count and circuit depth are used as secondary hardware metrics.

The optimization therefore prioritizes:

1. Minimum physical two-qubit gates
2. Minimum SWAP count when the primary cost is equal
3. Minimum circuit depth when the above are equal

---

# QFT Construction

For an $n$-qubit system, the QFT transformation is:

$$
QFT|x\rangle =
\frac{1}{\sqrt{N}}
\sum_{y=0}^{N-1}
e^{2\pi ixy/N}|y\rangle
$$

where:

$$
N = 2^n
$$

The QFT circuit consists mainly of:

- Hadamard gates
- Controlled-phase rotations

The controlled-phase gate is represented by:

$$
CP(\theta)=
\begin{bmatrix}
1&0&0&0\\
0&1&0&0\\
0&0&1&0\\
0&0&0&e^{i\theta}
\end{bmatrix}
$$

The QFT contains progressively smaller rotation angles:

$$
\frac{\pi}{2},
\frac{\pi}{4},
\frac{\pi}{8},
\frac{\pi}{16},
\dots
$$

These small-angle rotations are the main candidates for AQFT approximation.

---

# Exact QFT Validation

Before performing the approximation experiments, the manually implemented QFT was validated against Qiskit's QFT synthesis.

The comparison was performed using the mathematical unitary matrices of the circuits.

Two circuits were considered equivalent when their unitaries were equivalent up to global phase.

The exact QFT implementation was validated for:

$$
n \in \{3,4,5,6,8\}
$$

qubits.

---

# AQFT Approximation

AQFT reduces the QFT circuit by removing selected controlled-phase rotations.

The fundamental trade-off is:

$$
\text{Lower circuit cost}
\quad\Longleftrightarrow\quad
\text{Higher approximation error}
$$

Therefore, the objective is not simply to remove as many gates as possible.

Instead, the experiment searches for the lowest hardware cost while satisfying a specified approximation-error constraint.

---

# Approximation Error

Let:

$$
U_{\text{exact}}
$$

represent the exact QFT unitary and:

$$
U_{\text{AQFT}}
$$

represent the approximate QFT unitary.

For an $n$-qubit system:

$$
d = 2^n
$$

The unitary fidelity is calculated as:

$$
F_U =
\frac{
\left|
\mathrm{Tr}
\left(
U_{\text{exact}}^\dagger U_{\text{AQFT}}
\right)
\right|^2
}{
d^2
}
$$

The approximation error is then:

$$
E_{\text{approx}} = 1-F_U
$$

Therefore:

- $E_{\text{approx}}=0$ means no approximation error.
- Larger $E_{\text{approx}}$ means greater deviation from the exact QFT.

---

# Experimental Error Budgets

Four approximation-error budgets were used throughout the hardware-aware optimization experiment:

$$
E_{\max}\in\{0.01,\;0.05,\;0.10,\;0.20\}
$$

These represent increasingly relaxed approximation constraints.

| Error Budget | Interpretation |
|---:|---|
| 0.01 | Very strict approximation |
| 0.05 | Strict approximation |
| 0.10 | Moderate approximation |
| 0.20 | Relaxed approximation |

For every qubit size and every error budget, only AQFT configurations satisfying:

$$
E_{\text{approx}}\leq E_{\max}
$$

are considered valid.

Among the valid configurations, the configuration with the lowest physical two-qubit cost is selected.

This gives four independent optimization experiments for every qubit size.

---

# Degree-Based AQFT

In the degree-based approach, the approximation level is defined by the number of smallest-angle controlled-phase gates removed from the exact QFT.

For example:

- Degree 0 = exact QFT
- Degree 1 = remove one smallest-angle rotation
- Degree 2 = remove two smallest-angle rotations
- Degree 3 = remove three smallest-angle rotations
- etc.

For each degree, the following quantities are measured:

- Total logical gate count
- Logical circuit depth
- Logical two-qubit gate count
- Approximation error
- Transpiled physical gate count
- Transpiled circuit depth
- Physical two-qubit gate count
- SWAP count

The degree-based method provides a fine-grained approximation-error/resource trade-off.

---

# Threshold-Based AQFT

The threshold-based approach removes controlled-phase rotations according to their rotation angle.

A controlled-phase gate is removed when:

$$
\theta \leq \theta_{\text{threshold}}
$$

and retained when:

$$
\theta > \theta_{\text{threshold}}
$$

Thus, the threshold determines how aggressively small-angle rotations are removed.

The threshold approach and degree approach are two different parameterizations of the same basic AQFT principle: removing small-angle controlled-phase rotations.

---

# Hardware-Constrained Transpilation

Logical QFT circuits do not necessarily satisfy the connectivity constraints of a real quantum processor.

This experiment uses a **linear nearest-neighbor (LNN)** architecture.

For example, a 5-qubit architecture is:

```text
q0 ---- q1 ---- q2 ---- q3 ---- q4
```

Only neighboring qubits can directly interact.

If a logical circuit requires an interaction between non-adjacent qubits, the transpiler introduces routing operations such as SWAP gates.

Therefore:

$$
\text{Logical gate reduction}
\neq
\text{Physical gate reduction}
$$

This distinction is central to the experiment.

An AQFT circuit with fewer logical gates may not always produce the lowest hardware cost after transpilation.

---

# Transpilation Configuration

The experiments use the following transpilation configuration:

```python
optimization_level = 0
basis_gates = ["u", "cx", "swap"]
seed_transpiler = 42
```

The coupling map represents a linear nearest-neighbor architecture with bidirectional connections.

The same transpilation configuration is used for the compared AQFT methods to maintain a consistent experimental setup.

---

# Hardware-Aware Optimization Procedure

For each qubit size:

$$
n\in\{3,4,5,6,8\}
$$

and each error budget:

$$
E_{\max}\in\{0.01,0.05,0.10,0.20\}
$$

the following procedure is performed.

### Step 1 — Generate Exact QFT

Construct the exact QFT circuit.

### Step 2 — Generate AQFT Configurations

Generate AQFT circuits using:

- Degree-based approximation
- Threshold-based approximation

### Step 3 — Calculate Approximation Error

For every AQFT configuration:

$$
E_{\text{approx}} = 1-F_U
$$

### Step 4 — Transpile to LNN Hardware

Each circuit is transpiled to the same linear connectivity architecture.

### Step 5 — Measure Hardware Cost

The following are recorded:

$$
N_{2Q}^{\text{physical}}
$$

$$
N_{\text{SWAP}}
$$

$$
D_{\text{physical}}
$$

where:

- $N_{2Q}^{\text{physical}}$ = physical two-qubit gates
- $N_{\text{SWAP}}$ = SWAP gates
- $D_{\text{physical}}$ = transpiled circuit depth

### Step 6 — Apply Error Constraint

Only configurations satisfying:

$$
E_{\text{approx}}\leq E_{\max}
$$

are retained.

### Step 7 — Select the Hardware-Efficient Configuration

The valid configuration with the minimum physical two-qubit gate count is selected.

The optimization can therefore be written as:

$$
\min_{c\in C}
N_{2Q}^{\text{physical}}(c)
$$

subject to:

$$
E_{\text{approx}}(c)\leq E_{\max}
$$

where $C$ is the set of tested AQFT configurations.

---

# Physical Two-Qubit Gate Reduction

To compare the threshold-based and degree-based approaches, the physical two-qubit gate reduction is calculated as:

$$
\text{Reduction}(\%) =
\frac{
N_{2Q}^{\text{threshold}}
-
N_{2Q}^{\text{degree}}
}{
N_{2Q}^{\text{threshold}}
}
\times100
$$

A positive value means that the degree-based selection achieves a lower physical two-qubit cost than the threshold-based selection under the same error budget.

This metric is referred to as:

> **Physical 2Q gate reduction (%)**

rather than a generic optimization percentage.

---

# Final Hardware-Aware Results

| Qubits | Error Budget | Threshold Physical 2Q | Degree Physical 2Q | Physical 2Q Reduction |
|---:|---:|---:|---:|---:|
| 3 | 0.01 | 7 | 7 | 0.00% |
| 3 | 0.05 | 7 | 7 | 0.00% |
| 3 | 0.10 | 7 | 7 | 0.00% |
| 3 | 0.20 | 4 | 4 | 0.00% |
| 4 | 0.01 | 16 | 16 | 0.00% |
| 4 | 0.05 | 12 | 12 | 0.00% |
| 4 | 0.10 | 12 | 12 | 0.00% |
| 4 | 0.20 | 12 | 9 | 25.00% |
| 5 | 0.01 | 26 | 26 | 0.00% |
| 5 | 0.05 | 26 | 21 | 19.23% |
| 5 | 0.10 | 18 | 18 | 0.00% |
| 5 | 0.20 | 18 | 18 | 0.00% |
| 6 | 0.01 | 42 | 42 | 0.00% |
| 6 | 0.05 | 36 | 36 | 0.00% |
| 6 | 0.10 | 36 | 32 | 11.11% |
| 6 | 0.20 | 24 | 24 | 0.00% |
| 8 | 0.01 | 72 | 72 | 0.00% |
| 8 | 0.05 | 72 | 65 | 9.72% |
| 8 | 0.10 | 62 | 62 | 0.00% |
| 8 | 0.20 | 62 | 47 | 24.19% |

---

# Results Interpretation

The experiments show that degree-based and threshold-based AQFT follow the same fundamental resource-accuracy trade-off because both remove small-angle controlled-phase rotations.

However, their parameterizations do not always select the same approximation level for a given error budget.

The degree-based search provides a more fine-grained selection of possible truncation levels.

## Main observations

### 1. Hardware cost decreases with more aggressive approximation

Removing controlled-phase rotations generally reduces the number of logical two-qubit gates.

After transpilation, this can also reduce routing overhead and physical two-qubit gates.

### 2. Approximation error increases with more aggressive truncation

Removing more rotations produces a larger deviation from the exact QFT.

Therefore, the error constraint is necessary when selecting an AQFT configuration.

### 3. Logical and physical costs are different

A reduction in logical gate count does not necessarily produce the same reduction in physical gate count.

The hardware topology can introduce additional routing operations.

### 4. Degree-based selection improves hardware cost in selected cases

The degree-based approach produced a lower physical two-qubit count than the threshold-based approach in:

$$
5/20
$$

tested qubit-size/error-budget combinations.

The maximum observed physical two-qubit reduction was:

$$
25.00\%
$$

at 4 qubits with:

$$
E_{\max}=0.20
$$

where the physical two-qubit count decreased from:

$$
12\rightarrow9
$$

### 5. The improvement is not universal

In many cases, the threshold and degree approaches selected configurations with the same physical hardware cost.

Therefore, the results do not indicate that degree-based AQFT is universally superior.

Instead, they demonstrate that **hardware-aware selection of the approximation level can produce lower physical cost for certain error constraints and circuit sizes**.

---

# Selective Controlled-Phase Pruning

A secondary experiment investigates whether the controlled-phase gates removed by a conventional degree-based approximation can be selected individually rather than removing them as a fixed group.

The optimization uses the same constraint:

$$
E_{\text{approx}}\leq E_{\max}
$$

and the same hardware objective:

$$
\min N_{2Q}^{\text{physical}}
$$

This experiment tests whether the physical location of removed gates affects routing overhead.

The results show that selective pruning generally produces the same solution as the degree-based configuration for the tested cases.

Some cases show additional hardware-level improvements.

## 6 qubits, $E_{\max}=0.10$

Degree-based:

```text
Physical 2Q gates = 32
SWAPs              = 10
Depth              = 47
Error              = 0.062487
```

Selective:

```text
Physical 2Q gates = 32
SWAPs              = 8
Depth              = 49
Error              = 0.053449
```

The physical two-qubit count remains the same, but selective pruning reduces the number of SWAP gates.

## 8 qubits, $E_{\max}=0.10$

Degree-based:

```text
Physical 2Q gates = 62
SWAPs              = 26
Depth              = 79
Error              = 0.057350
```

Selective:

```text
Physical 2Q gates = 61
SWAPs              = 23
Depth              = 75
Error              = 0.050259
```

This demonstrates that the location of the removed controlled-phase gates can affect hardware routing cost, even when the number of removed gates is similar.

Selective pruning is therefore treated as a **secondary exploratory extension** rather than the primary contribution.

---

# Experimental Workflow

```text
Exact QFT
    |
    v
Generate AQFT configurations
    |
    +--------------------+
    |                    |
    v                    v
Degree-based        Threshold-based
AQFT                AQFT
    |                    |
    +---------+----------+
              |
              v
      Calculate Unitary
      Approximation Error
              |
              v
       Apply Error Budget
              |
              v
      Hardware Transpilation
              |
              v
    Linear Nearest-Neighbor
           Architecture
              |
              v
    +---------+---------+
    |         |         |
    v         v         v
Physical    SWAP      Depth
  2Q gates   Count
    |
    v
Hardware-Aware Selection
```

---

# Experimental Parameters

| Parameter | Values |
|---|---|
| Qubit sizes | 3, 4, 5, 6, 8 |
| AQFT methods | Degree, Threshold |
| Error budgets | 0.01, 0.05, 0.10, 0.20 |
| Hardware topology | Linear nearest-neighbor |
| Primary hardware metric | Physical 2Q gates |
| Secondary metrics | SWAP count, depth |
| Transpiler optimization | Level 0 |
| Basis gates | `u`, `cx`, `swap` |
| Transpiler seed | 42 |

---

# Reproducibility

The experiments are implemented using Python and Qiskit.

The transpilation experiments use a fixed transpiler seed:

```python
seed_transpiler = 42
```

This helps maintain consistent transpilation behavior when reproducing the experiments.

The same hardware topology, transpilation configuration, error calculation, and optimization criteria are applied across the tested configurations.

---

# Conclusion

This project demonstrates a hardware-aware evaluation of AQFT approximation strategies.

The key observation is that minimizing logical QFT resources alone does not fully describe the cost of executing a circuit on constrained hardware. Connectivity limitations can introduce additional SWAP gates and physical two-qubit operations during transpilation.

By formulating AQFT selection as:

$$
\min N_{2Q}^{\text{physical}}
\quad
\text{subject to}
\quad
E_{\text{approx}}\leq E_{\max}
$$

the approximation level can be selected according to both:

1. **Accuracy requirements**
2. **Hardware execution cost**

Across 20 qubit-size/error-budget combinations, the degree-based approach achieved a lower physical two-qubit cost in 5 cases, with a maximum observed reduction of 25.00%.

The selective pruning experiments additionally indicate that the physical location of removed controlled-phase gates can influence routing overhead, although the selective strategy generally produces results similar to conventional degree-based AQFT.

Overall, the experiments demonstrate the importance of evaluating AQFT **after hardware-constrained transpilation**, rather than considering only the logical circuit gate count.

---

# Key Formulae

### QFT

$$
QFT|x\rangle =
\frac{1}{\sqrt{N}}
\sum_{y=0}^{N-1}
e^{2\pi ixy/N}|y\rangle
$$

### Unitary Fidelity

$$
F_U =
\frac{
\left|
\mathrm{Tr}
\left(
U_{\text{exact}}^\dagger U_{\text{AQFT}}
\right)
\right|^2
}{
d^2
}
$$

### Approximation Error

$$
E_{\text{approx}}=1-F_U
$$

### Hardware-Aware Optimization

$$
\min N_{2Q}^{\text{physical}}
\quad
\text{subject to}
\quad
E_{\text{approx}}\leq E_{\max}
$$

### Experimental Error Budgets

$$
E_{\max}\in\{0.01,\;0.05,\;0.10,\;0.20\}
$$

### Physical Two-Qubit Gate Reduction

The physical two-qubit gate reduction is calculated as:

$$
\mathrm{Reduction} =
\frac{
N_{2Q}^{threshold} - N_{2Q}^{degree}
}{
N_{2Q}^{threshold}
}
\times 100
$$

where:

- `N_2Q_threshold` = physical two-qubit gates selected using the threshold-based method
- `N_2Q_degree` = physical two-qubit gates selected using the degree-based method

A positive reduction means that the degree-based method requires fewer physical two-qubit gates than the threshold-based method under the same approximation-error budget.