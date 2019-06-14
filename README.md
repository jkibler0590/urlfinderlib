# urlfinderlib
Python library for finding URLs in documents and arbitrary data and checking their validity.

    from urlfinderlib import find_urls
    
    with open('/path/to/file', 'rb') as f:
        print(find_urls(f.read())


