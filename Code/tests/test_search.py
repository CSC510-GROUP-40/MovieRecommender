import sys
sys.path.append('../recommenderapp')
from recommenderapp.prediction_scripts.search import Search
import unittest
import warnings
import sys
import os

sys.path.append("../")

warnings.filterwarnings("ignore")


class Tests(unittest.TestCase):
    def testSearchToy(self):
        search_word = "toy"
        search = Search()
        filtered_dict = search.resultsTop10(search_word)
        expected_resp = [
            "Toy Story (1995)",
            "Toys (1992)",
            "Toy Story 2 (1999)",
            "Toy, The (1982)",
            "Toy Soldiers (1991)",
            "Toy Story 3 (2010)",
            "Babes in Toyland (1961)",
            "Babes in Toyland (1934)",
        ]
        self.assertTrue(filtered_dict == expected_resp)

    def testSearchLove(self):
        search_word = "love"
        search = Search()
        filtered_dict = search.resultsTop10(search_word)
        expected_resp = [
            "Love & Human Remains (1993)",
            "Love Affair (1994)",
            "Love and a .45 (1994)",
            "Love in the Afternoon (1957)",
            "Love Bug, The (1969)",
            "Love Jones (1997)",
            "Love and Other Catastrophes (1996)",
            "Love Serenade (1996)",
            "Love and Death on Long Island (1997)",
            "Love Is the Devil (1998)",
        ]
        self.assertTrue(filtered_dict == expected_resp)

    def testSearchGibberish(self):
        search_word = "gibberish"
        search = Search()
        filtered_dict = search.resultsTop10(search_word)
        expected_resp = []
        self.assertTrue(filtered_dict == expected_resp)

    def testSearch1995(self):
        search_word = "1995"
        search = Search()
        filtered_dict = search.resultsTop10(search_word)
        expected_resp = [
            "Toy Story (1995)",
            "Jumanji (1995)",
            "Grumpier Old Men (1995)",
            "Waiting to Exhale (1995)",
            "Father of the Bride Part II (1995)",
            "Heat (1995)",
            "Sabrina (1995)",
            "Tom and Huck (1995)",
            "Sudden Death (1995)",
            "GoldenEye (1995)",
        ]
        self.assertTrue(filtered_dict == expected_resp)

    def testSearchSpecialCharacters(self):
        search_word = "!@#$%^&*()"
        search = Search()
        filtered_dict = search.resultsTop10(search_word)
        expected_resp = []
        self.assertTrue(
            filtered_dict == expected_resp,
            "Search with special characters should result in an empty list or a specific behavior")

    def testSearchLongString(self):
        search_word = "a" * 1000
        search = Search()
        filtered_dict = search.resultsTop10(search_word)
        expected_resp = []
        self.assertTrue(
            filtered_dict == expected_resp,
            "Long search terms should result in an empty list or a specific behavior")

    def testSearchTermNotFound(self):
        search_word = "nonexistentterm"
        search = Search()
        filtered_dict = search.resultsTop10(search_word)
        expected_resp = []
        self.assertTrue(
            filtered_dict == expected_resp,
            "Search term not found should result in an empty list or a specific behavior")

    def testSearchWhitespace(self):
        search_word = "  whitespace  "
        search = Search()
        filtered_dict = search.resultsTop10(search_word)
        expected_resp = []
        self.assertTrue(
            filtered_dict == expected_resp,
            "Search term with leading and trailing whitespaces should result in an empty list of results")

    def testSearchHTMLJavaScriptTags(self):
        search_word = "<script>alert('Hello');</script>"
        search = Search()
        filtered_dict = search.resultsTop10(search_word)
        expected_resp = []
        self.assertTrue(
            filtered_dict == expected_resp,
            "Search term with HTML/JavaScript tags should result in an empty list of results")

    def testSearchUnicodeCharacters(self):
        search_word = "😊"
        search = Search()
        filtered_dict = search.resultsTop10(search_word)
        expected_resp = []
        self.assertTrue(
            filtered_dict == expected_resp,
            "Search term with Unicode characters should result in an empty list of results")


if __name__ == "__main__":
    unittest.main()
