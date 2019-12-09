import pandas as pd


class Lattice:
    context_matrix: pd.DataFrame
    threshold: int

    def __init__(self, context_matrix: pd.DataFrame, threshold: int) -> None:
        super().__init__()
        self.context_matrix = context_matrix
        self.threshold = threshold

    def _filter_rows_below_threshold(self, column: str) -> pd.DataFrame:
        above_threshold = self.context_matrix[column] >= self.threshold
        filtered = self.context_matrix[above_threshold]
        return filtered

    def _filter_columns_below_threshold(self, filtered_rows: pd.DataFrame) -> pd.DataFrame:
        print("Filter columns")
        transposed = filtered_rows.transpose()
        columns = transposed.columns
        print(transposed[columns][0])
        # result_s = transposed[(transposed[columns] >= self.threshold).all(axis=1)]
        # # filter = transposed[resu] >= self.threshold
        # # above_threshold_transposed = transposed[filter]
        # return result_s.transpose()
