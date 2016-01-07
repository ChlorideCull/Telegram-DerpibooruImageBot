import requests
import sys
import json

class TelegramBot(object):
    __token = None
    __session = None
    __baseurl = "https://api.telegram.org/bot{token}/{func}"
    __last_update_id = 0

    __inline_request_calls = []

    def __init__(self, token, ua="TelegramAPI.py"):
        self.__token = token
        self.__session = requests.Session()
        self.__session.headers["User-Agent"] = ua + (" (Python {version.major}.{version.minor}.{version.micro}, "
                                                     "using Requests)").format(version=sys.version_info)

    def __call_api(self, function_string, arguments=None):
        """
        Send a raw call to the Telegram API.
        :param function_string: API function to call, for example "getUpdates".
        :param arguments: A dictionary of arguments to pass in the query string
        :return: Dictionary containing decoded JSON response
        """
        url = self.__baseurl.format(token=self.__token, func=function_string)
        if arguments is not None:
            response = self.__session.get(url, params=arguments)
        else:
            response = self.__session.get(url)
        if response.json()["ok"]:
            return response.json()["result"]
        else:
            raise Exception(response.json()["description"])

    def inline_request_hook(self, func):
        """
        Decorator to add hooks that respond to inline requests
        :param func: function to act as a hook, takes a single key arguments: "query", returns a list of
        results encoded as a dictionary, see <https://core.telegram.org/bots/api#inlinequeryresult>
        :return: parameter func
        """
        self.__inline_request_calls.append(func)
        return func

    def poll_once(self):
        updates = self.__call_api("getUpdates", {"offset": self.__last_update_id})
        if len(updates) > 0:
            print("Recieved {} updates in poll.".format(len(updates)))
        for update in updates:
            if update["update_id"] >= self.__last_update_id:
                self.__last_update_id = update["update_id"] + 1
            if "message" in update:
                continue
            elif "inline_query" in update:
                for hook in self.__inline_request_calls:
                    resp = json.dumps(hook(query=update["inline_query"]["query"]))
                    print(" Responding to {} with '{}'".format(update["inline_query"]["id"], resp))
                    try:
                        self.__call_api("answerInlineQuery", {
                             "inline_query_id": update["inline_query"]["id"],
                             "results": resp
                        })
                    except Exception as e:
                        print(e)
            elif "chosen_inline_result" in update:
                continue
