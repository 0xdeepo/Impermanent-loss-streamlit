import streamlit as st
import numpy as np
import matplotlib.pyplot as plt
import math
from math import log, sqrt
from statistics import NormalDist

###############################################################################
# Black–Scholes functions (r=0 for simplicity, no dividends)
###############################################################################
def bs_put_price(S, K, T, sigma):
    """
    Black–Scholes price for a European put option (r=0).
    S     : underlying price
    K     : strike
    T     : time to expiration (in years)
    sigma : volatility (decimal)
    """
    # Handle the case T=0 or near 0 => purely intrinsic
    if T <= 1e-10:
        return max(K - S, 0)

    d1 = (math.log(S/K) + 0.5 * sigma**2 * T) / (sigma * math.sqrt(T))
    d2 = d1 - sigma * math.sqrt(T)

    # N(x) is the CDF of the standard normal distribution
    N = NormalDist(0, 1).cdf

    # For r=0, discount factor exp(-rT) = 1
    put_value = K * N(-d2) - S * N(-d1)
    return put_value

def bs_put_delta(S, K, T, sigma):
    """
    Delta of a European put under Black–Scholes (r=0).
    This is dV/dS for the put.
    """
    if T <= 1e-10:
        # At T=0, payoff is intrinsic => delta is -1 if S<K, else 0
        return -1.0 if S < K else 0.0

    # Same d1 as above
    d1 = (math.log(S/K) + 0.5 * sigma**2 * T) / (sigma * math.sqrt(T))
    N = NormalDist(0, 1).cdf

    # Put delta = N(d1) - 1
    return N(d1) - 1.0

###############################################################################
# Main Streamlit app
###############################################################################
def main():
    st.title("Put Option: Intrinsic Value, Theoretical Value, PNL, and Delta")

    st.markdown("""
    This script shows four plots on a single chart:
    1. **Intrinsic Value**: \\(\\max(K - S, 0)\\)  
    2. **Theoretical Value (Black–Scholes)**: A smooth curve accounting for volatility and time.  
    3. **PNL**: If you **buy**, \\(\\mathrm{PNL}(S) = [\\text{BS\_put}(S) - \\text{premium}]\\times \\text{quantity}\\).  
       If you **sell**, \\(\\mathrm{PNL}(S) = [\\text{premium} - \\text{BS\_put}(S)]\\times \\text{quantity}\\).  
    4. **Delta**: The option's sensitivity to \\(S\\), plotted on a second (right) Y-axis.
    """)

    st.sidebar.header("Option Parameters")

    strike = st.sidebar.number_input("Strike Price (K)",
                                     key="put_strike_bs",
                                     value=100.0,
                                     step=1.0,
                                     min_value=0.
