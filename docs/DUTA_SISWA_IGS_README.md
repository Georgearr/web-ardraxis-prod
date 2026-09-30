# Documentation: Duta Siswa IGS 2026 Recruitment Platform

Official Student Ambassador Recruitment Platform for **OSIS SMA Ignatius Global School (IGS)**.
Target URL: `https://osissmaigs.com/dutasmaigs`

---

## Architecture Overview

```text
Student (Browser)
   │
   ├── Upload certificates & videos to personal cloud storage (Google Drive, YouTube, OneDrive, Dropbox, etc.)
   ├── Copy shareable link (Anyone with the link can view)
   │
   ▼
Fill Multi-step Form & Paste URLs (/dutasmaigs)
   │
   ▼
POST /dutasmaigs/api/submit (JSON payload)
   │
   ▼
Flask Backend (duta_bp blueprint in routes/duta.py)
   ├── Validate text input & essay paragraph count (max 3)
   ├── Validate HTTP/HTTPS URLs (Certificates & Talent Video)
   ├── Generate Application ID (IGS-DUTA-2026-XXXX)
   │
   ▼
Google Sheets API (Applications worksheet using DUTA_ credentials)
   └── Append row with status "Submitted"
   │
   ▼
Return success JSON with Application ID
```

---

## 1. Setup Environment Variables

Add the following namespaced environment variables to your `.env` file in the project root:

```env
# ============================================================
# DUTA SISWA IGS 2026
# ============================================================

DUTA_CLIENT_EMAIL=your-service-account@your-project.iam.gserviceaccount.com
DUTA_PRIVATE_KEY="-----BEGIN PRIVATE KEY-----\nyour_private_key_here\n-----END PRIVATE KEY-----"
DUTA_GOOGLE_SHEETS_ID=1AbCdEfGhIjKlMnOpQrStUvWxYz0123456789
```

> **Note**:
> - `DUTA_CLIENT_EMAIL`: Google Cloud service account email reserved for Duta Siswa IGS.
> - `DUTA_PRIVATE_KEY`: Private key string (safe `\n` newline handling supported).
> - `DUTA_GOOGLE_SHEETS_ID`: Spreadsheet ID for storing Duta Siswa pendaftaran data. If omitted, the system looks for `"Duta Siswa IGS — Pendaftaran"`.

---

## 2. Google Cloud & Google Sheets Setup Guide

1. **Create Google Cloud Project**: Go to [Google Cloud Console](https://console.cloud.google.com/).
2. **Enable APIs**:
   - Enable **Google Sheets API**.
   - Enable **Google Drive API** (optional, required if accessing restricted drive files).
3. **Create Service Account**:
   - Navigate to **IAM & Admin** > **Service Accounts**.
   - Click **Create Service Account**.
   - Download the JSON Key file, or copy `client_email` and `private_key` into `.env` as `DUTA_CLIENT_EMAIL` and `DUTA_PRIVATE_KEY`.
4. **Create Google Spreadsheet**:
   - Title: `Duta Siswa IGS — Pendaftaran`
   - Worksheet Name: `Applications`
   - Share the spreadsheet with the `DUTA_CLIENT_EMAIL` as **Editor**.

---

## 3. Google Sheets Header Structure

The `Applications` sheet uses the following 13 columns (automatically initialized on first submission if empty):

| Column Index | Header Name | Description |
|---|---|---|
| A | `application_id` | Auto-generated ID (`IGS-DUTA-2026-0001`) |
| B | `submitted_at` | Timestamp in `YYYY-MM-DD HH:MM:SS` (Asia/Jakarta) |
| C | `full_name` | Full name of applicant |
| D | `class` | Class text input (e.g. `XI-2`, `X-1`, `XII IPA 1`) |
| E | `vision_mission` | Vision & Mission text (max 1000 chars) |
| F | `programs` | JSON array string of Work Programs |
| G | `motivation_letter` | Essay (max 3 paragraphs) |
| H | `has_experience` | Experience toggle (`Ya` / `Tidak`) |
| I | `experiences` | Details of prior experiences |
| J | `certificate_urls` | JSON array string of Certificate links |
| K | `talent_video_urls` | JSON array string of Talent Video links |
| L | `commitment` | Commitment confirmation (`Ya, saya yakin.`) |
| M | `status` | Default status: `Submitted` |

---

## 4. Local Testing & Verification

1. Run Flask app locally:
   ```bash
   python main.py
   ```
2. Open browser:
   `http://localhost:5000/dutasmaigs`
3. Navigate through the 8 steps:
   - Test Motivation Letter paragraph validation (> 3 paragraphs error alert).
   - Test dynamic program addition/deletion.
   - Test dynamic certificate & video link preview buttons `[Open Video ↗]`.
   - Test final Review page and section `Edit` buttons.
   - Submit and check Application ID badge (`IGS-DUTA-2026-0001`).
