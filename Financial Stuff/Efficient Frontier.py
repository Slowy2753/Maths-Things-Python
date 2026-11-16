
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
SHORT_NAMES = ["All-World", "Momentum", "Value"]

# Fixed-weight portfolios, weights in the same order as TICKERS.
# Labels are generated automatically from the weights.
PORTFOLIO_WEIGHTS = [
    [1.00, 0.00, 0.00],
    [0.60, 0.20, 0.20],
    [0.60, 0.30, 0.10],
    [0.70, 0.20, 0.10],
]

START = "2014-10-01"
INITIAL_INVESTMENT = 1000.0
OUT = Path(__file__).resolve().parent


def portfolio_label(w):
    """Readable label built from the weights, e.g. '70/20/10 (All-World/Momentum/Value)'."""
    nonzero = [i for i, x in enumerate(w) if x > 0]
    if len(nonzero) == 1:
        return f"100% {SHORT_NAMES[nonzero[0]]}"
    split = "/".join(f"{x * 100:.0f}" for x in w)
    return f"{split} ({'/'.join(SHORT_NAMES)})"


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


def portfolio_cagr(w, R):
    """CAGR of a monthly-rebalanced fixed-weight portfolio.
    R is an (n_months x n_assets) array of monthly simple returns."""
    monthly = R @ w
    return float(np.exp(np.log1p(monthly).sum() * 12 / len(monthly)) - 1)


def portfolio_vol(w, cov):
    """Annualised volatility from the monthly covariance matrix."""
    return float(np.sqrt(w @ cov @ w * 12))


def portfolio_stats(w, R, cov):
    return portfolio_cagr(w, R), portfolio_vol(w, cov)


def optimize_frontier(R, cov, points=120):
    """Long-only efficient frontier in CAGR / volatility space.

    Runs from the minimum-variance portfolio up to the maximum-CAGR portfolio,
    so only the efficient (upward-sloping) part is drawn."""
    n = R.shape[1]
    bounds = [(0.0, 1.0)] * n
    sum_to_one = {"type": "eq", "fun": lambda w: np.sum(w) - 1.0}
    x0 = np.full(n, 1 / n)

    min_var = minimize(
        lambda w: w @ cov @ w * 12, x0, method="SLSQP",
        bounds=bounds, constraints=[sum_to_one],
        options={"maxiter": 2000, "ftol": 1e-12},
    )
    max_cagr = minimize(
        lambda w: -portfolio_cagr(w, R), x0, method="SLSQP",
        bounds=bounds, constraints=[sum_to_one],
        options={"maxiter": 2000, "ftol": 1e-12},
    )
    low = portfolio_cagr(min_var.x, R)
    high = portfolio_cagr(max_cagr.x, R)

    rows = []
    for target in np.linspace(low, high, points):
        constraints = [
            sum_to_one,
            {"type": "ineq", "fun": lambda w, t=target: portfolio_cagr(w, R) - t},
        ]
        result = minimize(
            lambda w: w @ cov @ w * 12, x0, method="SLSQP",
            bounds=bounds, constraints=constraints,
            options={"maxiter": 2000, "ftol": 1e-12},
        )
        if result.success:
            cagr, vol = portfolio_stats(result.x, R, cov)
            rows.append({
                "cagr": cagr,
                "annual_volatility": vol,
                **{f"weight_{SHORT_NAMES[i]}": float(result.x[i]) for i in range(n)},
            })
    return pd.DataFrame(rows)


def summarise(name, r):
    growth = (1 + r).cumprod()
    cagr = float((1 + r).prod() ** (12 / len(r)) - 1)
    vol = float(r.std(ddof=1) * np.sqrt(12))
    return {
        "portfolio": name,
        "cumulative_return": float(growth.iloc[-1] - 1),
        "cagr": cagr,
        "annualised_volatility": vol,
        "cagr_over_volatility": cagr / vol if vol > 0 else np.nan,
        "max_drawdown": float((growth / growth.cummax() - 1).min()),
    }


def main():
    prices = download_adjusted_monthly(TICKERS, START)
    returns = prices.pct_change().dropna()
    names = list(returns.columns)
    if len(names) != 3:
        raise RuntimeError("Expected three ETF series.")
    R = returns.to_numpy()
    cov = returns.cov().to_numpy()

    period = f"{returns.index.min():%b %Y} to {returns.index.max():%b %Y}"

    # Monthly-rebalanced return series for each fixed-weight portfolio.
    weights_map = {}
    for w in PORTFOLIO_WEIGHTS:
        w = np.array(w, dtype=float)
        if len(w) != 3 or not np.isclose(w.sum(), 1.0):
            raise ValueError(f"Weights must have 3 entries summing to 1: {w}")
        weights_map[portfolio_label(w)] = w
    portfolio_returns = pd.DataFrame(
        {label: R @ w for label, w in weights_map.items()},
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

    # Summary statistics: individual funds, then blends (all CAGR-based).
    summary_rows = [summarise(name, returns[name]) for name in names]
    summary_rows += [summarise(label, portfolio_returns[label]) for label in portfolio_returns.columns]
    summary = pd.DataFrame(summary_rows)

    # Frontier (CAGR vs volatility) and best CAGR/volatility portfolio (rf = 0).
    frontier = optimize_frontier(R, cov)

    def neg_ratio(w):
        cagr, vol = portfolio_stats(w, R, cov)
        return -(cagr / vol) if vol > 0 else 1e6

    opt = minimize(
        neg_ratio, np.full(3, 1 / 3), method="SLSQP",
        bounds=[(0.0, 1.0)] * 3,
        constraints=[{"type": "eq", "fun": lambda w: np.sum(w) - 1}],
        options={"maxiter": 2000, "ftol": 1e-12},
    )
    opt_weights = opt.x if opt.success else np.full(3, np.nan)
    opt_cagr, opt_vol = portfolio_stats(opt_weights, R, cov)

    # CSV outputs.
    prices.to_csv(OUT / "monthly_adjusted_prices.csv")
    returns.to_csv(OUT / "monthly_returns.csv")
    portfolio_returns.to_csv(OUT / "portfolio_monthly_returns.csv")
    start_date_values.to_csv(OUT / "lump_sum_value_by_start_date.csv")
    frontier.to_csv(OUT / "efficient_frontier.csv", index=False)
    summary.to_csv(OUT / "summary_statistics.csv", index=False)
    pd.DataFrame({"asset": names, "weight": opt_weights}).to_csv(OUT / "best_cagr_over_vol_weights.csv", index=False)

    # Chart 1: value today by investment start date.
    fig, ax = plt.subplots(figsize=(11, 6.5))
    for label in start_date_values.columns:
        ax.plot(start_date_values.index, start_date_values[label], label=label, linewidth=2)
    ax.set_yscale("log")
    ax.set_xlabel("Investment start date")
    ax.set_ylabel("Value today (£), log scale")
    ax.set_title(
        f"Value today of £{INITIAL_INVESTMENT:,.0f} invested at each month-end\n"
        f"({period}, monthly rebalanced)"
    )
    ax.grid(True, which="both", alpha=0.25)
    ax.legend(fontsize=9)
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
    ax.set_title(
        f"Growth of £{INITIAL_INVESTMENT:,.0f}, common period\n"
        f"({period}, monthly rebalanced)"
    )
    ax.grid(True, which="both", alpha=0.25)
    ax.legend(fontsize=9)
    fig.tight_layout()
    fig.savefig(OUT / "portfolio_growth_comparison.png", dpi=180)
    plt.close(fig)

    # Chart 3: efficient frontier (CAGR vs volatility).
    fig, ax = plt.subplots(figsize=(10.5, 7))
    if not frontier.empty:
        ax.plot(frontier["annual_volatility"] * 100, frontier["cagr"] * 100,
                label="Long-only efficient frontier", linewidth=2)
    for i, name in enumerate(names):
        cagr, vol = portfolio_stats(np.eye(3)[i], R, cov)
        ax.scatter(vol * 100, cagr * 100, s=55, label=name)
    for label, w in weights_map.items():
        cagr, vol = portfolio_stats(w, R, cov)
        ax.scatter(vol * 100, cagr * 100, s=75, marker="D", label=label)
    ax.scatter(opt_vol * 100, opt_cagr * 100, s=90, marker="*", label="Best CAGR/volatility")
    ax.set_xlabel("Annualised volatility (%)")
    ax.set_ylabel("CAGR (%)")
    ax.set_title(f"Historical efficient frontier: CAGR vs volatility\n({period}, monthly data)")
    ax.grid(True, alpha=0.25)
    ax.legend(fontsize=8)
    fig.tight_layout()
    fig.savefig(OUT / "efficient_frontier.png", dpi=180)
    plt.close(fig)

    print("\nCommon monthly observation range:", prices.index.min().date(), "to", prices.index.max().date())
    print("Monthly return observations:", len(returns))
    print("\nPortfolios:")
    for label in weights_map:
        print(f"  {label}")
    print("\nSummary statistics (historical, CAGR-based, not forecast):")
    print(summary.to_string(index=False, float_format=lambda x: f"{x:.4f}"))
    print("\nBest CAGR/volatility weights (risk-free rate assumed 0):")
    for name, weight in zip(names, opt_weights):
        print(f"  {name}: {weight:.1%}")
    print(f"  CAGR: {opt_cagr:.2%}")
    print(f"  Annualised volatility: {opt_vol:.2%}")
    print(f"\nFiles saved in: {OUT}")


if __name__ == "__main__":
    main()