import streamlit as st
import numpy as np
import math
import matplotlib.pyplot as plt

def uniswap_v3_value_unit(S, K, r):
    if S < (K / r):
        return S
    elif S > (K * r):
        return K
    else:
        return (2.0 * math.sqrt(S * K * r) - S - K) / (r - 1.0)

def plot_uniswap_v3_lp_value(S0, t_L, t_H, V0):
    K = math.sqrt(t_L * t_H)
    r = math.sqrt(t_H / t_L)
    value_unit_at_S0 = uniswap_v3_value_unit(S0, K, r)
    if value_unit_at_S0 == 0:
        st.error("The 'unit' value at S0 is 0, cannot scale properly.")
        return
    alpha = V0 / value_unit_at_S0

    # Unique keys for min/max token price
    price_min = st.sidebar.number_input(
        "Min Token Price (USD)",
        key="uni_price_min",  # <--- ADDED KEY
        min_value=0.0,
        value=float(t_L / 2),
        step=1.0
    )
    price_max = st.sidebar.number_input(
        "Max Token Price (USD)",
        key="uni_price_max",  # <--- ADDED KEY
        min_value=0.01,
        value=float(t_H * 1.5),
        step=1.0
    )
    
    if price_min >= price_max:
        st.error("Min must be < Max.")
        return

    S_values = np.linspace(price_min, price_max, 200)
    lp_values = [alpha * uniswap_v3_value_unit(S, K, r) for S in S_values]

    fig, ax = plt.subplots(figsize=(8, 5))
    ax.plot(S_values, lp_values, label='LP Value', color='blue')
    ax.axvline(x=t_L, color='red', linestyle='--', label='Lower Bound (t_L)')
    ax.axvline(x=t_H, color='green', linestyle='--', label='Upper Bound (t_H)')
    ax.axvline(x=S0, color='orange', linestyle=':', label='Starting Price (S0)')
    ax.set_title("Uniswap V3 LP Value vs. Token Price")
    ax.set_xlabel("Token Price in USD")
    ax.set_ylabel("LP Value in USD")
    ax.legend()
    ax.grid(True)
    
    st.pyplot(fig)

def main():
    st.title("Uniswap V3 LP Value")
    st.markdown("Plots the LP value (in USD) as token price changes.")

    st.sidebar.header("Input Parameters")
    S0 = st.sidebar.number_input("Starting Price (S0) of Token A in USD",
                                 key="uni_S0",  # <--- ADD UNIQUE KEY
                                 min_value=0.0001,
                                 value=100.0,
                                 step=1.0)
    t_L = st.sidebar.number_input("Lower Bound (t_L)",
                                  key="uni_tL",  # <--- ADD UNIQUE KEY
                                  min_value=0.0001,
                                  value=80.0,
                                  step=1.0)
    t_H = st.sidebar.number_input("Upper Bound (t_H)",
                                  key="uni_tH",  # <--- ADD UNIQUE KEY
                                  min_value=0.0001,
                                  value=120.0,
                                  step=1.0)
    V0 = st.sidebar.number_input("LP Total Value (V0) in USD at S0",
                                 key="uni_V0",  # <--- ADD UNIQUE KEY
                                 min_value=1.0,
                                 value=10000.0,
                                 step=100.0)
    if t_L >= t_H:
        st.error("t_L must be < t_H.")
        return

    plot_uniswap_v3_lp_value(S0, t_L, t_H, V0)

if __name__ == "__main__":
    main()
