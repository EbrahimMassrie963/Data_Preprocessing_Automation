import pandas as pd
from .data_analyzer import DataFrameAnalyzer
from .code_generator import CodeGenerator
from .code_executor import CodeExecutor
from .models import CleaningHistory, CleaningHistoryEntry

class DataProcessor:
    """Handles the interactive data processing workflow"""
    def __init__(self, analyzer: DataFrameAnalyzer, generator: CodeGenerator, executor: CodeExecutor):
        self.analyzer = analyzer
        self.generator = generator
        self.executor = executor
        self.cleaning_history = CleaningHistory()

    def process_data(self, df: pd.DataFrame) -> pd.DataFrame:
        iteration = 1
        
        while True:
            print(f"\n=== Processing Iteration {iteration} ===")
            self._display_data_state(df)
            
            instruction = self._get_user_instruction()
            if instruction.lower() == 'exit':
                print("\nProcessing completed!")
                break
            
            df = self._process_instruction(df, instruction, iteration)
            iteration += 1
        
        return df

    def _display_data_state(self, df: pd.DataFrame) -> None:
        data_state = self.analyzer.get_data_state(df)
        print("\nCurrent data sample:")
        print(data_state.head)

    @staticmethod
    def _get_user_instruction() -> str:
        return input("\nEnter your data processing instruction (or 'exit' to finish): ")

    def _process_instruction(self, df: pd.DataFrame, instruction: str, iteration: int) -> pd.DataFrame:
        try:
            code = self.generator.generate_code(instruction, list(df.columns))
            print("\nProposed code:")
            print(code)
            
            if input("\nExecute this code? (yes/no): ").lower() != 'yes':
                return df
            
            processed_df = self.executor.execute_code(df, code)
            if processed_df is not None:
                self.cleaning_history.add_entry(CleaningHistoryEntry(
                    iteration=iteration,
                    instruction=instruction,
                    code=code,
                    successful=True
                ))
                print("\nOperation completed. Updated data sample:")
                print(processed_df.head())
                return processed_df
            return df
        except Exception as e:
            print(f"\nError processing instruction: {e}")
            print("Please try rephrasing your instruction or try a different operation.")
            return df