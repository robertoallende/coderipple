# Analyse your code

To get your repository analyzed by CodeRipple, you need to set up a webhook in your repository settings:

1. **Go to your repository settings** → Webhooks → Add webhook
2. **Payload URL**: `https://your-webhook-endpoint.com/webhook`
3. **Content type**: `application/json`
4. **Events**: Select "Push" events
5. **Save** the webhook

Once configured, every push to your repository will trigger an automatic analysis.
