from typing import List

from data_model import Transformation, Operation, Operations
import Bio.pairwise2 as pair
from Bio.pairwise2 import format_alignment
import regex as re
import more_itertools as mit
import unicodedata
import collections


def read_file_data(file_name: str) -> List[Transformation]:
    lines = open(file_name, mode="r")
    data = []
    for l in lines:
        lemma, form, rule_str = l.split(u'\t')
        rules = rule_str.strip().split(';')
        data.append(Transformation(strip_unicode(lemma), strip_unicode(form), rules))

    return data


def strip_unicode(unicode_str: str) -> str:
    return unicodedata.normalize('NFKD', unicode_str) \
        .encode('ascii', 'ignore') \
        .decode('utf-8')


def find_gap_positions_and_matching_characters(gap_string: str, character_string: str) -> List[
    Operation]:
    assert len(gap_string) == len(character_string)
    positions = [m.start() for m in re.finditer('-', gap_string)]
    grouped_positions = group_consecutive_indexes(positions)
    operations = []
    for group in grouped_positions:
        if len(group) == 0:
            continue
        characters = ""
        for index in group:
            characters += character_string[index]
        directional_index = transform_index_to_directional_index(group[0], gap_string)
        operations.append(Operation(directional_index, characters))
    return operations


def transform_index_to_directional_index(index: int, string: str):
    if index > len(string) / 2:
        return index - len(string)
    return index


def group_consecutive_indexes(indexes: List[int]) -> List[List[int]]:
    return [list(group) for group in mit.consecutive_groups(indexes)]


def get_operations(transformations: List[Transformation]) -> List[Operations]:
    return [find_operations(transformation) for transformation in transformations]


def find_operations(transformation: Transformation) -> Operations:
    # Large penalty to make sure no mismatching characters appear
    penalty = -1000000
    alignements = pair.align.globalms(transformation.lemma, transformation.inflection, 1, penalty,
                                      -1, -0.1)
    first_alig = alignements[0]
    inserts = find_gap_positions_and_matching_characters(first_alig[0], first_alig[1])
    deletes = find_gap_positions_and_matching_characters(first_alig[1], first_alig[0])
    return Operations(transformation, inserts, deletes)

def group_inserts(operations: List[Operations]):
    inserts = [insert for operation in operations for insert in operation.inserts]
    return group_operations(inserts)

def group_deletes(operations: List[Operations]):
    deletes = [delete for operation in operations for delete in operation.deletes]
    return group_operations(deletes)


def group_operations(operations: List[Operation]):
    counter = collections.Counter(operations)
    return counter




trans_data = read_file_data("data/latin_alphabet/danish-dev")
operations = get_operations(trans_data)
grouped_inserts = group_inserts(operations)
grouped_deletes = group_deletes(operations)
print(grouped_inserts)
print(grouped_deletes)
