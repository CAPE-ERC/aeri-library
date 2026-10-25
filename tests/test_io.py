import gzip

import pandas as pd

from aeri.io import load_articles_csv, load_articles_tree

CSV_BODY = (
    "site,date,title,url,text\n"
    'Business Day,2026-03-01,"Inflation rises","https://example.com/a","<p>Inflation news</p>"\n'
    'Business Day,2026-03-05,"Football result","https://example.com/b","Local match report"\n'
)


def _write_tree(tmp_path):
    article_dir = tmp_path / "Nigeria" / "Business Day" / "2026-03"
    article_dir.mkdir(parents=True)
    csv_path = article_dir / "articles_Business Day_2026-03.csv.gz"
    with gzip.open(csv_path, "wt", encoding="utf-8") as fh:
        fh.write(CSV_BODY)
    return tmp_path, csv_path


def test_load_articles_csv_infers_country_from_path(tmp_path):
    _, csv_path = _write_tree(tmp_path)
    df = load_articles_csv(csv_path)
    assert list(df["country"].unique()) == ["Nigeria"]
    assert len(df) == 2
    assert set(["country", "site", "date", "title", "url", "text", "source_file"]).issubset(df.columns)


def test_load_articles_csv_raises_on_missing_columns(tmp_path):
    bad_path = tmp_path / "bad.csv"
    bad_path.write_text("a,b\n1,2\n", encoding="utf-8")
    try:
        load_articles_csv(bad_path)
        assert False, "expected ValueError"
    except ValueError:
        pass


def test_load_articles_tree_concatenates_all_matches(tmp_path):
    root, _ = _write_tree(tmp_path)
    extra_dir = root / "Ghana" / "Daily Graphic" / "2026-04"
    extra_dir.mkdir(parents=True)
    extra_path = extra_dir / "articles_Daily Graphic_2026-04.csv.gz"
    with gzip.open(extra_path, "wt", encoding="utf-8") as fh:
        fh.write(CSV_BODY)

    df = load_articles_tree(root)
    assert len(df) == 4
    assert set(df["country"]) == {"Nigeria", "Ghana"}


def test_load_articles_tree_empty_root_returns_empty_frame(tmp_path):
    df = load_articles_tree(tmp_path)
    assert isinstance(df, pd.DataFrame)
    assert len(df) == 0
