import gzip

import pytest

from aeri.articles import read_articles

CSV_BODY = (
    "site,date,title,url,text\n"
    'Business Day,2026-03-01,"Inflation rises","https://example.com/a","<p>Inflation &amp; news</p>"\n'
    'Business Day,2026-03-05,"Football result","https://example.com/b","Local match report"\n'
)


def _write_tree(tmp_path):
    article_dir = tmp_path / "Nigeria" / "Business Day" / "2026-03"
    article_dir.mkdir(parents=True)
    csv_path = article_dir / "articles_Business Day_2026-03.csv.gz"
    with gzip.open(csv_path, "wt", encoding="utf-8") as fh:
        fh.write(CSV_BODY)
    return tmp_path


def test_read_articles_infers_country_and_year_month(tmp_path):
    root = _write_tree(tmp_path)
    df = read_articles(root)
    assert list(df["country"].unique()) == ["Nigeria"]
    assert list(df["year_month"].unique()) == ["2026-03"]
    assert len(df) == 2


def test_read_articles_unescapes_html_entities(tmp_path):
    root = _write_tree(tmp_path)
    df = read_articles(root)
    assert df.loc[0, "text"] == "<p>Inflation & news</p>"


def test_read_articles_raises_on_missing_columns(tmp_path):
    bad_dir = tmp_path / "Nigeria" / "Site" / "2026-03"
    bad_dir.mkdir(parents=True)
    (bad_dir / "articles_Site_2026-03.csv").write_text("a,b\n1,2\n", encoding="utf-8")
    with pytest.raises(ValueError):
        read_articles(tmp_path)


def test_read_articles_raises_when_nothing_found(tmp_path):
    with pytest.raises(FileNotFoundError):
        read_articles(tmp_path)


def test_read_articles_concatenates_all_matches(tmp_path):
    root = _write_tree(tmp_path)
    extra_dir = root / "Ghana" / "Daily Graphic" / "2026-04"
    extra_dir.mkdir(parents=True)
    extra_path = extra_dir / "articles_Daily Graphic_2026-04.csv.gz"
    with gzip.open(extra_path, "wt", encoding="utf-8") as fh:
        fh.write(CSV_BODY)

    df = read_articles(root)
    assert len(df) == 4
    assert set(df["country"]) == {"Nigeria", "Ghana"}


def test_read_articles_does_not_canonicalize_country_folder_names(tmp_path):
    article_dir = tmp_path / "Morocco_new" / "Site" / "2026-03"
    article_dir.mkdir(parents=True)
    (article_dir / "articles_Site_2026-03.csv").write_text(CSV_BODY, encoding="utf-8")
    df = read_articles(tmp_path)
    assert list(df["country"].unique()) == ["Morocco_new"]
