# Zoom Transcript Organizer

Automatically organizes **Zoom Cloud** meeting transcripts and emails them to
`joshua@demanddesigner.com` via the **Gmail API**. It runs as a **GitHub
Action** on a schedule, so it keeps working even when no one is logged in.

## What it does

On each run the automation:

1. Authenticates to Zoom (Server-to-Server OAuth) and lists cloud recordings
   from the last `LOOKBACK_DAYS` days.
2. For every meeting that has a completed `VTT` transcript it has not already
   processed, it downloads the transcript.
3. Cleans it up: parses the WEBVTT, merges consecutive lines from the same
   speaker, adds timestamps, and lists participants.
4. *(Optional)* If `ANTHROPIC_API_KEY` is set, it adds a **Summary**, **Key
   Decisions**, and **Action Items by Person** section using Claude.
5. Emails the organized result (HTML + plain text) via Gmail.
6. Records what it sent in `.github/zoom-transcript-state.json` so nothing is
   ever emailed twice.

## Files

| File | Purpose |
| --- | --- |
| `automation/organize_zoom_transcripts.py` | The script. |
| `automation/requirements.txt` | Only dependency is `requests`. |
| `.github/workflows/zoom-transcript-organizer.yml` | Schedule + manual trigger. |
| `.github/zoom-transcript-state.json` | Tracks processed transcripts. |

## One-time setup

You need to create two app credentials and add them as repository secrets.

### 1. Zoom Server-to-Server OAuth app

1. Go to <https://marketplace.zoom.us/> → **Develop → Build App → Server-to-Server OAuth**.
2. Note the **Account ID**, **Client ID**, and **Client Secret**.
3. Under **Scopes**, add:
   - `cloud_recording:read:list_user_recordings` (read recordings)
   - `cloud_recording:read:recording` (download files)
   - *(legacy scope names: `recording:read`)*
4. **Activate** the app.
5. Make sure **cloud recording with audio transcript** is enabled in your Zoom
   account settings (Settings → Recording → *Create audio transcript*).

### 2. Gmail API credentials (OAuth refresh token)

1. In [Google Cloud Console](https://console.cloud.google.com/): create/select a
   project → **APIs & Services → Library → enable "Gmail API"**.
2. **APIs & Services → Credentials → Create Credentials → OAuth client ID →
   Desktop app.** Save the **Client ID** and **Client Secret**.
3. Add your Google account as a **Test user** on the OAuth consent screen.
4. Generate a refresh token with the `https://www.googleapis.com/auth/gmail.send`
   scope. The quickest way is the [OAuth 2.0 Playground](https://developers.google.com/oauthplayground/):
   - Click the gear (⚙) → check **Use your own OAuth credentials** → paste your
     Client ID/Secret.
   - In Step 1, enter scope `https://www.googleapis.com/auth/gmail.send` →
     **Authorize APIs** → sign in.
   - In Step 2, click **Exchange authorization code for tokens** → copy the
     **Refresh token**.

### 3. Add repository secrets

Repo → **Settings → Secrets and variables → Actions → New repository secret**:

| Secret | Value |
| --- | --- |
| `ZOOM_ACCOUNT_ID` | Zoom Account ID |
| `ZOOM_CLIENT_ID` | Zoom Client ID |
| `ZOOM_CLIENT_SECRET` | Zoom Client Secret |
| `GMAIL_CLIENT_ID` | Google OAuth Client ID |
| `GMAIL_CLIENT_SECRET` | Google OAuth Client Secret |
| `GMAIL_REFRESH_TOKEN` | Refresh token from the Playground |
| `GMAIL_SENDER` | *(optional)* the Gmail address that authorized the token |
| `ANTHROPIC_API_KEY` | *(optional)* enables AI summary + action items |

Optional **Variables** (same screen, *Variables* tab) to override defaults:

| Variable | Default | Meaning |
| --- | --- | --- |
| `TRANSCRIPT_RECIPIENT` | `joshua@demanddesigner.com` | Where to email |
| `ZOOM_USER_ID` | `me` | Whose recordings to scan (use an email for other users) |
| `LOOKBACK_DAYS` | `7` | How far back to scan each run |

## Running it

- **Automatically:** every 2 hours via the cron schedule in the workflow.
  Change the `cron:` line to adjust frequency (it is in UTC).
- **Manually:** repo → **Actions → Organize Zoom Transcripts → Run workflow**.
  You can set a custom lookback for a one-off backfill.

## Testing locally

```bash
pip install -r automation/requirements.txt
export ZOOM_ACCOUNT_ID=... ZOOM_CLIENT_ID=... ZOOM_CLIENT_SECRET=...
export GMAIL_CLIENT_ID=... GMAIL_CLIENT_SECRET=... GMAIL_REFRESH_TOKEN=...
export TRANSCRIPT_RECIPIENT=joshua@demanddesigner.com
python automation/organize_zoom_transcripts.py
```

## Notes & limits

- Zoom only produces transcripts for **cloud** recordings, and they appear a few
  minutes *after* the recording finishes processing. The 2-hour schedule plus a
  7-day lookback gives plenty of slack so nothing is missed.
- De-duplication is keyed on the meeting UUID + transcript file ID, persisted in
  `.github/zoom-transcript-state.json`. Deleting that file would re-send
  everything in the lookback window.
- Without `ANTHROPIC_API_KEY` you still get a clean, speaker-organized
  transcript — just no AI summary/action-items section.
