// Google Apps Script for waitlist capture.
// 1) Create a Google Sheet.
// 2) Extensions -> Apps Script -> paste this file.
// 3) Update SPREADSHEET_ID and SHEET_NAME.
// 4) Deploy -> New deployment -> Web app.
//    - Execute as: Me
//    - Who has access: Anyone
// 5) Copy the Web App URL and set it as WAITLIST_WEBHOOK_URL in Vercel.

const SPREADSHEET_ID = "PUT_YOUR_SHEET_ID_HERE";
const SHEET_NAME = "Waitlist";

function doPost(e) {
  try {
    const payload = JSON.parse(e.postData.contents);
    const email = payload.email || "";
    const saasUrl = payload.saas_url || "";
    const source = payload.source || "waitlist";
    const timestamp = new Date().toISOString();

    const ss = SpreadsheetApp.openById(SPREADSHEET_ID);
    const sheet = ss.getSheetByName(SHEET_NAME) || ss.insertSheet(SHEET_NAME);

    if (sheet.getLastRow() === 0) {
      sheet.appendRow(["timestamp", "email", "saas_url", "source"]);
    }

    sheet.appendRow([timestamp, email, saasUrl, source]);

    return ContentService
      .createTextOutput(JSON.stringify({ ok: true }))
      .setMimeType(ContentService.MimeType.JSON);
  } catch (err) {
    return ContentService
      .createTextOutput(JSON.stringify({ ok: false, error: String(err) }))
      .setMimeType(ContentService.MimeType.JSON);
  }
}
