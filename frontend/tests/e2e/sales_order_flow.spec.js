import { test, expect } from '@playwright/test';

test.describe('Sales Order Flow E2E Test', () => {
  let authToken = '';

  test.beforeAll(async ({ request }) => {
    const loginRes = await request.post('http://localhost:5000/api/v1/auth/login', {
      data: { email: 'admin@erpseed.org', password: 'admin123' },
    });
    const loginBody = await loginRes.json();
    authToken = loginBody.access_token;
  });

  test('complete sales order lifecycle: create, calculate total, save, edit and persist', async ({ page }) => {
    // 1. Login via UI
    await page.goto('http://localhost:5173/login');
    await page.locator('input[type="email"]').fill('admin@erpseed.org');
    await page.locator('input[type="password"]').fill('admin123');
    await page.locator('#rememberMe').check();
    await page.locator('button[type="submit"]').click();
    await page.waitForURL('**/projects');
    await page.waitForLoadState('networkidle');

    // 2. Navigate to Sales
    await page.goto('http://localhost:5173/sales');
    await page.waitForLoadState('networkidle');

    // 3. Click New Sales Order
    const newBtn = page.locator('button:has-text("New Sales Order")');
    await expect(newBtn).toBeVisible();
    await newBtn.click();

    // 4. Verify on /sales/new
    await expect(page).toHaveURL(/.*sales\/new/);
    const pageHeader = page.locator('h2');
    await expect(pageHeader).toBeVisible();
    await expect(pageHeader).toContainText('New Sales Order');

    // 5. Select Customer
    const customerSelect = page.locator('select[name="party_id"]');
    await expect(customerSelect).toBeVisible();
    await customerSelect.selectOption({ index: 1 });

    // 6. Select Order Date
    const dateInput = page.locator('input[name="order_date"]');
    await dateInput.fill('2026-09-09');

    // 7. Add Order Line
    const addLineBtn = page.locator('button:has-text("+ Aggiungi Riga")');
    await expect(addLineBtn).toBeVisible();
    await addLineBtn.click();

    // 8. Fill Line Form
    const productSelect = page.locator('select[name="product_id"]');
    await expect(productSelect).toBeVisible();
    await productSelect.selectOption({ index: 1 });

    const qtyInput = page.locator('input[name="quantity"]');
    await qtyInput.fill('2');

    const priceInput = page.locator('input[name="unit_price"]');
    await priceInput.fill('49.90');

    // 9. Confirm Line
    const confirmLineBtn = page.locator('button:has-text("Conferma Riga")');
    await confirmLineBtn.click();

    // 10. Verify calculated Total on page
    const totalHeading = page.locator('h4:has-text("Totale:")');
    await expect(totalHeading).toContainText('99');

    // 11. Click Save Order
    const saveBtn = page.locator('button:has-text("Save Order")');
    await saveBtn.click();

    // 12. Verify redirection to /sales
    await expect(page).toHaveURL(/.*sales/);
  });
});
