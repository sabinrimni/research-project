from typing import List, Dict, Iterable

from sklearn import tree
import pandas as pd
import numpy as np


class OperationTree:
    clf: tree.DecisionTreeClassifier
    object_mapping: Dict[str, int]
    num_to_object_mapping: Dict[int, str]
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
        predictions = self.clf.predict(data_for_word)
        return [self.num_to_object_mapping[pred] for pred in predictions]

    def _make_tree(self, feature_matrix: pd.DataFrame):
        self.objects = feature_matrix.index.tolist()
        self.object_mapping = _labels_to_num_indexes(self.objects)
        labels = [self.object_mapping[l] for l in self.objects]
        features = feature_matrix.values
        self.contexts = feature_matrix.columns.tolist()
        clf = tree.DecisionTreeClassifier(criterion="entropy")
        clf.fit(features, labels)
        self.clf = clf


def _concept_matrices_to_feature_matrix(concept_matrices: List[pd.DataFrame]) -> pd.DataFrame:
    merged: pd.DataFrame = pd.concat([m.transpose() for m in concept_matrices], axis=0)
    merged.reset_index(inplace=True)
    # TODO make this smarter, right now if 2 different objects have same contexts one will be lost
    empty_objects = merged.index[merged.sum(axis=1) == 0]
    merged.drop(index=empty_objects, inplace=True)

    merged.set_index("index", inplace=True)

    print("Merged")
    print(merged)
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
    rev = _reverse_dict(context_mapping)
    contexts_for_all_poses = []
    for i in range(len(word)):
        subs = _find_substrings_on_pos(word, i, max_len)
        contexts = [context_mapping[c] for c in subs if c in context_mapping]
        print([rev[c] for c in contexts])
        if (len(contexts)) == 0:
            continue
        binary_contexts = [1 if i in contexts else 0 for i in range(context_count)]
        contexts_for_all_poses.append(binary_contexts)
    return contexts_for_all_poses
