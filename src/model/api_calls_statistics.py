from typing import List, NamedTuple, Dict, Tuple
from datetime import datetime
import numpy as np

class ApiKeyCall(NamedTuple):
    """
    api_alias: the alias of the api caller
    path: the path of the api call
    method: the method used
    status: the status code returned
    time: the time elapsed in the query
    timestamp: the timestamp for the call
    """
    api_alias: str
    path: str
    method: str
    status: int
    time: float
    timestamp: datetime

class ApiCallsStatistics:
    """
    Object responsible for calculating the api call statistics
    """
    def __init__(self, api_calls: List[ApiKeyCall]):
        self.api_calls_by_alias = {}
        for api_call in api_calls:
            if api_call.api_alias not in self.api_calls_by_alias:
                self.api_calls_by_alias[api_call.api_alias] = []
            self.api_calls_by_alias[api_call.api_alias].append(api_call)

    def median_response_time_last_30_days(self) -> Dict[str, Dict[int, float]]:
        """
        Calculates the median response time from the last 30 days for each api
        @return: a dict with the server alias as key and a dict of day: median response time
        where day 30 is 30 days back and day 0 is today. If there is no data for a day, it is not included in the list
        """
        today_datetime = datetime.now()
        median_responses_by_alias = {}
        for alias in self.api_calls_by_alias.keys():
            median_response_time_by_day = {}
            for api_call in self.api_calls_by_alias[alias]:
                days_delta = abs((today_datetime - api_call.timestamp).days)
                if days_delta > 30:
                    continue
                if days_delta not in median_response_time_by_day:
                    median_response_time_by_day[days_delta] = [api_call.time]
                else:
                    median_response_time_by_day[days_delta] += [api_call.time]
            median_response_time_by_day = {k:np.median(v) for k,v in median_response_time_by_day.items()}
            median_responses_by_alias[alias] = median_response_time_by_day
        return median_responses_by_alias

    def api_calls_by_type(self) -> Dict[str, List[Dict]]:
        """
        Calculates the quantity of api calls by path, method and status code

        @return: a dictionary containing the dictionary of the counts
        """
        response_dict = {}
        for alias in self.api_calls_by_alias.keys():
            response_dict[alias] = [{},{},{}]
            for api_call in self.api_calls_by_alias[alias]:
                if api_call.path not in response_dict[alias][0]:
                    response_dict[alias][0][api_call.path] = 1
                else:
                    response_dict[alias][0][api_call.path] += 1
                if api_call.method not in response_dict[alias][1]:
                    response_dict[alias][1][api_call.method] = 1
                else:
                    response_dict[alias][1][api_call.method] += 1
                if api_call.status not in response_dict[alias][2]:
                    response_dict[alias][2][api_call.status] = 1
                else:
                    response_dict[alias][2][api_call.status] += 1
        return response_dict