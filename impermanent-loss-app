import streamlit as st
import numpy as np
import matplotlib.pyplot as plt

def main():
    st.title("Impermanent Loss Demo")

    st.markdown("""
    This app shows **Impermanent Loss** for a simplified **Uniswap V2-style** AMM (constant product).  
    - We assume a 50/50 pool of ETH/USDC.  
    - We compare the value of *HODLing* vs. *Liquidity Providing* at different ETH prices.  
    - The difference is **impermanent loss** (IL).  
    """)

    # --- Sidebar Inputs ---
    st.sidebar.header("Initial Settings")

    # 1) Initial Price
    P0 = st.sidebar.number_input("Initial ETH Price (P0) [USDC/ETH]", value=1600.0, step=50.0)

    # 2) Total Capital in USDC
    T  = st.sidebar.number_input("Total Capital (USDC)", value=10000.0, step=1000.0)

    # 3) Min and Max for Price Range
    P_min = st.sidebar.number_input("Min Price for chart", value=800.0, step=50.0)
    P_max = st.sidebar.number_input("Max Price for chart", value=3200.0, step=50.0)
    n_points = st.sidebar.slider("Number of points in range", min_value=50, max_value=500, value=200)

    st.write("### Simulation Parameters")
    st.write(f"- Initial ETH Price = {P0}")
    st.write(f"- Total Capital = {T}")
    st.write(f"- Price Range = [{P_min}, {P_max}]")

    # --- Calculate IL Curve ---
    prices = np.linspace(P_min, P_max, n_points)

    # 50/50 deposit
    x_init = T / 2.0          # USDC
    y_init = (T / 2.0) / P0   # ETH
    k = x_init * y_init       # constant product

    lp_values = []
    hodl_values = []
    il_values = []

    for P in prices:
        # HODL scenario
        hodl_val = x_init + (y_init * P)

        # LP scenario (constant product)
        #   x' * y' = k
        #   x'/y' = P => x' = sqrt(k*P), y' = sqrt(k/P)
        x_prime = np.sqrt(k * P)
        y_prime = np.sqrt(k / P)
        lp_val = x_prime + (y_prime * P)

        # Impermanent Loss
        if hodl_val > 0:
            il = 1 - (lp_val / hodl_val)
        else:
            il = 0.0

        lp_values.append(lp_val)
        hodl_values.append(hodl_val)
        il_values.append(il)

    # --- Plot Results ---
    fig, ax = plt.subplots(1, 2, figsize=(12, 5))

    # (A) HODL vs. LP Value
    ax[0].plot(prices, hodl_values, label="HODL Value", color="blue")
    ax[0].plot(prices, lp_values, label="LP Value", color="red")
    ax[0].set_xlabel("ETH Price (USDC)")
    ax[0].set_ylabel("Value (USDC)")
    ax[0].set_title("HODL vs. LP Value")
    ax[0].legend()
    ax[0].grid(True)

    # (B) Impermanent Loss
    il_percent = np.array(il_values) * 100.0
    ax[1].plot(prices, il_percent, color="green", label="IL (%)")
    ax[1].axhline(0, color="black", linewidth=1)
    ax[1].set_xlabel("ETH Price (USDC)")
    ax[1].set_ylabel("IL (%)")
    ax[1].set_title("Impermanent Loss")
    ax[1].grid(True)
    ax[1].legend()

    st.pyplot(fig)

if __name__ == "__main__":
    main()
