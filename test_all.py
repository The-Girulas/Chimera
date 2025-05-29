import json
import os
import re
import shutil
import subprocess
from collections import defaultdict
from datetime import datetime

import pandas as pd


def clean_previous_files():
    """Clean previous backtest results and downloaded data files."""
    print("Cleaning previous files...")

    # Clean backtest results
    results_dir = os.path.join("user_data", "backtest_results")
    if os.path.exists(results_dir):
        print(f"Cleaning directory: {results_dir}")
        for file in os.listdir(results_dir):
            file_path = os.path.join(results_dir, file)
            try:
                if os.path.isfile(file_path):
                    os.unlink(file_path)
                    print(f"Deleted file: {file_path}")
                elif os.path.isdir(file_path):
                    shutil.rmtree(file_path)
                    print(f"Deleted directory: {file_path}")
            except Exception as e:
                print(f"Error deleting {file_path}: {e}")

    # Clean downloaded data files in data/binance/futures
    data_dir = os.path.join("user_data", "data", "binance", "futures")
    if os.path.exists(data_dir):
        print(f"Cleaning directory: {data_dir}")
        for file in os.listdir(data_dir):
            file_path = os.path.join(data_dir, file)
            try:
                if os.path.isfile(file_path):
                    os.unlink(file_path)
                    print(f"Deleted file: {file_path}")
                elif os.path.isdir(file_path):
                    shutil.rmtree(file_path)
                    print(f"Deleted directory: {file_path}")
            except Exception as e:
                print(f"Error deleting {file_path}: {e}")

    print("Cleaning completed.")


def extract_timeframe(file_path):
    """Extract timeframe from a strategy file."""
    with open(file_path, "r") as file:
        content = file.read()
        # Look for timeframe parameter in the strategy file
        match = re.search(r'timeframe\s*=\s*[\'"]([^\'"]+)[\'"]', content)
        if match:
            return match.group(1)
    return None


def get_strategies_by_timeframe():
    """Get all strategies and group them by timeframe."""
    strategies_dir = os.path.join("user_data", "strategies")
    strategies_by_timeframe = defaultdict(list)

    # Check if directory exists
    if not os.path.exists(strategies_dir):
        print(f"Error: Directory {strategies_dir} not found.")
        return {}

    # Iterate through strategy files
    for file in os.listdir(strategies_dir):
        if file.endswith(".py") and not file.startswith("__"):
            file_path = os.path.join(strategies_dir, file)
            strategy_name = os.path.splitext(file)[0]

            # Extract timeframe from strategy file
            timeframe = extract_timeframe(file_path)
            if timeframe:
                strategies_by_timeframe[timeframe].append(strategy_name)
            else:
                print(f"Warning: Could not determine timeframe for {strategy_name}")

    # Print summary of found strategies
    print(
        f"Found {sum(len(s) for s in strategies_by_timeframe.values())} strategies across {len(strategies_by_timeframe)} timeframes"
    )

    return strategies_by_timeframe


def download_data_for_timeframes(strategies_by_timeframe):
    """Download data for each timeframe."""
    for timeframe in strategies_by_timeframe:
        print(f"Downloading data for timeframe {timeframe}...")
        # Just use freqtrade command
        download_cmd = f"freqtrade download-data --days 1      900 --timeframes {timeframe} --trading-mode futures"
        try:
            subprocess.run(download_cmd, shell=True, check=True)
            print(f"Data download completed for {timeframe}")
        except subprocess.CalledProcessError as e:
            print(f"Error downloading data for timeframe {timeframe}: {e}")


def extract_performance_from_output(output_text, strategy_name):
    """Extract performance metrics from backtest output, focusing on performance by pair."""
    # Dictionary to store performance data
    pairs_performance = {}

    # Look for BACKTESTING REPORT section which contains pair performance
    # The pattern needs to match the specific table format used in freqtrade output
    section_start = output_text.find("BACKTESTING REPORT")
    section_end = output_text.find("LEFT OPEN TRADES REPORT", section_start)

    if section_start != -1 and section_end != -1:
        table_section = output_text[section_start:section_end]
        lines = table_section.split("\n")

        # Find the lines with actual data (not headers or separators)
        for line in lines:
            # Skip lines without actual data
            if "│" not in line and "|" not in line:
                continue

            # If this is a row with trade data, extract the pair and profit %
            parts = line.split("│") if "│" in line else line.split("|")
            parts = [p.strip() for p in parts if p.strip()]

            # Check if we have enough parts and the line looks like a data row
            if len(parts) >= 5:
                pair_name = parts[0]

                # Skip header rows or invalid data
                if pair_name in ["Pair", "PAIR", ""] or "━" in pair_name:
                    continue

                try:
                    # Extract tot_profit_pct (5th column)
                    tot_profit_pct = parts[4]

                    # Convert percentage to float
                    # (sometimes the percentage has a '%' sign, sometimes not)
                    tot_profit_pct = tot_profit_pct.replace("%", "").strip()
                    tot_profit_pct = float(tot_profit_pct)

                    # Store in our results dictionary
                    pairs_performance[pair_name] = tot_profit_pct
                except (ValueError, IndexError) as e:
                    print(f"Error parsing profit percentage for {pair_name}: {e}")
    else:
        print(f"Could not find BACKTESTING REPORT section for {strategy_name}")

    # If we couldn't extract data from the table, try to get at least the TOTAL from SUMMARY METRICS
    if not pairs_performance or "TOTAL" not in pairs_performance:
        total_profit_pattern = r"Total profit %\s*[│|]\s*([-\d.]+)%"
        total_profit_match = re.search(total_profit_pattern, output_text)

        if total_profit_match:
            try:
                total_profit = float(total_profit_match.group(1).strip())
                pairs_performance["TOTAL"] = total_profit
            except ValueError:
                pass

    # If we still don't have data, try the STRATEGY SUMMARY section
    if not pairs_performance:
        strategy_pattern = (
            rf"{strategy_name}\s*[│|]\s*\d+\s*[│|]\s*[-\d.]+\s*[│|]\s*[-\d.]+\s*[│|]\s*([-\d.]+)"
        )
        strategy_match = re.search(strategy_pattern, output_text)
        if strategy_match:
            try:
                total_profit = float(strategy_match.group(1).strip())
                pairs_performance["TOTAL"] = total_profit
            except ValueError:
                pass

    return pairs_performance


def run_backtests(strategies_by_timeframe):
    """Run backtesting for each timeframe group with all strategies in parallel."""
    all_results = {}
    performance_data = {}

    for timeframe, strategies in strategies_by_timeframe.items():
        if not strategies or len(strategies) == 0:
            continue

        print(f"\n{'=' * 80}")
        print(
            f"Running backtesting for timeframe {timeframe} with strategies: {', '.join(strategies)}"
        )
        print(f"{'=' * 80}")

        # Build the strategy list argument
        strategy_list = " ".join(strategies)

        # Run backtest with all strategies for this timeframe in parallel
        command = f"freqtrade backtesting --timerange 20230101-20240427 --timeframe {timeframe} --strategy-list {strategy_list} "

        # Execute the backtesting command
        try:
            result = subprocess.run(command, shell=True, check=True, capture_output=True, text=True)
            output = result.stdout
            all_results[f"{timeframe}_combined"] = output
            print(output)

            # Extract performance data for each strategy
            # Process the output to identify each strategy's results
            strategy_sections = re.split(r"Result for strategy (\w+)", output)

            if len(strategy_sections) > 1:
                # First item is text before any strategy result
                for i in range(1, len(strategy_sections), 2):
                    if i + 1 < len(strategy_sections):
                        strategy_name = strategy_sections[i].strip()
                        strategy_output = strategy_sections[i + 1]

                        # Extract performance for this strategy
                        strategy_performance = extract_performance_from_output(
                            strategy_output, strategy_name
                        )
                        if strategy_performance:
                            performance_data[strategy_name] = strategy_performance

        except subprocess.CalledProcessError as e:
            print(f"Error running backtest for timeframe {timeframe}: {e}")
            # If parallel execution fails, fall back to running each strategy individually
            print("Falling back to individual strategy execution...")
            for strategy in strategies:
                command = f"freqtrade backtesting --timerange 20230101-20240427 --strategy {strategy} --timeframe {timeframe} "

                print(f"\nRunning individual backtest for strategy: {strategy}")

                try:
                    result = subprocess.run(
                        command, shell=True, check=True, capture_output=True, text=True
                    )
                    output = result.stdout
                    all_results[f"{timeframe}_{strategy}"] = output
                    print(output)

                    # Extract performance data
                    strategy_performance = extract_performance_from_output(output, strategy)
                    if strategy_performance:
                        performance_data[strategy] = strategy_performance

                except subprocess.CalledProcessError as e:
                    print(
                        f"Error running backtest for timeframe {timeframe} and strategy {strategy}: {e}"
                    )

    return all_results, performance_data


def save_results_to_csv(performance_data, file_path, strategies_by_timeframe):
    """Save performance data to CSV with strategies as rows and pairs as columns."""
    if not performance_data:
        print("No performance data to save.")
        return False

    # Create a set of all crypto pairs (excluding 'TOTAL')
    all_pairs = set()
    for strategy_data in performance_data.values():
        for pair in strategy_data.keys():
            if pair != "TOTAL":  # Exclude TOTAL from pairs list
                all_pairs.add(pair)

    # Sort pairs alphabetically for better readability
    all_pairs = sorted(list(all_pairs))

    # Create a dictionary to store strategy and timeframe info
    strategy_timeframes = {}
    for timeframe, strategies in strategies_by_timeframe.items():
        for strategy in strategies:
            strategy_timeframes[strategy] = timeframe

    # Create DataFrame
    df = pd.DataFrame(index=performance_data.keys(), columns=["Timeframe"] + all_pairs + ["TOTAL"])

    # Fill DataFrame with performance data
    for strategy, pairs_data in performance_data.items():
        # Add timeframe information
        if strategy in strategy_timeframes:
            df.loc[strategy, "Timeframe"] = strategy_timeframes[strategy]

        # Add performance for each pair
        for pair, profit in pairs_data.items():
            if pair in all_pairs or pair == "TOTAL":
                df.loc[strategy, pair] = profit

    # Replace NaN with zeros for better readability
    df = df.fillna(0)

    # Sort strategies by total return (if available)
    if "TOTAL" in df.columns:
        df = df.sort_values(by="TOTAL", ascending=False)

    # Save to CSV
    df.to_csv(file_path)
    print(f"Performance data saved to {file_path}")

    # Also save a formatted version for better human readability
    formatted_path = file_path.replace(".csv", "_formatted.csv")
    df_formatted = df.copy()
    for col in df_formatted.columns:
        if col != "Timeframe":
            df_formatted[col] = df_formatted[col].apply(
                lambda x: f"{x:.2f}%" if isinstance(x, (int, float)) else x
            )
    df_formatted.to_csv(formatted_path)
    print(f"Formatted performance data saved to {formatted_path}")

    # Create a version where negative values are replaced with empty strings
    positive_only_path = file_path.replace(".csv", "_positive_only.csv")
    df_positive = df.copy()
    for col in df_positive.columns:
        if col != "Timeframe":
            df_positive[col] = df_positive[col].apply(
                lambda x: x if isinstance(x, (int, float)) and x > 0 else ""
            )
    df_positive.to_csv(positive_only_path)
    print(f"Positive-only performance data saved to {positive_only_path}")

    return True


def save_results(backtest_results, performance_data, strategies_by_timeframe):
    """Save backtest results to files."""
    # Create a directory for results if it doesn't exist
    results_dir = os.path.join("user_data", "backtest_results")
    os.makedirs(results_dir, exist_ok=True)

    # Timestamp for filenames
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")

    # Save raw results
    for timeframe_strategy, result in backtest_results.items():
        result_file = os.path.join(
            results_dir, f"backtest_result_{timeframe_strategy}_{timestamp}.txt"
        )
        with open(result_file, "w") as f:
            f.write(result)

    # Save ALL performance data to CSV, not just positive ones
    if performance_data:
        csv_file = os.path.join(results_dir, f"performance_results_{timestamp}.csv")
        saved = save_results_to_csv(performance_data, csv_file, strategies_by_timeframe)
        if not saved:
            print("No performance data was saved to CSV")
    else:
        print("No performance data to save.")

    print(f"Results saved to {results_dir}")


def main():
    """Main function to run the entire process."""
    # First clean previous files
    clean_previous_files()

    print("Starting strategy analysis...")

    # Step 1: Analyze strategies and group by timeframe
    print("Analyzing strategies and grouping by timeframe...")
    strategies_by_timeframe = get_strategies_by_timeframe()

    if not strategies_by_timeframe:
        print("No strategies found or could not determine timeframes.")
        return

    # Print summary of strategy grouping
    print("\nStrategy grouping result:")
    for timeframe, strategies in strategies_by_timeframe.items():
        print(f"Timeframe {timeframe}: {', '.join(strategies)}")

    # Step 2: Download data for each timeframe
    print("\nDownloading data for backtesting...")
    download_data_for_timeframes(strategies_by_timeframe)

    # Step 3: Run backtesting for each timeframe group
    print("\nRunning backtests...")
    backtest_results, performance_data = run_backtests(strategies_by_timeframe)

    # Step 4: Save results
    save_results(backtest_results, performance_data, strategies_by_timeframe)

    print("\nBacktesting process completed!")


if __name__ == "__main__":
    main()
