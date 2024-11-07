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


What it does:

A slack bot that allows employees to print from their slack workspace directly to the office Epson printer.

```/print_weekly_report``` Generates and prints a weekly report summarizing team activities and collaboration.

```/print_monthly_report``` Generates and prints a monthly report summarizing team activities and collaboration.

```/print_yearly_report``` Generates and prints a yearly report summarizing team activities and collaboration.

```/print_user_report``` Produces a detailed report of what a user is currently working on

```/print_translate``` Translates the contents of a file into multiple languages and prints it. Currently supporting Spanish, Japanese, Russian, and Chinese.

```/print_file``` Searches for a specified file in Slack and prints it directly without downloading.

```/art``` Generates custom AI artwork based on a user-provided prompt.
