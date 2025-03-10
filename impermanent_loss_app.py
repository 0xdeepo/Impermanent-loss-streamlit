import streamlit as st
import numpy as np
import pandas as pd
import altair as alt

def impermanent_loss_ratio(price_ratio):
    """
    Returns the impermanent loss (in %) for a simple 50/50 pool, 
    given a price ratio `price_ratio` = (new_price / initial_price).
    """
    # Value if simply held the two assets: 1 unit of each, so total = price_ratio + 1
    value_if_held = price_ratio + 1.0

    # Value of LP position in a constant-product 50/50 AMM after price changes:
    # We'll have sqrt(price_ratio) units of the appreciated asset, 
    # and 1/sqrt(price_ratio) of the other, each worth sqrt(price_ratio) 
    # times the initial price. So total = 2 * sqrt(price_ratio).
    value_in_pool = 2.0 * np.sqrt(price_ratio)

    # Impermanent loss = (LP value - hold value) / hold value
    il = (value_in_pool - value_if_held) / value_if_held
    return il * 100.0  # Convert to percent

def main():
    st.title("Impermanent Loss Demonstration")

    st.markdown(
        """
        This app illustrates the concept of **impermanent loss** in a
        simple 50/50 constant-product Automated Market Maker (AMM).
        
        - The **x-axis** is the ratio of the new price to the initial price
          (so 200% means the price doubled).
        - The **y-axis** shows how much more (or less) a liquidity provider 
          would have if they had simply held both assets instead of depositing 
          them into the AMM.
        """
    )

    # Allow the user to tweak the range of price ratios:
    min_ratio = st.slider("Minimum price ratio (%)", 1, 100, 1)
    max_ratio = st.slider("Maximum price ratio (%)", 100, 1000, 500)
    n_points = st.slider("Number of points", 10, 200, 100)

    # Generate an array of price ratios:
    # Convert them from integer percentages (like 100, 200) to float (1.0, 2.0), etc.
    ratios = np.linspace(min_ratio / 100, max_ratio / 100, n_points)

    # Calculate impermanent loss for each ratio
    il_values = [impermanent_loss_ratio(r) for r in ratios]

    # Prepare data for plotting
    df = pd.DataFrame({
        'Price Ratio (%)': ratios * 100,  # back to percentage for labeling
        'Impermanent Loss (%)': il_values
    })

    chart = (
        alt.Chart(df)
        .mark_line(color="red", strokeWidth=3)
        .encode(
            x=alt.X('Price Ratio (%)', title="Current price as % of initial"),
            y=alt.Y('Impermanent Loss (%)', title="IL relative to simply holding")
        )
        .properties(width=700, height=400)
    )

    st.altair_chart(chart, use_container_width=True)

    st.markdown(
        """
        **Note**: The curve peaks around 1× (i.e., no price change). 
        The farther the price moves away from the initial, the more 
        the LP underperforms compared to simply holding the assets. 
        However, once you withdraw your liquidity and realize the loss, 
        it becomes "permanent"—hence the name "impermanent loss" 
        (assuming you might exit before the price returns).
        """
    )

if __name__ == "__main__":
    main()
