import streamlit as st
import numpy as np
import math
import matplotlib.pyplot as plt

def uniswap_v3_value_unit(S, K, r):
    if S < (K / r):
        return S
    elif S > (K * r):
        return K
    else:
        return (2.0 * math.sqrt(S * K * r) - S - K) / (r - 1.0)

def uniswap_lp_value(S, S0, t_L, t_H, V0):
    K = math.sqrt(t_L * t_H)
    r = math.sqrt(t_H / t_L)
    value_unit_at_S0 = uniswap_v3_value_unit(S0, K, r)
    if value_unit_at_S0 == 0:
        return 0.0
    alpha = V0 / value_unit_at_S0
    return alpha * uniswap_v3_value_unit(S, K, r)

def put_option_value(S, strike, premium, quantity, position_type):
    intrinsic = max(strike - S, 0.0)
    if position_type == "Buy":
        pl = intrinsic - premium
    else:
        pl = premium - intrinsic
    return pl * quantity

def main():
    st.title("Combined LP + Put Option Value Curve")

    st.sidebar.header("Uniswap LP Inputs")
    S0 = st.sidebar.number_input("LP: Current Price (S0)",
                                 key="lp_put_S0",  # <--- UNIQUE KEY
                                 value=100.0,
                                 step=1.0)
    t_L = st.sidebar.number_input("LP: Lower Bound (t_L)",
                                  key="lp_put_tL",  # <--- UNIQUE KEY
                                  value=80.0,
                                  step=1.0,
                                  min_value=0.01)
    t_H = st.sidebar.number_input("LP: Upper Bound (t_H)",
                                  key="lp_put_tH",  # <--- UNIQUE KEY
                                  value=120.0,
                                  step=1.0,
                                  min_value=0.01)
    V0 = st.sidebar.number_input("LP: Value @ S0 (USD)",
                                 key="lp_put_V0",  # <--- UNIQUE KEY
                                 value=10000.0,
                                 step=100.0,
                                 min_value=0.01)
    if t_L >= t_H:
        st.error("LP: t_L must be < t_H.")
        return

    st.sidebar.header("Put Option Inputs")
    strike = st.sidebar.number_input("Put: Strike Price",
                                     key="lp_put_strike",  # <--- UNIQUE KEY
                                     value=100.0,
                                     step=1.0,
                                     min_value=0.01)
    premium = st.sidebar.number_input("Put: Premium",
                                      key="lp_put_premium",  # <--- UNIQUE KEY
                                      value=5.0,
                                      step=0.1,
                                      min_value=0.0)
    quantity = st.sidebar.number_input("Put: Quantity",
                                       key="lp_put_qty",  # <--- UNIQUE KEY
                                       value=1.0,
                                       step=1.0,
                                       min_value=1.0)
    position_type = st.sidebar.selectbox("Put: Position Type",
                                         ["Buy", "Sell"],
                                         key="lp_put_position_type")  # <--- UNIQUE KEY

    st.sidebar.header("Plot Range")
    price_min = st.sidebar.number_input("Min Token Price (USD)",
                                        key="lp_put_price_min",  # <--- UNIQUE KEY
                                        value=50.0,
                                        step=1.0,
                                        min_value=0.0)
    price_max = st.sidebar.number_input("Max Token Price (USD)",
                                        key="lp_put_price_max",  # <--- UNIQUE KEY
                                        value=200.0,
                                        step=1.0,
                                        min_value=0.01)
    if price_min >= price_max:
        st.error("Min Token Price must be < Max Token Price.")
        return

    S_values = np.linspace(price_min, price_max, 400)
    lp_vals = []
    put_vals = []
    combined_vals = []

    for S in S_values:
        lp_v = uniswap_lp_value(S, S0, t_L, t_H, V0)
        put_v = put_option_value(S, strike, premium, quantity, position_type)
        lp_vals.append(lp_v)
        put_vals.append(put_v)
        combined_vals.append(lp_v + put_v)

    fig, ax = plt.subplots(figsize=(8, 5))
    ax.plot(S_values, lp_vals, label="LP Value", color="blue")
    ax.plot(S_values, put_vals, label="Put Value", color="purple")
    ax.plot(S_values, combined_vals, label="LP + Put", color="green", linewidth=2)

    ax.axvline(x=strike, color="red", linestyle="--", label=f"Strike={strike}")
    ax.axhline(y=0, color="black", linewidth=1)
    ax.set_title("LP + Put Option Combined Value Curve")
    ax.set_xlabel("Token Price in USD")
    ax.set_ylabel("Value in USD")
    ax.grid(True)
    ax.legend()

    st.pyplot(fig)

if __name__ == "__main__":
    main()
