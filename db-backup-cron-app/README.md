# 📦 Project Backup Setup with Google Drive

This project uses a Google Service Account to automatically back up your database files to a Google Drive folder. Follow the steps below to configure your environment.

---

## 🔧 Step 1: Create a Google Service Account

1. Navigate to the [Google Cloud Console](https://console.cloud.google.com/).
2. Go to:
   ```
   IAM & Admin > Service Accounts
   ```
3. Click **"Create Service Account"**.
4. Provide a name and description, then click **"Create and Continue"**.
5. Assign a role such as `Editor` or `Storage Admin`, then click **"Done"** (Optional).
6. After creation, **copy the email address** of the service account.
   - Example: `db-backup@your-project-id.iam.gserviceaccount.com`

---

## 🔑 Step 2: Generate and Save Service Account Key

1. In the service account list, click the **three dots** next to your account.
2. Select **"Manage keys"**.
3. Click **"Add Key" > "Create new key"**, select **JSON**, then click **Create**.
4. Save the downloaded JSON file to your project directory.
5. Rename the file to:
   ```
   service_account.json
   ```

---

## 📁 Step 3: Setup Google Drive Folder

1. Go to [Google Drive](https://drive.google.com/).
2. Create a new folder dedicated to backups.
3. Right-click the folder > **"Share"** > paste the service account email to grant access.
4. Click **"Done"**.
5. Open the folder and copy the Folder ID from the URL:
   ```
   https://drive.google.com/drive/u/0/folders/<GOOGLE_DRIVE_FOLDER_ID>
   ```

---

## ⚙️ Step 4: Configure Environment Variables

In your project's `.env` file, add the following variables:

```env
GOOGLE_DRIVE_FOLDER_ID=<your_google_drive_folder_id>
GOOGLE_SERVICE_ACCOUNT_FILE=service_account.json
BACKUP_DIR=./db-backup-cron-app/db-backups
```

> 🔒 Also ensure the same <google_drive_folder_id> is configured in [DB_CRON_FILE](./db-cron.py) DRIVE_FOLDER_ID varibale

    DRIVE_FOLDER_ID = <google_drive_folder_id>

> 🔒 Ensure `.env` and `service_account.json` are included in `.gitignore` to avoid committing sensitive information.

---

## ✅ Setup Complete

Your project is now configured to use a Google Service Account to upload database backups to a Google Drive folder automatically. Be sure to test the integration after setup.
