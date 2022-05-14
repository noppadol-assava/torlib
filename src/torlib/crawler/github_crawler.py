import multiprocessing as mp
from tqdm import tqdm
import os
import time
import requests
import json
from pathlib import Path
import responses

class NoTokenError(Exception):
    """Raised when input list of github token is empty

    Attributes:
        message (string): explanation of the error
    """

    def __init__(self, message="please input github token"):
        self.message = message
        super().__init__(self.message)

    def __str__(self):
        return f'{self.message}'


class LengthNotMatchError(Exception):
    """Raised when the length of savename and url is not the same

    Attributes:
        savename (list): input list that cause error
        url (list): input list that cause error
        message (string): explanation of the error
    """

    def __init__(self, savename, url, message="savename and url must have same length"):
        self.length_savename = len(savename)
        self.length_url = len(url)
        self.message = message
        super().__init__(self.message)

    def __str__(self):
        return f'len(savename)={self.length_savename} len(url)={self.length_url} -> {self.message}'


class InputNotStringError(Exception):
    """Raised when not all of member in savename or url are string

    Attributes:
        error_list_name (string): name of input list that cause error
        message (string): explanation of the error
    """

    def __init__(self, error_list_name, message="savename or url must contain only string"):
        self.error_list_name = error_list_name
        self.message = message
        super().__init__(self.message)

    def __str__(self):
        return f'{self.error_list_name} -> {self.message}'


def github_crawler_multipage(savename, url, GHtoken, retry=3, pc=1, log_file='github_crawler_log.txt', output_dir='', for_test=False):
    """ crawl the github api and save file to json this function will also generate the log file that show the url of api that cannot be crawled

    Args:
        savename (list): contain string of the save file name (need to be same length as url)
        url (list): contain string of url of the target api (need to be same length as savename)
        GHtoken (list): list of github token
        retry (int, optional): number of time to retry crawling the fail case. Defaults to 3.
        pc (int, optional): number of process for multiprocessing. Defaults to 1.
        log_file (str, optional): name of the log file showing the detail of fail case. Defaults to 'github_crawler_log.txt'.
        output_dir (str, optional): output directory. Defaults to ''.
        for_test (boolean, optional): used for testing or not. Defaults to False.

    Raises:
        LengthNotMatchError: Raised when the length of savename and url is not the same
        InputNotStringError: Raised when not all of member in savename or url are string
        NoTokenError: Raised when input list of github token is empty

    """
    # check the size of savename and url
    if len(savename) != len(url):
        raise LengthNotMatchError(savename, url)
    # check type of member of savename and url
    for i in savename:
        if type(i) != str:
            raise InputNotStringError('savename')
    for i in url:
        if type(i) != str:
            raise InputNotStringError('url')
    # check if github token is empty
    if len(GHtoken) == 0:
        raise NoTokenError()
    # if savename and url length is 0 do nothing
    if len(savename) == 0 and len(url) == 0:
        return
    # create path to output_dir if not exist
    Path(output_dir).mkdir(parents=True, exist_ok=True)
    # prepared parameter for collect_json_multipage
    save_path = [os.path.join(output_dir, f'{sn}.json') for sn in savename]
    list_to_crawl = list(zip(save_path, url))
    for i in range(len(list_to_crawl)):
        list_to_crawl[i] = list_to_crawl[i]+(GHtoken[i % len(GHtoken)],)
    count_try = 0
    complete = False
    while count_try < retry and not complete:
        print(f'{count_try+1} attempt to crawl {len(list_to_crawl)} url')
        count_try = count_try+1
        # create pool for multiprocessing
        with mp.Pool(pc) as p:
            multi_out = tqdm(p.imap(__collect_json_multipage if not for_test else __collect_json_multipage_for_testing,
                                    list_to_crawl, chunksize=1), total=len(list_to_crawl))
            result = [i for i in multi_out]
        # check if all of url is complete and list only fail url
        complete = True
        remain_list_to_crawl = []
        for i in range(len(result)):
            url, is_success = result[i]
            if is_success != 1:
                complete = False
                remain_list_to_crawl.append(list_to_crawl[i])
        list_to_crawl = remain_list_to_crawl
        print(list_to_crawl)
    # list url that cannot be crawled
    fail_list = [(url, is_success)
                 for url, is_success in result if is_success != 1]
    with open(log_file, 'w') as outfile:
        json.dump(fail_list, outfile)

        
def __collect_json_multipage(input_tuple):
    """ save response from request as json file

    Args:
        input_tuple (tuple): tuple contain three variables: 

        - save_path (string) save file name with path url (string) 

        - url of the api GHtoken (string) - Github Token

    Returns:
        tuple: (url, result) showing status of the crawling
        result will be 1 if sucess otherwise it will
        be the exception message of the error that occur
    """
    save_path, url, GHtoken = input_tuple
    # if the file is exist proceed to next one
    if os.path.exists(save_path):
        return (url, 1)
    page = 1
    stop_flag = False  # track last page
    result_json = []
    try:
        while not stop_flag:
            r = requests.get(url+'?per_page=100&page='+str(page),
                             headers={'Authorization': 'token '+GHtoken})
            # if ratelimit is not remain wait until rate limit reset and try again
            if int(r.headers['X-RateLimit-Remaining']) <= 0:
                current_time = time.time()
                left_time = current_time - int(r.headers['X-RateLimit-Reset'])
                while(left_time < 0):
                    time.sleep(10)
                    current_time = time.time()
                    left_time = current_time - \
                        int(r.headers['X-RateLimit-Reset'])
                r = requests.get(url+'?per_page=100&page='+str(page),
                                 headers={'Authorization': 'token '+GHtoken})
            json_r = r.json()
            if type(json_r) == dict:
                result_json.append(json_r)
            else:
                result_json.extend(json_r)
            page = page+1
            # stop if last page
            if 'link' not in r.headers or 'rel="last"' not in r.headers['link']:
                stop_flag = True
        # save json file
        with open(save_path, 'w') as outfile:
            json.dump(result_json, outfile)
    # return error
    except Exception as e:
        return (url, str(e))
    return (url, 1)


@responses.activate
def __collect_json_multipage_for_testing(input_tuple):
    """ function used for testing only"""
    responses.add(responses.GET,
                  'http://test_github/api/1?per_page=100&page=1',
                  status=200,
                  content_type='application/json',
                  headers={'X-RateLimit-Remaining': '100000'},
                  body='{"test": "test1"}')
    responses.add(responses.GET,
                  'http://test_github/api/2?per_page=100&page=1',
                  status=200,
                  content_type='application/json',
                  headers={'X-RateLimit-Remaining': '100000'},
                  body='{"test": "test2"}')
    responses.add(responses.GET,
                  'http://test_github/api/3?per_page=100&page=1',
                  status=200,
                  content_type='application/json',
                  headers={'X-RateLimit-Remaining': '100000'},
                  body='{"test": "test3"}')
    return __collect_json_multipage(input_tuple)