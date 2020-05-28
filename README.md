# Scripts

These are general scripts used for development.

## Quran Scrapper

### Requirements

Python: 3.7.3+
Pip: 19.0.3+

### Install

```
pip install -r requirements.txt
```

### Use Case

This script is used to scrap `web.mushafmakkah.com` for quranic verse data that include information about:

-   surah:
    -   surah name in english and arabic unicode representation
    -   surah number
    -   surah basmala
    -   surah verses
-   ayah:
    -   ayah arabic unicode representation
    -   ayah words in arabic unicode representation
    -   ayah page number
    -   ayah juzi number
    -   ayah number in english and arabic unicode representation

The data is used to generate three JSON data structures:

1. JSON by surah: where data is grouped by surah number
2. JSON by page: where data is grouped by page number
3. JSON by juzi: : where data is grouped by juzi number
