import pytest
import json
import os
import src.torlib.crawler.github_crawler as gc
from src.torlib.crawler.github_crawler import NoTokenError, LengthNotMatchError, InputNotStringError
import responses
import requests


def test_github_crawler_multipage_notoken():
    with pytest.raises(NoTokenError):
        savename = ['1', '1', '1']
        url = ['1', '1', '1']
        gc.github_crawler_multipage(savename, url, [], for_test=True)


def test_github_crawler_multipage_lengthnotmatch():
    with pytest.raises(LengthNotMatchError):
        savename = ['1', '1', '1']
        url = ['1']
        gc.github_crawler_multipage(savename, url, ['token'], for_test=True)


def test_github_crawler_multipage_inputnotstring():
    with pytest.raises(InputNotStringError):
        savename = ['1', '1', '1']
        url = ['1', '1', 1]
        gc.github_crawler_multipage(savename, url, ['token'], for_test=True)


@responses.activate
def test_github_crawler_multipage_fail():
    savename = ['test1', 'test2', 'test3']
    url = ['test_github/api/1', 'test_github/api/2', 'test_github/api/3']
    GHtoken = ['token']
    log_file = 'test_github_crawler_multipage_fail.txt'
    gc.github_crawler_multipage(savename, url, GHtoken, log_file=log_file, for_test=True)
    # check log
    with open(log_file, 'r') as outfile:
        log = json.load(outfile)
    os.remove(log_file)
    expected_log = [["test_github/api/1", "Invalid URL 'test_github/api/1?per_page=100&page=1': No schema supplied. Perhaps you meant http://test_github/api/1?per_page=100&page=1?"],
                    ["test_github/api/2", "Invalid URL 'test_github/api/2?per_page=100&page=1': No schema supplied. Perhaps you meant http://test_github/api/2?per_page=100&page=1?"],
                    ["test_github/api/3", "Invalid URL 'test_github/api/3?per_page=100&page=1': No schema supplied. Perhaps you meant http://test_github/api/3?per_page=100&page=1?"]]
    assert log == expected_log


@responses.activate
def test_github_crawler_multipage_success():
    savename = ['test1', 'test2', 'test3']
    url = ['http://test_github/api/1',
           'http://test_github/api/2', 'http://test_github/api/3']
    GHtoken = ['token']
    log_file = 'test_github_crawler_multipage_success.txt'
    gc.github_crawler_multipage(savename, url, GHtoken, log_file=log_file, for_test=True)
    # check log
    with open(log_file, 'r') as outfile:
        log = json.load(outfile)
    os.remove(log_file)
    expected_log = []
    assert log == expected_log
    #check result
    for i in range(1,4):
        with open(f'test{i}.json', 'r') as outfile:
            res = json.load(outfile)
        os.remove(f'test{i}.json')
        expected_res = [{"test": f"test{i}"}]
        assert res == expected_res

