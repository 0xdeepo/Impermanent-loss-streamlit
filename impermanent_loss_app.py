import streamlit as st
import numpy as np
import matplotlib.pyplot as plt

###############################################################################
#                             Uniswap V3 Math                                 #
###############################################################################

def compute_liquidity(x_init, y_init, P0, P_lower, P_upper):
    """
    Compute the Uniswap V3 Liquidity L for a position in [P_lower, P_upper],
    given:
      - x_init = initial ETH (token0) deposited
      - y_init = initial USDC (token1) deposited
      - P0 = current price (USDC per ETH), with P_lower < P0 < P_upper.
    We use the "in-range" formulas from the Uniswap V3 math docs:
      x(P) = L * ( sqrt(P_upper) - sqrt(P) ) / ( sqrt(P) * sqrt(P_upper) )
      y(P) = L * ( sqrt(P) - sqrt(P_lower) )

    We solve these for L using x_init, y_init at P0, then take L = min(Lx, Ly).
    """
    # Defensive check
    if not (P_lower < P0 < P_upper):
        st.warning("WARNING: P0 is not strictly between P_lower and P_upper. "
                   "This formula won't be correct if the position is partially or fully out of range initially.")

    # We'll define some helpers:
    sqrtP0   = np.sqrt(P0)
    sqrtPlow = np.sqrt(P_lower)
    sqrtPup  = np.sqrt(P_upper)

    # From the doc:
    # x_init = L * ( sqrt(P_upper) - sqrt(P0 ) ) / ( sqrt(P0 )* sqrt(P_upper) )
    # => Lx = x_init * sqrt(P0 ) * sqrt(P_upper) / [ sqrt(P_upper) - sqrt(P0 ) ]
    denom_x = (sqrtPup - sqrtP0)
    if abs(denom_x) < 1e-15:
        L_x = float('inf')
    else:
        L_x = x_init * (sqrtP0 * sqrtPup) / denom_x

    # y_init = L * ( sqrt(P0 ) - sqrt(P_lower ) )
    # => L_y = y_init / [ sqrt(P0 ) - sqrt(P_lower ) ]
    denom_y = (sqrtP0 - sqrtPlow)
    if abs(denom_y) < 1e-15:
        L_y = float('inf')
    else:
        L_y = y_init / denom_y

    return min(L_x, L_y)


def uniswap_v3_lp_value(P, L, P_lower, P_upper):
    """
    Piecewise formula for the Uniswap V3 LP value in USDC terms,
    for a position with liquidity L in range [P_lower, P_upper].
    We treat:
      - token0 = ETH
      - token1 = USDC
      - P = USDC per ETH

    Equations from the "Liquidity Math in Uniswap V3" doc:

    1) If P <= P_lower => all in ETH
       x = L * ( sqrt(P_upper) - sqrt(P_lower) ), value in USDC = x * P

    2) If P >= P_upper => all in USDC
       y = L * ( sqrt(P_upper) - sqrt(P_lower) ), value in USDC = y

       (But careful: The doc's eqn for "fully in Y" is:
           y = L ( sqrt(pb ) - sqrt(pa ) )
         That means if Y=USDC, the position's entire holdings is that many USDC. )

    3) If P_lower < P < P_upper => partial amounts:
       x = L * ( sqrt(P_upper) - sqrt(P) ) / ( sqrt(P)*sqrt(P_upper) )
       y = L * ( sqrt(P) - sqrt(P_lower) )
       total value = x*P + y
    """
    sqrtP   = np.sqrt(P)
    sqrtPl  = np.sqrt(P_lower)
    sqrtPu  = np.sqrt(P_upper)

    # CASE A: Price below range => all in ETH
    if P <= P_lower:
        # eqn 4 from doc: x = L ( sqrt(pb) - sqrt(pa) ), y=0
        x_amt = L * (sqrtPu - sqrtPl)
        return x_amt * P  # convert to USDC

    # CASE B: Price above range => all in USDC
    elif P >= P_upper:
        # eqn 8 from doc: y = L( sqrt(pb) - sqrt(pa) ), x=0
        y_amt = L * (sqrtPu - sqrtPl)
        return y_amt  # already USDC

    # CASE C: In-range => partial
    else:
        x_amt = L * ( sqrtPu - sqrtP ) / ( sqrtP * sqrtPu )
        y_amt = L * ( sqrtP - sqrtPl )
        return x_amt * P + y_amt


###############################################################################
#                             Streamlit App                                   #
###############################################################################

def main():
    st.title("Uniswap V3 Impermanent Loss Demo (Exact Formulas)")

    st.markdown("""
    This demo uses the formulas from the “Liquidity Math in Uniswap V3” document, assuming:
    - **Token0 = ETH**, Token1 = USDC
    - Price \(P\) = USDC per ETH
    - We deposit 50% USDC and 50% ETH at price \(P_0\)
    - The chosen LP range is \([P_{\\mathrm{lower}}, P_{\\mathrm{upper}}]\) with **P_lower < P_0 < P_upper**.
    - No fees or advanced nuances, purely the standard piecewise equations.

    **Impermanent loss** is \(\\mathrm{IL}(P) = 1 - \\frac{\\mathrm{LP\\ Value}(P)}{\\mathrm{HODL\\ Value}(P)}\\).
    """)

    # Sidebar: user inputs
    st.sidebar.header("User Inputs")

    P0 = st.sidebar.number_input("Current Price (P0, USDC/ETH)", value=1600.0, step=50.0)
    T  = st.sidebar.number_input("Total capital (USDC)", value=10000.0, step=1000.0)

    st.sidebar.write("**LP Range**")
    P_lower = st.sidebar.number_input("P_lower", value=1400.0, step=50.0)
    P_upper = st.sidebar.number_input("P_upper", value=1800.0, step=50.0)

    st.sidebar.write("**Chart Settings**")
    chart_min = st.sidebar.number_input("Chart Price Min", value=800.0, step=50.0)
    chart_max = st.sidebar.number_input("Chart Price Max", value=2400.0, step=50.0)
    n_points  = st.sidebar.slider("Number of points", min_value=50, max_value=500, value=200)

    st.write("### Summary of Inputs")
    st.write(f"- P0 = {P0} (must satisfy {P_lower} < {P0} < {P_upper})")
    st.write(f"- Total capital (T) = {T}")
    st.write(f"- LP range = [{P_lower}, {P_upper}]")
    st.write(f"- Chart range = [{chart_min}, {chart_max}], {n_points} points")

    # 1) We deposit T/2 in USDC, T/(2*P0) in ETH
    usdc_init = T/2.0
    eth_init  = (T/2.0) / P0   # how many ETH

    st.write(f"- USDC deposited: {usdc_init:,.4f}")
    st.write(f"- ETH deposited:  {eth_init:,.4f}")

    # 2) Compute Liquidity L
    L = compute_liquidity(
        x_init=eth_init,     # how many ETH
        y_init=usdc_init,    # how many USDC
        P0=P0,
        P_lower=P_lower,
        P_upper=P_upper
    )
    st.write(f"**Computed Liquidity (L)** = {L:,.4f}")

    # 3) Evaluate over a range of prices
    prices = np.linspace(chart_min, chart_max, int(n_points))
    lp_values  = []
    hodl_values = []
    il_values  = []

    for P in prices:
        # A) HODL value:
        # We just keep eth_init ETH + usdc_init USDC
        # => total in USDC = usdc_init + eth_init * P
        hodl_val = usdc_init + eth_init * P

        # B) LP value
        lp_val = uniswap_v3_lp_value(P, L, P_lower, P_upper)

        # C) IL
        # IL(P) = 1 - (lp_val / hodl_val)  if hodl_val != 0
        if hodl_val > 0:
            il = 1.0 - (lp_val / hodl_val)
        else:
            il = 0.0

        lp_values.append(lp_val)
        hodl_values.append(hodl_val)
        il_values.append(il)

    # 4) Plot
    fig, ax = plt.subplots(1, 2, figsize=(12, 5))

    # (A) HODL vs. LP Value
    ax[0].plot(prices, hodl_values, label="HODL Value", color="blue")
    ax[0].plot(prices, lp_values,  label="LP Value",   color="red")
    ax[0].set_xlabel("ETH Price (USDC)")
    ax[0].set_ylabel("Value (USDC)")
    ax[0].set_title("HODL vs. LP Value")
    ax[0].legend()
    ax[0].grid(True)

    # (B) Impermanent Loss
    il_percent = np.array(il_values) * 100.0
    ax[1].plot(prices, il_percent, color="green", label="IL (%)")
    ax[1].axhline(0, color="black", linewidth=1)
    ax[1].set_xlabel("ETH Price (USDC)")
    ax[1].set_ylabel("Impermanent Loss (%)")
    ax[1].set_title("Impermanent Loss (Uniswap V3)")
    ax[1].legend()
    ax[1].grid(True)

    st.pyplot(fig)

if __name__ == "__main__":
    main()
