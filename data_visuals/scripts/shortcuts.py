import pandas as pd


def row_index(row: pd.DataFrame):
	return row.index.tolist()[0]
