import pandas as pd


def get_chars_before_str(combined: str, sub_string: str, count: int) -> str:
    op_start = combined.index(sub_string)
    cleaned_combined, cleaned_op_start = escape_ops(combined, op_start)
    prefix = cleaned_combined[:cleaned_op_start]
    return prefix if len(prefix) < count else prefix[-count:]


def get_chars_after_str(combined: str, sub_string: str, count: int) -> str:
    op_end = combined.index(sub_string) + len(sub_string)
    cleaned_combined, cleaned_op_end = escape_ops(combined, op_end)
    postfix = cleaned_combined[cleaned_op_end:]
    return postfix if len(postfix) < count else postfix[:count]


def escape_ops(combined: str, index_to_keep_track_of: int):
    new_index = index_to_keep_track_of
    new_combined = ""
    clear_op = ""
    for index, char in enumerate(combined):
        if char == "I" or char == "D" or char == ")":
            clear_op = char
        elif clear_op == "" or clear_op == ")":
            new_combined = new_combined + char
            clear_op = ""
        elif clear_op == "D" and char == "(":
            clear_op = ")"

        if clear_op != "" and index < index_to_keep_track_of:
            new_index -= 1
    return new_combined, new_index


def load_csv_to_pandas(file_name: str) -> pd.DataFrame:
    return pd.read_csv(file_name, delimiter=";", quotechar='"')


def group_character_operations(first_step: pd.DataFrame, second_step: pd.DataFrame) -> pd.DataFrame:
    all_groups = []
    for index, row in second_step.iterrows():
        op = row['Operation type']
        op_type = "Inserts" if op == "INS" else "Deletes"
        string = row["String"]
        full_op = f"{op}({string})"
        matching_rows = first_step.loc[first_step[op_type] == full_op]
        filtered_rows = matching_rows[["Combined"]]
        filtered_rows["Object"] = full_op
        all_groups.append(filtered_rows)
    return pd.concat(all_groups)


def get_surrounding_character_finder(left: bool, right: bool, count: int):
    assert not (left == right and left), "Getting characters from both sides not implemented"
    if left:
        return lambda combined, operation: get_chars_before_str(combined, operation, count)
    if right:
        return lambda combined, operation: get_chars_after_str(combined, operation, count)

    return lambda combined, operation: ""


def find_surrounding_characters_in_data(data: pd.DataFrame, left: bool, right: bool,
                                        count: int) -> pd.DataFrame:
    character_op = get_surrounding_character_finder(left, right, count)
    data["Surrounding chars"] = data.apply(
        lambda r: character_op(r["Combined"], r["Object"]), axis=1)
    return data


def create_content_matrix_from_data(data: pd.DataFrame):
    return data.groupby(["Object", "Surrounding chars"]).size().unstack(fill_value=0)


def create_context_matrix(objects, first_step_file_name: str, second_step_file_name: str,
                          char_count=2,
                          left=True, right=False) -> pd.DataFrame:
    first_step = load_csv_to_pandas(first_step_file_name)
    second_step = load_csv_to_pandas(second_step_file_name)
    combined = group_character_operations(first_step, second_step)
    combined_with_chars = find_surrounding_characters_in_data(combined, left, right, char_count)
    return create_content_matrix_from_data(combined_with_chars)


def save_context_matrix(context_matrix: pd.DataFrame, path: str):
    context_matrix.to_csv(path, sep=";", quotechar='"')


def create_and_save_context_matrix(output_path: str, first_step_file_name: str,
                                   second_step_file_name: str, char_count=2,
                                   left=True, right=False):
    matrix = create_context_matrix(None, first_step_file_name, second_step_file_name, char_count, left, right)
    save_context_matrix(matrix, output_path)
