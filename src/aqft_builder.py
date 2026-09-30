from qiskit import QuantumCircuit
from qiskit.quantum_info import Operator
from math import pi


def create_aqft(num_qubits, degree):
    # Store all controlled-phase gates of the exact QFT
    cp_gates = []

    # Same QFT orientation as our validated qft_builder.py
    for i in reversed(range(num_qubits)):

        for k in reversed(range(i)):
            angle = pi / (2 ** (i - k))
            cp_gates.append((angle, k, i))

    # Sort from smallest angle to largest angle
    cp_gates.sort(key=lambda x: x[0])

    # Remove 'degree' smallest-angle gates
    gates_to_remove = cp_gates[:degree]

    # Build the AQFT circuit
    qc = QuantumCircuit(num_qubits)

    for i in reversed(range(num_qubits)):

        qc.h(i)

        for k in reversed(range(i)):
            angle = pi / (2 ** (i - k))

            if (angle, k, i) not in gates_to_remove:
                qc.cp(angle, k, i)

    return qc

def calculate_approximation_error(num_qubits, degree):

    exact_qft = create_aqft(num_qubits,0)
    aqft = create_aqft(num_qubits, degree)

    exact_operator = Operator(exact_qft)
    aqft_operator = Operator(aqft)

    dimension = 2 ** num_qubits

    overlap = (exact_operator.adjoint() @ aqft_operator).data
    fidelity = abs(overlap.trace()) ** 2 / (dimension ** 2)

    error = 1 - fidelity

    return fidelity, error

def create_aqft_threshold(num_qubits, threshold):
    qc = QuantumCircuit(num_qubits)

    for j in reversed(range(num_qubits)):
        qc.h(j)

        for k in reversed(range(j)):
            angle = pi / (2 ** (j - k))

            if angle > threshold:
                qc.cp(angle, k, j)

    return qc


def calculate_threshold_error(num_qubits, threshold):
    exact_qft = create_aqft(num_qubits, 0)
    threshold_qft = create_aqft_threshold(num_qubits, threshold)

    exact_operator = Operator(exact_qft).data
    threshold_operator = Operator(threshold_qft).data

    dimension = 2 ** num_qubits

    fidelity = (
        abs(
            (exact_operator.conj().T @ threshold_operator).trace()
        ) ** 2
        / dimension ** 2
    )

    error = 1 - fidelity

    return fidelity, error