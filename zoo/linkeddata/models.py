from django.db import models
from animals.models import Species

class ExternalIdentifier(models.Model):
    "Pulled from http://ids.freebaseapps.com/get_ids?id=/en/tiger"
    species = models.ForeignKey(Species, related_name='external_identifiers')
    source = models.CharField(max_length = 255, db_index = True)
    namespace = models.CharField(max_length = 255, db_index = True)
    key = models.CharField(max_length = 255, db_index = True)
    uri = models.CharField(max_length = 255, blank = True)
    order = models.IntegerField(default = 0, db_index = True)
    
    class Meta:
        ordering = ('order',)
    
    def __unicode__(self):
        return u'%s:%s:%s' % (self.source, self.namespace, self.key)

class WikipediaAbstract(models.Model):
    species = models.ForeignKey(Species, related_name = 'wikipedia_abstracts')
    abstract = models.TextField()
    
    def __unicode__(self):
        return u'Wikipedia abstract for %s: %s...' % (
            self.species, self.abstract[:30]
        )

from xml.etree import ElementTree as ET
import urllib

dbpedia_endpoint = "http://dbpedia.org/sparql?"
ns = {'ns': '{http://www.w3.org/2005/sparql-results#}'}
result_xpath ='%(ns)sresults/%(ns)sresult/%(ns)sbinding/%(ns)sliteral' % ns

def wikipedia_abstract_from_dbpedia(dbpedia_key):
    sparql = """
    SELECT ?abstract
    WHERE {
    { <http://dbpedia.org/resource/%s> <http://dbpedia.org/property/abstract> ?abstract .
    FILTER langMatches( lang(?abstract), 'en') }
    }
    """ % dbpedia_key
    url = dbpedia_endpoint + urllib.urlencode({'query': sparql})
    et = ET.parse(urllib.urlopen(url))
    el = et.find(result_xpath)
    if el is not None:
        return el.text
    else:
        return None
