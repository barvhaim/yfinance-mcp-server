#!/usr/bin/env python3

import asyncio
import logging
import os
from datetime import datetime, timedelta
from typing import Any, Dict, List, Optional, Union

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
    period: str = Field(default="1mo", description="Period: 1d,5d,1mo,3mo,6mo,1y,2y,5y,10y,ytd,max")
    interval: str = Field(default="1d", description="Interval: 1m,2m,5m,15m,30m,60m,90m,1h,1d,5d,1wk,1mo,3mo")

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
            "business_summary": info.get("businessSummary", "")[:500] + "..." if info.get("businessSummary", "") else ""
        }
    except Exception as e:
        logger.error(f"Error getting stock info for {symbol}: {str(e)}")
        return {"error": f"Failed to get stock info for {symbol}: {str(e)}"}

@mcp.tool()
async def get_historical_data(
    symbol: str,
    period: str = "1mo",
    interval: str = "1d"
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
            data.append({
                "date": date.strftime("%Y-%m-%d"),
                "open": float(row["Open"]),
                "high": float(row["High"]),
                "low": float(row["Low"]),
                "close": float(row["Close"]),
                "volume": int(row["Volume"]) if "Volume" in row else 0
            })
        
        return {
            "symbol": symbol.upper(),
            "period": period,
            "interval": interval,
            "data": data,
            "count": len(data)
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
            return {"symbol": symbol.upper(), "dividends": [], "message": "No dividend data available"}
        
        dividend_data = []
        for date, dividend in dividends.items():
            dividend_data.append({
                "date": date.strftime("%Y-%m-%d"),
                "dividend": float(dividend)
            })
        
        return {
            "symbol": symbol.upper(),
            "dividends": dividend_data,
            "count": len(dividend_data)
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
            return {"symbol": symbol.upper(), "splits": [], "message": "No split data available"}
        
        split_data = []
        for date, split in splits.items():
            split_data.append({
                "date": date.strftime("%Y-%m-%d"),
                "split_ratio": float(split)
            })
        
        return {
            "symbol": symbol.upper(),
            "splits": split_data,
            "count": len(split_data)
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
            "cash_flow": {}
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
    
    Args:
        symbol: Stock ticker symbol (e.g., 'AAPL', 'GOOGL')
    
    Returns:
        Dictionary containing earnings data
    """
    try:
        ticker = yf.Ticker(symbol.upper())
        earnings = ticker.earnings
        quarterly_earnings = ticker.quarterly_earnings
        
        result = {
            "symbol": symbol.upper(),
            "annual_earnings": {},
            "quarterly_earnings": {}
        }
        
        if not earnings.empty:
            result["annual_earnings"] = earnings.to_dict()
        
        if not quarterly_earnings.empty:
            result["quarterly_earnings"] = quarterly_earnings.to_dict()
        
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
            return {"symbol": symbol.upper(), "news": [], "message": "No news available"}
        
        # Limit the number of articles
        news = news[:count]
        
        news_data = []
        for article in news:
            news_data.append({
                "title": article.get("title", ""),
                "link": article.get("link", ""),
                "publisher": article.get("publisher", ""),
                "providerPublishTime": article.get("providerPublishTime", 0),
                "type": article.get("type", ""),
                "thumbnail": article.get("thumbnail", {}).get("resolutions", [{}])[0].get("url", "") if article.get("thumbnail") else ""
            })
        
        return {
            "symbol": symbol.upper(),
            "news": news_data,
            "count": len(news_data)
        }
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
            return {"symbol": symbol.upper(), "recommendations": [], "message": "No recommendations available"}
        
        # Convert to dictionary format
        rec_data = []
        for date, row in recommendations.iterrows():
            rec_data.append({
                "date": date.strftime("%Y-%m-%d"),
                "firm": row.get("Firm", ""),
                "to_grade": row.get("To Grade", ""),
                "from_grade": row.get("From Grade", ""),
                "action": row.get("Action", "")
            })
        
        return {
            "symbol": symbol.upper(),
            "recommendations": rec_data,
            "count": len(rec_data)
        }
    except Exception as e:
        logger.error(f"Error getting recommendations for {symbol}: {str(e)}")
        return {"error": f"Failed to get recommendations for {symbol}: {str(e)}"}

@mcp.tool()
async def search_stocks(query: str, limit: int = 10) -> Dict[str, Any]:
    """
    Search for stocks by name or symbol.
    
    Args:
        query: Search query (company name or ticker symbol)
        limit: Maximum number of results to return (default: 10)
    
    Returns:
        Dictionary containing search results
    """
    try:
        # Use yfinance search functionality
        search_results = yf.search(query, limit=limit)
        
        if not search_results:
            return {"query": query, "results": [], "message": "No results found"}
        
        results = []
        for result in search_results:
            results.append({
                "symbol": result.get("symbol", ""),
                "name": result.get("longname", ""),
                "type": result.get("type", ""),
                "exchange": result.get("exchange", ""),
                "market": result.get("market", "")
            })
        
        return {
            "query": query,
            "results": results,
            "count": len(results)
        }
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
        tickers = yf.Tickers(' '.join(symbols))
        
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
                    "change": info.get("currentPrice", 0.0) - info.get("previousClose", 0.0),
                    "change_percent": ((info.get("currentPrice", 0.0) - info.get("previousClose", 0.0)) / info.get("previousClose", 1.0)) * 100,
                    "volume": info.get("volume", 0),
                    "market_cap": info.get("marketCap"),
                    "pe_ratio": info.get("forwardPE")
                }
            except Exception as e:
                results[symbol] = {"error": f"Failed to get data for {symbol}: {str(e)}"}
        
        return {
            "symbols": symbols,
            "quotes": results,
            "count": len(symbols)
        }
    except Exception as e:
        logger.error(f"Error getting multiple quotes: {str(e)}")
        return {"error": f"Failed to get multiple quotes: {str(e)}"}

if __name__ == "__main__":
    # Run the FastMCP server
    mcp.run()
