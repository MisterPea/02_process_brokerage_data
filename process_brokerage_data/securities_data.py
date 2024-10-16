import urllib
from process_brokerage_data.account_methods import AccountMethods
from urllib.parse import quote
import requests
import datetime
from process_brokerage_data.securities_data_types import (PriceHistoryOptions, IndexSymbolType, MoverSortType, MoversFreqType,
                                   MarketTimeType)

class SecuritiesData:
    def __init__(self):
        self.data_url = "https://api.schwabapi.com/marketdata/v1"
        self.account = AccountMethods()

    @staticmethod
    def convert_to_ms_epoch(yyyy_mm_dd: str):
        """Converts a date string in YYYY-MM-DD format to milliseconds since the epoch."""
        date_object = datetime.datetime.strptime(yyyy_mm_dd, "%Y-%m-%d")
        ms_epoch = int(date_object.timestamp() * 1000)
        return ms_epoch

    def create_header(self):
        """Method to prepare header with valid token"""
        token = self.account.get_token()
        headers = {
            "accept": "application/json",
            "Authorization": f'Bearer {token["access_token"]}',
        }
        return headers

    def get_quotes(self, symbols: list[str]):
        """Method to retrieve multiple quotes"""
        url = f"{self.data_url}/quotes?symbols={"".join([quote(s) for s in symbols])}&fields=quote&2Cfundamental&indicative=false"
        headers = self.create_header()
        response = requests.get(url, headers=headers)

        # Check for success
        if response.status_code == 200:
            return response.json()
        else:
            print(f"Error fetching market data: {response.status_code}, {response.text}")
            return None

    def price_history(self, symbol: str, price_history_options: PriceHistoryOptions):
        """Method to retrieve the price history of a specific instrument"""
        start_date = price_history_options.get('start_date', None)
        end_date = price_history_options.get('end_date', None)
        period_type = price_history_options.get('period_type', 'ytd')
        period = price_history_options.get('period', 1)
        frequency_type = price_history_options.get('frequency_type', 'daily')
        frequency = price_history_options.get('frequency', 1)
        need_extended_hours_data = price_history_options.get('extended_hours', False)
        need_previous_close = price_history_options.get('need_previous_close', True)

        # Correct the list of strings for joining
        joined_options = "&".join([
            f"symbol={symbol}",
            f"periodType={period_type}",
            f"period={period}",
            f"frequencyType={frequency_type}",
            f"frequency={frequency}",
            f"needExtendedHoursData={need_extended_hours_data}",
            f"needPreviousClose={need_previous_close}"
        ])

        if start_date:
            joined_options += f"&startDate={self.convert_to_ms_epoch(start_date)}"
        if end_date:
            joined_options += f"&endDate={self.convert_to_ms_epoch(end_date)}"

        url = f"{self.data_url}/pricehistory?{joined_options}"
        headers = self.create_header()
        response = requests.get(url, headers=headers)

        # Check for success
        if response.status_code == 200:
            return response.json()
        else:
            print(f"Error fetching price history: {response.status_code}, {response.text}")
            return None

    def get_movers(self, symbol: IndexSymbolType, sort_by: MoverSortType, freq: MoversFreqType):
        """This method should find the movers for the index symbol, but doesn't seem to work-This is a Schwab issue"""
        url = f"{self.data_url}/movers/{urllib.parse.quote(symbol)}?sort={sort_by}&frequency={urllib.parse.quote(f"{freq}")}"
        print("**",url)
        headers = self.create_header()

        response = requests.get(url, headers=headers)

        if response.status_code == 200:
            return response.json()
        else:
            print(f"Error fetching movers: {response.status_code}, {response.text}")
            return None

    def get_market_hours(self, market: MarketTimeType, date: str | None):
        url = f"{self.data_url}/markets/{market}{f"?date={date}" if date else ""}"
        headers = self.create_header()

        response = requests.get(url, headers=headers)

        if response.status_code == 200:
            return response.json()
        else:
            print(f"Error fetching market hours: {response.status_code}, {response.text}")


#
# options: PriceHistoryOptions = {
#     'period_type': "year",
#     "period": 1,
#     "frequency_type": "daily",
#     "frequency": 1,
#     "extended_hours": False,
#     "need_previous_close": True,
#     "start_date": "2020-01-01",
#     "end_date": "2020-12-31",
# }
#
#
# spy_out = SecuritiesData().price_history("SPY", price_history_options=options)
# # movers_out = SecuritiesData().get_movers(symbol="EQUITY_ALL", sort_by="PERCENT_CHANGE_DOWN", freq=10)
# print(json.dumps(spy_out, indent=2))
