import streamlit as st
import numpy as np
import matplotlib.pyplot as plt

def main():
    st.title("Put Option P/L Visualizer")

    st.sidebar.header("Option Parameters")
    strike = st.sidebar.number_input("Strike Price (K)", 
                                     value=100.0, 
                                     step=1.0, 
                                     min_value=0.01)
    premium = st.sidebar.number_input("Premium Paid/Received", 
                                      value=5.0, 
                                      step=0.1, 
                                      min_value=0.0)
    quantity = st.sidebar.number_input("Quantity (number of contracts)", 
                                       value=1.0, 
                                       step=1.0, 
                                       min_value=1.0)
    position_type = st.sidebar.selectbox("Position Type", ("Buy", "Sell"))

    st.markdown("""
    **Instructions**:  
    - **Strike Price (K)**: the agreed-upon exercise price.  
    - **Premium**: 
      - If you're **buying** the put, this is what you pay.
      - If you're **selling** the put, this is what you receive.  
    - **Quantity**: how many contracts (or tokens, if it’s tokenized) you are trading.  
    - **Position Type**: Choose "Buy" if you are purchasing the put, or "Sell" if you are writing (selling) the put.  
    """)

    # Create a price range from near zero up to, say, 2× strike (adjust if you prefer)
    S_min = 0.0
    S_max = 2.0 * strike
    # Avoid S_min == S_max in extreme cases
    if S_max <= S_min:
        S_max = S_min + 1.0
    prices = np.linspace(S_min, S_max, 300)

    # Calculate P/L at each underlying price
    payoff = []
    for S in prices:
        # Intrinsic payoff of a put is max(K - S, 0)
        intrinsic = max(strike - S, 0.0)
        
        if position_type == "Buy":
            # If you BUY a put:
            #   payoff per contract = (K - S if S < K else 0) - premium
            #   total payoff = quantity * [that expression]
            pl = intrinsic - premium
        else:
            # If you SELL a put:
            #   payoff per contract = premium - (K - S if S < K else 0)
            pl = premium - intrinsic
        
        # Multiply by quantity
        payoff.append(pl * quantity)

    # --- Plotting ---
    fig, ax = plt.subplots(figsize=(8, 5))
    ax.plot(prices, payoff, label="Put Option P/L", color="blue")

    # Mark the strike
    ax.axvline(x=strike, color='red', linestyle='--', label=f'Strike = {strike}')
    ax.axhline(y=0, color='black', linewidth=1)

    ax.set_title("Put Option P/L vs. Underlying Price")
    ax.set_xlabel("Underlying Price (S)")
    ax.set_ylabel("Profit / Loss")
    ax.grid(True)
    ax.legend()

    st.pyplot(fig)

if __name__ == "__main__":
    main()
