import streamlit as st
import numpy as np
import matplotlib.pyplot as plt

def compute_liquidity(usdc_deposit, eth_deposit, P0, P_lower, P_upper):
    """
    Compute the Uniswap V3 liquidity L for a position in the range [P_lower, P_upper],
    given the user's initial deposits (in USDC, ETH) at current price P0 (assumed P_lower < P0 < P_upper).
    
    This is a simplified approach ignoring edge cases when P0 is outside [P_lower, P_upper].
    
    Based on the standard formula:
      L = min(
        usdc_deposit * sqrt(P0)*sqrt(P_upper) / ( sqrt(P_upper) - sqrt(P0) ),
        eth_deposit / ( sqrt(P0) - sqrt(P_lower) )
      )
    """
    # Defensive checks
    # If P0 not in (P_lower, P_upper), we might need more logic, but let's keep it simple.
    if not (P_lower < P0 < P_upper):
        st.warning("P0 is not strictly between P_lower and P_upper. This formula might not be correct.")
    
    # Compute partial L from the USDC side
    denominator_usdc = (np.sqrt(P_upper) - np.sqrt(P0))
    if abs(denominator_usdc) < 1e-12:
        part_usdc = 0
    else:
        part_usdc = usdc_deposit * np.sqrt(P0) * np.sqrt(P_upper) / denominator_usdc
    
    # Compute partial L from the ETH side
    denominator_eth = (np.sqrt(P0) - np.sqrt(P_lower))
    if abs(denominator_eth) < 1e-12:
        part_eth = 0
    else:
        part_eth = eth_deposit / denominator_eth
    
    # The actual L is the limiting factor
    L = min(part_usdc, part_eth)
    return L

def uniswap_v3_lp_value(P, L, P_lower, P_upper):
    """
    Uniswap V3 position value at price P for liquidity L
    in the range [P_lower, P_upper], ignoring fees.

    Piecewise:
      1) If P <= P_lower: entire position in ETH
      2) If P >= P_upper: entire position in USDC
      3) Otherwise: partial amounts of both USDC and ETH
    """

    # 1) If P <= P_lower
    if P <= P_lower:
        # All in ETH
        # formula for total ETH if below range:
        #   = L * (sqrt(P_upper) - sqrt(P_lower))
        eth_amount = L * (np.sqrt(P_upper) - np.sqrt(P_lower))
        return eth_amount * P  # convert to USDC

    # 2) If P >= P_upper
    elif P >= P_upper:
        # All in USDC
        # formula for total USDC if above range:
        #   = L * ( (sqrt(P_upper) - sqrt(P_lower)) / ( sqrt(P_lower)*sqrt(P_upper) ) )
        usdc_amount = L * ((np.sqrt(P_upper) - np.sqrt(P_lower))
                           / (np.sqrt(P_lower) * np.sqrt(P_upper)))
        return usdc_amount

    # 3) If in range: P_lower < P < P_upper
    else:
        # USDC portion:
        #   = L * ( (sqrt(P_upper) - sqrt(P)) / ( sqrt(P)*sqrt(P_upper) ) )
        usdc_in_range = L * ((np.sqrt(P_upper) - np.sqrt(P))
                             / (np.sqrt(P)*np.sqrt(P_upper)))
        # ETH portion:
        #   = L * ( sqrt(P) - sqrt(P_lower) )
        eth_in_range = L * (np.sqrt(P) - np.sqrt(P_lower))
        return usdc_in_range + eth_in_range * P

def main():
    st.title("Uniswap V3 Impermanent Loss Demo")

    st.markdown("""
    This app simulates **impermanent loss** for a simplified **Uniswap V3** position on an ETH/USDC pair.  
    - We assume you deposit a **50/50** ratio at **price P0**.  
    - You choose the **range** [P_lower, P_upper].  
    - We compute the **LP value** vs. **HODL value** across a range of ETH prices.  
    - The difference is impermanent loss.  

    **Note**: This model ignores fees and rebalances, and assumes P0 is strictly between P_lower and P_upper.
    """)

    # Sidebar Inputs
    st.sidebar.header("1) Basic Inputs")
    P0 = st.sidebar.number_input("Current ETH price (P0)", value=1600.0, step=50.0)
    T  = st.sidebar.number_input("Total capital (USDC)", value=10000.0, step=1000.0)
    
    st.sidebar.header("2) LP Range")
    P_lower = st.sidebar.number_input("P_lower (range lower bound)", value=1400.0, step=50.0)
    P_upper = st.sidebar.number_input("P_upper (range upper bound)", value=1800.0, step=50.0)
    
    st.sidebar.header("3) Chart Range")
    chart_min = st.sidebar.number_input("Min Price for chart", value=800.0, step=50.0)
    chart_max = st.sidebar.number_input("Max Price for chart", value=3200.0, step=50.0)
    n_points  = st.sidebar.slider("Number of points", min_value=50, max_value=500, value=200)

    # Show summary
    st.write(f"### Summary of Inputs")
    st.write(f"- Current Price (P0): {P0}")
    st.write(f"- Total Capital (USDC): {T}")
    st.write(f"- Range: [{P_lower}, {P_upper}]")
    st.write(f"- Chart Range: [{chart_min}, {chart_max}]")
    
    # 1) Determine how much USDC & ETH we deposit (50/50)
    usdc_initial = T / 2.0
    eth_initial  = (T / 2.0) / P0

    # 2) Compute Liquidity L
    L = compute_liquidity(usdc_initial, eth_initial, P0, P_lower, P_upper)
    st.write(f"**Liquidity (L)**: {L:,.2f}")

    # 3) HODL Value at any price P:
    #    If we just keep the initial tokens (usdc_initial, eth_initial):
    #    HODL_Value(P) = usdc_initial + eth_initial * P
    
    # 4) Evaluate a price range and compute LP value + IL
    prices = np.linspace(chart_min, chart_max, int(n_points))
    lp_values = []
    hodl_values = []
    il_values = []

    for P in prices:
        # HODL
        hodl_val = usdc_initial + (eth_initial * P)

        # LP
        lp_val = uniswap_v3_lp_value(P, L, P_lower, P_upper)

        # Impermanent Loss
        # IL = 1 - (LP_val / HODL_val), if HODL_val != 0
        if hodl_val != 0:
            il = 1.0 - (lp_val / hodl_val)
        else:
            il = 0.0

        lp_values.append(lp_val)
        hodl_values.append(hodl_val)
        il_values.append(il)

    # 5) Plot
    fig, ax = plt.subplots(1, 2, figsize=(12,5))

    # Subplot 1: LP vs. HODL Value
    ax[0].plot(prices, hodl_values, label="HODL Value", color="blue")
    ax[0].plot(prices, lp_values,  label="LP Value",   color="red")
    ax[0].set_xlabel("ETH Price (USDC)")
    ax[0].set_ylabel("Value (USDC)")
    ax[0].set_title("HODL vs. LP Value")
    ax[0].grid(True)
    ax[0].legend()

    # Subplot 2: Impermanent Loss
    il_percent = np.array(il_values) * 100.0
    ax[1].plot(prices, il_percent, color="green", label="IL (%)")
    ax[1].axhline(0, color="black", linewidth=1)
    ax[1].set_xlabel("ETH Price (USDC)")
    ax[1].set_ylabel("Impermanent Loss (%)")
    ax[1].set_title("Impermanent Loss for Uniswap V3")
    ax[1].grid(True)
    ax[1].legend()

    st.pyplot(fig)

if __name__ == "__main__":
    main()
