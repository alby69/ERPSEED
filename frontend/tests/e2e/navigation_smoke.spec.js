import { test, expect } from '@playwright/test';

const ROUTES_TO_TEST = [
  '/login',
  '/projects',
  '/projects/1',
  '/projects/1/members',
  '/projects/1/settings',
  '/projects/1/cashrec',
  '/projects/1/workflows',
  '/projects/1/business-rules',
  '/projects/1/workflow-builder',
  '/dashboard',
  '/dashboard/builder',
  '/builder/blocks',
  '/builder/relationships',
  '/marketplace',
  '/profile',
  '/users',
  '/anagrafiche',
  '/ruoli',
  '/indirizzi',
  '/geografia/comuni',
  '/geografia/nazioni',
  '/geografia/regioni',
  '/geografia/province',
  '/contatti',
  '/products',
  '/products/new',
  '/modules',
  '/test-runner',
  '/sales',
  '/sales/new',
  '/admin/builder',
  '/admin/blocks',
  '/admin/custom-modules',
  '/admin/project-import-export',
  '/admin/bi-builder',
  '/admin/audit-logs',
  '/ai-assistant',
  '/product-categories',
  '/tax-rates',
  '/units-of-measure',
  '/price-lists',
  '/chart-of-accounts',
  '/purchase-orders',
  '/purchase-requests',
  '/goods-receipts',
  '/purchase-returns',
  '/quotations',
  '/delivery-notes',
  '/invoices',
  '/sales-returns',
  '/crm',
  '/contracts',
  '/stock-levels',
  '/stock-movements',
  '/inventory-counts',
  '/lots',
  '/journal',
  '/maturities',
  '/trial-balance',
  '/vat-registers',
  '/intrastat',
  '/riba',
  '/production',
  '/mrp',
  '/employees',
  '/departments',
  '/attendance',
  '/leave-requests',
  '/project-management',
  '/timesheet',
  '/project-budgets',
  '/logistics/distances',
  '/reports',
];

test.describe('Navigation Smoke Tests', () => {
  let authToken = '';
  let userData = null;

  test.beforeAll(async ({ request }) => {
    // Authenticate via API to get token
    const loginRes = await request.post('http://127.0.0.1:5000/api/v1/auth/login', {
      data: {
        email: 'admin@erpseed.org',
        password: 'admin123',
      },
    });
    if (loginRes.ok()) {
      const body = await loginRes.json();
      authToken = body.access_token;
      userData = body.user;
    }

    // Ensure project 1 exists for project-nested routes
    await request.post('http://127.0.0.1:5000/api/v1/projects', {
      headers: { Authorization: `Bearer ${authToken}` },
      data: { name: 'smoke_test_project', title: 'Smoke Test Project' },
    });
  });

  for (const route of ROUTES_TO_TEST) {
    test(`should load route ${route} without uncaught errors`, async ({ page }) => {
      const consoleErrors = [];
      page.on('console', (msg) => {
        if (msg.type() === 'error') {
          consoleErrors.push(msg.text());
        }
      });

      // Set authentication in localStorage before navigating
      await page.goto('http://127.0.0.1:5173/login');
      if (authToken && route !== '/login') {
        await page.evaluate(({ token, user }) => {
          localStorage.setItem('access_token', token);
          localStorage.setItem('user', JSON.stringify(user));
        }, { token: authToken, user: userData });
      }

      const response = await page.goto(`http://127.0.0.1:5173${route}`);
      expect(response.status()).toBeLessThan(400);

      // Verify page container is loaded and no error boundary
      await expect(page.locator('#root')).toBeVisible();

      // Check no uncaught react runtime errors
      const pageText = await page.textContent('body');
      expect(pageText).not.toContain('Something went wrong');

      // Filter out non-fatal console warnings/notices
      const criticalErrors = consoleErrors.filter(
        err => !err.includes('Failed to load resource') &&
               !err.includes('404') &&
               !err.includes('antd: Spin') &&
               !err.includes('CORS policy') &&
               !err.includes('Failed to fetch')
      );
      expect(criticalErrors).toEqual([]);
    });
  }
});
