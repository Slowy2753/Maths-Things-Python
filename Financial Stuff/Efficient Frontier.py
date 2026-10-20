#!/usr/bin/env python3
"""
Historical comparison and efficient-frontier analysis for three ETFs
(All-World, Momentum, Value) and several fixed-weight blends.

Downloads adjusted daily prices via Yahoo Finance, samples month-end prices,
and calculates monthly total-return proxies. Output is saved next to this script.

Important:
- Yahoo Finance adjusted prices are a proxy, not an official NAV feed.
- The analysis uses the common date range across all three ETFs.
- Frontier uses historical monthly arithmetic mean returns and covariance,
  annualised by 12; this is a historical estimate, not a forecast.
- All blends are rebalanced monthly.
"""

from pathlib import Path

import numpy as np
import pandas as pd
import yfinance as yf
import matplotlib.pyplot as plt
from scipy.optimize import minimize

# Order matters: column 0 = All-World, 1 = Momentum, 2 = Value.
TICKERS = {
    "All-World (VWRL)": "VWRL.L",
    "Momentum (IWFM)": "IWFM.L",
    "Value (IWFV)": "IWFV.L",
}

# Fixed-weight portfolios, weights in the same order as TICKERS.
PORTFOLIOS = {
    "100% All-World": [1.00, 0.00, 0.00],
    "60/20/20": [0.60, 0.20, 0.20],
    "60/30/10": [0.60, 0.30, 0.10],
    "70/30/0": [0.70, 0.30, 0.00],
}

START = "2000-01-01"
INITIAL_INVESTMENT = 1000.0
OUT = Path(__file__).resolve().parent


def download_adjusted_monthly(tickers, start):
    frames = {}
    for name, ticker in tickers.items():
        print(f"Downloading {name}: {ticker}")
        data = yf.download(
            ticker, start=start, auto_adjust=True, actions=False,
            progress=False, interval="1d", group_by="column"
        )
        if data.empty:
            raise RuntimeError(
                f"No data returned for {ticker}. Check the ticker and Yahoo Finance availability."
            )
        close = data["Close"]
        if isinstance(close, pd.DataFrame):
            if ticker in close.columns:
                close = close[ticker]
            else:
                close = close.iloc[:, 0]
        close = close.dropna()
        month_end = close.resample("ME").last().dropna()
        frames[name] = month_end.rename(name)

    prices = pd.concat(frames.values(), axis=1, join="inner").dropna()
    if len(prices) < 24:
        raise RuntimeError(
            "Fewer than 24 common month-end observations. Check ticker listings and available history."
        )
    return prices


def portfolio_stats(weights, mean_returns, cov):
    annual_return = float(np.dot(weights, mean_returns) * 12)
    annual_vol = float(np.sqrt(weights @ cov @ weights * 12))
    return annual_return, annual_vol


def optimize_frontier(mean_returns, cov, points=120):
    n = len(mean_returns)
    bounds = [(0.0, 1.0)] * n
    constraint_sum = {"type": "eq", "fun": lambda w: np.sum(w) - 1.0}
    max_return = float(np.max(mean_returns) * 12)
    min_return = float(np.min(mean_returns) * 12)
    targets = np.linspace(min_return, max_return, points)
    rows = []
    for target in targets:
        constraints = [
            constraint_sum,
            {"type": "eq", "fun": lambda w, t=target: np.dot(w, mean_returns) * 12 - t},
        ]
        result = minimize(
            lambda w: w @ cov @ w * 12,
            np.full(n, 1 / n),
            method="SLSQP",
            bounds=bounds,
            constraints=constraints,
            options={"maxiter": 2000, "ftol": 1e-12},
        )
        if result.success:
            ret, vol = portfolio_stats(result.x, mean_returns, cov)
            rows.append({
                "annual_return": ret,
                "annual_volatility": vol,
                **{f"weight_{i}": float(result.x[i]) for i in range(n)},
            })
    return pd.DataFrame(rows)


def summarise(name, r):
    growth = (1 + r).cumprod()
    return {
        "portfolio": name,
        "cumulative_return": float(growth.iloc[-1] - 1),
        "annualised_geometric_return": float((1 + r).prod() ** (12 / len(r)) - 1),
        "annualised_volatility": float(r.std(ddof=1) * np.sqrt(12)),
        "max_drawdown": float((growth / growth.cummax() - 1).min()),
    }


def main():
    prices = download_adjusted_monthly(TICKERS, START)
    returns = prices.pct_change().dropna()
    names = list(returns.columns)
    if len(names) != 3:
        raise RuntimeError("Expected three ETF series.")
    mean_returns = returns.mean().to_numpy()
    cov = returns.cov().to_numpy()

    # Monthly-rebalanced return series for each fixed-weight portfolio.
    weights_map = {}
    for label, w in PORTFOLIOS.items():
        w = np.array(w, dtype=float)
        if len(w) != 3 or not np.isclose(w.sum(), 1.0):
            raise ValueError(f"Weights for '{label}' must have 3 entries summing to 1: {w}")
        weights_map[label] = w
    portfolio_returns = pd.DataFrame(
        {label: returns.to_numpy() @ w for label, w in weights_map.items()},
        index=returns.index,
    )

    # Value today of £1,000 invested at each month-end start date, held to the end.
    start_dates = prices.index
    end_date = returns.index[-1]
    start_date_values = pd.DataFrame(index=start_dates, columns=portfolio_returns.columns, dtype=float)
    for start_date in start_dates:
        if start_date >= end_date:
            start_date_values.loc[start_date, :] = INITIAL_INVESTMENT
            continue
        mask = (portfolio_returns.index > start_date) & (portfolio_returns.index <= end_date)
        start_date_values.loc[start_date, :] = (
            INITIAL_INVESTMENT * (1 + portfolio_returns.loc[mask]).prod()
        )

    growth = INITIAL_INVESTMENT * (1 + portfolio_returns).cumprod()

    # Summary statistics: individual funds, then blends.
    summary_rows = [summarise(name, returns[name]) for name in names]
    summary_rows += [summarise(label, portfolio_returns[label]) for label in portfolio_returns.columns]
    summary = pd.DataFrame(summary_rows)

    # Frontier and max historical Sharpe (rf = 0).
    frontier = optimize_frontier(mean_returns, cov)

    def neg_sharpe(w):
        ret, vol = portfolio_stats(w, mean_returns, cov)
        return -(ret / vol) if vol > 0 else 1e6

    opt = minimize(
        neg_sharpe, np.full(3, 1 / 3), method="SLSQP",
        bounds=[(0.0, 1.0)] * 3,
        constraints=[{"type": "eq", "fun": lambda w: np.sum(w) - 1}],
        options={"maxiter": 2000, "ftol": 1e-12},
    )
    opt_weights = opt.x if opt.success else np.full(3, np.nan)
    opt_ret, opt_vol = portfolio_stats(opt_weights, mean_returns, cov)

    # CSV outputs.
    prices.to_csv(OUT / "monthly_adjusted_prices.csv")
    returns.to_csv(OUT / "monthly_returns.csv")
    portfolio_returns.to_csv(OUT / "portfolio_monthly_returns.csv")
    start_date_values.to_csv(OUT / "lump_sum_value_by_start_date.csv")
    frontier.to_csv(OUT / "efficient_frontier.csv", index=False)
    summary.to_csv(OUT / "summary_statistics.csv", index=False)
    pd.DataFrame({"asset": names, "weight": opt_weights}).to_csv(OUT / "max_sharpe_weights.csv", index=False)

    # Chart 1: value today by investment start date.
    fig, ax = plt.subplots(figsize=(11, 6.5))
    for label in start_date_values.columns:
        ax.plot(start_date_values.index, start_date_values[label], label=label, linewidth=2)
    ax.set_yscale("log")
    ax.set_xlabel("Investment start date")
    ax.set_ylabel("Value today (£), log scale")
    ax.set_title(f"Value today of £{INITIAL_INVESTMENT:,.0f} invested at each month-end")
    ax.grid(True, which="both", alpha=0.25)
    ax.legend()
    fig.tight_layout()
    fig.savefig(OUT / "start_date_comparison.png", dpi=180)
    plt.close(fig)

    # Chart 2: growth of £1,000 over the common period.
    fig, ax = plt.subplots(figsize=(11, 6.5))
    for label in growth.columns:
        ax.plot(growth.index, growth[label], label=label, linewidth=2)
    ax.set_yscale("log")
    ax.set_xlabel("Date")
    ax.set_ylabel("Portfolio value (£), log scale")
    ax.set_title(f"Growth of £{INITIAL_INVESTMENT:,.0f}, common period (monthly rebalanced)")
    ax.grid(True, which="both", alpha=0.25)
    ax.legend()
    fig.tight_layout()
    fig.savefig(OUT / "portfolio_growth_comparison.png", dpi=180)
    plt.close(fig)

    # Chart 3: efficient frontier with individual funds and all blends.
    fig, ax = plt.subplots(figsize=(10, 7))
    if not frontier.empty:
        ax.plot(frontier["annual_volatility"] * 100, frontier["annual_return"] * 100,
                label="Long-only efficient frontier", linewidth=2)
    for i, name in enumerate(names):
        ret, vol = portfolio_stats(np.eye(3)[i], mean_returns, cov)
        ax.scatter(vol * 100, ret * 100, s=55, label=name)
    for label, w in weights_map.items():
        ret, vol = portfolio_stats(w, mean_returns, cov)
        ax.scatter(vol * 100, ret * 100, s=75, marker="D", label=label)
    ret, vol = portfolio_stats(opt_weights, mean_returns, cov)
    ax.scatter(vol * 100, ret * 100, s=90, marker="*", label="Max historical Sharpe")
    ax.set_xlabel("Annualised volatility (%)")
    ax.set_ylabel("Annualised arithmetic expected return (%)")
    ax.set_title("Historical mean-variance efficient frontier")
    ax.grid(True, alpha=0.25)
    ax.legend(fontsize=8)
    fig.tight_layout()
    fig.savefig(OUT / "efficient_frontier.png", dpi=180)
    plt.close(fig)

    print("\nCommon monthly observation range:", prices.index.min().date(), "to", prices.index.max().date())
    print("Monthly return observations:", len(returns))
    print("\nPortfolios (All-World / Momentum / Value):")
    for label, w in weights_map.items():
        print(f"  {label}: {w[0]:.0%} / {w[1]:.0%} / {w[2]:.0%}")
    print("\nSummary statistics (historical, not forecast):")
    print(summary.to_string(index=False, float_format=lambda x: f"{x:.4f}"))
    print("\nMax historical Sharpe weights (risk-free rate assumed 0):")
    for name, weight in zip(names, opt_weights):
        print(f"  {name}: {weight:.1%}")
    print(f"  Annualised arithmetic return: {opt_ret:.2%}")
    print(f"  Annualised volatility: {opt_vol:.2%}")
    print(f"\nFiles saved in: {OUT}")


if __name__ == "__main__":
    main()