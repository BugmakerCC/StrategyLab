#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
交互式量化回测系统
整合多币种和多策略回测功能，提供Web界面
"""

import streamlit as st
import numpy as np
import pandas as pd
import yfinance as yf
import plotly.graph_objs as go
from plotly.subplots import make_subplots
from datetime import datetime
import warnings
warnings.filterwarnings('ignore')


# ============ 策略基类 ============
class StrategyBase:
    """策略基类"""

    def __init__(self, data, initial_capital=10000, commission=0.001):
        self.data = data.copy()
        self.initial_capital = initial_capital
        self.commission = commission

    def generate_signals(self, **params):
        """生成交易信号（子类实现）"""
        raise NotImplementedError

    def backtest(self, signals):
        """回测引擎"""
        capital = self.initial_capital
        position = 0
        entry_capital = 0
        trades = []
        portfolio_values = []
        buy_signals = []
        sell_signals = []

        for i in range(len(signals)):
            price = float(self.data['Close'].iloc[i])
            signal = int(signals.iloc[i])
            date = self.data.index[i]

            # 买入
            if signal == 1 and position == 0:
                position = (capital * (1 - self.commission)) / price
                entry_capital = capital
                capital = 0
                trades.append({'type': 'BUY', 'price': price, 'date': date})
                buy_signals.append({'date': date, 'price': price, 'index': i})

            # 卖出
            elif signal == -1 and position > 0:
                capital = position * price * (1 - self.commission)
                profit = capital - entry_capital
                trades.append({
                    'type': 'SELL',
                    'price': price,
                    'date': date,
                    'profit': profit,
                    'profit_pct': (profit / entry_capital) * 100
                })
                sell_signals.append({'date': date, 'price': price, 'index': i})
                position = 0

            # 记录资产价值
            portfolio_value = position * price if position > 0 else capital
            portfolio_values.append(portfolio_value)

        # 强制平仓
        if position > 0:
            last_price = float(self.data['Close'].iloc[-1])
            last_date = self.data.index[-1]
            capital = position * last_price * (1 - self.commission)
            profit = capital - entry_capital
            trades.append({
                'type': 'SELL (Close)',
                'price': last_price,
                'date': last_date,
                'profit': profit,
                'profit_pct': (profit / entry_capital) * 100
            })
            sell_signals.append({'date': last_date, 'price': last_price, 'index': len(signals)-1})

        return self._calculate_performance(portfolio_values, trades, buy_signals, sell_signals)

    def _calculate_performance(self, portfolio_values, trades, buy_signals, sell_signals):
        """计算绩效指标"""
        final_value = portfolio_values[-1]
        total_return = ((final_value - self.initial_capital) / self.initial_capital) * 100

        # 最大回撤
        portfolio_series = pd.Series(portfolio_values)
        cummax = portfolio_series.cummax()
        drawdown = (portfolio_series - cummax) / cummax
        max_drawdown = drawdown.min() * 100

        # 胜率
        sell_trades = [t for t in trades if 'SELL' in t['type']]
        winning_trades = [t for t in sell_trades if t.get('profit', 0) > 0]
        win_rate = (len(winning_trades) / len(sell_trades) * 100) if sell_trades else 0

        # 夏普比率
        returns = portfolio_series.pct_change().dropna()
        sharpe = (returns.mean() / returns.std()) * np.sqrt(252) if returns.std() != 0 else 0

        # 买入持有收益
        buy_hold_return = ((float(self.data['Close'].iloc[-1]) / float(self.data['Close'].iloc[0])) - 1) * 100

        return {
            'total_return': total_return,
            'final_value': final_value,
            'max_drawdown': max_drawdown,
            'win_rate': win_rate,
            'sharpe_ratio': sharpe,
            'num_trades': len(sell_trades),
            'buy_hold_return': buy_hold_return,
            'portfolio_values': portfolio_values,
            'trades': trades,
            'buy_signals': buy_signals,
            'sell_signals': sell_signals
        }


# ============ 策略1: 移动平均线交叉 ============
class MAStrategy(StrategyBase):
    """移动平均线交叉策略"""

    def generate_signals(self, short_window=5, long_window=20, use_filter=True):
        df = self.data.copy()
        df['MA_short'] = df['Close'].rolling(window=short_window).mean()
        df['MA_long'] = df['Close'].rolling(window=long_window).mean()

        if use_filter:
            df['MA_trend'] = df['Close'].rolling(window=50).mean()

        df['Signal'] = 0

        for i in range(1, len(df)):
            # 金叉
            if (float(df['MA_short'].iloc[i]) > float(df['MA_long'].iloc[i]) and
                float(df['MA_short'].iloc[i-1]) <= float(df['MA_long'].iloc[i-1])):
                if not use_filter or float(df['Close'].iloc[i]) > float(df['MA_trend'].iloc[i]):
                    df.iloc[i, df.columns.get_loc('Signal')] = 1

            # 死叉
            elif (float(df['MA_short'].iloc[i]) < float(df['MA_long'].iloc[i]) and
                  float(df['MA_short'].iloc[i-1]) >= float(df['MA_long'].iloc[i-1])):
                df.iloc[i, df.columns.get_loc('Signal')] = -1

        return df['Signal'].fillna(0)


# ============ 策略2: RSI均值回归 ============
class RSIStrategy(StrategyBase):
    """RSI均值回归策略"""

    def generate_signals(self, rsi_period=14, oversold=35, overbought=80):
        df = self.data.copy()

        # 计算RSI
        delta = df['Close'].diff()
        gain = (delta.where(delta > 0, 0)).rolling(window=rsi_period).mean()
        loss = (-delta.where(delta < 0, 0)).rolling(window=rsi_period).mean()
        rs = gain / loss
        df['RSI'] = 100 - (100 / (1 + rs))

        df['Signal'] = 0
        position = 0

        for i in range(1, len(df)):
            rsi = float(df['RSI'].iloc[i])

            if rsi < oversold and position == 0:
                df.iloc[i, df.columns.get_loc('Signal')] = 1
                position = 1
            elif rsi > overbought and position == 1:
                df.iloc[i, df.columns.get_loc('Signal')] = -1
                position = 0

        return df['Signal'].fillna(0)


# ============ 策略3: 布林带突破 ============
class BollingerStrategy(StrategyBase):
    """布林带突破策略"""

    def generate_signals(self, period=20, num_std=2):
        df = self.data.copy()

        df['MA'] = df['Close'].rolling(window=period).mean()
        df['STD'] = df['Close'].rolling(window=period).std()
        df['Upper'] = df['MA'] + (df['STD'] * num_std)
        df['Lower'] = df['MA'] - (df['STD'] * num_std)

        df['Signal'] = 0
        position = 0

        for i in range(1, len(df)):
            price = float(df['Close'].iloc[i])
            lower = float(df['Lower'].iloc[i])
            upper = float(df['Upper'].iloc[i])

            if price < lower and position == 0:
                df.iloc[i, df.columns.get_loc('Signal')] = 1
                position = 1
            elif price > upper and position == 1:
                df.iloc[i, df.columns.get_loc('Signal')] = -1
                position = 0

        return df['Signal'].fillna(0)


# ============ 策略4: MACD ============
class MACDStrategy(StrategyBase):
    """MACD策略"""

    def generate_signals(self, fast=12, slow=26, signal=9):
        df = self.data.copy()

        ema_fast = df['Close'].ewm(span=fast).mean()
        ema_slow = df['Close'].ewm(span=slow).mean()
        df['MACD'] = ema_fast - ema_slow
        df['Signal_Line'] = df['MACD'].ewm(span=signal).mean()

        df['Signal'] = 0

        for i in range(1, len(df)):
            if (float(df['MACD'].iloc[i]) > float(df['Signal_Line'].iloc[i]) and
                float(df['MACD'].iloc[i-1]) <= float(df['Signal_Line'].iloc[i-1]) and
                float(df['MACD'].iloc[i]) < 0):
                df.iloc[i, df.columns.get_loc('Signal')] = 1
            elif (float(df['MACD'].iloc[i]) < float(df['Signal_Line'].iloc[i]) and
                  float(df['MACD'].iloc[i-1]) >= float(df['Signal_Line'].iloc[i-1])):
                df.iloc[i, df.columns.get_loc('Signal')] = -1

        return df['Signal'].fillna(0)


# ============ 策略5: 动量突破 ============
class MomentumStrategy(StrategyBase):
    """动量突破策略"""

    def generate_signals(self, lookback=20, entry_threshold=0.02):
        df = self.data.copy()

        df['High_N'] = df['High'].rolling(window=lookback).max()
        df['Low_N'] = df['Low'].rolling(window=lookback).min()

        df['Signal'] = 0
        position = 0

        for i in range(lookback, len(df)):
            price = float(df['Close'].iloc[i])
            high_n = float(df['High_N'].iloc[i-1])
            low_n = float(df['Low_N'].iloc[i-1])

            if price > high_n * (1 + entry_threshold) and position == 0:
                df.iloc[i, df.columns.get_loc('Signal')] = 1
                position = 1
            elif price < low_n and position == 1:
                df.iloc[i, df.columns.get_loc('Signal')] = -1
                position = 0

        return df['Signal'].fillna(0)


# ============ 数据获取 ============
@st.cache_data(ttl=3600)
def fetch_data(ticker, period, interval):
    """获取市场数据（带缓存）"""
    try:
        data = yf.download(ticker, period=period, interval=interval, progress=False)
        if data.empty:
            return None
        return data
    except Exception as e:
        st.error(f"获取数据失败: {e}")
        return None


# ============ 可视化 ============
def plot_backtest_results(data, result, ticker, strategy_name, initial_capital=10000):
    """绘制回测结果"""
    buy_signals = result['buy_signals']
    sell_signals = result['sell_signals']

    # 确保数据格式正确（处理多层级列名）
    if isinstance(data.columns, pd.MultiIndex):
        data.columns = data.columns.get_level_values(0)

    # 确保索引是DatetimeIndex
    if not isinstance(data.index, pd.DatetimeIndex):
        data.index = pd.to_datetime(data.index)

    fig = make_subplots(
        rows=3, cols=1,
        shared_xaxes=True,
        vertical_spacing=0.05,
        subplot_titles=(
            f'{ticker} - {strategy_name}',
            '成交量',
            '资产价值'
        ),
        row_heights=[0.5, 0.25, 0.25]
    )

    # 第一个图：价格和买卖点
    # 提取价格数据（确保是Series类型）
    dates = data.index
    high_prices = data['High'].values if 'High' in data.columns else data['Close'].values
    low_prices = data['Low'].values if 'Low' in data.columns else data['Close'].values
    close_prices = data['Close'].values

    # 高低价区间
    fig.add_trace(
        go.Scatter(
            x=dates,
            y=high_prices,
            mode='lines',
            line=dict(width=0),
            showlegend=False,
            hoverinfo='skip'
        ),
        row=1, col=1
    )

    fig.add_trace(
        go.Scatter(
            x=dates,
            y=low_prices,
            mode='lines',
            line=dict(width=0),
            fillcolor='rgba(180,180,180,0.2)',
            fill='tonexty',
            name='高低价区间',
            hoverinfo='skip'
        ),
        row=1, col=1
    )

    # 收盘价线
    fig.add_trace(
        go.Scatter(
            x=dates,
            y=close_prices,
            mode='lines',
            line=dict(color='blue', width=2),
            name='收盘价',
            hovertemplate='日期: %{x}<br>价格: $%{y:,.2f}<extra></extra>'
        ),
        row=1, col=1
    )

    # 买入点
    if buy_signals:
        buy_dates = [s['date'] for s in buy_signals]
        buy_prices = [s['price'] for s in buy_signals]
        fig.add_trace(
            go.Scatter(
                x=buy_dates,
                y=buy_prices,
                mode='markers',
                marker=dict(symbol='triangle-up', size=15, color='green'),
                name='买入',
                hovertemplate='买入<br>日期: %{x}<br>价格: $%{y:.4f}<extra></extra>'
            ),
            row=1, col=1
        )

    # 卖出点
    if sell_signals:
        sell_dates = [s['date'] for s in sell_signals]
        sell_prices = [s['price'] for s in sell_signals]
        fig.add_trace(
            go.Scatter(
                x=sell_dates,
                y=sell_prices,
                mode='markers',
                marker=dict(symbol='triangle-down', size=15, color='red'),
                name='卖出',
                hovertemplate='卖出<br>日期: %{x}<br>价格: $%{y:.4f}<extra></extra>'
            ),
            row=1, col=1
        )

    # 第二个图：成交量
    volume_data = data['Volume'].values if 'Volume' in data.columns else [0] * len(data)
    fig.add_trace(
        go.Bar(
            x=dates,
            y=volume_data,
            name='成交量',
            marker_color='rgba(100,100,100,0.3)',
            hovertemplate='日期: %{x}<br>成交量: %{y:,.0f}<extra></extra>'
        ),
        row=2, col=1
    )

    # 第三个图：资产价值
    fig.add_trace(
        go.Scatter(
            x=data.index,
            y=result['portfolio_values'],
            mode='lines',
            line=dict(color='green', width=2),
            fill='tozeroy',
            name='资产价值',
            hovertemplate='资产: $%{y:,.2f}<extra></extra>'
        ),
        row=3, col=1
    )

    # 初始资金线
    fig.add_hline(
        y=initial_capital,
        line_dash="dash",
        line_color="gray",
        row=3, col=1,
        annotation_text="初始资金"
    )

    # 关闭rangeslider（必须在update_layout之前）
    fig.update_xaxes(rangeslider_visible=False, row=1, col=1)
    fig.update_xaxes(rangeslider_visible=False, row=2, col=1)
    fig.update_xaxes(rangeslider_visible=False, row=3, col=1)

    # 设置Y轴范围和标题
    price_min = float(data['Low'].min())
    price_max = float(data['High'].max())
    price_range = price_max - price_min

    fig.update_yaxes(
        title_text="价格 ($)",
        row=1, col=1,
        range=[price_min - price_range * 0.1, price_max + price_range * 0.1],
        fixedrange=False
    )
    fig.update_yaxes(
        title_text="成交量",
        row=2, col=1,
        fixedrange=False
    )
    fig.update_yaxes(
        title_text="资产 ($)",
        row=3, col=1,
        fixedrange=False
    )

    # 更新布局（放在最后）
    fig.update_layout(
        height=1000,
        showlegend=True,
        hovermode='x unified',
        legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="right", x=1),
        margin=dict(l=80, r=80, t=100, b=80)
    )

    return fig


# ============ Streamlit 应用 ============
def main():
    st.set_page_config(page_title="量化回测系统", layout="wide", page_icon="📊")

    st.title("📊 加密货币量化回测系统")
    st.markdown("---")

    # 侧边栏 - 参数配置
    st.sidebar.header("⚙️ 回测参数")

    # 币种选择
    ticker = st.sidebar.selectbox(
        "选择加密货币",
        options=['BTC-USD', 'ETH-USD', 'BNB-USD', 'SOL-USD', 'DOGE-USD'],
        index=0,
        help="选择要回测的加密货币"
    )

    # 周期选择
    period = st.sidebar.selectbox(
        "回测周期",
        options=['1mo', '3mo', '6mo', '1y', '2y'],
        index=2,
        help="选择历史数据的时间范围"
    )

    # K线级别
    interval = st.sidebar.selectbox(
        "K线级别",
        options=['1d', '1h', '4h'],
        index=0,
        help="选择K线的时间间隔"
    )

    # 初始资金
    initial_capital = st.sidebar.number_input(
        "初始资金 ($)",
        min_value=100,
        max_value=1000000,
        value=10000,
        step=1000,
        help="设置回测的初始资金"
    )

    st.sidebar.markdown("---")

    # 策略选择
    strategy_name = st.sidebar.selectbox(
        "选择策略",
        options=[
            'RSI均值回归',
            '移动平均线交叉',
            '布林带突破',
            'MACD',
            '动量突破'
        ],
        index=0,
        help="选择交易策略"
    )

    st.sidebar.markdown("---")
    st.sidebar.subheader("📈 策略参数")

    # 根据不同策略显示不同参数
    strategy_params = {}

    if strategy_name == 'RSI均值回归':
        strategy_params['rsi_period'] = st.sidebar.slider("RSI周期", 5, 30, 14)
        strategy_params['oversold'] = st.sidebar.slider("超卖线", 20, 40, 35)
        strategy_params['overbought'] = st.sidebar.slider("超买线", 60, 90, 80)

    elif strategy_name == '移动平均线交叉':
        strategy_params['short_window'] = st.sidebar.slider("短期均线", 3, 20, 5)
        strategy_params['long_window'] = st.sidebar.slider("长期均线", 10, 50, 20)
        strategy_params['use_filter'] = st.sidebar.checkbox("使用趋势过滤", value=True)

    elif strategy_name == '布林带突破':
        strategy_params['period'] = st.sidebar.slider("布林带周期", 10, 30, 20)
        strategy_params['num_std'] = st.sidebar.slider("标准差倍数", 1.0, 3.0, 2.0, 0.1)

    elif strategy_name == 'MACD':
        strategy_params['fast'] = st.sidebar.slider("快线周期", 5, 20, 12)
        strategy_params['slow'] = st.sidebar.slider("慢线周期", 15, 40, 26)
        strategy_params['signal'] = st.sidebar.slider("信号线周期", 5, 15, 9)

    elif strategy_name == '动量突破':
        strategy_params['lookback'] = st.sidebar.slider("回看周期", 10, 50, 20)
        strategy_params['entry_threshold'] = st.sidebar.slider("突破阈值", 0.01, 0.05, 0.02, 0.01)

    st.sidebar.markdown("---")

    # 运行回测按钮
    run_backtest = st.sidebar.button("🚀 运行回测", type="primary", use_container_width=True)

    # 主界面
    if run_backtest:
        with st.spinner(f"正在获取 {ticker} 数据..."):
            data = fetch_data(ticker, period, interval)

        if data is None or data.empty:
            st.error("❌ 无法获取数据，请检查网络连接或稍后重试")
            return

        st.success(f"✅ 成功获取 {len(data)} 条数据")

        # 执行回测
        with st.spinner(f"正在运行 {strategy_name} 策略..."):
            # 选择策略
            if strategy_name == 'RSI均值回归':
                strategy = RSIStrategy(data, initial_capital=initial_capital)
                signals = strategy.generate_signals(**strategy_params)
            elif strategy_name == '移动平均线交叉':
                strategy = MAStrategy(data, initial_capital=initial_capital)
                signals = strategy.generate_signals(**strategy_params)
            elif strategy_name == '布林带突破':
                strategy = BollingerStrategy(data, initial_capital=initial_capital)
                signals = strategy.generate_signals(**strategy_params)
            elif strategy_name == 'MACD':
                strategy = MACDStrategy(data, initial_capital=initial_capital)
                signals = strategy.generate_signals(**strategy_params)
            elif strategy_name == '动量突破':
                strategy = MomentumStrategy(data, initial_capital=initial_capital)
                signals = strategy.generate_signals(**strategy_params)

            # 运行回测
            result = strategy.backtest(signals)

        st.success("✅ 回测完成！")

        # 显示绩效指标
        st.markdown("---")
        st.subheader("📊 回测绩效")

        col1, col2, col3, col4 = st.columns(4)

        with col1:
            outperformance = result['total_return'] - result['buy_hold_return']
            # 不使用delta_color，让Streamlit使用默认行为
            # 默认应该是：正数=绿色上，负数=红色下
            st.metric(
                label="总收益率",
                value=f"{result['total_return']:.2f}%",
                delta=f"{outperformance:.2f}% vs 买入持有"
            )

        with col2:
            st.metric("最终资金", f"${result['final_value']:,.2f}")

        with col3:
            st.metric("夏普比率", f"{result['sharpe_ratio']:.2f}")

        with col4:
            st.metric("最大回撤", f"{result['max_drawdown']:.2f}%")

        col5, col6, col7, col8 = st.columns(4)

        with col5:
            st.metric("交易次数", f"{result['num_trades']}")

        with col6:
            st.metric("胜率", f"{result['win_rate']:.1f}%")

        with col7:
            st.metric("买入持有收益", f"{result['buy_hold_return']:.2f}%")

        with col8:
            beat_market = "✅ 跑赢" if result['total_return'] > result['buy_hold_return'] else "❌ 跑输"
            st.metric("vs 市场", beat_market)

        # 显示图表
        st.markdown("---")
        st.subheader("📈 回测可视化")

        fig = plot_backtest_results(data, result, ticker, strategy_name, initial_capital)
        st.plotly_chart(fig, use_container_width=True)

        # 交易记录
        st.markdown("---")
        st.subheader("📋 交易记录")

        if result['trades']:
            trades_df = pd.DataFrame(result['trades'])
            trades_df['date'] = pd.to_datetime(trades_df['date']).dt.strftime('%Y-%m-%d')
            trades_df['price'] = trades_df['price'].apply(lambda x: f"${x:,.4f}")

            if 'profit' in trades_df.columns:
                trades_df['profit'] = trades_df['profit'].apply(
                    lambda x: f"${x:,.2f}" if pd.notna(x) else "-"
                )
            if 'profit_pct' in trades_df.columns:
                trades_df['profit_pct'] = trades_df['profit_pct'].apply(
                    lambda x: f"{x:+.2f}%" if pd.notna(x) else "-"
                )

            st.dataframe(trades_df, use_container_width=True, height=300)
        else:
            st.info("本次回测未产生任何交易")

    else:
        # 默认显示说明
        st.info("👈 请在左侧边栏配置参数，然后点击「运行回测」按钮开始回测")

        st.markdown("### 📚 使用指南")

        col1, col2 = st.columns(2)

        with col1:
            st.markdown("""
            **支持的加密货币：**
            - 比特币 (BTC-USD)
            - 以太坊 (ETH-USD)
            - 币安币 (BNB-USD)
            - Solana (SOL-USD)
            - 狗狗币 (DOGE-USD)
            """)

            st.markdown("""
            **支持的策略：**
            1. **RSI均值回归** - 基于超买超卖信号
            2. **移动平均线交叉** - 金叉死叉信号
            3. **布林带突破** - 价格突破布林带
            4. **MACD** - MACD线交叉信号
            5. **动量突破** - 价格突破历史高点
            """)

        with col2:
            st.markdown("""
            **回测周期：**
            - 1个月 (1mo)
            - 3个月 (3mo)
            - 6个月 (6mo)
            - 1年 (1y)
            - 2年 (2y)
            """)

            st.markdown("""
            **绩效指标：**
            - 总收益率
            - 最大回撤
            - 夏普比率
            - 胜率
            - 交易次数
            - 买入持有对比
            """)

        st.markdown("---")
        st.warning("⚠️ **风险提示**: 历史表现不代表未来收益，所有回测结果仅供参考，不构成投资建议。")


if __name__ == '__main__':
    main()
