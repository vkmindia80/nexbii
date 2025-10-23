# Testing Guide for Collaboration & Alert Features

## 🧪 Testing Overview

This guide provides step-by-step instructions for testing all collaboration and alert features in NexBII.

## Prerequisites

✅ **Required:**
- Backend running on http://localhost:8001
- Frontend running on http://localhost:3000
- Demo user credentials: `admin@nexbii.demo` / `demo123`
- PostgreSQL database running
- MongoDB running (optional)

⚠️ **Current Configuration:**
- `MOCK_EMAIL=true` (emails logged, not sent)
- `MOCK_SLACK=true` (Slack messages logged, not sent)

## 📋 Test Plan

### Phase 1: Alert System Testing

#### Test 1.1: Create Basic Alert

**Objective:** Verify alert creation with email notifications

**Steps:**
1. Navigate to http://localhost:3000/alerts
2. Click "Create Alert" button
3. Fill in the form:
   - Name: "Test Revenue Alert"
   - Description: "Testing alert system"
   - Query: Select any available query
   - Metric Column: Enter column name (e.g., "total")
   - Condition: "Greater than"
   - Threshold Value: 100
   - Frequency: "Once"
   - Notification Emails: Add your email
4. Click "Create Alert"

**Expected Result:**
- ✅ Alert created successfully
- ✅ Alert appears in alerts list
- ✅ Alert status shows as "active"

---

#### Test 1.2: Test Slack Integration

**Objective:** Verify Slack webhook configuration and testing

**Steps:**
1. Navigate to http://localhost:3000/alerts
2. Click "Create Alert"
3. Fill in basic alert details (similar to Test 1.1)
4. Check "Send notifications to Slack"
5. Enter webhook URL: `https://hooks.slack.com/services/TEST/TEST/TEST`
6. Click "Test Webhook" button

**Expected Result:**
- ✅ In MOCK mode: Success message appears
- ✅ Backend logs show: `💬 [MOCK SLACK] Webhook: https://hooks.slack.com/...`
- ✅ Backend logs show: `💬 [MOCK SLACK] Message: ✅ Slack webhook test successful!`

**Check Logs:**
```bash
tail -f /var/log/supervisor/backend.out.log | grep "MOCK SLACK"
```

---

#### Test 1.3: Manual Alert Evaluation

**Objective:** Test alert evaluation and notification triggering

**Steps:**
1. Go to Alerts page
2. Find the alert created in Test 1.1
3. Click the "Test" button

**Expected Result:**
- ✅ Alert evaluated successfully message appears
- ✅ If condition met, backend logs show email notification
- ✅ If Slack enabled, backend logs show Slack notification

**Check Logs:**
```bash
# Email notification
tail /var/log/supervisor/backend.out.log | grep "MOCK EMAIL"

# Slack notification
tail /var/log/supervisor/backend.out.log | grep "MOCK SLACK"
```

---

#### Test 1.4: Alert Status Management

**Objective:** Test pause/resume functionality

**Steps:**
1. Find an active alert
2. Click the pause icon (two vertical bars)
3. Verify status changes
4. Click play icon to resume
5. Verify status changes back to active

**Expected Result:**
- ✅ Alert pauses successfully
- ✅ Alert resumes successfully
- ✅ UI updates immediately

---

#### Test 1.5: Alert Deletion

**Objective:** Verify alert deletion

**Steps:**
1. Find a test alert
2. Click delete (trash) icon
3. Confirm deletion

**Expected Result:**
- ✅ Confirmation dialog appears
- ✅ Alert is deleted
- ✅ Alert disappears from list

---

### Phase 2: Email Subscriptions Testing

#### Test 2.1: Create Dashboard Subscription

**Objective:** Test subscription modal and creation

**Steps:**
1. Navigate to a dashboard (http://localhost:3000/dashboards)
2. Open any dashboard
3. Click "Subscribe" button (if available in toolbar)
4. Select frequency: "Weekly"
5. Click "Subscribe"

**Expected Result:**
- ✅ Subscription created successfully
- ✅ Success message appears
- ✅ Modal closes

**Alternative:** If subscribe button not in viewer, add it:
- Open `DashboardViewerPage.tsx`
- Look for subscription button around line 310

---

#### Test 2.2: Verify Subscription Created

**Objective:** Check subscription in database

**Steps:**
```bash
# Connect to PostgreSQL
psql -h localhost -U postgres -d nexbii

# Query subscriptions
SELECT * FROM email_subscriptions ORDER BY created_at DESC LIMIT 5;
```

**Expected Result:**
- ✅ Subscription record exists
- ✅ Frequency is correct
- ✅ next_send_date is set
- ✅ is_active is true

---

#### Test 2.3: Background Monitor - Subscriptions

**Objective:** Verify background monitor processes subscriptions

**Steps:**
1. Manually trigger subscription processing (as admin):
```bash
curl -X POST http://localhost:8001/api/subscriptions/send-due \
  -H "Authorization: Bearer YOUR_TOKEN"
```

**Expected Result:**
- ✅ Response shows count of sent emails
- ✅ Backend logs show: `📧 [MOCK EMAIL] ...`

---

### Phase 3: Comments & Mentions Testing

#### Test 3.1: Add Comment to Dashboard

**Objective:** Test comment creation

**Steps:**
1. Open any dashboard
2. Scroll to comments section
3. Enter comment: "This is a test comment"
4. Click send button

**Expected Result:**
- ✅ Comment appears immediately
- ✅ Timestamp is shown
- ✅ Delete button visible

---

#### Test 3.2: Test @Mentions

**Objective:** Verify mention detection and notification

**Steps:**
1. In comment input, type: "@admin This needs review"
2. Submit comment

**Expected Result:**
- ✅ Comment created
- ✅ Backend logs mention detection (if implemented)
- ✅ Email notification triggered (in MOCK mode, logged)

**Check Logs:**
```bash
tail /var/log/supervisor/backend.out.log | grep "mention"
```

---

#### Test 3.3: Delete Comment

**Objective:** Test comment deletion

**Steps:**
1. Find a comment you created
2. Click delete button
3. Confirm deletion

**Expected Result:**
- ✅ Confirmation dialog appears
- ✅ Comment is deleted
- ✅ Comment disappears from list

---

### Phase 4: Activity Feed Testing

#### Test 4.1: View My Activities

**Objective:** Test activity feed display

**Steps:**
1. Navigate to http://localhost:3000/activity
2. Verify "My Activities" is selected
3. Scroll through activities

**Expected Result:**
- ✅ Activities load successfully
- ✅ Recent activities appear first
- ✅ Each activity shows:
  - Icon with color coding
  - Entity name
  - Description
  - Relative timestamp (e.g., "5m ago")
  - Activity type badge

---

#### Test 4.2: View All Activities

**Objective:** Test all activities view (Admin/Editor only)

**Steps:**
1. On Activity Feed page
2. Click "All Activities" button
3. Verify activities from all users appear

**Expected Result:**
- ✅ Filter switches successfully
- ✅ All user activities visible
- ✅ If not admin, error message shown

---

#### Test 4.3: Verify Activity Logging

**Objective:** Check that activities are created automatically

**Steps:**
1. Create a new query
2. Update a dashboard
3. Delete a data source
4. Trigger an alert
5. Go to Activity Feed

**Expected Result:**
- ✅ All actions appear in activity feed
- ✅ Correct activity types
- ✅ Proper descriptions

---

### Phase 5: Dashboard Sharing Testing

#### Test 5.1: Create Public Share Link

**Objective:** Test dashboard sharing with public links

**Steps:**
1. Open any dashboard
2. Click "Share" button
3. Configure sharing:
   - Enable "Public Link"
   - Set expiration: "7 days"
   - Optional: Set password
   - Select: "View Only" mode
4. Click "Create Share Link"
5. Copy the share URL

**Expected Result:**
- ✅ Share link generated
- ✅ Share token visible
- ✅ Copy button works

---

#### Test 5.2: Access Public Dashboard

**Objective:** Test public dashboard access

**Steps:**
1. Open share URL in incognito/private window
2. If password protected, enter password
3. View dashboard

**Expected Result:**
- ✅ Dashboard loads without login
- ✅ Password prompt if protected
- ✅ View-only mode (no edit controls)
- ✅ All widgets render correctly

---

#### Test 5.3: Revoke Share Link

**Objective:** Test share link revocation

**Steps:**
1. Go back to dashboard (logged in)
2. Open Share modal
3. Click "Revoke" on the share link
4. Try accessing the share URL again

**Expected Result:**
- ✅ Link marked as inactive
- ✅ Share URL no longer works
- ✅ Error message shown to public users

---

### Phase 6: Background Monitor Testing

#### Test 6.1: Verify Background Monitor Running

**Objective:** Check that background monitor started

**Steps:**
```bash
# Check backend startup logs
grep "Background monitor" /var/log/supervisor/backend.out.log

# Check for monitoring activity
tail -f /var/log/supervisor/backend.out.log | grep -E "Alert check|subscription emails"
```

**Expected Result:**
- ✅ Log shows: "✅ Background monitor started for alerts and subscriptions"
- ✅ Every 5 minutes, monitor checks alerts
- ✅ Every 5 minutes, monitor checks subscriptions

---

#### Test 6.2: Manual Background Check

**Objective:** Manually trigger background processes (Admin only)

**Steps:**
```bash
# Get auth token first
TOKEN=$(curl -s -X POST http://localhost:8001/api/auth/login \
  -H "Content-Type: application/json" \
  -d '{"email":"admin@nexbii.demo","password":"demo123"}' \
  | python -c "import sys, json; print(json.load(sys.stdin)['access_token'])")

# Check all alerts
curl -X POST http://localhost:8001/api/alerts/check-all \
  -H "Authorization: Bearer $TOKEN"

# Send due subscriptions
curl -X POST http://localhost:8001/api/subscriptions/send-due \
  -H "Authorization: Bearer $TOKEN"
```

**Expected Result:**
- ✅ Alerts checked
- ✅ Response shows checked/triggered counts
- ✅ Subscriptions processed
- ✅ Response shows sent count

---

## 🔍 Debugging & Logs

### View Backend Logs

```bash
# Real-time output logs
tail -f /var/log/supervisor/backend.out.log

# Real-time error logs
tail -f /var/log/supervisor/backend.err.log

# Search for specific messages
grep "MOCK EMAIL" /var/log/supervisor/backend.out.log
grep "MOCK SLACK" /var/log/supervisor/backend.out.log
grep "Alert" /var/log/supervisor/backend.out.log
grep "subscription" /var/log/supervisor/backend.out.log
```

### View Frontend Logs

```bash
# Frontend logs
tail -f /var/log/supervisor/frontend.out.log

# Browser console
# Open Developer Tools > Console in your browser
```

### Check Service Status

```bash
sudo supervisorctl -c /etc/supervisor/supervisord.conf status
```

### Database Inspection

```bash
# Connect to PostgreSQL
psql -h localhost -U postgres -d nexbii

# Useful queries
SELECT COUNT(*) FROM alerts;
SELECT COUNT(*) FROM alert_history;
SELECT COUNT(*) FROM email_subscriptions;
SELECT COUNT(*) FROM comments;
SELECT COUNT(*) FROM activities;
SELECT COUNT(*) FROM shared_dashboards;

# Recent activities
SELECT activity_type, entity_name, created_at 
FROM activities 
ORDER BY created_at DESC 
LIMIT 10;

# Active alerts
SELECT name, status, frequency, is_active 
FROM alerts 
WHERE is_active = true;
```

---

## ✅ Testing Checklist

### Alert System
- [ ] Create alert with email notifications
- [ ] Create alert with Slack notifications
- [ ] Test Slack webhook
- [ ] Manual alert evaluation
- [ ] Alert triggers and sends notifications
- [ ] Pause/resume alert
- [ ] Delete alert
- [ ] View alert history
- [ ] Snooze alert

### Email Subscriptions
- [ ] Create subscription
- [ ] Update subscription frequency
- [ ] Unsubscribe
- [ ] Background monitor sends emails
- [ ] Email templates render correctly

### Comments & Mentions
- [ ] Add comment to dashboard
- [ ] Add comment to query
- [ ] Use @mention
- [ ] Edit comment
- [ ] Delete comment
- [ ] Reply to comment (if threading implemented)

### Activity Feed
- [ ] View my activities
- [ ] View all activities (admin)
- [ ] Activities created automatically
- [ ] Filtering works
- [ ] Icons and colors correct
- [ ] Timestamps relative

### Dashboard Sharing
- [ ] Create public share link
- [ ] Password protect link
- [ ] Set expiration date
- [ ] Access public dashboard
- [ ] View-only mode works
- [ ] Interactive mode works
- [ ] Revoke share link
- [ ] Embed code works

### Background Monitor
- [ ] Monitor starts on application startup
- [ ] Checks alerts every 5 minutes
- [ ] Sends due subscriptions
- [ ] Logs activity correctly
- [ ] Handles errors gracefully

---

## 🐛 Known Issues & Limitations

### Current Limitations

1. **Mock Mode Only**
   - Emails are logged but not sent (MOCK_EMAIL=true)
   - Slack messages are logged but not sent (MOCK_SLACK=true)
   - **Solution:** Set environment variables to false for production

2. **No Real-Time Updates**
   - Activity feed doesn't auto-refresh
   - Comments don't update live
   - **Solution:** Manual page refresh or implement WebSockets

3. **No Alert History UI**
   - Alert history exists in backend
   - No frontend component to display history yet
   - **Solution:** Add history modal in future enhancement

4. **Limited Error Handling**
   - Some edge cases may not have user-friendly errors
   - **Solution:** Add comprehensive error messages

### Workarounds

**For Real Email Testing:**
```bash
# In backend/.env
MOCK_EMAIL=false
SMTP_HOST=smtp.gmail.com
SMTP_PORT=587
SMTP_USER=your-email@gmail.com
SMTP_PASSWORD=your-app-password
```

**For Real Slack Testing:**
```bash
# In backend/.env
MOCK_SLACK=false

# Then use real Slack webhook URL in alert form
```

---

## 📊 Test Results Template

Use this template to document your test results:

```markdown
## Test Results - [Date]

### Tester: [Name]
### Environment: Development/Staging/Production

| Test ID | Test Name | Status | Notes |
|---------|-----------|--------|-------|
| 1.1 | Create Basic Alert | ✅ PASS | |
| 1.2 | Test Slack Integration | ✅ PASS | |
| 1.3 | Manual Alert Evaluation | ✅ PASS | |
| 1.4 | Alert Status Management | ✅ PASS | |
| 1.5 | Alert Deletion | ✅ PASS | |
| 2.1 | Create Dashboard Subscription | ❌ FAIL | Button not visible |
| ... | ... | ... | ... |

### Issues Found
1. [Issue description]
   - Severity: High/Medium/Low
   - Steps to reproduce
   - Expected vs Actual

### Overall Summary
- Total Tests: X
- Passed: Y
- Failed: Z
- Pass Rate: Y/X * 100%
```

---

## 🚀 Next Steps After Testing

1. **Fix Any Bugs Found**
   - Document issues
   - Prioritize by severity
   - Fix and retest

2. **Performance Testing**
   - Load test with many alerts
   - Stress test background monitor
   - Database query optimization

3. **Production Deployment**
   - Update environment variables
   - Configure real SMTP
   - Set up real Slack webhooks
   - Monitor background services

4. **User Documentation**
   - Create user guides
   - Add tooltips in UI
   - Record demo videos

---

## 📚 Additional Resources

- **Slack Setup:** See `/app/SLACK_INTEGRATION_GUIDE.md`
- **Feature Overview:** See `/app/COLLABORATION_FEATURES_COMPLETE.md`
- **Roadmap:** See `/app/ROADMAP.md`
- **API Docs:** http://localhost:8001/docs

---

**Happy Testing! 🧪**

If you encounter any issues, check the logs first, then refer to the troubleshooting sections in the respective guides.
