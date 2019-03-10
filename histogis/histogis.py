import requests

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
                return r.json()
            except IndexError:
                return self.empty_result

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
