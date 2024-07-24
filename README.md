# acdh-histogis

acdh-histogis is a python package providing a high level api to interact with [HistoGIS](https://histogis.acdh.oeaw.ac.at/)


## Installation
```bash
pip install acdh-histogis
```


## Use:

```python

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
```

## Develop

* clone the repo
* create and activate virtual env, e.g. 
```bash
python -m venv venv
source venv/bin/activate
```
* install package and dev-requiements 
```bash
pip install -e .[dev]
```
* run tests: 
```
coverage run -m pytest -v
```

## build the docs

* run 
```bash
./build_docs.sh
```