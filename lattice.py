from functools import partial, partialmethod
from typing import List, Tuple, Dict, Iterable, Union, Callable, Optional

import pandas as pd


def save_data_frames_to_excel(filename: str, data_frames: List[pd.DataFrame]):
    writer = pd.ExcelWriter(filename)
    for i, df in enumerate(data_frames):
        df.to_excel(writer, f'sheet{i}')
    writer.save()


def read_data_frames_from_excel(filename: str) -> List[pd.DataFrame]:
    xls = pd.ExcelFile(filename)
    sheets_to_frames = pd.read_excel(xls, sheet_name=None, index_col=0)
    return sheets_to_frames.values()


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
    confidence: float

    def __init__(self, binary_matrix: pd.DataFrame, contexts: pd.Series,
                 objects: pd.Series, confidence: float) -> None:
        super().__init__()
        self.binary_matrix = binary_matrix
        self.contexts = contexts
        self.objects = objects
        self.confidence = confidence

    def __str__(self) -> str:
        return f"Contexts:\n{self.contexts}\nObjects:\n{self.objects}" + \
               f"\nMatrix\n{self.binary_matrix}, Confidence {self.confidence}"

    def __repr__(self) -> str:
        return f"(Contexts: {self.contexts}, Objects: {self.objects}), Confidence: {self.confidence}"

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
        confidence = self._calculate_mean_confidence_for_objects(objects)
        subconcept = Concept(concept_matrix, contexts, objects, confidence)
        assert self._is_proper_concept(subconcept), f"Subconcept {subconcept} is not proper"
        return subconcept

    def find_superconcept(self, concept_1: Concept, concept_2: Concept) -> Concept:
        assert self._is_proper_concept(concept_1), f"Concept1 {concept_1} is not proper"
        assert self._is_proper_concept(concept_2), f"Concept1 {concept_2} is not proper"

        contexts = self._find_series_intersection(concept_1.contexts, concept_2.contexts)
        superconcept = self._create_concept_from_contexts(contexts)
        assert self._is_proper_concept(superconcept), f"Superconcept {superconcept} is not proper"
        return superconcept

    def find_concept_for_object(self, object: str) -> Concept:
        contexts = self.binary_matrix[object]
        concept = self._create_concept_from_contexts(contexts)
        assert self._is_proper_concept(concept), f"{concept} is not a proper concept"
        return concept

    def create_concept_from_concept_matrix(self, concept_matrix: pd.DataFrame) -> Concept:
        objects = self._find_objects_from_concept_matrix(concept_matrix)
        contexts = self._find_contexts_from_concept_matrix(concept_matrix, objects)
        confidence = self._calculate_mean_confidence_for_objects(objects)
        concept = Concept(concept_matrix, contexts, objects, confidence)
        assert self._is_proper_concept(concept), f"Concept from matrix not proper: {concept}"
        return concept

    def _create_concept_from_contexts(self, contexts: pd.Series) -> Concept:
        concept_matrix = self._zero_columns_not_matching_contexts(contexts, self.binary_matrix)
        objects = self._find_objects_from_concept_matrix(concept_matrix)
        confidence = self._calculate_mean_confidence_for_objects(objects)
        concept = Concept(concept_matrix, contexts, objects, confidence)
        return concept

    def _get_support_matrix_for_objects(self, objects: pd.Series) -> pd.DataFrame:
        return self.context_matrix[objects]

    def _get_confidence_matrix_from_support_matrix(self,
                                                   support_matrix: pd.DataFrame) -> pd.DataFrame:
        context_counts = self.context_matrix.sum(axis=1)
        return support_matrix.divide(context_counts, axis=0)

    def _calculate_mean_confidence_from_confidence_matrix(self,
                                                          confidence_matrix: pd.DataFrame) -> float:
        return confidence_matrix.mean().mean()

    def _calculate_mean_confidence_for_objects(self, objects: pd.Series):
        support_matrix = self._get_support_matrix_for_objects(get_non_zero_series_indexes(objects))
        confidence_matrix = self._get_confidence_matrix_from_support_matrix(support_matrix)
        return self._calculate_mean_confidence_from_confidence_matrix(confidence_matrix)

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
    concepts: List[Concept] = []
    superconcepts: List[Concept] = []
    _lattice: Lattice

    def __init__(self, context_matrix: pd.DataFrame,
                 support_threshold: int) -> None:
        super().__init__()
        self._lattice = Lattice(context_matrix, support_threshold)

    def calculate_concepts(self):
        repeating_concepts = self._get_base_concepts(self._lattice.context_matrix.columns)
        self.concepts = repeating_concepts  # MemorizingLattice._remove_repeating_concepts(repeating_concepts)

    def calculate_superconcepts(self, confidence_threshold: float) -> None:
        superconcept_op = lambda c_1, c_2: \
            self._create_superconcept_if_better(c_1, c_2, confidence_threshold)
        superconcepts = self._merge_concepts_til_convergence(self.concepts, superconcept_op)
        non_repeating_superconcepts = self._remove_repeating_concepts(superconcepts)
        not_contained_objects = self._get_not_contained_objects_of_concepts(
            non_repeating_superconcepts
        )
        assert len(not_contained_objects) == 0

        self.superconcepts = non_repeating_superconcepts  # + concepts_for_not_contained

    def _get_not_contained_objects_of_concepts(self, concepts: List[Concept]) -> List[str]:
        assert len(concepts) > 0
        objects = concepts[0].objects
        for i in range(1, len(concepts)):
            concept = concepts[i]
            objects = objects + concept.objects
        return get_zero_series_indexes(objects).tolist()

    # def _get_base_concepts_for_objects(self, objects: List[str]):
    #     base_concepts = []
    #     for object in objects:
    #         found = False
    #         for concept in self.concepts:
    #             if concept.objects[object] != 0:
    #                 base_concepts.append(concept)
    #                 found = True
    #                 break
    #         assert found, f"Concept not found for object {object}"
    #     return base_concepts

    def _merge_concepts_til_convergence(self, concepts: List[Concept],
                                        merge_op: Callable[[Concept, Concept], Optional[Concept]]
                                        ) -> List[Concept]:
        queue = concepts.copy()
        resulting_concepts = []
        while len(queue) > 1:
            current_concept = queue.pop(0)
            max_concepts_to_check = len(queue)
            print(f"Max to check: {max_concepts_to_check}")
            while max_concepts_to_check > 0:
                next_concept = queue.pop(0)
                merged = merge_op(current_concept, next_concept)
                if merged is not None:
                    queue.append(merged)
                    break
                queue.append(next_concept)
                max_concepts_to_check -= 1
            if max_concepts_to_check == 0:
                resulting_concepts.append(current_concept)

        return resulting_concepts + queue

    def _create_superconcept_if_better(self, concept_1: Concept, concept_2: Concept,
                                       confidence_threshold: float) -> Optional[Concept]:
        if binary_series_have_common_items(concept_1.contexts, concept_2.contexts):
            superconcept = self._lattice.find_superconcept(concept_1, concept_2)
            if self._is_better_confidence(concept_1, concept_2, superconcept, confidence_threshold):
                return superconcept
        return None

    def _create_subconcept_if_better(self, concept_1: Concept, concept_2: Concept,
                                     confidence_threshold: float):
        if binary_series_have_common_items(concept_1.objects, concept_2.objects):
            subconcept = self._lattice.find_subconcept(concept_1, concept_2)
            if self._is_better_confidence(concept_1, concept_2, subconcept, confidence_threshold):
                return subconcept
        return None

    def _is_better_confidence(self, concept_1: Concept, concept_2: Concept, merged_concept: Concept,
                              uncertanity_threshold: float) -> bool:
        return concept_1.confidence - uncertanity_threshold <= merged_concept.confidence \
               and concept_2.confidence - uncertanity_threshold <= merged_concept.confidence

    # def _get_superconcepts(self, concepts: List[Concept]) -> List[Concept]:
    #     superconcepts = []
    #     concept_count = len(concepts)
    #     for i in range(concept_count):
    #         for j in range(i + 1, concept_count):
    #             concept_1 = concepts[i]
    #             concept_2 = concepts[j]
    #             # Check that there are any shared contexts, otherwise the superconcept will just be the whole matrix
    #             if binary_series_have_common_items(concept_1.contexts, concept_2.contexts):
    #                 superconcepts.append(self._lattice.find_superconcept(concept_1, concept_2))
    #
    #     return self._remove_repeating_concepts(superconcepts)

    def print_concepts(self, use_confidence=True):
        print(f"\nPrinting concepts, using confidence {use_confidence}\n")
        for concept in self.concepts:
            self._print_concept(concept)

    def print_superconcepts(self, use_confidence=True):
        print(f"\nPrinting superconcepts, using confidence {use_confidence}\n")
        for superconcept in self.superconcepts:
            self._print_concept(superconcept)

    def save_superconcepts(self, filename: str):
        data = [s.binary_matrix for s in self.superconcepts]
        save_data_frames_to_excel(filename, data)

    def load_superconcepts(self, filename: str):
        concept_matrices = read_data_frames_from_excel(filename)
        self.superconcepts = [self._lattice.create_concept_from_concept_matrix(matrix)
                              for matrix in concept_matrices]

    def _print_concept(self, concept: Concept, use_confidence=True):
        if use_confidence:
            print(f"Confidence: {concept.confidence}")
        else:
            print(concept.get_matrix_without_zero_columns_and_zero_rows())
            print("")

    def _get_base_concepts(self, objects: pd.Series) -> List[Concept]:
        concepts = []
        base_concepts_left = len(objects)
        for o in objects:
            print(f"Base concepts left: {base_concepts_left}")
            base_concepts_left -= 1
            concept = self._lattice.find_concept_for_object(o)
            concepts.append(concept)
        return concepts

    @staticmethod
    def _remove_repeating_concepts(concepts: List[Concept]):
        # TODO make a hash function and use set, also fix this as it removes some concepts it shouldn't
        return [c for c in concepts if all(c != x or c is x for x in concepts)]
