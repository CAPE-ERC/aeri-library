"""Loaders for the scraped-article corpus.

Expects the on-disk layout used by the CAPE scraper exports:

    <root>/<Country>/<Publisher>/<YYYY-MM>/articles_<Publisher>_<YYYY-MM>.csv(.gz)

Each CSV has columns: site, date, title, url, text. `country` is not a
column in the CSV -- it is inferred from the top-level folder name.
"""

from __future__ import annotations

from pathlib import Path

import pandas as pd

REQUIRED_COLUMNS = ("site", "date", "title", "url", "text")


def load_articles_csv(path: str | Path, country: str | None = None) -> pd.DataFrame:
    """Load a single `articles_*.csv` or `articles_*.csv.gz` file.

    If `country` is not given, it is inferred as the name of the
    grandparent-of-grandparent directory (`<root>/<Country>/<Publisher>/<month>/file`),
    falling back to None if the path is too shallow.
    """
    path = Path(path)
    df = pd.read_csv(path, compression="infer")

    missing = set(REQUIRED_COLUMNS) - set(df.columns)
    if missing:
        raise ValueError(f"{path} is missing expected columns: {sorted(missing)}")

    if country is None:
        parts = path.parts
        country = parts[-4] if len(parts) >= 4 else None

    df.insert(0, "country", country)
    df["source_file"] = str(path)
    return df


def load_articles_tree(root: str | Path, pattern: str = "articles_*.csv*") -> pd.DataFrame:
    """Walk `root` (the `Shak_Scrapped_Top_Articles`-style export tree) and
    concatenate every matching CSV into a single DataFrame.

    Country is inferred per-file from the first path segment under `root`.
    """
    root = Path(root)
    frames: list[pd.DataFrame] = []
    for file_path in sorted(root.rglob(pattern)):
        relative = file_path.relative_to(root)
        country = relative.parts[0] if relative.parts else None
        frames.append(load_articles_csv(file_path, country=country))

    if not frames:
        return pd.DataFrame(columns=["country", *REQUIRED_COLUMNS, "source_file"])

    return pd.concat(frames, ignore_index=True)
