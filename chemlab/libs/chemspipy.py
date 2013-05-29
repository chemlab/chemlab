# -*- coding: utf-8 -*-
"""
ChemSpiPy

Python wrapper for the ChemSpider API.
https://github.com/mcs07/ChemSpiPy

Forked from ChemSpiPy by Cameron Neylon
https://github.com/cameronneylon/ChemSpiPy
"""

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


TOKEN = 'INSERT YOUR TOKEN'


class Compound(object):
    """ A class for retrieving record details about a compound by CSID.

    The purpose of this class is to provide access to various parts of the
    ChemSpider API that return information about a compound given its CSID.
    Information is loaded lazily when requested, and cached for future access.
    """

    def __init__(self,csid):
        """ Initialize with a CSID as an int or str """
        if type(csid) is str and csid.isdigit():
            self.csid = csid
        elif type(csid) == int:
            self.csid = str(csid)
        else:
            raise TypeError('Compound must be initialised with a CSID as an int or str')

        self._imageurl = None
        self._mf = None
        self._smiles = None
        self._inchi = None
        self._inchikey = None
        self._averagemass = None
        self._molecularweight = None
        self._monoisotopicmass = None
        self._nominalmass = None
        self._alogp = None
        self._xlogp = None
        self._commonname = None
        self._image = None
        self._mol = None
        self._mol3d = None

    def __repr__(self):
        return "Compound(%r)" % self.csid

    @property
    def imageurl(self):
        """ Return the URL of a png image of the 2D structure """
        if self._imageurl is None:
            self._imageurl = 'http://www.chemspider.com/ImagesHandler.ashx?id=%s' % self.csid
        return self._imageurl

    @property
    def mf(self):
        """ Retrieve molecular formula from ChemSpider """
        if self._mf is None:
            self.loadextendedcompoundinfo()
        return self._mf

    @property
    def smiles(self):
        """ Retrieve SMILES string from ChemSpider """
        if self._smiles is None:
            self.loadextendedcompoundinfo()
        return self._smiles

    @property
    def inchi(self):
        """ Retrieve InChi string from ChemSpider """
        if self._inchi is None:
            self.loadextendedcompoundinfo()
        return self._inchi

    @property
    def inchikey(self):
        """ Retrieve InChi string from ChemSpider """
        if self._inchikey is None:
            self.loadextendedcompoundinfo()
        return self._inchikey

    @property
    def averagemass(self):
        """ Retrieve average mass from ChemSpider """
        if self._averagemass is None:
            self.loadextendedcompoundinfo()
        return self._averagemass

    @property
    def molecularweight(self):
        """ Retrieve molecular weight from ChemSpider """
        if self._molecularweight is None:
            self.loadextendedcompoundinfo()
        return self._molecularweight

    @property
    def monoisotopicmass(self):
        """ Retrieve monoisotropic mass from ChemSpider """
        if self._monoisotopicmass is None:
            self.loadextendedcompoundinfo()
        return self._monoisotopicmass

    @property
    def nominalmass(self):
        """ Retrieve nominal mass from ChemSpider """
        if self._nominalmass is None:
            self.loadextendedcompoundinfo()
        return self._nominalmass

    @property
    def alogp(self):
        """ Retrieve ALogP from ChemSpider """
        if self._alogp is None:
            self.loadextendedcompoundinfo()
        return self._alogp

    @property
    def xlogp(self):
        """ Retrieve XLogP from ChemSpider """
        if self._xlogp is None:
            self.loadextendedcompoundinfo()
        return self._xlogp

    @property
    def commonname(self):
        """ Retrieve common name from ChemSpider """
        if self._commonname is None:
            self.loadextendedcompoundinfo()
        return self._commonname

    def loadextendedcompoundinfo(self):
        """ Load extended compound info from the Mass Spec API """
        apiurl = 'http://www.chemspider.com/MassSpecAPI.asmx/GetExtendedCompoundInfo?CSID=%s&token=%s' % (self.csid,TOKEN)
        response = urlopen(apiurl)
        tree = ET.parse(response)
        mf = tree.find('{http://www.chemspider.com/}MF')
        self._mf = mf.text if mf is not None else None
        smiles = tree.find('{http://www.chemspider.com/}SMILES')
        self._smiles = smiles.text if smiles is not None else None
        inchi = tree.find('{http://www.chemspider.com/}InChI')
        self._inchi = inchi.text if inchi is not None else None
        inchikey = tree.find('{http://www.chemspider.com/}InChIKey')
        self._inchikey = inchikey.text if inchikey is not None else None
        averagemass = tree.find('{http://www.chemspider.com/}AverageMass')
        self._averagemass = float(averagemass.text) if averagemass is not None else None
        molecularweight = tree.find('{http://www.chemspider.com/}MolecularWeight')
        self._molecularweight = float(molecularweight.text) if molecularweight is not None else None
        monoisotopicmass = tree.find('{http://www.chemspider.com/}MonoisotopicMass')
        self._monoisotopicmass = float(monoisotopicmass.text) if monoisotopicmass is not None else None
        nominalmass = tree.find('{http://www.chemspider.com/}NominalMass')
        self._nominalmass = float(nominalmass.text) if nominalmass is not None else None
        alogp = tree.find('{http://www.chemspider.com/}ALogP')
        self._alogp = float(alogp.text) if alogp is not None else None
        xlogp = tree.find('{http://www.chemspider.com/}XLogP')
        self._xlogp = float(xlogp.text) if xlogp is not None else None
        commonname = tree.find('{http://www.chemspider.com/}CommonName')
        self._commonname = commonname.text if commonname is not None else None

    @property
    def image(self):
        """ Return string containing PNG binary image data of 2D structure image """
        if self._image is None:
            apiurl = 'http://www.chemspider.com/Search.asmx/GetCompoundThumbnail?id=%s&token=%s' % (self.csid,TOKEN)
            response = urlopen(apiurl)
            tree = ET.parse(response)
            self._image = tree.getroot().text
        return self._image

    @property
    def mol(self):
        """ Return record in MOL format """
        if self._mol is None:
            apiurl = 'http://www.chemspider.com/MassSpecAPI.asmx/GetRecordMol?csid=%s&calc3d=false&token=%s' % (self.csid,TOKEN)
            response = urlopen(apiurl)
            tree = ET.parse(response)
            self._mol = tree.getroot().text
        return self._mol

    @property
    def mol3d(self):
        """ Return record in MOL format with 3D coordinates calculated """
        if self._mol3d is None:
            apiurl = 'http://www.chemspider.com/MassSpecAPI.asmx/GetRecordMol?csid=%s&calc3d=true&token=%s' % (self.csid,TOKEN)
            response = urlopen(apiurl)
            tree = ET.parse(response)
            self._mol3d = tree.getroot().text
        return self._mol3d


def find(query):
    """ Search by Name, SMILES, InChI, InChIKey, etc. Returns first 100 Compounds """
    assert type(query) == str or type(query) == str, 'query not a string object'
    searchurl = 'http://www.chemspider.com/Search.asmx/SimpleSearch?query=%s&token=%s' % (urlquote(query), TOKEN)
    response = urlopen(searchurl)
    tree = ET.parse(response)
    elem = tree.getroot()
    csid_tags = elem.getiterator('{http://www.chemspider.com/}int')
    compoundlist = []
    for tag in csid_tags:
        compoundlist.append(Compound(tag.text))
    return compoundlist if compoundlist else None


def find_one(query):
    """ Search by Name, SMILES, InChI, InChIKey, etc. Returns a single Compound """
    compoundlist = find(query)
    return compoundlist[0] if compoundlist else None

