from datetime import date
from decimal import Decimal, ROUND_HALF_UP
from lxml import etree

NS = "http://ivaservizi.agenziaentrate.gov.it/docs/xsd/fatture/v1.2"
NSP = f"{{{NS}}}"

SCHEMA_VERSION = "FPR12"


def _fmt(num):
    d = Decimal(str(num))
    return str(d.quantize(Decimal("0.01"), rounding=ROUND_HALF_UP))


def _taxable_from_total(total, tax_percent):
    if not tax_percent:
        return total or 0
    return round((total or 0) / (1 + tax_percent / 100), 2)


def generate_fattura_elettronica(invoice, lines, cedente, cessionario, tenant):
    root = etree.Element(f"{NSP}FatturaElettronica", attrib={
        "versione": SCHEMA_VERSION,
        "xmlns": NS,
    })

    # -- FatturaElettronicaHeader --
    header = etree.SubElement(root, f"{NSP}FatturaElettronicaHeader")

    # DatiTrasmissione
    dati_trasm = etree.SubElement(header, f"{NSP}DatiTrasmissione")
    etree.SubElement(dati_trasm, f"{NSP}IdTrasmittente")
    id_tras = dati_trasm.find(f"{NSP}IdTrasmittente")
    etree.SubElement(id_tras, f"{NSP}IdPaese").text = "IT"
    vat = (cedente.get("partita_iva") or "").replace(" ", "")
    etree.SubElement(id_tras, f"{NSP}IdCodice").text = vat
    progressivo_invio = f"{tenant.id:05d}_{invoice.id:05d}"
    etree.SubElement(dati_trasm, f"{NSP}ProgressivoInvio").text = progressivo_invio
    etree.SubElement(dati_trasm, f"{NSP}FormatoTrasmissione").text = SCHEMA_FORMATO = "FPR12"
    codice_dest = (cessionario.get("partita_iva") or cessionario.get("codice_fiscale") or "0000000").replace(" ", "")
    if tenant.country and tenant.country != "IT":
        etree.SubElement(dati_trasm, f"{NSP}CodiceDestinatario").text = "XXXXXXX"
        etree.SubElement(dati_trasm, f"{NSP}Telefono").text = tenant.phone or ""
    else:
        etree.SubElement(dati_trasm, f"{NSP}CodiceDestinatario").text = (codice_dest[:7] if len(codice_dest) >= 7 else codice_dest.zfill(7))

    # CedentePrestatore
    ced_prest = etree.SubElement(header, f"{NSP}CedentePrestatore")
    _add_dati_anagrafici(ced_prest, cedente, "RF01")
    _add_sede(ced_prest, tenant)

    # CessionarioCommittente
    ces_comm = etree.SubElement(header, f"{NSP}CessionarioCommittente")
    _add_dati_anagrafici(ces_comm, cessionario, "RF02")
    _add_sede(ces_comm, cessionario)

    # DatiGenerali
    body = etree.SubElement(root, f"{NSP}FatturaElettronicaBody")

    dati_gen = etree.SubElement(body, f"{NSP}DatiGenerali")
    doc = etree.SubElement(dati_gen, f"{NSP}DatiGeneraliDocumento")
    tipo = "TD01" if invoice.invoice_type == "AR" else "TD04"
    etree.SubElement(doc, f"{NSP}TipoDocumento").text = tipo
    etree.SubElement(doc, f"{NSP}Divisa").text = "EUR"
    etree.SubElement(doc, f"{NSP}Data").text = (
        invoice.date.isoformat() if hasattr(invoice.date, "isoformat") else str(invoice.date)
    )
    etree.SubElement(doc, f"{NSP}Numero").text = invoice.invoice_number or str(invoice.id)
    etree.SubElement(doc, f"{NSP}ImportoTotaleDocumento").text = _fmt(invoice.total or 0)

    # DatiRiassuntivo (righe IVA raggruppate per aliquota)
    vat_groups = {}
    for line in lines:
        rate = line.get("tax_percent") or 0
        vat_groups.setdefault(rate, {"imponibile": 0, "imposta": 0})
        line_total = (line.get("quantity") or 0) * (line.get("unit_price") or 0)
        vat_groups[rate]["imponibile"] += _taxable_from_total(line_total, rate)
        vat_groups[rate]["imposta"] += line_total - _taxable_from_total(line_total, rate)

    dati_riep = etree.SubElement(body, f"{NSP}DatiBeniServizi")
    for rate in sorted(vat_groups.keys()):
        riga = etree.SubElement(dati_riep, f"{NSP}DatiRiepilogo")
        etree.SubElement(riga, f"{NSP}AliquotaIVA").text = _fmt(rate)
        etree.SubElement(riga, f"{NSP}ImponibileImporto").text = _fmt(vat_groups[rate]["imponibile"])
        etree.SubElement(riga, f"{NSP}Imposta").text = _fmt(vat_groups[rate]["imposta"])
        if rate == 0:
            etree.SubElement(riga, f"{NSP}Natura").text = "N2.2"

    # DettaglioLinee
    for line in lines:
        dettaglio = etree.SubElement(dati_riep, f"{NSP}DettaglioLinee")
        etree.SubElement(dettaglio, f"{NSP}NumeroLinea").text = str(line.get("_num", 1))
        desc = line.get("description") or ""
        etree.SubElement(dettaglio, f"{NSP}Descrizione").text = desc
        etree.SubElement(dettaglio, f"{NSP}Quantita").text = _fmt(line.get("quantity") or 1)
        etree.SubElement(dettaglio, f"{NSP}PrezzoUnitario").text = _fmt(line.get("unit_price") or 0)
        etree.SubElement(dettaglio, f"{NSP}PrezzoTotale").text = _fmt(
            (line.get("quantity") or 1) * (line.get("unit_price") or 0)
        )
        etree.SubElement(dettaglio, f"{NSP}AliquotaIVA").text = _fmt(line.get("tax_percent") or 0)

    # DatiPagamento
    pag = etree.SubElement(body, f"{NSP}DatiPagamento")
    etree.SubElement(pag, f"{NSP}CondizioniPagamento").text = "TP02"
    dett_pag = etree.SubElement(pag, f"{NSP}DettaglioPagamento")
    scad = invoice.due_date or invoice.date
    if hasattr(scad, "isoformat"):
        scad_str = scad.isoformat()
    else:
        scad_str = str(scad)
    etree.SubElement(dett_pag, f"{NSP}DataScadenzaPagamento").text = scad_str
    etree.SubElement(dett_pag, f"{NSP}ImportoPagamento").text = _fmt(invoice.total or 0)

    return root


def _add_dati_anagrafici(parent, soggetto, ruolo):
    container = etree.SubElement(parent, f"{NSP}DatiAnagrafici")
    id_fisc = etree.SubElement(container, f"{NSP}IdFiscaleIVA")
    paese = (soggetto.get("nazione") or "IT")[:2]
    etree.SubElement(id_fisc, f"{NSP}IdPaese").text = paese
    vat = (soggetto.get("partita_iva") or "").replace(" ", "")
    etree.SubElement(id_fisc, f"{NSP}IdCodice").text = vat or "00000000000"
    cf = (soggetto.get("codice_fiscale") or "").replace(" ", "")
    if cf:
        etree.SubElement(container, f"{NSP}CodiceFiscale").text = cf
    anag = etree.SubElement(container, f"{NSP}Anagrafica")
    nome = soggetto.get("nome") or ""
    cognome = soggetto.get("cognome") or ""
    rag_soc = soggetto.get("ragione_sociale") or ""
    if rag_soc:
        etree.SubElement(anag, f"{NSP}Denominazione").text = rag_soc
    else:
        etree.SubElement(anag, f"{NSP}Nome").text = nome
        etree.SubElement(anag, f"{NSP}Cognome").text = cognome
    etree.SubElement(container, f"{NSP}RegimeFiscale").text = "RF01"


def _add_sede(parent, source):
    sede = etree.SubElement(parent, f"{NSP}Sede")
    if isinstance(source, dict):
        indirizzo = source.get("indirizzo") or "Via Sede"
        cap = source.get("cap") or "00000"
        comune = source.get("citta") or " "
        prov = source.get("provincia") or "  "
        paese = (source.get("nazione") or "IT")[:2]
    else:
        indirizzo = getattr(source, "address", None) or "Via Sede"
        cap = getattr(source, "postal_code", None) or "00000"
        comune = getattr(source, "city", None) or " "
        prov = getattr(source, "province", None) or "  "
        paese = (getattr(source, "country", None) or "IT")[:2]
    etree.SubElement(sede, f"{NSP}Indirizzo").text = indirizzo
    etree.SubElement(sede, f"{NSP}CAP").text = str(cap)[:5]
    etree.SubElement(sede, f"{NSP}Comune").text = comune
    etree.SubElement(sede, f"{NSP}Provincia").text = str(prov)[:2]
    etree.SubElement(sede, f"{NSP}Nazione").text = paese


def xml_to_string(root):
    return etree.tostring(root, pretty_print=True, xml_declaration=True, encoding="UTF-8").decode("UTF-8")
