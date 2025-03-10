import streamlit as st
import numpy as np
import matplotlib.pyplot as plt

# ---------------------------------------------------------
# 1) Uniswap V3 Liquidity Calculation
# ---------------------------------------------------------
def compute_liquidity(usdc_deposit, eth_deposit, P0, P_lower, P_upper):
    """
    Calculate Uniswap V3 liquidity L for a range [P_lower, P_upper].
    Assumes P0 is strictly between P_lower and P_upper, ignoring fees.

    L = min(
       usdc_deposit * sqrt(P0)*sqrt(P_upper) / (sqrt(P_upper) - sqrt(P0)),
       eth_deposit / (sqrt(P0) - sqrt(P_lower))
    )
    """
    # If P0 not in (P_lower, P_upper), the typical formula won't hold properly.
    # We'll assume user respects that condition or we warn them.
    if not (P_lower < P0 < P_upper):
        st.warning("Warning: P0 is not strictly within (P_lower, P_upper). "
                   "This formula may produce odd results.")

    # partial L from the USDC side
    denom_usdc = (np.sqrt(P_upper) - np.sqrt(P0))
    if abs(denom_usdc) < 1e-15:
        part_usdc = 0.0
    else:
        part_usdc = usdc_deposit * np.sqrt(P0) * np.sqrt(P_upper) / denom_usdc

    # partial L from the ETH side
    denom_eth = (np.sqrt(P0) - np.sqrt(P_lower))
    if abs(denom_eth) < 1e-15:
        part_eth = 0.0
    else:
        part_eth = eth_deposit / denom_eth

    return min(part_usdc, part_eth)

# ---------------------------------------------------------
# 2) Uniswap V3 LP Value at Price P
# ---------------------------------------------------------
def uniswap_v3_lp_value(P, L, P_lower, P_upper):
    """
    Returns the USDC value of a Uniswap V3 position with liquidity L
    in the price range [P_lower, P_upper], ignoring fees.

    Piecewise:
      - If P <= P_lower: all in ETH
      - If P >= P_upper: all in USDC
      - Else: partial USDC, partial ETH
    """

    # A) P below range => all in ETH
    if P <= P_lower:
        # total ETH = L * (sqrt(P_upper) - sqrt(P_lower))
        eth_amount = L * (np.sqrt(P_upper) - np.sqrt(P_lower))
        return eth_amount * P

    # B) P above range => all in USDC
    elif P >= P_upper:
        # total USDC = L * ((sqrt(P_upper) - sqrt(P_lower)) / (sqrt(P_lower)*sqrt(P_upper)))
        usdc_amount = L * (
            (np.sqrt(P_upper) - np.sqrt(P_lower))
            / (np.sqrt(P_lower) * np.sqrt(P_upper))
        )
        return usdc_amount

    # C) P in [P_lower, P_upper] => some of each
    else:
        usdc_in_range = L * (
            (np.sqrt(P_upper) - np.sqrt(P))
            / (np.sqrt(P) * np.sqrt(P_upper))
        )
        eth_in_range = L * (np.sqrt(P) - np.sqrt(P_lower))

        return usdc_in_range + eth_in_range * P

# ---------------------------------------------------------
# 3) Streamlit App
# ---------------------------------------------------------
def main():
    st.title("Uniswap V3 Impermanent Loss (Range)")

    st.markdown("""
    This app demonstrates **impermanent loss** for a **Uniswap V3** LP position on ETH/USDC, 
    given a price range [P_lower, P_upper]. 

    **Key assumptions**:
    - You deposit **50%** USDC and **50%** ETH at the current price P0.
    - You specify a range [P_lower, P_upper] **that includes P0** (i.e. P_lower < P0 < P_upper).
    - Fees, rebalancing, or advanced factors are ignored. 
    - We compare the LP's value to a simple "HODL" of your initial USDC + ETH. 
      The difference is **impermanent loss**.
    """)

    # --- Sidebar Inputs ---
    st.sidebar.header("Inputs")

    # A) Basic
    P0 = st.sidebar.number_input("Current ETH price (P0)", value=1600.0, step=50.0)
    T  = st.sidebar.number_input("Total Capital in USDC (T)", value=10000.0, step=500.0)

    # B) Range
    st.sidebar.write("#### LP Range")
    Plow = st.sidebar.number_input("P_lower", value=1400.0, step=50.0)
    Pup  = st.sidebar.number_input("P_upper", value=1800.0, step=50.0)

    # C) Chart range
    st.sidebar.write("#### Chart Range")
    chart_min = st.sidebar.number_input("Min price for chart", value=1000.0, step=50.0)
    chart_max = st.sidebar.number_input("Max price for chart", value=2500.0, step=50.0)
    n_points = st.sidebar.slider("Number of points", min_value=50, max_value=500, value=200)

    st.write("### Summary of Inputs")
    st.write(f"- P0 = {P0}, T = {T}")
    st.write(f"- Range: [{Plow}, {Pup}]")
    st.write(f"- Chart Range: [{chart_min}, {chart_max}]")

    # -- Step 1: Determine deposit amounts (50/50 at P0)
    usdc_initial = T / 2.0
    eth_initial  = (T / 2.0) / P0

    # -- Step 2: Compute Liquidity
    L = compute_liquidity(usdc_initial, eth_initial, P0, Plow, Pup)
    st.write(f"**Calculated Liquidity (L)**: {L:,.4f}")

    # -- Step 3: Evaluate the price range
    prices = np.linspace(chart_min, chart_max, int(n_points))
    lp_vals = []
    hodl_vals = []
    il_vals = []

    for P in prices:
        # A) HODL scenario
        #    still have usdc_initial + eth_initial
        #    total value in USDC = usdc_initial + eth_initial * P
        hodl_val = usdc_initial + eth_initial * P

        # B) LP scenario
        lp_val = uniswap_v3_lp_value(P, L, Plow, Pup)

        # C) Impermanent Loss
        #    IL = 1 - (LP_val / HODL_val) if HODL_val != 0
        if hodl_val > 0:
            il = 1.0 - (lp_val / hodl_val)
        else:
            il = 0.0

        lp_vals.append(lp_val)
        hodl_vals.append(hodl_val)
        il_vals.append(il)

    # -- Step 4: Plot
    fig, ax = plt.subplots(1, 2, figsize=(12, 5))

    # (A) HODL vs LP
    ax[0].plot(prices, hodl_vals, label="HODL Value", color="blue")
    ax[0].plot(prices, lp_vals,  label="LP Value",   color="red")
    ax[0].set_xlabel("ETH Price (USDC)")
    ax[0].set_ylabel("Value (USDC)")
    ax[0].set_title("HODL vs. LP Value")
    ax[0].legend()
    ax[0].grid(True)

    # (B) Impermanent Loss
    il_percent = np.array(il_vals) * 100.0
    ax[1].plot(prices, il_percent, label="IL (%)", color="green")
    ax[1].axhline(0, color="black", linewidth=1)
    ax[1].set_xlabel("ETH Price (USDC)")
    ax[1].set_ylabel("Impermanent Loss (%)")
    ax[1].set_title("Impermanent Loss for Uniswap V3")
    ax[1].legend()
    ax[1].grid(True)

    st.pyplot(fig)

if __name__ == "__main__":
    main()
