import React from 'react';
import { Drawer, Typography, Card, Divider } from 'antd';
import { useLocation } from 'react-router-dom';

const { Title, Paragraph, Text } = Typography;

const knowledgeBase = {
  '/sales': {
    title: 'Guida Gestione Vendite & Ordini',
    description: 'Il modulo Vendite gestisce il ciclo di vita delle offerte e degli ordini cliente.',
    steps: [
      'Crea un nuovo ordine selezionando il cliente (Soggetto) e inserendo i prodotti.',
      'Conferma l\'ordine per riservare la merce a magazzino e generare la bozza di fattura.',
      'Usa i filtri avanzati o la vista Kanban per monitorare lo stato di evasione.'
    ]
  },
  '/products': {
    title: 'Guida Catalogo Prodotti',
    description: 'Gestione del master data dei prodotti, prezzi di listino, aliquote IVA e scorte.',
    steps: [
      'Definisci il codice SKU univoco e la categoria del prodotto.',
      'Configura la tracciabilità tramite lotti o numeri di serie se applicabile.',
      'Imposta il punto di riordino per automatizzare le richieste d\'acquisto.'
    ]
  },
  '/invoices': {
    title: 'Guida Fatturazione & Contabilità',
    description: 'Gestione delle fatture attive/passive e trasmissione della fattura elettronica.',
    steps: [
      'Genera la fattura direttamente dall\'ordine di vendita confermato.',
      'Verifica la correttezza del codice SDI o PEC del cliente prima dell\'invio.',
      'Invia il file XML al Sistema di Interscambio (SDI).'
    ]
  }
};

export default function KnowledgeDrawer({ open, onClose }) {
  const location = useLocation();
  const currentPath = location.pathname;

  const doc = knowledgeBase[currentPath] || {
    title: 'Documentazione Operativa ERPSEED',
    description: 'Piattaforma ERP low-code e modulare multi-tenant.',
    steps: [
      'Naviga tra i moduli utilizzando il menu laterale o la Command Palette (Ctrl+K).',
      'Usa la vista Kanban o Tabella per gestire i dati operative in modo flessibile.',
      'Consulta la guida contestuale in ogni sezione per istruzioni dettagliate.'
    ]
  };

  return (
    <Drawer
      title={doc.title}
      placement="right"
      width={400}
      onClose={onClose}
      open={open}
      destroyOnClose
    >
      <Paragraph style={{ fontSize: 15, color: '#595959' }}>
        {doc.description}
      </Paragraph>

      <Divider />

      <Title level={5}>Procedura Operativa Standard (SOP)</Title>
      <Card size="small" style={{ backgroundColor: '#fafafa' }}>
        <ol style={{ paddingLeft: 18, margin: 0 }}>
          {doc.steps.map((step, idx) => (
            <li key={idx} style={{ marginBottom: 8 }}>
              <Text>{step}</Text>
            </li>
          ))}
        </ol>
      </Card>
    </Drawer>
  );
}
