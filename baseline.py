import csv
from statistics import mean
from typing import List, Tuple
import Bio.pairwise2 as pair


def _read_predictions_and_actual_words(prediction_file: str) -> List[Tuple[str, str, str]]:
    res = []
    with open(prediction_file) as file:
        r = csv.reader(file, delimiter=";")
        next(r)
        for row in r:
            res.append((row[0], row[1], row[2]))
    return res


def calculate_and_save_cost_baseline(prediction_file: str, output_file: str):
    predictions_and_actual = _read_predictions_and_actual_words(prediction_file)
    words_and_cost = []
    for original, prediction, actual in predictions_and_actual:
        score = pair.align.globalms(prediction, actual, 1, -1, -0.5, -0.1, score_only=True,
                                    force_generic=True)
        words_and_cost.append((original, score))
    _save_cost_baseline(words_and_cost, output_file)

def calculate_average_cost(word_cost_file: str) -> float:
    res = []
    with open(word_cost_file) as file:
        r = csv.reader(file, delimiter=";")
        next(r)
        for row in r:
            res.append(float(row[1]))
    return mean(res)




def _save_cost_baseline(words_and_cost: List[Tuple[str, str]], output_file: str):
    with open(output_file, mode='w+') as file:
        writer = csv.writer(file, delimiter=';', quotechar='"', quoting=csv.QUOTE_MINIMAL)
        writer.writerow(["Word", "Cost"])
        for word_and_cost in words_and_cost:
            writer.writerow(word_and_cost)
