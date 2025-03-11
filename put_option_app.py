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
    """
    Black–Scholes price for a European put option (r=0).

    Parameters:
      S            : current underlying price
      K            : strike
      T            : time to expiration in *years*
      sigma_annual : *annualized* volatility
    """
    # If T is effectively zero, just use intrinsic value
    if T <= 1e-10:
        return max(K - S, 0.0)

    d1 = (math.log(S/K) + 0.5 * sigma_annual**2 * T) / (sigma_annual * math.sqrt(T))
    d2 = d1 - sigma_annual * math.sqrt(T)

    # Standard normal CDF
    N = NormalDist(0, 1).cdf

    # For r=0, discount factor = 1
    put_value = K * N(-d2) - S * N(-d1)
    return put_value

def bs_put_delta(S, K, T, sigma_annual):
    """
    Delta of a European put under Black–Scholes (r=0).

    Parameters:
      S            : current underlying price
      K            : strike
      T            : time to expiration in years
      sigma_annual : annualized volatility
    """
    if T <= 1e-10:
        # At T=0, payoff is purely intrinsic => delta is -1 if S<K, else 0
        return -1.0 if S < K else 0.0

    d1 = (math.log(S/K) + 0.5 * sigma_annual**2 * T) / (sigma_annual * math.sqrt(T))
    N = NormalDist(0, 1).cdf

    # Put delta = N(d1) - 1
    return N(d1) - 1.0

def main():
    st.title("Put Option: Intrinsic Value, Theoretical Value, PNL, and Delta")

    st.markdown(r"""
    This script shows four plots on a single chart:
    1. **Intrinsic Value**: \(\max(K - S, 0)\)
    2. **Theoretical Value (Black–Scholes)**: A smooth curve accounting for volatility and time.
    3. **PNL**: 
       - If you **buy**, \(\mathrm{PNL}(S) = [\text{BS\_put}(S) - \text{premium}]\times \text{quantity}\).
       - If you **sell**, \(\mathrm{PNL}(S) = [\text{premium} - \text{BS\_put}(S)]\times \text{quantity}\).
    4. **Delta**: The option's sensitivity to \(S\), plotted on a second (right) Y-axis.

    **Important change**: 
    - **Time to Expiration** is now in **months** (we convert to years in the math).
    - **Implied Vol for 180 days**: the user inputs the volatility for a 180-day horizon, 
      and we convert that to an *annualized* volatility for Black–Scholes.
    """)

    st.sidebar.header("Option Parameters")

    strike = st.sidebar.number_input("Strike Price (K)",
                                     key="put_strike_bs",
                                     value=100.0,
                                     step=1.0,
                                     min_value=0.01)
    premium = st.sidebar.number_input("Premium you paid/received",
                                      key="put_premium_bs",
                                      value=5.0,
                                      step=0.1,
                                      min_value=0.0)
    quantity = st.sidebar.number_input("Quantity (contracts)",
                                       key="put_qty_bs",
                                       value=1.0,
                                       step=1.0,
                                       min_value=1.0)
    position_type = st.sidebar.selectbox("Position Type",
                                         ("Buy", "Sell"),
                                         key="put_position_type_bs")

    # Now we measure expiration in MONTHS
    st.sidebar.header("Market / Expiry Inputs")
    T_months = st.sidebar.number_input("Time to Expiration (months)",
                                       key="put_T_months",
                                       value=6.0,  # default 6 months
                                       step=1.0,
                                       min_value=0.0)

    # We'll convert from months to years for the BS formula
    T_years = T_months / 12.0

    # The user provides implied vol for 180 days => we annualize it
    # e.g. if user inputs 0.30 => that means 30% for 180 days => annual_vol ~ 0.30 / sqrt(180/365)
    st.sidebar.markdown("**Implied Vol for 180 days** (decimal, e.g. 0.3 => 30% stdev over 6 months)")
    user_iv_180 = st.sidebar.number_input("Implied Vol (180-day horizon)",
                                          key="put_sigma_180",
                                          value=0.3,  # 30% for 180 days
                                          step=0.05,
                                          min_value=0.0)
    # Convert to annual volatility
    # 180 days is roughly 180/365 ~ 0.493 years
    # so annual_vol = user_iv_180 / sqrt( (180/365) )
    if user_iv_180 < 0:
        st.error("Vol cannot be negative.")
        return
    annual_vol = 0.0
    days_180_in_years = 180.0 / 365.0
    if days_180_in_years > 1e-10:
        annual_vol = user_iv_180 / math.sqrt(days_180_in_years)

    st.sidebar.subheader("Plot Range for Underlying Price")
    S_min = st.sidebar.number_input("Min Token Price (USD)",
                                    key="put_price_min_bs",
                                    min_value=0.01,
                                    value=1.0,
                                    step=1.0)
    S_max = st.sidebar.number_input("Max Token Price (USD)",
                                    key="put_price_max_bs",
                                    min_value=0.01,
                                    value=200.0,
                                    step=1.0)

    if S_min >= S_max:
        st.error("Min price must be strictly less than Max price.")
        return

    # Generate the underlying price array
    prices = np.linspace(S_min, S_max, 300)

    intrinsic_vals = []
    bs_vals = []
    pnl_vals = []
    deltas = []

    for S in prices:
        # Intrinsic payoff at expiration
        intrinsic = max(strike - S, 0.0)

        # Theoretical BS Put Value (using annual_vol + T_years)
        bs_val = bs_put_price(S, strike, T_years, annual_vol)

        # Delta
        delta = bs_put_delta(S, strike, T_years, annual_vol)

        # PNL
        if position_type == "Buy":
            pl = (bs_val - premium) * quantity
        else:
            pl = (premium - bs_val) * quantity

        intrinsic_vals.append(intrinsic)
        bs_vals.append(bs_val)
        pnl_vals.append(pl)
        deltas.append(delta)

    # --- Plot
    fig, ax1 = plt.subplots(figsize=(8, 5))

    # Left axis: Intrinsic, Theoretical Value, and PNL
    ax1.plot(prices, intrinsic_vals, label="Intrinsic Value", linestyle="--")
    ax1.plot(prices, bs_vals, label="BS Theoretical Value (Smooth)")
    ax1.plot(prices, pnl_vals, label="PNL", linewidth=2)

    ax1.axvline(x=strike, color='red', linestyle='--', label=f'Strike = {strike}')
    ax1.axhline(y=0, color='black', linewidth=1)
    ax1.set_title("Put Option: Intrinsic, Theoretical, PNL, Delta (Months + 180d Vol)")
    ax1.set_xlabel("Underlying Price (S)")
    ax1.set_ylabel("Value / PNL (USD)")
    ax1.grid(True)

    # Right axis: Delta
    ax2 = ax1.twinx()
    ax2.plot(prices, deltas, color="orange", label="Delta")
    ax2.set_ylabel("Delta")

    # Merge legends
    lines1, labels1 = ax1.get_legend_handles_labels()
    lines2, labels2 = ax2.get_legend_handles_labels()
    ax1.legend(lines1 + lines2, labels1 + labels2, loc="best")

    st.pyplot(fig)

if __name__ == "__main__":
    main()
