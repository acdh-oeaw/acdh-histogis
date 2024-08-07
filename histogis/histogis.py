import datetime
import os
import glob
import re
import requests
import json
import lxml.etree as ET

from json import JSONDecodeError


HISTOGIS_URL = "https://histogis.acdh.oeaw.ac.at/api/"


class HistoGis:
    """Main class to interact with HistoGIS TempSpatial Objects"""

    def test_connection(self):
        """Checks if a GET request to histogis_url returns status code 200"""
        try:
            r = requests.get(self.histogis_url)
        except Exception as e:
            print(e)
            return False
        if r.status_code == 200:
            return True
        else:
            print(r.status_code)
            return False

    def count(self):
        """returns the number of available TempSpatial objects"""
        r = requests.get(self.list_endpoint)
        result = r.json()["count"]
        return result

    def query(self, lat=48.2894, lng=14.304, when="1860-12-12", polygon=False):
        """Makes a spatial lookup and returns a list of matching objects
        :param lat: Latitude of the place to query for
        :param lng: Langitude of the place to query for
        :param when: An iso-date string
        :param polygon: If true, the whole geojson is returned, only the properties
        :return: A list of matching objects
        """
        params = {"lat": lat, "lng": lng, "format": "json"}
        if when is not None:
            # ToDo: check if when casts to iso date
            params["when"] = when
        r = requests.get(self.list_endpoint, params=params)
        print(r.json())
        if polygon:
            return r.json()
        else:
            try:
                return r.json()["features"][0]["properties"]
            except IndexError:
                return self.empty_result

    def fetch_geonames_data(self, geonames="http://www.geonames.org/2772400/linz.html"):
        """returns name and coordinates for the passed in geonames identifier
        :param geonames: Any kind of geonames id, can be just the geonames id (as string)\
        or any geonames URI like http://www.geonames.org/2772400/linz.html
        :return: a dict with keys 'name', 'lat' and lng.
        """
        geonames_id = re.search(r"\d+", geonames).group()
        url = f"http://sws.geonames.org/{geonames_id}/about.rdf"
        rdf = ET.parse(url)
        lat = rdf.xpath(".//wgs84_pos:lat/text()", namespaces=self.nsmap)[0]
        lng = rdf.xpath(".//wgs84_pos:long/text()", namespaces=self.nsmap)[0]
        name = rdf.xpath(".//gn:name/text()", namespaces=self.nsmap)[0]
        return {"name": name, "lat": lat, "lng": lng}

    def fetch_gnd_data(self, gnd="http://d-nb.info/gnd/4066009-6/about/lds.rdf"):
        """returns name and coordinates for the passed in gnd identifier
        :param gnd: Any kind of gnd id, can be just the gnd id (as string)\
        or any geonames URI like http://d-nb.info/gnd/4066009-6/about/lds.rdf
        :return: a dict with keys 'name', 'lat' and lng.
        """
        gnd_id = re.search(r"(\d+[A-Z0-9\-]+)", gnd).group()
        url = f"http://d-nb.info/gnd/{gnd_id}/about/lds.rdf"
        res = requests.get(url)
        rdf = ET.fromstring(res.content)
        lat_long = rdf.xpath(".//geo:asWKT/text()", namespaces=self.nsmap)[0]
        lat_long_match = re.search(r"\+0?([0-9\.]+)\s+\+0?([0-9\.]+)", lat_long)
        if not lat_long_match:
            raise ValueError("GND RDF did not contain coordinates.")
        lng = lat_long_match.group(1)
        lat = lat_long_match.group(2)
        name = rdf.xpath(
            ".//gndo:preferredNameForThePlaceOrGeographicName/text()",
            namespaces=self.nsmap,
        )[0]
        return {"name": name, "lat": lat, "lng": lng}

    def fetch_wikidata_data(self, wikidata="https://www.wikidata.org/entity/Q41329"):
        """returns name and coordinates for the passed in wikidata identifier
        :param wikidata: Any kind of wikidata id, can be just the wikidata id (as string)\
        or any wikidata URI like https://www.wikidata.org/entity/Q41329
        :return: a dict with keys 'name', 'lat' and lng.
        """
        wikidata_id = re.search(r"(Q\d+)", wikidata).group()
        url = f"https://wikidata.org/entity/{wikidata_id}.rdf"
        res = requests.get(url)
        rdf = ET.fromstring(res.content)
        lat_long = rdf.xpath(".//wdt:P625/text()", namespaces=self.nsmap)[0]
        lat_long_match = re.search(r"0?([0-9\.]+)\s+0?([0-9\.]+)", lat_long)
        if not lat_long_match:
            raise ValueError("Wikidata RDF did not contain coordinates.")
        lng = lat_long_match.group(1)
        lat = lat_long_match.group(2)
        name = rdf.xpath(
            f".//rdf:Description[@rdf:about='http://www.wikidata.org/entity/{wikidata_id}']/rdfs:label[@xml:lang='de']/text()",  # noqa:E501
            namespaces=self.nsmap,
        )[0]
        return {"name": name, "lat": lat, "lng": lng}

    def query_by_service_id(
        self,
        service=None,
        id="https://www.geonames.org/2772400/",
        when="1860-12-12",
        polygon=False,
    ):
        """Makes a spatial lookup by geonames id a list of matching objects
        :param gnd: Any kind of geonames id, can be just the geonames id (as string)\
        or any geonames URI like http://www.geonames.org/2772400/linz.html
        :param when: An iso-date string
        :param polygon: If true, the whole geojson is returned, only the properties
        :return: A list of matching objects
        """
        if service is None:
            for s in self.map_url_service.keys():
                if s in id:
                    service = self.map_url_service[s]
        coords = getattr(self, f"fetch_{service}_data")(id)
        print(coords)
        return self.query(
            lat=coords["lat"], lng=coords["lng"], when=when, polygon=polygon
        )

    def dump_all(self, verbose=True):
        """Dumps HistoGIS data to GeoJSONL; a GeoJSON per line. Can take quite a while. So only/
        use if really necessary. Alternatively go to ??? to download the latest data dump
        :return: A text file.
        """
        file = "histogis_dump__{date:%Y-%m-%d__%H-%M-%S}.txt".format(
            date=datetime.datetime.now()
        )
        next_ft = self.list_endpoint
        with open(file, "w", encoding="utf-8") as f:
            while next_ft:
                r = requests.get(next_ft)
                ft = r.json()["features"]
                f.write(f"{json.dumps(ft)}\n")
                if verbose:
                    print(f"writing to file: {next_ft}")
                try:
                    next_ft = r.json()["next"]
                except JSONDecodeError:
                    next_ft = None
        return file

    def dump_all_file_per_feature(self, verbose=True, path="."):
        """Dumps HistoGIS data to GeoJSON; one file per object. Can take quite a while. So only/
        use if really necessary. Alternatively go to https://doi.org/10.5281/zenodo.2615387\
        to download the latest data dump
        :return: A text file.
        """

        next_ft = self.list_endpoint
        counter = 0
        while next_ft:
            r = requests.get(next_ft)
            ft = r.json()["features"][0]
            ft_slugged = ft["properties"]["slugged_name"]
            file = f"{ft_slugged}.geojson"
            file = os.path.join(path, file)
            counter += 1
            if verbose:
                print(f"{file}")
            with open(file, "w", encoding="utf-8") as f:
                f.write(f"{json.dumps(ft)}")
                try:
                    next_ft = r.json()["next"]
                except JSONDecodeError:
                    print("error")
                    next_ft = None
        return f"done: downloaded {counter} items"

    def __init__(self, histogis_url=HISTOGIS_URL):
        """__init__

        :param histogis_url: Url pointing to a HistoGIS-TempSpatial endpoint
        """
        if histogis_url.endswith("/"):
            self.histogis_url = histogis_url
        else:
            self.histogis_url = f"{histogis_url}/"
        self.status = self.test_connection()
        self.list_endpoint = f"{self.histogis_url}tempspatial/?format=json"
        self.query_endpoint = f"{self.histogis_url}"
        self.empty_result = {
            "count": 0,
            "features": [],
            "next": None,
            "previous": None,
            "type": "FeatureCollection",
        }
        self.map_url_service = {
            "geonames": "geonames",
            "d-nb": "gnd",
            "wikidata": "wikidata",
        }
        self.nsmap = {
            "wgs84_pos": "http://www.w3.org/2003/01/geo/wgs84_pos#",
            "gn": "http://www.geonames.org/ontology#",
            "rdf": "http://www.w3.org/1999/02/22-rdf-syntax-ns#",
            "rdfs": "http://www.w3.org/2000/01/rdf-schema#",
            "tei": "http://www.tei-c.org/ns/1.0",
            "xml": "http://www.w3.org/XML/1998/namespace",
            "geo": "http://www.opengis.net/ont/geosparql#",
            "gndo": "http://d-nb.info/standards/elementset/gnd#",
            "wdt": "http://www.wikidata.org/prop/direct/",
        }


def merge_single_files(
    file="histogis-dump.jsonl", source_path="single_files", verbose=True
):
    """
    writes all geojson from the given folder into a JSONL file
    :path: Path to folder containing the .geojson files
    :return: A JSONL file.
    """
    files = sorted(glob.glob(f"./{source_path}/*.geojson"))
    with open(file, "w", encoding="utf-8") as f:
        for x in files:
            with open(x) as json_file:
                data = json.load(json_file)
                f.write(f"{json.dumps(data)}\n")
    return file
