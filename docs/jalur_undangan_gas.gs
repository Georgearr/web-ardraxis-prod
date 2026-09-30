/**
 * Jalur Undangan OSIS SMA IGS — Google Apps Script
 *
 * SETUP (lakukan 2x: spreadsheet Mayor & spreadsheet CGC):
 * 1. Buat Google Spreadsheet baru.
 * 2. Extensions → Apps Script → hapus kode default → tempel file ini.
 * 3. Simpan, lalu jalankan fungsi setupSheets() sekali (Run).
 *    Izinkan permission saat diminta.
 * 4. Deploy → New deployment → Type: Web app
 *    - Execute as: Me
 *    - Who has access: Anyone
 * 5. Salin URL Web app ke config JSON:
 *    config/recruitment_jalurundangan_mayor.json → google.apps_script_url
 *    config/recruitment_jalurundangan_cgc.json   → google.apps_script_url
 */

const HEADERS = [
  "Timestamp",
  "Jalur",
  "Sekolah",
  "Nama",
  "Kelas",
  "Pilihan 1",
  "Pilihan 2",
  "Visi Misi",
  "Motivasi",
  "Kelebihan",
  "Kekurangan",
  "Pengalaman Organisasi",
  "Link Google Drive Sertifikat",
  "Skala Prioritas",
  "Link Google Drive Tugas Sekbid",
];

const SEKBID_SHEETS = {
  sub_sekbid_desain_ddv: "Desain-DDV",
  hubungan_masyarakat_dan_publikasi: "Publikasi",
  komunikasi: "Komunikasi",
  sub_sekbid_producer: "Producer",
  sub_sekbid_video_editor: "Editor",
  sub_sekbid_dokumentasi_ddv: "Dokumentasi-DDV",
  sub_sekbid_kreatif_ddv: "Kreatif",
  sosial: "Sosial",
  bela_negara: "Bela-Negara",
  bahasa: "Bahasa",
  apresiasi_seni_dan_olahraga: "Apres",
  multimedia_website: "Web",
  sub_sekbid_illustrator: "Illus",
};

function setupSheets() {
  const ss = SpreadsheetApp.getActiveSpreadsheet();
  ensureSheet_(ss, "Semua");
  Object.keys(SEKBID_SHEETS).forEach(function (id) {
    ensureSheet_(ss, SEKBID_SHEETS[id]);
  });
  const defaultSheet = ss.getSheetByName("Sheet1");
  if (defaultSheet && defaultSheet.getLastRow() === 0 && ss.getSheets().length > 1) {
    try {
      ss.deleteSheet(defaultSheet);
    } catch (err) {}
  }
}

function doPost(e) {
  try {
    const data = parseBody_(e);
    const ss = SpreadsheetApp.getActiveSpreadsheet();
    const row = buildRow_(data);
    const ids = normalizeIds_(data.sekbid_ids || data.sekbid || []);

    ensureSheet_(ss, "Semua").appendRow(row);

    ids.forEach(function (id) {
      const name = SEKBID_SHEETS[id] || String(id).substring(0, 90);
      ensureSheet_(ss, name).appendRow(row);
    });

    return json_({ success: true, message: "Pendaftaran tersimpan" });
  } catch (err) {
    return json_({ success: false, message: String(err) });
  }
}

function doGet() {
  return json_({ success: true, message: "Endpoint Jalur Undangan OSIS aktif" });
}

function parseBody_(e) {
  if (!e || !e.postData || !e.postData.contents) {
    const params = (e && e.parameter) || {};
    if (params.payload) return JSON.parse(params.payload);
    return params;
  }
  const raw = e.postData.contents;
  try {
    return JSON.parse(raw);
  } catch (err) {
    const params = e.parameter || {};
    if (params.payload) return JSON.parse(params.payload);
    return params;
  }
}

function normalizeIds_(value) {
  if (!value) return [];
  if (typeof value === "string") {
    try {
      const parsed = JSON.parse(value);
      if (Array.isArray(parsed)) return parsed;
    } catch (err) {
      return value.split(",").map(function (s) { return s.trim(); }).filter(Boolean);
    }
    return [value];
  }
  if (Array.isArray(value)) return value;
  return [];
}

function buildRow_(data) {
  return [
    data.timestamp || new Date(),
    data.jalur || "Undangan",
    data.sekolah || "",
    data.nama || "",
    data.kelas || "",
    data.pilihan1 || "",
    data.pilihan2 || "",
    data.visi_misi || "",
    data.motivasi || "",
    data.kelebihan || "",
    data.kekurangan || "",
    data.pengalaman || "",
    data.sertifikat_link || "",
    data.prioritas || "",
    data.google_drive_link || "",
  ];
}

function ensureSheet_(ss, name) {
  let sheet = ss.getSheetByName(name);
  if (!sheet) {
    sheet = ss.insertSheet(name);
  }
  const lastRow = sheet.getLastRow();
  let empty = false;
  if (lastRow === 0) {
    empty = true;
  } else {
    const first = sheet.getRange(1, 1, 1, HEADERS.length).getValues()[0];
    empty = !first || first.every(function (cell) { return cell === ""; });
  }
  if (empty) {
    sheet.getRange(1, 1, 1, HEADERS.length).setValues([HEADERS]);
    sheet.getRange(1, 1, 1, HEADERS.length).setFontWeight("bold");
    sheet.getRange(1, 1, 1, HEADERS.length).setBackground("#1a365d");
    sheet.getRange(1, 1, 1, HEADERS.length).setFontColor("#ffffff");
    sheet.setFrozenRows(1);
    for (let c = 1; c <= HEADERS.length; c++) {
      sheet.autoResizeColumn(c);
    }
  }
  return sheet;
}

function json_(obj) {
  return ContentService.createTextOutput(JSON.stringify(obj)).setMimeType(
    ContentService.MimeType.JSON
  );
}
