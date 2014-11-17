'''Find valid pages.

To use the script manually::

    python discover.py 0 100000000 myfile.txt.gz


The file will contain things like:

blog:help
'''
import gzip
import re
import requests
import string
import sys
import time
import random

DEFAULT_HEADERS = {'User-Agent': 'ArchiveTeam'}
ALPHABET = string.digits + string.ascii_lowercase
assert len(ALPHABET) == 10 + 26


class FetchError(Exception):
    '''Custom error class when fetching does not meet our expectation.'''


def main():
    # Take the program arguments given to this script
    # Normal programs use 'argparse' but this keeps things simple
    start_num = int(sys.argv[1])
    end_num = int(sys.argv[2])
    output_filename = sys.argv[3]  # this should be something like myfile.txt.gz

    assert start_num <= end_num

    print('Starting', start_num, end_num)

    gzip_file = gzip.GzipFile(output_filename, 'wb')

    for shortcode in check_range(start_num, end_num):
        # Write the valid result one per line to the file
        line = '{0}\n'.format(shortcode)
        gzip_file.write(line.encode('ascii'))

    gzip_file.close()

    print('Done')


def int_to_str(num, alphabet):
    '''Convert integer to string.'''
    # http://stackoverflow.com/a/1119769/1524507
    if (num == 0):
        return alphabet[0]
    arr = []
    base = len(alphabet)
    while num:
        rem = num % base
        num = num // base
        arr.append(alphabet[rem])
    arr.reverse()
    return ''.join(arr)


def check_range(start_num, end_num):
    '''Check if page exists.    '''

    for num in range(start_num, end_num + 1):
        shortcode = int_to_str(num, ALPHABET)
        url = 'http://{0}.jux.com'.format(shortcode)
        counter = 0

        while True:
            # Try 20 times before giving up
            if counter > 10:
                # This will stop the script with an error
                raise Exception('Giving up!')

            try:
                text = fetch(url)
            except FetchError:
                # The server may be overloaded so wait a bit
                print('Sleeping... If you see this')
                time.sleep(10)
            else:
                if text:
                	match = re.search(r'<div\s+id="no-stuff-message-text">', text)
					
  	                if match:
  	                	print('No content')
                    	
            		else:
            			yield 'blog:{0}'.format(shortcode)

                break  # stop the while loop

            counter += 1


def fetch(url):
    '''Fetch the URL and check if it returns OK.

    Returns True, returns the response text. Otherwise, returns None
    '''
    print('Fetch', url)
    response = requests.get(url, headers=DEFAULT_HEADERS)

    # response doesn't have a reason attribute all the time??
    print('Got', response.status_code, getattr(response, 'reason'))

    if response.status_code == 200:
        # The item exists
        if not response.text:
            # If HTML is empty maybe server broke
            raise FetchError()

        return response.text
    elif response.status_code == 404:
        # Does not exist
        return
    elif response.status_code == 500:
        # Pops up every now and then
        return
    else:
        # Problem
        raise FetchError()

if __name__ == '__main__':
    main()
