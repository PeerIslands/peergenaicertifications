import streamlit as st

DEFAULT_FACTORIES = {
    "chain": lambda: None,
    "chat_history": list,
    "last_processed_question": lambda: None,
    "current_question": lambda: "",
    "input_reset_key": lambda: 0,
    "last_bot_message_index": lambda: -1,
}


def _state():
    return st.session_state


def ensure_session_state():
    for key, factory in DEFAULT_FACTORIES.items():
        if key not in _state():
            _state()[key] = factory()


def reset_after_pdf_processing(chain):
    state = _state()
    state["chain"] = chain
    state["chat_history"] = []
    state["last_processed_question"] = None
    state["current_question"] = ""
    state["input_reset_key"] = 0
    state["last_bot_message_index"] = -1


def clear_chat_session():
    state = _state()
    state["chat_history"] = []
    state["last_processed_question"] = None
    state["current_question"] = ""
    state["input_reset_key"] = 0
    state["last_bot_message_index"] = -1


def handle_post_bot_response():
    state = _state()
    if (
        state["chat_history"]
        and state["chat_history"][-1].get("role") == "bot"
        and len(state["chat_history"]) - 1 > state["last_bot_message_index"]
    ):
        state["current_question"] = ""
        state["input_reset_key"] += 1
        state["last_bot_message_index"] = len(state["chat_history"]) - 1


def should_skip_question(question: str) -> bool:
    return question == _state()["last_processed_question"]


def start_question_processing(question: str):
    state = _state()
    state["current_question"] = question
    state["last_processed_question"] = question
    state["chat_history"].append({"role": "user", "content": question})


def add_bot_message(response: str):
    _state()["chat_history"].append({"role": "bot", "content": response})


def rollback_last_user_message():
    state = _state()
    if state["chat_history"] and state["chat_history"][-1].get("role") == "user":
        state["chat_history"].pop()
    state["last_processed_question"] = None

