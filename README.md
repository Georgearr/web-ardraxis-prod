# Recruitment Google Sheets

## Service Account Location

Place your Google Service Account JSON file in **one** of these locations (checked in order):

1. `secrets/google-service-account.json`
2. `config/credentials.json`
3. `credentials.json`

## Connecting Google Sheets

1. Open the target Google Spreadsheet.
2. Click **Share**.
3. Add the Service Account email (from the JSON file, `client_email` field).
4. Give **Editor** permission.

## Configuration

Spreadsheet IDs are already configured in:

- `config/recruitment_sma_mayor.json` → SMA Mayor spreadsheet
- `config/recruitment_sma_cgc.json` → SMA CGC spreadsheet

No other setup is required.
