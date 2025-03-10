import streamlit as st
import numpy as np
import math
import matplotlib.pyplot as plt

###############################################################################
# REUSE THE LOGIC FROM UNISWAP
###############################################################################
def uniswap_v3_value_unit(S, K, r):
    """
    Piecewise value function for ONE UNIT of Uniswap V3 liquidity
    (denominated in token B, e.g. USDC).
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

def uniswap_lp_value(S, S0, t_L, t_H, V0):
    """
    Given a price S, returns the scaled LP value in USD, for an LP that is worth V0 at S0.
    """
    # 1) Compute K and r
    K = math.sqrt(t_L * t_H)
    r = math.sqrt(t_H / t_L)

    # 2) Value of ONE UNIT at S0
    value_unit_at_S0 = uniswap_v3_value_unit(S0, K, r)
    if value_unit_at_S0 == 0:
        return 0.0

    # 3) Scaling factor
    alpha = V0 / value_unit_at_S0

    # 4) Value at S
    return alpha * uniswap_v3_value_unit(S, K, r)

###############################################################################
# REUSE THE LOGIC FROM PUT OPTION
###############################################################################
def put_option_value(S, strike, premium, quantity, position_type):
    """
    Returns the P/L of a put option at price S, given:
      - strike
      - premium
      - quantity
      - position_type = "Buy" or "Sell"
    """
    intrinsic = max(strike - S, 0.0)
    if position_type == "Buy":
        # payoff per contract = max(K - S, 0) - premium
        pl = intrinsic - premium
    else:
        # payoff per contract = premium - max(K - S, 0)
        pl = premium - intrinsic

    return pl * quantity

###############################################################################
# MAIN SCRIPT
###############################################################################
def main():
    st.title("Combined LP + Put Option Value Curve")

    st.markdown("""
    This script combines the **Uniswap LP position** and a **Put Option** 
    into a single chart, to visualize the hedge effect. 
    """)

    st.sidebar.header("Uniswap LP Inputs")
    S0 = st.sidebar.number_input("LP: Current Price (S0)", value=100.0, step=1.0)
    t_L = st.sidebar.number_input("LP: Lower Bound (t_L)", value=80.0, step=1.0, min_value=0.01)
    t_H = st.sidebar.number_input("LP: Upper Bound (t_H)", value=120.0, step=1.0, min_value=0.01)
    V0 = st.sidebar.number_input("LP: Value @ S0 (USD)", value=10000.0, step=100.0, min_value=0.01)

    if t_L >= t_H:
        st.error("LP: Lower Bound must be strictly less than Upper Bound.")
        return

    st.sidebar.header("Put Option Inputs")
    strike = st.sidebar.number_input("Put: Strike Price", value=100.0, step=1.0, min_value=0.01)
    premium = st.sidebar.number_input("Put: Premium", value=5.0, step=0.1, min_value=0.0)
    quantity = st.sidebar.number_input("Put: Quantity", value=1.0, step=1.0, min_value=1.0)
    position_type = st.sidebar.selectbox("Put: Position Type", ["Buy", "Sell"])

    st.sidebar.header("Plot Range")
    price_min = st.sidebar.number_input("Min Token Price (USD)", value=50.0, step=1.0, min_value=0.0)
    price_max = st.sidebar.number_input("Max Token Price (USD)", value=200.0, step=1.0, min_value=0.01)

    if price_min >= price_max:
        st.error("Min Token Price must be < Max Token Price.")
        return

    # Create the array of prices
    S_values = np.linspace(price_min, price_max, 400)

    # Compute each curve
    lp_vals = []
    put_vals = []
    combined_vals = []

    for S in S_values:
        lp_v = uniswap_lp_value(S, S0, t_L, t_H, V0)
        put_v = put_option_value(S, strike, premium, quantity, position_type)
        lp_vals.append(lp_v)
        put_vals.append(put_v)
        combined_vals.append(lp_v + put_v)

    # Plot
    fig, ax = plt.subplots(figsize=(8, 5))
    ax.plot(S_values, lp_vals, label="LP Value", color="blue")
    ax.plot(S_values, put_vals, label="Put Value", color="purple")
    ax.plot(S_values, combined_vals, label="LP + Put", color="green", linewidth=2)

    ax.axvline(x=strike, color="red", linestyle="--", label=f"Strike={strike}")
    ax.axhline(y=0, color="black", linewidth=1)

    ax.set_title("LP + Put Option Combined Value Curve")
    ax.set_xlabel("Token Price in USD")
    ax.set_ylabel("Value in USD")
    ax.grid(True)
    ax.legend()

    st.pyplot(fig)

if __name__ == "__main__":
    main()
