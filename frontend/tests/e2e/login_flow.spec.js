const { test, expect } = require('@playwright/test');

test.describe('Login Flow', () => {
  test('should show login page and allow entering credentials', async ({ page }) => {
    await page.goto('http://localhost:5173/login');

    // Check for title or specific elements
    await expect(page).toHaveTitle(/ERPSeed/i);

    const emailInput = page.locator('input[type="email"]');
    const passwordInput = page.locator('input[type="password"]');
    const loginButton = page.locator('button[type="submit"]');

    await expect(emailInput).toBeVisible();
    await expect(passwordInput).toBeVisible();
    await expect(loginButton).toBeVisible();

    await emailInput.fill('admin@erpseed.org');
    await passwordInput.fill('admin123');
  });
});
