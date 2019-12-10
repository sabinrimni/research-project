import pandas as pd


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

    # def find_operations_for_context(self, context: str) -> pd.DataFrame:
    #     if context not in self.context_matrix:
    #         return pd.DataFrame()
    #     filtered_rows = self._filter_rows_below_threshold(context, self.context_matrix)
    #     return self._filter_columns_below_threshold(filtered_rows)

    def find_superconcept(self, concept_1: pd.DataFrame, concept_2: pd.DataFrame) -> pd.DataFrame:

        pass

    def find_concept_for_object_as_bin_matrix(self, object: str) -> pd.DataFrame:
        return self._zero_columns_not_matching_column(object, self.binary_matrix)

    def find_concept_for_object_as_filtered_matrix(self, object: str) -> pd.DataFrame:
        matrix_copy: pd.DataFrame = self.context_matrix.copy()
        if object not in matrix_copy:
            matrix_copy[matrix_copy.columns] = 0
            return matrix_copy
        filtered_rows = self._filter_rows_below_threshold(object, matrix_copy)
        return self._filter_columns_below_threshold(filtered_rows).transpose()

    @staticmethod
    def _create_binary_matrix_based_on_threshold(context_matrix: pd.DataFrame,
                                                 threshold: int):
        matrix = context_matrix.copy()
        above_threshold = matrix[matrix.columns] >= threshold
        matrix[matrix.columns] = 0
        matrix[above_threshold] = 1
        return matrix

    @staticmethod
    def _zero_columns_not_matching_column(column: str,
                                          binary_matrix: pd.DataFrame) -> pd.DataFrame:
        matrix = binary_matrix.copy()
        for c in matrix.columns:
            non_matching_rows = matrix[column] > matrix[c]
            if non_matching_rows.any():
                matrix[c] = 0
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
