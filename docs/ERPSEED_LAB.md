# ERPSeed Lab

## Laboratorio di Programmazione Python a Basso Costo

---

> *Questo documento descrive come realizzare un laboratorio didattico per la programmazione Python a costi minimi, utilizzando un'architettura client-server basata su thin client e Raspberry Pi, perfetta per la formazione di giovani programmatori nel progetto ERPSeed.*

---

## 📋 Indice

1. [Introduzione](#1-introduzione)
2. [Filosofia del Laboratorio](#2-filosofia-del-laboratorio)
3. [Architettura di Rete](#3-architettura-di-rete)
4. [Scelte Software](#4-scelte-software)
5. [Configurazione Dettagliata](#5-configurazione-dettagliata)
6. [Stima dei Costi](#6-stima-dei-costi)
7. [Pro e Contro](#7-pro-e-contro)
8. [Alternative](#8-alternative)
9. [Roadmap Implementativa](#9-roadmap-implementativa)
10. [Risorse e Riferimenti](#10-risorse-e-riferimenti)

---

## 1. Introduzione

### 1.1 Perché un Laboratorio Python

Il progetto ERPSeed ha bisogno di un luogo fisico dove i giovani possano imparare a programmare in Python e sviluppare competenze tecniche utili per:

- Creare moduli FlaskERP
- Gestire la piattaforma ERPSeed
- Supportare le microimprese locali
- Costruire una carriera nel mondo tech

### 1.2 Problematica dei Costi

Un laboratorio tradizionale con PC potenti ha costi elevati:

| Componente | Costo tradizionale |
|------------|-------------------|
| PC gaming/studio | €800-1.500 ciascuno |
| 10 PC | €8.000-15.000 |
| Manutenzione | €1.000+/anno |
| Aggiornamenti | €2.000+ ogni 3-5 anni |

### 1.3 La Nostra Soluzione

Con un'architettura **thin client** il costo si riduce drasticamente:

| Componente | Costo thin client |
|------------|-------------------|
| Raspberry Pi 4 | €50-80 ciascuno |
| 10 client | €500-800 |
| Server (riciclato) | €200-400 |
| Costo totale | €700-1.200 |

---

## 2. Filosofia del Laboratorio

### 2.1 Principi Fondamentali

```
╔═══════════════════════════════════════════════════════════════════════╗
║              PRINCIPI DEL LABORATORIO ERPSEED                       ║
╠═══════════════════════════════════════════════════════════════════════╣
║                                                                       ║
║   💰 ECONOMICITÀ                                                    ║
║      Hardware minimale, massimo risparmio                             ║
║                                                                       ║
║   🔄 SEMPLICITÀ                                                     ║
║      Facilità di gestione e manutenzione                             ║
║                                                                       ║
║   📚 DIDATTICA                                                      ║
║      Ambienti pronti per l'apprendimento                             ║
║                                                                       ║
║   🌱 CRESCITA                                                       ║
║      Scalabilità per far crescere la community                       ║
║                                                                       ║
║   🔒 SICUREZZA                                                      ║
║      Dati al sicuro, sessioni isolate                                ║
║                                                                       ║
╚═══════════════════════════════════════════════════════════════════════╝
```

### 2.2 Obiettivi Formativi

| Obiettivo | Descrizione |
|-----------|-------------|
| **Python Base** | Sintassi, strutture dati, funzioni |
| **OOP** | Programmazione orientata agli oggetti |
| **Web** | Flask, HTML, CSS, JavaScript |
| **Database** | PostgreSQL, SQL, ORM |
| **Git** | Version control, collaborazione |
| **Progetti Reali** | Sviluppo moduli FlaskERP |

---

## 3. Architettura di Rete

### 3.1 Topologia Client-Server

```
┌─────────────────────────────────────────────────────────────────────────┐
│                    LABORATORIO PYTHON ERPSEED                          │
├─────────────────────────────────────────────────────────────────────────┤
│                                                                         │
│   ┌─────────────────────────────────────────────────────────────┐    │
│   │                       SERVER CENTRALE                         │    │
│   │  ┌─────────────┐  ┌─────────────┐  ┌─────────────┐        │    │
│   │  │   Ubuntu    │  │   Python    │  │   JupyterHub │        │    │
│   │  │   Server    │  │   3.x      │  │   (IDE)     │        │    │
│   │  └─────────────┘  └─────────────┘  └─────────────┘        │    │
│   │  ┌─────────────┐  ┌─────────────┐  ┌─────────────┐        │    │
│   │  │  Docker     │  │   X2Go     │  │   Storage   │        │    │
│   │  │  (ambienti)│  │   Server   │  │   condiviso │        │    │
│   │  └─────────────┘  └─────────────┘  └─────────────┘        │    │
│   └─────────────────────────────────────────────────────────────┘    │
│                              │                                        │
│                              │ LAN 1Gbps                              │
│                              │                                        │
│   ──────────────────────────┼─────────────────────────────          │
│              │               │               │                       │
│              ▼               ▼               ▼                       │
│   ┌─────────────┐    ┌─────────────┐    ┌─────────────┐           │
│   │ Raspberry   │    │   Vecchio   │    │   Thin      │           │
│   │   Pi 4      │    │     PC      │    │   Client    │           │
│   │  (Client)   │    │  (Client)  │    │  (Client)   │           │
│   └─────────────┘    └─────────────┘    └─────────────┘           │
│                                                                         │
└─────────────────────────────────────────────────────────────────────────┘
```

### 3.2 Flusso di Lavoro

```
┌─────────────────────────────────────────────────────────────────────────┐
│                       FLOWS DI LAVORO                                   │
├─────────────────────────────────────────────────────────────────────────┤
│                                                                         │
│   STUDENTE                    SERVER                      STORAGE     │
│   ────────                    ───────                      ──────     │
│                                                                         │
│   1. Accede al client    ──►  2. X2Go/Jupyter                     │
│      (Raspberry Pi/PC)       connessione                               │
│                                      │                                 │
│                                      ▼                                 │
│                              3. Sessione Python                       │
│                                 in container                           │
│                                      │                                 │
│                                      ▼                                 │
│                              4. IDE caricato                         │
│                                 (VS Code/Thonny/Jupyter)              │
│                                      │                                 │
│                                      ▼                                 │
│                              5. Salvataggio file                     │
│                                 ─────────────────► /home/studente     │
│                                                                         │
└─────────────────────────────────────────────────────────────────────────┘
```

### 3.3 Schema di Rete

```
┌─────────────────────────────────────────────────────────────────────────┐
│                         SCHEMA DI RETE                                   │
├─────────────────────────────────────────────────────────────────────────┤
│                                                                         │
│   INTERNET (opzionale)                                                 │
│        │                                                               │
│        │ (per aggiornamenti/backup)                                    │
│        │                                                               │
│   ┌────▼──────────────────────────────────────────────────────┐      │
│   │                     FIREWALL / ROUTER                       │      │
│   │                   (quello della scuola/ufficio)            │      │
│   └──────────────────────────┬───────────────────────────────────┘      │
│                              │                                           │
│                              │ LAN 192.168.1.0/24                       │
│                              │                                           │
│         ┌────────────────────┼────────────────────┐                    │
│         │                    │                    │                    │
│         ▼                    ▼                    ▼                    │
│   ┌───────────┐       ┌───────────┐       ┌───────────┐              │
│   │  Switch   │       │  Server   │       │  Client 1 │              │
│   │  8 porte  │◄────►│  (Linux)  │       │ (RPi/PC)  │              │
│   │  1Gbps    │       └───────────┘       └───────────┘              │
│   │           │              │                                            │
│   └─────┬─────┘              │                                            │
│         │                    │                                            │
│    ┌────┴────┐              │                                            │
│    │         │              │                                            │
│    ▼         ▼              │                                            │
│ ┌──────┐ ┌──────┐          │                                            │
│ │Client│ │Client│ ...      │                                            │
│ │  2   │ │  3   │          │                                            │
│ └──────┘ └──────┘          │                                            │
│                                                                         │
└─────────────────────────────────────────────────────────────────────────┘
```

---

## 4. Scelte Software

### 4.1 Server

| Componente | Scelta | Versione |
|------------|--------|----------|
| **OS** | Ubuntu Server | 24.04 LTS |
| **Python** | pyenv + Python | 3.11+ |
| **Container** | Docker | Latest |
| **Accesso** | X2Go Server | 4.x |
| **IDE** | JupyterHub | 4.x |

### 4.2 Client

| Componente | Scelta | Note |
|------------|--------|------|
| **OS** | Raspberry Pi OS Lite | Senza desktop |
| **Display** | X2Go Client | Connessione RDP leggera |
| **Browser** | Chromium | Per Jupyter |

### 4.3 IDE e Ambienti

```
╔═══════════════════════════════════════════════════════════════════════╗
║               IDE E AMBIENTI CONSIGLIATI                            ║
╠═══════════════════════════════════════════════════════════════════════╣
║                                                                       ║
║   🐍 THONNY (Principianti)                                         ║
║   ═══════════════════════════════                                   ║
║   • IDE semplicissimo, perfetto per imparare                        ║
║   • Debugger integrato                                              ║
║   • Installation: pip install thonny                                ║
║                                                                       ║
║   📊 JUPYTER (Intermedio)                                          ║
║   ══════════════════════════════                                   ║
║   • Notebook interattivi                                           ║
║   • Perfetto per data science                                       ║
║   • Condivisione facile                                             ║
║                                                                       ║
║   💻 VS CODE SERVER (Avanzato)                                     ║
║   ══════════════════════════════                                   ║
║   • IDE professionale                                               ║
║   • Estensioni Python                                               ║
║   • Terminale integrato                                            ║
║                                                                       ║
║   🐛 PYCHARM COMMUNITY (Avanzato)                                   ║
║   ══════════════════════════════                                   ║
║   • IDE completo per Python                                        ║
║   • Ottimo debugging                                                ║
║   • Refactoring avanzato                                            ║
║                                                                       ║
╚═══════════════════════════════════════════════════════════════════════╝
```

### 4.4 Gestione Utenti

| Opzione | Descrizione | Complessità |
|----------|-------------|-------------|
| **Locale** | Utenti Linux locali | Bassa |
| **LDAP** | Directory centralizzata | Media |
| **Active Directory** | Integrazione Windows | Alta |

**Raccomandazione**: Iniziare con utenti locali, passare a LDAP quando si supera i 20 utenti.

---

## 5. Configurazione Dettagliata

### 5.1 Setup Server (Ubuntu 24.04)

```bash
# Aggiornamento sistema
sudo apt update && sudo apt upgrade -y

# Installazione Python e pip
sudo apt install -y python3 python3-pip python3-venv

# Installazione Docker
curl -fsSL https://get.docker.com | sh
sudo usermod -aG docker $USER

# Installazione JupyterHub install j
pipupyterhub notebook jupyterlab

# Installazione X2Go Server
sudo apt install -y x2goserver x2goserver-xsession

# Configurazione rete (IP statico)
sudo nano /etc/netplan/01-netcfg.yaml
```

### 5.2 Setup Container per Studente

```dockerfile
# Dockerfile per ambiente Python didattico
FROM ubuntu:24.04

RUN apt update && apt install -y \
    python3 \
    python3-pip \
    python3-venv \
    git \
    vim \
    thonny \
    && rm -rf /var/lib/apt/lists/*

RUN useradd -m -s /bin/bash studente
USER studente

WORKDIR /home/studente
CMD ["/bin/bash"]
```

### 5.3 Setup Client Raspberry Pi

```bash
# Download Raspberry Pi OS Lite
# https://www.raspberrypi.com/software/operating-systems/

# Installazione su SD con Raspberry Pi Imager

# Aggiornamento
sudo apt update && sudo apt upgrade -y

# Installazione X2Go Client
sudo apt install -y x2goclient

# Configurazione connessione automatica
# (opzionale: boot da rete con PXE)
```

### 5.4 Configurazione X2Go

```
CONFIGURAZIONE X2GO CLIENT
═══════════════════════════════

1. Apri X2Go Client
2. New Session:
   - Session name: Lab Python
   - Host: 192.168.1.100 (IP server)
   - Login: studente1
   - Session type: Custom
   - Command: /usr/bin/startplasma-x11
   
3. Salva e connetti

4. Sul server, installa desktop leggero:
   sudo apt install -y xubuntu-desktop
```

### 5.5 Specifiche del Server

Per far funzionare VS Code Server, JupyterHub e X2Go contemporaneamente, il server deve avere risorse adeguate.

#### 5.5.1 Dimensionamento per Numero di Utenti

```
╔═══════════════════════════════════════════════════════════════════════════════╗
║               SPECIFICHE SERVER PER UTENTI                                 ║
╠═══════════════════════════════════════════════════════════════════════════════╣
║                                                                       ║
║   5 UTENTI (Laboratorio Mini)                                        ║
║   ───────────────────────────────────                                  ║
║   CPU:     Intel i5-4gen (4 core) o equivalente AMD                   ║
║   RAM:     8 GB DDR3/DDR4                                             ║
║   Storage: 256 GB SSD (importante!)                                   ║
║   Costo:   €150-200 (usato) o €300 (nuovo)                           ║
║                                                                       ║
║   10 UTENTI (Laboratorio Standard)                                    ║
║   ─────────────────────────────────────                                ║
║   CPU:     Intel i5-6gen/7gen (6 core) o AMD Ryzen 5                ║
║   RAM:     16 GB DDR4                                                 ║
║   Storage: 500 GB NVMe/SSD                                            ║
║   Costo:   €300-400 (usato) o €500 (nuovo)                           ║
║                                                                       ║
║   20+ UTENTI (Laboratorio Avanzato)                                   ║
║   ──────────────────────────────────────                               ║
║   CPU:     Intel i7/AMD Ryzen 7 (8-16 core)                          ║
║   RAM:     32-64 GB DDR4                                              ║
║   Storage: 1 TB NVMe + backup HDD                                     ║
║   Costo:   €600-800 (usato) o €1.000+ (nuovo)                       ║
║                                                                       ║
╚═══════════════════════════════════════════════════════════════════════╝
```

#### 5.5.2 Componenti Consigliati (Nuovo)

| Componente | Opzione Economica | Opzione Standard | Note |
|------------|------------------|------------------|------|
| **CPU** | Intel i5-12400 (6 core) | Intel i7-12700 (8 core) | ~€150-250 |
| **RAM** | 16 GB DDR4 | 32 GB DDR4 | ~€40-80 |
| **Storage** | 500 GB NVMe | 1 TB NVMe | ~€40-80 |
| **Case** | Mini Tower | Tower | ~€40 |
| **Alimentatore** | 450W 80+ Bronze | 550W 80+ Gold | ~€40-60 |
| **Scheda di rete** | Gigabit integrata | Gigabit integrata | - |
| **TOTALE** | **~€300-350** | **~€500-600** | |

#### 5.5.3 Dove Acquistare (Usato/Refurbished)

| Fonte | Vantaggi | Note |
|-------|----------|-------|
| **Amazon Warehouse** | Garanzia 1 anno | €250-350 per i5 8GB |
| **eBay** | Prezzi bassi | Verificare venditore |
| **Refurbished.it** | Certificati | €300-400 |
| **Mercatino** | Prezzi locali | Controllare stato |
| **Rigenerati** | Testati | €200-350 |

#### 5.5.4 Dove Acquistare (Nuovo)

| Fonte | Note |
|-------|-------|
| **Amazon** | Consegna rapida |
| **PCSpecialist** | Configurabile |
| **SchedaMadre.it** | Componenti italiani |
| **Alternative.it** | Prezzi competitivi |

#### 5.5.5 Configurazione Raccomandata

```
╔═══════════════════════════════════════════════════════════════════════════════╗
║               CONFIGURAZIONE SERVER CONSIGLIATA                            ║
╠═══════════════════════════════════════════════════════════════════════════════╣
║                                                                       ║
║   SERVER PER 10 UTENTI (CONFIGURAZIONE OTTIMALE)                    ║
║   ──────────────────────────────────────────────                      ║
║                                                                       ║
║   Hardware:                                                            ║
║   • CPU: Intel i5-10400 (6 core, 12 thread) - €120                   ║
║   • RAM: 16 GB DDR4 (2x8GB) - €50                                    ║
║   • SSD: 500 GB NVMe - €40                                           ║
║   • Case: Mini Tower - €40                                           ║
║   • PSU: 500W 80+ Bronze - €45                                      ║
║                                                                       ║
║   Totale hardware: ~€295                                              ║
║                                                                       ║
║   Software (gratis):                                                   ║
║   • Ubuntu Server 24.04 LTS (gratis)                                 ║
║   • Docker (gratis)                                                  ║
║   • X2Go Server (gratis)                                            ║
║   • JupyterHub (gratis)                                              ║
║   • VS Code Server (gratis)                                          ║
║                                                                       ║
║   Costo software: €0                                                 ║
║                                                                       ║
╚═══════════════════════════════════════════════════════════════════════╝
```

#### 5.5.6 Alternativa: Raspberry Pi 5 come Server

Per budget veramente limitati, anche Raspberry Pi 5 può fare da server:

| Configurazione | Specifiche | Costo | Note |
|---------------|------------|-------|------|
| **RPi 5 Server** | 8GB RAM, SSD USB3 | ~€130 | Solo per 3-5 utenti leggeri |
| **RPi Cluster** | 3x RPi 5 8GB | ~€350 | Per 10+ utenti |

```
┌─────────────────────────────────────────────────────────────────────────┐
│            RASPBERRY PI 5 COME SERVER (ALTERNATIVA)                  │
├─────────────────────────────────────────────────────────────────────────┤
│                                                                         │
│   Specifiche:                                                          │
│   • Raspberry Pi 5 8GB: €85                                          │
│   • SSD NVMe USB3 500GB: €40                                          │
│   • Alimentatore 27W: €15                                              │
│   • Case con raffreddamento: €15                                      │
│   • Storage case: €10                                                 │
│   ─────────────────────────────────────                                │
│   TOTALE: ~€165                                                       │
│                                                                         │
│   Limitazioni:                                                         │
│   • Performace ridotte rispetto a PC x86                             │
│   • Consigliato per 3-5 utenti                                       │
│   • Ideale per test/learning                                          │
│                                                                         │
└─────────────────────────────────────────────────────────────────────────┘
```

#### 5.5.7 Alternativa Avanzata: Cluster Raspberry Pi con k3s

Per un laboratorio moderno e veramente educativo, un cluster Raspberry Pi rappresenta un'evoluzione significativa rispetto al server tradizionale. Non è solo un modo per risparmiare, ma un'opportunità per far imparare agli studenti competenze molto richieste nel mondo del lavoro: Kubernetes, container orchestration, DevOps e GitOps.

```
┌─────────────────────────────────────────────────────────────────────────┐
│               CLUSTER RASPBERRY PI PER LAB ERPSEED                       │
├─────────────────────────────────────────────────────────────────────────┤
│                                                                         │
│   4 NODI RASPBERRY PI 5 8GB                                            │
│   ────────────────────────────────────                                 │
│                                                                         │
│   ┌─────────┐  ┌─────────┐  ┌─────────┐  ┌─────────┐                │
│   │  Node 1 │  │  Node 2 │  │  Node 3 │  │  Node 4 │                │
│   │(k3s-master)│ │(k3s-master)│ │(k3s-master)│ │(k3s-worker)│       │
│   └─────────┘  └─────────┘  └─────────┘  └─────────┘                │
│       │             │             │             │                       │
│       └─────────────┴─────────────┴─────────────┘                       │
│                             │                                           │
│                    ┌────────▼────────┐                                 │
│                    │   k3s Cluster   │                                 │
│                    │  (Kubernetes)   │                                 │
│                    └────────┬────────┘                                 │
│                             │                                           │
│   Servizi:                  │                                           │
│   ├── JupyterHub            ├──► Traefik (Ingress)                   │
│   ├── VS Code Server       │   (Load Balancer)                      │
│   ├── X2Go Server          │                                           │
│   ├── Nextcloud (opz.)    │                                           │
│   └── Docker Registry      │                                           │
│                                                                         │
└─────────────────────────────────────────────────────────────────────────┘
```

##### Perché un Cluster invece di un Server Singolo

| Aspetto | Server Singolo | Cluster Raspberry Pi |
|---------|---------------|---------------------|
| **Costo** | €300-500 | ~€620 |
| **Ridondanza** | Single point of failure | Se un nodo cade, servizi attivi sugli altri |
| **Approccio educativo** | Server tradizionale | Distribuito, Kubernetes, DevOps |
| **Skills insegnati** | Linux base | Kubernetes, Docker, CI/CD, monitoring |
| **Consumo** | 50-100W | 30-50W totali |
| **Scalabilità** | Limitata | Aggiungi nodi facilmente |
| **Complessità** | Bassa | Media-alta (ma educativa!) |

##### Vantaggi Educativi del Cluster

```
╔═══════════════════════════════════════════════════════════════════════════╗
║               COMPETENZE ACQUISITE CON CLUSTER                      ║
╠═══════════════════════════════════════════════════════════════════════════╣
║                                                                       ║
║   ☸️ KUBERNETES                                                       ║
║   • k3s - Kubernetes leggero specifico per edge/embedded             ║
║   • Pod scheduling e service discovery                               ║
║   • Persistent storage (Longhorn)                                    ║
║   • Ingress controllers (Traefik, NGINX)                            ║
║   • Gestione risorse e limiti                                       ║
║                                                                       ║
║   🔧 DEVOPS                                                          ║
║   • Docker containerization                                          ║
║   • CI/CD pipelines (GitLab CI, ArgoCD)                           ║
║   • Infrastructure as Code (Ansible)                               ║
║   • GitOps con FluxCD                                               ║
║   • Configuration management                                        ║
║                                                                       ║
║   📊 MONITORAGGIO E OSSERVAZIONE                                    ║
║   • Prometheus + Grafana                                            ║
║   • Log management (Loki)                                           ║
║   • Alerting e notifiche                                            ║
║   • Health checks e readiness                                       ║
║                                                                       ║
║   🌐 RETE E INFRASTRUTTURA                                           ║
║   • DNS con Pi-hole (block ads a livello network)                  ║
║   • Reverse proxy con Traefik                                       ║
║   • Firewall e sicurezza network                                    ║
║   • Load balancing                                                  ║
║                                                                       ║
║   💾 STORAGE DISTRIBUITO                                             ║
║   • GlusterFS o Longhorn per storage ridondante                    ║
║   • Backup e disaster recovery                                      ║
║   • NFS/Samba per condivisione file                                 ║
║                                                                           ║
╚═══════════════════════════════════════════════════════════════════════════╝
```

##### Configurazione Hardware Consigliata

| Componente | Qty | Costo Unitario | Totale |
|------------|-----|----------------|--------|
| Raspberry Pi 5 8GB | 4 | €85 | €340 |
| Case con raffreddamento attivo | 4 | €15 | €60 |
| Alimentatori USB-C 45W | 4 | €10 | €40 |
| SSD NVMe 500GB (USB 3.2) | 4 | €30 | €120 |
| Switch 8 porte Gigabit | 1 | €30 | €30 |
| Cavi ethernet Cat6 (1m) | 4 | €5 | €20 |
| MicroSD 32GB (boot) | 4 | €8 | €32 |
| **TOTALE** | | | **~€642** |

##### Software da Installare

```bash
# Installazione k3s (sul nodo master)
curl -sfL https://get.k3s.io | K3S_KUBECONFIG_MODE="644" sh -

# Aggiungi nodi worker
curl -sfL https://get.k3s.io | K3S_URL=https://192.168.1.10:6443 \
  K3S_TOKEN=TOKEN_DEL_NODO sh -

# Installazione Traefik (Ingress)
kubectl apply -f https://github.com/traefik/traefik/raw/v2.10/examples/k8s/traefik.yaml

# Installazione Longhorn (Storage)
kubectl apply -f https://raw.githubusercontent.com/longhorn/longhorn/v1.5.0/deploy/longhorn.yaml

# Installazione Prometheus + Grafana
kubectl apply -f https://raw.githubusercontent.com/prometheus-operator/prometheus-operator/main/bundle.yaml
```

##### Servizi sul Cluster

| Servizio | Descrizione | Container |
|----------|-------------|-----------|
| **k3s** | Kubernetes leggero | - |
| **Traefik** | Ingress controller + reverse proxy | Docker |
| **JupyterHub** | IDE Jupyter per Python | k8s |
| **code-server** | VS Code nel browser | k8s |
| **X2Go** | Desktop remoto | Docker |
| **Gitea** | Git self-hosted (opzionale) | Docker |
| **Pi-hole** | DNS + ad-blocker | Docker |
| **Prometheus** | Monitoring | k8s |
| **Grafana** | Dashboard monitoring | k8s |

##### Progetti di Riferimento

Esistono numerosi progetti open source ben documentati per creare cluster Raspberry Pi con k3s. Ecco i più rilevanti:

| Progetto | Descrizione | Link |
|----------|-------------|------|
| **Techno Tim k3s-ansible** | Installazione automatizzata con Ansible, molto popolare | [GitHub](https://github.com/techno-tim/k3s-ansible) |
| **davestephens/k3s-homelab** | Homelab completo con molti servizi | [GitHub](https://github.com/davestephens/k3s-homelab) |
| **sleighzy/raspberry-pi-k3s-homelab** | Note e configurazioni per cluster RPi | [GitHub](https://github.com/sleighzy/raspberry-pi-k3s-homelab) |
| **dwedia/K3S-HA-Cluster** | Cluster HA con Ansible, basato su Techno Tim | [GitHub](https://github.com/dwedia/k3s-ha-cluster) |
| **cmolendijk/k3s-pi-scripts** | Script per 5 RPi 4B | [GitHub](https://github.com/cmolendijk/k3s-pi-scripts) |
| **rpi5-k3s-homelab** | Progetto recente per RPi5 con Ansible | [GitHub](https://github.com/horvathmilcsi/rpi5-k3s-homelab) |

```
╔═══════════════════════════════════════════════════════════════════════════╗
║               PROGETTI CONSIGLIATI PER INIZIARE                       ║
╠═══════════════════════════════════════════════════════════════════════════╣
║                                                                       ║
║   ⭐ TECNO TIM (k3s-ansible)                                       ║
║   ═══════════════════════════════                                   ║
║   • YouTube + GitHub molto seguiti                                  ║
║   • Installazione Ansible automatizzata                             ║
║   • Tutorial video disponibile                                      ║
║                                                                       ║
║   📚 DAVE STEPHENS (k3s-homelab)                                   ║
║   ═════════════════════════════════                                 ║
║   • Configurazione completa homelab                                  ║
║   • Include molti servizi comuni                                    ║
║   • Ben documentato                                                  ║
║                                                                       ║
║   🆕 RPI5 K3S HOMELAB (2025)                                        ║
║   ═════════════════════════════                                      ║
║   • Progettato per Raspberry Pi 5                                   ║
║   • Ansible per automazione                                          ║
║   • Molto recente e aggiornato                                      ║
║                                                                       ║
╚═══════════════════════════════════════════════════════════════════════════╝
```

##### Risorse Aggiuntive

| Risorsa | Descrizione |
|---------|-------------|
| **Alex's Cloud Blog** | Guida dettagliata setup k3s su RPi cluster |
| **Sahan Serasinghe** | Articolo su costruzione cluster con hardware vecchio |
| **Techno Tim YouTube** | Video tutorial installazione k3s cluster |
| **Raspberry Pi Forums** | Community attiva con discussioni e progetti |

##### Confronto: Server Tradizionale vs Cluster

```
╔═══════════════════════════════════════════════════════════════════════════╗
║               CONFRONTO: SERVER SINGOLO vs CLUSTER                   ║
╠═══════════════════╦═══════════════════╦═══════════════════════════════╣
║    ASPETTO       ║  SERVER SINGOLO  ║      CLUSTER RPi             ║
╠═══════════════════╬═══════════════════╬═══════════════════════════════╣
║  Costo iniziale  ║     €300-500     ║         ~€650                ║
║  Complessità     ║      Bassa        ║         Alta                ║
║  Competenze DevOps║      Base        ║       Avanzate             ║
║  Ridondanza      ║      Nessuna       ║         Alta               ║
║  Scalabilità     ║     Limitata       ║        Elevata             ║
║  Consumo         ║      50-100W       ║         30-50W             ║
║  Manutenzione    ║      Semplice      ║        Complessa           ║
║  Impatto formativo║      Medio         ║        Molto alto          ║
╚═══════════════════╩═══════════════════╩═══════════════════════════════╝
```

##### Raccomandazione

Per il laboratorio ERPSeed, le due opzioni sono complementari:

1. **Per iniziare** (anno 1): Server tradizionale (più semplice)
2. **Per crescere** (anno 2+): Aggiungere cluster Raspberry Pi per insegnare DevOps

In alternativa, per un gruppo di studenti più motivati, si può partire direttamente con il cluster per massimizzare l'apprendimento.

---

## 6. Stima dei Costi

### 6.1 Configurazione Mini (5 utenti)

| Componente | Qty | Costo Unitario | Totale |
|------------|-----|----------------|--------|
| Raspberry Pi 4 4GB | 5 | €55 | €275 |
| Alimentatori 5V 3A | 5 | €10 | €50 |
| Schede SD 32GB | 5 | €10 | €50 |
| Cavi ethernet | 5 | €5 | €25 |
| Switch 8 porte Gigabit | 1 | €30 | €30 |
| Server (PC riciclato) | 1 | €150 | €150 |
| Monitor (riciclato) | 5 | €0 | €0 |
| Tastiera/Mouse (condivisi) | 2 | €20 | €40 |
| **TOTALE** | | | **€620** |

### 6.2 Configurazione Standard (10 utenti)

| Componente | Qty | Costo Unitario | Totale |
|------------|-----|----------------|--------|
| Raspberry Pi 4 8GB | 10 | €75 | €750 |
| Alimentatori | 10 | €10 | €100 |
| Schede SD 64GB | 10 | €15 | €150 |
| Cavi ethernet | 10 | €5 | €50 |
| Switch 16 porte Gigabit | 1 | €50 | €50 |
| Server (PC riciclato) | 1 | €200 | €200 |
| Tastiera/Mouse | 3 | €20 | €60 |
| **TOTALE** | | | **€1.360** |

### 6.3 Configurazione Avanzata (20 utenti)

| Componente | Qty | Costo Unitario | Totale |
|------------|-----|----------------|--------|
| Raspberry Pi 5 8GB | 20 | €85 | €1.700 |
| Switch 24 porte | 1 | €80 | €80 |
| Server dedicato | 1 | €500 | €500 |
| UPS 1500VA | 1 | €150 | €150 |
| Armadio rack | 1 | €100 | €100 |
| Cablaggio e accessori | - | - | €200 |
| **TOTALE** | | | **€2.730** |

### 6.4 Costo Annuo di Esercizio

| Voce | Costo Annuale |
|-------|---------------|
| Elettricità (~300W totali) | €200-400 |
| Connettività internet | €0-50 |
| Manutenzione (stima) | €100 |
| **Totale** | **€300-550/anno** |

---

## 7. Pro e Contro

### 7.1 Vantaggi

```
╔═══════════════════════════════════════════════════════════════════════╗
║               VANTAGGI DELL'ARCHITETTURA                             ║
╠═══════════════════════════════════════════════════════════════════════╣
║                                                                       ║
║   💰 COSTI BASSI                                                     ║
║   • Hardware minimale                                                ║
║   • Client economici (Raspberry Pi)                                  ║
║   • Server può essere riciclato                                     ║
║                                                                       ║
║   🔧 MANUTENZIONE SEMPLICE                                          ║
║   • Aggiornamenti centralizzati (solo server)                       ║
║   • Backup facilitato                                               ║
║   • Sostituzione client facile                                      ║
║                                                                       ║
║   📈 SCALABILITÀ                                                     ║
║   • Aggiungere utenti è economico                                   ║
║   • Server dimensionabile                                            ║
║   • Crescita lineare con i costi                                    ║
║                                                                       ║
║   🔒 SICUREZZA                                                       ║
║   • Dati centralizzati                                              ║
║   • Sessioni isolate (container)                                    ║
║   • Controllo accessi centralizzato                                  ║
║                                                                       ║
║   🌿 ECOLOGIA                                                        ║
║   • Basso consumo energetico                                        ║
║   • Hardware riciclabile                                             ║
║   • Rifiuti elettronici ridotti                                     ║
║                                                                       ║
╚═══════════════════════════════════════════════════════════════════════╝
```

### 7.2 Limitazioni

| Limitazione | Impatto | Soluzione |
|-------------|---------|----------|
| **Latenza rete** | Ritardo nella digitazione | LAN cablata 1Gbps |
| **Single point of failure** | Server giù = tutto bloccato | Server ridondante o backup |
| **Performance** | Meno potenti dei PC locali | Client più recenti |
| **Connessione internet** | Necessaria per esterna | Offline mode possibile |

### 7.3 Quando Preferire PC Tradizionali

| Scenario | Alternative |
|----------|-------------|
| Budget illimitato | PC moderni |
| Latenza critica | Client locali |
| Offline totale | PC con Linux locale |
| Grafica avanzata | GPU dedicate |

---

## 8. Alternative

### 8.1 Confronto Architetture

```
╔═══════════════════════════════════════════════════════════════════════╗
║               CONFRONTO ARCHITETTURE                                 ║
╠═══════════════╦═══════════════╦═══════════════╦═══════════════════╣
║   ASPETTO     ║  THIN CLIENT  ║  BROWSER-ONLY ║   PC LOCALE      ║
║               ║  (X2Go/RPi)   ║  (JupyterHub) ║   (Tradizionale)  ║
╠═══════════════╬═══════════════╬═══════════════╬═══════════════════╣
║  Costo        ║    €€€        ║    €€         ║    €€€€€         ║
║  Complessità  ║    Media       ║    Bassa      ║    Alta          ║
║  Performance  ║    Buona       ║    Media      ║    Eccellente    ║
║  Manutenzione ║    Semplice    ║    Semplice  ║    Complessa     ║
║  Portabilità  ║    Media       ║    Alta       ║    Bassa         ║
╚═══════════════╩═══════════════╩═══════════════╩═══════════════════╝
```

### 8.2 JupyterHub (Alternativa Browser-Only)

Se si preferisce evitare client desktop e usare solo browser:

```
┌─────────────────────────────────────────────────────────────────────────┐
│                   JUPYTERHUB (Browser Only)                             │
├─────────────────────────────────────────────────────────────────────────┤
│                                                                         │
│   STUDENTE                          SERVER                             │
│   ────────                          ───────                             │
│                                                                         │
│   Browser Chrome/Firefox ──► JupyterHub ──► Container per studente     │
│   (anche da tablet!)          (autenticazione)    (Python + Jupyter)    │
│                                                                         │
│   Vantaggi:                                                             │
│   • Nessun client da configurare                                        │
│   • Accesso da qualsiasi dispositivo                                   │
│   • Perfetto per Python + Data Science                                 │
│   • Condivisione notebook facile                                       │
│                                                                         │
└─────────────────────────────────────────────────────────────────────────┘
```

---

## 9. Roadmap Implementativa

### 9.1 Fase 1: Setup Base (Settimana 1-2)

```
📅 FASE 1: SETUP BASE
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

✅ Giorno 1-2: Preparazione hardware
   • Procurare server (PC riciclato)
   • Procurare 5 Raspberry Pi
   • Cablaggio di rete

✅ Giorno 3-4: Installazione server
   • Installare Ubuntu Server 24.04
   • Configurare rete (IP statico)
   • Installare Docker

✅ Giorno 5-6: Configurazione accesso
   • Installare X2Go Server
   • Creare utenti studente1-5
   • Configurare desktop XFCE

✅ Giorno 7: Test
   • Connessione da client
   • Verifica funzionamento
```

### 9.2 Fase 2: Configurazione Didattica (Settimana 3)

```
📅 FASE 2: CONFIGURAZIONE DIDATTICA
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

✅ Installazione Python 3.11+
✅ Configurazione virtual environments
✅ Installazione IDE (Thonny, Jupyter)
✅ Setup cartelle condivise (/home/class/)
✅ Installazione Git
✅ Configurazione Git globale
```

### 9.3 Fase 3: Primo Corso (Settimana 4)

```
📅 FASE 3: PRIMO CORSO
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

✅ Test con 5 studenti
✅ Raccolta feedback
✅ Ottimizzazione performance
✅ Documentazione procedura
✅ Pianificazione espansione
```

### 9.4 Fase 4: Espansione (Mese 2-3)

```
📅 FASE 4: ESPANSIONE
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

✅ Aggiunta utenti (fino a 10-15)
✅ Aggiornamento server (se necessario)
✅ Installazione moduli Python avanzati
✅ Setup JupyterHub (opzionale)
✅ Integrazione con sistema principale
```

---

## 10. Risorse e Riferimenti

### 10.1 Link Utili

| Risorsa | URL |
|---------|-----|
| Ubuntu Server | ubuntu.com/download/server |
| Raspberry Pi OS | raspberrypi.com/software |
| X2Go | x2go.org |
| JupyterHub | jupyterhub.readthedocs.io |
| Docker | docker.com |

### 10.2 Comandi Rapidi

```bash
# Installazione rapida server Python
curl -sSL https://get.docker.com | sh
docker run -d -p 8000:8000 -e JUPYTERHUB_JH_APP_SECRET=secret jupyterhub/jupyterhub jupyterhub

# Connettersi da client X2Go
# Scaricare client da: x2go.org
```

---

## Appendice A: Troubleshooting

### Problemi Comuni

| Problema | Causa | Soluzione |
|----------|-------|-----------|
| Connessione lenta | Rete 100Mbps | Usare 1Gbps |
| Sessione lenta | Server senza resource | Aggiungere RAM |
| Login fallito | Password errata | Verificare utente |
| Desktop non carica | Desktop mancante | Installare XFCE |

---

*Documento creato: Marzo 2026*
*Versione: 1.0*

---

<div align="center">

### 🌱 ERPSeed Lab

*"Imparare a programmare, costruire il futuro"*

</div>
