Readme
======

.. image:: https://badge.fury.io/py/acdh-histogis.svg
    :target: https://badge.fury.io/py/acdh-histogis

acdh-histogis is a python package providing a high level api to interact with [HistoGIS](https://histogis.acdh.oeaw.ac.at/)


Installation
------------

`pip install acdh-histogis`


Use:
------------

.. code-block:: python

    from histogis.histogis import HistoGis as hg

    hg().query(
        lat=48.2894, lng=14.304, when='1860-12-12', polygon=False
    )

    hg().query_by_geonames_id(
        gnd='https://www.geonames.org/2772400/',
        when='1860-12-12',
        polygon=False,
    )


```


Licensing
---------

All code unless otherwise noted is licensed under the terms of the MIT License (MIT). Please refer to the file LICENSE in the root directory of this repository.
