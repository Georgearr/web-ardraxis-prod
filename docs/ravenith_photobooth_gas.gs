/**
 * Ravenith Photobooth — Google Apps Script
 * Menyajikan daftar foto dari folder Google Drive sebagai JSON.
 *
 * SETUP:
 * 1. Buat folder Drive untuk foto photobooth, upload foto (jpg/png).
 * 2. Salin ID folder dari URL Drive: .../folders/FOLDER_ID_HERE
 * 3. Ganti FOLDER_ID di bawah.
 * 4. Deploy → Web app → Execute as: Me, Who has access: Anyone
 * 5. Salin URL ke .env: RAVENITH_PHOTOBOOTH_GAS_URL=...
 */

const FOLDER_ID = "GANTI_FOLDER_ID_DRIVE_ANDA";

function doGet(e) {
  const action = (e && e.parameter && e.parameter.action) || "list";
  if (action === "list") {
    return jsonResponse(listPhotosFromFolder());
  }
  return jsonResponse({ success: false, photos: [], message: "Action tidak dikenali." });
}

function listPhotosFromFolder() {
  try {
    const folder = DriveApp.getFolderById(FOLDER_ID);
    const files = folder.getFiles();
    const photos = [];
    const imageTypes = ["image/jpeg", "image/png", "image/webp", "image/gif"];

    while (files.hasNext()) {
      const file = files.next();
      const mime = file.getMimeType();
      if (imageTypes.indexOf(mime) === -1) continue;

      const id = file.getId();
      photos.push({
        id: id,
        name: file.getName(),
        url: "https://drive.google.com/thumbnail?id=" + id + "&sz=w1200",
        downloadUrl: "https://drive.google.com/uc?export=download&id=" + id,
      });
    }

    photos.sort(function (a, b) {
      return a.name.localeCompare(b.name);
    });

    return { success: true, photos: photos };
  } catch (err) {
    return {
      success: false,
      photos: [],
      message: "Error: " + err.toString(),
    };
  }
}

function jsonResponse(obj) {
  return ContentService.createTextOutput(JSON.stringify(obj)).setMimeType(
    ContentService.MimeType.JSON
  );
}
