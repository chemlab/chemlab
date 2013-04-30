================
Database Support
================

Typing every time your molecules and system is not fun nor efficient,
for this reason chemlab provides ready-to-use database utilities.

Databases in chemlab can store arbitrary data, that can be retrieved
by using the get method. The following is an example retrieving a
molecular structure from CIR
http://cactus.nci.nih.gov/chemical/structure , the chemical resolve
identifier website::

    from chemlab.db.cirdb import CirDB
    mol = CirDB().get("molecule", "aspirine")

.. note:: CirDB uses internally the CirPy wrapper
          https://github.com/mcs07/CIRpy , all credits go to the
          author.

Chemlab includes also his own database for data as well as some
molecules. For example to get the vdw radii (the data was taken from
OpenBabel) you can::

    from chemlab.db import ChemlabDB
    
    cdb = ChemlabDB()
    vdw = cdb.get("data", "vdwdict")
    vdw['He']

For more information refer to the :py:class:`chemlab.db.ChemlabDB`
documentation.

.. seealso:: :doc:`api/chemlab.db`

.. _localdb:

Having your own molecular database
----------------------------------

It may happen that you have your most-frequently used collection of
molecules and systems. Chemlab provides a serialization system that
let you easily dump your objects in a directory and retrieve them by
using a local database.

This is achieved by the class :py:class:`chemlab.db.LocalDB`::

    from chemlab.db import LocalDB
    
    ldb = LocalDB('/path/to/yourdb')
    # Generate/retrieve some molecule
    
    ldb.store('molecule', 'examplemol',  mol)
    ldb.store('system', 'examplesys',  sys)

The method :py:meth:`chemlab.db.LocalDB.store` takes a first argument
that can be ither molecule or system, as a second argument the key
used to store/retrieve the entry and finally the object to store.

You can, at a later time retrieve the entries in this way::
  
    from chemlab.db import LocalDB
    
    ldb = LocalDB('/path/to/yourdb')
    mol = ldb.get('molecule', 'examplemol')
    s = ldb.get('system', 'examplesys')

The molecules files are serialized using the json format and stored in
a very simple directory structure. For the previous example, the
database directory would look like this::

  /path/to/yourdb/
          - molecule/
	    - examplemol.json
          - system/
            - examplesys.json

The reason for such a simple structure is that in the future it will
be easy to define custom-made remote database, for example you could
have a community mantained github repo with commonly used molecules
and data, that can be directly accessed by chemlab (everybody is
welcome to develop such an extension). On top of that, you can
copy-paste json molecule files without having to do any migration.

.. seealso:: :doc:`api/chemlab.db`
