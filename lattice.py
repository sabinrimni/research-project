import pandas as pd


class Lattice:
    context_matrix: pd.DataFrame
    threshold: int

    def __init__(self, context_matrix: pd.DataFrame, threshold: int) -> None:
        super().__init__()
        self.context_matrix = context_matrix
        self.threshold = threshold

    def find_operations_for_context(self, context: str) -> pd.DataFrame:
        if context not in self.context_matrix:
            return pd.DataFrame()
        filtered_rows = self._filter_rows_below_threshold(context)
        return self._filter_columns_below_threshold(filtered_rows)

    def _filter_rows_below_threshold(self, column: str) -> pd.DataFrame:
        above_threshold = self.context_matrix[column] >= self.threshold
        filtered = self.context_matrix[above_threshold]
        return filtered

    def _filter_columns_below_threshold(self, filtered_rows: pd.DataFrame) -> pd.DataFrame:
        transposed = filtered_rows.transpose()
        columns = transposed.columns
        filtered_columns_transposed = \
            transposed[(transposed[columns] >= self.threshold).all(axis=1)]
        return filtered_columns_transposed.transpose()
