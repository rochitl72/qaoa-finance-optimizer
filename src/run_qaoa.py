import pandas as pd
import numpy as np

from qiskit import Aer
from qiskit.utils import QuantumInstance, algorithm_globals
from qiskit.algorithms import QAOA
from qiskit.algorithms.optimizers import COBYLA

from qiskit_optimization import QuadraticProgram
from qiskit_optimization.algorithms import MinimumEigenOptimizer

# Load your prepared stock data
mean_returns = pd.read_csv("data/mean_returns.csv", index_col=0).squeeze()
cov_matrix = pd.read_csv("data/cov_matrix.csv", index_col=0)

# Set portfolio parameters
num_assets = len(mean_returns)
budget = 3  # Choose exactly 3 assets
risk_penalty = 0.5

# Define QUBO problem
qp = QuadraticProgram()
for i in range(num_assets):
    qp.binary_var(name=f"x{i}")

# Objective: maximize returns - risk_penalty * risk
linear = -mean_returns.values
quadratic = 2 * risk_penalty * cov_matrix.values
qp.minimize(linear=linear, quadratic=quadratic)

# Constraint: select exactly 'budget' assets
qp.linear_constraint(
    linear={f"x{i}": 1 for i in range(num_assets)},
    sense="==",
    rhs=budget,
    name="budget"
)

# Setup quantum backend
backend = Aer.get_backend("qasm_simulator")
quantum_instance = QuantumInstance(backend=backend, shots=1024, seed_simulator=42, seed_transpiler=42)

# Initialize QAOA algorithm
qaoa = QAOA(optimizer=COBYLA(), quantum_instance=quantum_instance)

# Solve using QAOA
print("🚀 Running QAOA optimization...")
optimizer = MinimumEigenOptimizer(qaoa)
result = optimizer.solve(qp)

# Display results
selected_assets = [mean_returns.index[i] for i, bit in enumerate(result.x) if bit == 1]

print("\n✅ QAOA Selected Assets:", selected_assets)
print("📈 Objective Value (Return - Risk):", result.fval)
print("🧠 Bitstring Output:", result.x)