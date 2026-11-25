# VROOM-API

![Context](https://img.shields.io/badge/ESIEA-PST%202025--2026-0055A4?style=flat-square)
![Languages](https://img.shields.io/badge/Langages-C%20%2F%20C%2B%2B-00599C?style=flat-square)
![Hardware](https://img.shields.io/badge/CAN--Bus-MCP2515-orange?style=flat-square)
![Protocol](https://img.shields.io/badge/R%C3%A9seau-UDP-2ea44f?style=flat-square)

**VROOM-API** est un système embarqué d'acquisition de trames **CAN-Bus** basé sur un contrôleur **MCP2515**, couplé à une API réseau en **UDP** et à une bibliothèque cliente en **C** permettant d'exploiter les données véhicule depuis une application externe (ex. sous Windows).

---

## Contexte du projet

Ce projet a été conçu et développé durant l'année universitaire **2025–2026** dans le cadre du **Projet Scientifique et Technique (PST)** de 2ᵉ année à l'**ESIEA (campus de Laval)** par **Augustin Levrard**, **Thomas Mathieux**, **Daniil Gutcaki** et **Matteo Lebarbier**.

L'objectif était de bâtir une chaîne complète allant de l'électronique embarquée jusqu'à l'interface logicielle : lire et décoder les trames circulant sur un bus CAN via un contrôleur MCP2515, puis transmettre ces données à faible latence en UDP afin qu'un programme tiers puisse les consommer facilement via une API en C.

---

## Architecture du projet

Le dépôt est organisé en deux blocs principaux :

- **Partie embarquée (`src/`)** : gestion bas niveau du contrôleur CAN **MCP2515** (`mcp2515.cpp`, `mcp2515.h`), définition des structures de trames CAN (`can.h`) et programme principal d'acquisition et d'envoi (`main.cpp`).
- **Partie cliente / API (`VROOM_API_CALL/`)** : bibliothèque cliente **UDP** écrite en C (`udp_client.c`, `udp_client.h`) permettant d'appeler l'API depuis un poste distant, accompagnée d'un exemple d'intégration sous Windows (`exemple_windows.c`).

---

## Technologies & Matériel

| Composant | Détails |
| :--- | :--- |
| **Langages** | C++ (embarqué), C (bibliothèque cliente et exemple) |
| **Bus & Contrôleur** | CAN-Bus, contrôleur **MCP2515** |
| **Communication réseau** | Protocole **UDP** |
| **Environnement** | VS Code (`VroomAPI.code-workspace`) |

---

## Structure du dépôt

```text
VROOM-API/
├── VROOM_API_CALL/
│   ├── exemple_windows.c       # Exemple d'utilisation du client API sous Windows
│   ├── udp_client.c            # Implémentation du client UDP
│   └── udp_client.h            # En-tête de l'API cliente UDP
├── src/
│   ├── VroomAPI.code-workspace # Configuration de l'espace de travail VS Code
│   ├── can.h                   # Définitions et structures de trames CAN
│   ├── main.cpp                # Point d'entrée du programme embarqué
│   ├── mcp2515.cpp             # Pilote du contrôleur CAN MCP2515
│   └── mcp2515.h               # Déclarations et registres du MCP2515
└── README.md
