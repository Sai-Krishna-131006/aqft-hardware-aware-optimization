from math import pi

from src.qft_builder import create_qft
from src.aqft_builder import create_aqft
from src.aqft_builder import create_aqft_threshold


def print_cp_gates(circuit):

    gates = []

    for index, instruction in enumerate(circuit.data):

        operation = instruction.operation

        if operation.name == "cp":

            angle = float(operation.params[0])

            q0 = instruction.qubits[0]._index
            q1 = instruction.qubits[1]._index

            gates.append(
                (index, q0, q1, angle)
            )

    return gates


# ============================================================
# INSPECT 5-QUBIT CASE
# ============================================================

n = 5

print("=" * 80)
print("EXACT QFT")
print("=" * 80)

exact = create_qft(n)

for gate in print_cp_gates(exact):
    print(gate)


print()
print("=" * 80)
print("DEGREE = 1")
print("=" * 80)

degree_1 = create_aqft(n, 1)

for gate in print_cp_gates(degree_1):
    print(gate)


print()
print("=" * 80)
print("THRESHOLD = PI/16")
print("=" * 80)

threshold = create_aqft_threshold(
    n,
    pi / 16
)

for gate in print_cp_gates(threshold):
    print(gate)


print()
print("=" * 80)
print("THRESHOLD = PI/8")
print("=" * 80)

threshold = create_aqft_threshold(
    n,
    pi / 8
)

for gate in print_cp_gates(threshold):
    print(gate)