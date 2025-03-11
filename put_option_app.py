import streamlit as st
import numpy as np
import matplotlib.pyplot as plt
import math

def put_intrinsic_value(S, K, quantity):
    """
    Intrinsic value = max(K-S, 0), scaled by quantity.
    """
    return quantity * max(K - S, 0.0)

def put_pnl(S, K, premium, quantity, position_type):
    """
    PNL at expiration:
      If 'Buy': (intrinsic - premium) * quantity
      If 'Sell': (premium - intrinsic) * quantity
    """
    intrinsic = max(K - S, 0.0)
    if position_type == "Buy":
        return (intrinsic - premium) * quantity
    else:
        return (premium - intrinsic) * quantity

def main():
    st.title("Put Option: Intrinsic Value and PNL (Expiration)")

    st.markdown("""
    **This script** shows:
    1. **Intrinsic Value** = \\( \\max(K - S,0) \\times \\text{quantity}\\)
    2. **PNL**:
       - If **Buy**: \\( (\\max(K-S,0) - \\text{premium}) \\times \\text{quantity}\\)
       - If **Sell**: \\( (\\text{premium} - \\max(K-S,0)) \\times \\text{quantity}\\)

    No theoretical model or delta is used here—just payoff at expiration.
    """)

    st.sidebar.header("Put Option Parameters")
    strike = st.sidebar.number_input("Strike Price (K)",
                                     key="put_strike_bs",
                                     value=100.0,
                                     step=1.0,
                                     min_value=0.01)
    premium = st.sidebar.number_input("Premium Paid/Received",
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

    st.sidebar.subheader("Plot Range for Underlying Price")
    S_min = st.sidebar.number_input("Min Token Price (USD)",
                                    key="put_price_min_bs",
                                    min_value=0.0,
                                    value=0.0,   # It's okay to allow 0 here if we want to see payoff at 0
                                    step=1.0)
    S_max = st.sidebar.number_input("Max Token Price (USD)",
                                    key="put_price_max_bs",
                                    min_value=0.01,
                                    value=200.0,
                                    step=1.0)

    if S_min >= S_max:
        st.error("Min price must be strictly less than Max price.")
        return

    prices = np.linspace(S_min, S_max, 300)

    # Compute the lines
    intrinsic_vals = []
    pnl_vals = []

    for S in prices:
        iv = put_intrinsic_value(S, strike, quantity)
        p = put_pnl(S, strike, premium, quantity, position_type)
        intrinsic_vals.append(iv)
        pnl_vals.append(p)

    fig, ax = plt.subplots(figsize=(8, 5))
    ax.plot(prices, intrinsic_vals, label="Intrinsic Value", linestyle="--")
    ax.plot(prices, pnl_vals, label="PNL", linewidth=2)

    ax.axvline(x=strike, color='red', linestyle='--', label=f"Strike={strike}")
    ax.axhline(y=0, color='black', linewidth=1)

    ax.set_title("Put Option: Intrinsic Value & PNL at Expiration")
    ax.set_xlabel("Underlying Price (S)")
    ax.set_ylabel("Value / PNL (USD)")
    ax.grid(True)
    ax.legend()

    st.pyplot(fig)

if __name__ == "__main__":
    main()
