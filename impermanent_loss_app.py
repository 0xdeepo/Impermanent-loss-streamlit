import streamlit as st
import numpy as np
import matplotlib.pyplot as plt
import math

def uniswap_v3_value_unit(S, K, r):
    """
    Piecewise value function for ONE UNIT of Uniswap V3 liquidity
    (denominated in token B, e.g., USDC).
    """
    if S < (K / r):
        # Below lower bound => fully in token A, worth S (B) per A.
        return S
    elif S > (K * r):
        # Above upper bound => fully in token B, worth K.
        return K
    else:
        # Within the range => partial amounts of A and B.
        return (2.0 * math.sqrt(S * K * r) - S - K) / (r - 1.0)

def main():
    st.title("Uniswap V3 LP Value Visualizer")

    st.markdown("""
    This app plots the value (in USDC) of a Uniswap V3 LP position 
    as the price of Token A (in USDC) changes.
    """)

    # --- User Inputs ---
    st.sidebar.header("Input Parameters")

    # 1) Starting price: S0
    S0 = st.sidebar.number_input(
        "Starting Price (S0) of Token A in USDC",
        min_value=0.0001,
        value=100.0,
        step=1.0
    )

    # 2) Lower Bound: t_L
    t_L = st.sidebar.number_input(
        "Lower Bound (t_L)",
        min_value=0.0001,
        value=80.0,
        step=1.0
    )

    # 3) Upper Bound: t_H
    t_H = st.sidebar.number_input(
        "Upper Bound (t_H)",
        min_value=0.0001,
        value=120.0,
        step=1.0
    )

    # 4) LP Total Value: V0
    V0 = st.sidebar.number_input(
        "LP Total Value (V0) in USDC at S0",
        min_value=1.0,
        value=10000.0,
        step=100.0
    )

    # Ensure t_L < t_H
    if t_L >= t_H:
        st.error("Lower bound (t_L) must be strictly less than upper bound (t_H).")
        return

    # Calculate K and r
    K = math.sqrt(t_L * t_H)
    r = math.sqrt(t_H / t_L)

    # Value of ONE UNIT of liquidity at S0:
    value_unit_at_S0 = uniswap_v3_value_unit(S0, K, r)
    if value_unit_at_S0 == 0:
        st.error("The unit value at S0 is 0. Check bounds vs. S0.")
        return
    
    # Scaling factor
    alpha = V0 / value_unit_at_S0

    # --- Price Range for Plotting ---
    # By default, let’s show ±50% around the bounds for a nice visual range.
    price_min = 0.5 * t_L
    price_max = 1.5 * t_H
    # In case S0 is outside those multipliers, adjust the range:
    price_min = min(price_min, S0 * 0.5)
    price_max = max(price_max, S0 * 1.5)

    # Generate prices
    S_values = np.linspace(price_min, price_max, 300)

    # Compute scaled LP value
    lp_values = [alpha * uniswap_v3_value_unit(S, K, r) for S in S_values]

    # --- Plot ---
    fig, ax = plt.subplots(figsize=(8, 5))
    ax.plot(S_values, lp_values, label="LP Value", color="blue")

    # Draw vertical lines for t_L, t_H, and S0
    ax.axvline(x=t_L, color='red', linestyle='--', label='t_L')
    ax.axvline(x=t_H, color='green', linestyle='--', label='t_H')
    ax.axvline(x=S0, color='orange', linestyle=':', label='S0')

    ax.set_title("Uniswap V3 LP Value vs. Price of Token A (in USDC)")
    ax.set_xlabel("Price of Token A in USDC (S)")
    ax.set_ylabel("LP Value in USDC")
    ax.legend()
    ax.grid(True)

    st.pyplot(fig)

if __name__ == "__main__":
    main()
