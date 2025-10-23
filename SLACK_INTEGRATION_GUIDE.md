# Slack Integration Guide for NexBII Alerts

## Overview

NexBII now supports **Slack webhook notifications** for alerts! Get real-time notifications in your Slack channels when alert conditions are met.

## ✨ Features

- 🔔 **Rich Formatted Notifications** - Beautiful Slack messages with blocks, colors, and buttons
- 🧪 **Webhook Testing** - Test your webhook configuration before creating alerts
- ⚡ **Real-time Alerts** - Instant notifications when thresholds are exceeded
- 📊 **Detailed Context** - Include query names, thresholds, and actual values
- 🎯 **Flexible Configuration** - Enable/disable Slack per alert
- 🔄 **Mock Mode** - Development-friendly mock mode for testing

## 🚀 Quick Start

### Step 1: Get Your Slack Webhook URL

1. Go to https://api.slack.com/apps
2. Create a new app or select an existing one
3. Navigate to "Incoming Webhooks"
4. Activate Incoming Webhooks
5. Click "Add New Webhook to Workspace"
6. Select the channel where you want notifications
7. Copy the webhook URL (looks like: `https://hooks.slack.com/services/T00000000/B00000000/XXXXXXXXXXXXXXXXXXXX`)

### Step 2: Create an Alert with Slack Notifications

1. Go to the **Alerts** page in NexBII
2. Click **"Create Alert"**
3. Fill in the basic alert details:
   - Name
   - Query to monitor
   - Condition (>, <, =, ≠, between)
   - Metric column
   - Threshold value
   - Check frequency

4. Enable Slack notifications:
   - ✅ Check **"Send notifications to Slack"**
   - Paste your webhook URL
   - Click **"Test Webhook"** to verify it works
   
5. Click **"Create Alert"**

### Step 3: Test Your Alert

- Use the **"Test"** button on the alert card to manually trigger evaluation
- If conditions are met, you'll receive a Slack notification instantly
- Check your Slack channel for the formatted message

## 📝 Example Slack Notification

When an alert triggers, Slack receives a beautifully formatted message:

```
🔔 Alert Triggered: High Revenue Alert

Query: Daily Revenue Query
Triggered At: December 20, 2024 at 02:30 PM

Condition: Value greater than 10000
Threshold: 10000

⚠️ Actual Value: 15,432

[View Alert Button]

📊 NexBII Analytics Platform - Intelligent Alerts & Monitoring
```

## 🔧 Configuration

### Backend Environment Variables

You can configure Slack behavior via environment variables in `/app/backend/.env`:

```bash
# Slack Configuration
MOCK_SLACK=true  # Set to 'false' for real Slack notifications
```

**Development Mode (Default):**
- `MOCK_SLACK=true` - Notifications are logged to console but not sent to Slack
- Perfect for development and testing without spamming channels

**Production Mode:**
- `MOCK_SLACK=false` - Notifications are sent to actual Slack webhooks
- Use this when you're ready for real notifications

### Alert Model Fields

Each alert can have the following Slack-related fields:

```python
notify_slack: bool = False        # Enable Slack notifications
slack_webhook: str                # Slack webhook URL
```

## 🎨 Notification Format

Slack notifications use [Block Kit](https://api.slack.com/block-kit) for rich formatting:

- **Header Block**: Alert name with emoji
- **Section Blocks**: Query info, timestamp, condition details
- **Highlighted Value**: The actual value that triggered the alert
- **Action Button**: Direct link to view the alert (if configured)
- **Footer**: Platform branding and context

## 🧪 Testing

### Test Webhook Connection

Use the built-in webhook tester:

```typescript
// Frontend
await alertService.testSlackWebhook(webhookUrl);
```

```python
# Backend
from app.services.slack_service import SlackService
SlackService.send_test_message(webhook_url)
```

### Manual Alert Evaluation

Trigger an alert manually to test notifications:

1. Go to Alerts page
2. Click **"Test"** on any alert
3. Check your Slack channel

### API Endpoint

```bash
POST /api/alerts/test-slack-webhook?webhook_url=<YOUR_WEBHOOK_URL>
```

## 📡 API Reference

### Test Slack Webhook

**Endpoint:** `POST /api/alerts/test-slack-webhook`

**Query Parameters:**
- `webhook_url` (required): Slack webhook URL to test

**Response:**
```json
{
  "success": true,
  "message": "Test message sent successfully to Slack"
}
```

### Create Alert with Slack

**Endpoint:** `POST /api/alerts/`

**Request Body:**
```json
{
  "name": "High Revenue Alert",
  "query_id": "query-uuid",
  "condition_type": "greater_than",
  "metric_column": "total_revenue",
  "threshold_value": 10000,
  "frequency": "hourly",
  "notify_emails": ["admin@company.com"],
  "notify_slack": true,
  "slack_webhook": "https://hooks.slack.com/services/..."
}
```

## 🔒 Security Best Practices

1. **Keep Webhooks Secret**: Treat webhook URLs like passwords
2. **Use Environment Variables**: Don't hardcode webhooks in code
3. **Limit Webhook Scope**: Create channel-specific webhooks
4. **Rotate Regularly**: Regenerate webhooks periodically
5. **Monitor Usage**: Review Slack app usage logs

## 🐛 Troubleshooting

### Webhook Test Fails

**Problem:** "Failed to send test message to Slack webhook"

**Solutions:**
1. Verify webhook URL is correct (starts with `https://hooks.slack.com/`)
2. Check if webhook is still active in Slack settings
3. Ensure `MOCK_SLACK=false` in production
4. Check backend logs: `tail -f /var/log/supervisor/backend.out.log`

### Notifications Not Received

**Problem:** Alert triggers but no Slack message

**Checklist:**
- [ ] `notify_slack` is enabled on the alert
- [ ] `slack_webhook` URL is valid
- [ ] Alert condition was actually met
- [ ] Webhook is not revoked in Slack
- [ ] Check backend logs for errors
- [ ] Verify `MOCK_SLACK` setting

### "Invalid Slack webhook URL format"

**Problem:** Backend rejects webhook URL

**Solution:** 
- Ensure URL starts with `https://` or `http://`
- Slack webhooks typically start with `https://hooks.slack.com/services/`
- Copy the entire webhook URL from Slack settings

## 🎯 Advanced Usage

### Multiple Channels

Create different alerts with different webhook URLs to send notifications to multiple channels:

```javascript
// Alert 1 -> #engineering channel
notify_slack: true,
slack_webhook: "https://hooks.slack.com/services/.../engineering"

// Alert 2 -> #operations channel  
notify_slack: true,
slack_webhook: "https://hooks.slack.com/services/.../operations"
```

### Combining Email and Slack

You can enable both email AND Slack notifications:

```javascript
{
  "notify_emails": ["team@company.com"],
  "notify_slack": true,
  "slack_webhook": "https://hooks.slack.com/..."
}
```

Both channels will receive notifications when the alert triggers.

### Background Monitoring

The background monitor checks alerts every 5 minutes (default) and sends notifications automatically:

```python
# Configured in server.py
background_monitor = BackgroundMonitor(check_interval=300)  # 5 minutes
```

## 📊 Architecture

### Components

1. **SlackService** (`/app/backend/app/services/slack_service.py`)
   - Handles webhook HTTP requests
   - Formats rich Slack messages
   - Provides mock mode for development

2. **AlertService** (`/app/backend/app/services/alert_service.py`)
   - Evaluates alert conditions
   - Triggers notifications (Email + Slack)
   - Records history

3. **BackgroundMonitor** (`/app/backend/app/services/background_monitor.py`)
   - Runs in separate thread
   - Checks due alerts every 5 minutes
   - Sends scheduled notifications

4. **AlertsPage** (`/app/frontend/src/pages/AlertsPage.tsx`)
   - UI for creating/managing alerts
   - Webhook testing interface
   - Alert status display

### Flow Diagram

```
Alert Condition Met
       ↓
AlertService.evaluate_alert()
       ↓
AlertService._send_alert_notification()
       ↓
   ┌───────┴───────┐
   ↓               ↓
EmailService    SlackService
   ↓               ↓
SMTP Server    Slack API
   ↓               ↓
Recipient      Channel
```

## 🚀 Future Enhancements

Potential improvements for future versions:

- [ ] Slack interactive buttons (snooze, acknowledge)
- [ ] Thread replies for alert updates
- [ ] Custom message templates
- [ ] Slack slash commands
- [ ] Alert grouping/batching
- [ ] Slack user mentions (@user)
- [ ] Dashboard subscriptions to Slack
- [ ] Rich charts in Slack messages

## 📚 Resources

- [Slack Incoming Webhooks Documentation](https://api.slack.com/messaging/webhooks)
- [Slack Block Kit Builder](https://app.slack.com/block-kit-builder)
- [NexBII Alerts Documentation](./ROADMAP.md)

## 💡 Tips

1. **Use Mock Mode First**: Test with `MOCK_SLACK=true` before going live
2. **Test Webhooks**: Always click "Test Webhook" before creating an alert
3. **Descriptive Names**: Use clear alert names for easy identification in Slack
4. **Channel Organization**: Create dedicated channels for different alert types
5. **Frequency Balance**: Don't set hourly checks for non-critical alerts

## 📞 Support

For issues or questions:
- Check backend logs: `/var/log/supervisor/backend.out.log`
- Review alert history in the UI
- Verify Slack webhook status
- Consult [ROADMAP.md](./ROADMAP.md) for feature status

---

**Built with ❤️ for the NexBII Analytics Platform**
