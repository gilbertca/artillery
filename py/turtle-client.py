from argparse import ArgumentParser

from exit_codes.exit_codes import ExitCode

MAX_RETRIES = 3

def main(url):
    """`main` is the primary entry point for launching and playing ARTILLERY
    with the `turtle` client.

    Arguments:
        **url** (str): The URL which points to a running ARTILLERY server.

    Returns:
        int: An exit code (see the `exit_code` module for value explanations).
    """
    num_attempts = 0
    while True:
        num_attempts += 1
        try:
            ...

        except Exception as e:
            print(f"""
            An unhandled exception was raised by function '{main.__name__}'.

            This is probably the first time you have caught this exception,
            since this statement is printed by an `except Exception` clause.

            The exception is of type {type(e)}, and may be recoverable.
            """)
            if num_attempts >= MAX_RETRIES:
                raise e
            else: # Retry until we exceed MAX_RETRIES
                pass

if __name__ == '__main__':
    parser = ArgumentParser()
    parser.add_argument('url',
                        help='The URL to the ARTILLERY server.')
    args = vars(parser.parse_args())

    code = main(**args)
    print(code)
