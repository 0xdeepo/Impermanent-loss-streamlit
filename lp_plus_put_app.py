import streamlit as st
import numpy as np
import math
import matplotlib.pyplot as plt
from math import log, sqrt
from statistics import NormalDist

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
# 2) Black–Scholes put + PNL (same as put_option_app.py)
###############################################################################
def bs_put_price(S, K, T, sigma_annual):
    if T <= 1e-10:
        return max(K - S, 0.0)
    d1 = (log(S/K) + 0.5*sigma_annual**2*T) / (sigma_annual*math.sqrt(T))
    d2 = d1 - sigma_annual*math.sqrt(T)
    N = NormalDist(0,1).cdf
    return K*N(-d2) - S*N(-d1)

def bs_put_pnl(S, K, T, sigma_annual, premium, quantity, position_type):
    val = bs_put_price(S, K, T, sigma_annual)
    if position_type == "Buy":
        return (val - premium) * quantity
    else:
        return (premium - val) * quantity

###############################################################################
# 3) MAIN: Combined LP + Put (Black–Scholes) with Extra ETH Price Input
###############################################################################
def main():
    st.title("Combined LP + Put (Black–Scholes)")

    st.markdown("""
    **This script reuses parameters** from:
    - **Uniswap** (S0, t_L, t_H, V0, and its price range)
    - **Put Option** (strike, premium, quantity, position type, time in months, implied vol for 180 days, and its price range)

    It plots:
    1. LP Value (from Uniswap)
    2. Put PNL (using Black–Scholes)
    3. Their combined value

    Additionally, you can input a specific token price to get the expected total value.
    """)

    # 1) Retrieve Uniswap state
    needed_uni = ["uni_S0", "uni_tL", "uni_tH", "uni_V0", "uni_price_min", "uni_price_max"]
    for k in needed_uni:
        if k not in st.session_state:
            st.error(f"Missing '{k}' from session_state. Please run the Uniswap app first.")
            return
    S0   = st.session_state["uni_S0"]
    t_L  = st.session_state["uni_tL"]
    t_H  = st.session_state["uni_tH"]
    V0   = st.session_state["uni_V0"]
    uni_min = st.session_state["uni_price_min"]
    uni_max = st.session_state["uni_price_max"]

    # 2) Retrieve Put state
    needed_put = ["put_strike_bs", "put_premium_bs", "put_qty_bs", "put_position_type_bs", 
                  "put_T_months", "put_sigma_180", "put_price_min_bs", "put_price_max_bs"]
    for k in needed_put:
        if k not in st.session_state:
            st.error(f"Missing '{k}' from session_state. Please run the Put Option app first.")
            return
    strike = st.session_state["put_strike_bs"]
    premium = st.session_state["put_premium_bs"]
    quantity = st.session_state["put_qty_bs"]
    position_type = st.session_state["put_position_type_bs"]

    T_months = st.session_state["put_T_months"]
    T_years = T_months / 12.0

    user_iv_180 = st.session_state["put_sigma_180"]
    days_180 = 180.0 / 365.0
    if days_180 < 1e-10:
        st.error("Cannot compute annual volatility from 180 days.")
        return
    sigma_annual = user_iv_180 / math.sqrt(days_180)

    put_min = st.session_state["put_price_min_bs"]
    put_max = st.session_state["put_price_max_bs"]

    # 3) Combined price range
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
        put_pnl_val = bs_put_pnl(S, strike, T_years, sigma_annual, premium, quantity, position_type)
        lp_vals.append(lp_v)
        put_vals.append(put_pnl_val)
        combined_vals.append(lp_v + put_pnl_val)

    fig, ax = plt.subplots(figsize=(8, 5))
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

    # 4) Extra: Specific Token Price Value Calculation
    st.markdown("### Calculate Combined Value at a Specific Token Price")
    specific_price = st.number_input("Enter Token Price (USD) to Evaluate Combined Value:",
                                     key="specific_price",
                                     min_value=price_min,
                                     max_value=price_max,
                                     value=S0,
                                     step=1.0)
    combined_value_at_price = uniswap_lp_value(specific_price, S0, t_L, t_H, V0) + \
                              bs_put_pnl(specific_price, strike, T_years, sigma_annual, premium, quantity, position_type)
    st.write(f"At a token price of **${specific_price:.2f}**, the combined total value is **${combined_value_at_price:.2f}**.")

if __name__ == "__main__":
    main()
