import streamlit as st

def initialize_session_state():
    """Initialize all session state variables"""
    default_states = {
        'current_df': None,
        'code_snippets': [],
        'chat_history': [],
        'confirm_clear': False,
        'trigger_download': False,
        'show_download_message': False,
        'df_history': [],
        'df_history_position': -1
    }
    
    for key, default_value in default_states.items():
        if key not in st.session_state:
            st.session_state[key] = default_value