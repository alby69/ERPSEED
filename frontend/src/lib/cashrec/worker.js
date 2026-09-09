import { JSReconciliationEngine } from './engine.js';
import { JSExcelReporter } from './reporter.js';
import { robustCurrencyParser, parseItalianDate, parseCSVText } from './parser.js';
import * as XLSX from 'xlsx';

self.onmessage = async function(e) {
    const { fileData, fileName, config } = e.data;

    try {
        self.postMessage({ status: 'progress', percent: 10, message: 'Parsing del file in corso...' });

        let rows = [];
        const isCSV = fileName.toLowerCase().endsWith('.csv');

        if (isCSV) {
            const text = new TextDecoder("utf-8").decode(fileData);
            rows = parseCSVText(text);
        } else {
            const workbook = XLSX.read(fileData, { type: 'array', cellDates: true });
            const firstSheetName = workbook.SheetNames[0];
            const worksheet = workbook.Sheets[firstSheetName];
            rows = XLSX.utils.sheet_to_json(worksheet, { defval: "" });
        }

        if (!rows || rows.length === 0) {
            throw new Error("Il file caricato non contiene dati validi.");
        }

        self.postMessage({ status: 'progress', percent: 30, message: 'Preparazione dati e normalizzazione...' });

        // Normalizzazione colonne
        const mapping = config.column_mapping || { "Data Reg.": "Date", "Dare": "Debit", "Avere": "Credit" };
        const dateCol = Object.keys(mapping).find(k => mapping[k] === "Date") || "Data Reg.";
        const debitCol = Object.keys(mapping).find(k => mapping[k] === "Debit") || "Dare";
        const creditCol = Object.keys(mapping).find(k => mapping[k] === "Credit") || "Avere";

        const processedRows = rows.map((r, idx) => {
            const dVal = r[dateCol] || r["Data"] || r["Date"] || r["Data Reg."];
            const parsedDate = parseItalianDate(dVal);
            const debitVal = robustCurrencyParser(r[debitCol] || r["Dare"] || r["Debit"]);
            const creditVal = robustCurrencyParser(r[creditCol] || r["Avere"] || r["Credit"]);

            return {
                ...r,
                __row_id: idx + 1,
                Date: parsedDate,
                Debit: debitVal,
                Credit: creditVal
            };
        });

        self.postMessage({ status: 'progress', percent: 40, message: 'Esecuzione algoritmo di riconciliazione...' });

        const engine = new JSReconciliationEngine({
            ...config,
            progressCallback: (pct, msg) => {
                self.postMessage({ status: 'progress', percent: 40 + Math.round(pct * 0.4), message: msg });
            }
        });

        engine.run(processedRows);

        self.postMessage({ status: 'progress', percent: 85, message: 'Generazione report Excel...' });

        const reporter = new JSExcelReporter(engine, processedRows);
        const reportBlob = await reporter.generateReport((pct, msg) => {
            self.postMessage({ status: 'progress', percent: 85 + Math.round((pct - 82) * 0.15), message: msg });
        });

        const reportArrayBuffer = await reportBlob.arrayBuffer();

        self.postMessage({
            status: 'complete',
            result: {
                matches: engine.matches,
                stats: {
                    total_rows: processedRows.length,
                    debit_rows: engine.debit_df.length,
                    credit_rows: engine.credit_df.length,
                    matched_count: engine.matches.length,
                    total_anomalies: engine.matches.filter(m => m.anomaly_type).length
                },
                reportBuffer: reportArrayBuffer
            }
        }, [reportArrayBuffer]);

    } catch (error) {
        self.postMessage({ status: 'error', error: error.message || String(error) });
    }
};
