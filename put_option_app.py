import streamlit as st
import numpy as np
import matplotlib.pyplot as plt

def main():
    st.title("Put Option P/L Visualizer")

    st.markdown("""
    This app plots the **value (P/L) of a put option** in USD 
    as the underlying token price (in USD) changes.
    """)

    st.sidebar.header("Option Parameters")
    strike = st.sidebar.number_input("Strike Price (K)",
                                     key="put_strike",  # <--- UNIQUE KEY
                                     value=100.0,
                                     step=1.0,
                                     min_value=0.01)
    premium = st.sidebar.number_input("Premium (USD per contract)",
                                      key="put_premium",  # <--- UNIQUE KEY
                                      value=5.0,
                                      step=0.1,
                                      min_value=0.0)
    quantity = st.sidebar.number_input("Quantity (contracts)",
                                       key="put_qty",  # <--- UNIQUE KEY
                                       value=1.0,
                                       step=1.0,
                                       min_value=1.0)
    position_type = st.sidebar.selectbox("Position Type",
                                         ("Buy", "Sell"),
                                         key="put_position_type")  # <--- UNIQUE KEY

    st.sidebar.subheader("Plot Range for Token Price")
    S_min = st.sidebar.number_input("Min Token Price (USD)",
                                    key="put_price_min",  # <--- UNIQUE KEY
                                    min_value=0.0,
                                    value=0.0,
                                    step=1.0)
    S_max = st.sidebar.number_input("Max Token Price (USD)",
                                    key="put_price_max",  # <--- UNIQUE KEY
                                    min_value=0.01,
                                    value=200.0,
                                    step=1.0)

    if S_min >= S_max:
        st.error("Min Token Price must be strictly less than Max Token Price.")
        return

    prices = np.linspace(S_min, S_max, 300)
    payoff = []
    for S in prices:
        intrinsic = max(strike - S, 0.0)
        if position_type == "Buy":
            pl = intrinsic - premium
        else:
            pl = premium - intrinsic
        payoff.append(pl * quantity)

    fig, ax = plt.subplots(figsize=(8, 5))
    ax.plot(prices, payoff, label="Put Option P/L", color="purple")

    ax.axvline(x=strike, color='red', linestyle='--', label=f'Strike = {strike}')
    ax.axhline(y=0, color='black', linewidth=1)

    ax.set_title("Put Option P/L vs. Token Price")
    ax.set_xlabel("Token Price in USD")
    ax.set_ylabel("Option Value in USD")
    ax.grid(True)
    ax.legend()

    st.pyplot(fig)

if __name__ == "__main__":
    main()
