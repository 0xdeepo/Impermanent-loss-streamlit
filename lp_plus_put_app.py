import streamlit as st
import numpy as np
import math
import matplotlib.pyplot as plt

###############################################################################
# Utility functions for computing LP value and Put value
###############################################################################
def uniswap_v3_value_unit(S, K, r):
    if S < (K / r):
        return S
    elif S > (K * r):
        return K
    else:
        return (2.0 * math.sqrt(S * K * r) - S - K) / (r - 1.0)

def uniswap_lp_value(S, S0, t_L, t_H, V0):
    K = math.sqrt(t_L * t_H)
    r = math.sqrt(t_H / t_L)
    value_unit_at_S0 = uniswap_v3_value_unit(S0, K, r)
    if value_unit_at_S0 == 0:
        return 0.0
    alpha = V0 / value_unit_at_S0
    return alpha * uniswap_v3_value_unit(S, K, r)

def put_option_value(S, strike, premium, quantity, position_type):
    intrinsic = max(strike - S, 0.0)
    if position_type == "Buy":
        pl = intrinsic - premium
    else:
        pl = premium - intrinsic
    return pl * quantity

###############################################################################
# MAIN SCRIPT: reads previous inputs from st.session_state, no new widgets
###############################################################################
def main():
    st.title("Combined LP + Put Option Value Curve")
    st.markdown("""
    This chart **reuses** the inputs from the Uniswap LP app and the Put Option app,
    and plots the combined payoff (LP + Put) without asking for inputs again.
    """)

    # --- Retrieve Uniswap LP parameters from session_state ---
    # Make sure these match the keys in uniswap_app.py
    S0 = st.session_state["uni_S0"]
    t_L = st.session_state["uni_tL"]
    t_H = st.session_state["uni_tH"]
    V0 = st.session_state["uni_V0"]
    
    # We'll also retrieve the Uniswap's chosen min/max price (if you prefer to use them)
    uni_price_min = st.session_state["uni_price_min"]
    uni_price_max = st.session_state["uni_price_max"]

    # --- Retrieve Put Option parameters from session_state ---
    strike = st.session_state["put_strike"]
    premium = st.session_state["put_premium"]
    quantity = st.session_state["put_qty"]
    position_type = st.session_state["put_position_type"]
    
    # The put app also defines its own min/max
    put_price_min = st.session_state["put_price_min"]
    put_price_max = st.session_state["put_price_max"]

    # --- Decide on a single price range for the combined chart ---
    # For example, let's unify by taking the min of both mins and the max of both maxes:
    price_min = min(uni_price_min, put_price_min)
    price_max = max(uni_price_max, put_price_max)
    
    if price_min >= price_max:
        st.error("Combined: The selected price ranges are invalid (min >= max).")
        return

    # Generate price range
    S_values = np.linspace(price_min, price_max, 400)
    
    # Calculate each curve
    lp_vals = []
    put_vals = []
    combined_vals = []

    for S in S_values:
        lp_v = uniswap_lp_value(S, S0, t_L, t_H, V0)
        put_v = put_option_value(S, strike, premium, quantity, position_type)
        lp_vals.append(lp_v)
        put_vals.append(put_v)
        combined_vals.append(lp_v + put_v)

    # --- Plot ---
    fig, ax = plt.subplots(figsize=(8, 5))
    ax.plot(S_values, lp_vals, label="LP Value", color="blue")
    ax.plot(S_values, put_vals, label="Put Value", color="purple")
    ax.plot(S_values, combined_vals, label="LP + Put", color="green", linewidth=2)
    
    # Mark the strike
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
