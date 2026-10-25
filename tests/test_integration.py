import gzip

from aeri.articles import read_articles
from aeri.dictionary import CountryDictionary, Dictionary
from aeri.index import compute_aeri, coverage_filter, diagnostics
from aeri.scoring import score_articles

NIGERIA_CSV = (
    "site,date,title,url,text\n"
    'Business Day,2026-03-01,"Inflation crisis deepens",'
    '"https://example.com/a","<p>Inflation and currency devaluation triggered an economic crisis.</p>"\n'
    'Business Day,2026-03-05,"Local football result",'
    '"https://example.com/b","The home team won 2-1 on Saturday afternoon."\n'
)

DICTIONARY = Dictionary(
    countries={
        "Nigeria": CountryDictionary(
            country="Nigeria",
            languages=("en",),
            economic=("inflation", "devaluation", "naira"),
            policy=(),
            uncertainty=(),
        )
    }
)


def test_end_to_end_pipeline(tmp_path):
    article_dir = tmp_path / "Nigeria" / "Business Day" / "2026-03"
    article_dir.mkdir(parents=True)
    with gzip.open(
        article_dir / "articles_Business Day_2026-03.csv.gz", "wt", encoding="utf-8"
    ) as fh:
        fh.write(NIGERIA_CSV)

    articles = read_articles(tmp_path)
    scored = score_articles(articles, DICTIONARY)

    aeri_df = compute_aeri(scored)
    diag = diagnostics(scored)

    assert list(aeri_df.columns) == ["Country", "Period", "AERI"]
    assert aeri_df.loc[0, "Country"] == "Nigeria"
    assert aeri_df.loc[0, "Period"] == "2026-03"
    assert aeri_df.loc[0, "AERI"] > 0

    assert diag.loc[0, "TotalArticles"] == 2
    assert diag.loc[0, "RelevantArticles"] == 1
    assert diag.loc[0, "RelevantSharePct"] == 50.0

    filtered = coverage_filter(aeri_df, diag, min_articles=2)
    assert len(filtered) == 1
    filtered_none = coverage_filter(aeri_df, diag, min_articles=100)
    assert len(filtered_none) == 0
