import os
from typing import Callable, List, Tuple

from functools import partial
from context_matrix import create_and_save_context_matrix, load_context_matrix
import lattice as l
from data_pre_processing import process_data_file, write_alphabet
import pandas as pd
import operation_revisor as rev
import search_tree as tree
import baseline


def _run_steps(directory_name: str, filename: str, generate_step_1: bool, generate_step_2: bool,
               generate_step_3: bool, generate_step_4: bool, generate_step_5: bool) -> None:
    file_data = filename.split("-")
    language = file_data[0]
    operation = file_data[1]
    if operation == "dev":
        process_data_file(f"{directory_name}/{filename}", language, generate_step_1,
                          generate_step_2, generate_step_3, generate_step_4, generate_step_5)


def _iterate_directory(directory_name, operation: Callable[[str, str], None]) -> None:
    for filename in os.listdir(directory_name):
        operation(directory_name, filename)


def _write_alphabet_for_file(directory_name: str, filename: str):
    language = filename.split(".")[0]
    print(f"Writing alphabet for {language}")
    write_alphabet(f"data/processed/alphabet/{filename}", f"{directory_name}/{filename}")
    print(f"Finished alphabet for {language}")


# Generated the language alphabet
def write_alphabets():
    dir_name = "data/processed/first_step"
    _iterate_directory(dir_name, _write_alphabet_for_file)


# Branch method used for generating the various data pre-processing steps:
# Step 1 - Finding INS and DEL operation required for transforming Lemmas into Inflections
# Step 2 - Counting how many the INS and DEL operations appear
# Step 3 - Separate INS and DEL operation in different files per language
# Step 4 - Apply subword_mnt on the previously separated operations
# Step 5 -
def write_steps(generate_step_1=False, generate_step_2=False, generate_step_3=False,
                generate_step_4=False, generate_step_5=False):
    directory_name = "data/latin_alphabet"
    op = partial(_run_steps, generate_step_1=generate_step_1, generate_step_2=generate_step_2,
                 generate_step_3=generate_step_3, generate_step_4=generate_step_4,
                 generate_step_5=generate_step_5)
    _iterate_directory(directory_name, op)


def write_context_matrices():
    directory_name = "data/processed"
    for filename in os.listdir(f"{directory_name}/first_step"):
        file_data = filename.split(r".")
        language = file_data[0]
        print(f"Starting work on {language}")
        first_step_file = f"{directory_name}/first_step_revised/{filename}"
        second_step_file = f"{directory_name}/second_step_revised/{filename}"
        output_path = f"{directory_name}/context_matrix/{filename}"
        create_and_save_context_matrix(output_path, first_step_file, second_step_file)

        print(f"Finished work on {language}")


def write_concepts():
    directory_name = "data/processed"
    for filename in os.listdir(f"{directory_name}/context_matrix"):
        language = filename.split(r".")[0]
        print(f"Starting work on {language}")
        context_matrix = load_context_matrix(
            f"{directory_name}/context_matrix/{filename}").transpose()
        mem_lattice = l.MemorizingLattice(context_matrix, 1)
        mem_lattice.calculate_concepts()
        mem_lattice.calculate_superconcepts(0)
        mem_lattice.save_superconcepts(f"{directory_name}/concepts/{language}.xlsx")
        print(f"Finished work on {language}")


def write_first_second_step_revision():
    directory_name = "data/processed"
    for filename in os.listdir(f"{directory_name}/subword"):
        language = filename.split(r".")[0]
        print(f"Starting work on {language}")
        subword_file = f"{directory_name}/subword/{filename}"
        first_step_file = f"{directory_name}/first_step/{filename}"
        second_step_file = f"{directory_name}/second_step/{filename}"
        revised_first_step_file = f"{directory_name}/first_step_revised/{filename}"
        revised_second_step_file = f"{directory_name}/second_step_revised/{filename}"
        rev.revise_steps(subword_file, first_step_file, second_step_file, revised_first_step_file,
                         revised_second_step_file)
        print(f"Finished work on {language}")


def draw_trees():
    directory_name = "data/processed"
    for filename in os.listdir(f"{directory_name}/concepts"):
        language = filename.split(r".")[0]
        print(f"Starting work on {language}")
        concept_file = f"{directory_name}/concepts/{filename}"
        concept_matrices = l.read_data_frames_from_excel(concept_file)
        decision_tree = tree.OperationTree(concept_matrices)
        decision_tree.to_png(f"{directory_name}/decision_tree/{language}.png")
        print(f"Finished work on {language}")


def predict_words():
    directory_name = "data"
    for filename in os.listdir(f"{directory_name}/processed/concepts"):
        language = filename.split(r".")[0]
        print(f"Starting work on {language}")
        data_file = f"{directory_name}/latin_alphabet/{language}-test"
        concept_file = f"{directory_name}/processed/concepts/{language}.xlsx"
        output_file = f"{directory_name}/processed/predictions/base/{language}.csv"
        tree.predict_and_save_new_words(data_file, concept_file, output_file)
        print(f"Finished work on {language}")


def reformat_sigmorphon_predictions():
    directory_name = "data/baseline_res"
    for filename in os.listdir(f"{directory_name}"):
        language, type, _ = filename.split(r"-")
        if type != "high":
            continue
        print(f"Starting work on {language}")
        sig_file = f"{directory_name}/{filename}"
        data_file = f"data/latin_alphabet/{language}-test"
        out_file = f"data/processed/predictions/sigmorphon/{language}.csv"
        baseline.format_and_save_sigmorphon_predictions(sig_file, data_file, out_file)
        print(f"Finished work on {language}")


def write_sigmorphon_baseline_cost():
    _write_baseline_cost("sigmorphon", "sigmorphon_cost")


def _write_baseline_cost(input_file_dir: str, output_file_dir: str):
    directory_name = "data/processed/predictions"
    for filename in os.listdir(f"{directory_name}/{input_file_dir}"):
        language = filename.split(r".")[0]
        print(f"Starting work on {language}")
        word_and_prediction_file = f"{directory_name}/{input_file_dir}/{filename}"
        output_file = f"{directory_name}/{output_file_dir}/{filename}"
        baseline.calculate_and_save_cost_baseline(word_and_prediction_file, output_file)
        print(f"Finished work on {language}")


def write_baseline_cost():
    _write_baseline_cost("base", "base_cost")


def _get_mean_and_standard_devs_for_languages() -> List[Tuple[str, float, float]]:
    directory_name = "data/latin_alphabet"
    res = []
    for filename in os.listdir(f"{directory_name}"):
        sp = filename.split(r"-")
        language = sp[0]
        type = sp[1]
        if type != "test":
            continue
        data_file = f"{directory_name}/{filename}"
        mean, stdev = baseline.get_means_and_stdev_for_language(data_file)
        res.append((language, mean, stdev))
    return res


def _get_average_baseline_cost(cost_dir: str) -> List[Tuple[str, float]]:
    directory_name = f"data/processed/predictions/{cost_dir}"
    language_cost = []
    for filename in os.listdir(f"{directory_name}"):
        language = filename.split(r".")[0]
        cost_file = f"{directory_name}/{filename}"
        cost = baseline.calculate_average_cost(cost_file)
        language_cost.append((language, cost))
    return language_cost


def get_average_baseline_cost():
    _get_average_baseline_cost("base_cost")


def get_average_sigmorphon_cost():
    _get_average_baseline_cost("sigmorphon_cost")


def compare_base_to_sigmorphon():
    base = _get_average_baseline_cost("base_cost")
    sig = _get_average_baseline_cost("sigmorphon_cost")
    means_stdev = _get_mean_and_standard_devs_for_languages()
    zipped = zip(base, sig, means_stdev)
    for item in zipped:
        print(f"Language: {item[0][0]}")
        print(f"Base: {item[0][1]} - Sig: {item[1][1]} ")
        print(f"Mean: {item[2][1]}, Stdev: {item[2][2]}")


def _test_lattice():
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


def _test_memorizing_lattice():
    ctx = load_context_matrix("data/processed/context_matrix/danish.csv").transpose()
    memorizing_lattice = l.MemorizingLattice(ctx, 1)
    memorizing_lattice.calculate_concepts()
    # print("Created lattice")
    # print(f"Concept count: {len(memorizing_lattice.concepts)}")
    # print(f"Calculating superconcepts")
    memorizing_lattice.calculate_superconcepts(0)
    # memorizing_lattice.load_superconcepts("data/processed/concepts/danish.xls")
    # memorizing_lattice.print_superconcepts()
    for s in memorizing_lattice.superconcepts:
        s.clear_contexts_not_in_concept()
        print(s)
    memorizing_lattice.save_superconcepts("data/processed/concepts/danish.xlsx")
    print("\nDone")


def _test_revisor():
    sub = rev._load_file("data/processed/subword/test.csv")
    first = rev._load_file("data/processed/first_step/test.csv")
    second = rev._load_file("data/processed/second_step/test.csv")
    print(rev._revise_second_step(sub, second))


# def _test_decision_tree():
#     concept_matrices = l.read_data_frames_from_excel("data/processed/concepts/italian.xlsx")
#     t = tree.OperationTree(concept_matrices)
#     words = load_first_step("data/processed/first_step_revised/italian.csv")
#     for word in words:
#         w = word[0]
#         operations = t.get_operations_for_word(w)
#         print(w)
#         print(operations)
#     # print(tree.perform_operations_for_word("elskerinde", operations))
#     print("Done")


# write_steps(True, True, True, True, True)
# write_alphabets()
# write_first_second_step_revision()
# write_context_matrices()
# write_concepts()
# draw_trees()
# _test_memorizing_lattice()
# _test_decision_tree()
# predict_words()
# write_baseline_cost()
# predict_words()
# write_baseline_cost()
# reformat_sigmorphon_predictions()
# write_sigmorphon_baseline_cost()
# get_average_sigmorphon_cost()
# compare_base_to_sigmorphon()
write_steps(True, True, True, True, True)
write_first_second_step_revision()
write_context_matrices()
write_concepts()
predict_words()
write_baseline_cost()
compare_base_to_sigmorphon()
