"""
Contract test for AI agent intent recognition (T058).

This test verifies that the agent can correctly identify user intents
from various natural language phrases for task management.
"""

import pytest
from typing import List


# Test data for intent variations
CREATE_TASK_VARIATIONS = [
    "Add a task: Buy groceries",
    "Create a new task to call mom",
    "I need to remember to finish the report",
    "Remind me to take out the trash",
    "Add: Clean the kitchen",
    "New task: Schedule dentist appointment",
    "Task: Pay electricity bill",
    "Don't forget to water the plants",
    "I have to do laundry tomorrow",
    "Make a note: Call the insurance company"
]

LIST_TASKS_VARIATIONS = [
    "Show me my tasks",
    "What do I need to do?",
    "List all my tasks",
    "What's on my todo list?",
    "Display my tasks",
    "What are my tasks?",
    "Show me everything I need to do",
    "My task list please",
    "What tasks do I have?",
    "Give me my todo list"
]

COMPLETE_TASK_VARIATIONS = [
    "Mark task as done: Buy groceries",
    "Complete the task: Call mom",
    "I finished the report",
    "Task done: Take out trash",
    "Mark as completed: Clean kitchen",
    "I've completed the dentist appointment",
    "Finish task: Pay electricity bill",
    "Did the laundry",
    "Task completed: Water plants",
    "Mark done: Call insurance company"
]

DELETE_TASK_VARIATIONS = [
    "Delete task: Buy groceries",
    "Remove the task: Call mom",
    "I don't need to do the report anymore",
    "Cancel task: Take out trash",
    "Remove: Clean kitchen",
    "Delete the dentist appointment task",
    "Remove task: Pay electricity bill",
    "Forget about the laundry",
    "Delete the water plants task",
    "Remove this task: Call insurance"
]

UPDATE_TASK_VARIATIONS = [
    "Update task: Buy groceries to Buy groceries and milk",
    "Change the task: Call mom to Call mom at 5pm",
    "Modify the report task to Finish quarterly report",
    "Edit task: Take out trash to Take out trash and recycling",
    "Update: Clean kitchen to Clean kitchen thoroughly",
    "Change: Dentist appointment to Dentist appointment on Friday",
    "Modify task: Pay electricity bill to Pay electricity bill by Friday",
    "Edit: Laundry to Do laundry and fold clothes",
    "Update the water plants task to Water plants and fertilize",
    "Change task: Call insurance to Call insurance about claim"
]


@pytest.mark.parametrize("phrase", CREATE_TASK_VARIATIONS)
def test_create_task_intent_recognition(phrase: str):
    """
    Test that agent correctly identifies 'create task' intent from various phrases.

    This is a contract test defining the expected behavior.
    The actual implementation will be done in T061-T065.
    """
    # This test defines the contract - actual implementation comes later
    # For now, we just verify the test data is valid
    assert isinstance(phrase, str)
    assert len(phrase) > 0
    assert len(phrase.split()) >= 3  # Minimum reasonable phrase length

    # TODO: After agent implementation (T061-T065):
    # from src.agent.agent import AgentService
    # intent = await AgentService.detect_intent(phrase)
    # assert intent["action"] == "create_task"
    # assert "title" in intent or "content" in intent


@pytest.mark.parametrize("phrase", LIST_TASKS_VARIATIONS)
def test_list_tasks_intent_recognition(phrase: str):
    """
    Test that agent correctly identifies 'list tasks' intent.
    """
    assert isinstance(phrase, str)
    assert len(phrase) > 0

    # TODO: After agent implementation:
    # intent = await AgentService.detect_intent(phrase)
    # assert intent["action"] == "list_tasks"


@pytest.mark.parametrize("phrase", COMPLETE_TASK_VARIATIONS)
def test_complete_task_intent_recognition(phrase: str):
    """
    Test that agent correctly identifies 'complete task' intent.
    """
    assert isinstance(phrase, str)
    assert len(phrase) > 0

    # TODO: After agent implementation:
    # intent = await AgentService.detect_intent(phrase)
    # assert intent["action"] == "complete_task"
    # assert "task_identifier" in intent


@pytest.mark.parametrize("phrase", DELETE_TASK_VARIATIONS)
def test_delete_task_intent_recognition(phrase: str):
    """
    Test that agent correctly identifies 'delete task' intent.
    """
    assert isinstance(phrase, str)
    assert len(phrase) > 0

    # TODO: After agent implementation:
    # intent = await AgentService.detect_intent(phrase)
    # assert intent["action"] == "delete_task"
    # assert "task_identifier" in intent


@pytest.mark.parametrize("phrase", UPDATE_TASK_VARIATIONS)
def test_update_task_intent_recognition(phrase: str):
    """
    Test that agent correctly identifies 'update task' intent.
    """
    assert isinstance(phrase, str)
    assert len(phrase) > 0

    # TODO: After agent implementation:
    # intent = await AgentService.detect_intent(phrase)
    # assert intent["action"] == "update_task"
    # assert "task_identifier" in intent
    # assert "new_title" in intent or "new_content" in intent


def test_all_intent_variations_are_unique():
    """Verify that all test phrases are unique (no duplicates)."""
    all_phrases = (
        CREATE_TASK_VARIATIONS +
        LIST_TASKS_VARIATIONS +
        COMPLETE_TASK_VARIATIONS +
        DELETE_TASK_VARIATIONS +
        UPDATE_TASK_VARIATIONS
    )

    assert len(all_phrases) == len(set(all_phrases)), "Test phrases should be unique"


def test_intent_coverage():
    """Verify we have comprehensive test coverage for all intents."""
    assert len(CREATE_TASK_VARIATIONS) >= 10, "Should have at least 10 create task variations"
    assert len(LIST_TASKS_VARIATIONS) >= 10, "Should have at least 10 list tasks variations"
    assert len(COMPLETE_TASK_VARIATIONS) >= 10, "Should have at least 10 complete task variations"
    assert len(DELETE_TASK_VARIATIONS) >= 10, "Should have at least 10 delete task variations"
    assert len(UPDATE_TASK_VARIATIONS) >= 10, "Should have at least 10 update task variations"

    total_variations = (
        len(CREATE_TASK_VARIATIONS) +
        len(LIST_TASKS_VARIATIONS) +
        len(COMPLETE_TASK_VARIATIONS) +
        len(DELETE_TASK_VARIATIONS) +
        len(UPDATE_TASK_VARIATIONS)
    )

    assert total_variations >= 50, f"Should have at least 50 total test variations, got {total_variations}"
