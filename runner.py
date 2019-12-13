import os
from typing import Callable

from functools import partial
from context_matrix import create_and_save_context_matrix, load_context_matrix
import lattice as l
from main import process_data_file, write_alphabet
import pandas as pd


def generate_steps_1_2_3(generate_step_1=False, generate_step_2=False, generate_step_3=False):
    directory_name = "data/latin_alphabet"
    op = partial(run_steps_1_2_3, generate_step_1=generate_step_1, generate_step_2=generate_step_2,
                 generate_step_3=generate_step_3)
    iterate_directory(directory_name, op)


def run_steps_1_2_3(directory_name: str, filename: str, generate_step_1: bool,
                    generate_step_2: bool, generate_step_3: bool) -> None:
    file_data = filename.split("-")
    language = file_data[0]
    operation = file_data[1]
    if operation == "dev":
        process_data_file(f"{directory_name}/{filename}", language, generate_step_1,
                          generate_step_2, generate_step_3)


def iterate_directory(directory_name, operation: Callable[[str, str], None]) -> None:
    for filename in os.listdir(directory_name):
        operation(directory_name, filename)


def write_alphabets():
    dir_name = "data/processed/first_step"
    iterate_directory(dir_name, write_alphabet_for_file)


def write_alphabet_for_file(directory_name: str, filename: str):
    language = filename.split(".")[0]
    print(f"Writing alphabet for {language}")
    write_alphabet(f"data/processed/alphabet/{filename}", f"{directory_name}/{filename}")
    print(f"Finished alphabet for {language}")


def generate_step_4():
    directory_name = "data/processed"
    for filename in os.listdir(f"{directory_name}/first_step"):
        file_data = filename.split(r".")
        language = file_data[0]
        print(f"Starting work on {language}")
        first_step_file = f"{directory_name}/first_step/{filename}"
        second_step_file = f"{directory_name}/second_step/{filename}"
        output_path = f"{directory_name}/fourth_step/{filename}"
        create_and_save_context_matrix(output_path, first_step_file, second_step_file)

        print(f"Finished work on {language}")


def test_lattice():
    data = {
        "a": [1, 2, 3, 4, 5, 6, 7],
        "b": [5, 5, 5, 5, 5, 5, 5],
        "c": [9, 5, 7, 1, 1, 9, 5],
        "d": [5, 5, 5, 5, 2, 5, 5],
        "e": [0, 0, 8, 9, 5, 5, 9],
        "f": [8, 3, 9, 5, 1, 1, 0],
        "g": [5, 5, 2, 9, 0, 0, 9]
    }
    ctx = pd.DataFrame(data)
    lattice = l.Lattice(ctx, 4)
    concept_a = lattice.find_concept_for_object("a")
    concept_f = lattice.find_concept_for_object("f")
    print("\nA")
    print(concept_a)
    print("\nF")
    print(concept_f)
    # superconcept = lattice.find_superconcept(concept_a, concept_f)
    # print("Superconcept")
    # print(superconcept)
    # subconcept = lattice.find_subconcept(concept_a, concept_f)
    # print("Subconcept")
    # print(subconcept)
    # print("Original")
    # print(ctx)


ctx = load_context_matrix("data/processed/fourth_step/danish.csv").transpose()
memorizing_lattice = l.MemorizingLattice(ctx, 1)
memorizing_lattice.calculate_superconcepts()
memorizing_lattice.print_concepts(level=1)
memorizing_lattice.calculate_superconcepts()
memorizing_lattice.print_concepts(level=2)

# test_lattice()

# print(ctx)
# lattice = Lattice(ctx, 1)
# et_concept = lattice.find_concept_for_object("INS(et)")
# ser_concept = lattice.find_concept_for_object("INS(ser)")
# # print(et_concept.get_matrix_without_zero_columns_and_zero_rows())
# # print(ser_concept.get_matrix_without_zero_columns_and_zero_rows())
#
# super_concept = lattice.find_superconcept(et_concept, ser_concept)
# super_concept_support = lattice.get_support_for_concept(super_concept)
# # print(get_matrix_without_zero_columns_and_zero_rows(super_concept_support))
# print(get_matrix_without_zero_columns_and_zero_rows(lattice.get_confidence_for_concept(super_concept)))

