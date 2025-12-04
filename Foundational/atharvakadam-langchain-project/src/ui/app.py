import streamlit as st

from .html_templates import css, bot_template, user_template
from ..services.qa_chain import create_qa_chain, handle_user_query
from ..state.session_state import (
    ensure_session_state,
    reset_after_pdf_processing,
    clear_chat_session,
    handle_post_bot_response,
    should_skip_question,
    start_question_processing,
    add_bot_message,
    rollback_last_user_message,
)


def main():
    st.set_page_config(page_title="Chat with your PDF", page_icon=":books:")
    st.write(css, unsafe_allow_html=True)

    ensure_session_state()

    st.header("Chat with your PDF :books:")

    with st.sidebar:
        st.subheader("Upload PDF Document")
        pdf_file = st.file_uploader("Upload your PDF file", type="pdf")

        if pdf_file is not None:
            if st.button("Process PDF"):
                with st.spinner("Processing PDF and creating vector store..."):
                    try:
                        chain = create_qa_chain(pdf_file)
                    except Exception as exc:
                        st.error(f"Failed to process PDF: {exc}")
                        chain = None

                    if chain:
                        reset_after_pdf_processing(chain)
                        st.success("PDF processed successfully! You can now ask questions.")
                    else:
                        st.error("Failed to process PDF. Please try again.")

        if st.session_state.chain is None:
            st.info("Please upload a PDF file to get started")
        else:
            st.success("PDF is ready for queries")
            if st.button("Clear Chat History"):
                clear_chat_session()
                st.rerun()

    if st.session_state.chain is None:
        st.info("Please upload a PDF file using the sidebar to start asking questions.")
        return

    for message in st.session_state.chat_history:
        template = user_template if message["role"] == "user" else bot_template
        st.write(template.replace("{{MSG}}", message["content"]), unsafe_allow_html=True)

    handle_post_bot_response()

    with st.form(key="question_form", clear_on_submit=False):
        user_question = st.text_input(
            "Ask a question about your PDF:",
            key=f"user_input_{st.session_state.input_reset_key}",
            value=st.session_state.current_question,
        )
        submit_button = st.form_submit_button(label="Submit")

    if submit_button and user_question and not should_skip_question(user_question):
        start_question_processing(user_question)

        with st.spinner("Thinking..."):
            try:
                response = handle_user_query(st.session_state.chain, user_question)
            except Exception as exc:
                st.error(f"Error processing query: {exc}")
                response = None

        if response:
            add_bot_message(response)
            st.rerun()
        else:
            st.error("Failed to get response. Please try again.")
            rollback_last_user_message()

