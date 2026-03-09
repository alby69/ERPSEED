"""
PDF Generation Service per FlaskERP
Supporta: Sales Orders, Invoices, Quotes

Per utilizzare questo servizio:
1. Installare xhtml2pdf: pip install xhtml2pdf
"""
import io
from datetime import datetime
from typing import Optional, Dict, Any
from flask_smorest import abort

# xhtml2pdf sarà importato solo quando necessario per gestire l'errore se non installato
try:
    from xhtml2pdf import pisa
    XHTML2PDF_AVAILABLE = True
except ImportError:
    XHTML2PDF_AVAILABLE = False
    pisa = None

from backend.extensions import db
from backend.core.models.tenant import Tenant


class PDFService:
    """Service per generazione PDF documenti."""

    @staticmethod
    def generate_sales_order(order_id: int, tenant_id: int) -> bytes:
        """
        Genera PDF per ordine di vendita.
        
        Args:
            order_id: ID dell'ordine
            tenant_id: ID del tenant
            
        Returns:
            bytes: PDF in formato binario
        """
        from backend.sales import SalesOrder, SalesOrderLine
        
        order = SalesOrder.query.filter_by(
            id=order_id, 
            tenant_id=tenant_id
        ).first()
        
        if not order:
            raise ValueError("Ordine non trovato")
        
        tenant = Tenant.query.get(tenant_id)
        
        html = PDFService._render_sales_order_html(order, tenant)
        return PDFService._convert_to_pdf(html)
    
    @staticmethod
    def generate_invoice(invoice_id: int, tenant_id: int) -> bytes:
        """
        Genera PDF per fattura.
        
        Args:
            invoice_id: ID della fattura
            tenant_id: ID del tenant
            
        Returns:
            bytes: PDF in formato binario
        """
        from backend.plugins.accounting.models import Invoice, InvoiceLine
        
        invoice = Invoice.query.filter_by(
            id=invoice_id, 
            tenant_id=tenant_id
        ).first()
        
        if not invoice:
            raise ValueError("Fattura non trovata")
        
        tenant = Tenant.query.get(tenant_id)
        
        html = PDFService._render_invoice_html(invoice, tenant)
        return PDFService._convert_to_pdf(html)
    
    @staticmethod
    def generate_quote(quote_id: int, tenant_id: int) -> bytes:
        """
        Genera PDF per preventivo/quote.
        
        Args:
            quote_id: ID del preventivo
            tenant_id: ID del tenant
            
        Returns:
            bytes: PDF in formato binario
        """
        abort(501, message="La generazione di PDF per i preventivi non è ancora implementata.")
    
    @staticmethod
    def _convert_to_pdf(html: str) -> bytes:
        """
        Converte HTML in PDF.
        
        Args:
            html: Stringa HTML
            
        Returns:
            bytes: PDF in formato binario
            
        Raises:
            ImportError: Se xhtml2pdf non è installato
        """
        if not XHTML2PDF_AVAILABLE:
            raise ImportError(
                "xhtml2pdf non è installato. Installalo con: pip install xhtml2pdf"
            )
        
        buffer = io.BytesIO()
        if pisa:
            pisa_status = pisa.CreatePDF(
                html,
                dest=buffer
            )
            
            if pisa_status.err: # type: ignore
                raise Exception("Errore durante la generazione del PDF")
            
        buffer.seek(0)
        return buffer.getvalue()
    
    @staticmethod
    def _format_currency(amount: float, currency: str = 'EUR') -> str:
        """Formatta importo in valuta."""
        return f"€ {amount:,.2f}".replace(',', 'X').replace('.', ',').replace('X', '.')
    
    @staticmethod
    def _render_base_document(
        tenant,
        party,
        document_title: str,
        document_info: Dict[str, str],
        party_title: str,
        lines_header: str,
        lines_body: str,
        totals_html: str,
        notes: Optional[str]
    ) -> str:
        """Renderizza l'HTML di base per un documento."""

        doc_info_html = ""
        for key, value in document_info.items():
            doc_info_html += f"<p><strong>{key}</strong> {value}</p>"

        return f"""
        <!DOCTYPE html>
        <html>
        <head>
            <meta charset="UTF-8">
            <style>
                body {{ font-family: Arial, sans-serif; font-size: 12px; }}
                .header {{ display: flex; justify-content: space-between; margin-bottom: 30px; }}
                .company-info {{ width: 45%; }}
                .document-info {{ width: 45%; text-align: right; }}
                h1 {{ color: #333; margin-bottom: 5px; font-size: 24px; }}
                table {{ width: 100%; border-collapse: collapse; margin: 20px 0; }}
                th {{ background: #f5f5f5; padding: 10px; text-align: left; border-bottom: 2px solid #ddd; }}
                td {{ padding: 10px; border-bottom: 1px solid #eee; }}
                .text-right {{ text-align: right; }}
                .totals {{ margin-top: 20px; text-align: right; }}
                .totals table {{ width: 300px; margin-left: auto; border: none; }}
                .totals td {{ padding: 5px 10px; border: none; }}
                .totals .total-row {{ background: #f5f5f5; font-weight: bold; font-size: 14px; }}
                .footer {{ margin-top: 50px; font-size: 10px; color: #666; text-align: center; }}
                .badge {{ 
                    display: inline-block; padding: 5px 10px; 
                    background: #007bff; color: white; border-radius: 3px; font-size: 11px;
                }}
            </style>
        </head>
        <body>
            <div class="header">
                <div class="company-info">
                    <h2>{tenant.name}</h2>
                    <p>{tenant.address or ''}</p>
                    <p>{tenant.city or ''} {tenant.postal_code or ''}</p>
                    <p>P.IVA: {tenant.vat_number or '-'}</p>
                </div>
                <div class="document-info">
                    <h1>{document_title}</h1>
                    {doc_info_html}
                </div>
            </div>
            
            <div style="margin-bottom: 30px;">
                <h3>{party_title}</h3>
                <p><strong>{party.name}</strong></p>
                <p>{party.address or ''}</p>
                <p>{party.city or ''} {party.postal_code or ''}</p>
                <p>P.IVA: {party.vat_number or '-'}</p>
            </div>
            
            <table><thead>{lines_header}</thead><tbody>{lines_body}</tbody></table>
            <div class="totals">{totals_html}</div>
            {f'<div><h4>Note:</h4><p>{notes}</p></div>' if notes else ''}
            <div class="footer"><p>Documento generato da FlaskERP il {datetime.now().strftime('%d/%m/%Y %H:%M')}</p></div>
        </body>
        </html>
        """

    @staticmethod
    def _render_sales_order_html(order, tenant) -> str:
        """Renderizza HTML per ordine di vendita."""
        
        lines_html = ""
        for line in order.lines:
            lines_html += f"""
            <tr>
                <td>{line.product_name or 'Prodotto'}</td>
                <td class="text-right">{line.quantity}</td>
                <td class="text-right">{PDFService._format_currency(line.unit_price)}</td>
                <td class="text-right">{line.discount_percent}%</td>
                <td class="text-right">{PDFService._format_currency(line.total)}</td>
            </tr>
            """

        document_info = {
            "N.:": order.order_number,
            "Data:": order.order_date.strftime('%d/%m/%Y') if order.order_date else '-',
            "Stato:": f'<span class="badge" style="background: #007bff;">{order.state.upper()}</span>'
        }

        lines_header = """
        <tr>
            <th>Descrizione</th><th class="text-right">Qty</th><th class="text-right">Prezzo</th>
            <th class="text-right">Sconto</th><th class="text-right">Totale</th>
        </tr>
        """

        totals_html = f"""
        <table>
            <tr><td>Subtotale:</td><td>{PDFService._format_currency(order.subtotal)}</td></tr>
            <tr><td>Sconto:</td><td>- {PDFService._format_currency(order.discount_amount)}</td></tr>
            <tr><td>IVA:</td><td>{PDFService._format_currency(order.tax_amount)}</td></tr>
            <tr class="total-row"><td>Totale:</td><td>{PDFService._format_currency(order.total)}</td></tr>
        </table>
        """

        return PDFService._render_base_document(
            tenant=tenant, party=order.party, document_title="ORDINE DI VENDITA",
            document_info=document_info, party_title="Cliente", lines_header=lines_header,
            lines_body=lines_html, totals_html=totals_html, notes=order.note
        )
    
    @staticmethod
    def _render_invoice_html(invoice, tenant) -> str:
        """Renderizza HTML per fattura."""
        
        lines_html = ""
        for line in invoice.lines:
            lines_html += f"""
            <tr>
                <td>{line.product_name or 'Prodotto'}</td>
                <td class="text-right">{line.quantity}</td>
                <td class="text-right">{PDFService._format_currency(line.unit_price)}</td>
                <td class="text-right">{line.tax_percent}%</td>
                <td class="text-right">{PDFService._format_currency(line.total)}</td>
            </tr>
            """
        
        invoice_type = "FATTURA" if invoice.invoice_type == 'out' else "FATTURA RICEVUTA"

        document_info = {
            "N.:": invoice.invoice_number,
            "Data:": invoice.invoice_date.strftime('%d/%m/%Y') if invoice.invoice_date else '-',
            "Stato:": f'<span class="badge" style="background: #28a745;">{invoice.state.upper()}</span>'
        }

        lines_header = """
        <tr>
            <th>Descrizione</th><th class="text-right">Qty</th><th class="text-right">Prezzo</th>
            <th class="text-right">IVA</th><th class="text-right">Totale</th>
        </tr>
        """

        totals_html = f"""
        <table>
            <tr><td>Subtotale:</td><td>{PDFService._format_currency(invoice.subtotal)}</td></tr>
            <tr><td>IVA:</td><td>{PDFService._format_currency(invoice.tax_amount)}</td></tr>
            <tr class="total-row"><td>Totale:</td><td>{PDFService._format_currency(invoice.total)}</td></tr>
        </table>
        """

        return PDFService._render_base_document(
            tenant=tenant, party=invoice.party, document_title=invoice_type,
            document_info=document_info, party_title="Cliente/Fornitore", lines_header=lines_header,
            lines_body=lines_html, totals_html=totals_html, notes=invoice.note
        )
    
    @staticmethod
    def _render_quote_html(quote, tenant) -> str:
        """Renderizza HTML per preventivo."""
        
        lines_html = ""
        for line in quote.lines:
            lines_html += f"""
            <tr>
                <td>{line.product_name or 'Prodotto'}</td>
                <td class="text-right">{line.quantity}</td>
                <td class="text-right">{PDFService._format_currency(line.unit_price)}</td>
                <td class="text-right">{line.discount_percent}%</td>
                <td class="text-right">{PDFService._format_currency(line.total)}</td>
            </tr>
            """

        document_info = {
            "N.:": quote.quote_number,
            "Data:": quote.quote_date.strftime('%d/%m/%Y') if quote.quote_date else '-',
            "Valido fino:": quote.valid_until.strftime('%d/%m/%Y') if quote.valid_until else '-',
            "Stato:": f'<span class="badge" style="background: #ffc107; color: #333;">{quote.state.upper()}</span>'
        }

        lines_header = """
        <tr>
            <th>Descrizione</th><th class="text-right">Qty</th><th class="text-right">Prezzo</th>
            <th class="text-right">Sconto</th><th class="text-right">Totale</th>
        </tr>
        """

        totals_html = f"""
        <table>
            <tr><td>Subtotale:</td><td>{PDFService._format_currency(quote.subtotal)}</td></tr>
            <tr><td>Sconto:</td><td>- {PDFService._format_currency(quote.discount_amount)}</td></tr>
            <tr><td>IVA:</td><td>{PDFService._format_currency(quote.tax_amount)}</td></tr>
            <tr class="total-row"><td>Totale:</td><td>{PDFService._format_currency(quote.total)}</td></tr>
        </table>
        """

        return PDFService._render_base_document(
            tenant=tenant, party=quote.party, document_title="PREVENTIVO",
            document_info=document_info, party_title="Cliente", lines_header=lines_header,
            lines_body=lines_html, totals_html=totals_html, notes=quote.note
        )
