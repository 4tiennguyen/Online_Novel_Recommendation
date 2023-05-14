import os
import sys


def write(message: str):
    """

    """
    if sys.platform != 'darwin':
        with open('logg.txt', mode='a') \
            as output_file:
            output_file.write(str(message))
            output_file.write(os.linesep)
            output_file.flush()
