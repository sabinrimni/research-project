import os

from context_matrix import create_and_save_context_matrix, load_context_matrix
from lattice import Lattice
from main import process_data_file
import pandas as pd


def generate_steps_1_2_3(generate_step_1=False, generate_step_2=False, generate_step_3=False):
    directory_name = "data/latin_alphabet"
    for filename in os.listdir(directory_name):
        file_data = filename.split("-")
        language = file_data[0]
        operation = file_data[1]
        print(f"Starting work on {language}")
        if operation == "dev":
            process_data_file(f"{directory_name}/{filename}", language, generate_step_1,
                              generate_step_2, generate_step_3)
        print(f"Finished work on {language}")
    print("Done")


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
    lattice = Lattice(ctx, 4)
    concept_a = lattice.find_concept_for_object("a")
    concept_f = lattice.find_concept_for_object("f")
    print("\nA")
    print(concept_a)
    print("\nF")
    print(concept_f)
    # superconcept = lattice.find_superconcept(concept_a, concept_f)
    # print("Superconcept")
    # print(superconcept)
    subconcept = lattice.find_subconcept(concept_a, concept_f)
    print("Subconcept")
    print(subconcept)
    print("Original")
    print(ctx)


# ctx = load_context_matrix("data/processed/fourth_step/danish.csv")
# print(ctx)
# lattice = Lattice(ctx, 1)
# print(lattice.find_operations_for_context("en"))
# print(lattice.find_concept_for_object("INS(ser)"))
# generate_steps_1_2_3(generate_step_3=True)

test_lattice()