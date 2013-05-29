'''Database for toxnet'''
from .base import AbstractDB, EntryNotFound

# Python 2-3 compatibility
try:
    from urllib.parse import quote_plus
    from urllib.request import urlopen
except ImportError:
    from urllib import quote_plus
    from urllib2 import urlopen

import re

class ToxNetDB(AbstractDB):
    def __init__(self):
        self.baseurl = 'http://toxgate.nlm.nih.gov'


    def get(self, feature, query):
        searchurl = self.baseurl + '/cgi-bin/sis/search/x?dbs+hsdb:%s'%quote_plus(query)
        result = urlopen(searchurl).read()
        
        try:
            result= str(result, 'utf-8')
        except TypeError:
            pass
        
        if not result:
            raise EntryNotFound()
        
        #print result
        firstresult = re.findall(r'\<Id>(.*?)\</Id>', result)[0].split()[0]

        retrieveurl = self.baseurl + '/cgi-bin/sis/search/r?dbs+hsdb:@term+@DOCNO+%s'%firstresult
        result = urlopen(retrieveurl).read()
        
        try:
            result = str(result, 'utf-8')
        except TypeError:
            pass
        
        tocregex = 'SRC="(.*?)"'
        basesearch = re.findall(tocregex, result)[0]
        basesearch = ':'.join(basesearch.split(':')[:-1])
        
        if feature == 'boiling point':
            bprequest = urlopen(self.baseurl + basesearch + ':bp').read()
            # Massaging this request is not easy
            
            try: # python3
                bprequest = str(bprequest, 'utf-8')
            except TypeError:
                pass
            
            res = re.findall(r">\s*(.*?)\s*deg C", bprequest)
            #print res
            return float(res[0])
        
        if feature == 'melting point':
            bprequest = urlopen(self.baseurl + basesearch + ':mp').read()
            try: # python3
                bprequest = str(bprequest, 'utf-8')
            except TypeError:
                pass
            
            # Massaging this request is not easy
            res = re.findall(r">\s*(.*?)\s*deg C", bprequest)
            return float(res[0])
        
        