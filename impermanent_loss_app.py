import numpy as np
import matplotlib.pyplot as plt
import math

def uniswap_v3_value_unit(S, K, r):
    """
    Piecewise value function for ONE UNIT of Uniswap V3 liquidity
    (denominated in token B, e.g., USDC).
    """
    if S < (K / r):
        # Below lower bound => fully in token A, worth S (B) per A.
        return S
    elif S > (K * r):
        # Above upper bound => fully in token B, worth K.
        return K
    else:
        # Within the range => partial amounts of A and B.
        return (2.0 * math.sqrt(S * K * r) - S - K) / (r - 1.0)

def plot_uniswap_v3_lp_value(S0, t_L, t_H, V0):
    """
    Plots the total value of a Uniswap V3 LP position (in USDC)
    as the token A price S changes.
    
    Arguments:
        S0 : float
            Current price (A in terms of B, e.g. A/USDC).
        t_L : float
            Lower price bound for the LP position.
        t_H : float
            Upper price bound for the LP position.
        V0 : float
            Total initial value of the LP at price S0 (in USDC).
    """
    
    # 1) Compute K and r from t_L and t_H
    K = math.sqrt(t_L * t_H)
    r = math.sqrt(t_H / t_L)
    
    # 2) Compute the value of ONE UNIT of liquidity at S0
    value_unit_at_S0 = uniswap_v3_value_unit(S0, K, r)
    
    if value_unit_at_S0 == 0:
        raise ValueError("The 'unit' value at S0 is 0, cannot scale properly. "
                         "Check your bounds vs. S0.")
    
    # 3) Compute the scaling factor to ensure we get total value = V0 at S0
    alpha = V0 / value_unit_at_S0
    
    # 4) Create a range of prices around [t_L, t_H] for plotting
    #    (You can adjust these multipliers for a different zoom level.)
    price_min = 0.5 * t_L  # or max(1e-6, ...)
    price_max = 1.5 * t_H
    S_values = np.linspace(price_min, price_max, 200)
    
    # 5) Compute the scaled LP value for each price in S_values
    lp_values = [alpha * uniswap_v3_value_unit(S, K, r) for S in S_values]
    
    # 6) Plot
    plt.figure(figsize=(8, 5))
    plt.plot(S_values, lp_values, label='LP Value')
    
    # Mark your chosen bounds as vertical lines
    plt.axvline(x=t_L, color='red', linestyle='--', label='Lower Bound (t_L)')
    plt.axvline(x=t_H, color='green', linestyle='--', label='Upper Bound (t_H)')
    plt.axvline(x=S0, color='blue', linestyle=':', label='Starting Price (S0)')
    
    plt.title("Uniswap V3 LP Value vs. Price")
    plt.xlabel("Price of Token A in USDC (S)")
    plt.ylabel("LP Value in USDC")
    plt.legend()
    plt.grid(True)
    plt.show()

# -----------------------------
# Example usage:
if __name__ == "__main__":
    # Suppose you start at price S0=100 USDC per A,
    # pick a lower bound t_L=80 and upper bound t_H=120,
    # and deposit V0=10_000 USDC worth of liquidity.
    S0_example = 100
    t_L_example = 80
    t_H_example = 120
    V0_example = 10_000
    
    plot_uniswap_v3_lp_value(S0_example, t_L_example, t_H_example, V0_example)
