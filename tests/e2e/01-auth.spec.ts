/**
 * E2E Tests: Authentication Flow
 * Tests user registration and login workflows
 */
import { test, expect } from '@playwright/test';

test.describe('Authentication', () => {
  test.beforeEach(async ({ page }) => {
    await page.goto('/');
  });

  test('should display login page', async ({ page }) => {
    await expect(page).toHaveTitle(/NexBII/);
    await expect(page.getByText(/sign in to your account/i)).toBeVisible();
    await expect(page.getByLabel(/email/i)).toBeVisible();
    await expect(page.getByLabel(/password/i)).toBeVisible();
  });

  test('should login with valid credentials', async ({ page }) => {
    // Fill in login form with demo credentials
    await page.getByLabel(/email/i).fill('admin@nexbii.demo');
    await page.getByLabel(/password/i).fill('demo123');
    
    // Click sign in button
    await page.getByRole('button', { name: /sign in/i }).click();
    
    // Wait for navigation to complete
    await page.waitForURL(/dashboard|queries|datasources/);
    
    // Verify user is logged in (check for user menu or dashboard)
    await expect(page).toHaveURL(/dashboard|queries|datasources/);
  });

  test('should show error with invalid credentials', async ({ page }) => {
    await page.getByLabel(/email/i).fill('invalid@example.com');
    await page.getByLabel(/password/i).fill('wrongpassword');
    
    await page.getByRole('button', { name: /sign in/i }).click();
    
    // Wait for error message
    await expect(page.getByText(/invalid|error|failed/i)).toBeVisible({ timeout: 5000 });
  });

  test('should have link to register page', async ({ page }) => {
    const registerLink = page.getByText(/create an account|sign up/i);
    await expect(registerLink).toBeVisible();
  });

  test('should have forgot password link', async ({ page }) => {
    const forgotLink = page.getByText(/forgot password/i);
    await expect(forgotLink).toBeVisible();
  });

  test('should navigate to register page', async ({ page }) => {
    await page.getByText(/create an account|sign up/i).click();
    await expect(page).toHaveURL(/register/);
    await expect(page.getByText(/create.*account/i)).toBeVisible();
  });

  test('should logout successfully', async ({ page }) => {
    // Login first
    await page.getByLabel(/email/i).fill('admin@nexbii.demo');
    await page.getByLabel(/password/i).fill('demo123');
    await page.getByRole('button', { name: /sign in/i }).click();
    
    // Wait for successful login
    await page.waitForURL(/dashboard|queries|datasources/);
    
    // Click logout
    await page.getByText(/logout|sign out/i).click();
    
    // Verify redirected to login
    await expect(page).toHaveURL(/login|^\//);
  });
});
