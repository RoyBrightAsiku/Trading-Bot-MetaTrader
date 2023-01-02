import MetaTrader5 as mt5
import pandas as pd
import numpy as np
import plotly.graph_objects as go
from IPython.display import display
import time
from datetime import datetime, timedelta

mt5.initialize()

status = 'open'
symbols = mt5.symbols_get()

price = mt5.symbol_info_tick('EURUSD')
print(datetime.fromtimestamp(price.time))
print(price.bid)


class SupportResistance:
    def __init__(self):
        self.status = None
        self.symbol = 'EURUSD'
        self.year = int(str(datetime.now())[:-22])
        self.month = int(str(datetime.now())[5:-19])
        self.day = int(str(datetime.now())[8:-16])
        self.price = mt5.symbol_info_tick(self.symbol)
        self.timeframe = mt5.TIMEFRAME_M1
        pass

    def checkgraph(self):
        while self.status is None:
            start_dt = datetime(self.year, self.month, self.day)
            end_dt = datetime.now()

            bars = mt5.copy_rates_range(self.symbol, self.timeframe, start_dt, end_dt)
            df = pd.DataFrame(bars)[['time', 'open', 'high', 'low', 'close']]
            df['time'] = pd.to_datetime(df['time'], unit='s')

            fig = go.Figure(data=go.Ohlc(
                x=df['time'], open=df['open'], high=df['high'], low=df['low'], close=df['close']))

            def specify_candle_type(open_price, close_price):
                if close_price > open_price:
                    return 'bullish'
                elif close_price < open_price:
                    return 'bearish'
                else:
                    return 'doji'

            df['candle_type'] = np.vectorize(specify_candle_type)(df['open'], df['close'])

            df['candle_1'] = df['candle_type'].shift(1)
            df['candle_2'] = df['candle_type'].shift(2)
            df['candle_3'] = df['candle_type'].shift(3)
            df['prev_close'] = df['close'].shift(1)

            df_bullish = df[
                (df['candle_1'] == 'bullish') & (df['candle_2'] == 'bullish') & (df['candle_3'] == 'bullish')].copy()
            df_bullish['points'] = df_bullish['close'] - df['prev_close']

            df_bearish = df[
                (df['candle_1'] == 'bearish') & (df['candle_2'] == 'bearish') & (df['candle_3'] == 'bearish')].copy()
            df_bullish['points'] = df_bullish['close'] - df['prev_close']
            print(df_bearish)
            print(df_bullish)

            last_value = str(df_bearish['time'].tail(1))[6:-37]
            time_now = str(datetime.now())[:-10]
            print(last_value)
            print(time_now)
            print(last_value == time_now)
            if last_value == time_now:
                self.status = 'open_bearish'
                trade = SupportResistance()
                trade.buy()

            else:
                last_value = str(df_bullish['time'].tail(1))[6:-37]
                time_now = str(datetime.now())[:-10]
                print(last_value)
                print(time_now)
                print(last_value == time_now)
                if last_value == time_now:
                    self.status = 'open_bullish'
                    SupportResistance.sell()
                    trade = SupportResistance()
                    trade.buy()

            time.sleep(5)
        pass

    def analysis(self):
        lines = []
        lines = sorted(lines)
        lines_btn = []
        iterator = 0
        least_difference = lines[0] - self.price.bid

        while iterator < len(lines):
            least_difference_test = lines[iterator] - self.price.bid
            if 0 < least_difference_test <= least_difference:
                least_difference = least_difference_test
            iterator += 1

        for line in lines:
            difference = line - self.price.bid
            if difference == least_difference:
                lines_btn.append(line)
                break
        else:
            SupportResistance().closingpositions()
            pass

        iterator = 0
        least_difference = lines[0] - self.price.bid
        while iterator < len(lines):
            least_difference_test = lines[iterator] - self.price.bid
            if least_difference_test <= least_difference and least_difference_test < 0:
                least_difference = least_difference_test
            iterator += 1

        for line in lines:
            difference = line - self.price.bid
            if difference == least_difference:
                lines_btn.append(line)
                break
        else:
            SupportResistance().closingpositions()
            pass

        start_dt = datetime(self.year, self.month, self.day)
        end_dt = datetime.now()

        bars = mt5.copy_rates_range(self.symbol, self.timeframe, start_dt, end_dt)
        df = pd.DataFrame(bars)[['time', 'open', 'high', 'low', 'close']]
        df['time'] = pd.to_datetime(df['time'], unit='s')
        df['sma_200'] = df['open'].rolling(200).mean()

        while lines_btn[0] <= self.price.bid <= lines_btn[1] and lines_btn[0] <= float(df['sma_200'].tail(1)) <= \
                lines_btn[1]:
            start_dt = datetime(self.year, self.month, self.day)
            end_dt = datetime.now()

            bars = mt5.copy_rates_range(self.symbol, self.timeframe, start_dt, end_dt)
            df = pd.DataFrame(bars)[['time', 'open', 'high', 'low', 'close']]
            df['time'] = pd.to_datetime(df['time'], unit='s')
            df['sma_200'] = df['open'].rolling(200).mean()
            print('check 3')
            continue
        else:
            SupportResistance().closingpositions()
        pass

    def buy(self):
        request = {
            'action': mt5.TRADE_ACTION_DEAL,
            'symbol': self.symbol,
            'volume': 0.1,
            'type': mt5.ORDER_TYPE_BUY,
            'price': mt5.symbol_info_tick(self.symbol).ask,
            'deviation': 20,
            'magic': 100,
            'comment': 'python script open',
            'type-time': mt5.ORDER_TIME_GTC,
            'type_filling': mt5.ORDER_FILLING_IOC
        }

        mt5.order_send(request)
        self.status = 'open_bullish'
        SupportResistance().analysis()
        pass

    def sell(self):
        request = {
            'action': mt5.TRADE_ACTION_DEAL,
            'symbol': self.symbol,
            'volume': 0.1,
            'type': mt5.ORDER_TYPE_SELL,
            'price': mt5.symbol_info_tick(self.symbol).bid,
            'deviation': 20,
            'magic': 100,
            'comment': 'python script open',
            'type-time': mt5.ORDER_TIME_GTC,
            'type_filling': mt5.ORDER_FILLING_IOC
        }

        mt5.order_send(request)
        self.status = 'open_bullish'
        SupportResistance().analysis()
        pass

    def closingpositions(self):
        positions = mt5.positions_get()

        for position in positions:
            tick = mt5.symbol_info_tick(position.self.symbol)

            request = {
                'action': mt5.TRADE_ACTION_DEAL,
                'position': position.ticket,
                'symbol': position.symbol,
                'volume': position.volume,
                'type': mt5.ORDER_TYPE_SELL if position.type == 0 else mt5.ORDER_TYPE_BUY,
                'price': tick.ask if position.type == 1 else tick.bid,
                'deviation': 20,
                'magic': 100,
                'comment': 'python script open',
                'type-time': mt5.ORDER_TIME_GTC,
                'type_filling': mt5.ORDER_FILLING_IOC
            }
            mt5.order_send(request)

        self.status = None
        print('check 4')
        SupportResistance().checkgraph()
        pass


trade = SupportResistance()
trade.checkgraph()
