# -*- coding: utf-8 -*-
import yfinance as yf
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
from datetime import datetime, timedelta

import matplotlib
matplotlib.rcParams['axes.unicode_minus'] = False
plt.rcParams['font.sans-serif'] = ['Arial Unicode MS', 'DejaVu Sans']

# 1. TSLA 데이터 다운로드 (5년)
end_date = datetime.now()
start_date = end_date - timedelta(days=365 * 5)

print("📊 TSLA 매수/매도 포인트 분석")
print("=" * 60)
print(f"분석 기간: {start_date.date()} ~ {end_date.date()}")
print("=" * 60)

data = yf.download('TSLA', start=start_date, end=end_date, progress=False)
df = data.copy()

# 2. 기술적 지표 계산

# 2-1. 이동평균 (Moving Average)
df['MA20'] = df['Close'].rolling(window=20).mean()
df['MA50'] = df['Close'].rolling(window=50).mean()
df['MA200'] = df['Close'].rolling(window=200).mean()

# 2-2. RSI (Relative Strength Index)
def calculate_rsi(prices, period=14):
    delta = prices.diff()
    gain = (delta.where(delta > 0, 0)).rolling(window=period).mean()
    loss = (-delta.where(delta < 0, 0)).rolling(window=period).mean()
    rs = gain / loss
    rsi = 100 - (100 / (1 + rs))
    return rsi

df['RSI'] = calculate_rsi(df['Close'], 14)

# 2-3. MACD (Moving Average Convergence Divergence)
exp1 = df['Close'].ewm(span=12, adjust=False).mean()
exp2 = df['Close'].ewm(span=26, adjust=False).mean()
df['MACD'] = exp1 - exp2
df['Signal_Line'] = df['MACD'].ewm(span=9, adjust=False).mean()
df['MACD_Histogram'] = df['MACD'] - df['Signal_Line']

# 2-4. 볼린저 밴드 (Bollinger Bands)
bb_middle = df['Close'].rolling(window=20).mean()
bb_std = df['Close'].rolling(window=20).std()
df['BB_Middle'] = bb_middle
df['BB_Upper'] = bb_middle + (bb_std * 2)
df['BB_Lower'] = bb_middle - (bb_std * 2)

# 3. 거래 신호 생성

# 매수 신호 (Buy Signal)
df['Buy_Signal'] = False
df['Sell_Signal'] = False

for i in range(1, len(df)):
    try:
        # 값 추출 (스칼라로)
        rsi_val = float(df['RSI'].iloc[i])
        macd_val = float(df['MACD'].iloc[i])
        signal_val = float(df['Signal_Line'].iloc[i])
        macd_prev = float(df['MACD'].iloc[i-1])
        signal_prev = float(df['Signal_Line'].iloc[i-1])
        
        # NaN 체크
        if pd.isna(rsi_val) or pd.isna(signal_val):
            continue
        
        # 📈 매수 조건 (MACD + RSI 기반)
        # 1. MACD가 Signal Line을 위로 크로스 (Golden Cross)
        # 2. RSI가 50 이하 (과매도 영역으로 가는 중)
        # 3. MACD가 양수 (상승 모멘텀)
        buy_conditions = (
            (macd_val > signal_val) and              # MACD가 Signal Line 위에
            (macd_prev <= signal_prev) and           # 방금 크로스한 상태
            (rsi_val < 50)                           # RSI가 중립 이하
        )
        if buy_conditions:
            df.at[df.index[i], 'Buy_Signal'] = True
        
        # 📉 매도 조건 (MACD + RSI 기반)
        # 1. MACD가 Signal Line을 아래로 크로스 (Death Cross)
        # 2. RSI가 50 이상 (과매수 영역)
        # 3. MACD가 음수 (하강 모멘텀)
        sell_conditions = (
            (macd_val < signal_val) and              # MACD가 Signal Line 아래
            (macd_prev >= signal_prev) and           # 방금 크로스한 상태
            (rsi_val > 50)                           # RSI가 중립 이상
        )
        if sell_conditions:
            df.at[df.index[i], 'Sell_Signal'] = True
    except:
        continue

# 4. 신호 출력
print("\n🔔 최근 매매 신호 (최근 30일)")
print("-" * 60)

recent_signals = df.tail(30)
buy_signals = recent_signals[recent_signals['Buy_Signal'] == True]
sell_signals = recent_signals[recent_signals['Sell_Signal'] == True]

if len(buy_signals) > 0:
    print("\n✅ 매수 신호:")
    for idx, row in buy_signals.iterrows():
        close_val = row['Close'] if isinstance(row['Close'], (int, float)) else row['Close'].values[0]
        rsi_val = row['RSI'] if isinstance(row['RSI'], (int, float)) else row['RSI'].values[0]
        macd_val = row['MACD'] if isinstance(row['MACD'], (int, float)) else row['MACD'].values[0]
        print(f"  {idx.date()} - 가격: ${close_val:.2f}, RSI: {rsi_val:.2f}, MACD: {macd_val:.4f}")
else:
    print("\n✅ 매수 신호: 없음")

if len(sell_signals) > 0:
    print("\n❌ 매도 신호:")
    for idx, row in sell_signals.iterrows():
        close_val = row['Close'] if isinstance(row['Close'], (int, float)) else row['Close'].values[0]
        rsi_val = row['RSI'] if isinstance(row['RSI'], (int, float)) else row['RSI'].values[0]
        macd_val = row['MACD'] if isinstance(row['MACD'], (int, float)) else row['MACD'].values[0]
        print(f"  {idx.date()} - 가격: ${close_val:.2f}, RSI: {rsi_val:.2f}, MACD: {macd_val:.4f}")
else:
    print("\n❌ 매도 신호: 없음")

# 5. 현재 상태
print("\n📈 현재 상태")
print("-" * 60)
latest = df.iloc[-1]

# 값을 정확히 추출
close_price = latest.loc['Close'] if isinstance(latest.loc['Close'], (int, float)) else float(latest['Close'].values[0])
rsi_val = latest.loc['RSI'] if isinstance(latest.loc['RSI'], (int, float)) else float(latest['RSI'].values[0])
macd_val = latest.loc['MACD'] if isinstance(latest.loc['MACD'], (int, float)) else float(latest['MACD'].values[0])
signal_val = latest.loc['Signal_Line'] if isinstance(latest.loc['Signal_Line'], (int, float)) else float(latest['Signal_Line'].values[0])
ma20_val = latest.loc['MA20'] if isinstance(latest.loc['MA20'], (int, float)) else float(latest['MA20'].values[0])
ma50_val = latest.loc['MA50'] if isinstance(latest.loc['MA50'], (int, float)) else float(latest['MA50'].values[0])
ma200_val = latest.loc['MA200'] if isinstance(latest.loc['MA200'], (int, float)) else float(latest['MA200'].values[0])
bb_upper_val = latest.loc['BB_Upper'] if isinstance(latest.loc['BB_Upper'], (int, float)) else float(latest['BB_Upper'].values[0])
bb_middle_val = latest.loc['BB_Middle'] if isinstance(latest.loc['BB_Middle'], (int, float)) else float(latest['BB_Middle'].values[0])
bb_lower_val = latest.loc['BB_Lower'] if isinstance(latest.loc['BB_Lower'], (int, float)) else float(latest['BB_Lower'].values[0])

print(f"현재가: ${close_price:.2f}")
print(f"RSI(14): {rsi_val:.2f}")
print(f"MACD: {macd_val:.4f}")
print(f"Signal Line: {signal_val:.4f}")
print(f"MA20: ${ma20_val:.2f}")
print(f"MA50: ${ma50_val:.2f}")
print(f"MA200: ${ma200_val:.2f}")
print(f"볼린저 상단: ${bb_upper_val:.2f}")
print(f"볼린저 중단: ${bb_middle_val:.2f}")
print(f"볼린저 하단: ${bb_lower_val:.2f}")

# 현재 상태 평가
print("\n💡 기술적 평가:")
if rsi_val < 30:
    print("  • RSI: 과매도 상태 (매수 기회)")
elif rsi_val > 70:
    print("  • RSI: 과매수 상태 (매도 기회)")
else:
    print(f"  • RSI: 중립 상태 ({rsi_val:.2f})")

if macd_val > signal_val:
    print("  • MACD: 상승 모멘텀")
else:
    print("  • MACD: 하강 모멘텀")

if close_price > ma200_val:
    print("  • 추세: 장기 상승 추세 (MA200 위)")
else:
    print("  • 추세: 장기 하강 추세 (MA200 아래)")

# 6. 그래프 시각화
fig, axes = plt.subplots(4, 1, figsize=(14, 12))

# 서브플롯 1: 가격 + 이동평균 + 거래 신호
ax1 = axes[0]
ax1.plot(df.index, df['Close'], label='Close Price', color='black', linewidth=2)
ax1.plot(df.index, df['MA20'], label='MA20', color='blue', alpha=0.7)
ax1.plot(df.index, df['MA50'], label='MA50', color='orange', alpha=0.7)
ax1.plot(df.index, df['MA200'], label='MA200', color='red', alpha=0.7)

# 매수/매도 신호 마킹 (개선된 방식)
buy_points = df[df['Buy_Signal'] == True]
sell_points = df[df['Sell_Signal'] == True]

if len(buy_points) > 0:
    ax1.scatter(buy_points.index, buy_points['Close'], color='green', marker='^', s=300, 
               label=f'Buy Signal ({len(buy_points)})', zorder=5, edgecolors='darkgreen', linewidth=2)
    # Buy 텍스트 추가
    for idx, row in buy_points.iterrows():
        close_val = row.get('Close') if hasattr(row, 'get') else row['Close']
        close_val = close_val.iloc[0] if hasattr(close_val, 'iloc') else close_val
        ax1.text(idx, close_val + 5, 'BUY', fontsize=9, color='green', fontweight='bold', 
                ha='center', bbox=dict(boxstyle='round,pad=0.3', facecolor='lightgreen', alpha=0.7))

if len(sell_points) > 0:
    ax1.scatter(sell_points.index, sell_points['Close'], color='red', marker='v', s=300, 
               label=f'Sell Signal ({len(sell_points)})', zorder=5, edgecolors='darkred', linewidth=2)
    # Sell 텍스트 추가
    for idx, row in sell_points.iterrows():
        close_val = row.get('Close') if hasattr(row, 'get') else row['Close']
        close_val = close_val.iloc[0] if hasattr(close_val, 'iloc') else close_val
        ax1.text(idx, close_val - 5, 'SELL', fontsize=9, color='red', fontweight='bold', 
                ha='center', bbox=dict(boxstyle='round,pad=0.3', facecolor='lightcoral', alpha=0.7))

ax1.set_title('TSLA 가격 + 이동평균 + 거래 신호', fontsize=14, fontweight='bold')
ax1.set_ylabel('Price ($)')
ax1.legend(loc='upper left', fontsize=10)
ax1.grid(True, alpha=0.3)

# 서브플롯 2: RSI
ax2 = axes[1]
ax2.plot(df.index, df['RSI'], label='RSI(14)', color='purple', linewidth=2)
ax2.axhline(70, color='red', linestyle='--', alpha=0.5, label='Overbought (70)')
ax2.axhline(30, color='green', linestyle='--', alpha=0.5, label='Oversold (30)')
ax2.fill_between(df.index, 30, 70, alpha=0.1, color='blue')
ax2.set_title('RSI (Relative Strength Index)', fontsize=12, fontweight='bold')
ax2.set_ylabel('RSI')
ax2.legend(loc='upper left')
ax2.grid(True, alpha=0.3)

# 서브플롯 3: MACD
ax3 = axes[2]
ax3.plot(df.index, df['MACD'], label='MACD', color='blue', linewidth=2)
ax3.plot(df.index, df['Signal_Line'], label='Signal Line', color='red', linewidth=2)
ax3.bar(df.index, df['MACD_Histogram'], label='Histogram', color='gray', alpha=0.3)
ax3.axhline(0, color='black', linestyle='-', alpha=0.3)
ax3.set_title('MACD (Moving Average Convergence Divergence)', fontsize=12, fontweight='bold')
ax3.set_ylabel('MACD')
ax3.legend(loc='upper left')
ax3.grid(True, alpha=0.3)

# 서브플롯 4: 볼린저 밴드
ax4 = axes[3]
ax4.plot(df.index, df['Close'], label='Close Price', color='black', linewidth=2)
ax4.plot(df.index, df['BB_Upper'], label='Upper Band', color='red', linestyle='--', alpha=0.7)
ax4.plot(df.index, df['BB_Middle'], label='Middle Band (MA20)', color='blue', linestyle='-', alpha=0.7)
ax4.plot(df.index, df['BB_Lower'], label='Lower Band', color='green', linestyle='--', alpha=0.7)
ax4.fill_between(df.index, df['BB_Upper'], df['BB_Lower'], alpha=0.1, color='blue')
ax4.set_title('Bollinger Bands', fontsize=12, fontweight='bold')
ax4.set_ylabel('Price ($)')
ax4.legend(loc='upper left')
ax4.grid(True, alpha=0.3)

plt.tight_layout()
plt.show()

# 7. 성과 분석 (백테스팅)
print("\n📊 백테스팅 분석 (마지막 1년)")
print("-" * 60)

one_year_ago = len(df) - 252
recent_df = df.iloc[one_year_ago:]

recent_buys = recent_df[recent_df['Buy_Signal'] == True]
recent_sells = recent_df[recent_df['Sell_Signal'] == True]

if len(recent_buys) > 0 and len(recent_sells) > 0:
    print(f"매수 신호: {len(recent_buys)}회")
    print(f"매도 신호: {len(recent_sells)}회")
    
    # 간단한 수익률 계산
    total_return = ((recent_df['Close'].iloc[-1] / recent_df['Close'].iloc[0]) - 1) * 100
    print(f"\n기간 수익률: {total_return:.2f}%")
else:
    print("충분한 신호가 없어 성과 분석 불가")
