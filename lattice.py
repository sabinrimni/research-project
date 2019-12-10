from typing import List, Tuple

import pandas as pd


class Concept:
    contexts: pd.Series
    objects: pd.Series
    binary_matrix: pd.DataFrame

    def __init__(self, binary_matrix: pd.DataFrame, contexts: pd.Series,
                 objects: pd.Series) -> None:
        super().__init__()
        self.binary_matrix = binary_matrix
        self.contexts = contexts
        self.objects = objects

    def __str__(self) -> str:
        return f"Contexts:\n{self.contexts}\nObjects:\n{self.objects}\n{self.binary_matrix}"

    def __repr__(self) -> str:
        return f"(Contexts: {self.contexts}, Objects: {self.objects})"

    def is_consistent(self) -> bool:
        actual_objects = self.binary_matrix.max(axis=0)

        non_zero_columns = self.binary_matrix[actual_objects.index[actual_objects > 0]]
        objects_match = (actual_objects == self.objects).all()

        non_zero_columns_transpose = non_zero_columns.transpose()
        contexts = non_zero_columns_transpose.prod()
        contexts_match = (contexts == self.contexts).all()

        context_object_intersection = non_zero_columns_transpose[
            self.contexts.index[self.contexts == 1]]
        objects_fulfil_context_requirements = context_object_intersection.min().min() == 1

        return contexts_match and objects_match and objects_fulfil_context_requirements


class Lattice:
    context_matrix: pd.DataFrame
    binary_matrix: pd.DataFrame
    threshold: int

    def __init__(self, context_matrix: pd.DataFrame, threshold: int) -> None:
        super().__init__()
        self.context_matrix = context_matrix
        self.threshold = threshold
        self.binary_matrix = self._create_binary_matrix_based_on_threshold(self.context_matrix,
                                                                           self.threshold)

    def find_subconcept(self, concept_1: Concept, concept_2: Concept) -> pd.DataFrame:
        assert self._is_proper_concept(concept_1), f"Concept1 {concept_1} is not proper"
        assert self._is_proper_concept(concept_2), f"Concept1 {concept_2} is not proper"

        objects = self._find_series_intersection(concept_1.objects, concept_2.objects)
        concept_matrix = self._zero_columns_not_matching_objects(objects, self.binary_matrix)
        contexts = self._find_contexts_from_concept_matrix(concept_matrix, objects)
        subconcept = Concept(concept_matrix, contexts, objects)
        assert self._is_proper_concept(subconcept), f"Subconcept {subconcept} is not proper"
        return subconcept

    def find_superconcept(self, concept_1: Concept, concept_2: Concept) -> Concept:
        assert self._is_proper_concept(concept_1), f"Concept1 {concept_1} is not proper"
        assert self._is_proper_concept(concept_2), f"Concept1 {concept_2} is not proper"

        contexts = self._find_series_intersection(concept_1.contexts, concept_2.contexts)
        concept_matrix = self._zero_columns_not_matching_contexts(contexts, self.binary_matrix)
        objects = self._find_objects_from_concept_matrix(concept_matrix)
        superconcept = Concept(concept_matrix, contexts, objects)
        assert self._is_proper_concept(superconcept), f"Superconcept {superconcept} is not proper"
        return superconcept

    def find_concept_for_object(self, object: str) -> Concept:
        # concept_matrix = self._zero_columns_not_matching_column(object, self.binary_matrix)
        contexts = self.binary_matrix[object]
        concept_matrix = self._zero_columns_not_matching_contexts(contexts, self.binary_matrix)
        contexts = (concept_matrix[object] == 1).astype(int)
        objects = self._find_objects_from_concept_matrix(concept_matrix)
        concept = Concept(concept_matrix, contexts, objects)
        assert self._is_proper_concept(concept), f"{concept} is not a proper concept"
        return concept

    @staticmethod
    def _find_objects_from_concept_matrix(concept_matrix: pd.DataFrame) -> pd.Series:
        return (concept_matrix == 1).any().astype(int)

    @staticmethod
    def _find_contexts_from_concept_matrix(concept_matrix: pd.DataFrame,
                                           objects: pd.Series) -> pd.Series:
        non_zero_columns = concept_matrix[objects.index[objects == 1]]
        return non_zero_columns.transpose().prod()

    @staticmethod
    def _find_series_intersection(series_1: pd.Series, series_2: pd.Series) -> pd.Series:
        merged: pd.DataFrame = pd.concat([series_1, series_2], axis=1)
        return merged.prod(axis=1)

    @staticmethod
    def _find_series_union(series_1: pd.Series, series_2: pd.Series) -> pd.Series:
        merged: pd.DataFrame = pd.concat([series_1, series_2], axis=1)
        return merged.max(axis=1)

    @staticmethod
    def _create_binary_matrix_based_on_threshold(context_matrix: pd.DataFrame,
                                                 threshold: int):
        matrix = context_matrix.copy()
        above_threshold = matrix[matrix.columns] >= threshold
        matrix[matrix.columns] = 0
        matrix[above_threshold] = 1
        return matrix

    # @staticmethod
    # def _zero_columns_not_matching_column(column: str,
    #                                       binary_matrix: pd.DataFrame) -> pd.DataFrame:
    #     matrix = binary_matrix.copy()
    #     for c in matrix.columns:
    #         non_matching_rows = matrix[column] > matrix[c]
    #         if non_matching_rows.any():
    #             matrix[c] = 0
    #     return matrix

    def _zero_columns_not_matching_contexts(self, contexts: pd.Series,
                                            binary_matrix: pd.DataFrame) -> pd.DataFrame:
        matrix: pd.DataFrame = binary_matrix.copy()
        for c in matrix.columns:
            non_matching_rows = contexts > matrix[c]
            if non_matching_rows.any():
                matrix[c] = 0
        return matrix

    def _zero_columns_not_matching_objects(self, objects: pd.Series,
                                           binary_matrix: pd.DataFrame) -> pd.DataFrame:
        matrix: pd.DataFrame = binary_matrix.copy()
        non_object_indexes = objects.index[objects == 0]
        matrix[non_object_indexes] = 0
        return matrix

    def _filter_rows_below_threshold(self, column: str, matrix) -> pd.DataFrame:
        above_threshold = matrix[column] >= self.threshold
        filtered = matrix[above_threshold]
        return filtered

    def _filter_columns_below_threshold(self, filtered_rows: pd.DataFrame) -> pd.DataFrame:
        transposed = filtered_rows.transpose()
        columns = transposed.columns
        filtered_columns_transposed = \
            transposed[(transposed[columns] >= self.threshold).all(axis=1)]
        return filtered_columns_transposed.transpose()

    def _is_proper_concept(self, concept: Concept) -> bool:
        if not concept.is_consistent():
            return False

        object_indexes = concept.objects.index[concept.objects == 1]
        objects_in_lattice = self.binary_matrix[object_indexes]
        objects_in_concept = concept.binary_matrix[object_indexes]
        objects_match = (objects_in_lattice == objects_in_concept).all().all()
        if not objects_match:
            return False

        context_indexes = concept.contexts.index[concept.contexts == 1]
        non_object_indexes = concept.objects.index[concept.objects == 0]
        non_objects_for_contexts = self.binary_matrix[non_object_indexes].iloc[context_indexes]
        non_objects_match_contexts = non_objects_for_contexts.all().any()

        return not non_objects_match_contexts
