# pyright: reportMissingImports=false

# tests/test_session_state.py
import streamlit as st
import pytest

from src.state.session_state import (
    ensure_session_state,
    reset_after_pdf_processing,
    clear_chat_session,
    handle_post_bot_response,
    should_skip_question,
    start_question_processing,
    add_bot_message,
    rollback_last_user_message,
)


@pytest.fixture(autouse=True)
def mock_session_state(monkeypatch):
    """
    Replace st.session_state with a plain dict for testing.
    """
    mock_state = {}
    monkeypatch.setattr(st, "session_state", mock_state, raising=False)
    return mock_state


def test_ensure_session_state_initializes_defaults(mock_session_state):
    ensure_session_state()

    assert "chain" in mock_session_state
    assert "chat_history" in mock_session_state
    assert "last_processed_question" in mock_session_state
    assert "current_question" in mock_session_state
    assert "input_reset_key" in mock_session_state
    assert "last_bot_message_index" in mock_session_state


def test_reset_after_pdf_processing_sets_initial_values(mock_session_state):
    ensure_session_state()
    dummy_chain = object()

    reset_after_pdf_processing(dummy_chain)

    assert mock_session_state["chain"] is dummy_chain
    assert mock_session_state["chat_history"] == []
    assert mock_session_state["last_processed_question"] is None
    assert mock_session_state["current_question"] == ""
    assert mock_session_state["input_reset_key"] == 0
    assert mock_session_state["last_bot_message_index"] == -1


def test_clear_chat_session_clears_history_and_state(mock_session_state):
    ensure_session_state()
    mock_session_state["chat_history"] = [{"role": "user", "content": "hi"}]
    mock_session_state["last_processed_question"] = "hi"
    mock_session_state["current_question"] = "hi"
    mock_session_state["input_reset_key"] = 3
    mock_session_state["last_bot_message_index"] = 5

    clear_chat_session()

    assert mock_session_state["chat_history"] == []
    assert mock_session_state["last_processed_question"] is None
    assert mock_session_state["current_question"] == ""
    assert mock_session_state["input_reset_key"] == 0
    assert mock_session_state["last_bot_message_index"] == -1


def test_start_question_processing_updates_state_and_history(mock_session_state):
    ensure_session_state()

    start_question_processing("What is GAN?")
    history = mock_session_state["chat_history"]

    assert mock_session_state["current_question"] == "What is GAN?"
    assert mock_session_state["last_processed_question"] == "What is GAN?"
    assert len(history) == 1
    assert history[0]["role"] == "user"
    assert history[0]["content"] == "What is GAN?"


def test_should_skip_question(mock_session_state):
    ensure_session_state()
    mock_session_state["last_processed_question"] = "same question"

    assert should_skip_question("same question") is True
    assert should_skip_question("different question") is False


def test_add_bot_message_appends_to_history(mock_session_state):
    ensure_session_state()
    mock_session_state["chat_history"] = []

    add_bot_message("This is an answer.")

    assert len(mock_session_state["chat_history"]) == 1
    assert mock_session_state["chat_history"][0]["role"] == "bot"
    assert mock_session_state["chat_history"][0]["content"] == "This is an answer."


def test_handle_post_bot_response_resets_input(mock_session_state):
    ensure_session_state()
    mock_session_state["chat_history"] = [
        {"role": "user", "content": "Q"},
        {"role": "bot", "content": "A"},
    ]
    mock_session_state["current_question"] = "Q"
    mock_session_state["input_reset_key"] = 0
    mock_session_state["last_bot_message_index"] = -1

    handle_post_bot_response()

    assert mock_session_state["current_question"] == ""
    assert mock_session_state["input_reset_key"] == 1
    assert mock_session_state["last_bot_message_index"] == 1


def test_rollback_last_user_message_removes_last_user(mock_session_state):
    ensure_session_state()
    mock_session_state["chat_history"] = [
        {"role": "user", "content": "Q1"},
        {"role": "user", "content": "Q2"},
    ]
    mock_session_state["last_processed_question"] = "Q2"

    rollback_last_user_message()

    assert len(mock_session_state["chat_history"]) == 1
    assert mock_session_state["chat_history"][0]["content"] == "Q1"
    assert mock_session_state["last_processed_question"] is None
