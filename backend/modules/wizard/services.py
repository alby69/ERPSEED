"""
Wizard Services for Domain Analysis & ERP Provisioning.
"""
import json
import logging
from typing import Dict, Any, List

from backend.extensions import db
from backend.modules.builder.service import get_builder_service
from backend.models import SysModel, SysField
from backend.modules.wizard.models import WizardSession
from backend.modules.ai.service import ai_service
from backend.cli.scaffold import scaffold_module

logger = logging.getLogger(__name__)


class DomainAnalysisService:
    """Analyzes questionnaire answers and natural language input to generate candidate ER schemas."""

    def analyze_domain(self, payload: Dict[str, Any]) -> Dict[str, Any]:
        company_name = payload.get("company_name", "Mia Azienda")
        industry = payload.get("industry", "Generico")
        has_inventory = payload.get("has_inventory", True)
        has_purchases = payload.get("has_purchases", True)
        has_projects = payload.get("has_projects", False)
        custom_description = payload.get("custom_description", "").strip()

        # Base modules and entities based on toggles
        modules = ["entities", "products", "sales"]
        suggested_entities = []

        if has_inventory:
            modules.append("inventory")
        if has_purchases:
            modules.append("purchases")
        if has_projects:
            modules.append("projects")
            modules.append("timesheets")

        # Core base candidate entities
        suggested_entities.append({
            "name": "Customer",
            "table": "customers",
            "title": "Clienti",
            "fields": [
                {"name": "company_name", "type": "string", "title": "Ragione Sociale", "required": True},
                {"name": "vat_number", "type": "string", "title": "Partita IVA", "required": False},
                {"name": "email", "type": "string", "title": "Email", "required": False}
            ]
        })

        suggested_entities.append({
            "name": "Product",
            "table": "products",
            "title": "Prodotti / Servizi",
            "fields": [
                {"name": "code", "type": "string", "title": "Codice Prodotto", "required": True},
                {"name": "name", "type": "string", "title": "Nome Prodotto", "required": True},
                {"name": "unit_price", "type": "decimal", "title": "Prezzo Unitario", "required": True}
            ]
        })

        # Parse custom open description using AI Assistant if provided
        if custom_description:
            ai_suggested = self._extract_custom_entities_via_ai(custom_description)
            if ai_suggested:
                suggested_entities.extend(ai_suggested)

        return {
            "company_name": company_name,
            "industry": industry,
            "modules": modules,
            "entities": suggested_entities
        }

    def _extract_custom_entities_via_ai(self, description: str) -> List[Dict[str, Any]]:
        """Invokes LLM with strict system prompt to extract entities from open text."""
        prompt = f"""Estrai entità aziendali personalizzate dal seguente testo descrittivo.
Testo: "{description}"

Rispondi TASSATIVAMENTE in formato JSON valido aderente a questo schema:
[
  {{
    "name": "NomeEntitaSingoloInInglese",
    "table": "nome_tabella_plurale_in_inglese",
    "title": "Titolo Visuale In Italiano",
    "fields": [
      {{"name": "nome_campo_snake_case", "type": "string|integer|decimal|date|boolean", "title": "Label Campo", "required": true|false}}
    ]
  }}
]
Se nel testo sono menzionati veicoli, flotta, contratti, licenze, noleggi, cantieri o asset speciali, crea l'entità corrispondente con i campi principali."""

        try:
            res = ai_service.generate_erp_config(user_request=prompt, projectId=1)
            if res.get("success") and "config" in res and isinstance(res["config"], dict):
                models = res["config"].get("models", [])
                entities = []
                for m in models:
                    entities.append({
                        "name": m.get("name", "CustomEntity"),
                        "table": m.get("table", "custom_entities"),
                        "title": m.get("title") or m.get("name", "Entità Personalizzata"),
                        "fields": m.get("fields", [])
                    })
                return entities
        except Exception as e:
            logger.warning(f"AI entity extraction failed, using fallback parsing: {e}")

        # Basic rule-based fallback if AI is unavailable or fails
        entities = []
        desc_lower = description.lower()
        if "furgon" in desc_lower or "veicol" in desc_lower or "flott" in desc_lower:
            entities.append({
                "name": "Vehicle",
                "table": "vehicles",
                "title": "Veicoli e Flotta",
                "fields": [
                    {"name": "license_plate", "type": "string", "title": "Targa", "required": True},
                    {"name": "model_name", "type": "string", "title": "Modello", "required": True},
                    {"name": "maintenance_status", "type": "string", "title": "Stato Manutenzione", "required": False}
                ]
            })
        if "nolegg" in desc_lower or "affitt" in desc_lower:
            entities.append({
                "name": "RentalContract",
                "table": "rental_contracts",
                "title": "Contratti di Noleggio",
                "fields": [
                    {"name": "contract_code", "type": "string", "title": "Codice Contratto", "required": True},
                    {"name": "start_date", "type": "date", "title": "Data Inizio", "required": True},
                    {"name": "end_date", "type": "date", "title": "Data Fine", "required": False},
                    {"name": "daily_rate", "type": "decimal", "title": "Tariffa Giornaliera", "required": False}
                ]
            })

        return entities


class WizardProvisioningService:
    """Provisions SQLAlchemy dynamic metadata and modules based on domain_spec.yaml / JSON."""

    def __init__(self):
        self.builder_service = get_builder_service()

    def provision_domain(self, domain_spec: Dict[str, Any], project_id: int = 1, tenant_id: int = 1) -> Dict[str, Any]:
        created_models = []
        entities = domain_spec.get("entities", [])

        for entity in entities:
            table_name = entity.get("table") or entity.get("name").lower()
            title = entity.get("title") or entity.get("name")

            # Create or find SysModel metadata
            existing_model = SysModel.query.filter_by(projectId=project_id, technical_name=table_name).first()
            if existing_model:
                sys_model = existing_model
            else:
                sys_model = self.builder_service.create_model(
                    projectId=project_id,
                    name=table_name,
                    title=title,
                    description=f"Generato da ERP Wizard per {domain_spec.get('company_name', 'ERPSeed')}"
                )

            # Create fields
            for field in entity.get("fields", []):
                existing_field = SysField.query.filter_by(modelId=sys_model.id, name=field["name"]).first()
                if not existing_field:
                    self.builder_service.create_field(
                        modelId=sys_model.id,
                        name=field["name"],
                        field_type=field.get("type", "string"),
                        title=field.get("title", field["name"]),
                        required=field.get("required", False)
                    )

            created_models.append({
                "id": sys_model.id,
                "name": sys_model.name,
                "technical_name": sys_model.technical_name
            })

        db.session.commit()

        return {
            "success": True,
            "message": f"Dominio provisionato con successo per '{domain_spec.get('company_name', 'Mia Azienda')}'",
            "modules_enabled": domain_spec.get("modules", []),
            "models_created": created_models
        }


domain_analysis_service = DomainAnalysisService()
wizard_provisioning_service = WizardProvisioningService()
