/**
 * ESTRATTORE AUTOCOMPLETE CASSAZIONE - VERSIONE SOLR
 * 
 * Usa l'endpoint Solr reale trovato: isapi/hc.dll/sn.solr/sn-collection/select
 */

(async function() {
    console.log('='.repeat(70));
    console.log('🎯 ESTRATTORE AUTOCOMPLETE - SENTENZE CASSAZIONE (SOLR)');
    console.log('='.repeat(70));
    
    const BASE_URL = window.location.origin + '/sncass/';
    const SOLR_ENDPOINT = 'isapi/hc.dll/sn.solr/sn-collection/select?app.suggester';
    const DELAY = 200; // millisecondi tra richieste
    
    console.log(`\nBase URL: ${BASE_URL}`);
    console.log(`Endpoint Solr: ${SOLR_ENDPOINT}\n`);
    
    // Funzione per fare richieste Solr
    async function fetchSolrSuggestions(searchTerm) {
        const url = BASE_URL + SOLR_ENDPOINT;
        
        // Costruisci la query Solr
        const solrQuery = `{!boost b=score}kind:"key" AND key:${searchTerm}*`;
        const params = new URLSearchParams({
            rows: '100', // Aumentato per catturare più risultati
            q: solrQuery,
            wt: 'json',
            indent: 'off',
            fl: 'key'
        });
        
        try {
            const response = await fetch(url, {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/x-www-form-urlencoded',
                    'Accept': 'application/json',
                    'X-Requested-With': 'XMLHttpRequest'
                },
                body: params.toString()
            });
            
            if (response.ok) {
                const data = await response.json();
                
                if (data.response && data.response.docs) {
                    const suggestions = data.response.docs
                        .map(doc => doc.key ? doc.key[0] : null)
                        .filter(k => k !== null);
                    
                    return {
                        suggestions: suggestions,
                        total: data.response.numFound
                    };
                }
            } else {
                console.warn(`❌ Errore ${response.status} per term="${searchTerm}"`);
            }
            
            return { suggestions: [], total: 0 };
            
        } catch (error) {
            console.error(`❌ Errore per term="${searchTerm}":`, error.message);
            return { suggestions: [], total: 0 };
        }
    }
    
    // Funzione per attendere
    function sleep(ms) {
        return new Promise(resolve => setTimeout(resolve, ms));
    }
    
    // Funzione principale di estrazione
    async function extractAllSuggestions() {
        console.log('🚀 Inizio estrazione completa...\n');
        console.log('Strategia: Ricerca per lettera singola (a-z) + bigrammi comuni\n');
        
        const allSuggestions = new Set();
        const suggestionsByPrefix = {};
        const stats = {
            totalQueries: 0,
            totalUnique: 0,
            byPrefix: {}
        };
        
        // Fase 1: Caratteri singoli (lettere + numeri)
        console.log('📋 Fase 1: Caratteri singoli (a-z, 0-9)\n');
        const letters = 'abcdefghijklmnopqrstuvwxyz0123456789'.split('');
        
        for (let i = 0; i < letters.length; i++) {
            const letter = letters[i];
            stats.totalQueries++;
            
            const result = await fetchSolrSuggestions(letter);
            
            if (result.suggestions.length > 0) {
                console.log(`[${i + 1}/${letters.length}] '${letter}' → ${result.suggestions.length} suggerimenti (${result.total} totali in DB)`);
                
                suggestionsByPrefix[letter] = result.suggestions;
                stats.byPrefix[letter] = result.total;
                
                result.suggestions.forEach(s => allSuggestions.add(s));
            } else {
                console.log(`[${i + 1}/${letters.length}] '${letter}' → Nessuno`);
            }
            
            await sleep(DELAY);
        }
        
        console.log(`\n✓ Fase 1 completata: ${allSuggestions.size} suggerimenti unici trovati`);
        
        // Fase 2: Bigrammi comuni per catturare più termini
        console.log('\n📋 Fase 2: Bigrammi e combinazioni comuni\n');
        const bigrams = [
            // Combinazioni comuni in italiano legale
            'ab', 'ac', 'ad', 'ag', 'al', 'an', 'ap', 'ar', 'as', 'at', 'av',
            'ca', 'ce', 'ci', 'co', 'con', 'cu',
            'da', 'de', 'di', 'do',
            'ec', 'ed', 'ef', 'el', 'em', 'en', 'er', 'es', 'ev',
            'fa', 'fe', 'fi', 'fo', 'fr',
            'ga', 'ge', 'gi', 'gr', 'gu',
            'il', 'im', 'in', 'ip', 'ir', 'is',
            'la', 'le', 'li', 'lo',
            'ma', 'me', 'mi', 'mo', 'mu',
            'na', 'ne', 'no', 'nu',
            'ob', 'oc', 'of', 'og', 'ol', 'om', 'on', 'op', 'or', 'os',
            'pa', 'pe', 'pi', 'po', 'pr', 'pu',
            'qu',
            're', 'ri', 'ro', 'ru',
            'sa', 'sc', 'se', 'si', 'so', 'sp', 'st', 'su',
            'ta', 'te', 'ti', 'to', 'tr', 'tu',
            'ub', 'uc', 'uf', 'ul', 'um', 'un', 'ur', 'us',
            've', 'vi', 'vo',
            'za', 'zo',
            // Combinazioni con numeri comuni in ricerche sentenze
            '19', '20', '21', '10', '11', '12', '13', '14', '15', '16', '17', '18',
            '200', '201', '202', '199', '198',
            // Combinazioni numero-lettera
            '1a', '2a', '3a', '1b', '2b',
            // Articoli e riferimenti normativi comuni
            'art', 'art.', 'cod', 'dpr', 'dlg', 'cpc', 'cpp'
        ];
        
        let newFound = 0;
        
        for (let i = 0; i < bigrams.length; i++) {
            const bigram = bigrams[i];
            stats.totalQueries++;
            
            const result = await fetchSolrSuggestions(bigram);
            
            if (result.suggestions.length > 0) {
                let newInThisQuery = 0;
                
                suggestionsByPrefix[bigram] = result.suggestions;
                stats.byPrefix[bigram] = result.total;
                
                result.suggestions.forEach(s => {
                    if (!allSuggestions.has(s)) {
                        allSuggestions.add(s);
                        newInThisQuery++;
                        newFound++;
                    }
                });
                
                console.log(`[${i + 1}/${bigrams.length}] '${bigram}' → +${newInThisQuery} nuovi (${result.suggestions.length} totali, ${result.total} in DB)`);
            } else {
                console.log(`[${i + 1}/${bigrams.length}] '${bigram}' → Nessuno`);
            }
            
            await sleep(DELAY);
        }
        
        console.log(`\n✓ Fase 2 completata: +${newFound} nuovi suggerimenti`);
        
        stats.totalUnique = allSuggestions.size;
        
        return {
            suggestions: Array.from(allSuggestions).sort(),
            byPrefix: suggestionsByPrefix,
            stats: stats
        };
    }
    
    // Funzione per scaricare i risultati
    function downloadJSON(data, filename) {
        const blob = new Blob([JSON.stringify(data, null, 2)], { type: 'application/json' });
        const url = URL.createObjectURL(blob);
        const a = document.createElement('a');
        a.href = url;
        a.download = filename;
        document.body.appendChild(a);
        a.click();
        document.body.removeChild(a);
        URL.revokeObjectURL(url);
        console.log(`✓ Scaricato: ${filename}`);
    }
    
    function downloadText(text, filename) {
        const blob = new Blob([text], { type: 'text/plain' });
        const url = URL.createObjectURL(blob);
        const a = document.createElement('a');
        a.href = url;
        a.download = filename;
        document.body.appendChild(a);
        a.click();
        document.body.removeChild(a);
        URL.revokeObjectURL(url);
        console.log(`✓ Scaricato: ${filename}`);
    }
    
    // ESEGUI ESTRAZIONE
    const results = await extractAllSuggestions();
    
    // Prepara dati finali
    const finalData = {
        metadata: {
            timestamp: new Date().toISOString(),
            date: new Date().toLocaleString('it-IT'),
            url: window.location.href,
            source: 'Solr autocomplete - Sentenze Cassazione',
            total_suggestions: results.stats.totalUnique,
            total_queries: results.stats.totalQueries
        },
        suggestions: results.suggestions,
        statistics: results.stats
    };
    
    const detailedData = {
        metadata: finalData.metadata,
        suggestions_by_prefix: results.byPrefix,
        statistics: results.stats
    };
    
    // Scarica i file
    console.log('\n' + '='.repeat(70));
    console.log('📥 Salvataggio risultati...\n');
    
    downloadJSON(finalData, 'cassazione_autocomplete_solr.json');
    downloadJSON(detailedData, 'cassazione_autocomplete_detailed.json');
    downloadText(results.suggestions.join('\n'), 'cassazione_keywords.txt');
    
    // Statistiche finali
    console.log('\n' + '='.repeat(70));
    console.log('✅ ESTRAZIONE COMPLETATA CON SUCCESSO!');
    console.log('='.repeat(70));
    console.log(`\n📊 STATISTICHE:`);
    console.log(`   Query eseguite:        ${results.stats.totalQueries}`);
    console.log(`   Suggerimenti unici:    ${results.stats.totalUnique}`);
    console.log(`   Prefissi con risultati: ${Object.keys(results.byPrefix).length}`);
    
    // Top 20 suggerimenti più comuni (alfabeticamente primi)
    console.log(`\n📋 Primi 20 suggerimenti (alfabetici):`);
    results.suggestions.slice(0, 20).forEach((s, i) => {
        console.log(`   ${(i + 1).toString().padStart(2, ' ')}. ${s}`);
    });
    
    if (results.suggestions.length > 20) {
        console.log(`   ... e altri ${results.suggestions.length - 20} suggerimenti`);
    }
    
    console.log(`\n✅ File scaricati:`);
    console.log(`   - cassazione_autocomplete_solr.json`);
    console.log(`   - cassazione_autocomplete_detailed.json`);
    console.log(`   - cassazione_keywords.txt`);
    
    console.log(`\n💡 I dati sono disponibili anche in:`);
    console.log(`   window.cassazioneData`);
    
    console.log('\n' + '='.repeat(70) + '\n');
    
    // Salva in variabile globale
    window.cassazioneData = finalData;
    window.cassazioneDetailed = detailedData;
    
    return finalData;
    
})().catch(error => {
    console.error('❌ ERRORE FATALE:', error);
    console.error('Stack trace:', error.stack);
});
