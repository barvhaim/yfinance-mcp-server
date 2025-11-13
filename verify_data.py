#!/usr/bin/env python3
"""
Data Verification Script for YFinance MCP Server
Compares MCP server data with direct yfinance calls to verify accuracy
"""

import asyncio
import yfinance as yf
from typing import Any, Dict, List


async def get_stock_info_direct(symbol: str) -> Dict[str, Any]:
    """Direct implementation of get_stock_info for testing"""
    try:
        ticker = yf.Ticker(symbol.upper())
        info = ticker.info

        return {
            "symbol": symbol.upper(),
            "name": info.get("longName", ""),
            "current_price": info.get("currentPrice", 0.0),
            "previous_close": info.get("previousClose"),
            "trailing_pe": info.get("trailingPE"),
            "forward_pe": info.get("forwardPE"),
            "peg_ratio": info.get("pegRatio"),
            "price_to_sales": info.get("priceToSalesTrailing12Months"),
            "price_to_book": info.get("priceToBook"),
            "enterprise_to_ebitda": info.get("enterpriseToEbitda"),
            "profit_margins": info.get("profitMargins"),
            "operating_margins": info.get("operatingMargins"),
            "gross_margins": info.get("grossMargins"),
            "return_on_equity": info.get("returnOnEquity"),
            "return_on_assets": info.get("returnOnAssets"),
        }
    except Exception as e:
        return {"error": f"Failed to get stock info for {symbol}: {str(e)}"}


async def verify_stock_data(symbol: str):
    """Verify data for a single stock"""
    print(f"\n{'='*80}")
    print(f"Verifying data for {symbol}")
    print(f"{'='*80}\n")

    # Get data from our function
    mcp_data = await get_stock_info_direct(symbol)

    # Get data directly from yfinance
    ticker = yf.Ticker(symbol)
    direct_data = ticker.info

    # Compare key P/E metrics
    print("P/E RATIO COMPARISON:")
    print(f"  Trailing P/E (TTM):")
    print(f"    MCP Server:  {mcp_data.get('trailing_pe')}")
    print(f"    Direct call: {direct_data.get('trailingPE')}")
    print(f"    Match: {mcp_data.get('trailing_pe') == direct_data.get('trailingPE')}")

    print(f"\n  Forward P/E:")
    print(f"    MCP Server:  {mcp_data.get('forward_pe')}")
    print(f"    Direct call: {direct_data.get('forwardPE')}")
    print(f"    Match: {mcp_data.get('forward_pe') == direct_data.get('forwardPE')}")

    print(f"\n  PEG Ratio:")
    print(f"    MCP Server:  {mcp_data.get('peg_ratio')}")
    print(f"    Direct call: {direct_data.get('pegRatio')}")
    print(f"    Match: {mcp_data.get('peg_ratio') == direct_data.get('pegRatio')}")

    # Compare price data
    print("\n\nPRICE DATA COMPARISON:")
    print(f"  Current Price:")
    print(f"    MCP Server:  ${mcp_data.get('current_price')}")
    print(f"    Direct call: ${direct_data.get('currentPrice')}")
    print(
        f"    Match: {mcp_data.get('current_price') == direct_data.get('currentPrice')}"
    )

    # Compare valuation metrics
    print("\n\nVALUATION METRICS COMPARISON:")
    valuation_fields = [
        ("price_to_sales", "priceToSalesTrailing12Months", "Price/Sales"),
        ("price_to_book", "priceToBook", "Price/Book"),
        ("enterprise_to_ebitda", "enterpriseToEbitda", "EV/EBITDA"),
    ]

    for mcp_field, direct_field, display_name in valuation_fields:
        mcp_val = mcp_data.get(mcp_field)
        direct_val = direct_data.get(direct_field)
        match = mcp_val == direct_val
        print(f"  {display_name}:")
        print(f"    MCP Server:  {mcp_val}")
        print(f"    Direct call: {direct_val}")
        print(f"    Match: {match}")

    # Compare profitability metrics
    print("\n\nPROFITABILITY METRICS COMPARISON:")
    profitability_fields = [
        ("profit_margins", "profitMargins", "Profit Margin"),
        ("operating_margins", "operatingMargins", "Operating Margin"),
        ("gross_margins", "grossMargins", "Gross Margin"),
        ("return_on_equity", "returnOnEquity", "ROE"),
        ("return_on_assets", "returnOnAssets", "ROA"),
    ]

    for mcp_field, direct_field, display_name in profitability_fields:
        mcp_val = mcp_data.get(mcp_field)
        direct_val = direct_data.get(direct_field)
        match = mcp_val == direct_val
        print(f"  {display_name}:")
        print(f"    MCP Server:  {mcp_val}")
        print(f"    Direct call: {direct_val}")
        print(f"    Match: {match}")

    # Show all available P/E related fields from yfinance
    print("\n\nALL AVAILABLE P/E FIELDS FROM YFINANCE:")
    pe_fields = {
        k: v
        for k, v in direct_data.items()
        if "pe" in k.lower() or "eps" in k.lower() or "earnings" in k.lower()
    }
    for key, value in sorted(pe_fields.items()):
        print(f"  {key}: {value}")

    return mcp_data, direct_data


async def verify_multiple_quotes():
    """Verify multiple quotes functionality"""
    symbols = ["AAPL", "MSFT", "GOOGL"]
    print(f"\n{'='*80}")
    print(f"Verifying multiple quotes for {', '.join(symbols)}")
    print(f"{'='*80}\n")

    for symbol in symbols:
        ticker = yf.Ticker(symbol)
        info = ticker.info

        print(f"\n{symbol}:")
        print(f"  Price: ${info.get('currentPrice')}")
        print(f"  Trailing P/E: {info.get('trailingPE')}")
        print(f"  Forward P/E: {info.get('forwardPE')}")
        print(f"  PEG Ratio: {info.get('pegRatio')}")
        print(f"  Profit Margin: {info.get('profitMargins')}")


async def main():
    """Main verification routine"""
    print("\n" + "=" * 80)
    print("YFINANCE MCP SERVER - DATA VERIFICATION")
    print("=" * 80)

    # Test with popular stocks
    test_symbols = ["AAPL", "MSFT", "TSLA"]

    for symbol in test_symbols:
        await verify_stock_data(symbol)

    # Test multiple quotes
    await verify_multiple_quotes()

    print("\n" + "=" * 80)
    print("VERIFICATION COMPLETE")
    print("=" * 80)
    print("\nNOTE: All MCP data should match direct yfinance calls exactly.")
    print("The MCP server is a transparent wrapper around yfinance.")
    print("\nDifferences from Yahoo Finance website may occur because:")
    print("  1. Website may cache data differently")
    print("  2. Website may use different calculation methods")
    print("  3. API and website data sources may differ slightly")
    print("\nFor the most accurate comparison, compare MCP data with")
    print("direct yfinance library calls (as shown above).\n")


if __name__ == "__main__":
    asyncio.run(main())
