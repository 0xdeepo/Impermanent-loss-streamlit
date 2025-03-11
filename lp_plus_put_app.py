import streamlit as st
import numpy as np
import math
import matplotlib.pyplot as plt
from math import log, sqrt
from statistics import NormalDist

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
# 2) Black–Scholes put + PNL
###############################################################################
def bs_put_price(S, K, T, sigma_annual):
    if T <= 1e-10:
        return max(K - S, 0.0)
    d1 = (math.log(S/K) + 0.5*sigma_annual**2*T)/(sigma_annual*math.sqrt(T))
    d2 = d1 - sigma_annual*math.sqrt(T)
    N = NormalDist(0,1).cdf
    return K*N(-d2) - S*N(-d1)

def bs_put_pnl(S, K, T, sigma_annual, premium, quantity, position_type):
    """
    If 'Buy': PNL = (BS_put - premium) * quantity
    If 'Sell': PNL = (premium - BS_put) * quantity
    """
    val = bs_put_price(S, K, T, sigma_annual)
    if position_type == "Buy":
        return (val - premium)*quantity
    else:
        return (premium - val)*quantity

###############################################################################
# 3) MAIN: Summation of LP Value + Theoretical Put PNL
###############################################################################
def main():
    st.title("Combined LP + Put (Black–Scholes)")

    st.markdown("""
    **This script reuses**:
    - **Uniswap** inputs (S0, t_L, t_H, V0, price range)
    - **Put** inputs (strike, premium, quantity, position type, *T_months*, *implied vol for 180 days*, price range)

    Then we do **the same** monthly → yearly + annualizing steps to match the second script,
    and sum the LP Value with the put PNL.
    """)

    # 1) Retrieve Uniswap state
    needed_uni = ["uni_S0", "uni_tL", "uni_tH", "uni_V0", "uni_price_min", "uni_price_max"]
    for k in needed_uni:
        if k not in st.session_state:
            st.error(f"Missing '{k}' from session_state. Please run Uniswap script first.")
            return
    S0   = st.session_state["uni_S0"]
    t_L  = st.session_state["uni_tL"]
    t_H  = st.session_state["uni_tH"]
    V0   = st.session_state["uni_V0"]
    uni_min = st.session_state["uni_price_min"]
    uni_max = st.session_state["uni_price_max"]

    # 2) Retrieve Put state
    needed_put = ["put_strike_bs", "put_premium_bs", "put_qty_bs",
                  "put_position_type_bs", 
                  "put_T_months", "put_sigma_180",
                  "put_price_min_bs", "put_price_max_bs"]
    for k in needed_put:
        if k not in st.session_state:
            st.error(f"Missing '{k}' from session_state. Please run Put script first.")
            return

    strike = st.session_state["put_strike_bs"]
    premium = st.session_state["put_premium_bs"]
    quantity = st.session_state["put_qty_bs"]
    position_type = st.session_state["put_position_type_bs"]

    # Time in months => years
    T_months = st.session_state["put_T_months"]
    T_years = T_months / 12.0

    # 180-day vol => annual vol
    user_iv_180 = st.session_state["put_sigma_180"]
    days_180 = 180.0/365.0
    if days_180 < 1e-10:
        st.error("Cannot compute annual vol from 180 days. Something's off.")
        return
    sigma_annual = user_iv_180 / math.sqrt(days_180)

    put_min = st.session_state["put_price_min_bs"]
    put_max = st.session_state["put_price_max_bs"]

    # 3) Combine the price ranges
    price_min = min(uni_min, put_min)
    price_max = max(uni_max, put_max)
    if price_min >= price_max:
        st.error("Combined: price_min >= price_max. Adjust in Uniswap/Put sections.")
        return

    # 4) Build arrays
    S_values = np.linspace(price_min, price_max, 300)
    lp_vals = []
    put_vals = []
    combined_vals = []

    for S in S_values:
        lp_v = uniswap_lp_value(S, S0, t_L, t_H, V0)
        put_pnl_val = bs_put_pnl(S, strike, T_years, sigma_annual, premium, quantity, position_type)
        lp_vals.append(lp_v)
        put_vals.append(put_pnl_val)
        combined_vals.append(lp_v + put_pnl_val)

    fig, ax = plt.subplots(figsize=(8,5))
    ax.plot(S_values, lp_vals, label="LP Value", color="blue")
    ax.plot(S_values, put_vals, label="Put PNL (BS)", color="purple")
    ax.plot(S_values, combined_vals, label="LP + Put Combined", color="green", linewidth=2)

    ax.axvline(x=strike, color='red', linestyle='--', label=f"Strike={strike}")
    ax.axhline(y=0, color='black', linewidth=1)
    ax.set_title("Combined LP + Put (Black–Scholes) Theoretical PNL")
    ax.set_xlabel("Token Price in USD")
    ax.set_ylabel("Value in USD")
    ax.grid(True)
    ax.legend()

    st.pyplot(fig)

if __name__ == "__main__":
    main()
