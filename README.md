# urlfinderlib
Python library for finding URLs in documents and arbitrary data and checking their validity.

**Basic usage**

    from urlfinderlib import find_urls
    
    with open('/path/to/file', 'rb') as f:
        print(find_urls(f.read())

**base_url usage**

If you are trying to find URLs inside of an HTML file, the paths in the URLs are likely relative to their location on the server hosting the HTML. You can use the *base_url* parameter in this case to extract these "relative" URLs.

    from urlfinderlib import find_urls
    
    with open('/path/to/file', 'rb') as f:
        print(find_urls(f.read(), base_url='http://somewebsite.com/')
