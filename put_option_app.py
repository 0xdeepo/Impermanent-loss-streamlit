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
                                     value=100.0, 
                                     step=1.0, 
                                     min_value=0.01)
    premium = st.sidebar.number_input("Premium (USD per contract)", 
                                      value=5.0, 
                                      step=0.1, 
                                      min_value=0.0)
    quantity = st.sidebar.number_input("Quantity (contracts)", 
                                       value=1.0, 
                                       step=1.0, 
                                       min_value=1.0)
    position_type = st.sidebar.selectbox("Position Type", ("Buy", "Sell"))

    st.markdown("""
    **Instructions**:  
    - **Strike Price (K)**: the exercise price.  
    - **Premium**: cost (if buying) or credit (if selling) per contract.  
    - **Quantity**: number of contracts.  
    - **Position Type**: "Buy" for buying the put, "Sell" for writing the put.  
    """)

    st.sidebar.subheader("Plot Range for Token Price")
    S_min = st.sidebar.number_input("Min Token Price (USD)", 
                                    min_value=0.0, 
                                    value=0.0, 
                                    step=1.0)
    S_max = st.sidebar.number_input("Max Token Price (USD)", 
                                    min_value=0.01, 
                                    value=2.0*strike, 
                                    step=1.0)

    if S_min >= S_max:
        st.error("Min Token Price must be strictly less than Max Token Price.")
        return

    # Generate the underlying price range
    prices = np.linspace(S_min, S_max, 300)

    # Calculate P/L at each price
    payoff = []
    for S in prices:
        # Intrinsic payoff of a put is max(K - S, 0)
        intrinsic = max(strike - S, 0.0)
        
        if position_type == "Buy":
            # payoff (per contract) = (K-S if S<K else 0) - premium
            pl = intrinsic - premium
        else:
            # payoff (per contract) = premium - (K-S if S<K else 0)
            pl = premium - intrinsic
        
        # Multiply by quantity
        payoff.append(pl * quantity)

    # Plot
    fig, ax = plt.subplots(figsize=(8, 5))
    ax.plot(prices, payoff, label="Put Option P/L", color="purple")

    # Mark the strike
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
