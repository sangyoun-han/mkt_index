import yfinance as yf
import matplotlib.pyplot as plt
import pandas as pd
from datetime import datetime, timedelta

# 1. 데이터 기간 설정
end_date = datetime.now()
start_date = end_date - timedelta(days=365 * 10)

# 2. 데이터 다운로드
# HG=F(구리), GC=F(금), ^TNX(10년물 금리), ^GSPC(S&P 500), AAPL(알파벳), ^DJI(다우존스)
tickers = ['HG=F', 'GC=F', '^TNX', '^GSPC', 'AAPL', '^DJI']
data = yf.download(tickers, start=start_date, end=end_date)['Close']

# 3. 데이터 가공 및 지수화
df = pd.DataFrame()
df['Cu/Au Ratio'] = data['HG=F'] / data['GC=F']
df['10Y Yield'] = data['^TNX']
df['S&P 500'] = data['^GSPC']
df['AAPL/DJI Ratio'] = data['AAPL'] / data['^DJI']
df = df.dropna()

# 모든 데이터를 첫날(10년 전) 가격으로 나누고 100을 곱해 표준화
df_indexed = (df / df.iloc[0]) * 100

# 4. 통합 그래프 시각화
plt.figure(figsize=(14, 8))

plt.plot(df_indexed.index, df_indexed['Cu/Au Ratio'], label='Copper/Gold Ratio (Economy)', color='royalblue', linewidth=2)
plt.plot(df_indexed.index, df_indexed['10Y Yield'], label='10Y Treasury Yield (Cost)', color='firebrick', linewidth=2, linestyle='--')
plt.plot(df_indexed.index, df_indexed['S&P 500'], label='S&P 500 (Market)', color='forestgreen', linewidth=2)
plt.plot(df_indexed.index, df_indexed['AAPL/DJI Ratio'], label='AAPL/DJI Ratio', color='purple', linewidth=2)

# 그래프 스타일링
plt.title('Normalized Comparison (10-Year Trend, Base=100)', fontsize=16)
plt.ylabel('Performance Index', fontsize=12)
plt.axhline(100, color='black', lw=1, alpha=0.5) # 기준선
plt.grid(True, alpha=0.3)
plt.legend(loc='upper left', fontsize=11)

plt.tight_layout()
plt.show()