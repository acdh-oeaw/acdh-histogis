Readme
======

.. image:: https://badge.fury.io/py/acdh-histogis.svg
    :target: https://badge.fury.io/py/acdh-histogis

acdh-histogis is a python package providing a high level api to interact with [HistoGIS](https://histogis.acdh.oeaw.ac.at/)


Installation
------------

    pip install acdh-histogis


Use:
------------

.. code-block:: python

    from histogis.histogis import HistoGis as hg

    # by geonames (id or URL)

    hg().query_by_service_id(id="https://www.geonames.org/2772400/", when='1860-12-12', polygon=False)

    # by wikidata (id or URL)

    hg().query_by_service_id(id="https://www.wikidata.org/wiki/Q41329", when='1860-12-12', polygon=False)

    # by GND (id or URL)

    hg().query_by_service_id(service="gnd", id="4074255-6", when='1860-12-12', polygon=False)

    # returns:

    {
    'id': 8118,
    'wikidata_id': '',
    'name': 'Linz (Stadt)',
    'alt_name': '',
    'source': 'https://histogis.acdh.oeaw.ac.at/api/source/93/?format=json',
    'source_name': 'Cisleithania Districts 1880',
    'administrative_unit': 'https://histogis.acdh.oeaw.ac.at/api/skosconcepts/135/?format=json',
    'adm_name': 'Statutarstadt',
    'start_date': '1850-01-01',
    'end_date': '1918-10-31',
    ...
    }



Licensing
---------

All code unless otherwise noted is licensed under the terms of the MIT License (MIT). Please refer to the file LICENSE in the root directory of this repository.
