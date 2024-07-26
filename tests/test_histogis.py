import unittest
from histogis import HistoGis as hg


class TestTestTest(unittest.TestCase):
    """Tests for `acdh-wikidata-pyutils` package."""

    def test_001_testsetup(self):
        self.assertTrue(True)

    def test_002_query_by_service_id(self):
        item = hg().query_by_service_id(
            id="https://www.geonames.org/2772400/", when="1860-12-12", polygon=False
        )
        self.assertTrue("name" in item.keys())
        self.assertFalse("features" in item.keys())

    def test_003_query_by_service_id(self):
        item = hg().query_by_service_id(
            id="https://www.geonames.org/2772400/", when="1860-12-12", polygon=True
        )
        self.assertFalse("name" in item.keys())
        self.assertTrue("features" in item.keys())

    def test_004_query_by_service_id(self):
        item = hg().query_by_service_id(
            id="https://www.geonames.org/2772400/", when=None, polygon=True
        )
        self.assertFalse("name" in item.keys())
        self.assertTrue("features" in item.keys())

    def test_004_count(self):
        item = hg().count()
        self.assertTrue(item > 0)
