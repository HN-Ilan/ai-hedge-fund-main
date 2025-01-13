import gradio as gr
from datetime import datetime, timedelta
from dateutil.relativedelta import relativedelta
import pandas as pd
import matplotlib.pyplot as plt
from typing import Dict, Any, List
import json
import os
import sys
from pathlib import Path

from .config import ConfigManager
from ..main import run_hedge_fund
# from backtester import Backtester
from ..utils.analysts import ANALYST_ORDER
from ..utils.display import (
    print_trading_output, 
    print_backtest_results, 
    format_trading_output,
    format_backtest_output
)
# Add project root to Python path
root_dir = str(Path(__file__).parent.parent.parent)
if root_dir not in sys.path:
    sys.path.append(root_dir)

# Local dashboard imports
from src.dashboard.config import ConfigManager

# Agent imports
from ..agents.technicals import technical_analyst_agent
from ..agents.fundamentals import fundamentals_agent
from ..agents.sentiment import sentiment_agent
from ..agents.valuation import valuation_agent
from ..agents.risk_manager import risk_management_agent
from ..agents.portfolio_manager import portfolio_management_agent

# Utility imports
from ..utils.analysts import ANALYST_ORDER
from ..utils.display import print_trading_output

# Main system imports
from ..main import run_hedge_fund
from ..backtester import Backtester

FREE_TICKERS = ["AAPL", "GOOGL", "MSFT", "NVDA", "TSLA"]
class UILogger:
    def __init__(self):
        self.logs = []
    
    def log(self, message: str, log_type: str = 'info') -> None:
        """Add a log message with timestamp."""
        timestamp = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        log_entry = [timestamp, str(message), log_type]
        self.logs.append(log_entry)
    
    def get_logs(self) -> list:
        """Get all logs as a list."""
        return self.logs
    
    def clear(self) -> None:
        """Clear all logs."""
        self.logs.clear()
def create_dashboard():
    with gr.Blocks(title="AI Hedge Fund Dashboard") as dashboard:
        config_manager = ConfigManager()
        
        with gr.Tab("Trading Setup"):
            gr.Markdown("## Trading Mode and Ticker Selection")
            
            mode = gr.Radio(
                choices=["Live Trading", "Backtesting"],
                label="Trading Mode",
                value="Live Trading"
            )
            
            with gr.Row():
                ticker_choice = gr.Radio(
                    choices=["Free Ticker", "Custom Ticker"],
                    label="Ticker Selection",
                    value="Free Ticker"
                )
                
                free_ticker = gr.Dropdown(
                    choices=FREE_TICKERS,
                    label="Free Tickers",
                    value="AAPL"
                )
                
                custom_ticker = gr.Textbox(
                    label="Custom Ticker",
                    visible=False
                )
                
                api_key = gr.Textbox(
                    label="Financial Datasets API Key",
                    visible=False,
                    type="password"
                )
            
            with gr.Row():
                start_date = gr.Textbox(
                    label="Start Date (YYYY-MM-DD)",
                    value=(datetime.now() - relativedelta(months=3)).strftime("%Y-%m-%d")
                )
                end_date = gr.Textbox(
                    label="End Date (YYYY-MM-DD)",
                    value=datetime.now().strftime("%Y-%m-%d")
                )
            
            initial_capital = gr.Number(
                value=100000,
                label="Initial Capital ($)"
            )
        
        with gr.Tab("Risk Parameters"):
            gr.Markdown("## Risk Management Settings")
            
            max_position = gr.Slider(
                minimum=0.05,
                maximum=0.50,
                value=0.20,
                label="Maximum Position Size (% of Portfolio)"
            )
            
            stop_loss = gr.Slider(
                minimum=0.05,
                maximum=0.20,
                value=0.10,
                label="Stop Loss (%)"
            )
            
            max_drawdown = gr.Slider(
                minimum=0.10,
                maximum=0.40,
                value=0.20,
                label="Maximum Drawdown (%)"
            )
        
        with gr.Tab("Technical Indicators"):
            gr.Markdown("## Technical Analysis Parameters")
            
            with gr.Row():
                ma_short = gr.Number(value=8, label="Short MA Period")
                ma_medium = gr.Number(value=21, label="Medium MA Period")
                ma_long = gr.Number(value=55, label="Long MA Period")
            
            with gr.Row():
                rsi_oversold = gr.Number(value=30, label="RSI Oversold")
                rsi_overbought = gr.Number(value=70, label="RSI Overbought")
                volatility = gr.Slider(
                    minimum=0.10,
                    maximum=0.50,
                    value=0.30,
                    label="Volatility Threshold"
                )
        
        with gr.Tab("Fundamental & Valuation"):
            gr.Markdown("## Fundamental Analysis Parameters")
            
            with gr.Row():
                min_roe = gr.Slider(
                    minimum=0.05,
                    maximum=0.30,
                    value=0.15,
                    label="Minimum ROE"
                )
                min_margin = gr.Slider(
                    minimum=0.05,
                    maximum=0.30,
                    value=0.10,
                    label="Minimum Profit Margin"
                )
                max_debt = gr.Slider(
                    minimum=0.5,
                    maximum=4.0,
                    value=2.0,
                    label="Maximum Debt/Equity"
                )
            
            gr.Markdown("## Valuation Parameters")
            with gr.Row():
                req_return = gr.Slider(
                    minimum=0.08,
                    maximum=0.25,
                    value=0.15,
                    label="Required Return"
                )
                growth_rate = gr.Slider(
                    minimum=0.02,
                    maximum=0.15,
                    value=0.05,
                    label="Growth Rate"
                )
                safety_margin = gr.Slider(
                    minimum=0.15,
                    maximum=0.40,
                    value=0.25,
                    label="Margin of Safety"
                )
        
        with gr.Tab("Analysts"):
            gr.Markdown("## Select Active Analysts")
            analyst_choices = gr.CheckboxGroup(
                choices=[display for display, _ in ANALYST_ORDER],
                label="Active Analysts",
                value=[display for display, _ in ANALYST_ORDER]
            )
        
        # Run button and outputs
        run_button = gr.Button("Run Analysis")
        
        with gr.Row():
            with gr.Column():
                signals_output = gr.Dataframe(
                    headers=["Analyst", "Signal", "Confidence"],
                    label="Analyst Signals"
                )
                decision_output = gr.Dataframe(
                    headers=["Metric", "Value"],
                    label="Trading Decision"
                )
            
            with gr.Column():
                plot_output = gr.Plot(label="Portfolio Performance")
                status_output = gr.Textbox(label="Status")
        # Initialize logger at the start of create_dashboard
        logger = UILogger()

        # Add this after your existing tabs
        with gr.Tab("System Logs"):
            with gr.Row():
                log_output = gr.Dataframe(
                    headers=["Timestamp", "Message", "Type"],
                    label="System Logs",
                    interactive=False,
                    wrap=True
                )
            with gr.Column(scale=1):
                clear_logs = gr.Button("Clear Logs")

        def clear_log_display():
            """Clear the log display."""
            logger.clear()
            return logger.get_logs()
        
        def update_ticker_visibility(choice):
            return {
                free_ticker: gr.update(visible=choice == "Free Ticker"),
                custom_ticker: gr.update(visible=choice == "Custom Ticker"),
                api_key: gr.update(visible=choice == "Custom Ticker")
            }
        
        def save_and_run(
            mode, ticker_choice, free_ticker, custom_ticker, api_key,
            start_date, end_date, initial_capital, max_position,
            stop_loss, max_drawdown, ma_short, ma_medium, ma_long,
            rsi_oversold, rsi_overbought, volatility, min_roe,
            min_margin, max_debt, req_return, growth_rate,
            safety_margin, selected_analysts,progress=gr.Progress() # Add progress bar

        ):
            try:
                logger.log("Starting analysis...", "info")
                # Save configuration
                config = {
                    "max_position_size": float(max_position),
                    "stop_loss": float(stop_loss),
                    "max_drawdown": float(max_drawdown),
                    "ma_short_period": int(ma_short),
                    "ma_medium_period": int(ma_medium),
                    "ma_long_period": int(ma_long),
                    "rsi_oversold": int(rsi_oversold),
                    "rsi_overbought": int(rsi_overbought),
                    "volatility_threshold": float(volatility),
                    "min_roe": float(min_roe),
                    "min_profit_margin": float(min_margin),
                    "max_debt_equity": float(max_debt),
                    "required_return": float(req_return),
                    "growth_rate": float(growth_rate),
                    "margin_of_safety": float(safety_margin)
                }
                
                config_manager.save_config(config)
                logger.log("Configuration saved successfully", "success")

                # Set up ticker and API key
                ticker = free_ticker if ticker_choice == "Free Ticker" else custom_ticker
                if api_key and ticker_choice == "Custom Ticker":
                    os.environ["FINANCIAL_DATASETS_API_KEY"] = api_key
                
                # Convert analyst display names to values
                analyst_map = dict(ANALYST_ORDER)
                selected_analyst_values = [
                    analyst_map[display] for display in selected_analysts
                ]
                
                portfolio = {"cash": float(initial_capital), "stock": 0}
                
                if mode == "Live Trading":
                    logger.log("Starting live trading analysis...", "info")
                    result = run_hedge_fund(
                        ticker=ticker,
                        start_date=start_date,
                        end_date=end_date,
                        portfolio=portfolio,
                        show_reasoning=True,
                        selected_analysts=selected_analyst_values
                    )
                    
                    # Format signals and decisions for UI tables
                    signals_data = [
                        [
                            agent.replace("_agent", "").title(),
                            signal.get("signal", "").upper(),
                            f"{signal.get('confidence', 0)}%"
                        ]
                        for agent, signal in result["analyst_signals"].items()
                    ]
                    
                    decision = result["decision"]
                    decision_data = [
                        ["Action", decision["action"].upper()],
                        ["Quantity", decision["quantity"]],
                        ["Confidence", f"{decision['confidence']}%"]
                    ]
                    # Add formatted output to logs
                    formatted_output = format_trading_output(result)
                    logger.log(formatted_output, "info")
                    logger.log("Live trading analysis completed", "success")
                    
                    return (
                        signals_data,
                        decision_data,
                        None,  # No plot for live trading
                        "Live trading analysis completed",
                        logger.get_logs()
                    )
                else:
                    logger.log("Starting backtesting...", "info")
                    backtester = Backtester(
                        agent=run_hedge_fund,
                        ticker=ticker,
                        start_date=start_date,
                        end_date=end_date,
                        initial_capital=float(initial_capital),
                        selected_analysts=selected_analyst_values,
                        progress=progress,  # Add progress callback
                        logger=logger  # Add logger
                    )
                    
                    # Run backtest with progress updates
                    progress(0, desc="Starting backtest...")
                    backtester.run_backtest()
                    progress(1, desc="Backtest completed")
                    performance_df = backtester.analyze_performance()
                    # Format backtest results for logs
                    formatted_backtest = format_backtest_output(backtester.get_table_rows())
                    logger.log(formatted_backtest, "info")
                    # Create performance plot
                    fig = plt.figure(figsize=(12, 6))
                    performance_df["Portfolio Value"].plot(
                        title="Portfolio Value Over Time"
                    )
                    plt.ylabel("Portfolio Value ($)")
                    plt.xlabel("Date")
                    
                    signals_data = []  # Final day's signals
                    decision_data = [
                        ["Total Return", f"{backtester.total_return * 100:.2f}%"],
                        ["Sharpe Ratio", f"{backtester.sharpe_ratio:.2f}"],
                        ["Max Drawdown", f"{backtester.max_drawdown * 100:.2f}%"]
                    ]
                    logger.log("Backtesting completed", "success")
                    return (
                        signals_data,
                        decision_data,
                        fig,
                        "Backtesting completed",
                        logger.get_logs()
                    )
            
            except Exception as e:
                logger.log(f"Error saving configuration: {str(e)}", "error")
                return (
                    [],
                    [],
                    None,
                    f"Error: {str(e)}",
                    logger.get_logs()  # log_output
                )
        
        # Connect components
        ticker_choice.change(
            fn=update_ticker_visibility,
            inputs=ticker_choice,
            outputs=[free_ticker, custom_ticker, api_key]
        )
        
        run_button.click(
            fn=save_and_run,
            inputs=[
                mode, ticker_choice, free_ticker, custom_ticker, api_key,
                start_date, end_date, initial_capital, max_position,
                stop_loss, max_drawdown, ma_short, ma_medium, ma_long,
                rsi_oversold, rsi_overbought, volatility, min_roe,
                min_margin, max_debt, req_return, growth_rate,
                safety_margin, analyst_choices
            ],
            outputs=[signals_output, decision_output, plot_output, status_output, log_output]
        )

        clear_logs.click(
            fn=clear_log_display,
            inputs=[],
            outputs=[log_output]
        )
        # Add periodic log update
        dashboard.load(
            fn=lambda: logger.get_logs(),
            inputs=None,
            outputs=log_output,
            every=1  # Update every second
        )    
    return dashboard

if __name__ == "__main__":
    print(f"Current working directory: {os.getcwd()}")
    print(f"Python path: {sys.path}")
    dashboard = create_dashboard()
    dashboard.launch()