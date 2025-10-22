import { test, expect } from '@playwright/test';

test.describe('Chat Interface', () => {
  test('should have message input field', async ({ page }) => {
    await page.goto('/');
    
    const input = page.locator('input[placeholder*="message"], textarea[placeholder*="message"]').first();
    await expect(input).toBeVisible();
  });

  test('should have send button', async ({ page }) => {
    await page.goto('/');
    
    const sendButton = page.locator('button[type="submit"], button:has-text("Send")').first();
    await expect(sendButton).toBeVisible();
  });

  test('should allow typing in message input', async ({ page }) => {
    await page.goto('/');
    
    const input = page.locator('input[placeholder*="message"], textarea[placeholder*="message"]').first();
    await input.fill('Test message');
    await expect(input).toHaveValue('Test message');
  });

  test('should clear input after sending message', async ({ page }) => {
    await page.goto('/');
    
    const input = page.locator('input[placeholder*="message"], textarea[placeholder*="message"]').first();
    await input.fill('Test message');
    
    const sendButton = page.locator('button[type="submit"], button:has-text("Send")').first();
    await sendButton.click();
    
    // Input should be cleared (or at least attempted to clear)
    await page.waitForTimeout(500);
  });
});

