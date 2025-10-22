import { test, expect } from '@playwright/test';

test.describe('Application', () => {
  test('should load homepage', async ({ page }) => {
    await page.goto('/');
    await expect(page).toHaveTitle(/Foundational/i);
  });

  test('should have upload functionality visible', async ({ page }) => {
    await page.goto('/');
    const uploadButton = page.locator('text=/upload/i').first();
    await expect(uploadButton).toBeVisible();
  });

  test('should display sidebar', async ({ page }) => {
    await page.goto('/');
    // Check for sidebar elements
    await expect(page.locator('[role="complementary"]').first()).toBeVisible();
  });

  test('should have chat interface', async ({ page }) => {
    await page.goto('/');
    // Check for message input
    const messageInput = page.locator('input[type="text"], textarea').first();
    await expect(messageInput).toBeVisible();
  });
});

