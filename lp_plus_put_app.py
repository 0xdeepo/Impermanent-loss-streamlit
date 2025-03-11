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

def uniswap_lp_value(S, S0, t_L, t_H, V0):
    K = math.sqrt(t_L * t_H)
    r = math.sqrt(t_H / t_L)
    value_unit_at_S0 = uniswap_v3_value_unit(S0, K, r)
    if value_unit_at_S0 == 0:
        return 0.0
    alpha = V0 / value_unit_at_S0
    return alpha * uniswap_v3_value_unit(S, K, r)

def put_option_expiry_payoff(S, strike, premium, quantity, position_type):
    """
    Simple payoff at expiration:
      Buy put => payoff = (max(K-S,0) - premium) * quantity
      Sell put => payoff = (premium - max(K-S,0)) * quantity
    """
    intrinsic = max(strike - S, 0.0)
    if position_type == "Buy":
        return (intrinsic - premium) * quantity
    else:
        return (premium - intrinsic) * quantity

def main():
    st.title("Combined LP + Put Option Value Curve")
    st.markdown("""
    This chart reuses the inputs from:
    - **Uniswap LP App** (S0, tL, tH, V0, plus the min/max price)
    - **Put Option App** (strike, premium, quantity, position type, plus min/max price)

    Then plots their **combined payoff** at expiration, 
    without re-asking for parameters.
    """)

    # Retrieve Uniswap LP params from st.session_state
    S0 = st.session_state["uni_S0"]
    t_L = st.session_state["uni_tL"]
    t_H = st.session_state["uni_tH"]
    V0 = st.session_state["uni_V0"]

    # Uniswap's chosen price range
    uni_price_min = st.session_state["uni_price_min"]
    uni_price_max = st.session_state["uni_price_max"]

    # Retrieve Put params from st.session_state
    strike = st.session_state["put_strike_bs"]
    premium = st.session_state["put_premium_bs"]
    quantity = st.session_state["put_qty_bs"]
    position_type = st.session_state["put_position_type_bs"]

    # Put's chosen price range
    put_price_min = st.session_state["put_price_min_bs"]
    put_price_max = st.session_state["put_price_max_bs"]

    # Combine the ranges
    price_min = min(uni_price_min, put_price_min)
    price_max = max(uni_price_max, put_price_max)

    if price_min >= price_max:
        st.error("Combined: Price range is invalid (min >= max).")
        return

    # Build the combined price array
    S_values = np.linspace(price_min, price_max, 300)

    lp_vals = []
    put_vals = []
    combined_vals = []

    for S in S_values:
        lp_v = uniswap_lp_value(S, S0, t_L, t_H, V0)
        put_v = put_option_expiry_payoff(S, strike, premium, quantity, position_type)
        lp_vals.append(lp_v)
        put_vals.append(put_v)
        combined_vals.append(lp_v + put_v)

    # Plot
    fig, ax = plt.subplots(figsize=(8, 5))
    ax.plot(S_values, lp_vals, label="LP Value", color="blue")
    ax.plot(S_values, put_vals, label="Put Value (Payoff)", color="purple")
    ax.plot(S_values, combined_vals, label="LP + Put", color="green", linewidth=2)

    ax.axvline(x=strike, color="red", linestyle="--", label=f"Strike={strike}")
    ax.axhline(y=0, color="black", linewidth=1)
    ax.set_title("Combined: Uniswap LP + Put Payoff")
    ax.set_xlabel
