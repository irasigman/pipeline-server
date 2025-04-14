import json
import os
from pprint import pprint
import requests


class WebSearch:
    def __init__(self):
        self.subscription_key = os.environ['BING_SEARCH_V7_SUBSCRIPTION_KEY']
        self.endpoint = os.environ['BING_SEARCH_V7_ENDPOINT'] + "/v7.0/search"
        self.mkt = 'en-US'
        self.headers = {'Ocp-Apim-Subscription-Key': self.subscription_key}

    def get_search_results(self, query: str):
        params = {'q': query, 'mkt': self.mkt}
        try:
            response = requests.get(self.endpoint, headers=self.headers, params=params)
            response.raise_for_status()
            return response.json()
        except Exception as ex:
            raise ex


# Example usage:
if __name__ == '__main__':
    bing_search = WebSearch()
    results = bing_search.get_search_results("dry cleaners pittsburgh")
    pprint(results)