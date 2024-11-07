1. Install Firebase CLI: Download and install the Firebase CLI if you haven't already.

   ```npm install -g firebase-tools```

2. Create a ```.env``` File:
   In the root of your project, create a ```.env``` file to store your environment variables. Replace the placeholders with your actual keys:

```
SLACK_BOT_TOKEN="your-slack-bot-token"
OPEN_AI_KEY="your-open-ai-key"
PRINTER_EMAIL="your-printer-email"
EPSON_CLIENT_ID="your-epson-client-id"
EPSON_CLIENT_SECRET="your-epson-client-secret"
```

3. Deploy to Firebase:
   After setting up your environment variables, deploy your Firebase Functions with:
   
   ```
   firebase deploy --only functions
   ```
