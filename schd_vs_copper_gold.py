# -*- coding: utf-8 -*-
import yfinance as yf
import matplotlib.pyplot as plt
import pandas as pd
from datetime import datetime, timedelta
import numpy as np

import matplotlib
matplotlib.rcParams['axes.unicode_minus'] = False
plt.rcParams['font.sans-serif'] = ['Arial Unicode MS', 'DejaVu Sans']

# 1. 데이터 기간 설정 (10년)
end_date = datetime.now()
start_date = end_date - timedelta(days=365 * 10)

print("📊 SCHD 주가 vs 구리/금 비율 분석")
print("=" * 70)
print(f"분석 기간: {start_date.date()} ~ {end_date.date()}")
print("=" * 70)

# 2. 데이터 다운로드
# SCHD (Schwab US Dividend Equity ETF)
# HG=F (구리), GC=F (금)
tickers = ['SCHD', 'HG=F', 'GC=F']
data = yf.download(tickers, start=start_date, end=end_date, progress=False)['Close']

# 3. 데이터 가공 및 지수화
df = pd.DataFrame()
df['SCHD'] = data['SCHD']
df['Copper'] = data['HG=F']
df['Gold'] = data['GC=F']
df['Cu/Au Ratio'] = data['HG=F'] / data['GC=F']
df = df.dropna()

# 모든 데이터를 첫날(10년 전) 가격으로 나누고 100을 곱해 표준화
df_indexed = (df / df.iloc[0]) * 100

# 4. 통계 분석
print("\n📈 통계 분석")
print("-" * 70)
print(f"SCHD 수익률: {((df['SCHD'].iloc[-1] / df['SCHD'].iloc[0]) - 1) * 100:.2f}%")
print(f"Cu/Au 비율 변화: {((df['Cu/Au Ratio'].iloc[-1] / df['Cu/Au Ratio'].iloc[0]) - 1) * 100:.2f}%")
print(f"\nSCHD 최고가: ${df['SCHD'].max():.2f} ({df['SCHD'].idxmax().date()})")
print(f"SCHD 최저가: ${df['SCHD'].min():.2f} ({df['SCHD'].idxmin().date()})")
print(f"SCHD 평균가: ${df['SCHD'].mean():.2f}")
print(f"SCHD 표준편차: ${df['SCHD'].std():.2f}")

# 상관관계 분석
correlation = df['SCHD'].corr(df['Cu/Au Ratio'])
print(f"\n📊 SCHD와 Cu/Au 비율의 상관관계: {correlation:.4f}")
if correlation > 0.3:
    print("  → 양의 상관관계 (함께 움직임)")
elif correlation < -0.3:
    print("  → 음의 상관관계 (반대로 움직임)")
else:
    print("  → 약한 상관관계 (독립적)")

# 5. 최근 데이터
print("\n📌 최근 상태 (마지막 거래일)")
print("-" * 70)
latest = df.iloc[-1]
latest_indexed = df_indexed.iloc[-1]
print(f"SCHD 현재가: ${latest['SCHD']:.2f} (지수: {latest_indexed['SCHD']:.2f})")
print(f"구리 가격: ${latest['Copper']:.2f}")
print(f"금 가격: ${latest['Gold']:.2f}")
print(f"Cu/Au 비율: {latest['Cu/Au Ratio']:.4f}")

# 6. 이동평균 추가 (추세 파악)
df['SCHD_MA50'] = df['SCHD'].rolling(window=50).mean()
df['SCHD_MA200'] = df['SCHD'].rolling(window=200).mean()
df_indexed['SCHD_MA50'] = df_indexed['SCHD'].rolling(window=50).mean()
df_indexed['SCHD_MA200'] = df_indexed['SCHD'].rolling(window=200).mean()

# 7. 추세 판단
latest_schd = df['SCHD'].iloc[-1]
latest_ma50 = df['SCHD_MA50'].iloc[-1]
latest_ma200 = df['SCHD_MA200'].iloc[-1]

print(f"\n💡 추세 판단:")
if latest_schd > latest_ma50 > latest_ma200:
    print("  → 강한 상승 추세 (현재가 > MA50 > MA200)")
elif latest_schd > latest_ma200:
    print("  → 상승 추세 (현재가 > MA200)")
else:
    print("  → 하강 추세 또는 약세")

# 8. 그래프 시각화
fig, axes = plt.subplots(3, 1, figsize=(14, 12))

# 서브플롯 1: SCHD 가격 (원본)
ax1 = axes[0]
ax1.plot(df.index, df['SCHD'], label='SCHD Price', color='darkblue', linewidth=2)
ax1.plot(df.index, df['SCHD_MA50'], label='MA50', color='orange', linestyle='--', alpha=0.7)
ax1.plot(df.index, df['SCHD_MA200'], label='MA200', color='red', linestyle='--', alpha=0.7)
ax1.fill_between(df.index, df['SCHD_MA200'], df['SCHD'], alpha=0.2, color='blue')
ax1.set_title('SCHD 주가 추이 (원본)', fontsize=14, fontweight='bold')
ax1.set_ylabel('Price ($)')
ax1.legend(loc='upper left', fontsize=10)
ax1.grid(True, alpha=0.3)

# 서브플롯 2: 정규화된 비교 (SCHD vs Cu/Au)
ax2 = axes[1]
ax2_twin = ax2.twinx()

line1 = ax2.plot(df_indexed.index, df_indexed['SCHD'], label='SCHD (Index)', 
                color='darkblue', linewidth=2.5)
line2 = ax2_twin.plot(df_indexed.index, df_indexed['Cu/Au Ratio'], label='Copper/Gold Ratio (Index)', 
                     color='green', linewidth=2.5)

ax2.set_title('SCHD vs 구리/금 비율 비교 (정규화, Base=100)', fontsize=14, fontweight='bold')
ax2.set_ylabel('SCHD Index', fontsize=12, color='darkblue')
ax2_twin.set_ylabel('Cu/Au Ratio Index', fontsize=12, color='green')
ax2.tick_params(axis='y', labelcolor='darkblue')
ax2_twin.tick_params(axis='y', labelcolor='green')
ax2.axhline(100, color='black', linestyle=':', alpha=0.3)
ax2.grid(True, alpha=0.3)

# 범례 통합
lines = line1 + line2
labels = [l.get_label() for l in lines]
ax2.legend(lines, labels, loc='upper left', fontsize=10)

# 서브플롯 3: 롤링 상관관계
rolling_corr = df['SCHD'].rolling(window=60).corr(df['Cu/Au Ratio'])
ax3 = axes[2]
ax3.plot(rolling_corr.index, rolling_corr, label='60-Day Rolling Correlation', 
        color='purple', linewidth=2)
ax3.axhline(0, color='black', linestyle='-', alpha=0.3)
ax3.fill_between(rolling_corr.index, 0, rolling_corr, alpha=0.3, color='purple')
ax3.set_title('SCHD와 Cu/Au 비율의 60일 롤링 상관관계', fontsize=14, fontweight='bold')
ax3.set_ylabel('Correlation')
ax3.legend(loc='upper left', fontsize=10)
ax3.grid(True, alpha=0.3)
ax3.set_ylim([-1, 1])

plt.tight_layout()
plt.show()

# 9. 투자 인사이트
print("\n💎 투자 인사이트")
print("-" * 70)

# Cu/Au 비율이 높으면 경제 호황
latest_cu_au = df['Cu/Au Ratio'].iloc[-1]
avg_cu_au = df['Cu/Au Ratio'].mean()

if latest_cu_au > avg_cu_au:
    print("🌱 현재 Cu/Au 비율이 평균보다 높음")
    print("  → 경제 상황이 비교적 좋음 (구리 수요 증가)")
    print("  → 배당주(SCHD)에 긍정적 신호")
else:
    print("⚠️ 현재 Cu/Au 비율이 평균보다 낮음")
    print("  → 경제 상황이 약해짐 (금 선호 증가)")
    print("  → 배당주 수익성 하락 가능성")

# SCHD 추천
latest_price_vs_ma200 = (df['SCHD'].iloc[-1] / df['SCHD_MA200'].iloc[-1] - 1) * 100
print(f"\n📊 SCHD 평가:")
if latest_price_vs_ma200 > 15:
    print(f"  → 고평가 상태 (MA200 대비 +{latest_price_vs_ma200:.1f}%)")
    print("  → 매도 기회 또는 관망 추천")
elif latest_price_vs_ma200 < -15:
    print(f"  → 저평가 상태 (MA200 대비 {latest_price_vs_ma200:.1f}%)")
    print("  → 매수 기회 추천")
else:
    print(f"  → 정상 범위 (MA200 대비 {latest_price_vs_ma200:+.1f}%)")
    print("  → 정기 매수 추천")

# 시장 신호 종합
print(f"\n🎯 종합 평가:")
if correlation > 0.3 and latest_cu_au > avg_cu_au and latest_schd > latest_ma200:
    print("  ✅ 긍정적 신호: 경제 호황 + 강한 상승 추세 → 매수 강화")
elif correlation < -0.3 and latest_cu_au < avg_cu_au:
    print("  ⚠️ 주의 신호: 경제 약세 신호 → 손절 또는 매도 검토")
else:
    print("  ↔️ 중립: 신호가 엇갈림 → 추가 관찰 필요")

print("\n" + "=" * 70)
