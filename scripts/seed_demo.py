"""
VERITAS - Demo Data Generator
Generates realistic, interconnected synthetic FIRs, CDR telecom logs, financial transactions,
and pre-computed Cytoscape knowledge graph fixtures for the KAYA Hackathon demo.
"""
import os
import json
import csv
import math
from datetime import datetime, timedelta, timezone

ROOT_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DEMO_DIR = os.path.join(ROOT_DIR, "data", "demo")
FIRS_DIR = os.path.join(DEMO_DIR, "firs")

def generate_firs():
    """Generates 5 realistic police FIR and intelligence reports."""
    os.makedirs(FIRS_DIR, exist_ok=True)

    fir_001 = """FIRST INFORMATION REPORT (FIR) - CRIME NO: 104/2026
POLICE STATION: SPECIAL CELL, NEW DELHI
DATE & TIME OF REPORT: 12-FEB-2026 23:45 IST
SECTIONS APPLIED: SEC 120B (CRIMINAL CONSPIRACY), SEC 420, IPC & SEC 21 NDPS ACT

INCIDENT SUMMARY:
During an inter-state border checkpoint operation near Singhu Border, Delhi Police intercepted a commercial transport truck (Registration: DL-1M-4412). The driver was identified as ARJUN VERMA (Age 28, S/o Ramesh Verma). Search of the hidden cargo compartment yielded 14 kg of high-grade contraband concealed under agricultural sacks.

Under interrogation, accused ARJUN VERMA stated that the consignment was received from a warehouse in Okhla Industrial Area, managed by RAJESH KUMAR (alias "Raju Swift", Phone: +919811010003). Verma stated he was promised INR 50,000 upon successful delivery to a drop location in Noida. Verma was found in possession of a smartphone (IMEI: 864201049921102, MSISDN: +919811010006) containing recent outgoing calls to RAJESH KUMAR and incoming WhatsApp dispatches from an unknown coordinator using alias "Ghost".

INVESTIGATING OFFICER:
INSPECTOR V. K. MALHOTRA, SPECIAL CELL
"""

    fir_002 = """FIRST INFORMATION REPORT (FIR) - CRIME NO: 188/2026
POLICE STATION: ECONOMIC OFFENCES WING (EOW), DELHI
DATE & TIME OF REPORT: 24-FEB-2026 18:20 IST
SECTIONS APPLIED: PREVENTION OF MONEY LAUNDERING ACT (PMLA) & SEC 468, 471 IPC

INCIDENT SUMMARY:
Acting on intelligence input from the Financial Intelligence Unit (FIU), EOW officers conducted a search and seizure operation at a commercial premises in Chandni Chowk, Old Delhi. The premises was operated as an unlicenced forex and cash transfer counter under the name 'Sheikh Trading Enterprises', overseen by TARIQ SHEIKH (Age 46, alias "The Broker", Phone: +919811010002).

Seizure included INR 48,00,000 in unaccounted cash, multiple international SIM cards, encrypted ledger notebooks, and token receipts. Preliminary analysis of ledgers revealed recurring fund layering disguised as freight forwarding payments to ASTRA LOGISTICS LTD (Account: ACC-ASTRA-7701). Ledgers show multiple payments routed to accounts registered under VIKRAMADITYA SINGHANIA (Account: ACC-SINGH-9901) and ANITA ROY.

INVESTIGATING OFFICER:
ACP MANOJ PANDEY, EOW
"""

    fir_003 = """INTELLIGENCE BRIEF / SURVEILLANCE REPORT: INT-DEL-2026-409
AGENCY: CRIME INTELLIGENCE BRANCH
SUBJECT: CELLULAR BURST ANOMALY & BURNER PHONE NETWORK
DATE: 04-MAR-2026

OPERATIONAL SUMMARY:
Electronic signals intelligence intercepted a cluster of newly activated SIM cards operating in cell towers around Connaught Place and Aerocity. The devices operate exclusively between 23:00 and 03:00 hrs with zero daytime activity. 

Device MSISDN +919811010004 was identified as being operated by KABIR MIRZA (alias "Ghost", Age 34, wanted in extortion case FIR 44/2024). Signal triangulation shows device +919811010004 established multiple short-duration calls (average 35 seconds) with logistics coordinator RAJESH KUMAR (+919811010003) and an unlisted secure terminal (+919811010001) registered to a corporate address in Vasant Vihar belonging to VIKRAMADITYA SINGHANIA.

Vehicle surveillance observed Kabir Mirza driving a black Mahindra Scorpio (Registration: DL-4C-9901) registered to RAJESH KUMAR.

AUTHOR:
SPECIAL INTELLIGENCE ANALYST - SQUAD 4
"""

    fir_004 = """FIELD SURVEILLANCE LOG: SURV-2026-031
LOCATION: OKHLA INDUSTRIAL AREA, PHASE II (GODOWN #44B)
DATES: 10-MAR-2026 TO 14-MAR-2026

OBSERVATION CHRONOLOGY:
- 10-MAR 22:15 - Silver Swift (DL-3C-1234) driven by RAJESH KUMAR arrives at Godown #44B. Driver unloaded cardboard crates stamped 'Astra Exports'.
- 11-MAR 23:40 - Luxury Sedan (DL-1C-0001) registered to VIKRAMADITYA SINGHANIA observed outside Okhla warehouse. Singhania entered the office mezzanine accompanied by ANITA ROY (Director, Astra Logistics).
- 12-MAR 01:10 - TARIQ SHEIKH arrived in a taxi. A 45-minute meeting occurred behind shuttered glass.
- 12-MAR 02:00 - Two courier bikes operated by SAMEER KHAN (+919811010007) departed the premises carrying wrapped parcel backpacks toward South Delhi.

CONCLUSION:
The Okhla facility serves as the physical transfer nexus connecting the logistics distribution arm, corporate front management, and hawala finance brokers.
"""

    fir_005 = """FORENSIC FINANCIAL AUDIT: FIN-EOW-2026-092
AGENCY: FINANCIAL INVESTIGATION SQUAD
SUBJECT: SHELL ENTITY ENTANGLEMENT - ASTRA LOGISTICS LTD
DATE OF AUDIT: 18-MAR-2026

EXECUTIVE FINDINGS:
Astra Logistics Ltd (CIN: U63090DL2021PTC389102), with registered office at Barakhamba Road, New Delhi, shows annual declared revenues of INR 12.4 Crores despite having no verifiable freight fleet or commercial warehouse leases in its corporate name.

Key Shareholders & Directorship:
1. ANITA ROY - Managing Director (Holding 70% equity).
2. VIKRAMADITYA SINGHANIA - Non-Executive Director & Primary Beneficiary through offshore entity 'Trident Holdings Ltd'.

Banking Footprint:
- Bank Account ACC-ASTRA-7701 received 42 structured cash deposits of INR 1,95,000 (just below mandatory CTR reporting thresholds) across 15 different retail branches in 21 days.
- Over 65% of the pooled funds were immediately wired out to account ACC-SINGH-9901 (Vikramaditya Singhania personal wealth account) or liquidated via Tariq Sheikh's trade settlement conduits.
"""

    files = [
        ("FIR_001_Smuggling_Bust.txt", fir_001),
        ("FIR_002_Hawala_Raid.txt", fir_002),
        ("FIR_003_Burner_Phone_Recovery.txt", fir_003),
        ("FIR_004_Surveillance_Report_Warehouse.txt", fir_004),
        ("FIR_005_Shell_Company_Audit.txt", fir_005),
    ]

    for fname, text in files:
        with open(os.path.join(FIRS_DIR, fname), "w", encoding="utf-8") as f:
            f.write(text)
    print(f"Generated 5 FIR text reports in {FIRS_DIR}")

def generate_cdrs():
    """Generates 60+ realistic Call Detail Records (CDRs)."""
    cdrs_path = os.path.join(DEMO_DIR, "cdrs.csv")
    
    # Key suspect phones
    # PH001: Vikramaditya Singhania (+919811010001)
    # PH002: Tariq Sheikh (+919811010002)
    # PH003: Rajesh Kumar (+919811010003)
    # PH004: Kabir Mirza (+919811010004)
    # PH005: Anita Roy (+919811010005)
    # PH006: Arjun Verma (+919811010006)
    # PH007: Sameer Khan (+919811010007)
    # PH008: Deepak Sharma - Driver (+919811010008)
    # PH009: Imran Qureshi - Courier (+919811010009)
    # PH010: Farhan Ali - Associate (+919811010010)

    calls = [
        # Boss (Vikram) <-> Financial Broker (Tariq)
        ("CDR1001", "+919811010001", "+919811010002", "2026-03-01T14:22:10Z", 420, "VOICE", "TOWER_CP_01"),
        ("CDR1002", "+919811010002", "+919811010001", "2026-03-02T16:45:00Z", 185, "VOICE", "TOWER_CHANDNI_04"),
        ("CDR1003", "+919811010001", "+919811010002", "2026-03-05T11:10:30Z", 310, "VOICE", "TOWER_CP_01"),
        ("CDR1004", "+919811010002", "+919811010001", "2026-03-08T09:30:15Z", 240, "VOICE", "TOWER_CHANDNI_04"),
        ("CDR1005", "+919811010001", "+919811010002", "2026-03-11T20:15:00Z", 512, "VOICE", "TOWER_CP_01"),

        # Boss (Vikram) <-> Shell Director (Anita Roy)
        ("CDR1006", "+919811010001", "+919811010005", "2026-03-01T10:05:00Z", 340, "VOICE", "TOWER_CP_01"),
        ("CDR1007", "+919811010005", "+919811010001", "2026-03-04T15:20:12Z", 210, "VOICE", "TOWER_BARAKHAMBA_02"),
        ("CDR1008", "+919811010001", "+919811010005", "2026-03-09T18:00:00Z", 490, "VOICE", "TOWER_CP_01"),
        ("CDR1009", "+919811010005", "+919811010001", "2026-03-12T12:45:30Z", 160, "VOICE", "TOWER_OKHLA_03"),

        # Boss (Vikram) <-> Enforcer (Kabir Mirza) - Rare, high security calls
        ("CDR1010", "+919811010001", "+919811010004", "2026-03-03T23:55:00Z", 95, "VOICE", "TOWER_AEROCITY_09"),
        ("CDR1011", "+919811010004", "+919811010001", "2026-03-10T02:15:10Z", 120, "VOICE", "TOWER_AEROCITY_09"),

        # Financial Broker (Tariq) <-> Shell Director (Anita Roy)
        ("CDR1012", "+919811010002", "+919811010005", "2026-03-02T18:10:00Z", 310, "VOICE", "TOWER_CHANDNI_04"),
        ("CDR1013", "+919811010005", "+919811010002", "2026-03-06T14:40:00Z", 280, "VOICE", "TOWER_BARAKHAMBA_02"),
        ("CDR1014", "+919811010002", "+919811010005", "2026-03-10T19:25:00Z", 415, "VOICE", "TOWER_CHANDNI_04"),

        # Logistics Manager (Rajesh Kumar) <-> Enforcer (Kabir Mirza)
        ("CDR1015", "+919811010004", "+919811010003", "2026-03-02T22:15:00Z", 180, "VOICE", "TOWER_AEROCITY_09"),
        ("CDR1016", "+919811010003", "+919811010004", "2026-03-03T01:30:00Z", 95, "VOICE", "TOWER_OKHLA_03"),
        ("CDR1017", "+919811010004", "+919811010003", "2026-03-07T23:10:00Z", 210, "VOICE", "TOWER_AEROCITY_09"),
        ("CDR1018", "+919811010003", "+919811010004", "2026-03-10T00:45:00Z", 140, "VOICE", "TOWER_OKHLA_03"),

        # Logistics Manager (Rajesh Kumar) <-> Street Runner (Arjun Verma) - High Volume
        ("CDR1019", "+919811010003", "+919811010006", "2026-02-11T19:10:00Z", 320, "VOICE", "TOWER_OKHLA_03"),
        ("CDR1020", "+919811010006", "+919811010003", "2026-02-12T14:05:00Z", 190, "VOICE", "TOWER_SINGHU_01"),
        ("CDR1021", "+919811010003", "+919811010006", "2026-02-12T20:45:00Z", 410, "VOICE", "TOWER_OKHLA_03"),
        ("CDR1022", "+919811010006", "+919811010003", "2026-02-12T22:30:10Z", 65, "VOICE", "TOWER_SINGHU_01"),

        # Logistics Manager (Rajesh Kumar) <-> Courier (Sameer Khan)
        ("CDR1023", "+919811010003", "+919811010007", "2026-03-08T11:20:00Z", 175, "VOICE", "TOWER_OKHLA_03"),
        ("CDR1024", "+919811010007", "+919811010003", "2026-03-09T16:30:00Z", 220, "VOICE", "TOWER_NOIDA_05"),
        ("CDR1025", "+919811010003", "+919811010007", "2026-03-12T01:50:00Z", 95, "VOICE", "TOWER_OKHLA_03"),

        # Logistics Manager (Rajesh Kumar) <-> Driver (Deepak Sharma)
        ("CDR1026", "+919811010003", "+919811010008", "2026-03-04T08:15:00Z", 150, "VOICE", "TOWER_OKHLA_03"),
        ("CDR1027", "+919811010008", "+919811010003", "2026-03-06T19:40:00Z", 280, "VOICE", "TOWER_GHAZIABAD_02"),

        # Enforcer (Kabir Mirza) <-> Courier (Imran Qureshi)
        ("CDR1028", "+919811010004", "+919811010009", "2026-03-05T22:10:00Z", 130, "VOICE", "TOWER_AEROCITY_09"),
        ("CDR1029", "+919811010009", "+919811010004", "2026-03-09T01:25:00Z", 185, "VOICE", "TOWER_MEHRAULI_01"),

        # Financial Broker (Tariq) <-> Associate (Farhan Ali)
        ("CDR1030", "+919811010002", "+919811010010", "2026-03-03T11:00:00Z", 240, "VOICE", "TOWER_CHANDNI_04"),
        ("CDR1031", "+919811010010", "+919811010002", "2026-03-07T15:30:00Z", 310, "VOICE", "TOWER_CHANDNI_04"),
        ("CDR1032", "+919811010002", "+919811010010", "2026-03-11T17:45:00Z", 190, "VOICE", "TOWER_CHANDNI_04"),

        # Additional interconnected activity across secondary operatives
        ("CDR1033", "+919811010006", "+919811010007", "2026-02-10T14:15:00Z", 115, "VOICE", "TOWER_OKHLA_03"),
        ("CDR1034", "+919811010007", "+919811010008", "2026-03-08T18:22:00Z", 90, "VOICE", "TOWER_NOIDA_05"),
        ("CDR1035", "+919811010008", "+919811010009", "2026-03-07T12:05:00Z", 145, "VOICE", "TOWER_GHAZIABAD_02"),
        ("CDR1036", "+919811010009", "+919811010010", "2026-03-06T16:50:00Z", 210, "VOICE", "TOWER_MEHRAULI_01"),
        ("CDR1037", "+919811010002", "+919811010003", "2026-03-10T21:40:00Z", 350, "VOICE", "TOWER_CHANDNI_04"),
        ("CDR1038", "+919811010003", "+919811010002", "2026-03-11T10:15:00Z", 195, "VOICE", "TOWER_OKHLA_03"),
        ("CDR1039", "+919811010005", "+919811010003", "2026-03-11T16:20:00Z", 230, "VOICE", "TOWER_BARAKHAMBA_02"),
        ("CDR1040", "+919811010004", "+919811010007", "2026-03-12T00:15:00Z", 110, "VOICE", "TOWER_AEROCITY_09"),
    ]

    # Generate additional 20 realistic records
    base_time = datetime(2026, 3, 1, 9, 0, 0)
    for i in range(41, 65):
        c_time = base_time + timedelta(hours=i*5, minutes=i*3)
        caller = f"+91981101000{((i % 7) + 1)}"
        receiver = f"+91981101000{(((i + 2) % 7) + 1)}"
        dur = 60 + ((i * 17) % 350)
        tower = f"TOWER_SECTOR_{((i % 8) + 1):02d}"
        calls.append((f"CDR{1000+i}", caller, receiver, c_time.isoformat() + "Z", dur, "VOICE", tower))

    with open(cdrs_path, "w", newline="", encoding="utf-8") as f:
        writer = csv.writer(f)
        writer.writerow(["call_id", "caller_msisdn", "receiver_msisdn", "timestamp", "duration_sec", "call_type", "cell_tower_id"])
        writer.writerows(calls)
    print(f"Generated {len(calls)} Call Detail Records in {cdrs_path}")

def generate_transactions():
    """Generates 50+ financial and hawala transactions showing fund flow."""
    tx_path = os.path.join(DEMO_DIR, "transactions.csv")

    # Accounts:
    # ACC-STREET-01 (Cash pool / runners)
    # ACC-ASTRA-7701 (Astra Logistics Ltd corporate account)
    # ACC-SHEIKH-4401 (Tariq Sheikh trade counter)
    # ACC-SINGH-9901 (Vikramaditya Singhania personal wealth)
    # ACC-ANITA-5501 (Anita Roy personal account)
    # ACC-OFFSHORE-01 (Trident Holdings Ltd / Dubai conduit)
    # ACC-RUNNER-01 (Arjun Verma account)
    # ACC-RUNNER-02 (Sameer Khan account)

    txs = [
        # Structured cash deposits into Astra Logistics
        ("TX1001", "ACC-CASH-POOL", "ACC-ASTRA-7701", 195000, "INR", "2026-02-15T11:20:00Z", "CASH_DEPOSIT", "Freight retainer cash branch 01"),
        ("TX1002", "ACC-CASH-POOL", "ACC-ASTRA-7701", 195000, "INR", "2026-02-16T14:10:00Z", "CASH_DEPOSIT", "Freight retainer cash branch 04"),
        ("TX1003", "ACC-CASH-POOL", "ACC-ASTRA-7701", 190000, "INR", "2026-02-18T10:45:00Z", "CASH_DEPOSIT", "Transport advance invoice #881"),
        ("TX1004", "ACC-CASH-POOL", "ACC-ASTRA-7701", 195000, "INR", "2026-02-20T16:30:00Z", "CASH_DEPOSIT", "Fleet maintenance fund cash"),
        ("TX1005", "ACC-CASH-POOL", "ACC-ASTRA-7701", 185000, "INR", "2026-02-22T12:15:00Z", "CASH_DEPOSIT", "Depot transit cash"),

        # Layering from Astra Logistics -> Tariq Sheikh Hawala conduit
        ("TX1006", "ACC-ASTRA-7701", "ACC-SHEIKH-4401", 850000, "INR", "2026-02-25T11:00:00Z", "RTGS", "Subcontractor logistics settlement"),
        ("TX1007", "ACC-ASTRA-7701", "ACC-SHEIKH-4401", 1200000, "INR", "2026-03-01T15:30:00Z", "RTGS", "Fuel and overland transport clearing"),
        ("TX1008", "ACC-ASTRA-7701", "ACC-SHEIKH-4401", 950000, "INR", "2026-03-06T10:15:00Z", "NEFT", "Invoice #4401 settlement"),

        # Tariq Sheikh -> Offshore & Vikram Singhania Wealth Account
        ("TX1009", "ACC-SHEIKH-4401", "ACC-SINGH-9901", 1500000, "INR", "2026-03-03T16:45:00Z", "IMPS", "Private dividend distribution"),
        ("TX1010", "ACC-SHEIKH-4401", "ACC-SINGH-9901", 2200000, "INR", "2026-03-08T14:20:00Z", "RTGS", "Consulting fee Singhania Trust"),
        ("TX1011", "ACC-SHEIKH-4401", "ACC-OFFSHORE-01", 3500000, "INR", "2026-03-10T11:50:00Z", "SWIFT", "Trade financing Trident Holdings"),

        # Astra Logistics -> Anita Roy Director payouts
        ("TX1012", "ACC-ASTRA-7701", "ACC-ANITA-5501", 450000, "INR", "2026-02-28T18:00:00Z", "NEFT", "Director management remuneration"),
        ("TX1013", "ACC-ASTRA-7701", "ACC-ANITA-5501", 600000, "INR", "2026-03-12T17:15:00Z", "NEFT", "Executive quarterly bonus"),

        # Astra Logistics -> Logistics manager Rajesh Kumar (Disbursements)
        ("TX1014", "ACC-ASTRA-7701", "ACC-RAJESH-3301", 250000, "INR", "2026-02-10T09:30:00Z", "NEFT", "Fleet operational petty cash"),
        ("TX1015", "ACC-ASTRA-7701", "ACC-RAJESH-3301", 300000, "INR", "2026-03-05T10:00:00Z", "NEFT", "Warehouse rental and security"),

        # Rajesh Kumar -> Runners & Couriers (Arjun Verma & Sameer Khan)
        ("TX1016", "ACC-RAJESH-3301", "ACC-RUNNER-01", 50000, "INR", "2026-02-12T08:00:00Z", "UPI", "Inter-state delivery advance"),
        ("TX1017", "ACC-RAJESH-3301", "ACC-RUNNER-02", 35000, "INR", "2026-03-09T14:00:00Z", "UPI", "Parcel courier fee"),
        ("TX1018", "ACC-RAJESH-3301", "ACC-DEEPAK-08", 40000, "INR", "2026-03-04T12:30:00Z", "UPI", "Heavy transport diesel allowance"),
    ]

    # Additional synthetic transactions to establish density
    base_date = datetime(2026, 2, 1)
    for i in range(19, 52):
        t_date = base_date + timedelta(days=(i % 38), hours=(i % 12))
        amt = 25000 + ((i * 13500) % 450000)
        src = "ACC-ASTRA-7701" if (i % 2 == 0) else "ACC-SHEIKH-4401"
        dst = "ACC-SINGH-9901" if (i % 3 == 0) else f"ACC-SUB-{i%5}"
        txs.append((f"TX{1000+i}", src, dst, amt, "INR", t_date.isoformat() + "Z", "RTGS", f"Settlement ledger tranche #{i}"))

    with open(tx_path, "w", newline="", encoding="utf-8") as f:
        writer = csv.writer(f)
        writer.writerow(["transaction_id", "sender_account", "receiver_account", "amount", "currency", "timestamp", "payment_channel", "reference_note"])
        writer.writerows(txs)
    print(f"Generated {len(txs)} Financial Transactions in {tx_path}")

def generate_graph_fixtures():
    """
    Generates standardized entities.json, relationships.json, and graph.json (Cytoscape format).
    Includes algorithmic properties: Degree, Betweenness Centrality, PageRank, and Community IDs.
    """
    entities = [
        # PERSONS
        {"id": "P001", "name": "Vikramaditya Singhania", "type": "Person", "role": "Syndicate Mastermind", "risk_score": 96, "aliases": ["Vikram", "The Don"], "degree": 9, "betweenness": 0.48, "pagerank": 0.165, "community_id": 1},
        {"id": "P002", "name": "Tariq Sheikh", "type": "Person", "role": "Hawala Broker", "risk_score": 88, "aliases": ["The Broker", "Sheikh Ji"], "degree": 12, "betweenness": 0.62, "pagerank": 0.142, "community_id": 2},
        {"id": "P003", "name": "Rajesh Kumar", "type": "Person", "role": "Logistics Coordinator", "risk_score": 82, "aliases": ["Raju Swift"], "degree": 11, "betweenness": 0.44, "pagerank": 0.125, "community_id": 1},
        {"id": "P004", "name": "Kabir Mirza", "type": "Person", "role": "Enforcer & Security", "risk_score": 89, "aliases": ["Ghost"], "degree": 7, "betweenness": 0.28, "pagerank": 0.088, "community_id": 3},
        {"id": "P005", "name": "Anita Roy", "type": "Person", "role": "Shell Company Director", "risk_score": 78, "aliases": ["Director Roy"], "degree": 8, "betweenness": 0.35, "pagerank": 0.095, "community_id": 2},
        {"id": "P006", "name": "Arjun Verma", "type": "Person", "role": "Transport Courier", "risk_score": 74, "aliases": ["Ramesh S/o"], "degree": 5, "betweenness": 0.12, "pagerank": 0.052, "community_id": 1},
        {"id": "P007", "name": "Sameer Khan", "type": "Person", "role": "Urban Dispatcher", "risk_score": 68, "aliases": ["Sam"], "degree": 4, "betweenness": 0.09, "pagerank": 0.045, "community_id": 1},
        {"id": "P008", "name": "Deepak Sharma", "type": "Person", "role": "Heavy Fleet Driver", "risk_score": 62, "aliases": ["Deepu"], "degree": 3, "betweenness": 0.06, "pagerank": 0.038, "community_id": 1},
        {"id": "P009", "name": "Imran Qureshi", "type": "Person", "role": "Safehouse Guard", "risk_score": 65, "aliases": ["Imran Bhai"], "degree": 3, "betweenness": 0.05, "pagerank": 0.036, "community_id": 3},
        {"id": "P010", "name": "Farhan Ali", "type": "Person", "role": "Forex Runner", "risk_score": 71, "aliases": ["Cashier"], "degree": 4, "betweenness": 0.08, "pagerank": 0.042, "community_id": 2},

        # PHONES
        {"id": "PH001", "name": "+919811010001", "type": "Phone", "role": "Encrypted Terminal", "risk_score": 90, "aliases": ["Secure Line 1"], "degree": 5, "betweenness": 0.22, "pagerank": 0.065, "community_id": 1},
        {"id": "PH002", "name": "+919811010002", "type": "Phone", "role": "Broker Primary Line", "risk_score": 85, "aliases": ["Old Delhi Line"], "degree": 7, "betweenness": 0.38, "pagerank": 0.082, "community_id": 2},
        {"id": "PH003", "name": "+919811010003", "type": "Phone", "role": "Logistics Dispatch Line", "risk_score": 80, "aliases": ["Okhla Line"], "degree": 8, "betweenness": 0.34, "pagerank": 0.078, "community_id": 1},
        {"id": "PH004", "name": "+919811010004", "type": "Phone", "role": "Burner Device Cluster", "risk_score": 92, "aliases": ["Burner Alpha"], "degree": 5, "betweenness": 0.25, "pagerank": 0.061, "community_id": 3},
        {"id": "PH005", "name": "+919811010005", "type": "Phone", "role": "Corporate Office Line", "risk_score": 72, "aliases": ["Astra HQ Line"], "degree": 4, "betweenness": 0.18, "pagerank": 0.051, "community_id": 2},
        {"id": "PH006", "name": "+919811010006", "type": "Phone", "role": "Seized Courier Phone", "risk_score": 84, "aliases": ["Border Intercept"], "degree": 3, "betweenness": 0.09, "pagerank": 0.039, "community_id": 1},

        # VEHICLES
        {"id": "V001", "name": "DL-1C-0001 (BMW 7-Series)", "type": "Vehicle", "role": "Executive Vehicle", "risk_score": 75, "aliases": ["Black Luxury Sedan"], "degree": 2, "betweenness": 0.04, "pagerank": 0.028, "community_id": 1},
        {"id": "V002", "name": "DL-3C-1234 (Swift Dzire)", "type": "Vehicle", "role": "Logistics Car", "risk_score": 70, "aliases": ["Silver Sedan"], "degree": 2, "betweenness": 0.05, "pagerank": 0.029, "community_id": 1},
        {"id": "V003", "name": "DL-4C-9901 (Mahindra Scorpio)", "type": "Vehicle", "role": "Enforcement SUV", "risk_score": 86, "aliases": ["Black Scorpio"], "degree": 2, "betweenness": 0.08, "pagerank": 0.035, "community_id": 3},
        {"id": "V004", "name": "DL-1M-4412 (Transport Truck)", "type": "Vehicle", "role": "Smuggling Carrier", "risk_score": 94, "aliases": ["Intercepted Truck"], "degree": 2, "betweenness": 0.06, "pagerank": 0.032, "community_id": 1},

        # ORGANIZATIONS
        {"id": "ORG001", "name": "Astra Logistics Ltd", "type": "Organization", "role": "Corporate Shell", "risk_score": 88, "aliases": ["Astra Exports"], "degree": 6, "betweenness": 0.36, "pagerank": 0.089, "community_id": 2},
        {"id": "ORG002", "name": "Sheikh Trading Enterprises", "type": "Organization", "role": "Hawala Counter", "risk_score": 84, "aliases": ["Sheikh Forex"], "degree": 5, "betweenness": 0.31, "pagerank": 0.075, "community_id": 2},
        {"id": "ORG003", "name": "Trident Holdings Ltd (Offshore)", "type": "Organization", "role": "Offshore Conduit", "risk_score": 91, "aliases": ["Trident Dubai"], "degree": 3, "betweenness": 0.15, "pagerank": 0.048, "community_id": 2},

        # LOCATIONS
        {"id": "LOC001", "name": "Okhla Industrial Area (Godown 44B)", "type": "Location", "role": "Distribution Hub", "risk_score": 85, "aliases": ["Central Depot"], "degree": 5, "betweenness": 0.28, "pagerank": 0.068, "community_id": 1},
        {"id": "LOC002", "name": "Chandni Chowk Counter", "type": "Location", "role": "Hawala Vault", "risk_score": 82, "aliases": ["Old Delhi Vault"], "degree": 4, "betweenness": 0.22, "pagerank": 0.058, "community_id": 2},
        {"id": "LOC003", "name": "Vasant Vihar Residence", "type": "Location", "role": "Command Safehouse", "risk_score": 79, "aliases": ["South Delhi Base"], "degree": 3, "betweenness": 0.14, "pagerank": 0.044, "community_id": 1},

        # BANK ACCOUNTS
        {"id": "BA001", "name": "ACC-SINGH-9901", "type": "BankAccount", "role": "Master Beneficiary Account", "risk_score": 93, "aliases": ["Singhania Private Wealth"], "degree": 4, "betweenness": 0.25, "pagerank": 0.062, "community_id": 1},
        {"id": "BA002", "name": "ACC-ASTRA-7701", "type": "BankAccount", "role": "Layering Hub Account", "risk_score": 89, "aliases": ["Astra Corporate Operating"], "degree": 7, "betweenness": 0.42, "pagerank": 0.086, "community_id": 2},
        {"id": "BA003", "name": "ACC-SHEIKH-4401", "type": "BankAccount", "role": "Hawala Settlement Account", "risk_score": 86, "aliases": ["Sheikh Trade Ledger"], "degree": 5, "betweenness": 0.32, "pagerank": 0.071, "community_id": 2},
    ]

    relationships = [
        # Person -> Phone
        {"id": "R001", "source": "P001", "target": "PH001", "type": "USES_PHONE", "weight": 1.0, "timestamp": "2026-03-01T00:00:00Z", "provenance": {"source_id": "INT-DEL-2026-409", "source_type": "SURVEILLANCE", "snippet": "Phone registered to Vasant Vihar residence.", "confidence": 0.95}},
        {"id": "R002", "source": "P002", "target": "PH002", "type": "USES_PHONE", "weight": 1.0, "timestamp": "2026-03-01T00:00:00Z", "provenance": {"source_id": "FIR-188/2026", "source_type": "POLICE_REPORT", "snippet": "Device recovered from Tariq Sheikh during raid.", "confidence": 0.98}},
        {"id": "R003", "source": "P003", "target": "PH003", "type": "USES_PHONE", "weight": 1.0, "timestamp": "2026-03-01T00:00:00Z", "provenance": {"source_id": "FIR-104/2026", "source_type": "POLICE_REPORT", "snippet": "Driver Verma confirmed dispatch coordination with this MSISDN.", "confidence": 0.94}},
        {"id": "R004", "source": "P004", "target": "PH004", "type": "USES_PHONE", "weight": 1.0, "timestamp": "2026-03-01T00:00:00Z", "provenance": {"source_id": "INT-DEL-2026-409", "source_type": "SURVEILLANCE", "snippet": "Signals intelligence linked burner cluster to Kabir Mirza.", "confidence": 0.91}},
        {"id": "R005", "source": "P005", "target": "PH005", "type": "USES_PHONE", "weight": 1.0, "timestamp": "2026-03-01T00:00:00Z", "provenance": {"source_id": "FIN-EOW-2026-092", "source_type": "AUDIT", "snippet": "Corporate listing on Astra Logistics MCA filing.", "confidence": 0.99}},
        {"id": "R006", "source": "P006", "target": "PH006", "type": "USES_PHONE", "weight": 1.0, "timestamp": "2026-03-01T00:00:00Z", "provenance": {"source_id": "FIR-104/2026", "source_type": "POLICE_REPORT", "snippet": "Recovered from driver Arjun Verma during Singhu border seizure.", "confidence": 0.99}},

        # Phone -> Phone (Calls)
        {"id": "R007", "source": "PH001", "target": "PH002", "type": "CALLED", "weight": 5.0, "timestamp": "2026-03-11T20:15:00Z", "provenance": {"source_id": "CDR-LOG-2026", "source_type": "TELECOM_CDR", "snippet": "5 calls totaling 1667 seconds between Vikram Singhania and Tariq Sheikh.", "confidence": 1.0}},
        {"id": "R008", "source": "PH001", "target": "PH005", "type": "CALLED", "weight": 4.0, "timestamp": "2026-03-12T12:45:30Z", "provenance": {"source_id": "CDR-LOG-2026", "source_type": "TELECOM_CDR", "snippet": "4 calls totaling 1200 seconds between Vikram Singhania and Anita Roy.", "confidence": 1.0}},
        {"id": "R009", "source": "PH001", "target": "PH004", "type": "CALLED", "weight": 2.0, "timestamp": "2026-03-10T02:15:10Z", "provenance": {"source_id": "CDR-LOG-2026", "source_type": "TELECOM_CDR", "snippet": "2 late night encrypted calls with burner device.", "confidence": 1.0}},
        {"id": "R010", "source": "PH002", "target": "PH005", "type": "CALLED", "weight": 3.0, "timestamp": "2026-03-10T19:25:00Z", "provenance": {"source_id": "CDR-LOG-2026", "source_type": "TELECOM_CDR", "snippet": "3 calls coordinating Hawala settlements.", "confidence": 1.0}},
        {"id": "R011", "source": "PH004", "target": "PH003", "type": "CALLED", "weight": 4.0, "timestamp": "2026-03-10T00:45:00Z", "provenance": {"source_id": "CDR-LOG-2026", "source_type": "TELECOM_CDR", "snippet": "4 calls directing logistics dispatches.", "confidence": 1.0}},
        {"id": "R012", "source": "PH003", "target": "PH006", "type": "CALLED", "weight": 4.0, "timestamp": "2026-02-12T22:30:10Z", "provenance": {"source_id": "CDR-LOG-2026", "source_type": "TELECOM_CDR", "snippet": "4 calls preceding Singhu border checkpoint intercept.", "confidence": 1.0}},

        # Person -> Vehicle
        {"id": "R013", "source": "P001", "target": "V001", "type": "OWNS", "weight": 1.0, "timestamp": "2026-03-01T00:00:00Z", "provenance": {"source_id": "SURV-2026-031", "source_type": "SURVEILLANCE", "snippet": "Observed arriving at Okhla warehouse.", "confidence": 0.95}},
        {"id": "R014", "source": "P003", "target": "V002", "type": "OWNS", "weight": 1.0, "timestamp": "2026-03-01T00:00:00Z", "provenance": {"source_id": "SURV-2026-031", "source_type": "SURVEILLANCE", "snippet": "Rajesh Kumar unloads cargo from Swift Dzire.", "confidence": 0.95}},
        {"id": "R015", "source": "P004", "target": "V003", "type": "OPERATES", "weight": 1.0, "timestamp": "2026-03-04T00:00:00Z", "provenance": {"source_id": "INT-DEL-2026-409", "source_type": "SURVEILLANCE", "snippet": "Kabir Mirza observed driving black Scorpio.", "confidence": 0.92}},
        {"id": "R016", "source": "P006", "target": "V004", "type": "OPERATES", "weight": 1.0, "timestamp": "2026-02-12T00:00:00Z", "provenance": {"source_id": "FIR-104/2026", "source_type": "POLICE_REPORT", "snippet": "Arjun Verma intercepted driving commercial truck.", "confidence": 0.99}},

        # Person -> Organization
        {"id": "R017", "source": "P001", "target": "ORG001", "type": "CONTROLS", "weight": 1.0, "timestamp": "2026-02-01T00:00:00Z", "provenance": {"source_id": "FIN-EOW-2026-092", "source_type": "AUDIT", "snippet": "Ultimate beneficial owner through offshore vehicle.", "confidence": 0.94}},
        {"id": "R018", "source": "P005", "target": "ORG001", "type": "MEMBER_OF", "weight": 1.0, "timestamp": "2026-02-01T00:00:00Z", "provenance": {"source_id": "FIN-EOW-2026-092", "source_type": "AUDIT", "snippet": "Managing Director holding 70% registered equity.", "confidence": 0.99}},
        {"id": "R019", "source": "P002", "target": "ORG002", "type": "CONTROLS", "weight": 1.0, "timestamp": "2026-02-01T00:00:00Z", "provenance": {"source_id": "FIR-188/2026", "source_type": "POLICE_REPORT", "snippet": "Sole proprietor of unlicenced currency counter.", "confidence": 0.99}},
        {"id": "R020", "source": "P001", "target": "ORG003", "type": "CONTROLS", "weight": 1.0, "timestamp": "2026-02-01T00:00:00Z", "provenance": {"source_id": "FIN-EOW-2026-092", "source_type": "AUDIT", "snippet": "Beneficial ownership revealed in offshore tax filings.", "confidence": 0.90}},

        # Person -> Bank Account
        {"id": "R021", "source": "P001", "target": "BA001", "type": "OWNS_ACCOUNT", "weight": 1.0, "timestamp": "2026-02-01T00:00:00Z", "provenance": {"source_id": "FIN-EOW-2026-092", "source_type": "AUDIT", "snippet": "Private wealth management account.", "confidence": 1.0}},
        {"id": "R022", "source": "ORG001", "target": "BA002", "type": "OWNS_ACCOUNT", "weight": 1.0, "timestamp": "2026-02-01T00:00:00Z", "provenance": {"source_id": "FIN-EOW-2026-092", "source_type": "AUDIT", "snippet": "Primary corporate operating account.", "confidence": 1.0}},
        {"id": "R023", "source": "ORG002", "target": "BA003", "type": "OWNS_ACCOUNT", "weight": 1.0, "timestamp": "2026-02-01T00:00:00Z", "provenance": {"source_id": "FIR-188/2026", "source_type": "POLICE_REPORT", "snippet": "Seized ledger bank account.", "confidence": 1.0}},

        # Account -> Account (Transactions / Money Trail)
        {"id": "R024", "source": "BA002", "target": "BA003", "type": "TRANSACTED_WITH", "weight": 3000000.0, "timestamp": "2026-03-06T10:15:00Z", "provenance": {"source_id": "BANK-TX-2026", "source_type": "BANK_LEDGER", "snippet": "Multiple wire tranches aggregating INR 30 Lakhs.", "confidence": 1.0}},
        {"id": "R025", "source": "BA003", "target": "BA001", "type": "TRANSACTED_WITH", "weight": 3700000.0, "timestamp": "2026-03-08T14:20:00Z", "provenance": {"source_id": "BANK-TX-2026", "source_type": "BANK_LEDGER", "snippet": "Consulting and dividend disbursements to Vikram Singhania.", "confidence": 1.0}},

        # Person <-> Person (Criminal Association / Hierarchy)
        {"id": "R026", "source": "P001", "target": "P002", "type": "ASSOCIATED_WITH", "weight": 0.95, "timestamp": "2026-03-12T01:10:00Z", "provenance": {"source_id": "SURV-2026-031", "source_type": "SURVEILLANCE", "snippet": "Direct closed-door meeting at Okhla warehouse.", "confidence": 0.96}},
        {"id": "R027", "source": "P001", "target": "P005", "type": "ASSOCIATED_WITH", "weight": 0.90, "timestamp": "2026-03-11T23:40:00Z", "provenance": {"source_id": "SURV-2026-031", "source_type": "SURVEILLANCE", "snippet": "Joint arrival at Okhla warehouse mezzanine.", "confidence": 0.95}},
        {"id": "R028", "source": "P003", "target": "P006", "type": "SUPERVISES", "weight": 0.88, "timestamp": "2026-02-12T00:00:00Z", "provenance": {"source_id": "FIR-104/2026", "source_type": "POLICE_REPORT", "snippet": "Verma confirmed Rajesh Kumar as immediate handler.", "confidence": 0.98}},
        {"id": "R029", "source": "P003", "target": "P007", "type": "SUPERVISES", "weight": 0.80, "timestamp": "2026-03-12T02:00:00Z", "provenance": {"source_id": "SURV-2026-031", "source_type": "SURVEILLANCE", "snippet": "Dispatched Sameer Khan on parcel courier run.", "confidence": 0.92}},
        {"id": "R030", "source": "P004", "target": "P003", "type": "COORDINATES_WITH", "weight": 0.85, "timestamp": "2026-03-03T01:30:00Z", "provenance": {"source_id": "INT-DEL-2026-409", "source_type": "SURVEILLANCE", "snippet": "Frequent coordination over encrypted phone lines.", "confidence": 0.93}},

        # Person / Vehicle -> Location
        {"id": "R031", "source": "P003", "target": "LOC001", "type": "LOCATED_AT", "weight": 1.0, "timestamp": "2026-03-10T22:15:00Z", "provenance": {"source_id": "SURV-2026-031", "source_type": "SURVEILLANCE", "snippet": "Present during cargo unloading at Okhla godown.", "confidence": 0.97}},
        {"id": "R032", "source": "P002", "target": "LOC002", "type": "LOCATED_AT", "weight": 1.0, "timestamp": "2026-02-24T18:20:00Z", "provenance": {"source_id": "FIR-188/2026", "source_type": "POLICE_REPORT", "snippet": "Apprehended inside Chandni Chowk counter premises.", "confidence": 0.99}},
        {"id": "R033", "source": "P001", "target": "LOC003", "type": "LOCATED_AT", "weight": 1.0, "timestamp": "2026-03-04T00:00:00Z", "provenance": {"source_id": "INT-DEL-2026-409", "source_type": "SURVEILLANCE", "snippet": "Residence and command location.", "confidence": 0.90}},
    ]

    # Save entities.json
    entities_path = os.path.join(DEMO_DIR, "entities.json")
    with open(entities_path, "w", encoding="utf-8") as f:
        json.dump(entities, f, indent=2)

    # Save relationships.json
    relationships_path = os.path.join(DEMO_DIR, "relationships.json")
    with open(relationships_path, "w", encoding="utf-8") as f:
        json.dump(relationships, f, indent=2)

    # Format Cytoscape elements structure for graph.json
    cytoscape_nodes = []
    for e in entities:
        cytoscape_nodes.append({
            "data": {
                "id": e["id"],
                "label": e["name"],
                "type": e["type"],
                "role": e["role"],
                "risk_score": e["risk_score"],
                "aliases": e.get("aliases", []),
                "degree": e.get("degree", 1),
                "betweenness": e.get("betweenness", 0.0),
                "pagerank": e.get("pagerank", 0.01),
                "community_id": e.get("community_id", 1),
            }
        })

    cytoscape_edges = []
    for r in relationships:
        cytoscape_edges.append({
            "data": {
                "id": r["id"],
                "source": r["source"],
                "target": r["target"],
                "type": r["type"],
                "weight": r.get("weight", 1.0),
                "timestamp": r.get("timestamp", ""),
                "provenance": r.get("provenance", {}),
            }
        })

    graph_payload = {
        "metadata": {
            "title": "Operation Shadow Syndicate - Demo Dataset",
            "generated_at": datetime.now(timezone.utc).isoformat(),
            "total_nodes": len(cytoscape_nodes),
            "total_edges": len(cytoscape_edges),
            "communities_detected": 3,
            "key_mastermind": "P001 (Vikramaditya Singhania)",
            "key_broker": "P002 (Tariq Sheikh)"
        },
        "nodes": cytoscape_nodes,
        "edges": cytoscape_edges
    }

    graph_path = os.path.join(DEMO_DIR, "graph.json")
    with open(graph_path, "w", encoding="utf-8") as f:
        json.dump(graph_payload, f, indent=2)

    print(f"Generated {len(entities)} entities in {entities_path}")
    print(f"Generated {len(relationships)} relationships in {relationships_path}")
    print(f"Generated Cytoscape graph payload ({len(cytoscape_nodes)} nodes, {len(cytoscape_edges)} edges) in {graph_path}")

def main():
    print("=" * 60)
    print("VERITAS - Synthetic Demo Dataset Generator")
    print("=" * 60)
    os.makedirs(DEMO_DIR, exist_ok=True)
    generate_firs()
    generate_cdrs()
    generate_transactions()
    generate_graph_fixtures()
    print("=" * 60)
    print("SUCCESS: All demo datasets and Cytoscape fixtures created!")
    print("=" * 60)

if __name__ == "__main__":
    main()
