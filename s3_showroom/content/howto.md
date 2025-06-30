# Analyze Your Code with CodeRipple

Connect your GitHub repository to CodeRipple's automated analysis pipeline by configuring a webhook. Every push to your repository will trigger comprehensive code analysis and generate detailed documentation.

## Setup Instructions

### Step 1: Access Repository Settings
1. Navigate to your GitHub repository
2. Click the **Settings** tab
3. Select **Webhooks** from the left sidebar
4. Click **Add webhook**

### Step 2: Configure Webhook
**Payload URL:**
```
https://1dx8rzw03f.execute-api.us-east-1.amazonaws.com/prod/webhook
```

**Content type:** `application/json`

**SSL verification:** ✅ **Enable SSL verification** (recommended)

**Which events would you like to trigger this webhook?**
- Select **"Just the push event"**
- This triggers CodeRipple analysis when code is pushed to your repository

**Active:** ✅ **Checked** (enables webhook delivery)

### Step 3: Save and Test
1. Click **Add webhook**
2. GitHub will immediately send a test ping
3. Look for a ✅ green checkmark indicating successful delivery
4. Expected response: `200 OK` with message `"Webhook received - CodeRipple Gatekeeper"`

### Step 4: Trigger Analysis
Push code to your repository:
```bash
git add .
git commit -m "Trigger CodeRipple analysis"
git push
```

## View Your Results

After triggering the webhook, your analysis documentation will be available within a few minutes at:

**🌐 [CodeRipple Showroom](http://coderipple-showroom.s3-website-us-east-1.amazonaws.com/)**

The analysis includes comprehensive code documentation, metrics, and insights delivered through an elegant web interface.
