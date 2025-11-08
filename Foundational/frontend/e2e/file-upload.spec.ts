import { test, expect } from '@playwright/test';
import path from 'path';

test.describe('File Upload', () => {
  test('should allow file selection', async ({ page }) => {
    await page.goto('/');
    
    // Look for file input
    const fileInput = page.locator('input[type="file"]').first();
    await expect(fileInput).toBeAttached();
  });

  test('should accept PDF files', async ({ page }) => {
    await page.goto('/');
    
    const fileInput = page.locator('input[type="file"]').first();
    const accept = await fileInput.getAttribute('accept');
    expect(accept).toContain('pdf');
  });

  test('should show upload button', async ({ page }) => {
    await page.goto('/');
    
    const uploadButton = page.locator('text=/upload/i').first();
    await expect(uploadButton).toBeVisible();
  });
});

