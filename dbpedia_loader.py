import urllib, urllib2
import os.path
import json


class DbpediaResourceLoader:
    """ DBPedia stores a "resource" corresponding to a Wikipedia article:
        https://wiki.dbpedia.org/services-resources/datasets/dbpedia-datasets#h434-5
        These resources are available in JSON format, which provides a simple,
        yet inelegant, way of accessing them, compared to RDF with SPARQL. To
        save bandwidth, this class also caches the resources locally.
    """
    def __init__(self):
        # Filename of a cache of URLs that were previously loaded:
        self.RESOURCE_CACHE_FILENAME = "_resource_cache.json"
        self.url_cache = None
        self.url_cache_updated = False

    def __enter__(self):
        self.loadResourceCache()

    def __exit__(self, exc_type, exc_value, traceback):
        if self.url_cache_updated:
            self.dumpResourceCache()

    def loadResourceCache(self):
        """ Load the resource cache from disk. """
        self.url_cache = {}
        if not os.path.isfile(self.RESOURCE_CACHE_FILENAME):
            return
        with open(self.RESOURCE_CACHE_FILENAME, 'r') as f:
            self.url_cache = json.load(f)

    def dumpResourceCache(self):
        """ Persist the resource cache to disk. """
        with open(self.RESOURCE_CACHE_FILENAME, 'w') as f:
            json.dump(self.url_cache, f)

    def getUrl(self, url, accept='application/json'):
        """ Load @url (possibly from the cache) and return its contents as a string. """
        if url not in self.url_cache:
            opener = urllib2.build_opener(urllib2.HTTPHandler)
            request = urllib2.Request(url)
            request.add_header('Accept', accept)
            request.get_method = lambda: 'GET'
            print "Downloading", url
            fd = opener.open(request)
            self.url_cache[url] = fd.read()
            self.url_cache_updated = True
        return self.url_cache[url]

    def getPop(self, resource_name):
        """ Return the population as a float for the city identified by @resource_name. """
        data = self.getUrl("http://dbpedia.org/data/%s.json" % urllib.quote(resource_name.encode('utf8')))
        o = json.loads(data)
        resource = o['http://dbpedia.org/resource/'+resource_name]
        for rel in ['populationMetro', 'populationTotal']: # check these relationships, in this order
            if 'http://dbpedia.org/ontology/'+rel in resource:
                val = resource['http://dbpedia.org/ontology/'+rel][0]['value']
                return float(val)
        return None


if __name__ == '__main__':
    dbrl = DbpediaResourceLoader()
    with dbrl:
        print dbrl.getPop("New_York_City")
