import re
from typing import List
from ..base.qwen_agent import QwenAgent

class CodeGenerator:
    """Handles code generation and extraction"""
    def __init__(self, llm_agent: QwenAgent):
        self.llm_agent = llm_agent

    def generate_code(self, instruction: str, columns: List[str]) -> str:
        code_prompt = f"""
        Convert this instruction into executable Python code:
        {instruction}
        
        Available DataFrame columns:
        {', '.join(columns)}
        
        Generate complete, executable code that works with a DataFrame named 'df'.
        Include only necessary imports (pandas as pd, numpy as np, sklearn,...).
        """
        response = self.llm_agent.generate_response(code_prompt)
        return self._extract_code(response)

    @staticmethod
    def _extract_code(text: str) -> str:
        code_blocks = re.findall(r"```(?:python)?(.*?)```", text, flags=re.DOTALL)
        code = code_blocks[0] if code_blocks else text
        return code.strip()