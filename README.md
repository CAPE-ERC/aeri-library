# aeri

AERI article scoring and country-month economic-risk index library, built
from the AERI/ARS work at CAPE Economic Research and Consulting.

This first release covers **Library 1** from the proposal: scoring each
scraped news article and rolling the scores up into the country-month
AERI (Africa Economic Risk Index). Pillar indices, the ARS composite and
early-warning alerts (Libraries 2-4) are planned as follow-up PRs on top
of this foundation.

## Install

```bash
pip install -e ".[dev]"
```

## Data format

`aeri` expects article data with these columns: `country`, `site`, `date`,
`title`, `url`, `text` (the scraper's raw HTML/text). This matches the
`articles_<Publisher>_<YYYY-MM>.csv.gz` exports under
`<Country>/<Publisher>/<YYYY-MM>/` in the scraped-article archive. Use
`load_articles_tree()` to ingest that directory structure directly:

```python
import aeri

articles = aeri.load_articles_tree("path/to/Shak_Scrapped_Top_Articles")
scored = aeri.score_dataframe(articles)

aeri_index = aeri.compute_aeri(scored)
aeri_index = aeri.coverage_filter(aeri_index)  # drop thin country-months

diag = aeri.diagnostics(scored)
```

## Scoring pipeline

| Function | What it does |
| --- | --- |
| `normalize_text()` | Strip HTML; standardise case, whitespace and Unicode |
| `is_relevant()` | Economic relevance flag `R_i` from the multilingual dictionary |
| `severity_tier()` | Ordinal severity `S_i` from 0 to 4; the highest tier matched wins |
| `confidence_weight()` | `W_i = clip(1 + 0.5*TitleHint + 0.2*LongText + 0.3*MultiPillar, 1, 2)` |
| `assign_pillars()` | Flags for the 8 pillars; one article can activate several |
| `article_score()` | `A_i = R_i * S_i * W_i` |
| `compute_aeri()` | `AERI = 100 * sum(A_i) / N_t` for each country and month |
| `diagnostics()` | Total articles, relevant share, average severity, average confidence |
| `coverage_filter()` | Keeps country-months with at least 100 articles |

`score_dataframe()` runs the per-article functions (`is_relevant`,
`severity_tier`, `assign_pillars`, `confidence_weight`, `article_score`)
over an articles DataFrame in one pass and appends the resulting columns,
including one boolean column per pillar.

The 8 pillars are: Inflation, FX and External, Debt and Fiscal, Financial
Sector, Growth and Real Economy, Commodity Supply, Political Economy, and
Climate and Disaster.

## Dictionaries

The relevance, severity and pillar keyword dictionaries in `aeri/data/`
are a first-pass, hand-curated starting point (English, with French,
Portuguese, Arabic and Swahili coverage for relevance) meant to be
calibrated against real coverage before being treated as final. Every
scoring function accepts an `AERIConfig` so a project can supply its own
dictionary without forking the library:

```python
from aeri import AERIConfig, is_relevant

my_config = AERIConfig(
    relevance_keywords=frozenset({"inflation", "naira", "devaluation"}),
    severity_keywords=AERIConfig.default().severity_keywords,
    pillar_keywords=AERIConfig.default().pillar_keywords,
)
is_relevant("Naira weakens further amid fuel subsidy removal", my_config)
```

## Roadmap

- Pillar composite indices and PCA-combined pillar measure (Library 2)
- `ars` composite score (Library 3)
- `riskalert` early-warning alerts (Library 4)

## Development

```bash
pip install -e ".[dev]"
pytest
```
