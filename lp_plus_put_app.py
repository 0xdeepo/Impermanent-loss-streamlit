import streamlit as st
import numpy as np
import math
import matplotlib.pyplot as plt
from math import log, sqrt
from statistics import NormalDist

###############################################################################
# 1) Uniswap logic (unchanged)
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
# 2) Black–Scholes Put Value & PNL (matching the put_option_app.py approach)
###############################################################################
def bs_put_price(S, K, T, sigma):
    """
    Black–Scholes price for a European put (r=0).
    """
    if T <= 1e-10:
        return max(K - S, 0.0)

    d1 = (math.log(S / K) + 0.5 * sigma**2 * T) / (sigma * math.sqrt(T))
    d2 = d1 - sigma * math.sqrt(T)
    N = NormalDist(0,1).cdf

    put_value = K * N(-d2) - S * N(-d1)
    return put_value

def bs_put_pnl(S, K, T, sigma, premium, quantity, position_type):
    """
    If you 'Buy' the put: PNL = (BS put value - premium) * quantity
    If you 'Sell': PNL = (premium - BS put value) * quantity
    """
    bs_val = bs_put_price(S, K, T, sigma)
    if position_type == "Buy":
        return (bs_val - premium) * quantity
    else:
        return (premium - bs_val) * quantity

###############################################################################
# 3) MAIN: Summation of LP Value + Put PNL (using Black–Scholes)
###############################################################################
def main():
    st.title("Combined LP + Put: Summing LP Value + Theoretical Put PNL (Black–Scholes)")

    st.markdown("""
    This chart **reuses** parameters from:
    - **Uniswap** (S0, t_L, t_H, V0, plus min/max price)
    - **Put Option** (strike, premium, quantity, buy/sell, T, sigma, plus min/max price)
    
    It computes:
    1. LP Value at each S
    2. Put PNL at each S using the **Black–Scholes** model (matching the second script),
    3. Sums them to form the final "LP + Put" curve.

    That way, the **smooth** Put PNL curve from the second script is preserved here.
    """)

    # 1) Retrieve Uniswap inputs
    needed_uni = ["uni_S0", "uni_tL", "uni_tH", "uni_V0",
                  "uni_price_min", "uni_price_max"]
    for k in needed_uni:
        if k not in st.session_state:
            st.error(f"Missing '{k}' in session_state. Run the Uniswap app first.")
            return

    S0 = st.session_state["uni_S0"]
    t_L = st.session_state["uni_tL"]
    t_H = st.session_state["uni_tH"]
    V0 = st.session_state["uni_V0"]
    uni_min = st.session_state["uni_price_min"]
    uni_max = st.session_state["uni_price_max"]

    if t_L >= t_H:
        st.error("Invalid Uniswap bounds (t_L >= t_H). Please adjust in Uniswap section.")
        return

    # 2) Retrieve Put inputs
    needed_put = ["put_strike_bs", "put_premium_bs", "put_qty_bs",
                  "put_position_type_bs", "put_T", "put_sigma",
                  "put_price_min_bs", "put_price_max_bs"]
    for k in needed_put:
        if k not in st.session_state:
            st.error(f"Missing '{k}' in session_state. Run the Put Option app first.")
            return

    strike = st.session_state["put_strike_bs"]
    premium = st.session_state["put_premium_bs"]
    quantity = st.session_state["put_qty_bs"]
    position_type = st.session_state["put_position_type_bs"]
    T = st.session_state["put_T"]
    sigma = st.session_state["put_sigma"]
    put_min = st.session_state["put_price_min_bs"]
    put_max = st.session_state["put_price_max_bs"]

    # 3) Combine the price ranges
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
        # Uniswap portion
        lp_v = uniswap_lp_value(S, S0, t_L, t_H, V0)
        
        # Put PNL from Black–Scholes
        pnl_put = bs_put_pnl(S, strike, T, sigma, premium, quantity, position_type)

        lp_vals.append(lp_v)
        put_vals.append(pnl_put)
        combined_vals.append(lp_v + pnl_put)

    # 4) Plot
    fig, ax = plt.subplots(figsize=(8, 5))
    ax.plot(S_values, lp_vals, label="LP Value", color="blue")
    ax.plot(S_values, put_vals, label="Put PNL (Black–Scholes)", color="purple")
    ax.plot(S_values, combined_vals, label="LP + Put Combined", color="green", linewidth=2)

    ax.axvline(x=strike, color='red', linestyle='--', label=f"Strike={strike}")
    ax.axhline(y=0, color='black', linewidth=1)
    ax.set_title("Combined: LP Value + Put PNL (Black–Scholes)")
    ax.set_xlabel("Token Price in USD")
    ax.set_ylabel("Value in USD")
    ax.grid(True)
    ax.legend()

    st.pyplot(fig)

if __name__ == "__main__":
    main()
