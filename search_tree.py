import csv
from typing import List, Dict, Iterable, Tuple, Collection

from sklearn import tree
from graphviz import Source
import pandas as pd
import lattice as l


class OperationTree:
    clf: tree.DecisionTreeClassifier
    object_mapping: Dict[str, int]
    num_to_object_mapping: Dict[int, str]
    context_mapping: Dict[str, int]
    objects: List[str]
    contexts: List[str]

    def __init__(self, concept_matrices: List[pd.DataFrame]) -> None:
        super().__init__()
        feature_matrix = _concept_matrices_to_feature_matrix(concept_matrices)
        self._make_tree(feature_matrix)
        self.num_to_object_mapping = _reverse_dict(self.object_mapping)

    def get_operations_for_word(self, word: str, grammar_rules: List[str] = None,
                                max_context_len: int = 3) -> List[str]:
        data_for_word = _get_contexts_in_word(word, self.contexts, max_context_len)
        gap_indexes = [i for i in range(len(data_for_word)) if
                       all(d == 0 for d in data_for_word[i])]
        data_for_word = [data_for_word[i] for i in range(len(data_for_word)) if
                         i not in gap_indexes]
        if len(data_for_word) == 0:
            return []
        data_for_word = self._include_grammar_rules_in_contexts(data_for_word, grammar_rules)
        predictions = self.clf.predict(data_for_word)
        op_predictions = [self.num_to_object_mapping[pred] for pred in predictions]
        for gap in gap_indexes:
            op_predictions.insert(gap, None)
        return op_predictions

    def to_png(self, output_path: str):
        graph = Source(tree.export_graphviz(self.clf, out_file=None, feature_names=self.contexts))
        png_bytes = graph.pipe(format='png')
        with open(output_path, 'wb') as f:
            f.write(png_bytes)

    def _include_grammar_rules_in_contexts(self, contexts: List[List[int]],
                                           grammar_rules: List[str] = None) -> List[List[int]]:
        if grammar_rules is None:
            return contexts

        rule_indexes = [
            self.context_mapping[rule] for rule in grammar_rules if rule in self.context_mapping
        ]
        for context in contexts:
            for index in rule_indexes:
                context[index] = 1
        return contexts

    def _make_tree(self, feature_matrix: pd.DataFrame):
        self.objects = feature_matrix.index.tolist()
        self.object_mapping = _labels_to_num_indexes(self.objects)
        labels = [self.object_mapping[l] for l in self.objects]
        features = feature_matrix.values
        self.contexts = feature_matrix.columns.tolist()
        self.context_mapping = _labels_to_num_indexes(self.contexts)
        clf = tree.DecisionTreeClassifier(criterion="entropy")
        clf.fit(features, labels)
        self.clf = clf


def _concept_matrices_to_feature_matrix(concept_matrices: List[pd.DataFrame]) -> pd.DataFrame:
    merged: pd.DataFrame = pd.concat([m.transpose() for m in concept_matrices], axis=0)
    merged.reset_index(inplace=True)
    empty_objects = merged.index[merged.sum(axis=1) == 0]
    merged.drop(index=empty_objects, inplace=True)
    merged.drop_duplicates(inplace=True)

    merged.set_index("index", inplace=True)
    # print(merged)

    return merged


def _labels_to_num_indexes(rows: Iterable[str]) -> Dict[str, int]:
    mapping = {}
    for row in rows:
        if row not in mapping:
            mapping[row] = len(mapping)

    return mapping


def _reverse_dict(dict: Dict) -> Dict:
    return {v: k for k, v in dict.items()}


def _find_left_substrings_on_pos(word: str, pos: int, max_len: int) -> List[str]:
    contexts = []
    for i in range(1, max_len + 1):
        if pos - i < 0:
            break
        contexts.append(f"L({word[pos - i:pos]})")
    return contexts


def _find_right_substrings_on_pos(word: str, pos: int, max_len: int):
    max_pos = len(word)
    contexts = []
    for i in range(1, max_len + 1):
        if pos + i > max_pos:
            break
        contexts.append(f"R({word[pos:pos + i]})")
    return contexts


def _find_substrings_on_pos(word: str, pos: int, max_len: int):
    return _find_left_substrings_on_pos(word, pos, max_len) \
           + _find_right_substrings_on_pos(word, pos, max_len)


def _get_contexts_in_word(word: str, all_contexts: List[str], max_len: int) -> List[List[int]]:
    context_count = len(all_contexts)
    context_mapping = _labels_to_num_indexes(all_contexts)
    contexts_for_all_poses = []
    for i in range(len(word)):
        subs = _find_substrings_on_pos(word, i, max_len)
        contexts = [context_mapping[c] for c in subs if c in context_mapping]
        binary_contexts = [1 if i in contexts else 0 for i in range(context_count)]
        contexts_for_all_poses.append(binary_contexts)
    return contexts_for_all_poses


def _get_op_chars(op: str):
    return op[4: -1]


def _perform_operations_for_word(word: str, operations: List[str]) -> str:
    assert len(word) == len(operations)
    new_word = ""
    for index in range(len(word)):
        operation = operations[index]
        if operation is None:
            new_word += word[index]
        elif operation.startswith("INS"):
            new_word += _get_op_chars(operation) + word[index]
        elif operation.startswith("DEL"):
            del_chars = _get_op_chars(operation)
            if len(del_chars) <= len(new_word) and del_chars == new_word[-len(del_chars):]:
                new_word = new_word[-len(del_chars)] + word[index]
            else:
                new_word += word[index]
    return new_word


def _load_test_data(file_path: str) -> List[Tuple[str, str, List[str]]]:
    res = []
    with open(file_path) as file:
        r = csv.reader(file, delimiter="\t")
        for row in r:
            res.append((row[0], row[1], row[2].split(";")))
    return res


def predict_and_save_new_words(data_file_path: str, concepts_path: str, output_path: str):
    words_and_grammar = _load_test_data(data_file_path)
    print(words_and_grammar)
    concept_matrices = l.read_data_frames_from_excel(concepts_path)
    o_tree = OperationTree(concept_matrices)
    words_and_predictions = []
    for word, actual, grammar in words_and_grammar:
        operations = o_tree.get_operations_for_word(word, grammar_rules=grammar)
        predicted_word = word if len(operations) == 0 \
            else _perform_operations_for_word(word, operations)
        words_and_predictions.append((word, predicted_word, actual))
    _save_words_and_predictions(words_and_predictions, output_path)


def _save_words_and_predictions(words_and_predictions: Collection[Tuple[str, str, str]],
                                output_path: str):
    with open(output_path, mode='w+') as file:
        writer = csv.writer(file, delimiter=';', quotechar='"', quoting=csv.QUOTE_MINIMAL)
        writer.writerow(["Word", "Prediction", "Actual"])
        for word_and_prediction in words_and_predictions:
            writer.writerow(word_and_prediction)
