from qiskit import QuantumCircuit
from math import pi


def create_qft(n):
    circuit = QuantumCircuit(n)

    for i in reversed(range(n)):
        # Hadamard gate
        circuit.h(i)

        # Controlled phase rotations
        for k in reversed(range(i)):
            angle = pi / (2 ** (i - k))
            circuit.cp(angle, k, i)

    return circuit


if __name__ == "__main__":
    for n in [3, 4, 5, 6, 8]:
        qft = create_qft(n)
        print(f"\n--- {n}-qubit QFT ---")
    
        print(qft.draw());
        print("Gate count:", qft.size())
        print("Circuit depth:", qft.depth())
        print("Gate breakdown:", qft.count_ops())
