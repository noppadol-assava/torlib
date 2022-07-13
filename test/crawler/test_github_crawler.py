import pytest
import json
import os
import src.torlib.crawler.github_crawler as gc
from src.torlib.crawler.github_crawler import NoTokenError, LengthNotMatchError, InputNotStringError
import responses


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
    assert len(log) == 3


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

@responses.activate
def test_github_crawler_multipage_pretty_json():
    savename = ['test1', 'test2', 'test3']
    url = ['http://test_github/api/1',
           'http://test_github/api/2', 'http://test_github/api/3']
    GHtoken = ['token']
    log_file = 'test_github_crawler_multipage_success.txt'
    # check when pretty_json = False
    gc.github_crawler_multipage(savename, url, GHtoken, log_file=log_file, for_test=True, pretty_json=False)
    # check log
    with open(log_file, 'r') as outfile:
        log = json.load(outfile)
    os.remove(log_file)
    expected_log = []
    assert log == expected_log
    #check result
    for i in range(1,4):
        with open(f'test{i}.json', 'r') as outfile:
            assert outfile.read() == '[{"test": "test'+str(i)+'"}]'
        os.remove(f'test{i}.json')
    # check when pretty_json = True
    gc.github_crawler_multipage(savename, url, GHtoken, log_file=log_file, for_test=True, pretty_json=True)
    # check log
    with open(log_file, 'r') as outfile:
        log = json.load(outfile)
    os.remove(log_file)
    expected_log = []
    assert log == expected_log
    #check result
    for i in range(1,4):
        with open(f'test{i}.json', 'r') as outfile:
            assert outfile.read() == '[\n    {\n        "test": "test'+str(i)+'"\n    }\n]'
        os.remove(f'test{i}.json')

