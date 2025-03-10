import streamlit as st
import numpy as np
import pandas as pd
import altair as alt

"""
Uniswap v3 Concentrated Liquidity Impermanent Loss Demo
"""

def get_liquidity_for_50_50(p_upper):
    """
    Given an upper bound p_upper > 1 (price of token0 in token1 terms),
    solve for the lower bound p_lower so that depositing at price=1
    results in a 50/50 dollar split between token0 and token1.

    Also returns the liquidity L assuming we deposit 1 token0 + 1 token1.
    """
    # pLower is determined by the condition that at P=1, the amounts of token0 and token1
    # are equal (in units).  From the Uniswap v3 formulas:
    #
    #   amount0 = L * (sqrt(p_upper) - sqrt(P))        [P=1 => sqrt(P)=1]
    #   amount1 = L * (1/sqrt(P) - 1/sqrt(p_lower))
    # for a 50/50 “by dollar” deposit at P=1, we want amount0 = amount1.
    # That implies:  sqrt(p_upper) - 1 = 1 - 1/sqrt(p_lower)
    # => sqrt(p_upper) + 1/sqrt(p_lower) = 2
    # => 1/sqrt(p_lower) = 2 - sqrt(p_upper)
    # => p_lower = 1 / (2 - sqrt(p_upper))^2

    sqrt_p_upper = np.sqrt(p_upper)
    # Ensure we stay below 4 so (2 - sqrt_p_upper) stays positive
    p_lower = 1.0 / (2.0 - sqrt_p_upper) ** 2

    # Now we find L such that amount0 = 1 token of token0.
    # amount0 = 1 => 1 = L * (sqrt_p_upper - 1)
    L = 1.0 / (sqrt_p_upper - 1.0)

    return p_lower, L

def final_holdings_and_value(p, p_lower, p_upper, L):
    """
    Given a final price p and a Uniswap v3 position covering [p_lower, p_upper]
    with liquidity L (all prices are token0 in terms of token1),
    return (amount0, amount1, total_value_in_token1).

    We measure "value" in units of token1 (e.g. USDC).
    """
    sqrt_p       = np.sqrt(p)
    sqrt_p_lower = np.sqrt(p_lower)
    sqrt_p_upper = np.sqrt(p_upper)

    if p < p_lower:
        # Entire position in token0
        amount0 = L * (sqrt_p_upper - sqrt_p_lower)
        amount1 = 0.0
    elif p > p_upper:
        # Entire position in token1
        amount0 = 0.0
        amount1 = L * (1.0/sqrt_p_lower - 1.0/sqrt_p_upper)
    else:
        # Price is in range
        amount0 = L * (sqrt_p_upper - sqrt_p)
        amount1 = L * (1.0/sqrt_p - 1.0/sqrt_p_lower)

    # Total value in terms of token1
    total_value = amount0 * p + amount1
    return amount0, amount1, total_value

def impermanent_loss_v3(p, p_lower, p_upper, L):
    """
    Compare final value of the LP position vs. simply holding 1 token0 + 1 token1.
    We deposited 1 of token0 + 1 of token1 originally, so "HODL" final value = p + 1.
    Returns IL in % (negative => underperforming HODL).
    """
    _, _, lp_value = final_holdings_and_value(p, p_lower, p_upper, L)
    hold_value = p + 1.0  # if we simply held 1 token0 + 1 token1
    return 100.0 * (lp_value - hold_value) / hold_value

def main():
    st.title("Uniswap v3 Concentrated Liquidity IL Demo (50/50 at P=1)")

    st.markdown("""
    This app shows how impermanent loss behaves for a **concentrated liquidity**  
    position (Uniswap v3 style) when you set a lower and upper price bound  
    such that your initial deposit is 50/50 by dollar value at price = 1.  
    (Imagine 1 ETH = 1 USDC for simplicity.)

    - **pUpper**: Upper bound on the price of token0 in token1 terms.  
      We solve for **pLower** automatically so that at P=1, half your  
      capital is in token0 and half in token1.
    - We deposit exactly 1 token0 and 1 token1 at P=1 (total $2).  
    - Then we track the final value of your LP vs. simply _holding_ those  
      1 token0 + 1 token1 as price changes from below 0.2× up to 5×.
    """)

    p_upper = st.slider("Pick pUpper (must be < 4 so 50/50 is possible)", 
                        min_value=1.01, max_value=3.99, value=2.0, step=0.01)
    p_lower, L = get_liquidity_for_50_50(p_upper)

    st.write(f"**Computed pLower** = {p_lower:.4f}")
    st.write(f"**Liquidity L**     = {L:.4f}")

    # Range of final prices to plot
    prices = np.linspace(0.2, 5.0, 200)
    il_list = [impermanent_loss_v3(p, p_lower, p_upper, L) for p in prices]

    df = pd.DataFrame({
        "Final Price (token0 in token1)": prices,
        "Impermanent Loss (%)": il_list
    })

    chart = (
        alt.Chart(df)
        .mark_line(color="red", strokeWidth=3)
        .encode(
            x=alt.X("Final Price (token0 in token1)", title="Final Price (P)"),
            y=alt.Y("Impermanent Loss (%)", title="IL vs. Just Holding ( % )")
        )
        .properties(width=700, height=400)
    )
    st.altair_chart(chart, use_container_width=True)

    st.markdown("""
    **Interpretation**  
    - If the final price leaves your [pLower, pUpper] range, you end up  
      holding effectively all one token (whichever side you'd be "pushed" into).  
    - Within the range, you hold some of each.  
    - The red line shows how your final LP value compares to holding 1 token0 + 1 token1.
    """)

if __name__ == "__main__":
    main()
