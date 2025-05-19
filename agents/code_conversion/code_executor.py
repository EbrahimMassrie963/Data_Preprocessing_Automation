import pandas as pd
import numpy as np
from typing import Optional
from .code_generator import CodeGenerator

class CodeExecutor:
    """Handles code execution and error recovery"""
    def __init__(self, code_generator: CodeGenerator):
        self.code_generator = code_generator

    def execute_code(self, df: pd.DataFrame, code: str, max_retries: int = 3) -> Optional[pd.DataFrame]:
        retries = 0
        original_code = code
        while retries < max_retries:
            try:
                local_dict = {
                    'df': df.copy(),
                    'pd': pd,
                    'np': np
                }
                exec(code, globals(), local_dict)
                return local_dict['df']
            except Exception as e:
                if retries < max_retries - 1:
                    code = self._handle_error(e, original_code, df)
                    retries += 1
                else:
                    return None

    def _handle_error(self, error: Exception, original_code: str, df: pd.DataFrame) -> str:
        error_prompt = f"""
        Fix this code that raised an error:
        Error message: {str(error)}
        
        Original code:
        {original_code}

        Requirements:
        1. Provide alternative implementation if needed
        2. Ensure the code achieves the same goal
        """
        return self.code_generator.generate_code(error_prompt, list(df.columns))