# Zahnarztpraxis Dr. Heinrich Schülein

Static website for the dental practice of Dr. Heinrich Schülein, Pfaffenstraße 27,
17033 Neubrandenburg. The domain schuelein-zahnheilkunde.de is reserved at
Strato and currently has no site.

Built on the Dentaltechnik Gussmann engine (tokens, reveal, accordion, form,
preloader) with its own layouts: nameplate hero with live office-hours status,
Leistungen index, night timeline (Schlafmedizin), week chart (Sprechzeiten).
No dependencies, no cookies, no third-party requests. Fonts are self-hosted.

## Structure

- `src/*.html` + `src/partials/` → `python3 build.py` → `index.html`, `impressum.html`, `datenschutz.html`
- `css/styles.css`, `js/main.js`: all styling and behaviour
- `assets/`: logo (`logo.svg`, `logo-mark.svg`), `og.png`, `apple-touch-icon.png`, `mark.json` (outlined ü for inline use)
- `tools/logo.py`: regenerates the logo from the Newsreader variable font

Edit `src/`, never the built HTML in the root.

## Logo

The mark is the "ü" of *Schülein*, set in Newsreader and outlined, on a petrol
tile, with the umlaut dots in brass. It is a letter from the name rather than
a tooth pictogram.

## Before launch

- Impressum/Datenschutz: fill everything marked in red (`.ph`): chamber address, KZV, liability insurance, hosting provider.
- Contact form: validates, but nothing is sent yet. Connect a DSGVO-compliant form service in `js/main.js`.
- Confirm the facts with the practice: Invisalign offering, "alle Kassen", review figures (sanego 9,9/10 from 12 reviews, Google 4,7 from 36 reviews, as of September 2026).
- Add real photos (practice, team) if available.

## Sources

sanego.de (reviews and quotes), dasoertliche.de, 11880.com (opening hours),
portal-der-zahnmedizin.de (fax), dgzs.de (DGZS member practice),
invisalign.de (provider listing), LinkedIn / Universität Greifswald.
