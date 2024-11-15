# StreamR

# Version: 1.0.0
# Date Released: 2024-11-01
# Authors: Sravya Yepuri, Chirag Hegde, Melika Ahmadi Ranjbar

# Licensed under the MIT License.
# You may obtain a copy of the License at

#     https://opensource.org/licenses/MIT

import pandas as pd

# from app import app
from flask import jsonify, request, render_template
import sys
import os

app_dir = os.path.dirname(os.path.abspath(__file__))
code_dir = os.path.dirname(app_dir)
project_dir = os.path.dirname(code_dir)


class Search:

    df = pd.read_csv(project_dir + "/recommenderapp/prediction_scripts/data/movies.csv")

    def __init__(self):
        pass

    def startsWith(self, word):
        n = len(word)
        res = []
        word = word.lower()
        for x in self.df["title"]:
            curr = x.lower()
            if curr[:n] == word:
                res.append(x)
        return res

    def anywhere(self, word, visitedWords):
        res = []
        word = word.lower()
        for x in self.df["title"]:
            if x not in visitedWords:
                curr = x.lower()
                if word in curr:
                    res.append(x)
        return res

    def results(self, word):
        startsWith = self.startsWith(word)
        visitedWords = set()
        for x in startsWith:
            visitedWords.add(x)
        anywhere = self.anywhere(word, visitedWords)
        startsWith.extend(anywhere)
        return startsWith

    def resultsTop10(self, word):
        return self.results(word)[:10]


if __name__ == "__main__":
    app.run()
