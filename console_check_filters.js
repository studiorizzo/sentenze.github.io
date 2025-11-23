// ========================================
// SCRIPT PER CONSOLE BROWSER
// ========================================
// Copia e incolla questo script nella console del browser quando sei su:
// https://www.italgiure.giustizia.it/sncass/
//
// Lo script mostra tutti i filtri disponibili e i filtri attualmente applicati
// ========================================

console.log("🔍 ANALISI FILTRI ITALGIURE\n" + "=".repeat(80));

// 1. FILTRI ARCHIVIO (kind)
console.log("\n📚 ARCHIVI SENTENZE (kind):");
console.log("-".repeat(80));
const archiveFilters = document.querySelectorAll('tr[id*="[kind]"]');
archiveFilters.forEach(row => {
    const id = row.getAttribute('id');
    const text = row.querySelector('td.idxRow.rowb')?.textContent.trim();
    const hiddenValue = row.querySelector('span[style*="display:none"]')?.textContent;
    const isActive = row.style.backgroundColor === 'rgb(240, 240, 240)';
    console.log(`  ${isActive ? '✓' : ' '} ID: ${id.padEnd(15)} | Valore: ${(hiddenValue || 'N/A').padEnd(10)} | Testo: ${text}`);
});

// 2. FILTRI SEZIONE (szdec)
console.log("\n🏛️  SEZIONI (szdec):");
console.log("-".repeat(80));
const sectionFilters = document.querySelectorAll('tr[id*="[szdec]"]');
sectionFilters.forEach(row => {
    const id = row.getAttribute('id');
    const text = row.querySelector('td.idxRow.rowb')?.textContent.trim();
    const hiddenValue = row.querySelector('span[style*="display:none"]')?.textContent;
    const isActive = row.style.backgroundColor === 'rgb(240, 240, 240)';
    console.log(`  ${isActive ? '✓' : ' '} ID: ${id.padEnd(15)} | Valore: ${(hiddenValue || 'N/A').padEnd(10)} | Testo: ${text}`);
});

// 3. VALORI INPUT NASCOSTI (filtri applicati)
console.log("\n⚙️  FILTRI ATTUALMENTE APPLICATI:");
console.log("-".repeat(80));
const kindInput = document.querySelector('input[name="[kind]"]');
const szdecInput = document.querySelector('input[name="[szdec]"]');
const annoInput = document.querySelector('input[name="[anno]"]');

console.log(`  ARCHIVIO [kind]:  ${kindInput?.value || 'NESSUNO'}`);
console.log(`  SEZIONE [szdec]:  ${szdecInput?.value || 'NESSUNO'}`);
console.log(`  ANNO [anno]:      ${annoInput?.value || 'NESSUNO'}`);

// 4. QUERY DI RICERCA
console.log("\n🔎 QUERY DI RICERCA:");
console.log("-".repeat(80));
const startQuery = document.querySelector('input#startquery');
console.log(`  Start Query: ${startQuery?.value || 'N/A'}`);

// 5. TOTALE DOCUMENTI
console.log("\n📊 TOTALE DOCUMENTI:");
console.log("-".repeat(80));
const totCount = document.querySelector('#totCount .tot');
console.log(`  Totale: ${totCount?.textContent.trim() || 'N/A'}`);

// 6. XPATH CORRETTI DA USARE
console.log("\n✅ XPATH DA USARE NEL CODICE PYTHON:");
console.log("-".repeat(80));
console.log('  CIVILE:  \'//tr[@id="1.[kind]"]\'');
console.log('  QUINTA:  \'//tr[@id="5.[szdec]"]\'  (ID=5, non 4!)');

console.log("\n" + "=".repeat(80));
console.log("✅ Analisi completata!");
