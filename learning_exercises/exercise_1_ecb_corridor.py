# Learning Exercise 1: ECB Corridor Calculation
# ============================================
#
# Objective: Understand how the ECB interest rate corridor guides overnight funding costs.
#
# What to implement:
# - Function to calculate corridor width between DFR (floor) and MLF (ceiling)
# - Estimate ESTR trading range within the corridor
# - Explain funding implications for banks
#
# Data Sources:
# - ECB rates: Fetch real data from ECB API using Risk_Factors
# - Series keys: DFR="FM.D.U2.EUR.4F.KR.DFR.LEV", MRO="FM.D.U2.EUR.4F.KR.MRR_FR.LEV",
#   legacy MRO="FM.D.U2.EUR.4F.KR.MRR_MBR.LEV", MLF="FM.D.U2.EUR.4F.KR.MLFR.LEV"
# - Use fetch_ecb_series from risk_factors.data_fetching.interest_rates_fetcher
#
# Hints:
# 1. Corridor width = MLF - DFR (in bps: multiply by 10000)
# 2. ESTR typically trades 3-10 bps inside the corridor
# 3. Banks won't lend below DFR or borrow above MLF
# 4. Test with different corridor widths (narrow: 25bps, wide: 200bps)
#
# Expected Output:
# - Dictionary with rates, width, ESTR range, implications
#
# Self-Assessment:
# - Can you explain why ECB uses a corridor?
# - How does corridor width affect interbank liquidity?
# - What happens if MLF = DFR (zero corridor)?

from risk_factors.data_fetching.interest_rates_fetcher import fetch_ecb_series
import pandas as pd
import matplotlib.pyplot as plt

def calculate_ecb_corridor(dfr: float, mro: float, mlf: float) -> dict:
    """Calculate ECB interest rate corridor and implications.

    Args:
        dfr: Deposit facility rate (floor)
        mro: Main refinancing operations rate (central)
        mlf: Marginal lending facility rate (ceiling)

    Returns:
        Dictionary with corridor analysis
    """
    # TODO: Implement corridor width calculation
    # TODO: Estimate ESTR trading range
    # TODO: Generate funding implications text

    if not dfr <= mro <= mlf:
        raise ValueError("Expected corridor ordering: dfr <= mro <= mlf")

    corridor_width_bps = round((mlf - dfr) * 10_000, 1)
    lower_spread_bps = round((mro - dfr) * 10_000, 1)
    upper_spread_bps = round((mlf - mro) * 10_000, 1)

    # Simple ESTR assumption:
    # ESTR typically trades close to the deposit facility rate,
    # usually slightly below or around DFR depending on liquidity conditions.
    estr_low = dfr - 0.0010  # 10 bps below DFR
    estr_high = dfr + 0.0005  # 5 bps above DFR

    if corridor_width_bps <= 50:
        corridor_type = "narrow"
        implication = (
            "A narrow corridor limits money-market rate volatility and keeps "
            "overnight rates closely anchored around the policy floor."
        )
    elif corridor_width_bps <= 100:
        corridor_type = "standard"
        implication = (
            "A standard corridor gives banks a moderate incentive to trade reserves "
            "in the interbank market while keeping rates bounded by ECB facilities."
        )
    else:
        corridor_type = "wide"
        implication = (
            "A wide corridor increases the potential dispersion of short-term funding "
            "rates and may make liquidity management more important for banks."
        )

    return {
        "dfr": dfr,
        "mro": mro,
        "mlf": mlf,
        "corridor_width_bps": corridor_width_bps,
        "mro_above_dfr_bps": lower_spread_bps,
        "mlf_above_mro_bps": upper_spread_bps,
        "corridor_type": corridor_type,
        "est_interbank_range": f"{estr_low:.4%} - {estr_high:.4%}",
        "funding_implications": implication,
    }

ECB_POLICY_RATE_SERIES = {
    "dfr": "FM.D.U2.EUR.4F.KR.DFR.LEV",
    "mro_fixed_rate": "FM.D.U2.EUR.4F.KR.MRR_FR.LEV",
    "mro_min_bid_legacy": "FM.D.U2.EUR.4F.KR.MRR_MBR.LEV",
    "mlf": "FM.D.U2.EUR.4F.KR.MLFR.LEV",
}

ESTR_SERIES_KEY = "EST.B.EU000A2X2A25.WT"

def fetch_ecb_policy_rate_history(years: int = 20) -> pd.DataFrame:
    start_date = pd.Timestamp.today() - pd.DateOffset(years=years)

    frames = []

    for name, series_key in ECB_POLICY_RATE_SERIES.items():
        df = fetch_ecb_series(series_key, start_date=start_date)
        df["rate"] = name
        frames.append(df)

    history = pd.concat(frames, ignore_index=True)

    wide = (
        history
        .pivot(index="date", columns="rate", values="value")
        .sort_index()
    )

    wide["mro"] = wide["mro_fixed_rate"].combine_first(wide["mro_min_bid_legacy"])

    return wide[["dfr", "mro", "mlf"]] / 100


def fetch_estr_history(years: int = 20) -> pd.DataFrame:
    """Fetch historical euro short-term rate data as decimal rates."""
    start_date = pd.Timestamp.today() - pd.DateOffset(years=years)
    estr = fetch_ecb_series(ESTR_SERIES_KEY, start_date=start_date)
    estr = estr.rename(columns={"value": "estr"}).set_index("date").sort_index()
    return estr[["estr"]] / 100

def calculate_ecb_corridor_history(policy_rates: pd.DataFrame) -> pd.DataFrame:
    """Add ECB corridor metrics to a historical policy-rate DataFrame.

    Args:
        policy_rates: DataFrame indexed by date with decimal-rate columns:
            dfr, mro, and mlf.

    Returns:
        DataFrame with original rates plus corridor/spread metrics.
    """
    required_columns = {"dfr", "mro", "mlf"}
    missing = required_columns.difference(policy_rates.columns)
    if missing:
        raise ValueError(f"policy_rates is missing required columns: {sorted(missing)}")

    corridor = policy_rates.copy().sort_index()
    corridor = corridor.dropna(subset=["dfr", "mro", "mlf"], how="all")

    corridor["corridor_width_bps"] = (corridor["mlf"] - corridor["dfr"]) * 10_000
    corridor["mro_above_dfr_bps"] = (corridor["mro"] - corridor["dfr"]) * 10_000
    corridor["mlf_above_mro_bps"] = (corridor["mlf"] - corridor["mro"]) * 10_000
    corridor["policy_rate_level"] = corridor[["dfr", "mro", "mlf"]].mean(axis=1)
    corridor["policy_rate_level_pct"] = corridor["policy_rate_level"] * 100

    return corridor


def add_estr_to_corridor_history(
    corridor_history: pd.DataFrame,
    estr_history: pd.DataFrame,
) -> pd.DataFrame:
    """Join ESTR to corridor history and calculate ESTR corridor-position metrics."""
    result = corridor_history.join(estr_history, how="left")
    result["estr_minus_dfr_bps"] = (result["estr"] - result["dfr"]) * 10_000
    result["estr_position_in_corridor"] = (
        (result["estr"] - result["dfr"]) / (result["mlf"] - result["dfr"])
    )
    return result


def summarize_corridor_history(corridor_history: pd.DataFrame) -> dict:
    """Summarize corridor regimes and rate-level relationship."""
    clean = corridor_history.dropna(subset=["corridor_width_bps", "policy_rate_level"])
    width_changes = clean["corridor_width_bps"].diff().dropna()

    return {
        "start_date": clean.index.min(),
        "end_date": clean.index.max(),
        "min_width_bps": clean["corridor_width_bps"].min(),
        "max_width_bps": clean["corridor_width_bps"].max(),
        "latest_width_bps": clean["corridor_width_bps"].iloc[-1],
        "latest_dfr": clean["dfr"].iloc[-1],
        "latest_mro": clean["mro"].iloc[-1],
        "latest_mlf": clean["mlf"].iloc[-1],
        "rate_level_width_correlation": clean["policy_rate_level"].corr(clean["corridor_width_bps"]),
        "widening_dates": width_changes[width_changes > 0].index.tolist(),
        "narrowing_dates": width_changes[width_changes < 0].index.tolist(),
    }


def interpret_corridor_history(corridor_history: pd.DataFrame) -> str:
    """Generate a concise economic interpretation of corridor behaviour."""
    summary = summarize_corridor_history(corridor_history)
    corr = summary["rate_level_width_correlation"]

    if pd.isna(corr):
        relationship = "The sample is not sufficient to estimate a rate-level/corridor-width relationship."
    elif abs(corr) < 0.25:
        relationship = (
            "The corridor width is only weakly related to the average level of policy rates. "
            "This suggests the corridor is mainly a monetary-policy operating-framework choice, "
            "not a mechanical function of whether rates are high or low."
        )
    elif corr > 0:
        relationship = (
            "The corridor tends to be wider when policy rates are higher in this sample, "
            "suggesting the ECB may allow more room around the policy target during tightening phases."
        )
    else:
        relationship = (
            "The corridor tends to be narrower when policy rates are higher in this sample, "
            "suggesting stronger anchoring of money-market rates during tightening phases."
        )

    widening_dates = summary["widening_dates"]
    narrowing_dates = summary["narrowing_dates"]
    widening_text = ", ".join(pd.Timestamp(date).strftime("%Y-%m-%d") for date in widening_dates[-5:]) or "none"
    narrowing_text = ", ".join(pd.Timestamp(date).strftime("%Y-%m-%d") for date in narrowing_dates[-5:]) or "none"

    return (
        f"ECB corridor history from {summary['start_date'].date()} to {summary['end_date'].date()}:\n"
        f"- Width range: {summary['min_width_bps']:.0f} to {summary['max_width_bps']:.0f} bps.\n"
        f"- Latest width: {summary['latest_width_bps']:.0f} bps "
        f"(DFR {summary['latest_dfr']:.2%}, MRO {summary['latest_mro']:.2%}, "
        f"MLF {summary['latest_mlf']:.2%}).\n"
        f"- Correlation between average policy-rate level and corridor width: {corr:.2f}.\n"
        f"- Recent widening dates: {widening_text}.\n"
        f"- Recent narrowing dates: {narrowing_text}.\n"
        f"{relationship}"
    )


def plot_ecb_corridor_history(corridor_history: pd.DataFrame) -> None:
    """Plot policy rates and corridor width through time."""
    clean = corridor_history.dropna(subset=["dfr", "mro", "mlf", "corridor_width_bps"], how="any")

    fig, ax_rates = plt.subplots(figsize=(12, 6))

    ax_rates.fill_between(
        clean.index,
        clean["dfr"] * 100,
        clean["mlf"] * 100,
        color="lightsteelblue",
        alpha=0.25,
        label="ECB corridor",
    )
    ax_rates.plot(clean.index, clean["dfr"] * 100, label="DFR", linewidth=1.8)
    ax_rates.plot(clean.index, clean["mro"] * 100, label="MRO", linewidth=1.8)
    ax_rates.plot(clean.index, clean["mlf"] * 100, label="MLF", linewidth=1.8)
    ax_rates.set_ylabel("Policy rate (%)")
    ax_rates.set_title("ECB policy-rate corridor and corridor width")
    ax_rates.grid(True, alpha=0.25)

    ax_width = ax_rates.twinx()
    ax_width.plot(
        clean.index,
        clean["corridor_width_bps"],
        color="black",
        linestyle="--",
        linewidth=1.4,
        label="Corridor width",
    )
    ax_width.set_ylabel("Corridor width (bps)")

    rate_handles, rate_labels = ax_rates.get_legend_handles_labels()
    width_handles, width_labels = ax_width.get_legend_handles_labels()
    ax_rates.legend(rate_handles + width_handles, rate_labels + width_labels, loc="best")

    fig.tight_layout()
    plt.show()


def plot_ecb_corridor_with_estr(corridor_history: pd.DataFrame) -> None:
    """Plot ECB policy corridor with observed ESTR."""
    policy_clean = corridor_history.dropna(subset=["dfr", "mro", "mlf"], how="any")
    estr_clean = corridor_history.dropna(subset=["estr"], how="any")

    fig, ax = plt.subplots(figsize=(12, 6))

    ax.fill_between(
        policy_clean.index,
        policy_clean["dfr"] * 100,
        policy_clean["mlf"] * 100,
        color="lightsteelblue",
        alpha=0.25,
        label="ECB corridor",
    )
    ax.plot(policy_clean.index, policy_clean["dfr"] * 100, label="DFR", linewidth=1.7)
    ax.plot(policy_clean.index, policy_clean["mro"] * 100, label="MRO", linewidth=1.7)
    ax.plot(policy_clean.index, policy_clean["mlf"] * 100, label="MLF", linewidth=1.7)
    ax.plot(estr_clean.index, estr_clean["estr"] * 100, label="ESTR", color="black", linewidth=1.3)

    ax.set_title("ECB policy-rate corridor and ESTR")
    ax.set_ylabel("Rate (%)")
    ax.grid(True, alpha=0.25)
    ax.legend(loc="best")

    fig.tight_layout()
    plt.show()


def plot_estr_spread_and_corridor_width(corridor_history: pd.DataFrame) -> None:
    """Plot ESTR minus DFR against ECB corridor width."""
    clean = corridor_history.dropna(subset=["estr_minus_dfr_bps", "corridor_width_bps"], how="any")

    fig, ax_spread = plt.subplots(figsize=(12, 5))

    ax_spread.axhline(0, color="gray", linewidth=1, alpha=0.6)
    ax_spread.plot(
        clean.index,
        clean["estr_minus_dfr_bps"],
        color="black",
        linewidth=1.4,
        label="ESTR - DFR",
    )
    ax_spread.set_ylabel("ESTR - DFR (bps)")
    ax_spread.set_title("ESTR anchoring versus ECB corridor width")
    ax_spread.grid(True, alpha=0.25)

    ax_width = ax_spread.twinx()
    ax_width.plot(
        clean.index,
        clean["corridor_width_bps"],
        color="tab:blue",
        linestyle="--",
        linewidth=1.4,
        label="Corridor width",
    )
    ax_width.set_ylabel("Corridor width (bps)")

    spread_handles, spread_labels = ax_spread.get_legend_handles_labels()
    width_handles, width_labels = ax_width.get_legend_handles_labels()
    ax_spread.legend(spread_handles + width_handles, spread_labels + width_labels, loc="best")

    fig.tight_layout()
    plt.show()


if __name__ == "__main__":
    policy_rates = fetch_ecb_policy_rate_history(years=25)
    estr_history = fetch_estr_history(years=25)
    corridor_history = calculate_ecb_corridor_history(policy_rates)
    corridor_history = add_estr_to_corridor_history(corridor_history, estr_history)
    print(interpret_corridor_history(corridor_history))
    plot_ecb_corridor_with_estr(corridor_history)
    plot_estr_spread_and_corridor_width(corridor_history)
