# StrategyLab

An interactive cryptocurrency quantitative trading backtesting system built with Streamlit. Test and analyze various trading strategies on historical cryptocurrency data through an intuitive web interface - no coding required.

![Python Version](https://img.shields.io/badge/python-3.12%2B-blue)
![License](https://img.shields.io/badge/license-MIT-green)

## Features

### 🚀 Core Capabilities

- **Multi-Cryptocurrency Support**: Backtest strategies on 5 major cryptocurrencies
  - Bitcoin (BTC-USD)
  - Ethereum (ETH-USD)
  - Binance Coin (BNB-USD)
  - Solana (SOL-USD)
  - Dogecoin (DOGE-USD)

- **5 Built-in Trading Strategies**:
  - **RSI Mean Reversion** (Recommended) - Buy oversold, sell overbought
  - **Moving Average Crossover** - Classic trend-following strategy
  - **Bollinger Bands Breakout** - Volatility-based entries
  - **MACD Strategy** - Momentum and trend confirmation
  - **Momentum Breakout** - Price momentum detection

- **Flexible Backtesting Parameters**:
  - Time periods: 1 month, 3 months, 6 months, 1 year, 2 years
  - Timeframes: Daily (1d), 4-hour (4h), Hourly (1h) candles
  - Customizable strategy parameters via interactive sliders
  - Realistic commission simulation (0.1% per trade)

### 📊 Performance Analytics

- **Comprehensive Metrics**:
  - Total Return (%)
  - Final Portfolio Value
  - Sharpe Ratio
  - Maximum Drawdown
  - Win Rate
  - Number of Trades
  - Buy & Hold Comparison

- **Interactive Visualizations**:
  - Price chart with buy/sell signals
  - Volume analysis
  - Portfolio value evolution
  - Detailed trade log with P&L tracking

### 🎯 User-Friendly Interface

- Web-based GUI powered by Streamlit
- Real-time parameter adjustment
- No programming knowledge required
- Responsive design for desktop and tablet

## Installation

### Prerequisites

- Python 3.12 or higher
- pip package manager

### Quick Start

1. **Clone the repository**:
```bash
git clone <repository-url>
cd StrategyLab
```

2. **Install dependencies**:
```bash
pip install -r requirements.txt
```

Or install manually:
```bash
pip install streamlit yfinance plotly pandas numpy
```

3. **Launch the application**:
```bash
./run_interactive.sh
```

Or directly:
```bash
streamlit run interactive_backtest.py
```

4. **Access the interface**:
Open your browser and navigate to `http://localhost:8501`

## Usage

### Basic Workflow

1. **Select a Cryptocurrency**: Choose from BTC, ETH, BNB, SOL, or DOGE
2. **Choose Time Period**: Select backtesting duration (1 month to 2 years)
3. **Select Timeframe**: Pick candle interval (1h, 4h, or 1d)
4. **Pick a Strategy**: Choose one of 5 trading strategies
5. **Adjust Parameters**: Fine-tune strategy parameters using sliders
6. **Run Backtest**: Click to execute and view results
7. **Analyze Results**: Review metrics, charts, and trade history

### Strategy Parameters

Each strategy comes with customizable parameters:

- **RSI Mean Reversion**:
  - RSI Period (default: 14)
  - Oversold Level (default: 30)
  - Overbought Level (default: 70)

- **Moving Average Crossover**:
  - Fast MA Period (default: 10)
  - Slow MA Period (default: 30)

- **Bollinger Bands**:
  - Period (default: 20)
  - Standard Deviation Multiplier (default: 2.0)

- **MACD Strategy**:
  - Fast Period (default: 12)
  - Slow Period (default: 26)
  - Signal Period (default: 9)

- **Momentum Breakout**:
  - Lookback Period (default: 20)
  - Breakout Threshold (default: 1.02)

## Project Structure

```
StrategyLab/
├── interactive_backtest.py    # Main application (all-in-one)
├── run_interactive.sh          # Launch script
├── README.md                   # This file
├── requirements.txt            # Python dependencies
└── venv/                       # Virtual environment (optional)
```

## Technical Details

### Architecture

The system follows an object-oriented design with a base strategy class:

```
StrategyBase (Base Class)
├── MAStrategy (Moving Average)
├── RSIStrategy (RSI Mean Reversion)
├── BollingerStrategy (Bollinger Bands)
├── MACDStrategy (MACD)
└── MomentumStrategy (Momentum Breakout)
```

### Data Source

- Market data fetched from Yahoo Finance via `yfinance`
- Data is cached for improved performance
- Supports multiple timeframes and historical periods

### Backtesting Engine

- Position sizing: Full capital deployment per trade
- Commission: 0.1% per transaction (buy/sell)
- Signal generation: Each strategy implements custom logic
- Performance calculation: Risk-adjusted metrics

## Performance Metrics Explained

- **Total Return**: Percentage gain/loss from initial capital
- **Sharpe Ratio**: Risk-adjusted return (higher is better)
- **Maximum Drawdown**: Largest peak-to-trough decline
- **Win Rate**: Percentage of profitable trades
- **Buy & Hold**: Baseline comparison strategy

## Use Cases

- **Education**: Learn quantitative trading concepts
- **Strategy Development**: Test and refine trading ideas
- **Parameter Optimization**: Find optimal strategy settings
- **Performance Analysis**: Evaluate historical strategy performance
- **Comparative Analysis**: Compare strategies across assets

## Important Disclaimers

⚠️ **Risk Warning**:
- This system is for educational and research purposes only
- All signals and results are for reference, not investment advice
- Past performance does not guarantee future results
- Cryptocurrency markets are highly volatile
- Never invest more than you can afford to lose
- Always conduct your own research before trading

## Requirements

### Python Dependencies

- streamlit >= 1.52.2
- yfinance >= 1.0
- plotly >= 6.5.0
- pandas >= 2.4.0
- numpy >= 2.4.0

## Contributing

Contributions are welcome! Please feel free to submit a Pull Request.

## License

This project is licensed under the MIT License - see the LICENSE file for details.

## Acknowledgments

- Built with [Streamlit](https://streamlit.io/)
- Market data from [Yahoo Finance](https://finance.yahoo.com/)
- Visualization powered by [Plotly](https://plotly.com/)

## Support

For issues, questions, or suggestions:
- Open an issue on GitHub
- Contact the maintainer

## Roadmap

Future enhancements may include:
- Additional trading strategies
- More cryptocurrencies
- Advanced risk management features
- Portfolio optimization tools
- Real-time trading integration
- Machine learning strategies

---

**Happy Backtesting!** 📈
