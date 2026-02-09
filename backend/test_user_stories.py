"""
Simple test script to verify User Stories 2 and 3 functionality.
"""

import asyncio
import os
from uuid import UUID, uuid4
from dotenv import load_dotenv

from sqlalchemy.ext.asyncio import create_async_engine, async_sessionmaker, AsyncSession

from src.services.chat_service import ChatService
from src.services.task_service import TaskService
from src.models.user import User


async def test_user_story_2():
    """Test User Story 2: Conversation Continuity"""
    print("=" * 60)
    print("Testing User Story 2: Conversation Continuity")
    print("=" * 60)

    # Get database URL
    load_dotenv()
    database_url = os.getenv("DATABASE_URL")
    if database_url.startswith("postgresql://"):
        database_url = database_url.replace("postgresql://", "postgresql+asyncpg://", 1)

    # Remove sslmode parameter
    if "sslmode=" in database_url:
        database_url = database_url.split("?")[0]

    # Create engine and session
    engine = create_async_engine(database_url, echo=False)
    async_session_maker = async_sessionmaker(engine, class_=AsyncSession, expire_on_commit=False)

    try:
        async with async_session_maker() as session:
            chat_service = ChatService(session)

            # Create test user
            user_id = uuid4()
            user = User(id=user_id, email=f"user_{user_id.hex[:8]}@example.com")
            session.add(user)
            await session.commit()
            print(f"[OK] Created test user: {user_id}")

            # Test 1: Create conversation
            result = await chat_service.create_conversation(user_id=user_id)
            conversation_id = UUID(result["conversation_id"])
            print(f"[OK] Created conversation: {conversation_id}")

            # Test 2: Save messages
            await chat_service.save_message(
                conversation_id=conversation_id,
                role="user",
                content="Add a task: Buy groceries"
            )
            await chat_service.save_message(
                conversation_id=conversation_id,
                role="assistant",
                content="I've added the task 'Buy groceries' to your list"
            )
            print("[OK] Saved 2 messages")

            # Test 3: Retrieve history
            history = await chat_service.get_conversation_history(
                conversation_id=conversation_id,
                user_id=user_id
            )
            print(f"[OK] Retrieved history with {len(history)} messages")
            assert len(history) == 2
            assert history[0]["role"] == "user"
            assert history[1]["role"] == "assistant"

            print("\n[PASS] User Story 2 PASSED!\n")

    except Exception as e:
        print(f"\n[FAIL] User Story 2 FAILED: {e}\n")
        raise

    finally:
        await engine.dispose()


async def test_user_story_3():
    """Test User Story 3: Multi-User Isolation"""
    print("=" * 60)
    print("Testing User Story 3: Multi-User Task Isolation")
    print("=" * 60)

    load_dotenv()
    database_url = os.getenv("DATABASE_URL")
    if database_url.startswith("postgresql://"):
        database_url = database_url.replace("postgresql://", "postgresql+asyncpg://", 1)

    if "sslmode=" in database_url:
        database_url = database_url.split("?")[0]

    engine = create_async_engine(database_url, echo=False)
    async_session_maker = async_sessionmaker(engine, class_=AsyncSession, expire_on_commit=False)

    try:
        async with async_session_maker() as session:
            task_service = TaskService(session)

            # Create test users
            user1_id = uuid4()
            user2_id = uuid4()

            user1 = User(id=user1_id, email=f"user1_{user1_id.hex[:8]}@example.com")
            user2 = User(id=user2_id, email=f"user2_{user2_id.hex[:8]}@example.com")
            session.add(user1)
            session.add(user2)
            await session.commit()
            print(f"[OK] Created 2 test users")

            # Test 1: User 1 creates tasks
            task1 = await task_service.create_task(user_id=user1_id, title="User 1 - Task A")
            task2 = await task_service.create_task(user_id=user1_id, title="User 1 - Task B")
            print(f"[OK] User 1 created 2 tasks")

            # Test 2: User 2 creates tasks
            task3 = await task_service.create_task(user_id=user2_id, title="User 2 - Task X")
            task4 = await task_service.create_task(user_id=user2_id, title="User 2 - Task Y")
            print(f"[OK] User 2 created 2 tasks")

            # Test 3: User 1 retrieves their tasks
            user1_tasks = await task_service.list_tasks(user_id=user1_id)
            print(f"[OK] User 1 retrieved {len(user1_tasks)} tasks")
            assert len(user1_tasks) == 2
            assert all(task["user_id"] == str(user1_id) for task in user1_tasks)

            # Test 4: User 2 retrieves their tasks
            user2_tasks = await task_service.list_tasks(user_id=user2_id)
            print(f"[OK] User 2 retrieved {len(user2_tasks)} tasks")
            assert len(user2_tasks) == 2
            assert all(task["user_id"] == str(user2_id) for task in user2_tasks)

            # Test 5: User 2 tries to access User 1's task
            result = await task_service.get_task(task_id=UUID(task1["task_id"]), user_id=user2_id)
            assert result is None
            print("[OK] User 2 cannot access User 1's tasks")

            # Test 6: User 1 can complete their own task
            result = await task_service.complete_task(task_id=UUID(task1["task_id"]), user_id=user1_id)
            assert result is not None
            assert result["completed"] is True
            print("[OK] User 1 completed their own task")

            # Test 7: User 2 cannot complete User 1's task
            result = await task_service.complete_task(task_id=UUID(task2["task_id"]), user_id=user2_id)
            assert result is None
            print("[OK] User 2 cannot complete User 1's task")

            print("\n[PASS] User Story 3 PASSED!\n")

    except Exception as e:
        print(f"\n[FAIL] User Story 3 FAILED: {e}\n")
        raise

    finally:
        await engine.dispose()


async def main():
    """Run all user story tests"""
    print("\n" + "=" * 60)
    print("RUNNING USER STORY TESTS")
    print("=" * 60 + "\n")

    try:
        await test_user_story_2()
        await test_user_story_3()

        print("=" * 60)
        print("[SUCCESS] ALL USER STORY TESTS PASSED!")
        print("=" * 60)
        print("\n[PASS] User Story 2: Conversation Continuity - WORKING")
        print("[PASS] User Story 3: Multi-User Isolation - WORKING")
        print("\nAll implementations are functioning correctly!\n")

    except Exception as e:
        print("=" * 60)
        print("TESTS FAILED")
        print("=" * 60)
        print(f"Error: {e}")
        import traceback
        traceback.print_exc()


if __name__ == "__main__":
    asyncio.run(main())
