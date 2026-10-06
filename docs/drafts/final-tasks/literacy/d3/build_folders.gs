/**
 * 成果物3の引き継ぎフォルダを学生ごとに作る（教員のアカウントの Google Apps Script。パソコンで実行）。
 * 【未実行】まだ一度も動かしていない。本番の前に、学生役の個人アカウント1つで作って、
 *  スマホから「名前の変更・フォルダへの移動・共有の変更」が編集者でできるかを必ず確かめる。
 *
 * 準備: ドライブに「成果物3_材料」フォルダを作り、次を上げておく
 *   data/ の CSV（make.py で作ったもの。番号ごと）と folder/ の画像・txt
 * 使い方: MATERIAL_ID・PARENT_ID・ROLES・STUDENTS を書き換えて buildAll を実行
 */
const MATERIAL_ID = '成果物3_材料フォルダのID';
const PARENT_ID = '学生のフォルダを入れる親フォルダのID';
const ROLES = { koshi: 'koshi.yaku@example.com', insatsu: 'insatsu.yaku@example.com' };
const STUDENTS = [ ['07', 'student07@example.com'] ];  // [番号, 学生のGoogleアカウント]

function fileByName_(folder, name) {
  const it = folder.getFilesByName(name);
  if (!it.hasNext()) throw new Error('材料がない: ' + name);
  return it.next();
}

function sheetFromCsv_(folder, name, csvFile) {
  const rows = Utilities.parseCsv(csvFile.getBlob().getDataAsString('UTF-8'));
  const ss = SpreadsheetApp.create(name);
  ss.getSheets()[0].getRange(1, 1, rows.length, rows[0].length).setNumberFormat('@').setValues(rows);
  const f = DriveApp.getFileById(ss.getId());
  f.moveTo(folder);
  return f;
}

function docFromTxt_(folder, name, text) {
  const doc = DocumentApp.create(name);
  doc.getBody().setText(text);
  doc.saveAndClose();
  const f = DriveApp.getFileById(doc.getId());
  f.moveTo(folder);
  return f;
}

function buildOne_(no, student) {
  const mat = DriveApp.getFolderById(MATERIAL_ID);
  const root = DriveApp.getFolderById(PARENT_ID).createFolder('成果物3_' + no + '_引き継ぎ');
  const csv = (n) => fileByName_(mat, n);
  sheetFromCsv_(root, '申込一覧', csv('申込-' + no + '-1116.csv'));
  sheetFromCsv_(root, '申込一覧_最終版', csv('申込-' + no + '-1110.csv'));
  sheetFromCsv_(root, '申込一覧_最終版 のコピー', csv('申込-' + no + '-1110.csv'));
  sheetFromCsv_(root, '申込一覧(古い)', csv('申込-' + no + '-1103.csv'));
  sheetFromCsv_(root, '参加者名簿', csv('名簿-' + no + '.csv')).addViewer(ROLES.insatsu);   // 罠
  const txt = (n) => fileByName_(mat, n).getBlob().getDataAsString('UTF-8');
  docFromTxt_(root, '案内文_最終', txt('案内文_最終.txt')).addEditor(ROLES.koshi);          // 罠
  docFromTxt_(root, '案内文_下書き', txt('案内文_下書き.txt'));
  docFromTxt_(root, '案内文_下書き_修正版', txt('案内文_下書き_修正版.txt')).addViewer(ROLES.koshi);
  docFromTxt_(root, '運用メモ', txt('運用メモ.txt').replace(/NN/g, no));
  fileByName_(mat, 'チラシ.png').makeCopy('チラシ.png', root)
    .setSharing(DriveApp.Access.ANYONE_WITH_LINK, DriveApp.Permission.VIEW);                 // 罠
  fileByName_(mat, 'チラシ_修正.png').makeCopy('チラシ_修正.png', root);
  fileByName_(mat, '会場の地図.png').makeCopy('会場の地図.png', root);
  const photos = root.createFolder('下見写真');
  for (let i = 1; i <= 6; i++) {
    const n = 'IMG_310' + i + '.jpg';
    fileByName_(mat, n).makeCopy(n, photos);
  }
  root.addEditor(student);
  return root.getUrl();
}

function buildAll() {
  STUDENTS.forEach(([no, mail]) => Logger.log(no + ' ' + buildOne_(no, mail)));
}
