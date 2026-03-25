from typing import List, Optional
from datetime import datetime
from backend.extensions import db
from backend.infrastructure.entities.models import Soggetto as SoggettoModel, Ruolo as RuoloModel, SoggettoRuolo as SoggettoRuoloModel, Indirizzo as IndirizzoModel, SoggettoIndirizzo as SoggettoIndirizzoModel, Contatto as ContattoModel, SoggettoContatto as SoggettoContattoModel
from backend.domain.entities.models import (
    Soggetto, Ruolo, RuoloAssegnato,
    IndirizzoValue, SoggettoIndirizzo,
    ContattoValue, SoggettoContatto
)


class SoggettoRepository:
    def __init__(self):
        self.model = SoggettoModel

    def get_by_id(self, soggetto_id: int) -> Optional[Soggetto]:
        model = self.model.query.get(soggetto_id)
        if not model:
            return None
        return self._to_domain(model)

    def get_by_codice(self, tenant_id: int, codice: str) -> Optional[Soggetto]:
        model = self.model.query.filter_by(tenant_id=tenant_id, codice=codice).first()
        if not model:
            return None
        return self._to_domain(model)

    def get_by_tenant(self, tenant_id: int, skip: int = 0, limit: int = 100) -> List[Soggetto]:
        models = self.model.query.filter_by(tenant_id=tenant_id).offset(skip).limit(limit).all()
        return [self._to_domain(m) for m in models]

    def create(self, domain: Soggetto) -> Soggetto:
        model = self.model(
            codice=domain.codice,
            tipo_soggetto=domain.tipo_soggetto,
            nome=domain.nome,
            cognome=domain.cognome,
            ragione_sociale=domain.ragione_sociale,
            partita_iva=domain.partita_iva,
            codice_fiscale=domain.codice_fiscale,
            email_principale=domain.email_principale,
            telefono_principale=domain.telefono_principale,
            website=domain.website,
            stato=domain.stato,
            note=domain.note,
            tags=domain.tags,
            tenant_id=domain.tenant_id,
        )
        db.session.add(model)
        db.session.flush()
        return self._to_domain(model)

    def update(self, domain: Soggetto) -> Soggetto:
        model = self.model.query.get(domain.id)
        if not model:
            raise ValueError(f"Soggetto {domain.id} not found")
        model.codice = domain.codice
        model.tipo_soggetto = domain.tipo_soggetto
        model.nome = domain.nome
        model.cognome = domain.cognome
        model.ragione_sociale = domain.ragione_sociale
        model.partita_iva = domain.partita_iva
        model.codice_fiscale = domain.codice_fiscale
        model.email_principale = domain.email_principale
        model.telefono_principale = domain.telefono_principale
        model.website = domain.website
        model.stato = domain.stato
        model.note = domain.note
        model.tags = domain.tags
        db.session.flush()
        return self._to_domain(model)

    def delete(self, soggetto_id: int) -> None:
        model = self.model.query.get(soggetto_id)
        if model:
            db.session.delete(model)
            db.session.flush()

    def _to_domain(self, model: SoggettoModel) -> Soggetto:
        ruoli = []
        for sr in model.ruoli.all():
            ruoli.append(RuoloAssegnato(
                ruolo_id=sr.ruolo_id,
                ruolo_codice=sr.ruolo.codice if sr.ruolo else '',
                ruolo_nome=sr.ruolo.nome if sr.ruolo else '',
                data_inizio=sr.data_inizio,
                data_fine=sr.data_fine,
                stato=sr.stato,
                parametri=sr.parametri,
            ))

        indirizzi = []
        for si in model.indirizzi.all():
            addr = si.indirizzo
            indirizzi.append(SoggettoIndirizzo(
                indirizzo_id=si.indirizzo_id,
                indirizzo=IndirizzoValue(
                    id=addr.id,
                    denominazione=addr.denominazione,
                    numero_civico=addr.numero_civico,
                    CAP=addr.CAP,
                    città=addr.città,
                    provincia=addr.provincia,
                    regione=addr.regione,
                    nazione=addr.nazione,
                    latitudine=addr.latitudine,
                    longitudine=addr.longitudine,
                    indirizzo_completo=addr.indirizzo_completo,
                    tipo=addr.tipo,
                    geocoded=addr.geocoded,
                    geocoding_data=addr.geocoding_data,
                ) if addr else None,
                tipo_riferimento=si.tipo_riferimento,
                is_preferred=si.is_preferred,
                data_inizio=si.data_inizio,
                data_fine=si.data_fine,
            ))

        contatti = []
        for sc in model.contatti.all():
            cont = sc.contatto
            contatti.append(SoggettoContatto(
                contatto_id=sc.contatto_id,
                contatto=ContattoValue(
                    id=cont.id,
                    canale=cont.canale,
                    valore=cont.valore,
                    tipo_utilizzo=cont.tipo_utilizzo,
                    is_verified=cont.is_verified,
                    verifica_data=cont.verifica_data,
                    is_preferred=cont.is_preferred,
                ) if cont else None,
                tipo_riferimento=sc.tipo_riferimento,
                is_primary=sc.is_primary,
            ))

        return Soggetto(
            id=model.id,
            codice=model.codice,
            tipo_soggetto=model.tipo_soggetto,
            nome=model.nome,
            cognome=model.cognome,
            ragione_sociale=model.ragione_sociale,
            partita_iva=model.partita_iva,
            codice_fiscale=model.codice_fiscale,
            email_principale=model.email_principale,
            telefono_principale=model.telefono_principale,
            website=model.website,
            stato=model.stato,
            note=model.note,
            tags=model.tags,
            tenant_id=model.tenant_id,
            created_at=model.created_at,
            updated_at=model.updated_at,
            ruoli=ruoli,
            indirizzi=indirizzi,
            contatti=contatti,
        )


class RuoloRepository:
    def __init__(self):
        self.model = RuoloModel

    def get_by_id(self, ruolo_id: int) -> Optional[Ruolo]:
        model = self.model.query.get(ruolo_id)
        if not model:
            return None
        return self._to_domain(model)

    def get_by_codice(self, tenant_id: int, codice: str) -> Optional[Ruolo]:
        model = self.model.query.filter_by(tenant_id=tenant_id, codice=codice).first()
        if not model:
            return None
        return self._to_domain(model)

    def get_by_tenant(self, tenant_id: int) -> List[Ruolo]:
        models = self.model.query.filter_by(tenant_id=tenant_id, is_active=True).all()
        return [self._to_domain(m) for m in models]

    def create(self, domain: Ruolo) -> Ruolo:
        model = self.model(
            codice=domain.codice,
            nome=domain.nome,
            descrizione=domain.descrizione,
            categoria=domain.categoria,
            richiede_credito=domain.richiede_credito,
            richiede_contratto=domain.richiede_contratto,
            soggetto_a_fatturazione=domain.soggetto_a_fatturazione,
            is_active=domain.is_active,
            tenant_id=domain.tenant_id,
        )
        db.session.add(model)
        db.session.flush()
        return self._to_domain(model)

    def update(self, domain: Ruolo) -> Ruolo:
        model = self.model.query.get(domain.id)
        if not model:
            raise ValueError(f"Ruolo {domain.id} not found")
        model.codice = domain.codice
        model.nome = domain.nome
        model.descrizione = domain.descrizione
        model.categoria = domain.categoria
        model.richiede_credito = domain.richiede_credito
        model.richiede_contratto = domain.richiede_contratto
        model.soggetto_a_fatturazione = domain.soggetto_a_fatturazione
        model.is_active = domain.is_active
        db.session.flush()
        return self._to_domain(model)

    def delete(self, ruolo_id: int) -> None:
        model = self.model.query.get(ruolo_id)
        if model:
            db.session.delete(model)
            db.session.flush()

    def _to_domain(self, model: RuoloModel) -> Ruolo:
        return Ruolo(
            id=model.id,
            codice=model.codice,
            nome=model.nome,
            descrizione=model.descrizione,
            categoria=model.categoria,
            richiede_credito=model.richiede_credito,
            richiede_contratto=model.richiede_contratto,
            soggetto_a_fatturazione=model.soggetto_a_fatturazione,
            is_active=model.is_active,
            tenant_id=model.tenant_id,
            created_at=model.created_at,
            updated_at=model.updated_at,
        )


class SoggettoRuoloRepository:
    def __init__(self):
        self.model = SoggettoRuoloModel

    def get_by_soggetto(self, soggetto_id: int) -> List[dict]:
        models = self.model.query.filter_by(soggetto_id=soggetto_id).all()
        return [self._to_dict(m) for m in models]

    def create(self, soggetto_id: int, ruolo_id: int, data_inizio=None, data_fine=None, stato='attivo', parametri=None) -> dict:
        model = self.model(
            soggetto_id=soggetto_id,
            ruolo_id=ruolo_id,
            data_inizio=data_inizio,
            data_fine=data_fine,
            stato=stato,
            parametri=parametri,
        )
        db.session.add(model)
        db.session.flush()
        return self._to_dict(model)

    def delete(self, soggetto_id: int, ruolo_id: int) -> None:
        model = self.model.query.filter_by(soggetto_id=soggetto_id, ruolo_id=ruolo_id).first()
        if model:
            db.session.delete(model)
            db.session.flush()

    def _to_dict(self, model: SoggettoRuoloModel) -> dict:
        return {
            'id': model.id,
            'soggetto_id': model.soggetto_id,
            'ruolo_id': model.ruolo_id,
            'ruolo_codice': model.ruolo.codice if model.ruolo else None,
            'ruolo_nome': model.ruolo.nome if model.ruolo else None,
            'data_inizio': model.data_inizio,
            'data_fine': model.data_fine,
            'stato': model.stato,
            'parametri': model.parametri,
        }


class IndirizzoRepository:
    def __init__(self):
        self.model = IndirizzoModel

    def get_by_id(self, indirizzo_id: int) -> Optional[IndirizzoValue]:
        model = self.model.query.get(indirizzo_id)
        if not model:
            return None
        return self._to_domain(model)

    def create(self, domain: IndirizzoValue, tenant_id: int) -> IndirizzoValue:
        model = self.model(
            denominazione=domain.denominazione,
            numero_civico=domain.numero_civico,
            CAP=domain.CAP,
            città=domain.città,
            provincia=domain.provincia,
            regione=domain.regione,
            nazione=domain.nazione,
            latitudine=domain.latitudine,
            longitudine=domain.longitudine,
            indirizzo_completo=domain.indirizzo_completo,
            tipo=domain.tipo,
            geocoded=domain.geocoded,
            geocoding_data=domain.geocoding_data,
            tenant_id=tenant_id,
        )
        db.session.add(model)
        db.session.flush()
        return self._to_domain(model)

    def update(self, domain: IndirizzoValue) -> IndirizzoValue:
        model = self.model.query.get(domain.id)
        if not model:
            raise ValueError(f"Indirizzo {domain.id} not found")
        model.denominazione = domain.denominazione
        model.numero_civico = domain.numero_civico
        model.CAP = domain.CAP
        model.città = domain.città
        model.provincia = domain.provincia
        model.regione = domain.regione
        model.nazione = domain.nazione
        model.latitudine = domain.latitudine
        model.longitudine = domain.longitudine
        model.indirizzo_completo = domain.indirizzo_completo
        model.tipo = domain.tipo
        model.geocoded = domain.geocoded
        model.geocoding_data = domain.geocoding_data
        db.session.flush()
        return self._to_domain(model)

    def delete(self, indirizzo_id: int) -> None:
        model = self.model.query.get(indirizzo_id)
        if model:
            db.session.delete(model)
            db.session.flush()

    def _to_domain(self, model: IndirizzoModel) -> IndirizzoValue:
        return IndirizzoValue(
            id=model.id,
            denominazione=model.denominazione,
            numero_civico=model.numero_civico,
            CAP=model.CAP,
            città=model.città,
            provincia=model.provincia,
            regione=model.regione,
            nazione=model.nazione,
            latitudine=model.latitudine,
            longitudine=model.longitudine,
            indirizzo_completo=model.indirizzo_completo,
            tipo=model.tipo,
            geocoded=model.geocoded,
            geocoding_data=model.geocoding_data,
        )


class ContattoRepository:
    def __init__(self):
        self.model = ContattoModel

    def get_by_id(self, contatto_id: int) -> Optional[ContattoValue]:
        model = self.model.query.get(contatto_id)
        if not model:
            return None
        return self._to_domain(model)

    def create(self, domain: ContattoValue, tenant_id: int) -> ContattoValue:
        model = self.model(
            canale=domain.canale,
            valore=domain.valore,
            tipo_utilizzo=domain.tipo_utilizzo,
            is_verified=domain.is_verified,
            verifica_data=domain.verifica_data,
            is_preferred=domain.is_preferred,
            tenant_id=tenant_id,
        )
        db.session.add(model)
        db.session.flush()
        return self._to_domain(model)

    def update(self, domain: ContattoValue) -> ContattoValue:
        model = self.model.query.get(domain.id)
        if not model:
            raise ValueError(f"Contatto {domain.id} not found")
        model.canale = domain.canale
        model.valore = domain.valore
        model.tipo_utilizzo = domain.tipo_utilizzo
        model.is_verified = domain.is_verified
        model.verifica_data = domain.verifica_data
        model.is_preferred = domain.is_preferred
        db.session.flush()
        return self._to_domain(model)

    def delete(self, contatto_id: int) -> None:
        model = self.model.query.get(contatto_id)
        if model:
            db.session.delete(model)
            db.session.flush()

    def _to_domain(self, model: ContattoModel) -> ContattoValue:
        return ContattoValue(
            id=model.id,
            canale=model.canale,
            valore=model.valore,
            tipo_utilizzo=model.tipo_utilizzo,
            is_verified=model.is_verified,
            verifica_data=model.verifica_data,
            is_preferred=model.is_preferred,
        )
