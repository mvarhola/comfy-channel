from datetime import datetime

from colorama import Back, Fore, Style

TYPE_INFO = 1
TYPE_ERROR = 2
TYPE_CRIT = 3


def get_time():
    return datetime.now().strftime("%Y-%m-%d %H:%M:%S")


class Logger:

    def __init__(self, log_file):
        self.log_file = log_file

    def log(self, log_type, text):
        if log_type == TYPE_INFO:
            print(Fore.GREEN+get_time()+" INFO" +
                  Style.RESET_ALL+': {}'.format(text))
        if log_type == TYPE_ERROR:
            print(Fore.YELLOW+get_time()+" ERROR" +
                  Style.RESET_ALL+': {}'.format(text))
        if log_type == TYPE_CRIT:
            print(Fore.RED+get_time()+" CRITICAL" +
                  Style.RESET_ALL+': {}'.format(text))

    # TODO: Write log statements to file to file


LOGGER = Logger(None)
