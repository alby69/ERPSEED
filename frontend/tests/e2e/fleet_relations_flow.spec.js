import { test, expect } from '@playwright/test';

test.describe('Fleet Scenario E2E Test (No-Code Builder + Relations)', () => {
  let authToken = '';
  let userData = null;
  let projectId = null;
  let vehicleModelId = null;
  let maintenanceModelId = null;

  test.beforeAll(async ({ request }) => {
    // 1. Authenticate via API
    const loginRes = await request.post('http://127.0.0.1:5000/api/v1/auth/login', {
      data: {
        email: 'admin@erpseed.org',
        password: 'admin123',
      },
    });
    expect(loginRes.ok()).toBeTruthy();
    const loginBody = await loginRes.json();
    authToken = loginBody.access_token;
    userData = loginBody.user;

    const headers = {
      Authorization: `Bearer ${authToken}`,
      'Content-Type': 'application/json',
    };

    // 2. Create Fleet Project
    const projectRes = await request.post('http://127.0.0.1:5000/api/v1/projects', {
      headers,
      data: {
        name: `fleet_e2e_${Date.now()}`,
        title: 'Fleet E2E Management',
        description: 'Test project for relational builder',
      },
    });
    expect(projectRes.ok()).toBeTruthy();
    const project = await projectRes.json();
    projectId = project.id;

    // 3. Create Vehicle Model
    const vehicleRes = await request.post('http://127.0.0.1:5000/api/v1/sys-models', {
      headers,
      data: { projectId, name: 'vehicle', title: 'Vehicle' },
    });
    expect(vehicleRes.ok()).toBeTruthy();
    const vehicleModel = await vehicleRes.json();
    vehicleModelId = vehicleModel.id;

    // Vehicle fields
    await request.post('http://127.0.0.1:5000/api/v1/sys-fields', {
      headers,
      data: { modelId: vehicleModelId, name: 'plate', type: 'string', required: true, is_unique: true },
    });
    await request.post('http://127.0.0.1:5000/api/v1/sys-fields', {
      headers,
      data: { modelId: vehicleModelId, name: 'brand', type: 'select', options: JSON.stringify(['Ford', 'Fiat', 'Tesla']) },
    });
    await request.post('http://127.0.0.1:5000/api/v1/sys-fields', {
      headers,
      data: { modelId: vehicleModelId, name: 'model', type: 'string', required: true },
    });

    await request.post(`http://127.0.0.1:5000/api/v1/sys-models/${vehicleModelId}/generate-table`, { headers });

    // 4. Create Maintenance Model
    const maintenanceRes = await request.post('http://127.0.0.1:5000/api/v1/sys-models', {
      headers,
      data: { projectId, name: 'maintenance', title: 'Maintenance' },
    });
    expect(maintenanceRes.ok()).toBeTruthy();
    const maintenanceModel = await maintenanceRes.json();
    maintenanceModelId = maintenanceModel.id;

    // Maintenance fields
    await request.post('http://127.0.0.1:5000/api/v1/sys-fields', {
      headers,
      data: { modelId: maintenanceModelId, name: 'description', type: 'text' },
    });
    await request.post('http://127.0.0.1:5000/api/v1/sys-fields', {
      headers,
      data: { modelId: maintenanceModelId, name: 'date', type: 'date', required: true },
    });
    await request.post('http://127.0.0.1:5000/api/v1/sys-fields', {
      headers,
      data: { modelId: maintenanceModelId, name: 'cost', type: 'float' },
    });
    await request.post('http://127.0.0.1:5000/api/v1/sys-fields', {
      headers,
      data: {
        modelId: maintenanceModelId,
        name: 'vehicle',
        type: 'relation',
        required: true,
        options: JSON.stringify({ target_table: 'vehicle', label_field: 'plate' }),
      },
    });

    // Add Lookup field on Maintenance: vehicle_plate
    await request.post('http://127.0.0.1:5000/api/v1/sys-fields', {
      headers,
      data: {
        modelId: maintenanceModelId,
        name: 'vehicle_plate',
        type: 'lookup',
        title: 'Targa Veicolo',
        options: JSON.stringify({ target_table: 'vehicle', local_key: 'vehicle', remote_key: 'id', remote_field: 'plate' }),
      },
    });

    await request.post(`http://127.0.0.1:5000/api/v1/sys-models/${maintenanceModelId}/generate-table`, { headers });

    // 5. Add Master-Detail (lines) and Summary fields on Vehicle
    await request.post('http://127.0.0.1:5000/api/v1/sys-fields', {
      headers,
      data: {
        modelId: vehicleModelId,
        name: 'maintenance_history',
        type: 'lines',
        title: 'Storico Manutenzioni',
        options: JSON.stringify({ target_table: 'maintenance', foreign_key: 'vehicle' }),
      },
    });

    await request.post('http://127.0.0.1:5000/api/v1/sys-fields', {
      headers,
      data: {
        modelId: vehicleModelId,
        name: 'total_maintenance_cost',
        type: 'summary',
        title: 'Totale Spese Manutenzione',
        summary_expression: 'SUM(cost)',
        options: JSON.stringify({ target_table: 'maintenance', foreign_key: 'vehicle' }),
      },
    });

    await request.post(`http://127.0.0.1:5000/api/v1/sys-models/${vehicleModelId}/generate-table`, { headers });
  });

  test('validate relation, lookup, summary, and lines data flow', async ({ page, request }) => {
    const headers = {
      Authorization: `Bearer ${authToken}`,
      'Content-Type': 'application/json',
    };

    const testPlate = 'AB' + String(Date.now()).slice(-5) + 'CD';

    // 1. Create Vehicle Record via API
    const createVehRes = await request.post(`http://127.0.0.1:5000/api/v1/projects/${projectId}/data/vehicle`, {
      headers,
      data: {
        plate: testPlate,
        brand: 'Ford',
        model: 'Transit',
      },
    });
    expect(createVehRes.ok()).toBeTruthy();
    const vehicleData = await createVehRes.json();
    const vehicleId = vehicleData.id;

    // 2. Create 2 Maintenance Records linked to Vehicle
    const m1Res = await request.post(`http://127.0.0.1:5000/api/v1/projects/${projectId}/data/maintenance`, {
      headers,
      data: {
        description: 'Cambio Olio',
        date: '2026-09-01',
        cost: 120.50,
        vehicle: vehicleId,
      },
    });
    expect(m1Res.ok()).toBeTruthy();

    const m2Res = await request.post(`http://127.0.0.1:5000/api/v1/projects/${projectId}/data/maintenance`, {
      headers,
      data: {
        description: 'Sostituzione Freni',
        date: '2026-09-05',
        cost: 200.00,
        vehicle: vehicleId,
      },
    });
    expect(m2Res.ok()).toBeTruthy();

    // 3. Verify Lookup field (vehicle_plate) via API
    const maintListRes = await request.get(`http://127.0.0.1:5000/api/v1/projects/${projectId}/data/maintenance`, { headers });
    expect(maintListRes.ok()).toBeTruthy();
    const maintList = await maintListRes.json();
    const items = Array.isArray(maintList) ? maintList : (maintList.items || []);
    expect(items.length).toBeGreaterThanOrEqual(2);
    expect(items[0].vehicle_plate).toBe(testPlate);

    // 4. Verify Summary field (total_maintenance_cost = 320.5) via API
    const vehDetailRes = await request.get(`http://127.0.0.1:5000/api/v1/projects/${projectId}/data/vehicle/${vehicleId}`, { headers });
    expect(vehDetailRes.ok()).toBeTruthy();
    const vehDetail = await vehDetailRes.json();
    expect(vehDetail.total_maintenance_cost).toBe(320.5);

    // 5. Test UI Rendering of dynamic models
    await page.goto('http://127.0.0.1:5173/login');
    await page.locator('input[type="email"]').fill('admin@erpseed.org');
    await page.locator('input[type="password"]').fill('admin123');
    await page.locator('#rememberMe').check();
    await page.locator('button[type="submit"]').click();
    await page.waitForURL('**/projects');

    // Navigate to Vehicle List
    await page.goto(`http://127.0.0.1:5173/projects/${projectId}/data/vehicle`);
    await page.waitForLoadState('networkidle');
    await expect(page.locator('body')).toContainText(testPlate);

    // Navigate to Maintenance List (verify lookup column vehicle_plate)
    await page.goto(`http://127.0.0.1:5173/projects/${projectId}/data/maintenance`);
    await page.waitForLoadState('networkidle');
    await expect(page.locator('body')).toContainText(testPlate);
  });
});
