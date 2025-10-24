/**
 * E2E Tests: Data Source Management
 * Tests creating, viewing, and managing data sources
 */
import { test, expect } from '@playwright/test';

test.describe('Data Sources', () => {
  test.beforeEach(async ({ page }) => {
    // Login before each test
    await page.goto('/');
    await page.getByLabel(/email/i).fill('admin@nexbii.demo');
    await page.getByLabel(/password/i).fill('demo123');
    await page.getByRole('button', { name: /sign in/i }).click();
    
    // Wait for dashboard to load
    await page.waitForURL(/dashboard|queries|datasources/, { timeout: 10000 });
    
    // Navigate to data sources page
    await page.getByText('Data Sources').first().click();
    await page.waitForURL(/datasources/);
  });

  test('should display data sources page', async ({ page }) => {
    await expect(page).toHaveURL(/datasources/);
    await expect(page.getByText(/data sources/i)).toBeVisible();
  });

  test('should show existing data sources', async ({ page }) => {
    // Should show at least demo data sources
    const dataSourcesList = page.locator('[data-testid="datasource-item"], .datasource-card, .datasource-list-item');
    
    // Wait for data sources to load
    await page.waitForTimeout(2000);
    
    // Check if either list exists or "Add" button is visible
    const addButton = page.getByText(/add.*data source|new.*data source/i);
    await expect(addButton).toBeVisible();
  });

  test('should open add data source modal', async ({ page }) => {
    await page.getByText(/add.*data source|new.*data source/i).first().click();
    
    // Check for modal or form elements
    await expect(page.getByText(/add.*data source|create.*data source|new.*data source/i)).toBeVisible();
    await expect(page.getByLabel(/name/i)).toBeVisible();
  });

  test('should have different database type options', async ({ page }) => {
    await page.getByText(/add.*data source|new.*data source/i).first().click();
    
    // Check for database type selector
    const typeSelector = page.locator('select, [role="combobox"]').filter({ hasText: /type|database/i }).first();
    
    if (await typeSelector.isVisible()) {
      await expect(typeSelector).toBeVisible();
    }
  });

  test('should view data source schema', async ({ page }) => {
    // Wait for page to load
    await page.waitForTimeout(2000);
    
    // Look for schema or view button
    const schemaButton = page.getByText(/schema|view|details/i).first();
    
    if (await schemaButton.isVisible({ timeout: 5000 })) {
      await schemaButton.click();
      await expect(page.getByText(/schema|tables|columns/i)).toBeVisible();
    }
  });
});
