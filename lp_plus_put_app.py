import streamlit as st
import numpy as np
import math
import matplotlib.pyplot as plt

###############################################################################
# 1) Uniswap logic
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

###############################################################################
# 2) Simple put payoff at expiration (not Black–Scholes)
###############################################################################
def put_option_expiry_payoff(S, strike, premium, quantity, position_type):
    """
    Plain-vanilla payoff at expiration:
      - If you BUY a put: payoff = (max(K-S,0) - premium) * quantity
      - If you SELL: payoff = (premium - max(K-S,0)) * quantity
    """
    intrinsic = max(strike - S, 0.0)
    if position_type == "Buy":
        return (intrinsic - premium) * quantity
    else:
        return (premium - intrinsic) * quantity

###############################################################################
# 3) Main: Combine the LP & Put payoffs. Reuse st.session_state from prior scripts
###############################################################################
def main():
    st.title("Combined LP + Put Option Value Curve")
    st.markdown("""
    **This chart reuses the inputs from**:
    1. **Uniswap LP App** (S0, t_L, t_H, V0, plus chosen price range)
    2. **Put Option App** (strike, premium, quantity, buy/sell, plus chosen price range)
    
    Then it plots a **single chart** showing:
    - LP Value alone,
    - Put Value alone (payoff at expiration),
    - **Combined** (LP + Put).
    
    Please ensure you fill out the first two sections before viewing this one.
    """)

    # --- 1) Retrieve Uniswap inputs ---
    required_uni_keys = ["uni_S0", "uni_tL", "uni_tH", "uni_V0",
                         "uni_price_min", "uni_price_max"]
    for k in required_uni_keys:
        if k not in st.session_state:
            st.error(f"Missing key '{k}' in st.session_state. Please run the Uniswap app first.")
            return

    S0 = st.session_state["uni_S0"]
    t_L = st.session_state["uni_tL"]
    t_H = st.session_state["uni_tH"]
    V0 = st.session_state["uni_V0"]
    uni_min = st.session_state["uni_price_min"]
    uni_max = st.session_state["uni_price_max"]

    if t_L >= t_H:
        st.error("Invalid LP bounds (t_L >= t_H). Please correct in Uniswap section.")
        return

    # --- 2) Retrieve Put inputs ---
    required_put_keys = ["put_strike_bs", "put_premium_bs", "put_qty_bs",
                         "put_position_type_bs", "put_price_min_bs", "put_price_max_bs"]
    for k in required_put_keys:
        if k not in st.session_state:
            st.error(f"Missing key '{k}' in st.session_state. Please run the Put Option app first.")
            return

    strike = st.session_state["put_strike_bs"]
    premium = st.session_state["put_premium_bs"]
    quantity = st.session_state["put_qty_bs"]
    position_type = st.session_state["put_position_type_bs"]
    put_min = st.session_state["put_price_min_bs"]
    put_max = st.session_state["put_price_max_bs"]

    # --- 3) Combine the two price ranges ---
    # This ensures we see a single chart spanning the entire min->max
    price_min = min(uni_min, put_min)
    price_max = max(uni_max, put_max)
    if price_min >= price_max:
        st.error("Combined price range is invalid (min >= max). Adjust in the Uniswap/Put sections.")
        return

    # --- 4) Generate the unified price array ---
    S_values = np.linspace(price_min, price_max, 300)

    # We'll store separate curves: LP alone, Put alone, Combined
    lp_vals = []
    put_vals = []
    combined_vals = []

    for S in S_values:
        # LP
        lp_v = uniswap_lp_value(S, S0, t_L, t_H, V0)
        # Put payoff at expiration
        put_v = put_option_expiry_payoff(S, strike, premium, quantity, position_type)

        lp_vals.append(lp_v)
        put_vals.append(put_v)
        combined_vals.append(lp_v + put_v)

    # --- 5) Plot
    fig, ax = plt.subplots(figsize=(8, 5))
    ax.plot(S_values, lp_vals, label="LP Value", color="blue")
    ax.plot(S_values, put_vals, label="Put Value (Expiry Payoff)", color="purple")
    ax.plot(S_values, combined_vals, label="LP + Put Combined", color="green", linewidth=2)

    ax.axvline(x=strike, color="red", linestyle="--", label=f"Strike={strike}")
    ax.axhline(y=0, color="black", linewidth=1)
    ax.set_title("Combined Uniswap LP + Put Payoff at Expiration")
    ax.set_xlabel("Token Price in USD")
    ax.set_ylabel("Value in USD")
    ax.grid(True)
    ax.legend()

    st.pyplot(fig)

if __name__ == "__main__":
    main()
