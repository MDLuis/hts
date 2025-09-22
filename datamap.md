# Tariff Sources Data Map

This document lists key tariff and classification data sources. 

Each section describes a source and includes a small table of its key attributes.

---

## 1. World Customs Organization Harmonized System (WCO HS)

World Customs Organization’s official explanatory notes for the Harmonized System.  
Provides detailed guidance for classifying goods.

| Attribute          | Details                                    |
|-------------------|--------------------------------------------|
| **URL**           | https://www.wcotradetools.org/en/harmonized-system
| **Data Type**     | PDF / Digital (paid license)               |
| **Update Frequency** | Annual updates (when WCO issues revisions) |
| **Restrictions**  | Paid license required; not publicly distributable |

---

## 2. U.S. Harmonized Tariff Schedule (HTS)

Official U.S. tariff classification maintained by the U.S. International Trade Commission (USITC).  
Contains chapters, headings, subheadings, duty rates, legal notes, and annotations.

| Attribute          | Details                                    |
|-------------------|--------------------------------------------|
| **URL**           | https://hts.usitc.gov/ |
| **Data Type**     | HTML pages + JSON API                      |
| **Update Frequency** | Several times per year (new proclamations) |
| **Restrictions**  | Publicly accessible; terms of use apply |

---

## 3. USITC DataWeb

USITC’s trade and tariff data interface. Allows downloads of historical trade flows and tariff schedules.

| Attribute          | Details                                    |
|-------------------|--------------------------------------------|
| **URL**           | https://dataweb.usitc.gov/ |
| **Data Type**     | CSV downloads / API queries                |
| **Update Frequency** | Continuous                               |
| **Restrictions**  | Free registration required for some downloads, downloaded data may be limited to 300,000 rows|

---

### 4. Data.gov – U.S. Government Datasets

Portal for discovering and downloading datasets from across U.S. government agencies (often CSV, JSON, or APIs).  
Many trade, customs, and tariff-related datasets are hosted here.

| Attribute          | Details                                    |
|-------------------|--------------------------------------------|
| **URL**           | https://www.data.gov/ |
| **Data Type**     | CSV, JSON, APIs                             |
| **Update Frequency** | Varies by dataset                        |
| **Restrictions**  | Public access; licensing varies by dataset  |

---

## 5. Canada – Customs Tariff (CBSA)

Provides the current Canadian Customs Tariff files, including chapter-by-chapter breakdowns and legal notes.

| Attribute          | Details                                    |
|-------------------|--------------------------------------------|
| **URL**           | https://www.cbsa-asfc.gc.ca/trade-commerce/tariff-tarif/menu-eng.html |
| **Data Type**     | HTML + PDF files                           |
| **Update Frequency** | Annual (with budget) + amendments as needed |
| **Restrictions**  | Public access |

---

## 6. EU TARIC (Integrated Tariff Database)

The integrated tariff database of the EU. Contains all tariff and regulatory information applying to goods entering the EU.

| Attribute          | Details                                    |
|-------------------|--------------------------------------------|
| **URL**           | https://taxation-customs.ec.europa.eu/customs/calculation-customs-duties/customs-tariff/eu-customs-tariff-taric_en |
| **Data Type**     | Web interface + downloads                  |
| **Update Frequency** | Continuous (legal acts)                 |
| **Restrictions**  | Public access |

---