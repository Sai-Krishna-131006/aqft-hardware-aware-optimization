from qft_builder import create_qft
from qiskit.synthesis import synth_qft_full
from qiskit.quantum_info import Operator

n = 3

our_qft = create_qft(n)

qiskit_qft = synth_qft_full(n, do_swaps=False,approximation_degree=0)

our_operator = Operator(our_qft)
qiskit_operator = Operator(qiskit_qft)

print("Our QFT:")
print(our_qft.draw())

print("Qiskit QFT:")
print(qiskit_qft.draw())

print("Out QFT Operator")
print(our_operator.data)

print("\nQiskit QFT Operator")
print(qiskit_operator.data)


print("Equivalent:", our_operator.equiv(qiskit_operator))