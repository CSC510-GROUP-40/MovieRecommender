import sys
sys.path.append('../recommenderapp')
from recommenderapp.prediction_scripts.item_based import recommendForNewUser
import unittest
import warnings
import sys

sys.path.append("../")

warnings.filterwarnings("ignore")


class Tests(unittest.TestCase):
    def testToyStory(self):
        ts = [
            {"title": "Toy Story (1995)", "rating": 5.0},
        ]
        recommendations = recommendForNewUser(ts)
        self.assertTrue("Toy Story 3 (2010)" in recommendations)

    def testToyStoryNeg(self):
        ts = [
            {"title": "Toy Story (1995)", "rating": 5.0},
        ]
        recommendations = recommendForNewUser(ts)
        self.assertFalse("Inception" in recommendations)

    def testKunfuPanda(self):
        ts = [
            {"title": "Kung Fu Panda (2008)", "rating": 5.0},
        ]
        recommendations = recommendForNewUser(ts)
        self.assertTrue("Toy Story (1995)" in recommendations)

    def testKunfuPandaNeg(self):
        ts = [
            {"title": "Kung Fu Panda (2008)", "rating": 5.0},
        ]
        recommendations = recommendForNewUser(ts)
        self.assertFalse("Batman (2001)" in recommendations)

    def testHorrorWithCartoon(self):
        ts = [
            {"title": "Strangers, The (2008)", "rating": 5.0},
        ]
        recommendations = recommendForNewUser(ts)
        self.assertTrue(("Toy Story (1995)" in recommendations) == False)

    def testIronMan(self):
        ts = [
            {"title": "Iron Man (2008)", "rating": 5.0},
        ]
        recommendations = recommendForNewUser(ts)
        self.assertTrue(
            ("Avengers: Infinity War - Part I (2018)" in recommendations))

    def testRoboCop(self):
        ts = [
            {"title": "RoboCop (1987)", "rating": 5.0},
        ]
        recommendations = recommendForNewUser(ts)
        self.assertTrue(("RoboCop 2 (1990)" in recommendations))

    def testNolan(self):
        ts = [
            {"title": "Inception (2010)", "rating": 5.0},
        ]
        recommendations = recommendForNewUser(ts)
        self.assertTrue(("Dark Knight, The (2008)" in recommendations))

    def testDC(self):
        ts = [
            {"title": "Man of Steel (2013)", "rating": 5.0},
        ]
        recommendations = recommendForNewUser(ts)
        self.assertTrue(
            ("Batman v Superman: Dawn of Justice (2016)" in recommendations)
        )

    def testArmageddon(self):
        ts = [
            {"title": "Armageddon (1998)", "rating": 5.0},
        ]
        recommendations = recommendForNewUser(ts)
        self.assertTrue(("2012 (2009)" in recommendations))

    def testLethalWeapon(self):
        ts = [
            {"title": "Lethal Weapon (1987)", "rating": 5.0},
        ]
        recommendations = recommendForNewUser(ts)
        self.assertTrue(("Lethal Weapon 3 (1992)" in recommendations))

    def testDarkAction(self):
        ts = [
            {"title": "Batman: The Killing Joke (2016)", "rating": 5.0},
        ]
        recommendations = recommendForNewUser(ts)
        self.assertTrue(("Punisher: War Zone (2008)" in recommendations))

    def testDark(self):
        ts = [
            {"title": "Puppet Master (1989)", "rating": 5.0},
        ]
        recommendations = recommendForNewUser(ts)
        self.assertTrue(
            ("Black Mirror: White Christmas (2014)" in recommendations))

    def testHorrorComedy(self):
        ts = [
            {"title": "Scary Movie (2000)", "rating": 5.0},
        ]
        recommendations = recommendForNewUser(ts)
        self.assertTrue(("I Sell the Dead (2008)" in recommendations))

    def testSuperHeroes(self):
        ts = [
            {"title": "Spider-Man (2002)", "rating": 5.0},
        ]
        recommendations = recommendForNewUser(ts)
        self.assertTrue(("Iron Man 2 (2010)" in recommendations))

    def testCartoon(self):
        ts = [
            {"title": "Moana (2016)", "rating": 5.0},
        ]
        recommendations = recommendForNewUser(ts)
        self.assertTrue(("Monsters, Inc. (2001)" in recommendations))

    def testMultipleMovies(self):
        ts = [
            {"title": "Harry Potter and the Goblet of Fire (2005)", "rating": 5.0},
            {"title": "Twilight Saga: New Moon, The (2009)", "rating": 5.0},
        ]
        recommendations = recommendForNewUser(ts)
        self.assertTrue(("Twilight (2008)" in recommendations))

    def testEmptyInput(self):
        ts = []
        recommendations = recommendForNewUser(ts)
        self.assertEqual(
            recommendations,
            [],
            "Empty input should result in empty recommendations")

    def testInvalidRating(self):
        ts = [{"title": "Toy Story (1995)", "rating": 6.0}]
        recommendations = recommendForNewUser(ts)
        self.assertEqual(
            recommendations,
            [],
            "Invalid rating should result in empty recommendations")

    def testTooLongMovieTitle(self):
        ts = [{"title": "T" * 1000, "rating": 5.0}]
        recommendations = recommendForNewUser(ts)
        self.assertEqual(
            recommendations,
            [],
            "Too long movie titles should result in empty recommendations")

    def testInvalidTitle(self):
        ts = [
            {"title": "Invalid Movie", "rating": 5.0},  # Incorrect key "title"
        ]
        recommendations = recommendForNewUser(ts)
        self.assertEqual(
            recommendations,
            [],
            "Invalid input should result in empty recommendations")

    def testGibberishTitles(self):
        ts = [{"title": "@#$%^", "rating": 5.0}]
        recommendations = recommendForNewUser(ts)
        self.assertEqual(
            recommendations,
            [],
            "Movies with gibberish titles should result in empty recommendations")

    def testNegativeRatings(self):
        ts = [
            {"title": "Toy Story (1995)", "rating": -2.0},  # Negative rating
        ]
        recommendations = recommendForNewUser(ts)
        self.assertEqual(
            recommendations,
            [],
            "Negative ratings should result in empty recommendations")

    def testMixValidInvalidRatings(self):
        ts = [
            {"title": "Toy Story (1995)", "rating": 5.0},
            {"title": "Inception (2010)", "rating": 6.0},  # Invalid rating
        ]
        recommendations = recommendForNewUser(ts)
        self.assertEqual(
            recommendations,
            [],
            "Mix of valid and invalid ratings should result in empty recommendations")

    def testTitlesWithLeadingTrailingSpaces(self):
        ts = [
            {"title": "  Batman (1989) ", "rating": 5.0},
        ]
        recommendations = recommendForNewUser(ts)
        self.assertTrue("RoboCop (1987)" in recommendations)

    def testEmptyRatingValue(self):
        ts = [
            {"title": "Inception (2010)", "rating": None},
        ]
        recommendations = recommendForNewUser(ts)
        self.assertEqual(
            recommendations,
            [],
            "Empty rating value should result in empty recommendations")


if __name__ == "__main__":
    unittest.main()
