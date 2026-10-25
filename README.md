# aeri

AERI article scoring and country-month economic-risk index library, built
from the AERI/ARS work at CAPE Economic Research and Consulting.

This covers **Libraries 1 and 2** from the proposal: scoring each scraped
news article, rolling the scores up into the country-month AERI (Africa
Economic Risk Index), and the eight pillar indices plus their
PCA-combined composite. The ARS composite score and early-warning alerts
(Libraries 3-4) are planned as follow-up PRs on top of this foundation.
Matching conventions, data layout and output schema are kept consistent
with the sibling
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

pillars_df = aeri.pillar_indices(scored)
composite = aeri.pillar_composite(aeri.transform_pillars(pillars_df))
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

## Pillar composite (`aeri.pillars`)

Per-article pillar flagging (`assign_pillars()`, Library 1) and the
country-month pillar-composite pipeline (Library 2) both live under
`aeri.pillars`:

| Function | What it does |
| --- | --- |
| `pillar_indices()` | `Pillar_p = 100 * sum(A_i * I_p,i) / N` for each of the 8 pillars |
| `active_pillars()` | Number of pillars with a positive index, per country-month |
| `transform_pillars()` | `log(1 + P)`, scaled to 0-1 between frozen 1st/99th-percentile bounds |
| `calibrate_pillar_weights()` | First-principal-component weights for the 8 pillars |
| `pillar_composite()` | `H_t = sum_p(100 * u_p * Q_p)`, the combined cross-pillar measure |
| `rank_pillars()` | Ranks one country-period's pillars by raw index value, descending |

```python
pillars_df = aeri.pillar_indices(scored)
coverage = aeri.active_pillars(pillars_df)       # ActivePillars per country-month
transformed = aeri.transform_pillars(pillars_df)  # Q in [0, 1], frozen bounds
composite = aeri.pillar_composite(transformed)    # PillarComposite, frozen weights
```

The frozen 1st/99th-percentile bounds (`DEFAULT_LOG_LOWER`/`DEFAULT_LOG_UPPER`)
and PCA weights (`DEFAULT_PILLAR_WEIGHTS`) are sourced directly from the
full AERI/ARS paper (Table 4): calibrated on 6,238 country-months with
>=100 articles, Jan 2015-Jul 2025 (PC1 explains 52.50% of standardised
variance). `fit_transform_bounds()` and `calibrate_pillar_weights()`
recompute both from a different panel if needed; `calibrate_pillar_weights()`
raises `MixedSignLoadingsError` if the panel doesn't support a single
coherent "overall risk" direction (any negative loading after orientation).

`rank_pillars()` has no documented methodology beyond "sort descending" --
the paper's own pillar ranking is a pooled, cross-sample average (Table 6
/ Figure 5), not a single-country-period function, so this is implemented
as a straightforward per-row sort with nothing further to calibrate.

## Dictionaries

`data/aeri_country_keywords.json` is the real, production EPTU-schema
keyword dictionary (54 African countries, Economic/Policy/Uncertainty
term lists) shared with `newsindex`. `is_relevant()` uses the Economic
component alone for `R_i` (confirmed: there's no source information to
justify also counting Policy terms). `AERIConfig.relevance_components`
remains overridable if that changes:

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

- `ars` composite score (Library 3): `ARS = 100 * (0.40*Intensity + 0.25*Breadth + 0.20*Severity + 0.15*Structure)`, risk bands at 20/40/60/80
- `riskalert` early-warning alerts (Library 4)

## Development

```bash
pip install -e ".[test]"
pytest
```
