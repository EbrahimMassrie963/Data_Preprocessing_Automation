import pandas as pd
from io import StringIO
from .models import DataState

class DataFrameAnalyzer:
    """Handles DataFrame analysis and state reporting"""
    @staticmethod
    def get_data_state(df: pd.DataFrame) -> DataState:
        buffer = StringIO()
        df.info(memory_usage='deep', show_counts=True, buf=buffer)
        return DataState(
            head=df.head().to_string(),
            info=buffer.getvalue(),
            null_info=df.isnull().sum().to_string()
        )