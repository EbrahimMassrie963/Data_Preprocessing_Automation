import streamlit as st
from .constants import LOGO_PATH, LOGO_WIDTH, APP_TITLE

def display_logo():
    st.sidebar.image(LOGO_PATH, width=LOGO_WIDTH)
    st.sidebar.title(APP_TITLE)

def display_code_history():
    st.sidebar.subheader("Processing Steps")
    for i, code in enumerate(st.session_state.code_snippets, 1):
        with st.sidebar.expander(f"Step {i}"):
            st.code(code, language="python")

def display_chat_history():
    with st.container():
        for entry in st.session_state.chat_history:
            if entry['type'] == 'instruction':
                with st.chat_message("user"):
                    st.markdown(entry['content'])
            elif entry['type'] == 'data':
                with st.chat_message("assistant"):
                    st.write("Data Preview:")
                    st.dataframe(entry['content'])

def display_sidebar_actions():
    with st.sidebar:
        st.subheader("Actions")
        btn_col1, btn_col2 = st.columns(2)

        with btn_col1:
            if st.button("✅ Finish", use_container_width=True):
                st.session_state.trigger_download = True

        with btn_col2:
            if st.button("🗑️ Clear", use_container_width=True):
                st.session_state.confirm_clear = True

        handle_clear_confirmation()
        st.markdown("---")

def handle_clear_confirmation():
    if st.session_state.confirm_clear:
        st.warning("Clear all chat and data?")
        col1, col2 = st.columns(2)
        with col1:
            if st.button("Yes, clear all"):
                for key in ["chat_history", "code_snippets", "current_df"]:
                    if key in st.session_state:
                        del st.session_state[key]
                st.session_state.confirm_clear = False
                st.rerun()
        with col2:
            if st.button("Cancel"):
                st.session_state.confirm_clear = False
                st.rerun()