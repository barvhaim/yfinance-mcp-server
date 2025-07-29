#!/usr/bin/env python3

import asyncio
import logging
import os
from datetime import datetime, timedelta
from typing import Any, Dict, List, Optional, Union

import pandas as pd
import yfinance as yf
from fastmcp import FastMCP
from pydantic import BaseModel, Field

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Initialize FastMCP server
mcp = FastMCP("YFinance MCP Server")


class StockInfo(BaseModel):
    """Stock information model"""

    symbol: str
    name: str = ""
    current_price: float = 0.0
    market_cap: Optional[int] = None
    pe_ratio: Optional[float] = None
    dividend_yield: Optional[float] = None


class HistoricalDataRequest(BaseModel):
    """Request model for historical data"""

    symbol: str
    period: str = Field(
        default="1mo", description="Period: 1d,5d,1mo,3mo,6mo,1y,2y,5y,10y,ytd,max"
    )
    interval: str = Field(
        default="1d",
        description="Interval: 1m,2m,5m,15m,30m,60m,90m,1h,1d,5d,1wk,1mo,3mo",
    )


@mcp.tool()
async def get_stock_info(symbol: str) -> Dict[str, Any]:
    """
    Get basic stock information including current price, market cap, and key metrics.

    Args:
        symbol: Stock ticker symbol (e.g., 'AAPL', 'GOOGL')

    Returns:
        Dictionary containing stock information
    """
    try:
        ticker = yf.Ticker(symbol.upper())
        info = ticker.info

        return {
            "symbol": symbol.upper(),
            "name": info.get("longName", ""),
            "current_price": info.get("currentPrice", 0.0),
            "market_cap": info.get("marketCap"),
            "pe_ratio": info.get("forwardPE"),
            "dividend_yield": info.get("dividendYield"),
            "52_week_high": info.get("fiftyTwoWeekHigh"),
            "52_week_low": info.get("fiftyTwoWeekLow"),
            "volume": info.get("volume"),
            "avg_volume": info.get("averageVolume"),
            "beta": info.get("beta"),
            "earnings_per_share": info.get("trailingEps"),
            "price_to_book": info.get("priceToBook"),
            "debt_to_equity": info.get("debtToEquity"),
            "return_on_equity": info.get("returnOnEquity"),
            "sector": info.get("sector"),
            "industry": info.get("industry"),
            "country": info.get("country"),
            "website": info.get("website"),
            "business_summary": (
                info.get("businessSummary", "")[:500] + "..."
                if info.get("businessSummary", "")
                else ""
            ),
        }
    except Exception as e:
        logger.error(f"Error getting stock info for {symbol}: {str(e)}")
        return {"error": f"Failed to get stock info for {symbol}: {str(e)}"}


@mcp.tool()
async def get_historical_data(
    symbol: str, period: str = "1mo", interval: str = "1d"
) -> Dict[str, Any]:
    """
    Get historical stock price data.

    Args:
        symbol: Stock ticker symbol (e.g., 'AAPL', 'GOOGL')
        period: Time period (1d,5d,1mo,3mo,6mo,1y,2y,5y,10y,ytd,max)
        interval: Data interval (1m,2m,5m,15m,30m,60m,90m,1h,1d,5d,1wk,1mo,3mo)

    Returns:
        Dictionary containing historical price data
    """
    try:
        ticker = yf.Ticker(symbol.upper())
        hist = ticker.history(period=period, interval=interval)

        if hist.empty:
            return {"error": f"No data found for symbol {symbol}"}

        # Convert DataFrame to dictionary format
        data = []
        for date, row in hist.iterrows():
            data.append(
                {
                    "date": date.strftime("%Y-%m-%d"),
                    "open": float(row["Open"]),
                    "high": float(row["High"]),
                    "low": float(row["Low"]),
                    "close": float(row["Close"]),
                    "volume": int(row["Volume"]) if "Volume" in row else 0,
                }
            )

        return {
            "symbol": symbol.upper(),
            "period": period,
            "interval": interval,
            "data": data,
            "count": len(data),
        }
    except Exception as e:
        logger.error(f"Error getting historical data for {symbol}: {str(e)}")
        return {"error": f"Failed to get historical data for {symbol}: {str(e)}"}


@mcp.tool()
async def get_dividends(symbol: str) -> Dict[str, Any]:
    """
    Get dividend history for a stock.

    Args:
        symbol: Stock ticker symbol (e.g., 'AAPL', 'GOOGL')

    Returns:
        Dictionary containing dividend history
    """
    try:
        ticker = yf.Ticker(symbol.upper())
        dividends = ticker.dividends

        if dividends.empty:
            return {
                "symbol": symbol.upper(),
                "dividends": [],
                "message": "No dividend data available",
            }

        dividend_data = []
        for date, dividend in dividends.items():
            dividend_data.append(
                {"date": date.strftime("%Y-%m-%d"), "dividend": float(dividend)}
            )

        return {
            "symbol": symbol.upper(),
            "dividends": dividend_data,
            "count": len(dividend_data),
        }
    except Exception as e:
        logger.error(f"Error getting dividends for {symbol}: {str(e)}")
        return {"error": f"Failed to get dividends for {symbol}: {str(e)}"}


@mcp.tool()
async def get_splits(symbol: str) -> Dict[str, Any]:
    """
    Get stock split history for a stock.

    Args:
        symbol: Stock ticker symbol (e.g., 'AAPL', 'GOOGL')

    Returns:
        Dictionary containing split history
    """
    try:
        ticker = yf.Ticker(symbol.upper())
        splits = ticker.splits

        if splits.empty:
            return {
                "symbol": symbol.upper(),
                "splits": [],
                "message": "No split data available",
            }

        split_data = []
        for date, split in splits.items():
            split_data.append(
                {"date": date.strftime("%Y-%m-%d"), "split_ratio": float(split)}
            )

        return {
            "symbol": symbol.upper(),
            "splits": split_data,
            "count": len(split_data),
        }
    except Exception as e:
        logger.error(f"Error getting splits for {symbol}: {str(e)}")
        return {"error": f"Failed to get splits for {symbol}: {str(e)}"}


@mcp.tool()
async def get_financials(symbol: str, quarterly: bool = False) -> Dict[str, Any]:
    """
    Get financial statements for a stock.

    Args:
        symbol: Stock ticker symbol (e.g., 'AAPL', 'GOOGL')
        quarterly: If True, get quarterly data; if False, get annual data

    Returns:
        Dictionary containing financial statements
    """
    try:
        ticker = yf.Ticker(symbol.upper())

        if quarterly:
            income_stmt = ticker.quarterly_income_stmt
            balance_sheet = ticker.quarterly_balance_sheet
            cash_flow = ticker.quarterly_cashflow
        else:
            income_stmt = ticker.income_stmt
            balance_sheet = ticker.balance_sheet
            cash_flow = ticker.cashflow

        result = {
            "symbol": symbol.upper(),
            "quarterly": quarterly,
            "income_statement": {},
            "balance_sheet": {},
            "cash_flow": {},
        }

        # Convert financial data to dictionary format
        if not income_stmt.empty:
            result["income_statement"] = income_stmt.to_dict()

        if not balance_sheet.empty:
            result["balance_sheet"] = balance_sheet.to_dict()

        if not cash_flow.empty:
            result["cash_flow"] = cash_flow.to_dict()

        return result
    except Exception as e:
        logger.error(f"Error getting financials for {symbol}: {str(e)}")
        return {"error": f"Failed to get financials for {symbol}: {str(e)}"}


@mcp.tool()
async def get_earnings(symbol: str) -> Dict[str, Any]:
    """
    Get earnings data for a stock.
    Note: Uses income statement data as 'earnings' property is deprecated.

    Args:
        symbol: Stock ticker symbol (e.g., 'AAPL', 'GOOGL')

    Returns:
        Dictionary containing earnings data extracted from financial statements
    """
    try:
        ticker = yf.Ticker(symbol.upper())

        # Get income statement data since earnings property is deprecated
        annual_income = ticker.income_stmt
        quarterly_income = ticker.quarterly_income_stmt

        result = {
            "symbol": symbol.upper(),
            "annual_earnings": {},
            "quarterly_earnings": {},
            "note": "Earnings data extracted from income statements (Net Income)",
        }

        # Extract Net Income from annual income statement
        if annual_income is not None and not annual_income.empty:
            # Look for Net Income row
            net_income_rows = annual_income[
                annual_income.index.str.contains("Net Income", case=False, na=False)
            ]
            if not net_income_rows.empty:
                # Convert to dictionary with dates as keys
                net_income_data = net_income_rows.iloc[0].to_dict()
                # Convert timestamps to strings for JSON serialization
                annual_earnings = {}
                for date, value in net_income_data.items():
                    date_str = (
                        date.strftime("%Y-%m-%d")
                        if hasattr(date, "strftime")
                        else str(date)
                    )
                    annual_earnings[date_str] = (
                        float(value)
                        if value is not None and not pd.isna(value)
                        else None
                    )
                result["annual_earnings"] = annual_earnings

        # Extract Net Income from quarterly income statement
        if quarterly_income is not None and not quarterly_income.empty:
            net_income_rows = quarterly_income[
                quarterly_income.index.str.contains("Net Income", case=False, na=False)
            ]
            if not net_income_rows.empty:
                net_income_data = net_income_rows.iloc[0].to_dict()
                quarterly_earnings = {}
                for date, value in net_income_data.items():
                    date_str = (
                        date.strftime("%Y-%m-%d")
                        if hasattr(date, "strftime")
                        else str(date)
                    )
                    quarterly_earnings[date_str] = (
                        float(value)
                        if value is not None and not pd.isna(value)
                        else None
                    )
                result["quarterly_earnings"] = quarterly_earnings

        return result
    except Exception as e:
        logger.error(f"Error getting earnings for {symbol}: {str(e)}")
        return {"error": f"Failed to get earnings for {symbol}: {str(e)}"}


@mcp.tool()
async def get_news(symbol: str, count: int = 10) -> Dict[str, Any]:
    """
    Get recent news for a stock.

    Args:
        symbol: Stock ticker symbol (e.g., 'AAPL', 'GOOGL')
        count: Number of news articles to return (default: 10)

    Returns:
        Dictionary containing news articles
    """
    try:
        ticker = yf.Ticker(symbol.upper())
        news = ticker.news

        if not news:
            return {
                "symbol": symbol.upper(),
                "news": [],
                "message": "No news available",
            }

        # Limit the number of articles
        news = news[:count]

        news_data = []
        for article in news:
            content = article.get("content", {})
            thumbnail_url = ""
            if content.get("thumbnail") and content["thumbnail"].get("resolutions"):
                thumbnail_url = content["thumbnail"]["resolutions"][0].get("url", "")

            # Convert pubDate to timestamp if available
            pub_time = 0
            if content.get("pubDate"):
                try:
                    from datetime import datetime

                    pub_time = int(
                        datetime.fromisoformat(
                            content["pubDate"].replace("Z", "+00:00")
                        ).timestamp()
                    )
                except:
                    pub_time = 0

            news_data.append(
                {
                    "title": content.get("title", ""),
                    "link": content.get("canonicalUrl", {}).get("url", ""),
                    "publisher": content.get("provider", {}).get("displayName", ""),
                    "providerPublishTime": pub_time,
                    "type": content.get("contentType", ""),
                    "thumbnail": thumbnail_url,
                    "summary": content.get("summary", ""),
                }
            )

        return {"symbol": symbol.upper(), "news": news_data, "count": len(news_data)}
    except Exception as e:
        logger.error(f"Error getting news for {symbol}: {str(e)}")
        return {"error": f"Failed to get news for {symbol}: {str(e)}"}


@mcp.tool()
async def get_recommendations(symbol: str) -> Dict[str, Any]:
    """
    Get analyst recommendations for a stock.

    Args:
        symbol: Stock ticker symbol (e.g., 'AAPL', 'GOOGL')

    Returns:
        Dictionary containing analyst recommendations
    """
    try:
        ticker = yf.Ticker(symbol.upper())
        recommendations = ticker.recommendations

        if recommendations is None or recommendations.empty:
            return {
                "symbol": symbol.upper(),
                "recommendations": [],
                "message": "No recommendations available",
            }

        # Convert to dictionary format - new structure has recommendation counts by period
        rec_data = []
        for index, row in recommendations.iterrows():
            period = row.get("period", "")
            total_recommendations = (
                row.get("strongBuy", 0)
                + row.get("buy", 0)
                + row.get("hold", 0)
                + row.get("sell", 0)
                + row.get("strongSell", 0)
            )

            rec_data.append(
                {
                    "period": period,
                    "strong_buy": int(row.get("strongBuy", 0)),
                    "buy": int(row.get("buy", 0)),
                    "hold": int(row.get("hold", 0)),
                    "sell": int(row.get("sell", 0)),
                    "strong_sell": int(row.get("strongSell", 0)),
                    "total": total_recommendations,
                }
            )

        return {
            "symbol": symbol.upper(),
            "recommendations": rec_data,
            "count": len(rec_data),
            "note": "Recommendations show analyst count by rating for different time periods",
        }
    except Exception as e:
        logger.error(f"Error getting recommendations for {symbol}: {str(e)}")
        return {"error": f"Failed to get recommendations for {symbol}: {str(e)}"}


@mcp.tool()
async def search_stocks(query: str, limit: int = 10) -> Dict[str, Any]:
    """
    Search for stocks by company name or ticker symbol.

    This tool searches Yahoo Finance's database for stocks matching your query.
    Works best with specific company names or partial ticker symbols.

    Examples of effective queries:
    - "Microsoft" (company name)
    - "AAPL" (ticker symbol)
    - "Tesla" (company name)
    - "JPM" (partial ticker)

    Note: Complex multi-word queries may return fewer results. For best results,
    search for one company at a time.

    Args:
        query: Search query - company name or ticker symbol (e.g., 'Microsoft', 'AAPL')
        limit: Maximum number of results to return (default: 10, max recommended: 25)

    Returns:
        Dictionary containing search results with symbol, name, type, exchange,
        sector, industry, relevance score, and other metadata
    """
    try:
        # Use yfinance Search class (updated API)
        search_obj = yf.Search(query, max_results=limit)
        search_results = search_obj.quotes

        if not search_results:
            return {"query": query, "results": [], "message": "No results found"}

        results = []
        for result in search_results[:limit]:  # Ensure we don't exceed limit
            results.append(
                {
                    "symbol": result.get("symbol", ""),
                    "name": result.get("longname", result.get("shortname", "")),
                    "type": result.get("quoteType", ""),
                    "exchange": result.get("exchange", ""),
                    "sector": result.get("sector", ""),
                    "industry": result.get("industry", ""),
                    "score": result.get("score", 0),
                    "is_yahoo_finance": result.get("isYahooFinance", False),
                }
            )

        return {"query": query, "results": results, "count": len(results)}
    except Exception as e:
        logger.error(f"Error searching stocks for query '{query}': {str(e)}")
        return {"error": f"Failed to search stocks for query '{query}': {str(e)}"}


@mcp.tool()
async def get_multiple_quotes(symbols: List[str]) -> Dict[str, Any]:
    """
    Get current quotes for multiple stocks at once.

    Args:
        symbols: List of stock ticker symbols (e.g., ['AAPL', 'GOOGL', 'MSFT'])

    Returns:
        Dictionary containing quotes for all requested symbols
    """
    try:
        # Convert to uppercase
        symbols = [symbol.upper() for symbol in symbols]

        # Use yfinance to get multiple tickers
        tickers = yf.Tickers(" ".join(symbols))

        results = {}
        for symbol in symbols:
            try:
                ticker = tickers.tickers[symbol]
                info = ticker.info

                results[symbol] = {
                    "symbol": symbol,
                    "name": info.get("longName", ""),
                    "current_price": info.get("currentPrice", 0.0),
                    "previous_close": info.get("previousClose", 0.0),
                    "change": info.get("currentPrice", 0.0)
                    - info.get("previousClose", 0.0),
                    "change_percent": (
                        (info.get("currentPrice", 0.0) - info.get("previousClose", 0.0))
                        / info.get("previousClose", 1.0)
                    )
                    * 100,
                    "volume": info.get("volume", 0),
                    "market_cap": info.get("marketCap"),
                    "pe_ratio": info.get("forwardPE"),
                }
            except Exception as e:
                results[symbol] = {
                    "error": f"Failed to get data for {symbol}: {str(e)}"
                }

        return {"symbols": symbols, "quotes": results, "count": len(symbols)}
    except Exception as e:
        logger.error(f"Error getting multiple quotes: {str(e)}")
        return {"error": f"Failed to get multiple quotes: {str(e)}"}


if __name__ == "__main__":
    # Run the FastMCP server

    mcp.run()
