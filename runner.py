import os

from context_matrix import create_and_save_context_matrix, load_context_matrix
from lattice import Lattice
from main import process_data_file


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


# ctx = load_context_matrix("data/processed/fourth_step/danish.csv")
# print(ctx)
# lattice = Lattice(ctx, 1)
# rows = lattice._filter_rows_below_threshold("ad")
# print(rows)
# columns = lattice._filter_columns_below_threshold(rows)
# print(columns)

generate_steps_1_2_3(generate_step_3=True)
