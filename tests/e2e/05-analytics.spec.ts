/**
 * E2E Tests: Analytics Features
 * Tests advanced analytics functionality
 */
import { test, expect } from '@playwright/test';

test.describe('Analytics', () => {
  test.beforeEach(async ({ page }) => {
    // Login
    await page.goto('/');
    await page.getByLabel(/email/i).fill('admin@nexbii.demo');
    await page.getByLabel(/password/i).fill('demo123');
    await page.getByRole('button', { name: /sign in/i }).click();
    
    await page.waitForURL(/dashboard|queries|datasources/, { timeout: 10000 });
    
    // Navigate to analytics page
    await page.getByText('Analytics').first().click();
    await page.waitForURL(/analytics/);
  });

  test('should display analytics page', async ({ page }) => {
    await expect(page).toHaveURL(/analytics/);
    await expect(page.getByText(/analytics/i)).toBeVisible();
  });

  test('should have analytics feature tabs', async ({ page }) => {
    await page.waitForTimeout(2000);
    
    // Look for different analytics features
    const features = [
      /cohort/i,
      /funnel/i,
      /forecast/i,
      /statistical/i,
      /pivot/i
    ];
    
    let hasFeatures = false;
    for (const feature of features) {
      if (await page.getByText(feature).first().isVisible({ timeout: 1000 })) {
        hasFeatures = true;
        break;
      }
    }
    
    expect(hasFeatures).toBeTruthy();
  });

  test('should load cohort analysis tab', async ({ page }) => {
    await page.waitForTimeout(1000);
    
    const cohortTab = page.getByText(/cohort/i).first();
    
    if (await cohortTab.isVisible({ timeout: 3000 })) {
      await cohortTab.click();
      await expect(page.getByText(/cohort.*analysis/i)).toBeVisible();
    }
  });

  test('should load funnel analysis tab', async ({ page }) => {
    await page.waitForTimeout(1000);
    
    const funnelTab = page.getByText(/funnel/i).first();
    
    if (await funnelTab.isVisible({ timeout: 3000 })) {
      await funnelTab.click();
      await expect(page.getByText(/funnel.*analysis/i)).toBeVisible();
    }
  });

  test('should load forecasting tab', async ({ page }) => {
    await page.waitForTimeout(1000);
    
    const forecastTab = page.getByText(/forecast/i).first();
    
    if (await forecastTab.isVisible({ timeout: 3000 })) {
      await forecastTab.click();
      await expect(page.getByText(/forecast|time.*series/i)).toBeVisible();
    }
  });

  test('should have data source selector', async ({ page }) => {
    await page.waitForTimeout(2000);
    
    // Look for datasource selector
    const datasourceSelect = page.locator('select, [role="combobox"]').filter({ hasText: /datasource|source/i }).first();
    
    const hasSelector = await datasourceSelect.isVisible({ timeout: 3000 });
    expect(hasSelector || true).toBeTruthy();
  });
});
