# How to Set Up Google Cloud Text-to-Speech (TTS)

Follow these steps to enable Google Cloud TTS and get your credentials.

## Step 1: Create a Google Cloud Project
1.  Go to the [Google Cloud Console](https://console.cloud.google.com/).
2.  Click on the project dropdown at the top left.
3.  Click **"New Project"**.
4.  Enter a name (e.g., `RailPro-AI`) and click **Create**.
5.  Select the newly created project.

## Step 2: Enable the Text-to-Speech API
1.  In the search bar at the top, type **"Text-to-Speech API"**.
2.  Click on **"Cloud Text-to-Speech API"** in the results.
3.  Click **"Enable"**.
    *   *Note: You may need to link a billing account. Google Cloud offers a free tier (e.g., 4 million characters free per month for standard voices).*

## Step 3: Create a Service Account
1.  Go to **IAM & Admin** > **Service Accounts** in the left sidebar.
2.  Click **"+ CREATE SERVICE ACCOUNT"** at the top.
3.  **Service account details**:
    *   Name: `railpro-tts-service`
    *   Click **Create and Continue**.
4.  **Grant this service account access to project**:
    *   Role: Search for and select **"Cloud Text-to-Speech API User"**.
    *   Click **Continue**.
5.  Click **Done**.

## Step 4: Download the JSON Key
1.  In the Service Accounts list, click on the email address of the service account you just created (e.g., `railpro-tts-service@...`).
2.  Go to the **KEYS** tab.
3.  Click **ADD KEY** > **Create new key**.
4.  Select **JSON**.
5.  Click **Create**.
6.  A JSON file will automatically download to your computer.
    *   **Keep this file safe!** It contains your credentials.

## Step 5: Configure Your Project
1.  Move the downloaded JSON file to your project folder: `c:\Users\abinv\Desktop\DEV\railpro\`
2.  Rename it to something simple, like `service_account.json`.
3.  Open your `.env` file in VS Code.
4.  Update the `GOOGLE_APPLICATION_CREDENTIALS` variable:
    ```env
    GOOGLE_APPLICATION_CREDENTIALS=service_account.json
    ```
    *(If you put it in a subfolder, make sure to include the full path).*

## Step 6: Verify
The backend is already configured to look for this file. Once you restart the server, TTS will be enabled.
