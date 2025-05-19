###############

'''
this is unsused Agent.....
'''

##############

from agents.qwen_agent import QwenAgent
import pandas as pd
import numpy as np
from io import StringIO
import re
from typing import Optional, Dict

class CodeConversionAgent(QwenAgent):
    def __init__(self, api_key: str):
        super().__init__(
            api_key=api_key,
            model_name="Qwen/Qwen2.5-Coder-7B",
            prompt="""You are a Python code generation assistant that converts natural language instructions into executable pandas/numpy code.

                        Your task is to:
                        1. Convert English text descriptions into working Python code
                        2. Use only pandas (pd) and numpy (np) libraries
                        3. Work with a DataFrame named 'df'
                        4. Generate complete, executable code with necessary imports
                        5. Handle data cleaning and transformation tasks

                        Example Input/Output:
                        Input: "Remove all duplicate rows from the dataframe"
                        Output: ```python
                        import pandas as pd
                        import numpy as np
                        df = df.drop_duplicates()""",
            temperature=0.1
        )
        self.cleaning_history = []

    def get_data_state(self, df: pd.DataFrame) -> Dict[str, str]:
        """Get current DataFrame state including null values"""
        buffer = StringIO()
        df.info(memory_usage='deep', show_counts=True, buf=buffer)
        return {
            'head': df.head().to_string(),
            'info': buffer.getvalue(),
            'null_info': df.isnull().sum().to_string()
        }

    def generate_code(self, instruction: str, columns: list) -> str:
        """Convert natural language instruction to Python code"""
        code_prompt = f"""
        Convert this instruction into executable Python code:
        {instruction}
        
        Available DataFrame columns:
        {', '.join(columns)}
        
        Generate complete, executable code that works with a DataFrame named 'df'.
        Include only necessary imports (pandas as pd, numpy as np, sklearn,...).
        """
        response = self.generate_response(code_prompt)
        return self._extract_code(response)

    def _extract_code(self, text: str) -> str:
        """Extract and clean code from model response"""
        code_blocks = re.findall(r"```(?:python)?(.*?)```", text, flags=re.DOTALL)
        code = code_blocks[0] if code_blocks else text
        return code.strip()

    def execute_code(self, df: pd.DataFrame, code: str, max_retries: int = 3) -> Optional[pd.DataFrame]:
        """Execute code with retry mechanism"""
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
                error_msg = str(e)
                if retries < max_retries - 1:
                    # Generate error-specific prompt
                    error_prompt = f"""
                    Fix this code that raised an error:
                    Error message: {error_msg}
                    
                    Original code:
                    {original_code}
        
                    Requirements:
                    1. Provide alternative implementation if needed
                    2. Ensure the code achieves the same goal
                    """
                    
                    # Silently get corrected code
                    corrected_code = self.generate_code(error_prompt, list(df.columns))
                    code = corrected_code
                    retries += 1
                else:
                    return None

    def process_data(self, df: pd.DataFrame) -> pd.DataFrame:
        """Interactive data processing workflow"""
        iteration = 1
        
        while True:
            print(f"\n=== Processing Iteration {iteration} ===")
            
            # Show current data state
            data_state = self.get_data_state(df)
            print("\nCurrent data sample:")
            print(data_state['head'])
            
            # Get user instruction
            instruction = input("\nEnter your data processing instruction (or 'exit' to finish): ")
            if instruction.lower() == 'exit':
                print("\nProcessing completed!")
                break
            
            # Generate and show code
            code = self.generate_code(instruction, list(df.columns))
            print("\nProposed code:")
            print(code)
            
            # Get user approval
            if input("\nExecute this code? (yes/no): ").lower() != 'yes':
                continue
            
            # Execute code
            processed_df = self.execute_code(df, code)
            if processed_df is not None:
                df = processed_df
                self.cleaning_history.append({
                    'iteration': iteration,
                    'instruction': instruction,
                    'code': code,
                    'successful': True
                })
                
                print("\nOperation completed. Updated data sample:")
                print(df.head())
            
            iteration += 1
        
        return df