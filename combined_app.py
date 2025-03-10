import streamlit as st
import runpy

def main():
    st.title("Single-Page App: Uniswap LP + Put Option + Combined Hedge")

    st.subheader("1) Uniswap V3 LP Value App")
    runpy.run_path("uniswap_app.py", run_name="__main__")

    st.write("---")

    st.subheader("2) Put Option P/L App")
    runpy.run_path("put_option_app.py", run_name="__main__")

    st.write("---")

    st.subheader("3) Combined LP + Put Option Hedging App")
    runpy.run_path("lp_plus_put_app.py", run_name="__main__")

if __name__ == "__main__":
    main()
