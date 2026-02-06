# Market Index Analysis - Copilot Instructions

## Project Overview
A Python financial data analysis tool that tracks and visualizes the relationship between commodity ratios, treasury yields, and equity market performance over a 10-year period using yfinance data.

**Core Logic**: Downloads financial data for four tickers (copper, gold, 10Y yield, S&P 500), computes normalized indices with day-1 values as base (=100), and displays comparative trends.

## Architecture

### Data Flow
1. **Fetch Phase**: `yfinance.download()` retrieves daily closing prices for: HG=F (copper), GC=F (gold), ^TNX (10Y Treasury), ^GSPC (S&P 500)
2. **Transform Phase**: 
   - Copper/Gold ratio = economic health indicator
   - 10Y yield = financing cost proxy
   - S&P 500 = market performance
   - All indexed to base=100 at start date
3. **Visualization**: Multi-line time-series plot comparing normalized performance

### Key Dependencies
- `yfinance`: Financial data retrieval
- `pandas`: Data manipulation and time-series handling
- `matplotlib`: Charting and visualization
- `datetime`: Date range calculation

## Development Patterns

### Data Processing Convention
- Always drop NaN values after feature engineering (`df.dropna()`)
- Use index-based normalization: `(value / first_value) * 100` for comparison
- Maintain DataFrame structure through transformations for matplotlib compatibility

### Visualization Style
- Base grid appearance: `figsize=(14, 8)` for readability
- Reference line at 100: `plt.axhline(100, ...)` marks starting point
- Color coding: royalblue (economy), firebrick (cost), forestgreen (market)
- Use dashed linestyle (`linestyle='--'`) for secondary indicators

## Extension Points

### Adding New Indicators
To add another market signal:
1. Add ticker to `tickers` list and `yfinance.download()`
2. Create feature in `df` DataFrame (e.g., `df['VIX'] = data['^VIX']`)
3. Index it: `df_indexed['VIX'] = (df['VIX'] / df['VIX'].iloc[0]) * 100`
4. Plot with `plt.plot(df_indexed.index, df_indexed['VIX'], label='...', color='...', linewidth=2)`

### Extending Date Range
Modify the `timedelta(days=365 * 10)` parameter—currently 10 years. Note: longer ranges increase yfinance download time.

## Common Tasks

**Modify date range**: Edit start/end date calculation (lines 7-9)
**Change chart colors**: Update color parameters in `plt.plot()` calls (lines 28-30)
**Adjust time period**: Multiply by years in `timedelta(days=365 * {years})`
**Add statistics**: Insert calculations before indexing (e.g., correlation, moving averages)
