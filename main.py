from typing import List

from data_model import Transformation
import Bio.pairwise2 as pair
from Bio.SubsMat import MatrixInfo as matlist


def read_file_data(file_name: str) -> List[Transformation]:
    lines = open(file_name, mode="r")
    data = []
    for l in lines:
        lemma, form, rule_str = l.split(u'\t')
        rules = rule_str.strip().split(';')
        data.append(Transformation(lemma, form, rules))

    return data


transformations = read_file_data("data/latin_alphabet/czech-dev")

first = transformations[0]
print(first)
matrix = matlist.blosum62
for a in pair.align.globaldx(first.lemma, first.inflection, matrix):
    print(pair.format_alignment(*a))
