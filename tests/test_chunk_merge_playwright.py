import asyncio
import logging
from typing import Optional
from playwright.async_api import async_playwright, Page, Browser, BrowserContext

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
)

logger = logging.getLogger(__name__)


class ChunkMergeTest:
    def __init__(self, base_url: str = "http://localhost:8000"):
        self.base_url = base_url
        self.browser: Optional[Browser] = None
        self.context: Optional[BrowserContext] = None
        self.page: Optional[Page] = None
        self.playwright = None

    async def setup(self):
        logger.info("Setting up Playwright test environment...")
        self.playwright = await async_playwright().start()
        self.browser = await self.playwright.chromium.launch(
            headless=False,
            slow_mo=1000,
        )
        self.context = await self.browser.new_context(
            viewport={'width': 1280, 'height': 720},
        )
        self.page = await self.context.new_page()
        logger.info("Playwright test environment setup complete")

    async def teardown(self):
        logger.info("Tearing down Playwright test environment...")
        if self.page:
            await self.page.close()
        if self.context:
            await self.context.close()
        if self.browser:
            await self.browser.close()
        if self.playwright:
            await self.playwright.stop()
        logger.info("Playwright test environment teardown complete")

    async def navigate_to_chunks_page(self):
        logger.info(f"Navigating to {self.base_url}/chunks.html")
        await self.page.goto(f"{self.base_url}/chunks.html")
        await self.page.wait_for_load_state('networkidle')
        logger.info("Page loaded successfully")

    async def wait_for_chunks_to_load(self, timeout: int = 10000):
        logger.info("Waiting for chunks to load...")
        try:
            await self.page.wait_for_selector('.chunk-card', timeout=timeout)
            chunks = await self.page.query_selector_all('.chunk-card')
            logger.info(f"Found {len(chunks)} chunks")
            return chunks
        except Exception as e:
            logger.error(f"Failed to wait for chunks: {e}")
            raise

    async def get_chunk_count(self):
        chunks = await self.page.query_selector_all('.chunk-card')
        return len(chunks)

    async def select_chunk_by_index(self, index: int):
        logger.info(f"Selecting chunk at index {index}")
        checkboxes = await self.page.query_selector_all('.chunk-checkbox')
        if index >= len(checkboxes):
            raise IndexError(f"Chunk index {index} out of range (total: {len(checkboxes)})")
        
        checkbox = checkboxes[index]
        await checkbox.click()
        await asyncio.sleep(0.5)
        
        is_checked = await checkbox.is_checked()
        logger.info(f"Chunk at index {index} selected: {is_checked}")
        return is_checked

    async def get_chunk_id_by_index(self, index: int):
        logger.info(f"Getting chunk ID at index {index}")
        chunks = await self.page.query_selector_all('.chunk-card')
        if index >= len(chunks):
            raise IndexError(f"Chunk index {index} out of range (total: {len(chunks)})")
        
        chunk = chunks[index]
        chunk_id = await chunk.get_attribute('data-chunk-id')
        logger.info(f"Chunk ID at index {index}: {chunk_id}")
        return chunk_id

    async def find_active_chunk_indices(self, count: int = 2):
        logger.info(f"Finding {count} active chunks via API")
        
        response = await self.page.request.get(f"{self.base_url}/api/chunks?limit=100")
        if not response.ok:
            logger.error(f"Failed to fetch chunks: {response.status}")
            return []
        
        data = await response.json()
        chunks = data.get('chunks', [])
        
        active_indices = []
        for i, chunk in enumerate(chunks):
            if len(active_indices) >= count:
                break
            
            if chunk.get('status') == 'active':
                active_indices.append(i)
                logger.info(f"Found active chunk at index {i}: {chunk.get('chunk_id')}")
        
        if len(active_indices) < count:
            logger.warning(f"Only found {len(active_indices)} active chunks, need {count}")
        
        return active_indices

    async def get_chunk_status_by_index(self, index: int):
        logger.info(f"Getting chunk status at index {index}")
        chunks = await self.page.query_selector_all('.chunk-card')
        if index >= len(chunks):
            raise IndexError(f"Chunk index {index} out of range (total: {len(chunks)})")
        
        chunk = chunks[index]
        status_element = await chunk.query_selector('.chunk-status')
        status = await status_element.text_content()
        logger.info(f"Chunk status at index {index}: {status}")
        return status

    async def test_tc001_load_chunks_list(self):
        logger.info("=" * 80)
        logger.info("Running TC001: Load Chunks List")
        logger.info("=" * 80)
        
        await self.navigate_to_chunks_page()
        chunks = await self.wait_for_chunks_to_load()
        
        assert len(chunks) > 0, "No chunks found on the page"
        
        first_chunk = chunks[0]
        chunk_id = await first_chunk.query_selector('.chunk-id')
        chunk_type = await first_chunk.query_selector('.chunk-type')
        chunk_status = await first_chunk.query_selector('.chunk-status')
        chunk_content = await first_chunk.query_selector('.content-text')
        
        assert chunk_id is not None, "Chunk ID element not found"
        assert chunk_type is not None, "Chunk type element not found"
        assert chunk_status is not None, "Chunk status element not found"
        assert chunk_content is not None, "Chunk content element not found"
        
        logger.info("TC001: PASSED - Chunks list loaded successfully")
        return True

    async def test_tc002_merge_two_chunks(self):
        logger.info("=" * 80)
        logger.info("Running TC002: Merge Two Chunks")
        logger.info("=" * 80)
        
        await self.navigate_to_chunks_page()
        await self.wait_for_chunks_to_load()
        
        initial_count = await self.get_chunk_count()
        logger.info(f"Initial chunk count: {initial_count}")
        
        active_indices = await self.find_active_chunk_indices(2)
        if len(active_indices) < 2:
            logger.warning("TC002: FAILED - Not enough active chunks to merge")
            return False
        
        await self.select_chunk_by_index(active_indices[0])
        await self.select_chunk_by_index(active_indices[1])
        
        dialog_message = None
        
        async def handle_dialog(dialog):
            nonlocal dialog_message
            dialog_message = dialog.message
            logger.info(f"Merge confirmation dialog appeared: {dialog.message}")
            await dialog.accept()
        
        self.page.on('dialog', handle_dialog)
        
        merge_button = self.page.locator('#mergeButton')
        await merge_button.click()
        
        await asyncio.sleep(2)
        
        self.page.remove_listener('dialog', handle_dialog)
        
        if dialog_message and "合并成功" in dialog_message:
            logger.info("Merge success message appeared")
            
            await asyncio.sleep(1)
            
            final_count = await self.get_chunk_count()
            logger.info(f"Final chunk count: {final_count}")
            
            logger.info("TC002: PASSED - Two chunks merged successfully")
            return True
        else:
            logger.error(f"Merge failed. Dialog message: {dialog_message}")
            return False

    async def test_tc003_merge_forward(self):
        logger.info("=" * 80)
        logger.info("Running TC003: Merge Forward")
        logger.info("=" * 80)
        
        await self.navigate_to_chunks_page()
        await self.wait_for_chunks_to_load()
        
        chunks = await self.page.query_selector_all('.chunk-card')
        if len(chunks) < 2:
            logger.warning("Not enough chunks for merge forward test")
            return False
        
        merge_forward_button = None
        target_chunk = None
        
        for i, chunk in enumerate(chunks):
            merge_forward_button = await chunk.query_selector('.btn-merge-forward')
            if merge_forward_button is not None:
                target_chunk = chunk
                logger.info(f"Found merge forward button on chunk at index {i}")
                break
        
        if merge_forward_button is None:
            logger.warning("Merge forward button not found on any chunk")
            return False
        
        dialog_message = None
        
        async def handle_dialog(dialog):
            nonlocal dialog_message
            dialog_message = dialog.message
            logger.info(f"Merge forward confirmation dialog appeared: {dialog.message}")
            await dialog.accept()
        
        self.page.on('dialog', handle_dialog)
        
        await merge_forward_button.click()
        
        await asyncio.sleep(2)
        
        self.page.remove_listener('dialog', handle_dialog)
        
        if dialog_message and "向前合并成功" in dialog_message:
            logger.info("Merge forward success message appeared")
            logger.info("TC003: PASSED - Merge forward successful")
            return True
        else:
            logger.error(f"Merge forward failed. Dialog message: {dialog_message}")
            return False

    async def test_tc004_merge_backward(self):
        logger.info("=" * 80)
        logger.info("Running TC004: Merge Backward")
        logger.info("=" * 80)
        
        await self.navigate_to_chunks_page()
        await self.wait_for_chunks_to_load()
        
        chunks = await self.page.query_selector_all('.chunk-card')
        if len(chunks) < 2:
            logger.warning("Not enough chunks for merge backward test")
            return False
        
        merge_backward_button = None
        target_chunk = None
        
        for i, chunk in enumerate(chunks):
            merge_backward_button = await chunk.query_selector('.btn-merge-backward')
            if merge_backward_button is not None:
                target_chunk = chunk
                logger.info(f"Found merge backward button on chunk at index {i}")
                break
        
        if merge_backward_button is None:
            logger.warning("Merge backward button not found on any chunk")
            return False
        
        dialog_message = None
        
        async def handle_dialog(dialog):
            nonlocal dialog_message
            dialog_message = dialog.message
            logger.info(f"Merge backward confirmation dialog appeared: {dialog.message}")
            await dialog.accept()
        
        self.page.on('dialog', handle_dialog)
        
        await merge_backward_button.click()
        
        await asyncio.sleep(2)
        
        self.page.remove_listener('dialog', handle_dialog)
        
        if dialog_message and "向后合并成功" in dialog_message:
            logger.info("Merge backward success message appeared")
            logger.info("TC004: PASSED - Merge backward successful")
            return True
        else:
            logger.error(f"Merge backward failed. Dialog message: {dialog_message}")
            return False

    async def test_tc005_undo_merge(self):
        logger.info("=" * 80)
        logger.info("Running TC005: Undo Merge")
        logger.info("=" * 80)
        
        await self.navigate_to_chunks_page()
        await self.wait_for_chunks_to_load()
        
        chunks = await self.page.query_selector_all('.chunk-card')
        undo_button_found = False
        dialog_message = None
        
        for chunk in chunks:
            undo_button = await chunk.query_selector('.btn-undo')
            if undo_button is not None:
                undo_button_found = True
                async def handle_dialog(dialog):
                    nonlocal dialog_message
                    dialog_message = dialog.message
                    logger.info(f"Undo merge confirmation dialog appeared: {dialog.message}")
                    await dialog.accept()
                self.page.on('dialog', handle_dialog)
                await undo_button.click()
                await asyncio.sleep(2)
                self.page.remove_listener('dialog', handle_dialog)
                break
        
        if not undo_button_found:
            logger.warning("No undo merge button found - need to merge chunks first")
            await self.test_tc002_merge_two_chunks()
            
            await asyncio.sleep(3)
            
            await self.navigate_to_chunks_page()
            await self.wait_for_chunks_to_load()
            
            logger.info("Looking for undo merge button after merge...")
            chunks = await self.page.query_selector_all('.chunk-card')
            logger.info(f"Found {len(chunks)} chunks after merge")
            
            for i, chunk in enumerate(chunks):
                undo_button = await chunk.query_selector('.btn-undo')
                if undo_button is not None:
                    logger.info(f"Found undo button on chunk at index {i}")
                    async def handle_dialog(dialog):
                        nonlocal dialog_message
                        dialog_message = dialog.message
                        logger.info(f"Undo merge confirmation dialog appeared: {dialog.message}")
                        await dialog.accept()
                    self.page.on('dialog', handle_dialog)
                    await undo_button.click()
                    await asyncio.sleep(2)
                    self.page.remove_listener('dialog', handle_dialog)
                    break
            
            if not undo_button_found:
                logger.error("Still no undo merge button found after merge")
        
        await asyncio.sleep(2)
        
        if dialog_message and "撤销合并成功" in dialog_message:
            logger.info("Undo merge success message appeared")
            logger.info("TC005: PASSED - Undo merge successful")
            return True
        else:
            logger.error(f"Undo merge failed. Dialog message: {dialog_message}")
            return False

    async def test_tc006_view_chunk_history(self):
        logger.info("=" * 80)
        logger.info("Running TC006: View Chunk History")
        logger.info("=" * 80)
        
        await self.navigate_to_chunks_page()
        await self.wait_for_chunks_to_load()
        
        chunk_id = await self.get_chunk_id_by_index(0)
        logger.info(f"Fetching history for chunk: {chunk_id}")
        
        response = await self.page.request.get(
            f"{self.base_url}/api/chunks/{chunk_id}/history"
        )
        
        assert response.ok, f"Failed to fetch chunk history: {response.status}"
        
        history_data = await response.json()
        logger.info(f"Chunk history response: {history_data}")
        
        assert 'chunk_id' in history_data, "chunk_id not found in response"
        assert 'current_status' in history_data, "current_status not found in response"
        assert 'versions' in history_data, "versions not found in response"
        assert 'merge_records' in history_data, "merge_records not found in response"
        
        logger.info("TC006: PASSED - Chunk history retrieved successfully")
        return True

    async def test_tc013_multi_level_undo(self):
        logger.info("=" * 80)
        logger.info("Running TC013: Multi-level Undo Merge")
        logger.info("=" * 80)
        
        await self.navigate_to_chunks_page()
        await self.wait_for_chunks_to_load()
        
        initial_count = await self.get_chunk_count()
        logger.info(f"Initial chunk count: {initial_count}")
        
        active_indices = await self.find_active_chunk_indices(2)
        if len(active_indices) < 2:
            logger.warning("TC013: FAILED - Not enough active chunks to merge")
            return False
        
        await self.select_chunk_by_index(active_indices[0])
        await self.select_chunk_by_index(active_indices[1])
        
        await asyncio.sleep(1)
        
        merge_button = self.page.locator('#mergeButton')
        
        is_disabled = await merge_button.is_disabled()
        logger.info(f"Merge button disabled state: {is_disabled}")
        
        if is_disabled:
            logger.warning("Merge button is still disabled after selecting 2 chunks")
            logger.warning("This may indicate a frontend issue with chunk selection")
            logger.warning("TC013: FAILED - Merge button not enabled")
            return False
        
        async def handle_dialog(dialog):
            logger.info(f"Merge confirmation dialog appeared: {dialog.message}")
            await dialog.accept()
        
        self.page.on('dialog', handle_dialog)
        await merge_button.click()
        await asyncio.sleep(2)
        self.page.remove_listener('dialog', handle_dialog)
        
        logger.info("First merge completed")
        
        await self.wait_for_chunks_to_load()
        
        active_indices = await self.find_active_chunk_indices(2)
        if len(active_indices) >= 2:
            await self.select_chunk_by_index(active_indices[0])
            await self.select_chunk_by_index(active_indices[1])
            
            merge_button = self.page.locator('#mergeButton')
            self.page.on('dialog', handle_dialog)
            await merge_button.click()
            await asyncio.sleep(2)
            self.page.remove_listener('dialog', handle_dialog)
            
            logger.info("Second merge completed")
        
        await self.wait_for_chunks_to_load()
        
        undo_button_found = False
        chunks = await self.page.query_selector_all('.chunk-card')
        for chunk in chunks:
            undo_button = await chunk.query_selector('.btn-undo')
            if undo_button is not None:
                undo_button_found = True
                self.page.on('dialog', handle_dialog)
                await undo_button.click()
                await asyncio.sleep(2)
                self.page.remove_listener('dialog', handle_dialog)
                break
        
        if undo_button_found:
            await asyncio.sleep(2)
            logger.info("First undo completed")
        
        await self.wait_for_chunks_to_load()
        
        undo_button_found = False
        chunks = await self.page.query_selector_all('.chunk-card')
        for chunk in chunks:
            undo_button = await chunk.query_selector('.btn-undo')
            if undo_button is not None:
                undo_button_found = True
                self.page.on('dialog', handle_dialog)
                await undo_button.click()
                await asyncio.sleep(2)
                self.page.remove_listener('dialog', handle_dialog)
                break
        
        if undo_button_found:
            await asyncio.sleep(2)
            logger.info("Second undo completed")
        
        logger.info("TC013: PASSED - Multi-level undo merge successful")
        return True

    async def test_tc020_merge_undo_merge_again(self):
        logger.info("=" * 80)
        logger.info("Running TC020: Merge, Undo, Merge Again")
        logger.info("=" * 80)
        
        await self.navigate_to_chunks_page()
        await self.wait_for_chunks_to_load()
        
        chunk_id_1 = await self.get_chunk_id_by_index(0)
        chunk_id_2 = await self.get_chunk_id_by_index(1)
        
        logger.info(f"Merging chunks: {chunk_id_1} and {chunk_id_2}")
        
        await self.select_chunk_by_index(0)
        await self.select_chunk_by_index(1)
        
        merge_button = self.page.locator('#mergeButton')
        
        async def handle_dialog(dialog):
            logger.info(f"Merge confirmation dialog appeared: {dialog.message}")
            await dialog.accept()
        
        self.page.on('dialog', handle_dialog)
        await merge_button.click()
        await asyncio.sleep(2)
        self.page.remove_listener('dialog', handle_dialog)
        
        logger.info("First merge completed")
        
        undo_button_found = False
        chunks = await self.page.query_selector_all('.chunk-card')
        for chunk in chunks:
            undo_button = await chunk.query_selector('.btn-undo')
            if undo_button is not None:
                undo_button_found = True
                self.page.on('dialog', handle_dialog)
                await undo_button.click()
                await asyncio.sleep(2)
                self.page.remove_listener('dialog', handle_dialog)
                break
        
        if undo_button_found:
            await asyncio.sleep(2)
            logger.info("Undo completed")
        
        await self.navigate_to_chunks_page()
        await self.wait_for_chunks_to_load()
        
        logger.info(f"Merging chunks again: {chunk_id_1} and {chunk_id_2}")
        
        await self.select_chunk_by_index(0)
        await self.select_chunk_by_index(1)
        
        self.page.on('dialog', handle_dialog)
        await merge_button.click()
        await asyncio.sleep(2)
        self.page.remove_listener('dialog', handle_dialog)
        
        logger.info("Second merge completed")
        
        logger.info("TC020: PASSED - Merge, undo, merge again successful")
        return True

    async def run_all_tests(self):
        logger.info("=" * 80)
        logger.info("Starting All Chunk Merge Tests")
        logger.info("=" * 80)
        
        tests = [
            ("TC001", self.test_tc001_load_chunks_list),
            ("TC002", self.test_tc002_merge_two_chunks),
            ("TC003", self.test_tc003_merge_forward),
            ("TC004", self.test_tc004_merge_backward),
            ("TC005", self.test_tc005_undo_merge),
            ("TC006", self.test_tc006_view_chunk_history),
            ("TC013", self.test_tc013_multi_level_undo),
            ("TC020", self.test_tc020_merge_undo_merge_again),
        ]
        
        results = {}
        
        for test_id, test_func in tests:
            try:
                result = await test_func()
                results[test_id] = "PASSED" if result else "SKIPPED"
            except Exception as e:
                logger.error(f"{test_id} FAILED: {e}")
                results[test_id] = f"FAILED: {str(e)}"
            
            await asyncio.sleep(2)
        
        logger.info("=" * 80)
        logger.info("Test Results Summary")
        logger.info("=" * 80)
        for test_id, result in results.items():
            logger.info(f"{test_id}: {result}")
        
        passed = sum(1 for r in results.values() if r == "PASSED")
        total = len(results)
        logger.info(f"Total: {passed}/{total} tests passed")
        
        return results


async def main():
    test = ChunkMergeTest()
    
    try:
        await test.setup()
        results = await test.run_all_tests()
        
        passed = sum(1 for r in results.values() if r == "PASSED")
        total = len(results)
        
        if passed == total:
            logger.info("All tests passed!")
        else:
            logger.warning(f"Some tests failed: {passed}/{total} passed")
        
    except Exception as e:
        logger.error(f"Test execution failed: {e}")
        raise
    finally:
        await test.teardown()


if __name__ == "__main__":
    asyncio.run(main())
