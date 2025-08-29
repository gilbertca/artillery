from json import loads

from requests import delete, get, post

# TODO: Error handling in 'query_api'

class API:
    def __init__(self, url):
        self.url = url

    def query_api(self, uri, method, payload={}):
        method_namespace = {
            'delete': delete,
            'get': get,
            'post': post,
        }

        # Attempt query:
        try:
            url = f"{self.url}/{uri}"
            response = method_namespace[method](url, json=payload).json()

            # Convert all JSON strings to Python objects:
            return_values = {}
            for key, value in response.items():
                return_values.update({key: loads(value)})

            return return_values

        # Method is incorrect
        except KeyError as method_error:
            raise method_error

        # All other request errors
        except Exception as e:
            raise e

