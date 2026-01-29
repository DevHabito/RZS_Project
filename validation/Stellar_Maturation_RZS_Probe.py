import numpy as np

# ============================================================
# RZS EXPLORATORY MODEL
# ------------------------------------------------------------
# This code implements a phenomenological mapping
# inspired by the Relational Zero State (RZS) logic.
#
# This is NOT a direct physical inference.
# Alpha (α) is treated as a proxy for relational noise,
# and stability is a normalized, dimensionless measure.
# ============================================================

def calculate_stability(alpha, zero_state, beta=1.0):
    """
    Measures normalized relational stability (0–1),
    decaying with distance from the relational zero state.

    Parameters:
    - alpha: IMF slope (phenomenological proxy)
    - zero_state: hypothetical relational rest state
    - beta: decay rate (sensitivity control)

    Returns:
    - normalized stability (0 to 1)
    """
    return np.exp(-beta * abs(alpha - zero_state))


def explore_rzs_maturation(
    zero_state=1.5,
    beta=1.0,
    alpha_min=1.5,
    alpha_max=2.35,
    n_points=100,
    target_stability=0.90
):
    print("=" * 80)
    print("RZS EXPLORATORY MAPPING (PHENOMENOLOGICAL MODEL)")
    print("=" * 80)

    alphas = np.linspace(alpha_max, alpha_min, n_points)

    print(f"{'Regime':<30} | {'α':<6} | {'Stability (RZS)':<20}")
    print("-" * 80)

    alpha_target = None

    for a in alphas:
        stability = calculate_stability(a, zero_state, beta)

        if abs(a - 2.35) < 0.01:
            print(f"{'Salpeter IMF (reference)':<30} | {a:<6.2f} | {stability:.3f}")

        if abs(a - 2.15) < 0.01:
            print(f"{'Low-Z regimes (halo)':<30} | {a:<6.2f} | {stability:.3f}")

        if stability >= target_stability and alpha_target is None:
            alpha_target = a
            print(f"\n>>> HIGH RZS STABILITY REGIME IDENTIFIED")
            print(f"{'Relative rest point':<30} | {a:<6.2f} | {stability:.3f}")

        if abs(a - zero_state) < 0.01:
            print(f"{'Relational zero state':<30} | {a:<6.2f} | {stability:.3f}")

    print("=" * 80)

    if alpha_target is not None:
        print("INTERPRETATION (QUALITATIVE):")
        print(
            f"The model suggests that regimes with α ≲ {alpha_target:.2f} "
            "exhibit high relational stability within the RZS logic.\n"
            "This does NOT imply observational confirmation, but indicates\n"
            "a conceptual transition domain toward low-noise systems."
        )
    else:
        print("No regime reached the defined stability threshold.")

    print("\nLIMITATIONS:")
    print("- Non-causal relationships")
    print("- No fitting to observational data")
    print("- Alpha used only as a relational proxy")


if __name__ == "__main__":
    explore_rzs_maturation()
