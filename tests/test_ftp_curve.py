import pytest

from ftp_simulation.curves import (
    ProductFTPRequest,
    build_sample_market_inputs,
    construct_ftp_curve,
    load_risk_weight_factors,
    regulatory_capital_spread,
    quote_product_ftp_rate,
)


def test_construct_ftp_curve_decomposes_all_in_rate():
    market_inputs = build_sample_market_inputs()

    curve = construct_ftp_curve(market_inputs)

    five_year = curve.loc[curve["tenor"] == "5Y"].iloc[0]
    assert five_year["all_in_ftp_rate"] == pytest.approx(0.0350 + 0.0055 + 0.0040)
    assert five_year["all_in_ftp_bps"] == pytest.approx(445.0)


def test_quote_product_ftp_rate_uses_product_behavior_adjustment():
    curve = construct_ftp_curve(build_sample_market_inputs())
    product = ProductFTPRequest(
        product_name="5Y corporate term loan",
        product_type="corporate_loan",
        side="asset",
        balance_eur_m=155_000,
        maturity_years=5.0,
    )

    quote = quote_product_ftp_rate(product, curve)

    assert quote["base_curve_rate"] == pytest.approx(0.0350)
    assert quote["bank_funding_spread"] == pytest.approx(0.0055)
    assert quote["liquidity_premium"] == pytest.approx(0.0040)
    assert quote["behavior_adjustment"] == pytest.approx(0.0008)
    assert quote["all_in_ftp_rate"] == pytest.approx(0.0453)


def test_quote_product_ftp_rate_can_include_regulatory_capital_spread():
    curve = construct_ftp_curve(build_sample_market_inputs())
    product = ProductFTPRequest(
        product_name="5Y corporate term loan",
        product_type="corporate_loan",
        side="asset",
        balance_eur_m=155_000,
        maturity_years=5.0,
        counterparty_type="corporate",
    )

    quote = quote_product_ftp_rate(product, curve)

    assert quote["risk_weight"] == pytest.approx(1.15)
    assert quote["regulatory_capital_spread"] == pytest.approx(1.15 * 0.13 * 0.10)
    assert quote["all_in_ftp_rate"] == pytest.approx(0.0453 + 0.01495)


def test_regulatory_capital_spread_allows_risk_weight_override():
    product = ProductFTPRequest(
        product_name="Overridden product",
        product_type="corporate_loan",
        side="asset",
        balance_eur_m=100,
        maturity_years=3.0,
        risk_weight_override=0.42,
    )

    assert regulatory_capital_spread(product) == pytest.approx(0.42 * 0.13 * 0.10)


def test_load_risk_weight_factors_from_static_table():
    factors = load_risk_weight_factors()

    assert set(factors.columns) == {
        "product_type",
        "counterparty_type",
        "base_risk_weight",
        "short_maturity_multiplier",
        "long_maturity_multiplier",
    }
