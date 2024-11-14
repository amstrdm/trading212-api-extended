import logging
from datetime import datetime
import requests
from requests.exceptions import HTTPError


class Trading212:
    """Rest API client for Trading212"""

    def __init__(self, api_key: str, demo: bool = True):
        """ """
        self._api_key = api_key
        self.host = (
            "https://live.trading212.com" if demo else "https://live.trading212.com"
        )

    def _get(self, endpoint: str, params=None, api_version: str = "v0"):
        return self._process_response(
            requests.get(
                f"{self.host}/api/{api_version}/{endpoint}",
                headers={"Authorization": self._api_key},
                params=params,
            )
        )

    def _post(self, endpoint: str, data: dict, api_version: str = "v0"):
        return self._process_response(
            requests.post(
                f"{self.host}/api/{api_version}/{endpoint}",
                headers={"Authorization": self._api_key},
                data=data,
            )
        )

    def _get_url(
        self,
        url,
    ):
        return self._process_response(
            requests.get(
                f"{self.host}/{url}",
                headers={"Authorization": self._api_key},
            )
        )

    def _delete_url(
        self,
        url,
    ):
        return self._process_response(
            requests.delete(
                f"{self.host}/{url}",
                headers={"Authorization": self._api_key},
            )
        )

    @staticmethod
    def _process_response(resp):
        try:
            resp.raise_for_status()
        except HTTPError as http_err:
            logging.error(resp.text)
            raise http_err

        return resp.json()

    def _process_items(self, response):
        res = []
        res += response["items"]
        while next_page := response.get("nextPagePath"):
            response = self._get_url(next_page)
            res += response["items"]

        return res

    @staticmethod
    def _validate_time_validity(time_validity: str):
        if time_validity not in ["GTC", "DAY"]:
            raise ValueError("time_validity must be one of GTC or DAY")

    @staticmethod
    def _validate_date(date_text: str):
        try:
            # Attempt to parse the date string
            datetime.strptime(date_text, "%Y-%m-%dT%H:%M:%SZ")
        except ValueError:
            raise ValueError("Incorrect date format, should be YYYY-MM-DDTHH:MM:SSZ")
    
    @staticmethod
    def _validate_dividend_cash_action(dividend_cash_action:str):
        valid_actions = ["REINVEST", "TO_ACCOUNT_CASH"]
        if dividend_cash_action not in valid_actions:
            raise ValueError(f"dividendCashAction must be one of {valid_actions}")

    @staticmethod
    def _validate_icon(icon:str):
        valid_icons = [
            "Home", "PiggyBank", "Iceberg", "Airplane", "RV", "Unicorn", "Whale", "Convertable", "Family",
            "Coins", "Education", "BillsAndCoins", "Bills", "Water","Wind", "Car", "Briefcase", "Medical",
            "Landscape", "Child", "Vault", "Travel", "Cabin", "Apartments", "Burger", "Bus", "Energy", 
            "Factory", "Global", "Leaf", "Materials", "Pill", "Ring", "Shipping", "Storefront", "Tech", "Umbrella"]

        if icon not in valid_icons:
            raise ValueError(f"icon must be one of {valid_icons}")
    
    @staticmethod
    def _validate_instrument_shares(instrument_shares):
        if not isinstance(instrument_shares, dict):
            raise TypeError("instrument_shares must be a dictionary")
        if not instrument_shares:
            raise ValueError("instrument_shares cannot be empty")
        for key, value in instrument_shares.items():
            if not isinstance(key, str):
                raise TypeError("Instrument identifiers must be strings")
            if not isinstance(value, (int, float)):
                raise TypeError("Number of shares must be a number")
            if value <= 0:
                raise ValueError("Number of shares must be greater than zero")

    def orders(self, cursor: int = 0, ticker: str = None, limit: int = 50):
        """Historical order data"""

        params = {"cursor": cursor, "limit": limit}
        if ticker:
            params["ticker"] = ticker

        return self._process_items(self._get("equity/history/orders", params=params))

    def dividends(self, cursor: int = 0, ticker: str = None, limit: int = 50):
        """Dividends paid out"""

        params = {"cursor": cursor, "limit": limit}
        if ticker:
            params["ticker"] = ticker

        return self._process_items(self._get("history/dividends", params=params))

    def export(self):
        """Fetches all Account exports as a List"""
        return self._get("history/exports")
    
    def export_csv(
        self,
        time_from: datetime,
        time_to: datetime,
        include_dividends: bool = True,
        include_interest: bool = True,
        include_orders: bool = True,
        include_transactions = True,
    ):
        """Request a csv export of the account's orders, dividends and transactions history"""
        # Format the date-time parameters to ISO 8601 strings
        time_from_str = time_from.strftime("%Y-%m-%dT%H:%M:%SZ")
        time_to_str = time_to.strftime("%Y-%m-%dT%H:%M:%SZ")

        return self._post(
            "/history/exports",
            data={
                "dataIncluded": {
                "includeDividends": include_dividends,
                "includeInterest": include_interest,
                "includeOrders": include_orders,
                "includeTransactions": include_transactions
                },  
                "timeFrom": time_from_str,
                "timeTo": time_to_str
            },
        )


    def transactions(self, cursor: int = 0, limit: int = 50):
        """Transactions list"""

        params = {"cursor": cursor, "limit": limit}

        return self._process_items(self._get("history/transactions", params=params))

    def instruments(self):
        """Tradeable instruments metadata"""
        return self._get("equity/metadata/instruments")

    def cash(self):
        """Account cash"""
        return self._get("equity/account/cash")

    def portfolio(self):
        """All open positions"""
        return self._get("equity/portfolio")

    def position(self, ticker: str):
        """Open position by ticker"""
        return self._get(f"equity/portfolio/{ticker}")

    def exchanges(self):
        """Exhange list"""
        return self._get("equity/metadata/exchanges")

    def account_info(self):
        """Account info"""
        return self._get("equity/account/info")

    def equity_orders(self):
        """All equity orders"""
        return self._get("equity/orders")

    def equity_order(self, id: int):
        """Equity order by ID"""
        return self._get(f"equity/orders/{id}")

    def equity_order_cancel(self, id: int):
        """Cancel equity order"""
        return self._delete_url(f"equity/orders/{id}")

    def equity_order_place_limit(
        self, 
        ticker: str, 
        quantity: int, 
        limit_price: float, 
        time_validity: str
    ):
        """Place limit order"""

        self._validate_time_validity(time_validity)

        return self._post(
            f"equity/orders/limit",
            data={
                "quantity": quantity,
                "limitPrice": limit_price,
                "ticker": ticker,
                "timeValidity": time_validity,
            },
        )

    def equity_order_place_market(
        self,
        ticker: str, 
        quantity: int
    ):
        """Place market order"""

        return self._post(
            f"equity/orders/market", data={"quantity": quantity, "ticker": ticker}
        )

    def equity_order_place_stop(
        self, 
        ticker: str,
        quantity: int, 
        stop_price: float, 
        time_validity: str
    ):
        """Place stop order"""

        self._validate_time_validity(time_validity)

        return self._post(
            f"equity/orders/stop",
            data={
                "quantity": quantity,
                "stopPrice": stop_price,
                "ticker": ticker,
                "timeValidity": time_validity,
            },
        )

    def equity_order_place_stop_limit(
        self,
        ticker: str,
        quantity: int,
        stop_price: float,
        limit_price: float,
        time_validity: str,
    ):
        """Place stop-limit order"""

        self._validate_time_validity(time_validity)

        return self._post(
            f"equity/orders/stop_limit",
            data={
                "quantity": quantity,
                "stopPrice": stop_price,
                "limitPrice": limit_price,
                "ticker": ticker,
                "timeValidity": time_validity,
            },
        )

    def pies(self):
        """Fetch all Pies"""
        return self._get("equity/pies")
    
    def pie_create(
        self,
        dividend_cash_action: str,
        end_date: datetime,
        goal: int,
        icon: str,
        instrument_shares: dict,
        name: str
    ):
        """Create a Pie"""
        self._validate_dividend_cash_action(dividend_cash_action)
        self._validate_icon(icon)
        self._validate_date(end_date)
        self._validate_instrument_shares(instrument_shares)
        
        return self._post(
            f"/equity/pies",
            data={
                "dividendCashAction": dividend_cash_action,
                "endDate": end_date,
                "goal": goal,
                "icon": icon,
                "instrumentShares": instrument_shares,
                "name": name
            },
        )
    
    def pie_delete(self, id: int):
        """Delete Pie by ID"""
        return self._delete_url(f"/equity/pies/{id}")
    
    def pie(self, id:int):
        """Fetch Pie by ID"""
        return self._get(f"/equity/pies/{id}")
    
    def pie_update(
        self,
        id:int,
        dividend_cash_action: str,
        end_date: str,
        goal: int,
        icon: str,
        instrument_shares: dict,
        name: str
    ):
        """Update existing Pie"""
        self._validate_dividend_cash_action(dividend_cash_action)
        self._validate_icon(icon)
        self._validate_date(end_date)
        self._validate_instrument_shares(instrument_shares)

        return self._post(
            f"equity/pies/{id}",
            data={
                "dividendCashAction": dividend_cash_action,
                "endDate": end_date,
                "goal":goal,
                "icon": icon,
                "instrumentShares": instrument_shares,
                "name": name
            },
        )
        

        



    def __repr__(self):
        return "Trading212(api_key=****{}, demo={})".format(
            self._api_key[-4:], self.host == "https://demo.trading212.com"
        )
