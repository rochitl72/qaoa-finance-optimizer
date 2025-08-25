import streamlit as st
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import plotly.express as px
import plotly.graph_objects as go

from qiskit import Aer
from qiskit.utils import algorithm_globals
from qiskit.algorithms import QAOA
from qiskit.algorithms.optimizers import COBYLA
from qiskit_optimization import QuadraticProgram
from qiskit_optimization.algorithms import MinimumEigenOptimizer

# Load data
mean_returns = pd.read_csv("data/mean_returns.csv", index_col=0).squeeze()
cov_matrix = pd.read_csv("data/cov_matrix.csv", index_col=0)

# Streamlit UI setup
st.set_page_config(page_title="Quantum Portfolio Optimizer", layout="wide")
st.title("🔮 Quantum Portfolio Optimizer")
st.markdown("Optimize your portfolio using QAOA to balance return and risk (Sharpe Ratio).")

# Sidebar controls
st.sidebar.header("🧮 QAOA Settings")
budget = st.sidebar.slider("Number of Assets to Select", 1, len(mean_returns), 3)
risk_penalty = st.sidebar.slider("Risk Penalty (Higher = Safer)", 0.0, 1.0, 0.5, step=0.1)

# Create QUBO formulation
qp = QuadraticProgram()
for i in range(len(mean_returns)):
    qp.binary_var(name=f"x{i}")

linear = -mean_returns.values
quadratic = 2 * risk_penalty * cov_matrix.values
qp.minimize(linear=linear, quadratic=quadratic)

qp.linear_constraint(
    linear={f"x{i}": 1 for i in range(len(mean_returns))},
    sense="==",
    rhs=budget,
    name="budget"
)

# Run QAOA optimization
backend = Aer.get_backend("aer_simulator")
algorithm_globals.random_seed = 42
qaoa = QAOA(optimizer=COBYLA(), reps=1, quantum_instance=backend)
optimizer = MinimumEigenOptimizer(qaoa)

status_placeholder = st.sidebar.empty()
status_placeholder.markdown("⚛️ Running QAOA Optimization...")

try:
    result = optimizer.solve(qp)
    status_placeholder.success("✅ Optimization complete!")
except Exception as e:
    status_placeholder.error(f"❌ Optimization failed: {str(e)}")

# Decode result
bitstring = result.x
selected_assets = [mean_returns.index[i] for i, bit in enumerate(bitstring) if bit == 1]
portfolio_returns = mean_returns[selected_assets]
portfolio_alloc = portfolio_returns / portfolio_returns.sum()

# Table
st.header("✅ Selected Assets")
st.table(pd.DataFrame({
    "Asset": selected_assets,
    "Expected Return": portfolio_returns.values
}))



# Summary
st.subheader("📈 Optimization Summary")
st.markdown(f"- **Budget Used:** {budget}")
st.markdown(f"- **Risk Penalty:** {risk_penalty}")
st.markdown(f"- **Total Expected Return:** `{portfolio_returns.sum():.5f}`")

# Sharpe Ratio
risk_free_rate = 0.0
cov_subset = cov_matrix.loc[selected_assets, selected_assets]
weights = portfolio_alloc.values.reshape(-1, 1)
portfolio_std = np.sqrt(weights.T @ cov_subset.values @ weights)[0][0]
sharpe_ratio = (portfolio_returns.sum() - risk_free_rate) / portfolio_std

st.markdown(f"- **Portfolio Risk (σ):** `{portfolio_std:.5f}`")
st.markdown(f"- **Sharpe Ratio:** `{sharpe_ratio:.5f}`")

# ----------------------
# 🔲 MULTI-VIEW VISUALS
# ----------------------
st.subheader("📊 Portfolio Visualization Panel")

# Create columns for visual layout
col1, col2 = st.columns(2)
with col1:
    fig_bar = go.Figure([go.Bar(x=selected_assets, y=portfolio_alloc.values)])
    fig_bar.update_layout(title="Bar Chart - Asset Weights", xaxis_title="Asset", yaxis_title="Weight")
    st.plotly_chart(fig_bar, use_container_width=True)

with col2:
    fig_tree = px.treemap(
        names=selected_assets,
        values=portfolio_alloc.values,
        parents=[""] * len(selected_assets),
        title="Treemap - Allocation Hierarchy"
    )
    st.plotly_chart(fig_tree, use_container_width=True)

col3, col4 = st.columns(2)
with col3:
    fig_radar = go.Figure()
    fig_radar.add_trace(go.Scatterpolar(
        r=[portfolio_returns.sum(), portfolio_std, sharpe_ratio],
        theta=["Return", "Risk", "Sharpe"],
        fill='toself',
        name='Portfolio'
    ))
    fig_radar.update_layout(
        polar=dict(radialaxis=dict(visible=True)),
        showlegend=False,
        title="Radar Chart - Performance Metrics"
    )
    st.plotly_chart(fig_radar, use_container_width=True)

with col4:
    fig_donut = px.pie(
        names=selected_assets,
        values=portfolio_alloc.values,
        hole=0.4,
        title="Donut Chart - Asset Allocation"
    )
    st.plotly_chart(fig_donut, use_container_width=True)