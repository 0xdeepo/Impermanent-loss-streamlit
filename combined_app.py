import streamlit as st
import runpy

def main():
    st.title("My Combined App")

    st.subheader("1) Uniswap V3 App")
    runpy.run_path("uniswap_app.py", run_name="__main__")

    st.write("---")

    st.subheader("2) Put Option App")
    runpy.run_path("put_option_app.py", run_name="__main__")

    st.write("---")

    st.subheader("3) Something Else...")

if __name__ == "__main__":
    main()
