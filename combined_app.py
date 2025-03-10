import streamlit as st
import runpy

def main():
    st.title("Combined Single-Page App")

    st.subheader("1) Uniswap V3 LP Value")
    # IMPORTANT: pass run_name="__main__" so the script actually runs
    runpy.run_path("uniswap_app.py", run_name="__main__")

    st.write("---")  # A horizontal divider

    st.subheader("2) Put Option P/L")
    # Again, use run_name="__main__"
    runpy.run_path("put_option_app.py", run_name="__main__")

if __name__ == "__main__":
    main()
