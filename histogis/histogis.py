import re
import requests
import lxml.etree as ET

HISTOGIS_URL = "https://histogis.acdh.oeaw.ac.at/api"


class HistoGis():
    """Main class to interact with HistoGIS TempSpatial Objects"""

    def test_connection(self):
        """ Checks if a GET request to histogis_url returns status code 200 """
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
        result = r.json()['count']
        return result

    def query(self, lat=48.2894, lng=14.304, when='1860-12-12', polygon=False):
        """Makes a spatial lookup and returns a list of matching objects
        :param lat: Latitude of the place to query for
        :param lng: Langitude of the place to query for
        :param when: An iso-date string
        :param polygon: If true, the whole geojson is returned, only the properties
        :return: A list of matching objects
        """

        if when is not None:
            # ToDo check if when casts to iso date
            url = "{}?lat={}&lng={}&when={}".format(
                self.query_endpoint, lat, lng, when
            )
        else:
            url = "{}?lat={}&lng={}&format".format(
                self.query_endpoint, lat, lng
            )
        url = "{}&format=json".format(url)
        r = requests.get(url)
        if polygon:
            return r.json()
        else:
            try:
                return r.json()['features'][0]['properties']
            except IndexError:
                return self.empty_result

    def fetch_gnd_rdf(self, gnd="http://www.geonames.org/2772400/linz.html"):
        """returns name and coordinates for the passed in geonames identifier
        :param gnd: Any kind of geonames id, can be just the geonames id (as string)\
        or any geonames URI like http://www.geonames.org/2772400/linz.html
        :return: a dict with keys 'name', 'lat' and lng.
        """
        gnd_id = re.search(r"\d+", gnd).group()
        url = "http://sws.geonames.org/{}/about.rdf".format(gnd_id)
        rdf = ET.parse(url)
        lat = rdf.xpath(".//wgs84_pos:lat/text()", namespaces=self.nsmap)[0]
        lng = rdf.xpath(".//wgs84_pos:long/text()", namespaces=self.nsmap)[0]
        name = rdf.xpath(".//gn:name/text()", namespaces=self.nsmap)[0]
        return {
            "name": name,
            "lat": lat,
            "lng": lng
        }

    def query_by_geonames_id(
        self, gnd="https://www.geonames.org/2772400/", when='1860-12-12', polygon=False
    ):
        """Makes a spatial lookup by geonames id a list of matching objects
        :param gnd: Any kind of geonames id, can be just the geonames id (as string)\
        or any geonames URI like http://www.geonames.org/2772400/linz.html
        :param when: An iso-date string
        :param polygon: If true, the whole geojson is returned, only the properties
        :return: A list of matching objects
        """
        coords = self.fetch_gnd_rdf(gnd)
        return self. query(lat=coords['lat'], lng=coords['lng'], when=when, polygon=polygon)

    def __init__(self, histogis_url=HISTOGIS_URL):
        """__init__

        :param histogis_url: Url pointing to a HistoGIS-TempSpatial endpoint
        """
        if histogis_url.endswith('/'):
            self.histogis_url = histogis_url
        else:
            self.histogis_url = "{}/".format(histogis_url)
        self.status = self.test_connection()
        self.list_endpoint = "{}tempspatial/?format=json".format(self.histogis_url)
        self.query_endpoint = "{}where-was/".format(self.histogis_url)
        self.empty_result = {
            'count': 0,
            'features': [],
            'next': None,
            'previous': None,
            'type': 'FeatureCollection'
        }
        self.nsmap = {
            'wgs84_pos': "http://www.w3.org/2003/01/geo/wgs84_pos#",
            'gn': "http://www.geonames.org/ontology#",
            'rdf': "http://www.w3.org/1999/02/22-rdf-syntax-ns#",
            'tei': "http://www.tei-c.org/ns/1.0",
            'xml': "http://www.w3.org/XML/1998/namespace",
        }
