from json import loads

from requests import delete, get, post


class API:
    """API serves as an interface between the client and server.

    An API is initialized with a `url`. This `url` is manipulated internally
    to query the various endpoints. Users of the API class should always use
    the method dedicated to a specific endpoint (for example, `add_unit`).

    Users of the API class should NOT use the _query_api method;
    Let the API class do all of the validation and error handling.

    Params:
        `url` - The url to a running **artillery** server (prepended with 'http://')
    """
    def __init__(self, url):
        self.url = url

    def _query_api(self, uri, method, payload={}):
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
            raise method_error(f"Expected a value in {[method for method in method_namespace.keys()]}, but API received {method}")

        # All other request errors
        except Exception as e:
            raise e

