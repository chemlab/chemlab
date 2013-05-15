'''Database for toxnet'''
from .base import AbstractDB, EntryNotFound
import urllib
import re

class ToxNetDB(AbstractDB):
    def __init__(self):
        self.baseurl = 'http://toxgate.nlm.nih.gov'


    def get(self, feature, query):
        searchurl = self.baseurl + '/cgi-bin/sis/search/x?dbs+hsdb:%s'%urllib.quote_plus(query)
        result = urllib.urlopen(searchurl).read()
        
        if not result:
            raise EntryNotFound()
        
        #print result
        firstresult = re.findall(r'\<Id>(.*?)\</Id>', result)[0].split()[0]

        retrieveurl = self.baseurl + '/cgi-bin/sis/search/r?dbs+hsdb:@term+@DOCNO+%s'%firstresult
        result = urllib.urlopen(retrieveurl).read()
        
        tocregex = r'SRC="(.*?)"'
        basesearch = re.findall(tocregex, result)[0]
        basesearch = ':'.join(basesearch.split(':')[:-1])
        
        if feature == 'boiling point':
            bprequest = urllib.urlopen(self.baseurl + basesearch + ':bp').read()
            # Massaging this request is not easy
            #print bprequest
            res = re.findall(">\s*(.*?)\s*deg C", bprequest)
            #print res
            return float(res[0])
        
        if feature == 'melting point':
            bprequest = urllib.urlopen(self.baseurl + basesearch + ':mp').read()
            # Massaging this request is not easy
            #print bprequest
            res = re.findall(">\s*(.*?)\s*deg C", bprequest)
            #print res
            return float(res[0])
        
        