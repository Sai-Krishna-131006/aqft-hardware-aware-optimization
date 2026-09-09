from qiskit import QuantumCircuit
from math import pi


def create_qft(n):
    circuit = QuantumCircuit(n)

    for i in range(n):
        # Hadamard gate
        circuit.h(i)

        # Controlled phase rotations
        for k in range(i + 1, n):
            angle = pi / (2 ** (k - i))
            circuit.cp(angle, k, i)

    return circuit


for n in [3, 4, 5, 6, 8]:
    qft = create_qft(n)
    print(f"\n--- {n}-qubit QFT ---")
    
    print(qft.draw());
    print("Gate count:", qft.size())
    print("Circuit depth:", qft.depth())
    print("Gate breakdown:", qft.count_ops())