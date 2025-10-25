#!/usr/bin/env python3
"""
Tenant Settings Frontend Test
Verifies that the tenant settings page loads and displays data correctly
"""

import time
import json
from playwright.sync_api import sync_playwright

def test_tenant_settings():
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True)
        page = browser.new_page()
        
        print("🌐 Navigating to login page...")
        page.goto("http://localhost:3000/login", timeout=60000)
        time.sleep(3)
        
        print("🔑 Logging in...")
        # Fill login form
        page.fill('input[type="email"]', 'settings-test@test.com')
        page.fill('input[type="password"]', 'Test123!@#')
        page.click('button[type="submit"]')
        
        # Wait for navigation
        time.sleep(5)
        
        print("⚙️  Navigating to Tenant Settings...")
        page.goto("http://localhost:3000/tenant-settings", timeout=60000)
        time.sleep(3)
        
        # Take screenshot
        page.screenshot(path="/app/tenant_settings_screenshot.png")
        print("📸 Screenshot saved: /app/tenant_settings_screenshot.png")
        
        # Check for key elements
        print("\n✅ Checking page elements...")
        
        # Check page title
        title = page.locator('h1:has-text("Tenant Settings")').count()
        print(f"  ✓ Page title: {'Found' if title > 0 else 'NOT FOUND'}")
        
        # Check tabs
        branding_tab = page.locator('button:has-text("Branding")').count()
        domains_tab = page.locator('button:has-text("Custom Domains")').count()
        ssl_tab = page.locator('button:has-text("SSL Certificates")').count()
        print(f"  ✓ Branding tab: {'Found' if branding_tab > 0 else 'NOT FOUND'}")
        print(f"  ✓ Domains tab: {'Found' if domains_tab > 0 else 'NOT FOUND'}")
        print(f"  ✓ SSL tab: {'Found' if ssl_tab > 0 else 'NOT FOUND'}")
        
        # Check branding form fields
        logo_input = page.locator('input[placeholder*="logo"]').count()
        color_inputs = page.locator('input[type="color"]').count()
        print(f"  ✓ Logo input: {'Found' if logo_input > 0 else 'NOT FOUND'}")
        print(f"  ✓ Color inputs: {color_inputs} found")
        
        # Check save button
        save_button = page.locator('button:has-text("Save Branding")').count()
        print(f"  ✓ Save button: {'Found' if save_button > 0 else 'NOT FOUND'}")
        
        # Get page content
        content = page.content()
        
        # Check for error messages
        if "No tenant found" in content:
            print("\n❌ ERROR: No tenant found message displayed")
        elif "Failed to load" in content:
            print("\n❌ ERROR: Failed to load message displayed")
        else:
            print("\n✅ Page loaded successfully without errors")
        
        # Check if branding fields are populated or showing defaults
        primary_color = page.locator('input[type="color"]').first
        if primary_color.count() > 0:
            value = primary_color.get_attribute('value')
            print(f"\n🎨 Primary color value: {value}")
        
        # Test filling and saving branding
        print("\n🧪 Testing branding update...")
        page.fill('input[placeholder*="example.com/logo"]', 'https://via.placeholder.com/200x50/667eea/ffffff?text=TestCorp')
        page.locator('input[type="color"]').first.fill('#FF6B6B')
        
        # Click save
        page.click('button:has-text("Save Branding")')
        time.sleep(3)
        
        # Check for success message
        success_msg = page.locator('div:has-text("updated successfully")').count()
        print(f"  ✓ Success message: {'Shown' if success_msg > 0 else 'NOT SHOWN'}")
        
        # Take final screenshot
        page.screenshot(path="/app/tenant_settings_after_save.png")
        print("📸 Final screenshot saved: /app/tenant_settings_after_save.png")
        
        browser.close()
        print("\n✅ Test complete!")

if __name__ == "__main__":
    test_tenant_settings()
