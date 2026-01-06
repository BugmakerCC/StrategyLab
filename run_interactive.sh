#!/bin/bash
# 启动交互式回测系统

echo "======================================"
echo "  加密货币量化回测系统"
echo "======================================"
echo ""

# 检查 streamlit 是否安装
if ! command -v streamlit &> /dev/null; then
    echo "❌ Streamlit 未安装"
    echo "正在安装依赖..."
    pip install streamlit yfinance plotly pandas numpy
    echo ""
fi

echo "✅ 准备就绪"
echo "🚀 启动 Web 应用..."
echo ""
echo "访问地址: http://localhost:8501"
echo "按 Ctrl+C 停止服务"
echo ""

# 启动应用
streamlit run interactive_backtest.py
