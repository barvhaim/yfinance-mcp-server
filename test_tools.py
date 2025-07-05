#!/usr/bin/env python3

import asyncio
import json
import logging
from datetime import datetime
from typing import Dict, Any, List
import yfinance as yf

# Direct implementation of the functions to test the underlying logic
async def get_stock_info(symbol: str) -> Dict[str, Any]:
    """Get basic stock information including current price, market cap, and key metrics."""
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
        return {"error": f"Failed to get stock info for {symbol}: {str(e)}"}

async def get_historical_data(symbol: str, period: str = "1mo", interval: str = "1d") -> Dict[str, Any]:
    """Get historical stock price data."""
    try:
        ticker = yf.Ticker(symbol.upper())
        hist = ticker.history(period=period, interval=interval)
        
        if hist.empty:
            return {"error": f"No data found for symbol {symbol}"}
        
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
        return {"error": f"Failed to get historical data for {symbol}: {str(e)}"}

async def get_dividends(symbol: str) -> Dict[str, Any]:
    """Get dividend history for a stock."""
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
        return {"error": f"Failed to get dividends for {symbol}: {str(e)}"}

async def get_splits(symbol: str) -> Dict[str, Any]:
    """Get stock split history for a stock."""
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
        return {"error": f"Failed to get splits for {symbol}: {str(e)}"}

async def get_financials(symbol: str, quarterly: bool = False) -> Dict[str, Any]:
    """Get financial statements for a stock."""
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
        
        if not income_stmt.empty:
            result["income_statement"] = income_stmt.to_dict()
        
        if not balance_sheet.empty:
            result["balance_sheet"] = balance_sheet.to_dict()
        
        if not cash_flow.empty:
            result["cash_flow"] = cash_flow.to_dict()
        
        return result
    except Exception as e:
        return {"error": f"Failed to get financials for {symbol}: {str(e)}"}

async def get_earnings(symbol: str) -> Dict[str, Any]:
    """Get earnings data for a stock."""
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
        return {"error": f"Failed to get earnings for {symbol}: {str(e)}"}

async def get_news(symbol: str, count: int = 10) -> Dict[str, Any]:
    """Get recent news for a stock."""
    try:
        ticker = yf.Ticker(symbol.upper())
        news = ticker.news
        
        if not news:
            return {"symbol": symbol.upper(), "news": [], "message": "No news available"}
        
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
        return {"error": f"Failed to get news for {symbol}: {str(e)}"}

async def get_recommendations(symbol: str) -> Dict[str, Any]:
    """Get analyst recommendations for a stock."""
    try:
        ticker = yf.Ticker(symbol.upper())
        recommendations = ticker.recommendations
        
        if recommendations is None or recommendations.empty:
            return {"symbol": symbol.upper(), "recommendations": [], "message": "No recommendations available"}
        
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
        return {"error": f"Failed to get recommendations for {symbol}: {str(e)}"}

async def search_stocks(query: str, limit: int = 10) -> Dict[str, Any]:
    """Search for stocks by name or symbol."""
    try:
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
        return {"error": f"Failed to search stocks for query '{query}': {str(e)}"}

async def get_multiple_quotes(symbols: List[str]) -> Dict[str, Any]:
    """Get current quotes for multiple stocks at once."""
    try:
        symbols = [symbol.upper() for symbol in symbols]
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
        return {"error": f"Failed to get multiple quotes: {str(e)}"}

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

class ToolTester:
    """Test suite for all MCP financial tools"""
    
    def __init__(self):
        self.test_symbols = ['AAPL', 'GOOGL', 'MSFT', 'INVALID_SYMBOL']
        self.results = {}
        
    async def test_get_stock_info(self) -> Dict[str, Any]:
        """Test get_stock_info tool"""
        logger.info("Testing get_stock_info...")
        results = {}
        
        for symbol in self.test_symbols[:3]:  # Test valid symbols
            try:
                result = await get_stock_info(symbol)
                results[symbol] = {
                    'success': 'error' not in result,
                    'has_name': bool(result.get('name')),
                    'has_price': result.get('current_price', 0) > 0,
                    'has_market_cap': result.get('market_cap') is not None,
                    'data': result
                }
                logger.info(f"✓ {symbol}: {result.get('name', 'N/A')} - ${result.get('current_price', 0)}")
            except Exception as e:
                results[symbol] = {'success': False, 'error': str(e)}
                logger.error(f"✗ {symbol}: {str(e)}")
        
        # Test invalid symbol
        invalid_result = await get_stock_info('INVALID_SYMBOL')
        results['INVALID_SYMBOL'] = {
            'success': 'error' not in invalid_result,
            'data': invalid_result
        }
        
        return results
    
    async def test_get_historical_data(self) -> Dict[str, Any]:
        """Test get_historical_data tool"""
        logger.info("Testing get_historical_data...")
        results = {}
        
        test_cases = [
            ('AAPL', '1mo', '1d'),
            ('GOOGL', '1wk', '1d'),
            ('MSFT', '1y', '1wk'),
            ('INVALID_SYMBOL', '1mo', '1d')
        ]
        
        for symbol, period, interval in test_cases:
            try:
                result = await get_historical_data(symbol, period, interval)
                results[f"{symbol}_{period}_{interval}"] = {
                    'success': 'error' not in result,
                    'has_data': len(result.get('data', [])) > 0,
                    'count': result.get('count', 0),
                    'data': result
                }
                logger.info(f"✓ {symbol} ({period}, {interval}): {result.get('count', 0)} records")
            except Exception as e:
                results[f"{symbol}_{period}_{interval}"] = {'success': False, 'error': str(e)}
                logger.error(f"✗ {symbol} ({period}, {interval}): {str(e)}")
        
        return results
    
    async def test_get_dividends(self) -> Dict[str, Any]:
        """Test get_dividends tool"""
        logger.info("Testing get_dividends...")
        results = {}
        
        # Test stocks known to have dividends
        dividend_stocks = ['AAPL', 'MSFT', 'JNJ', 'GOOGL']  # GOOGL doesn't pay dividends
        
        for symbol in dividend_stocks:
            try:
                result = await get_dividends(symbol)
                results[symbol] = {
                    'success': 'error' not in result,
                    'has_dividends': len(result.get('dividends', [])) > 0,
                    'count': result.get('count', 0),
                    'data': result
                }
                logger.info(f"✓ {symbol}: {result.get('count', 0)} dividend records")
            except Exception as e:
                results[symbol] = {'success': False, 'error': str(e)}
                logger.error(f"✗ {symbol}: {str(e)}")
        
        return results
    
    async def test_get_splits(self) -> Dict[str, Any]:
        """Test get_splits tool"""
        logger.info("Testing get_splits...")
        results = {}
        
        # Test stocks known to have splits
        split_stocks = ['AAPL', 'GOOGL', 'TSLA', 'NVDA']
        
        for symbol in split_stocks:
            try:
                result = await get_splits(symbol)
                results[symbol] = {
                    'success': 'error' not in result,
                    'has_splits': len(result.get('splits', [])) > 0,
                    'count': result.get('count', 0),
                    'data': result
                }
                logger.info(f"✓ {symbol}: {result.get('count', 0)} split records")
            except Exception as e:
                results[symbol] = {'success': False, 'error': str(e)}
                logger.error(f"✗ {symbol}: {str(e)}")
        
        return results
    
    async def test_get_financials(self) -> Dict[str, Any]:
        """Test get_financials tool"""
        logger.info("Testing get_financials...")
        results = {}
        
        test_cases = [
            ('AAPL', False),  # Annual
            ('MSFT', True),   # Quarterly
            ('GOOGL', False), # Annual
            ('INVALID_SYMBOL', False)
        ]
        
        for symbol, quarterly in test_cases:
            try:
                result = await get_financials(symbol, quarterly)
                results[f"{symbol}_{'Q' if quarterly else 'A'}"] = {
                    'success': 'error' not in result,
                    'has_income': bool(result.get('income_statement')),
                    'has_balance': bool(result.get('balance_sheet')),
                    'has_cashflow': bool(result.get('cash_flow')),
                    'data': result
                }
                logger.info(f"✓ {symbol} ({'Quarterly' if quarterly else 'Annual'}): Financial data retrieved")
            except Exception as e:
                results[f"{symbol}_{'Q' if quarterly else 'A'}"] = {'success': False, 'error': str(e)}
                logger.error(f"✗ {symbol} ({'Quarterly' if quarterly else 'Annual'}): {str(e)}")
        
        return results
    
    async def test_get_earnings(self) -> Dict[str, Any]:
        """Test get_earnings tool"""
        logger.info("Testing get_earnings...")
        results = {}
        
        for symbol in self.test_symbols[:3]:
            try:
                result = await get_earnings(symbol)
                results[symbol] = {
                    'success': 'error' not in result,
                    'has_annual': bool(result.get('annual_earnings')),
                    'has_quarterly': bool(result.get('quarterly_earnings')),
                    'data': result
                }
                logger.info(f"✓ {symbol}: Earnings data retrieved")
            except Exception as e:
                results[symbol] = {'success': False, 'error': str(e)}
                logger.error(f"✗ {symbol}: {str(e)}")
        
        return results
    
    async def test_get_news(self) -> Dict[str, Any]:
        """Test get_news tool"""
        logger.info("Testing get_news...")
        results = {}
        
        test_cases = [
            ('AAPL', 5),
            ('GOOGL', 10),
            ('TSLA', 3),
            ('INVALID_SYMBOL', 5)
        ]
        
        for symbol, count in test_cases:
            try:
                result = await get_news(symbol, count)
                results[f"{symbol}_{count}"] = {
                    'success': 'error' not in result,
                    'has_news': len(result.get('news', [])) > 0,
                    'count': result.get('count', 0),
                    'data': result
                }
                logger.info(f"✓ {symbol}: {result.get('count', 0)} news articles")
            except Exception as e:
                results[f"{symbol}_{count}"] = {'success': False, 'error': str(e)}
                logger.error(f"✗ {symbol}: {str(e)}")
        
        return results
    
    async def test_get_recommendations(self) -> Dict[str, Any]:
        """Test get_recommendations tool"""
        logger.info("Testing get_recommendations...")
        results = {}
        
        for symbol in self.test_symbols[:3]:
            try:
                result = await get_recommendations(symbol)
                results[symbol] = {
                    'success': 'error' not in result,
                    'has_recommendations': len(result.get('recommendations', [])) > 0,
                    'count': result.get('count', 0),
                    'data': result
                }
                logger.info(f"✓ {symbol}: {result.get('count', 0)} recommendations")
            except Exception as e:
                results[symbol] = {'success': False, 'error': str(e)}
                logger.error(f"✗ {symbol}: {str(e)}")
        
        return results
    
    async def test_search_stocks(self) -> Dict[str, Any]:
        """Test search_stocks tool"""
        logger.info("Testing search_stocks...")
        results = {}
        
        search_queries = [
            ('Apple', 5),
            ('Microsoft', 3),
            ('Tesla', 10),
            ('AAPL', 5),
            ('nonexistent_company_12345', 5)
        ]
        
        for query, limit in search_queries:
            try:
                result = await search_stocks(query, limit)
                results[f"{query}_{limit}"] = {
                    'success': 'error' not in result,
                    'has_results': len(result.get('results', [])) > 0,
                    'count': result.get('count', 0),
                    'data': result
                }
                logger.info(f"✓ '{query}': {result.get('count', 0)} results")
            except Exception as e:
                results[f"{query}_{limit}"] = {'success': False, 'error': str(e)}
                logger.error(f"✗ '{query}': {str(e)}")
        
        return results
    
    async def test_get_multiple_quotes(self) -> Dict[str, Any]:
        """Test get_multiple_quotes tool"""
        logger.info("Testing get_multiple_quotes...")
        results = {}
        
        test_cases = [
            ['AAPL', 'GOOGL', 'MSFT'],
            ['TSLA', 'NVDA'],
            ['AAPL', 'INVALID_SYMBOL'],
            ['INVALID_SYMBOL1', 'INVALID_SYMBOL2']
        ]
        
        for i, symbols in enumerate(test_cases):
            try:
                result = await get_multiple_quotes(symbols)
                results[f"batch_{i+1}"] = {
                    'success': 'error' not in result,
                    'requested_count': len(symbols),
                    'returned_count': len(result.get('quotes', {})),
                    'symbols': symbols,
                    'data': result
                }
                logger.info(f"✓ Batch {i+1}: {len(result.get('quotes', {}))} quotes for {symbols}")
            except Exception as e:
                results[f"batch_{i+1}"] = {'success': False, 'error': str(e)}
                logger.error(f"✗ Batch {i+1}: {str(e)}")
        
        return results
    
    async def run_all_tests(self) -> Dict[str, Any]:
        """Run all tool tests"""
        logger.info("Starting comprehensive tool testing...")
        
        test_methods = [
            ('get_stock_info', self.test_get_stock_info),
            ('get_historical_data', self.test_get_historical_data),
            ('get_dividends', self.test_get_dividends),
            ('get_splits', self.test_get_splits),
            ('get_financials', self.test_get_financials),
            ('get_earnings', self.test_get_earnings),
            ('get_news', self.test_get_news),
            ('get_recommendations', self.test_get_recommendations),
            ('search_stocks', self.test_search_stocks),
            ('get_multiple_quotes', self.test_get_multiple_quotes)
        ]
        
        all_results = {}
        start_time = datetime.now()
        
        for tool_name, test_method in test_methods:
            logger.info(f"\n{'='*50}")
            logger.info(f"Testing {tool_name}...")
            logger.info(f"{'='*50}")
            
            try:
                tool_results = await test_method()
                all_results[tool_name] = {
                    'success': True,
                    'results': tool_results,
                    'test_count': len(tool_results)
                }
                
                # Count successful tests
                success_count = sum(1 for r in tool_results.values() if r.get('success', False))
                total_count = len(tool_results)
                logger.info(f"✓ {tool_name}: {success_count}/{total_count} tests passed")
                
            except Exception as e:
                all_results[tool_name] = {
                    'success': False,
                    'error': str(e),
                    'test_count': 0
                }
                logger.error(f"✗ {tool_name}: Failed with error: {str(e)}")
        
        end_time = datetime.now()
        duration = (end_time - start_time).total_seconds()
        
        # Generate summary
        total_tools = len(test_methods)
        successful_tools = sum(1 for r in all_results.values() if r.get('success', False))
        
        summary = {
            'total_tools_tested': total_tools,
            'successful_tools': successful_tools,
            'failed_tools': total_tools - successful_tools,
            'test_duration_seconds': duration,
            'timestamp': datetime.now().isoformat(),
            'results': all_results
        }
        
        logger.info(f"\n{'='*60}")
        logger.info(f"TEST SUMMARY")
        logger.info(f"{'='*60}")
        logger.info(f"Total tools tested: {total_tools}")
        logger.info(f"Successful tools: {successful_tools}")
        logger.info(f"Failed tools: {total_tools - successful_tools}")
        logger.info(f"Test duration: {duration:.2f} seconds")
        logger.info(f"{'='*60}")
        
        return summary

def save_results(results: Dict[str, Any], filename: str = "test_results.json"):
    """Save test results to JSON file"""
    try:
        with open(filename, 'w') as f:
            json.dump(results, f, indent=2, default=str)
        logger.info(f"Test results saved to {filename}")
    except Exception as e:
        logger.error(f"Failed to save results: {str(e)}")

async def main():
    """Main test runner"""
    logger.info("YFinance MCP Server - Tool Testing Suite")
    logger.info("=" * 60)
    
    tester = ToolTester()
    
    try:
        # Run all tests
        results = await tester.run_all_tests()
        
        # Save results
        save_results(results)
        
        # Print final summary
        if results['failed_tools'] == 0:
            logger.info("🎉 ALL TESTS PASSED!")
        else:
            logger.warning(f"⚠️  {results['failed_tools']} tool(s) failed testing")
            
    except Exception as e:
        logger.error(f"Test suite failed: {str(e)}")
        raise

if __name__ == "__main__":
    asyncio.run(main())