'''
this is the Base Agent, other Agent inherit it.
'''


from typing import List, Dict, Optional, Callable
from langchain_community.chat_models import ChatDeepInfra
from langchain_core.messages import AIMessage, HumanMessage
import json
import logging
import traceback
import os
from datetime import datetime
from utils.logger import get_logger

logger = get_logger()

class QwenAgent:
    """
    A wrapper class for interacting with Qwen models via DeepInfra.
    
    This class provides a convenient interface for generating responses from Qwen models,
    managing conversation history, and configuring model parameters.
    """
    
    def __init__(
        self,
        api_key: str,
        model_name: str = "Qwen/Qwen2.5-Coder-7B",
        prompt: str = "You are Assistant",
        memory: bool = False,
        memory_limit: int = 3,
        max_tokens: int = 2048,
        temperature: float = 0.2,
        stream: bool = False,
        debug_mode: bool = False,
        stream_callback: Optional[Callable[[str], None]] = None
    ):
        """Initialize a new QwenAgent instance."""
        try:
            self.chat_model = ChatDeepInfra(
                model=model_name,
                temperature=temperature,
                max_tokens=max_tokens,
                deepinfra_api_token=api_key
            )
            
            self.model_name = model_name
            self.system_prompt = prompt
            self.use_memory = memory
            self.memory_limit = memory_limit
            self.max_tokens = max_tokens
            self.temperature = temperature
            self.stream = stream
            self.history: List[Dict[str, str]] = []
            self.prompts = {"default": self.system_prompt}
            self.debug_mode = debug_mode
            self.stream_callback = stream_callback if stream_callback else self.default_stream_callback

            logger.setLevel(logging.DEBUG if debug_mode else logging.INFO)
            logger.info("QwenAgent initialized successfully.")
            
        except Exception as e:
            logger.error(f"Failed to initialize QwenAgent: {e}\n{traceback.format_exc()}")
            raise

    def set_prompt(self, new_prompt: str) -> None:
        """Update the system prompt."""
        self.system_prompt = new_prompt
        self.prompts["default"] = new_prompt
        logger.info("System prompt updated.")

    def set_model(self, model_name: str) -> None:
        """Change the Qwen model being used."""
        self.model_name = model_name
        self.chat_model.model = model_name
        logger.info(f"Model switched to {model_name}.")

    def toggle_memory(self, status: bool) -> None:
        """Enable or disable conversation memory."""
        self.use_memory = status
        if not status:
            self.clear_memory()
        logger.info(f"Memory toggled to {'ON' if status else 'OFF'}.")

    def set_memory_limit(self, limit: int) -> None:
        """Set the maximum number of conversation turns to remember."""
        self.memory_limit = limit
        logger.info(f"Memory limit set to {limit} messages.")

    def set_max_tokens(self, max_tokens: int) -> None:
        """Set the maximum number of tokens in generated responses."""
        self.max_tokens = max_tokens
        self.chat_model.max_tokens = max_tokens
        logger.info(f"Max output tokens set to {max_tokens}.")

    def set_temperature(self, temperature: float) -> None:
        """Set the temperature parameter for response generation."""
        self.temperature = temperature
        self.chat_model.temperature = temperature
        logger.info(f"Temperature set to {temperature}.")

    def toggle_stream(self, status: bool) -> None:
        """Enable or disable response streaming."""
        self.stream = status
        logger.info(f"Streaming toggled to {'ON' if status else 'OFF'}.")

    def clear_memory(self) -> None:
        """Clear the conversation history."""
        self.history = []
        logger.info("Conversation history cleared.")

    def save_memory_to_file(self, filename: str = None) -> None:
        """Save the conversation history to a JSON file."""
        try:
            chats_dir = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), 'chats')
            if not os.path.exists(chats_dir):
                os.makedirs(chats_dir)
                logger.info(f"Created chats directory at {chats_dir}")
            
            if filename is None:
                timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
                filename = os.path.join(chats_dir, f"chat_{timestamp}.json")
            elif not os.path.isabs(filename):
                filename = os.path.join(chats_dir, filename)
                
            with open(filename, 'w') as f:
                json.dump(self.history, f)
            logger.info(f"Memory saved to {filename}.")
            return filename
        except Exception as e:
            logger.error(f"Error saving memory: {e}\n{traceback.format_exc()}")
            return None

    def load_memory_from_file(self, filename: str) -> None:
        """Load conversation history from a JSON file."""
        try:
            if not os.path.isabs(filename):
                chats_dir = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), 'chats')
                filename = os.path.join(chats_dir, filename)
                
            with open(filename, 'r') as f:
                self.history = json.load(f)
            logger.info(f"Memory loaded from {filename}.")
        except Exception as e:
            logger.error(f"Error loading memory: {e}\n{traceback.format_exc()}")

    def default_stream_callback(self, chunk: str) -> None:
        """Default callback function for handling streaming response chunks."""
        print(chunk, end="", flush=True)

    def generate_response(self, user_input: str) -> Optional[str]:
        """Generate a response from the Qwen model."""
        try:
            if self.use_memory:
                self.history.append({"role": "user", "text": user_input})
                self.history = self.history[-self.memory_limit * 2:]

            messages = [
                ("system", self.system_prompt),
                *[(msg["role"], msg["text"]) for msg in self.history],
                ("user", user_input)
            ]

            response = self.chat_model.invoke(messages)
            response_text = response.content

            if self.use_memory:
                self.history.append({"role": "assistant", "text": response_text})

            logger.info("User input processed successfully.")
            return response_text

        except Exception as e:
            logger.error(f"Error generating response: {e}\n{traceback.format_exc()}")
            print(f"\nAn error occurred while processing your request. Details: {e}")
            return None

    def chat_loop(self) -> None:
        """Start an interactive chat loop in the console."""
        try:
            print(f"Welcome to {self.model_name} conversation! (type 'exit' to quit)")
            while True:
                user_input = input("You: ")
                if user_input.strip().lower() in ["exit", "quit", "خروج"]:
                    print("Conversation ended.")
                    logger.info("Conversation loop terminated by user.")
                    break
                response = self.generate_response(user_input)
                if response is not None and not self.stream:
                    print(f"{self.model_name}: {response}")
        except KeyboardInterrupt:
            print("\nConversation interrupted by user.")
            logger.info("Conversation loop interrupted by user (KeyboardInterrupt).")
        except Exception as e:
            logger.error(f"Unexpected error in chat loop: {e}\n{traceback.format_exc()}")
            print("An unexpected error occurred. Check log for details.")