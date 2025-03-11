import streamlit as st
import numpy as np
import math
import matplotlib.pyplot as plt

###############################################################################
# 1) Uniswap logic (same as uniswap_app.py)
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
# 2) Put PNL at expiration (copied from put_option_app.py)
###############################################################################
def put_pnl(S, K, premium, quantity, position_type):
    intrinsic = max(K - S, 0.0)
    if position_type == "Buy":
        return (intrinsic - premium) * quantity
    else:
        return (premium - intrinsic) * quantity

###############################################################################
# 3) MAIN: Summation of LP Value + Put PNL
###############################################################################
def main():
    st.title("Combined LP + Put: Summing LP Value + Put PNL (Expiration)")

    st.markdown("""
    This chart **reuses** parameters from:
    - **Uniswap** (S0, t_L, t_H, V0, plus min/max price)
    - **Put Option** (strike, premium, quantity, buy/sell, plus min/max price)
    
    Then it plots:
    1. LP Value alone
    2. Put PNL alone
    3. **Combined** = (LP Value + Put PNL)
    """)

    # 1) Retrieve Uniswap inputs
    needed_uni = ["uni_S0", "uni_tL", "uni_tH", "uni_V0",
                  "uni_price_min", "uni_price_max"]
    for k in needed_uni:
        if k not in st.session_state:
            st.error(f"Missing '{k}' in session_state. Please run the Uniswap app first.")
            return

    S0 = st.session_state["uni_S0"]
    t_L = st.session_state["uni_tL"]
    t_H = st.session_state["uni_tH"]
    V0 = st.session_state["uni_V0"]
    uni_min = st.session_state["uni_price_min"]
    uni_max = st.session_state["uni_price_max"]

    # 2) Retrieve Put inputs
    needed_put = ["put_strike_bs", "put_premium_bs", "put_qty_bs",
                  "put_position_type_bs", "put_price_min_bs", "put_price_max_bs"]
    for k in needed_put:
        if k not in st.session_state:
            st.error(f"Missing '{k}' in session_state. Please run the Put Option app first.")
            return

    strike = st.session_state["put_strike_bs"]
    premium = st.session_state["put_premium_bs"]
    quantity = st.session_state["put_qty_bs"]
    position_type = st.session_state["put_position_type_bs"]
    put_min = st.session_state["put_price_min_bs"]
    put_max = st.session_state["put_price_max_bs"]

    # 3) Combined range
    price_min = min(uni_min, put_min)
    price_max = max(uni_max, put_max)
    if price_min >= price_max:
        st.error("Combined: price_min >= price_max. Adjust in Uniswap/Put sections.")
        return

    S_values = np.linspace(price_min, price_max, 300)

    lp_vals = []
    put_vals = []
    combined_vals = []

    for S in S_values:
        lp_v = uniswap_lp_value(S, S0, t_L, t_H, V0)
        put_v = put_pnl(S, strike, premium, quantity, position_type)
        lp_vals.append(lp_v)
        put_vals.append(put_v)
        combined_vals.append(lp_v + put_v)

    fig, ax = plt.subplots(figsize=(8, 5))
    ax.plot(S_values, lp_vals, label="LP Value", color="blue")
    ax.plot(S_values, put_vals, label="Put PNL", color="purple")
    ax.plot(S_values, combined_vals, label="LP + Put Combined", color="green", linewidth=2)

    ax.axvline(x=strike, color='red', linestyle='--', label=f"Strike={strike}")
    ax.axhline(y=0, color='black', linewidth=1)
    ax.set_title("Combined: LP Value + Put PNL (Expiration)")
    ax.set_xlabel("Token Price in USD")
    ax.set_ylabel("Value in USD")
    ax.grid(True)
    ax.legend()

    st.pyplot(fig)

if __name__ == "__main__":
    main()
