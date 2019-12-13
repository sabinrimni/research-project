import collections
import csv
import os
from typing import List

import Bio.pairwise2 as pair
import more_itertools as mit
import regex as re
import pandas as pd

from context_matrix import create_and_save_context_matrix
from data_model import Transformation, Operation, Operations


def read_file_data(file_name: str) -> List[Transformation]:
    lines = open(file_name, mode="r", encoding="utf-8")
    data = []
    for l in lines:
        lemma, form, rule_str = l.split(u'\t')
        rules = rule_str.strip().split(';')
        data.append(Transformation(lemma, form, rules))

    return data


def find_gap_positions_and_matching_characters(gap_string: str, character_string: str) -> List[
    Operation]:
    assert len(gap_string) == len(character_string)
    positions = [m.start() for m in re.finditer('<', gap_string)]
    grouped_positions = group_consecutive_indexes(positions)
    operations = []
    for group in grouped_positions:
        if len(group) == 0:
            continue
        characters = ""
        for index in group:
            characters += character_string[index]
        operations.append(Operation(group[0], characters))
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
                                      -1, -0.1, force_generic=True, one_alignment_only=True,
                                      gap_char="<")
    first_alig = alignements[0]
    inserts = find_gap_positions_and_matching_characters(first_alig[0], first_alig[1])
    deletes = find_gap_positions_and_matching_characters(first_alig[1], first_alig[0])
    return Operations(transformation, inserts, deletes)


def group_inserts(operations: List[Operations]):
    inserts = [insert for operation in operations for insert in operation.inserts]
    return group_operations(inserts)


def group_inserts_by_characters_only(operations: List[Operations]):
    inserts = [insert for operation in operations for insert in operation.inserts]
    return group_operation_characters(inserts)


def group_deletes_by_characters_only(operations: List[Operations]):
    deletes = [delete for operation in operations for delete in operation.deletes]
    return group_operation_characters(deletes)


def group_deletes(operations: List[Operations]):
    deletes = [delete for operation in operations for delete in operation.deletes]
    return group_operations(deletes)


def group_operations(operations: List[Operation]):
    counter = collections.Counter(operations)
    return counter


def group_operation_characters(operations: List[Operation]):
    counter = collections.Counter([op.letters for op in operations])
    return counter


def write_first_step(file, operations: List[Operations]):
    writer = csv.writer(file, delimiter=';', quotechar='"', quoting=csv.QUOTE_MINIMAL)
    writer.writerow(["Source", "Target", "Combined", "Inserts", "Deletes"])
    for op in operations:
        lemma = op.transformation.lemma
        inflection = op.transformation.inflection
        combined = op.combined()
        ins_steps = ",".join([f"INS({ins.letters})" for ins in op.inserts])
        del_steps = ",".join([f"DEL({delete.letters})" for delete in op.deletes])

        writer.writerow([lemma, inflection, combined, ins_steps, del_steps])


def write_second_step(file, operations: List[Operations]):
    counted_inserts = group_inserts_by_characters_only(operations)
    counted_deletes = group_deletes_by_characters_only(operations)
    writer = csv.writer(file, delimiter=';', quotechar='"', quoting=csv.QUOTE_MINIMAL)
    writer.writerow(["String", "Operation type", "Occurrences"])
    for characters in counted_inserts:
        writer.writerow([characters, "INS", counted_inserts[characters]])
    for characters in counted_deletes:
        writer.writerow([characters, "DEL", counted_deletes[characters]])


def extract_alphabet(words: List[str]):
    alphabet = set()
    for word in words:
        print(word)
        for letter in word:
            if len(letter) > 0:
                alphabet.add(letter.lower())
    return alphabet


def write_alphabet(output_file: str, first_step_file_name: str):
    first_step = pd.read_csv(first_step_file_name, delimiter=";", quotechar='"')
    words = first_step["Source"] + first_step["Target"]
    alphabet = extract_alphabet(words)
    pd.DataFrame(alphabet, columns=["Letter"]).to_csv(output_file, ";")



def write_third_step_ins(file, operations: List[Operations]):
    writer = csv.writer(file, delimiter=';', quotechar='"', quoting=csv.QUOTE_MINIMAL)
    for op in operations:
        for ins in op.inserts:
            writer.writerow([ins.letters])


def write_third_step_del(file, operations: List[Operations]):
    writer = csv.writer(file, delimiter=';', quotechar='"', quoting=csv.QUOTE_MINIMAL)
    for op in operations:
        for d in op.deletes:
            writer.writerow([d.letters])


def process_data_file(file_name, language, perform_step_one=False, perform_step_two=False,
                      perform_step_three=False):
    trans_data = read_file_data(file_name)
    operations = get_operations(trans_data)
    if perform_step_one:
        with open(f'data/processed/first_step/{language}.csv', mode='w+') as file:
            write_first_step(file, operations)
    if perform_step_two:
        with open(f'data/processed/second_step/{language}.csv', mode='w+') as file:
            write_second_step(file, operations)
    if perform_step_three:
        with open(f'data/processed/third_step/ins_{language}.txt', mode='w+') as file:
            write_third_step_ins(file, operations)
        with open(f'data/processed/third_step/del_{language}.txt', mode='w+') as file:
            write_third_step_del(file, operations)

