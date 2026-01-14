# Chunk Merge Playwright Tests

This directory contains automated tests for the chunk merge functionality using Playwright.

## Prerequisites

1. **Python 3.8+** installed
2. **Backend server running** on `http://localhost:8000`
3. **Playwright** installed and configured

## Installation

1. Install Python dependencies:
```bash
pip install playwright pytest-playwright pytest-asyncio
```

2. Install Playwright browsers:
```bash
playwright install chromium
```

## Running the Tests

### Start the Backend Server

Before running the tests, make sure the backend server is running:

```bash
uvicorn src.aitechpioneer.interfaces.api:app --host 0.0.0.0 --port 8000 --reload
```

### Run All Tests

```bash
python tests/test_chunk_merge_playwright.py
```

### Run Individual Tests

You can modify the `run_all_tests` method in the test file to run specific tests only.

## Test Cases

The test suite includes the following test cases:

| Test ID | Test Name | Description |
|---------|-----------|-------------|
| TC001 | Load Chunks List | Verifies that the chunk list loads correctly and displays all required information |
| TC002 | Merge Two Chunks | Tests the basic chunk merge functionality using the merge button |
| TC003 | Merge Forward | Tests merging a chunk with the next chunk (forward merge) |
| TC004 | Merge Backward | Tests merging a chunk with the previous chunk (backward merge) |
| TC005 | Undo Merge | Tests undoing a chunk merge operation |
| TC006 | View Chunk History | Tests retrieving and displaying chunk version history |
| TC013 | Multi-level Undo Merge | Tests undoing multiple levels of chunk merges |
| TC020 | Merge, Undo, Merge Again | Regression test for merging, undoing, and merging again |

## Test Data Requirements

The tests require the following data in the database:

- At least 3 chunks for basic merge tests
- Chunks with different statuses (active, deprecated, inactive)
- Chunks with different types (parent, child)

## Test Output

The tests will output detailed logs including:

- Test execution progress
- Success/failure status for each test
- Detailed error messages if a test fails
- Summary of test results at the end

## Troubleshooting

### Backend Server Not Running

If you see connection errors, make sure the backend server is running on `http://localhost:8000`.

### No Chunks Found

If tests fail because no chunks are found, make sure the database has test data. You can create test data using the migration script:

```bash
python scripts/migrate_chunk_versions.py
```

### Browser Issues

If you encounter browser-related issues, try reinstalling Playwright browsers:

```bash
playwright install --force chromium
```

### Timeout Errors

If tests timeout, you may need to increase the timeout values in the test file. Look for `timeout` parameters in the test methods.

## Test Coverage

The current test suite covers:

- ✅ Chunk list loading
- ✅ Basic chunk merge (select and merge)
- ✅ Forward merge (with next chunk)
- ✅ Backward merge (with previous chunk)
- ✅ Undo merge operation
- ✅ Chunk history retrieval
- ✅ Multi-level undo
- ✅ Regression scenarios

### Not Yet Covered

- ❌ Smart recommendation feature
- ❌ Status filtering
- ❌ Type filtering
- ❌ Quick locate by document ID
- ❌ Update chunk status
- ❌ Delete chunk
- ❌ Boundary conditions (selecting more than 2 chunks)
- ❌ Error handling (merging non-existent chunks)
- ❌ Performance testing

## Extending the Tests

To add new test cases:

1. Create a new test method in the `ChunkMergeTest` class
2. Add the test to the `tests` list in the `run_all_tests` method
3. Follow the existing test structure and naming conventions

Example:

```python
async def test_tc021_custom_test(self):
    logger.info("=" * 80)
    logger.info("Running TC021: Custom Test")
    logger.info("=" * 80)
    
    # Your test logic here
    
    logger.info("TC021: PASSED - Custom test successful")
    return True
```

## Running Tests in Headless Mode

By default, tests run with a visible browser (`headless=False`). To run in headless mode, modify the `setup` method in the test file:

```python
self.browser = await self.playwright.chromium.launch(
    headless=True,  # Change to True
    slow_mo=1000,
)
```

## CI/CD Integration

These tests can be integrated into a CI/CD pipeline:

1. Start the backend server
2. Run the Playwright tests
3. Check the exit code (0 for success, non-zero for failure)

Example GitHub Actions workflow:

```yaml
name: Chunk Merge Tests

on: [push, pull_request]

jobs:
  test:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v2
      - name: Set up Python
        uses: actions/setup-python@v2
        with:
          python-version: '3.9'
      - name: Install dependencies
        run: |
          pip install playwright pytest-playwright pytest-asyncio
          playwright install chromium
      - name: Start backend
        run: uvicorn src.aitechpioneer.interfaces.api:app --host 0.0.0.0 --port 8000 &
      - name: Run tests
        run: python tests/test_chunk_merge_playwright.py
```

## License

These tests are part of the AI Tech Pioneer project.
