# Word lists and licences

| Used for | Source | Licence |
|---|---|---|
| English words | ENABLE word list (Alan Beale, M Cooper et al.) | Public domain |
| Spanish words | LibreOffice es_ES dictionary v2.8 (Santiago Bosio and contributors), via npm `dictionary-es` 4.0.0 | GPL-3.0+ or LGPL-3.0+ or MPL-1.1+ (used under MPL-1.1) |
| French words | Dicollecte / Grammalecte dictionary v7.5 (Olivier R. and contributors), via npm `dictionary-fr` 3.0.0 | MPL-2.0 |
| Offensive-word filter | LDNOOBW word lists (en/es/fr), cross-checked with npm `profane-words`, plus our own additions | CC BY 4.0 / WTFPL |
| Cognates (same word across languages) | Princeton WordNet 3.0 + Open Multilingual WordNet 1.4 (Spanish: Multilingual Central Repository; French: WOLF) | WordNet licence / CC BY 3.0 / CeCILL-C |

The game file contains only the words that can be made from each puzzle's seven letters, not the full lists.
`tools/` holds the scripts that built the puzzle data (run order: `wn.py`, then `build.py "<letters>:<center>,..."`, then `inject.py`); they expect the downloaded lists in a work folder, see `lib.py`.
