import streamlit as st
import numpy as np
import matplotlib.pyplot as plt
import math
from math import log, sqrt
from statistics import NormalDist

###############################################################################
# Black–Scholes functions (r=0 for simplicity, no dividends)
###############################################################################
def bs_put_price(S, K, T, sigma_annual):
    if T <= 1e-10:
        return max(K - S, 0.0)

    d1 = (math.log(S/K) + 0.5 * sigma_annual**2 * T) / (sigma_annual * math.sqrt(T))
    d2 = d1 - sigma_annual * math.sqrt(T)
    N = NormalDist(0, 1).cdf
    put_value = K * N(-d2) - S * N(-d1)
    return put_value

def bs_put_delta(S, K, T, sigma_annual):
    if T <= 1e-10:
        return -1.0 if S < K else 0.0

    d1 = (math.log(S/K) + 0.5 * sigma_annual**2 * T) / (sigma_annual * math.sqrt(T))
    N = NormalDist(0, 1).cdf
    return N(d1) - 1.0

def main():
    st.title("Put Option: Intrinsic Value, Theoretical Value, PNL, and Delta (Months + 180d Vol)")

    st.markdown(r"""
    1. **Intrinsic Value**: \(\max(K - S,0)\)
    2. **Theoretical Value (Black–Scholes)**: A smooth curve for volatility & time.
    3. **PNL**: 
       - If **Buy**, \(\mathrm{PNL}(S) = [\text{BS\_put}(S) - \text{premium}]\times \text{quantity}\).
       - If **Sell**, \(\mathrm{PNL}(S) = [\text{premium} - \text{BS\_put}(S)]\times \text{quantity}\).
    4. **Delta**: The option's sensitivity to \(S\).
    
    **Inputs are now:**
    - Time to Expiration in **months** (converted to years)
    - Implied Vol for a **180-day horizon** (converted to annual vol)
    """)

    st.sidebar.header("Option Parameters")
    strike = st.sidebar.number_input("Strike Price (K)",
                                     key="put_strike_bs",
                                     value=2100.0,
                                     step=1.0,
                                     min_value=0.01)
    premium = st.sidebar.number_input("Premium you paid/received",
                                      key="put_premium_bs",
                                      value=187.0,
                                      step=1.0,
                                      min_value=0.0)
    quantity = st.sidebar.number_input("Quantity (contracts)",
                                       key="put_qty_bs",
                                       value=1.0,
                                       step=1.0,
                                       min_value=1.0)
    position_type = st.sidebar.selectbox("Position Type",
                                         ("Buy", "Sell"),
                                         key="put_position_type_bs",
                                         index=0)

    st.sidebar.header("Market / Expiry Inputs")
    T_months = st.sidebar.number_input("Time to Expiration (months)",
                                       key="put_T_months",
                                       value=1.0,
                                       step=1.0,
                                       min_value=0.0)
    T_years = T_months / 12.0

    st.sidebar.markdown("**Implied Vol (180-day horizon)**")
    user_iv_180 = st.sidebar.number_input("Implied Vol (180-day horizon)",
                                          key="put_sigma_180",
                                          value=0.65,
                                          step=0.01,
                                          min_value=0.0)
    days_180 = 180.0 / 365.0
    if days_180 < 1e-10:
        st.error("Vol cannot be computed for 180 days.")
        return
    sigma_annual = user_iv_180 / math.sqrt(days_180)

    st.sidebar.subheader("Plot Range for Underlying Price")
    S_min = st.sidebar.number_input("Min Token Price (USD)",
                                    key="put_price_min_bs",
                                    min_value=0.01,
                                    value=500.0,
                                    step=1.0)
    S_max = st.sidebar.number_input("Max Token Price (USD)",
                                    key="put_price_max_bs",
                                    min_value=0.01,
                                    value=4000.0,
                                    step=1.0)

    if S_min >= S_max:
        st.error("Min price must be strictly less than Max price.")
        return

    prices = np.linspace(S_min, S_max, 300)

    intrinsic_vals = []
    bs_vals = []
    pnl_vals = []
    deltas = []

    for S in prices:
        intrinsic = max(strike - S, 0.0)
        bs_val = bs_put_price(S, strike, T_years, sigma_annual)
        delta = bs_put_delta(S, strike, T_years, sigma_annual)

        if position_type == "Buy":
            pl = (bs_val - premium) * quantity
        else:
            pl = (premium - bs_val) * quantity

        intrinsic_vals.append(intrinsic)
        bs_vals.append(bs_val)
        pnl_vals.append(pl)
        deltas.append(delta)

    fig, ax1 = plt.subplots(figsize=(8, 5))
    ax1.plot(prices, intrinsic_vals, label="Intrinsic Value", linestyle="--")
    ax1.plot(prices, bs_vals, label="BS Theoretical Value (Smooth)")
    ax1.plot(prices, pnl_vals, label="PNL", linewidth=2)

    ax1.axvline(x=strike, color='red', linestyle='--', label=f'Strike = {strike}')
    ax1.axhline(y=0, color='black', linewidth=1)
    ax1.set_title("Put Option: Intrinsic, BS Value, PNL, Delta (Months + 180d Vol)")
    ax1.set_xlabel("Underlying Price (S)")
    ax1.set_ylabel("Value / PNL (USD)")
    ax1.grid(True)

    ax2 = ax1.twinx()
    ax2.plot(prices, deltas, color="orange", label="Delta")
    ax2.set_ylabel("Delta")

    lines1, labels1 = ax1.get_legend_handles_labels()
    lines2, labels2 = ax2.get_legend_handles_labels()
    ax1.legend(lines1 + lines2, labels1 + labels2, loc="best")

    st.pyplot(fig)

if __name__ == "__main__":
    main()
