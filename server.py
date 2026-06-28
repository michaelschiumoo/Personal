"""Robinhood Trading MCP Server"""

import os
import robin_stocks.robinhood as rh
from mcp.server.fastmcp import FastMCP

mcp = FastMCP("robinhood-trading")

_logged_in = False


def _ensure_login():
    global _logged_in
    if not _logged_in:
        username = os.environ.get("ROBINHOOD_USERNAME")
        password = os.environ.get("ROBINHOOD_PASSWORD")
        mfa_code = os.environ.get("ROBINHOOD_MFA_CODE")
        if not username or not password:
            raise RuntimeError(
                "Set ROBINHOOD_USERNAME and ROBINHOOD_PASSWORD environment variables."
            )
        rh.login(username, password, mfa_code=mfa_code, store_session=True)
        _logged_in = True


# ── Account ──────────────────────────────────────────────────────────────────

@mcp.tool()
def get_account_info() -> dict:
    """Return basic Robinhood account details (buying power, portfolio value, etc.)."""
    _ensure_login()
    profile = rh.profiles.load_account_profile()
    portfolio = rh.profiles.load_portfolio_profile()
    return {"account": profile, "portfolio": portfolio}


@mcp.tool()
def get_positions() -> list:
    """Return all current stock positions with quantity and average cost."""
    _ensure_login()
    return rh.account.get_open_stock_positions(info=None)


@mcp.tool()
def get_holdings() -> dict:
    """Return holdings with current market value and equity."""
    _ensure_login()
    return rh.account.build_holdings()


# ── Market Data ───────────────────────────────────────────────────────────────

@mcp.tool()
def get_quote(symbol: str) -> dict:
    """Get the latest quote for a stock symbol (e.g. AAPL)."""
    _ensure_login()
    return rh.stocks.get_quotes(symbol.upper())[0]


@mcp.tool()
def get_quotes(symbols: list[str]) -> list:
    """Get latest quotes for multiple stock symbols."""
    _ensure_login()
    return rh.stocks.get_quotes([s.upper() for s in symbols])


@mcp.tool()
def get_fundamentals(symbol: str) -> dict:
    """Get fundamental data (P/E, market cap, 52-week high/low) for a stock."""
    _ensure_login()
    result = rh.stocks.get_fundamentals(symbol.upper())
    return result[0] if result else {}


@mcp.tool()
def search_stocks(query: str) -> list:
    """Search for stocks by company name or ticker symbol."""
    _ensure_login()
    return rh.stocks.find_instrument_data(query)


@mcp.tool()
def get_historical_prices(symbol: str, interval: str = "day", span: str = "3month") -> list:
    """
    Get historical price data for a stock.

    interval: '5minute' | '10minute' | 'hour' | 'day' | 'week'
    span:     'day' | 'week' | 'month' | '3month' | 'year' | '5year'
    """
    _ensure_login()
    return rh.stocks.get_stock_historicals(symbol.upper(), interval=interval, span=span)


# ── Orders ────────────────────────────────────────────────────────────────────

@mcp.tool()
def get_open_orders() -> list:
    """Return all open (unfilled) orders."""
    _ensure_login()
    return rh.orders.get_all_open_stock_orders()


@mcp.tool()
def get_order_history(count: int = 20) -> list:
    """Return recent order history (default last 20 orders)."""
    _ensure_login()
    orders = rh.orders.get_all_stock_orders()
    return orders[:count] if orders else []


@mcp.tool()
def cancel_order(order_id: str) -> dict:
    """Cancel an open order by its order ID."""
    _ensure_login()
    return rh.orders.cancel_stock_order(order_id)


@mcp.tool()
def place_market_buy(symbol: str, quantity: float) -> dict:
    """
    Place a market buy order.

    symbol:   Stock ticker (e.g. 'AAPL')
    quantity: Number of shares (fractional allowed)
    """
    _ensure_login()
    return rh.orders.order_buy_market(symbol.upper(), quantity)


@mcp.tool()
def place_market_sell(symbol: str, quantity: float) -> dict:
    """
    Place a market sell order.

    symbol:   Stock ticker (e.g. 'AAPL')
    quantity: Number of shares (fractional allowed)
    """
    _ensure_login()
    return rh.orders.order_sell_market(symbol.upper(), quantity)


@mcp.tool()
def place_limit_buy(symbol: str, quantity: float, limit_price: float) -> dict:
    """
    Place a limit buy order.

    symbol:      Stock ticker
    quantity:    Number of shares
    limit_price: Maximum price per share to pay
    """
    _ensure_login()
    return rh.orders.order_buy_limit(symbol.upper(), quantity, limit_price)


@mcp.tool()
def place_limit_sell(symbol: str, quantity: float, limit_price: float) -> dict:
    """
    Place a limit sell order.

    symbol:      Stock ticker
    quantity:    Number of shares
    limit_price: Minimum price per share to accept
    """
    _ensure_login()
    return rh.orders.order_sell_limit(symbol.upper(), quantity, limit_price)


@mcp.tool()
def place_stop_loss(symbol: str, quantity: float, stop_price: float) -> dict:
    """
    Place a stop-loss sell order.

    symbol:     Stock ticker
    quantity:   Number of shares
    stop_price: Price at which the order triggers
    """
    _ensure_login()
    return rh.orders.order_sell_stop_loss(symbol.upper(), quantity, stop_price)


# ── Watchlists ────────────────────────────────────────────────────────────────

@mcp.tool()
def get_watchlists() -> list:
    """Return all watchlists and the stocks in them."""
    _ensure_login()
    return rh.account.get_all_watchlists()


@mcp.tool()
def add_to_watchlist(symbol: str, watchlist_name: str = "Default") -> dict:
    """Add a stock to a watchlist."""
    _ensure_login()
    return rh.account.post_symbols_to_watchlist(symbol.upper(), name=watchlist_name)


# ── Options (read-only) ───────────────────────────────────────────────────────

@mcp.tool()
def get_options_positions() -> list:
    """Return all open options positions."""
    _ensure_login()
    return rh.options.get_open_option_positions()


@mcp.tool()
def get_options_chain(symbol: str, expiration_date: str | None = None) -> list:
    """
    Get the options chain for a stock.

    symbol:          Stock ticker
    expiration_date: 'YYYY-MM-DD' (optional; returns all dates if omitted)
    """
    _ensure_login()
    return rh.options.get_options_for_stock(symbol.upper(), expirationDate=expiration_date)


if __name__ == "__main__":
    mcp.run()
