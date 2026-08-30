"""
End-to-end integration test for NOHA core architecture.

Tests the complete pipeline:
POST /command
    ↓
bridge/api/routes.py
    ↓
process_command()
    ↓
RuntimeBuilder().build()
    ↓
RuntimeEngine
    ↓
Brain.process()
    ↓
Intent Classification
    ↓
Planning
    ↓
Execution
    ↓
Reflection
    ↓
Structured response through the API boundary
"""

import asyncio
import json
import sys
from pathlib import Path

# Test via direct runtime service (bypasses HTTP layer but tests full pipeline)
from bridge.services.runtime_service import process_command

# Also test via HTTP if server is available
import httpx


async def test_direct_pipeline():
    """Test the full pipeline through the runtime service."""
    print("=" * 60)
    print("END-TO-END TEST: Direct Runtime Service")
    print("=" * 60)

    test_command = (
        "Create a folder called e2e_test and generate a Python hello world "
        "program in a file called hello.py inside it"
    )

    print(f"\nCommand: {test_command}")

    result = await process_command(test_command)

    print(f"\nResult: {result}")

    # Verify the result structure
    assert hasattr(result, 'status'), "Missing status field"
    assert hasattr(result, 'execution'), "Missing execution field"
    assert result.execution is not None, "Execution result is None"
    assert result.execution.success is True, "Execution failed"
    assert result.execution.completed_tasks > 0, "No tasks completed"

    # Verify file was created
    workspace = Path("workspace")
    hello_file = workspace / "e2e_test" / "hello.py"
    assert hello_file.exists(), f"Expected file not found: {hello_file}"

    content = hello_file.read_text()
    print(f"\nGenerated file content:\n{content}")

    # Verify Python syntax
    compile(content, "hello.py", "exec")
    print("\n[OK] Generated Python code is syntactically valid")

    # Verify sandbox - file should be in workspace only
    resolved = hello_file.resolve()
    workspace_resolved = workspace.resolve()
    assert resolved.is_relative_to(workspace_resolved), "File escaped workspace!"
    print("[OK] Filesystem sandbox enforced")

    print("\n" + "=" * 60)
    print("DIRECT PIPELINE TEST PASSED")
    print("=" * 60)
    return True


async def test_http_pipeline():
    """Test the full pipeline through the FastAPI HTTP endpoint."""
    print("=" * 60)
    print("END-TO-END TEST: HTTP API Endpoint")
    print("=" * 60)

    test_command = (
        "Create a folder called e2e_http_test and generate a Python function "
        "that adds two numbers in a file called math.py inside it"
    )

    print(f"\nCommand: {test_command}")

    async with httpx.AsyncClient(timeout=120.0) as client:
        response = await client.post(
            "http://127.0.0.1:8000/command",
            json={"command": test_command}
        )

    print(f"HTTP Status: {response.status_code}")
    assert response.status_code == 200, f"Expected 200, got {response.status_code}"

    data = response.json()
    print(f"Response: {json.dumps(data, indent=2)}")

    # Verify response structure
    assert data.get("status") == "success", "Response status not success"
    assert data.get("should_retry") is False, "Should not retry"
    assert "execution" in data, "Missing execution in response"
    assert data["execution"]["success"] is True, "Execution failed in response"
    assert data["execution"]["completed_tasks"] > 0, "No tasks completed"

    # Verify file was created
    workspace = Path("workspace")
    math_file = workspace / "e2e_http_test" / "math.py"
    assert math_file.exists(), f"Expected file not found: {math_file}"

    content = math_file.read_text()
    print(f"\nGenerated file content:\n{content}")

    # Verify Python syntax
    compile(content, "math.py", "exec")
    print("\n[OK] Generated Python code is syntactically valid")

    # Verify sandbox
    resolved = math_file.resolve()
    workspace_resolved = workspace.resolve()
    assert resolved.is_relative_to(workspace_resolved), "File escaped workspace!"
    print("[OK] Filesystem sandbox enforced")

    print("\n" + "=" * 60)
    print("HTTP PIPELINE TEST PASSED")
    print("=" * 60)
    return True


async def test_task_output_resolution():
    """Test $TASK_N_OUTPUT and $TASK_N_OUTPUT.field resolution."""
    print("=" * 60)
    print("END-TO-END TEST: Task Output Reference Resolution")
    print("=" * 60)

    # This command should generate code and write it using $TASK_N_OUTPUT.code
    test_command = (
        "Create a folder called field_res_test and write a Python function "
        "that multiplies two numbers into a file called multiply.py inside it"
    )

    print(f"\nCommand: {test_command}")

    result = await process_command(test_command)

    print(f"\nResult: {result}")
    assert result.execution.success is True, "Execution failed"
    assert result.execution.completed_tasks == 4, f"Expected 4 tasks, got {result.execution.completed_tasks}"

    # Verify file was created with correct content
    workspace = Path("workspace")
    multiply_file = workspace / "field_res_test" / "multiply.py"
    assert multiply_file.exists(), f"Expected file not found: {multiply_file}"

    content = multiply_file.read_text()
    print(f"\nGenerated file content:\n{content}")

    # The content should be the code, not the full result object
    assert "def " in content or "lambda" in content, "Code not written to file"
    assert "status" not in content, "Full result object written instead of code field"
    print("[OK] $TASK_N_OUTPUT.field resolution works correctly")

    print("\n" + "=" * 60)
    print("TASK OUTPUT RESOLUTION TEST PASSED")
    print("=" * 60)
    return True


async def test_multiple_tools():
    """Test a command that uses multiple different tools."""
    print("=" * 60)
    print("END-TO-END TEST: Multiple Tools Pipeline")
    print("=" * 60)

    test_command = (
        "Create a folder called multi_tool, then create a file called "
        "notes.txt inside it with the content 'Hello from NOHA'"
    )

    print(f"\nCommand: {test_command}")

    result = await process_command(test_command)

    print(f"\nResult: {result}")
    assert result.execution.success is True, "Execution failed"

    workspace = Path("workspace")
    notes_file = workspace / "multi_tool" / "notes.txt"
    assert notes_file.exists(), f"Expected file not found: {notes_file}"

    content = notes_file.read_text()
    print(f"\nFile content: {content}")
    assert content == "Hello from NOHA", "File content mismatch"

    print("\n" + "=" * 60)
    print("MULTIPLE TOOLS TEST PASSED")
    print("=" * 60)
    return True


async def main():
    """Run all end-to-end tests."""
    print("\n" + "=" * 60)
    print("NOHA CORE ARCHITECTURE - END-TO-END INTEGRATION TESTS")
    print("=" * 60)

    tests = [
        ("Direct Pipeline", test_direct_pipeline),
        ("Task Output Resolution", test_task_output_resolution),
        ("Multiple Tools", test_multiple_tools),
    ]

    # Try HTTP test if server is running
    try:
        async with httpx.AsyncClient(timeout=5.0) as client:
            await client.get("http://127.0.0.1:8000/")
        tests.append(("HTTP Pipeline", test_http_pipeline))
    except Exception:
        print("\n[SKIP] HTTP server not available, skipping HTTP test")

    passed = 0
    failed = 0

    for name, test_func in tests:
        try:
            await test_func()
            passed += 1
        except Exception as e:
            print(f"\n[FAIL] {name}: {e}")
            import traceback
            traceback.print_exc()
            failed += 1

    print("\n" + "=" * 60)
    print(f"SUMMARY: {passed} passed, {failed} failed")
    print("=" * 60)

    return failed == 0


if __name__ == "__main__":
    success = asyncio.run(main())
    sys.exit(0 if success else 1)