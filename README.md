# 📊 量化交易工具集

比特币量化交易策略回测与自动信号推送系统

## ⭐️ 新功能：交互式Web回测系统

**🎉 现在支持可视化Web界面进行回测！**

```bash
./run_interactive.sh
```

详见 [交互式回测系统使用指南](INTERACTIVE_GUIDE.md)

---

## 📁 项目文件

| 文件 | 说明 |
|------|------|
| `interactive_backtest.py` | **🆕 交互式Web回测系统**（整合所有功能，支持5币种×5策略） |
| `run_interactive.sh` | **🆕 一键启动Web界面** |
| `INTERACTIVE_GUIDE.md` | **🆕 交互式系统完整使用指南** |
| `main.py` | 基础技术分析图表（蜡烛图 + 移动平均线） |
| `main2.py` | 移动平均线策略回测脚本 |
| `strategy_optimizer.py` | 策略优化器（测试5种策略，自动寻找最优参数） |
| `multi_crypto_backtest.py` | 多币种回测脚本（RSI策略） |
| `telegram_bot.py` | Telegram 交易信号机器人 |
| `bot_config.py` | Telegram Bot 配置文件 |
| `TELEGRAM_BOT_SETUP.md` | Telegram Bot 详细设置指南 |
| `setup_telegram_bot.sh` | 一键安装和启动Telegram Bot |

## 🚀 快速开始

### 1️⃣ 技术分析可视化

查看比特币价格走势和移动平均线：

```bash
python main.py
```

### 2️⃣ 策略回测

运行单个策略的完整回测：

```bash
python main2.py
```

### 3️⃣ 策略优化（推荐）

自动测试多种策略，找出最佳盈利策略：

```bash
python strategy_optimizer.py
```

包含的策略：
- ✅ 移动平均线交叉（改进版，带趋势过滤）
- ✅ RSI 均值回归
- ✅ 布林带突破
- ✅ MACD 策略
- ✅ 动量突破

### 4️⃣ Telegram 自动信号推送（推荐）

设置后可自动监控市场并推送交易信号到手机：

**第一步：安装依赖**
```bash
pip install python-telegram-bot
```

**第二步：配置机器人**

1. 在 Telegram 搜索 `@BotFather`，创建机器人获取 Token
2. 在 Telegram 搜索 `@userinfobot`，获取你的 Chat ID
3. 编辑 `bot_config.py`，填入这两个值：

```python
BOT_TOKEN = "你的BOT_TOKEN"
CHAT_ID = "你的CHAT_ID"
```

**第三步：启动机器人**

方式1 - 使用脚本（推荐）：
```bash
./setup_telegram_bot.sh
```

方式2 - 手动启动：
```bash
python telegram_bot.py
```

详细说明请查看：[TELEGRAM_BOT_SETUP.md](TELEGRAM_BOT_SETUP.md)

## 📈 最佳策略（基于回测）

根据你的回测结果，**日线级别**最佳策略为：

### RSI(35/80) 策略

- **超卖线**: 35（RSI < 35 时买入）
- **超买线**: 80（RSI > 80 时卖出）
- **适用周期**: 1日K线（中长期交易）

这个策略已经内置在 Telegram 机器人中！

## 🎯 使用场景

### 场景1：研究和学习
```bash
# 1. 查看市场走势
python main.py

# 2. 了解策略逻辑
python main2.py
```

### 场景2：策略优化
```bash
# 测试多种策略，找出最优参数
python strategy_optimizer.py
```

### 场景3：自动监控（推荐）
```bash
# 1. 配置 Telegram Bot
# 2. 启动机器人
./setup_telegram_bot.sh

# 机器人会自动：
# ✓ 每小时检查信号
# ✓ 发现买入/卖出信号时推送到手机
# ✓ 支持命令查询市场状态
```

## 📱 Telegram 机器人命令

在 Telegram 中向你的机器人发送：

- `/start` - 查看欢迎信息
- `/status` - 查看当前市场状态（RSI、价格）
- `/signal` - 立即检查交易信号
- `/help` - 显示帮助

## ⚙️ 自定义配置

### 修改监控标的

编辑 `bot_config.py`:
```python
TICKER = "ETH-USD"  # 改为以太坊
TICKER = "AAPL"     # 改为苹果股票
```

### 修改检查频率

```python
CHECK_INTERVAL = 30   # 每30分钟检查（更频繁）
CHECK_INTERVAL = 240  # 每4小时检查（更少打扰）
```

### 修改 RSI 参数

```python
OVERSOLD = 30     # 更激进的买入
OVERBOUGHT = 70   # 更激进的卖出
```

## 📊 策略优化器使用示例

```python
# 修改 strategy_optimizer.py 底部的配置
results, data = optimize_strategies(
    ticker='BTC-USD',  # 监控标的
    period='1y',       # 回测周期：1年
    top_n=5            # 显示前5个策略
)
```

输出示例：
```
🏆 排名 #1: RSI(35/80)
──────────────────────────────────────
  参数设置: oversold=35, overbought=80
  总收益率:    45.23%
  最终资金: $14,523.00
  夏普比率:     1.85
  最大回撤:   -12.45%
  胜率:        67.50%
  交易次数:       12
```

## 🛡️ 风险提示

1. ⚠️ **所有策略信号仅供参考**，不构成投资建议
2. ⚠️ **历史表现不代表未来收益**
3. ⚠️ **加密货币波动性大**，请控制仓位
4. ⚠️ **永远不要投入无法承受损失的资金**
5. ⚠️ **建议先在模拟账户测试**

## 🔧 故障排查

### 问题1：无法安装依赖
```bash
# 使用国内镜像源
pip install -i https://pypi.tuna.tsinghua.edu.cn/simple python-telegram-bot
```

### 问题2：Telegram Bot 无响应
1. 检查是否点击了机器人的 "START" 按钮
2. 确认 BOT_TOKEN 和 CHAT_ID 正确
3. 检查网络连接

### 问题3：获取不到市场数据
1. 检查网络连接
2. Yahoo Finance 可能有访问限制，稍后重试
3. 考虑使用代理

## 📚 学习资源

- [策略优化器详解](strategy_optimizer.py) - 查看5种策略的具体实现
- [Telegram Bot 设置](TELEGRAM_BOT_SETUP.md) - 完整的机器人设置指南
- [回测逻辑](main2.py) - 了解回测引擎如何工作

## 🎓 技术指标说明

### RSI（相对强弱指数）
- **计算**: 基于14周期的价格变动
- **超卖**: RSI < 35，可能反弹
- **超买**: RSI > 80，可能回调
- **中性**: 35 < RSI < 80

### 移动平均线
- **MA5**: 5期短期均线
- **MA20**: 20期长期均线
- **金叉**: 短期上穿长期（买入信号）
- **死叉**: 短期下穿长期（卖出信号）

### MACD
- **快线**: 12期EMA
- **慢线**: 26期EMA
- **信号线**: 9期EMA
- **交叉**: 快线穿越信号线产生信号

### 布林带
- **中轨**: 20期移动平均
- **上轨**: 中轨 + 2倍标准差
- **下轨**: 中轨 - 2倍标准差
- **突破**: 价格突破轨道产生信号

## 🚀 进阶功能（未来）

- [ ] 多标的同时监控
- [ ] 策略组合优化
- [ ] 自动交易（接入交易所API）
- [ ] 风控管理（止损/止盈）
- [ ] 实时绩效报告
- [ ] Web 控制面板

## 📞 获取帮助

1. 查看各个脚本的代码注释
2. 阅读 `TELEGRAM_BOT_SETUP.md`
3. 检查日志文件 `bot.log`

## 📄 许可

本项目仅供学习和研究使用。

---

**祝交易顺利！** 📈✨
