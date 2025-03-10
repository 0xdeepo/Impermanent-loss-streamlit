import streamlit as st
import runpy

def main():
    st.title("Combined Single-Page App")

    st.write("## 1) Uniswap V3 LP Value")
    # Run the uniswap_app.py in the current Python process
    runpy.run_path("uniswap_app.py")

    st.write("---")  # A horizontal rule to separate sections

    st.write("## 2) Put Option P/L")
    # Run the put_option_app.py in the current Python process
    runpy.run_path("put_option_app.py")

if __name__ == "__main__":
    main()
