from ..base.qwen_agent import QwenAgent
from .data_analyzer import DataFrameAnalyzer
from .code_generator import CodeGenerator
from .code_executor import CodeExecutor
from .data_processor import DataProcessor
from utils.config import CODE_CONVERSION_PROMPT, MODEL_NAME
import pandas as pd

class CodeConversionAgent(QwenAgent):
    """Main agent class that orchestrates the data processing workflow"""
    def __init__(self, api_key: str):
        super().__init__(
            api_key=api_key,
            model_name=MODEL_NAME,
            prompt=CODE_CONVERSION_PROMPT,
            temperature=0.1
        )
        
        # Initialize components
        self.code_generator = CodeGenerator(self)
        self.data_analyzer = DataFrameAnalyzer()
        self.code_executor = CodeExecutor(self.code_generator)
        self.data_processor = DataProcessor(
            self.data_analyzer,
            self.code_generator,
            self.code_executor
        )

    def process_data(self, df: pd.DataFrame) -> pd.DataFrame:
        return self.data_processor.process_data(df)