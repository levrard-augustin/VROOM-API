# VROOM-API

![Context](https://img.shields.io/badge/ESIEA-PST%202025--2026-0055A4?style=flat-square)
![Domain](https://img.shields.io/badge/Domaine-Syst%C3%A8mes%20Embarqu%C3%A9s%20%2F%20CAN--Bus-orange?style=flat-square)
![Interface](https://img.shields.io/badge/Interface-OBD2%20%7C%20REST%20API-2ea44f?style=flat-square)

**VROOM-API** est un système embarqué d'acquisition et d'exposition de données véhicule via le bus **CAN / OBD-II**, conçu pour rendre la télémétrie automobile accessible en temps réel à travers une **API REST**.

---

## Contexte du projet

Ce projet a été réalisé en équipe durant l'année universitaire **2025–2026** dans le cadre du **Projet Scientifique et Technique (PST)** de 2ᵉ année à l'**ESIEA (campus de Laval)**.

L'objectif était de concevoir une chaîne complète mêlant électronique embarquée, communication bas niveau et interface logicielle : interroger le calculateur d'un véhicule via sa prise OBD-II, décoder les trames CAN utiles, puis exposer ces métriques de manière standardisée pour un client externe (dashboard, application ou module d'affichage).

---

## Fonctionnalités principales

- **Acquisition CAN / OBD-II** : interrogation et lecture des trames sur le bus véhicule en temps réel.
- **Décodage des PIDs** : conversion des octets bruts en valeurs exploitables (ex. régime moteur RPM, vitesse, température moteur, charge — *à ajuster selon les PIDs implémentés*).
- **Exposition API REST** : mise à disposition des données au format `JSON` via des requêtes HTTP.
- **Architecture modulaire** : séparation entre la couche matérielle/acquisition et l'exposition des données pour faciliter l'ajout de nouveaux capteurs ou clients.

---

## Architecture & Technologies

| Couche | Technologies / Composants |
| :--- | :--- |
| **Matériel** | Prise OBD-II, module/transceiver CAN (`[ex. MCP2515 / SN65HVD230]`), `[ex. ESP32 / Raspberry Pi / Arduino]` |
| **Protocoles** | CAN-Bus, OBD-II, HTTP / REST |
| **Logiciel** | `[ex. C / C++ / Python / JavaScript]` |
| **Format d'échange** | JSON |

*(Remplace les éléments entre crochets par les composants et langages exacts présents dans ce dépôt.)*

---

## Aperçu de l'API

Exemples de routes exposées par le serveur :

| Méthode | Endpoint | Description |
| :--- | :--- | :--- |
| `GET` | `/api/status` | Vérifie l'état de la connexion avec le bus CAN / OBD-II |
| `GET` | `/api/telemetry` | Retourne l'ensemble des données véhicule en temps réel (JSON) |
| `GET` | `/api/rpm` | Retourne le régime moteur actuel |

*(Adapte ce tableau aux routes réelles définies dans ton code.)*

---

## Installation et utilisation

1. **Cloner le dépôt**
   ```bash
   git clone [https://github.com/levrard-augustin/VROOM-API.git](https://github.com/levrard-augustin/VROOM-API.git)
   cd VROOM-API
