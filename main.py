from dotenv import load_dotenv
import os
import streamlit as st
from agents.code_conversion.agent import CodeConversionAgent
from data_processor.processor import DataProcessor
from utils.logger import get_logger
from ui.state import initialize_session_state
from ui.components import (
    display_logo, display_code_history, 
    display_chat_history, display_sidebar_actions
)
from ui.constants import (
    APP_TITLE, APP_ICON,
    ALLOWED_FILE_TYPES, OUTPUT_FILENAME
)

def main():
    logger = get_logger("DataCleaning")
    initialize_session_state()
    load_dotenv()

    api_key = os.getenv("DEEPINFRA_API_TOKEN")
    if not api_key:
        st.error("API key not found in environment variables")
        return

    display_logo()
    display_sidebar_actions()
    st.title(APP_TITLE)

    try:
        agent = CodeConversionAgent(api_key)
        processor = DataProcessor(agent)

        uploaded_file = st.file_uploader(
            "Upload your dataset",
            type=ALLOWED_FILE_TYPES
        )

        if uploaded_file and st.session_state.current_df is None:
            try:
                temp_path = f"temp_{uploaded_file.name}"
                with open(temp_path, "wb") as f:
                    f.write(uploaded_file.getbuffer())

                df = processor.load_data(temp_path)
                st.session_state.current_df = df
                # Initialize history with the first DataFrame
                st.session_state.df_history = [df.copy()]
                st.session_state.df_history_position = 0
                os.remove(temp_path)

                st.session_state.chat_history.append({
                    'type': 'data',
                    'content': df.head()
                })

                st.rerun()
            except Exception as e:
                logger.error(f"Error loading file: {e}")
                st.error(f"Error loading file: {str(e)}")
                return

        if st.session_state.current_df is not None:
            display_chat_history()

            # Chat input for user instruction
            user_prompt = st.chat_input("Enter your preprocessing instruction:")

            # Undo and Redo buttons placed directly below the chat input
            with st.container():
                col1, col2 = st.columns([1, 1], gap="small")

                with col1:
                    undo_disabled = len(st.session_state.df_history) <= 1 or st.session_state.df_history_position <= 0
                    if st.button("↩️ Undo", disabled=undo_disabled, use_container_width=True):
                        st.session_state.df_history_position -= 1
                        st.session_state.current_df = st.session_state.df_history[st.session_state.df_history_position]
                        st.session_state.chat_history.append({
                            'type': 'data',
                            'content': st.session_state.current_df.head()
                        })
                        st.rerun()

                with col2:
                    redo_disabled = st.session_state.df_history_position >= len(st.session_state.df_history) - 1
                    if st.button("↪️ Redo", disabled=redo_disabled, use_container_width=True):
                        st.session_state.df_history_position += 1
                        st.session_state.current_df = st.session_state.df_history[st.session_state.df_history_position]
                        st.session_state.chat_history.append({
                            'type': 'data',
                            'content': st.session_state.current_df.head()
                        })
                        st.rerun()

            if user_prompt:
                with st.spinner("Processing..."):
                    try:
                        st.session_state.chat_history.append({
                            'type': 'instruction',
                            'content': user_prompt
                        })

                        code = agent.code_generator.generate_code(
                            user_prompt,
                            list(st.session_state.current_df.columns)
                        )
                        st.session_state.code_snippets.append(code)

                        new_df = processor.process_data(
                            st.session_state.current_df,
                            custom_code=code
                        )

                        if not new_df.equals(st.session_state.current_df):
                            # Remove any future history if not at latest state
                            st.session_state.df_history = st.session_state.df_history[:st.session_state.df_history_position + 1]
                            # Append new state to history
                            st.session_state.df_history.append(new_df.copy())
                            st.session_state.df_history_position += 1
                            st.session_state.current_df = new_df

                        st.session_state.chat_history.append({
                            'type': 'data',
                            'content': st.session_state.current_df.head()
                        })

                        st.rerun()

                    except Exception:
                        logger.error("Processing error occurred", exc_info=True)
                        st.warning("Processing step needs adjustment. Trying alternative approach...")

        display_code_history()

        if st.session_state.get("trigger_download") and st.session_state.current_df is not None:
            try:
                output_file = "cleaned_data.csv"
                processor.save_data(st.session_state.current_df, output_file)

                with open(output_file, "rb") as f:
                    st.session_state.cleaned_data = f.read()

                processor.log_processing_history()
                st.session_state.trigger_download = False
                st.session_state.show_download_message = True
            except Exception as e:
                logger.error(f"Error saving data: {e}")
                st.error(f"Error saving data: {str(e)}")

        if st.session_state.get("show_download_message"):
            with st.container():
                st.success("✅ Data processed successfully! Download below.")
                st.download_button(
                    label="📥 Download Cleaned Data",
                    data=st.session_state.cleaned_data,
                    file_name="cleaned_data.csv",
                    mime="text/csv",
                    key="success_download_btn"
                )
                if st.button("Close Message"):
                    st.session_state.show_download_message = False
                    st.rerun()

    except Exception as e:
        logger.error(f"Error in processing pipeline: {e}")
        st.error(f"An error occurred: {str(e)}")

if __name__ == "__main__":
    st.set_page_config(
        page_title=APP_TITLE,
        page_icon=APP_ICON,
        layout="wide"
    )
    main()
