# -*- coding: utf-8 -*-
"""
CIRpy

Python interface for the Chemical Identifier Resolver (CIR) by the CADD Group at the NCI/NIH.
https://github.com/mcs07/CIRpy
"""


import os
try:
    from urllib.request import urlopen
    from urllib.parse import urlparse, urlencode
    from urllib.parse import quote as urlquote
    from urllib.error import HTTPError
except ImportError:
    from urllib2 import urlopen, HTTPError
    from urllib2 import quote as urlquote
    from urllib import urlencode
    
from xml.etree import ElementTree as ET


__author__ = 'Matt Swain'
__email__ = 'm.swain@me.com'
__version__ = '1.0'
__license__ = 'MIT'


API_BASE = 'http://cactus.nci.nih.gov/chemical/structure'


def resolve(input, representation, resolvers=None, **kwargs):
    """ Resolve input to the specified output representation """
    resultdict = query(input, representation, resolvers, **kwargs)
    result = resultdict[0]['value'] if resultdict else None
    if result and len(result) == 1:
        result = result[0]
    return result


def query(input, representation, resolvers=None, **kwargs):
    """ Get all results for resolving input to the specified output representation """
    apiurl = API_BASE+'/%s/%s/xml' % (urlquote(input), representation)
    if resolvers:
        kwargs['resolver'] = ",".join(resolvers)
    if kwargs:
        apiurl+= '?%s' % urlencode(kwargs)
    result = []
    try:
        tree = ET.parse(urlopen(apiurl))
        for data in tree.findall(".//data"):
            datadict = {'resolver':data.attrib['resolver'],
                        'notation':data.attrib['notation'],
                        'value':[]}
            for item in data.findall("item"):
                datadict['value'].append(item.text)
            if len(datadict['value']) == 1:
                datadict['value'] = datadict['value'][0]
            result.append(datadict)
    except HTTPError:
        # TODO: Proper handling of 404, for now just returns None
        pass
    return result if result else None

def download(input, filename, format='sdf', overwrite=False, resolvers=None, **kwargs):
    """ Resolve and download structure as a file """
    kwargs['format'] = format
    if resolvers:
        kwargs['resolver'] = ",".join(resolvers)
    url = API_BASE+'/%s/file?%s' % (urlquote(input), urlencode(kwargs))
    try:
        servefile = urlopen(url)
        if not overwrite and os.path.isfile(filename):
            raise IOError("%s already exists. Use 'overwrite=True' to overwrite it." % filename)
        file = open(filename, "w")
        file.write(servefile.read())
        file.close()
    except urllib.error.HTTPError:
        # TODO: Proper handling of 404, for now just does nothing
        pass


class CacheProperty(object):
    """ Descriptor for caching Molecule properties. """

    def __init__(self, func):
        self._func = func
        self.__name__ = func.__name__
        self.__doc__ = func.__doc__

    def __get__(self, obj, obj_class=None):
        if obj is None: return None
        result = obj.__dict__[self.__name__] = self._func(obj)
        return result


class Molecule(object):
    """Class to hold and cache the structure information for a given CIR input"""

    def __init__(self, input, resolvers=None, **kwargs):
        """ Initialize with a query input """
        self.input = input
        self.resolvers = resolvers
        self.kwargs = kwargs

    def __repr__(self):
        return "Molecule(%r, %r)" % (self.input, self.resolvers)

    @CacheProperty
    def stdinchi(self): return resolve(self.input, 'stdinchi', self.resolvers, **self.kwargs)

    @CacheProperty
    def stdinchikey(self): return resolve(self.input, 'stdinchikey', self.resolvers, **self.kwargs)

    @CacheProperty
    def smiles(self): return resolve(self.input, 'smiles', self.resolvers, **self.kwargs)

    @CacheProperty
    def ficts(self): return resolve(self.input, 'ficts', self.resolvers, **self.kwargs)

    @CacheProperty
    def ficus(self): return resolve(self.input, 'ficus', self.resolvers, **self.kwargs)

    @CacheProperty
    def uuuuu(self): return resolve(self.input, 'uuuuu', self.resolvers, **self.kwargs)

    @CacheProperty
    def hashisy(self): return resolve(self.input, 'hashisy', self.resolvers, **self.kwargs)

    @CacheProperty
    def sdf(self): return resolve(self.input, 'sdf', self.resolvers, **self.kwargs)

    @CacheProperty
    def names(self): return resolve(self.input, 'names', self.resolvers, **self.kwargs)

    @CacheProperty
    def iupac_name(self): return resolve(self.input, 'iupac_name', self.resolvers, **self.kwargs)

    @CacheProperty
    def cas(self): return resolve(self.input, 'cas', self.resolvers, **self.kwargs)

    @CacheProperty
    def chemspider_id(self): return resolve(self.input, 'chemspider_id', self.resolvers, **self.kwargs)

    @CacheProperty
    def mw(self): return resolve(self.input, 'mw', self.resolvers, **self.kwargs)

    @CacheProperty
    def formula(self): return resolve(self.input, 'formula', self.resolvers, **self.kwargs)

    @CacheProperty
    def h_bond_donor_count(self): return resolve(self.input, 'h_bond_donor_count', self.resolvers, **self.kwargs)

    @CacheProperty
    def h_bond_acceptor_count(self): return resolve(self.input, 'h_bond_acceptor_count', self.resolvers, **self.kwargs)

    @CacheProperty
    def h_bond_center_count(self): return resolve(self.input, 'h_bond_center_count', self.resolvers, **self.kwargs)

    @CacheProperty
    def rule_of_5_violation_count(self): return resolve(self.input, 'rule_of_5_violation_count', self.resolvers, **self.kwargs)

    @CacheProperty
    def rotor_count(self): return resolve(self.input, 'rotor_count', self.resolvers, **self.kwargs)

    @CacheProperty
    def effective_rotor_count(self): return resolve(self.input, 'effective_rotor_count', self.resolvers, **self.kwargs)

    @CacheProperty
    def ring_count(self): return resolve(self.input, 'ring_count', self.resolvers, **self.kwargs)

    @CacheProperty
    def ringsys_count(self): return resolve(self.input, 'ringsys_count', self.resolvers, **self.kwargs)

    @property
    def image_url(self):
        url = API_BASE+'/%s/image' % urlquote(self.input)
        qsdict = self.kwargs
        if self.resolvers:
            qsdict['resolver'] = ",".join(self.resolvers)
        if qsdict:
            url += '?%s' % urlencode(qsdict)
        return url

    @property
    def twirl_url(self):
        url = API_BASE+'/%s/twirl' % urlquote(self.input)
        qsdict = self.kwargs
        if self.resolvers:
            qsdict['resolver'] = ",".join(self.resolvers)
        if qsdict:
            url += '?%s' % urlencode(qsdict)
        return url

    def download(self, filename, format='sdf', overwrite=False, resolvers=None, **kwargs):
        """ Download the resolved structure as a file """
        download(self.input, filename, format, overwrite, resolvers, **kwargs)

