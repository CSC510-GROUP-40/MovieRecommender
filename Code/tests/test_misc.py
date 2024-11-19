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
        self.assertTrue(any("toy story 3 (2010)" == rec.lower() for rec in recommendations))
        self.assertTrue(any("toy story 2 (1999)" == rec.lower() for rec in recommendations))

    def testToyStoryNeg(self):
        ts = [
            {"title": "Toy Story (1995)", "rating": 5.0},
        ]
        recommendations = recommendForNewUser(ts)
        self.assertFalse(any("inception" == rec.lower() for rec in recommendations))

    def testKunfuPanda(self):
        ts = [
            {"title": "Kung Fu Panda (2008)", "rating": 5.0},
        ]
        recommendations = recommendForNewUser(ts)
        self.assertTrue(any("kung fu panda 2 (2011)" == rec.lower() for rec in recommendations))

    def testKunfuPandaNeg(self):
        ts = [
            {"title": "Kung Fu Panda (2008)", "rating": 5.0},
        ]
        recommendations = recommendForNewUser(ts)
        self.assertFalse(any("batman (2001)" == rec.lower() for rec in recommendations))

    def testHorrorWithCartoon(self):
        ts = [
            {"title": "Strangers, The (2008)", "rating": 5.0},
        ]
        recommendations = recommendForNewUser(ts)
        self.assertFalse(any("toy story (1995)" == rec.lower() for rec in recommendations))

    def testIronMan(self):
        ts = [
            {"title": "Iron Man (2008)", "rating": 5.0},
        ]
        recommendations = recommendForNewUser(ts)
        self.assertTrue(any("iron man 2 (2010)" == rec.lower() for rec in recommendations))

    def testRoboCop(self):
        ts = [
            {"title": "RoboCop (1987)", "rating": 5.0},
        ]
        recommendations = recommendForNewUser(ts)
        print(f"{recommendations}")
        self.assertTrue(any("robocop 2 (1990)" == rec.lower() for rec in recommendations))

    def testNolan(self):
        ts = [
            {"title": "Inception (2010)", "rating": 5.0},
        ]
        recommendations = recommendForNewUser(ts)
        self.assertTrue(any("insomnia (2002)" == rec.lower() for rec in recommendations))

    def testDC(self):
        ts = [
            {"title": "Man of Steel (2013)", "rating": 5.0},
        ]
        recommendations = recommendForNewUser(ts)
        self.assertTrue(any("batman v superman dawn of justice (2016)" == rec.lower() for rec in recommendations))

    def testArmageddon(self):
        ts = [
            {"title": "Armageddon (1998)", "rating": 5.0},
        ]
        recommendations = recommendForNewUser(ts)
        self.assertTrue(any("2012 (2009)" == rec.lower() for rec in recommendations))

    def testLethalWeapon(self):
        ts = [
            {"title": "Lethal Weapon (1987)", "rating": 5.0},
        ]
        recommendations = recommendForNewUser(ts)
        self.assertTrue(any("lethal weapon 3 (1992)" == rec.lower() for rec in recommendations))

    def testDarkAction(self):
        ts = [
            {"title": "Batman: The Killing Joke (2016)", "rating": 5.0},
        ]
        recommendations = recommendForNewUser(ts)
        self.assertTrue(any("punisher war zone (2008)" == rec.lower() for rec in recommendations))

    def testDark(self):
        ts = [
            {"title": "Puppet Master (1989)", "rating": 5.0},
        ]
        recommendations = recommendForNewUser(ts)
        self.assertTrue(any("black mirror white christmas (2014)" == rec.lower() for rec in recommendations))

    def testHorrorComedy(self):
        ts = [
            {"title": "Scary Movie (2000)", "rating": 5.0},
        ]
        recommendations = recommendForNewUser(ts)
        self.assertTrue(any("i sell the dead (2008)" == rec.lower() for rec in recommendations))

    def testSuperHeroes(self):
        ts = [
            {"title": "Spider-Man (2002)", "rating": 5.0},
        ]
        recommendations = recommendForNewUser(ts)
        self.assertTrue(any("iron man 2 (2010)" == rec.lower() for rec in recommendations))

    def testCartoon(self):
        ts = [
            {"title": "Moana (2016)", "rating": 5.0},
        ]
        recommendations = recommendForNewUser(ts)
        print(recommendations)
        self.assertTrue(any("monsters inc (2001)" == rec.lower() for rec in recommendations))

    def testMultipleMovies(self):
        ts = [
            {"title": "Harry Potter and the Goblet of Fire (2005)", "rating": 5.0},
            {"title": "Twilight Saga: New Moon The (2009)", "rating": 5.0},
        ]
        recommendations = recommendForNewUser(ts)
        self.assertTrue(any("twilight (2008)" == rec.lower() for rec in recommendations))

