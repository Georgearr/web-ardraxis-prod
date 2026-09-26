/**
 * ====================================================================
 * GOOGLE APPS SCRIPT — JALUR UNDANGAN OSIS SMA IGS MAYOR
 * ====================================================================
 * 
 * PANDUAN PEMASANGAN (STEP-BY-STEP):
 * 1. Buka Google Spreadsheet tujuan Anda (Spreadsheet Jalur Undangan Mayor).
 * 2. Di menu atas spreadsheet, klik: Ekstensi (Extensions) > Apps Script.
 * 3. Hapus semua baris kode default yang ada di editor Apps Script.
 * 4. Salin (copy) dan tempelkan (paste) seluruh isi file kode.gs ini.
 * 5. Klik ikon Simpan (Save / Ctrl+S atau Cmd+S).
 * 6. Jalankan Inisialisasi Sheet:
 *    - Pada dropdown fungsi di samping tombol Run/Debug, pilih fungsi: setupSheets
 *    - Klik tombol Jalankan (Run).
 *    - Muncul pop-up izin akses:
 *      * Klik 'Tinjau Izin' (Review Permissions)
 *      * Pilih akun Google Anda
 *      * Klik 'Lanjutan' (Advanced) di kiri bawah
 *      * Klik 'Buka ... (tidak aman)' / 'Go to ... (unsafe)'
 *      * Klik 'Izinkan' (Allow)
 *    - Tunggu beberapa detik hingga Execution completed.
 *    - Kembali ke spreadsheet Anda: Tab "Semua" dan 13 tab Sekbid sudah dibuat otomatis dengan header rapi!
 * 7. Deploy sebagai Web App:
 *    - Di pojok kanan atas Apps Script, klik tombol biru: Deploy > New deployment (Penerapan baru).
 *    - Klik ikon gerigi (Select type) > pilih: Web app.
 *    - Deskripsi: Jalur Undangan Mayor (atau bebas).
 *    - Execute as (Jalankan sebagai): Me (email Anda).  <-- PENTING!
 *    - Who has access (Yang memiliki akses): Anyone (Siapa saja). <-- PENTING!
 *    - Klik Deploy.
 *    - Salin "Web app URL" (URL yang berakhiran /exec).
 * 8. Sambungkan ke Website:
 *    - Buka file: config/recruitment_jalurundangan_mayor.json
 *    - Tempel URL tadi ke properti: "apps_script_url"
 *    - Simpan file. Selesai!
 * ====================================================================
 */

// Header kolom spreadsheet
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

// Pemetaan ID sekbid ke nama sheet / tab
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

/**
 * Inisialisasi awal seluruh tab sheet dan header
 * Jalankan fungsi ini sekali dari menu Run di Apps Script
 */
function setupSheets() {
  const ss = SpreadsheetApp.getActiveSpreadsheet();

  // 1. Buat sheet rekapitulasi utama "Semua"
  ensureSheet_(ss, "Semua");

  // 2. Buat sheet untuk masing-masing Sekbid
  Object.keys(SEKBID_SHEETS).forEach(function (id) {
    ensureSheet_(ss, SEKBID_SHEETS[id]);
  });

  // Hapus tab bawaan Sheet1 jika masih kosong
  const defaultSheet = ss.getSheetByName("Sheet1");
  if (defaultSheet && defaultSheet.getLastRow() === 0 && ss.getSheets().length > 1) {
    try {
      ss.deleteSheet(defaultSheet);
    } catch (err) {
      // Lewati jika tidak bisa dihapus
    }
  }
}

/**
 * Handle POST request saat formulir dikirim dari website
 */
function doPost(e) {
  try {
    const data = parseBody_(e);
    const ss = SpreadsheetApp.getActiveSpreadsheet();
    const row = buildRow_(data);
    const ids = normalizeIds_(data.sekbid_ids || data.sekbid || []);

    // 1. Simpan ke sheet "Semua"
    ensureSheet_(ss, "Semua").appendRow(row);

    // 2. Simpan juga ke masing-masing sheet Sekbid yang dipilih
    ids.forEach(function (id) {
      const sheetName = SEKBID_SHEETS[id] || String(id).substring(0, 50);
      ensureSheet_(ss, sheetName).appendRow(row);
    });

    return json_({
      success: true,
      message: "Pendaftaran berhasil disimpan ke spreadsheet"
    });
  } catch (err) {
    return json_({
      success: false,
      message: "Terjadi kesalahan di Google Apps Script: " + String(err)
    });
  }
}

/**
 * Handle GET request untuk cek status / kesehatan endpoint
 */
function doGet(e) {
  return json_({
    success: true,
    message: "Endpoint Jalur Undangan OSIS Mayor aktif dan siap menerima data"
  });
}

/**
 * Parsing data dari POST request (JSON payload / parameter form)
 */
function parseBody_(e) {
  if (!e) return {};
  if (e.postData && e.postData.contents) {
    const raw = e.postData.contents;
    try {
      return JSON.parse(raw);
    } catch (err) {
      const params = e.parameter || {};
      if (params.payload) {
        return JSON.parse(params.payload);
      }
      return params;
    }
  }
  return e.parameter || {};
}

/**
 * Normalisasi id sekbid ke dalam format Array
 */
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

/**
 * Konversi data pendaftar menjadi 1 baris kolom spreadsheet
 */
function buildRow_(data) {
  return [
    data.timestamp || new Date(),
    data.jalur || "Undangan",
    data.sekolah || "SMA Mayor (Jalur Undangan)",
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

/**
 * Membuat tab sheet jika belum ada, dan memberikan styling header rapi
 */
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
    const firstRowValues = sheet.getRange(1, 1, 1, HEADERS.length).getValues()[0];
    empty = !firstRowValues || firstRowValues.every(function (cell) { return cell === ""; });
  }

  if (empty) {
    const headerRange = sheet.getRange(1, 1, 1, HEADERS.length);
    headerRange.setValues([HEADERS]);
    headerRange.setFontWeight("bold");
    headerRange.setBackground("#1a365d"); // Warna biru navy formal
    headerRange.setFontColor("#ffffff");  // Teks putih
    headerRange.setHorizontalAlignment("center");
    sheet.setFrozenRows(1);

    // Otomatis sesuaikan lebar kolom
    for (let c = 1; c <= HEADERS.length; c++) {
      sheet.autoResizeColumn(c);
    }
  }

  return sheet;
}

/**
 * Helper JSON response
 */
function json_(obj) {
  return ContentService.createTextOutput(JSON.stringify(obj))
    .setMimeType(ContentService.MimeType.JSON);
}
