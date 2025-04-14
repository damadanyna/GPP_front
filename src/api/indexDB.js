// indexedDB.js
import { openDB } from 'idb';

const DB_NAME = 'encoursDB';
const STORE_NAME = 'encoursStore';

export async function initDB() {
  return openDB(DB_NAME, 1, {
    upgrade(db) {
      if (!db.objectStoreNames.contains(STORE_NAME)) {
        db.createObjectStore(STORE_NAME);
      }
    },
  });
}

export async function saveData(key, data) {
  const db = await initDB();
  await db.put(STORE_NAME, data, key);
}

export async function getData(key) {
  const db = await initDB();
  return db.get(STORE_NAME, key);
}

export async function clearData() {
  const db = await initDB();
  return db.clear(STORE_NAME);
}

export async function getAllData() {
  const db = await initDB();
  const allData = [];
  const tx = db.transaction(STORE_NAME, 'readonly');
  const store = tx.objectStore(STORE_NAME);

  let cursor = await store.openCursor();
  while (cursor) {
    allData.push(...cursor.value); // déstructure si value est un tableau
    cursor = await cursor.continue();
  }

  return allData;
}
