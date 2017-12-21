# coding: utf-8
import warnings
import os
import requests
from compat import quote, imap, urljoin
from error import build_api_error
from model import APIObject, new_api_object
from util import encode_params, check_uri_security

COINBASE_CRT_PATH = os.path.join(os.path.dirname(os.path.realpath(__file__)), 'ca-coinbase.crt')


class Data(object):
    """ API Data Endpoint for the Coinbase API.

    Entry point for making requests to Coinbase Data API.
    It doesn't require key and secret.
    """

    BASE_API_URI = 'https://api.coinbase.com/'
    VERIFY_SSL = True
    API_VERSION = '2016-02-18'

    def __init__(self, base_api_uri=None, api_version=None):
        # Allow passing in a different API base.
        self.BASE_API_URI = check_uri_security(base_api_uri or self.BASE_API_URI)
        self.API_VERSION = api_version or self.API_VERSION
        # Set up a requests session for interacting with the API.
        self.session = self._build_session(None)

    def _create_api_uri(self, *parts):
        """Internal helper for creating fully qualified endpoint URIs."""
        return urljoin(self.BASE_API_URI, '/'.join(imap(quote, parts)))

    def _handle_response(self, response):
        """Internal helper for handling API responses from the Coinbase server.
        Raises the appropriate exceptions when necessary; otherwise, returns the
        response.
        """
        if not str(response.status_code).startswith('2'):
            raise build_api_error(response)
        return response

    def _build_session(self, auth_class, *args, **kwargs):
        """Internal helper for creating a requests `session` with the correct
        authentication handling."""
        session = requests.session()
        if auth_class:
            session.auth = auth_class(*args, **kwargs)
        session.headers.update({requests.utils.to_native_string('CB-VERSION'): self.API_VERSION})
        session.headers.update({'Accept': 'application/json',
                                'Content-Type': 'application/json',
                                'User-Agent': 'coinbase/python/2.0'})
        return session

    def _request(self, method, *relative_path_parts, **kwargs):
        """Internal helper for creating HTTP requests to the Coinbase API.
        Raises an APIError if the response is not 20X. Otherwise, returns the
        response object. Not intended for direct use by API consumers.
        """
        uri = self._create_api_uri(*relative_path_parts)
        data = kwargs.get('data', None)
        if data and isinstance(data, dict):
            kwargs['data'] = encode_params(data)
        if self.VERIFY_SSL:
            kwargs.setdefault('verify', COINBASE_CRT_PATH)
        else:
            kwargs.setdefault('verify', False)
        kwargs.update(verify=self.VERIFY_SSL)
        response = getattr(self.session, method)(uri, **kwargs)
        return self._handle_response(response)

    def _get(self, *args, **kwargs):
        return self._request('get', *args, **kwargs)

    def _make_api_object(self, response, model_type=None):
        blob = response.json()
        data = blob.get('data', None)
        # All valid responses have a "data" key.
        if data is None:
            raise build_api_error(response, blob)
        # Warn the user about each warning that was returned.
        warnings_data = blob.get('warnings', None)
        for warning_blob in warnings_data or []:
            message = "%s (%s)" % (
                warning_blob.get('message', ''),
                warning_blob.get('url', ''))
            warnings.warn(message, UserWarning)

        pagination = blob.get('pagination', None)
        kwargs = {
            'response': response,
            'pagination': pagination and new_api_object(None, pagination, APIObject),
            'warnings': warnings_data and new_api_object(None, warnings_data, APIObject),
        }
        if isinstance(data, dict):
            obj = new_api_object(self, data, model_type, **kwargs)
        else:
            obj = APIObject(self, **kwargs)
            obj.data = new_api_object(self, data, model_type)
        return obj

    # Data API
    # -----------------------------------------------------------

    def get_currencies(self, **params):
        """https://developers.coinbase.com/api/v2#currencies"""
        response = self._get('v2', 'currencies', data=params)
        return self._make_api_object(response, APIObject)

    def get_exchange_rates(self, **params):
        """https://developers.coinbase.com/api/v2#exchange-rates"""
        response = self._get('v2', 'exchange-rates', data=params)
        return self._make_api_object(response, APIObject)

    def get_buy_price(self, **params):
        """https://developers.coinbase.com/api/v2#get-buy-price"""
        if 'currency_pair' in params:
            currency_pair = params['currency_pair']
        else:
            currency_pair = 'BTC-USD'
        response = self._get('v2', 'prices', currency_pair, 'buy', data=params)
        return self._make_api_object(response, APIObject)

    def get_sell_price(self, **params):
        """https://developers.coinbase.com/api/v2#get-sell-price"""
        if 'currency_pair' in params:
            currency_pair = params['currency_pair']
        else:
            currency_pair = 'BTC-USD'
        response = self._get('v2', 'prices', currency_pair, 'sell', data=params)
        return self._make_api_object(response, APIObject)

    def get_spot_price(self, **params):
        """https://developers.coinbase.com/api/v2#get-spot-price"""
        if 'currency_pair' in params:
            currency_pair = params['currency_pair']
        else:
            currency_pair = 'BTC-USD'
        response = self._get('v2', 'prices', currency_pair, 'spot', data=params)
        return self._make_api_object(response, APIObject)

    def get_historic_prices(self, **params):
        """https://developers.coinbase.com/api/v2#get-historic-prices"""
        response = self._get('v2', 'prices', 'historic', data=params)
        return self._make_api_object(response, APIObject)

    def get_time(self, **params):
        """https://developers.coinbase.com/api/v2#time"""
        response = self._get('v2', 'time', data=params)
        return self._make_api_object(response, APIObject)


if __name__ == '__main__':
    data = Data()
    print(data.get_time())
    print(data.get_sell_price(currency_pair='LTC-USD'))
    print(data.get_buy_price(currency_pair='BTC-USD'))
    print(data.get_spot_price())