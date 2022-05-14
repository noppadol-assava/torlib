.. _autodoc:

=======
Crawler
=======
torlib provide the easy way to crawl data from API in just only one function call.
The current supported API is `GitHub API`_.
 
GitHub Crawler
==============
This provide the function for crawling data from `GitHub API`_. 
torlib also support multiprocess (by specifying ``pc``) to allow faster crawling by utilize all of rate limit of the API request.
When the rate limit exceed, the function will wait until the rate limit reset and try sending request to the url again 

github_crawler_multipage
------------------------
.. autofunction:: torlib.crawler.github_crawler.github_crawler_multipage


Example Usage
^^^^^^^^^^^^^
.. code-block:: python
  
  import torlib.crawler.github_crawler as gc

  savename = ['test1', 'test2', 'test3']
  url = ['github/api/link/1', 'github/api/link/2', 'github/api/link/3']
  GHtoken = ['token1','token2']

  gc.github_crawler_multipage(savename, url, GHtoken, output_dir='data')

The above python code will created *data/test1.json*, *data/test2.json*, *data/test3.json*, and *github_crawler_log.txt*.
The result from each of API url will be in separate json file (if successfully crawl) and stored in ``output_dir`` directory. The log will list the url and error message in ``log_file``
If there is an error when crawling the url, after trying to crawl it ``retry`` times, the url will be in ``log_file`` together with error message.

.. code-block:: text
   :caption: github_crawler_log.txt

   [('github/api/link/1','Connection Error')]
 
.. _GitHub API: https://docs.github.com/en/rest