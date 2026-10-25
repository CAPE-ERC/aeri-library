# aeri

AERI article scoring and country-month economic-risk index library, built
from the AERI/ARS work at CAPE Economic Research and Consulting.

This first release covers **Library 1** from the proposal: scoring each
scraped news article and rolling the scores up into the country-month
AERI (Africa Economic Risk Index). Pillar composite indices, the ARS
composite score and early-warning alerts (Libraries 2-4) are planned as
follow-up PRs on top of this foundation. Matching conventions, data
layout and output schema are kept consistent with the sibling
[`newsindex`](https://github.com/CAPE-ERC/newsindex-library) (EPU) library
and the production AERI Pillar API, so the CAPE libraries interoperate.

## Install

```bash
pip install cape-aeri  # the import name is still `aeri`: import aeri
```

For development:

```bash
pip install -e ".[test]"
```

## Quickstart

```python
import aeri

dictionary = aeri.dictionary.load("data/aeri_country_keywords.json")
articles = aeri.read_articles("path/to/Shak_Scrapped_Top_Articles")

scored = aeri.score_articles(articles, dictionary)

aeri_df = aeri.compute_aeri(scored)
diag = aeri.diagnostics(scored)
aeri_df = aeri.coverage_filter(aeri_df, diag)  # drop thin country-months
```

## Data format

`read_articles()` expects the on-disk layout produced by CAPE's scraper:

```
<root>/<Country>/<Publisher>/<YYYY-MM>/articles_<Publisher>_<YYYY-MM>.csv(.gz)
```

Each CSV has columns `site`, `date`, `title`, `url`, `text`. `country` is
not a column -- it's the top-level folder name, added by `read_articles()`
along with `year_month`.

`read_articles()` does **not** auto-canonicalize country folder names
(matching `newsindex`'s loader). A folder like `Morocco_new` is kept
distinct from `Morocco` rather than silently merged -- it may be a
deliberately separate re-scrape. Apply `aeri.countries.canonicalize()`
yourself once you've decided whether/how to merge it.

## Scoring pipeline

| Function | What it does |
| --- | --- |
| `normalize_text()` | Strip HTML; standardise case, whitespace and Unicode |
| `is_relevant()` | Economic relevance flag `R_i`, per the article's country dictionary |
| `severity_tier()` | Ordinal severity `S_i` from 0 to 4; the highest tier matched wins |
| `confidence_weight()` | `W_i = clip(1 + 0.5*TitleHint + 0.2*LongText + 0.3*MultiPillar, 1, 2)` |
| `assign_pillars()` | Flags for the 8 pillars; one article can activate several |
| `article_score()` | `A_i = R_i * S_i * W_i` |
| `compute_aeri()` | `AERI = 100 * sum(A_i) / N_t` for each country and month |
| `diagnostics()` | Total/relevant articles, relevant share, average confidence, average severity among relevant articles |
| `coverage_filter()` | Keeps country-months with at least 100 articles |

`score_articles()` runs the per-article functions over an articles
DataFrame in one pass. Relevance, severity and pillar matching run on the
article's **title and body concatenated** (`x_i = title + " " + text`),
and matching is **word-boundary aware** (`aeri.match`), not substring
search -- e.g. the severity term `"war"` does not match inside `"warning"`
or `"forward"`. `compute_aeri()` / `diagnostics()` output `Country`,
`Period` (`YYYY-MM`), `AERI`, `TotalArticles`, `RelevantArticles`,
`RelevantSharePct`, `AvgConfidence`, `AvgSeverityAmongRelevant` -- the
same column names as the production `aeri_country_period.csv` /
`aeri_diagnostics.csv` already consumed by the AERI Pillar API.

The 8 pillars (`aeri.config.PILLARS`) are named to match the Pillar API's
catalog: `InflationRisk`, `FXExternalRisk`, `DebtFiscalRisk`,
`FinancialSectorRisk`, `GrowthRealEconomyRisk`, `CommoditySupplyRisk`,
`PoliticalEconomyRisk`, `ClimateDisasterRisk`.

## Dictionaries

`data/aeri_country_keywords.json` is the real, production EPTU-schema
keyword dictionary (54 African countries, Economic/Policy/Uncertainty
term lists) shared with `newsindex`. `is_relevant()` defaults to the
Economic component alone for `R_i` -- **this default is an assumption**;
no source document specified whether Policy terms should also count
toward relevance. Add `"policy"` via `AERIConfig.relevance_components` to
include them:

```python
from aeri import AERIConfig
config = AERIConfig(relevance_components=("economic", "policy"))
```

The **severity-tier and pillar keyword lists have no equivalent
production source** -- nothing in the underlying research materials
defines them as keyword lists, only conceptually ("mild concern" through
"crisis-level language"). `aeri.config.DEFAULT_SEVERITY_KEYWORDS` and
`DEFAULT_PILLAR_KEYWORDS` are a first-pass, hand-curated starting point
that needs calibration before being treated as final. Every scoring
function takes an `AERIConfig` to override them without forking the
library.

The `TitleHint`/`LongText`/`MultiPillar` thresholds inside
`confidence_weight()` (title relevance; >=300 words; >=2 active pillars)
are likewise placeholders -- the exact numeric cutoffs used in the
original research were not found in any available source and need
confirmation.

## Roadmap

- Pillar composite indices and PCA-combined pillar measure (Library 2)
- `ars` composite score (Library 3): `ARS = 100 * (0.40*Intensity + 0.25*Breadth + 0.20*Severity + 0.15*Structure)`, risk bands at 20/40/60/80
- `riskalert` early-warning alerts (Library 4)

## Development

```bash
pip install -e ".[test]"
pytest
```
