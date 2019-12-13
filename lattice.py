from typing import List, Tuple, Dict

import pandas as pd


def get_matrix_without_zero_columns_and_zero_rows(data_matrix: pd.DataFrame,
                                                  copy=False) -> pd.DataFrame:
    matrix: pd.DataFrame = data_matrix.copy() if copy else data_matrix
    non_zero_columns = matrix[get_non_zero_series_indexes(matrix.max(axis=0))]
    non_zero_rows = non_zero_columns[non_zero_columns.max(axis=1) != 0]
    return non_zero_rows


def get_non_zero_series_indexes(series: pd.Series) -> pd.Series:
    return series.index[series != 0]


def get_zero_series_indexes(series: pd.Series) -> pd.Series:
    return series.index[series == 0]


def binary_series_have_common_items(series_1: pd.Series, series_2: pd.Series):
    series_product = series_1 * series_2
    return series_product.sum() > 0


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

    def __eq__(self, o: object) -> bool:
        if not isinstance(o, Concept):
            return False
        return self.contexts.equals(o.contexts) and self.objects.equals(o.objects)

    def get_object_indexes(self) -> pd.Series:
        return get_non_zero_series_indexes(self.objects)

    def get_context_indexes(self) -> pd.Series:
        return get_non_zero_series_indexes(self.contexts)

    def is_consistent(self) -> bool:
        actual_objects = self.binary_matrix.max(axis=0)

        object_indexes = self.get_object_indexes()
        non_zero_columns = self.binary_matrix[object_indexes]
        objects_match = (actual_objects == self.objects).all()

        non_zero_columns_transpose = non_zero_columns.transpose()
        contexts = non_zero_columns_transpose.prod()
        contexts_match = (contexts == self.contexts).all()

        context_indexes = self.get_context_indexes()
        if (context_indexes.empty):
            objects_fulfil_context_requirements = len(object_indexes) == len(self.objects)
        else:
            context_object_intersection = non_zero_columns_transpose[context_indexes]
            objects_fulfil_context_requirements = context_object_intersection.min().min() == 1

        return contexts_match and objects_match and objects_fulfil_context_requirements

    def get_matrix_without_zero_columns_and_zero_rows(self, copy=False) -> pd.DataFrame:
        return get_matrix_without_zero_columns_and_zero_rows(self.binary_matrix, copy)


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

    def find_subconcept(self, concept_1: Concept, concept_2: Concept) -> Concept:
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

    def get_support_for_concept(self, concept: Concept) -> pd.DataFrame:
        return self.context_matrix[concept.get_object_indexes()]

    def get_confidence_for_concept(self, concept: Concept) -> pd.DataFrame:
        context_counts = self.context_matrix.sum(axis=1)
        support_matrix: pd.DataFrame = self.get_support_for_concept(concept).copy()
        return support_matrix.divide(context_counts, axis=0)

        pass

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
        matrix[get_zero_series_indexes(objects)] = 0
        return matrix

    def _is_proper_concept(self, concept: Concept) -> bool:
        if not concept.is_consistent():
            return False

        object_indexes = get_non_zero_series_indexes(concept.objects)
        objects_in_lattice = self.binary_matrix[object_indexes]
        objects_in_concept = concept.binary_matrix[object_indexes]
        objects_match = (objects_in_lattice == objects_in_concept).all().all()
        if not objects_match:
            return False

        context_indexes = get_non_zero_series_indexes(concept.contexts)
        non_object_indexes = get_zero_series_indexes(concept.objects)
        non_objects_for_contexts = self.binary_matrix[non_object_indexes].loc[context_indexes, :]
        non_objects_match_contexts = non_objects_for_contexts.all().any()

        return not non_objects_match_contexts


class MemorizingLattice:
    concepts: Dict[int, List[Concept]] = {0: []}
    _lattice: Lattice

    def __init__(self, context_matrix: pd.DataFrame,
                 support_threshold: int) -> None:
        super().__init__()
        self._lattice = Lattice(context_matrix, support_threshold)
        # TODO make a hash function and use set
        repeating_concepts = self._get_base_concepts(context_matrix.columns)
        self.concepts[0] = MemorizingLattice._remove_repeating_concepts(repeating_concepts)

    def calculate_superconcepts(self):
        next_level = len(self.concepts)
        current_concepts = self.concepts[next_level - 1]
        self.concepts[next_level] = self._get_superconcepts(current_concepts)

    def _get_superconcepts(self, concepts: List[Concept]) -> List[Concept]:
        superconcepts = []
        concept_count = len(concepts)
        for i in range(concept_count):
            for j in range(i + 1, concept_count):
                concept_1 = concepts[i]
                concept_2 = concepts[j]
                #Check that there are any shared contexts, otherwise the superconcept will just be the whole matrix
                if binary_series_have_common_items(concept_1.contexts, concept_2.contexts):
                    superconcepts.append(self._lattice.find_superconcept(concept_1, concept_2))

        return self._remove_repeating_concepts(superconcepts)

    def print_concepts(self, level=0, use_confidence=True):
        for concept in self.concepts[level]:
            if use_confidence:
                confidence_matrix = self._lattice.get_confidence_for_concept(concept)
                print(get_matrix_without_zero_columns_and_zero_rows(confidence_matrix))
            else:
                print(concept.get_matrix_without_zero_columns_and_zero_rows())

    def _get_base_concepts(self, objects: pd.Series) -> List[Concept]:
        concepts = []
        for o in objects:
            concept = self._lattice.find_concept_for_object(o)
            concepts.append(concept)
        return concepts

    @staticmethod
    def _remove_repeating_concepts(concepts: List[Concept]):
        return [c for c in concepts if all(c != x or c is x for x in concepts)]
