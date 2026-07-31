from typing import List


def areSentencesSimilar(sentence1: List[str], sentence2: List[str], similarPairs: List[List[str]]) -> bool:
        if len(sentence1) != len(sentence2):
            return False
        dc1 = {similarPairs[i][0]: similarPairs[i][1] for i in range(len(similarPairs))}
        dc2 = {similarPairs[i][1]: similarPairs[i][0] for i in range(len(similarPairs))}
        for i in range(len((sentence1))):
            if sentence1[i] != dc1[sentence1[i]] or sentence2[i] != dc2[sentence2[i]]:
                return False
        return True






if __name__ == "__main__":

    # sentence1 = ["great","acting","skills"]
    # sentence2 = ["fine","drama","talent"]
    # similarPairs = [["great","fine"],["drama","acting"],["skills","talent"]]
    # res = areSentencesSimilar(sentence1, sentence2, similarPairs)
    # print(res)  # Output: True
    res = []
    res.append((1,2))
    print(res)