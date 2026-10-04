"""Tidy the UK Official Albums Chart workbook (author-supplied) for the cross-country comparison.

Raw file: data/raw/uktop100albums.xlsx, one sheet per chart week ("Week YYYYMMDD", the Sunday
the chart week starts; 1956-07-29 to 2025-08-03), columns Album, Artist, Position, Last Week
("LW:n", "LW:New", "LW:RE"), Peak, Weeks on Chart, Week. Quirks handled here:
- New entries have "New" glued to the front of the title ("NewROCK AROUND THE CLOCK"); it
  appears exactly when Last Week is "LW:New" and is stripped.
- The #1 album is missing from almost every week since 1959 (positions 2-100 only). It is
  rebuilt from later weeks: the #1 of week t is the album marked "LW:1" in the first later week
  that has one (no "LW:1" row means the #1 stayed at #1 and is missing again). Its weeks on
  chart at t = weeks on chart then minus the number of weeks elapsed. If that is below 1, the
  #1 of week t left the top 100 the next week and cannot be identified; it is recorded as an
  unidentified new entry (all such cases are after 2020).
The UK added streams to the albums chart from the chart published Sunday 1 March 2015
(sheet "Week 20150301"). Output covers 2000 onward.
"""

import openpyxl
import pandas as pd

from paths import FINAL_DIR, RAW_UK_ALBUMS, UK_ALBUMS_WEEKLY

START = "2000-01-01"


def read_workbook():
    workbook = openpyxl.load_workbook(RAW_UK_ALBUMS, read_only=True)
    frames = []
    for sheet in workbook.worksheets:
        rows = list(sheet.iter_rows(values_only=True))
        assert rows[0] == ("Album", "Artist", "Position", "Last Week", "Peak", "Weeks on Chart", "Week"), sheet.title
        frame = pd.DataFrame(rows[1:], columns=rows[0])
        frame["chart_week"] = pd.to_datetime(sheet.title.replace("Week ", ""), format="%Y%m%d")
        frames.append(frame)
    data = pd.concat(frames, ignore_index=True)
    return data[data["chart_week"] >= START].copy()


def tidy(data):
    data = data.astype({"Album": str, "Artist": str, "Last Week": str})
    data["position"] = pd.to_numeric(data["Position"]).astype(int)
    data["peak"] = pd.to_numeric(data["Peak"]).astype(int)
    data["weeks_on_chart"] = pd.to_numeric(data["Weeks on Chart"]).astype(int)
    last = data["Last Week"].str.replace("LW:", "", regex=False)
    data["status"] = last.map({"New": "new", "RE": "re-entry"}).fillna("continuing")
    data["last_week"] = pd.to_numeric(last, errors="coerce")
    is_new = data["status"] == "new"
    assert data.loc[is_new, "Album"].str.startswith("New").all()
    data.loc[is_new, "Album"] = data.loc[is_new, "Album"].str[3:]
    data = data.rename(columns={"Album": "album", "Artist": "artist"})
    data["no1_rebuilt"] = False
    data["no1_unidentified"] = False
    return data[["chart_week", "position", "album", "artist", "status", "last_week", "peak", "weeks_on_chart",
                 "no1_rebuilt", "no1_unidentified"]]


def rebuild_number_ones(data):
    weeks = sorted(data["chart_week"].unique())
    previous = dict(zip(weeks[1:], weeks[:-1]))
    has_one = set(data.loc[data["position"] == 1, "chart_week"])
    marked = data[data["last_week"] == 1].set_index("chart_week")
    present = {(w, a, b): p for w, a, b, p in zip(data["chart_week"], data["album"], data["artist"], data["position"])}
    rebuilt = {}
    for i, week in enumerate(weeks[:-1]):
        if week in has_one:
            continue
        for k in range(1, len(weeks) - i):
            later = weeks[i + k]
            if later in marked.index:
                row = marked.loc[later]
                rebuilt[week] = (row["album"], row["artist"], int(row["weeks_on_chart"]) - k)
                break
    rows = []
    for week in weeks[:-1]:
        if week not in rebuilt:
            continue
        album, artist, woc = rebuilt[week]
        if woc < 1:
            rows.append({"chart_week": week, "position": 1, "album": "", "artist": "", "status": "new",
                         "peak": 1, "weeks_on_chart": 1, "no1_rebuilt": True, "no1_unidentified": True})
            continue
        before = previous.get(week)
        last = present.get((before, album, artist))
        if last is None and before in rebuilt and rebuilt[before][:2] == (album, artist) and rebuilt[before][2] >= 1:
            last = 1
        status = "new" if woc == 1 else ("continuing" if last is not None else "re-entry")
        rows.append({"chart_week": week, "position": 1, "album": album, "artist": artist, "status": status,
                     "last_week": last, "peak": 1, "weeks_on_chart": woc, "no1_rebuilt": True, "no1_unidentified": False})
    out = pd.concat([data, pd.DataFrame(rows)], ignore_index=True)
    return out.sort_values(["chart_week", "position"]).reset_index(drop=True)


def main():
    data = rebuild_number_ones(tidy(read_workbook()))
    final_week = data["chart_week"].max()
    sizes = data.groupby("chart_week").size()
    print(f"{len(data)} rows, {data['chart_week'].nunique()} weeks, {data['chart_week'].min().date()} to {final_week.date()}")
    print("chart length:", sizes.value_counts().to_dict(), f"(final week {final_week.date()} has no later week to rebuild its #1)")
    print("rebuilt #1s:", int(data["no1_rebuilt"].sum()), "| unidentified:",
          data.loc[data["no1_unidentified"], "chart_week"].dt.date.astype(str).tolist())
    window = data[data["chart_week"].between("2010-01-01", "2019-12-31")]
    print("2010-2019: weeks", window["chart_week"].nunique(), "| unidentified #1s", int(window["no1_unidentified"].sum()),
          "| #1 status:", window.loc[window["position"] == 1, "status"].value_counts().to_dict())
    FINAL_DIR.mkdir(parents=True, exist_ok=True)
    data.to_csv(UK_ALBUMS_WEEKLY, index=False)


if __name__ == "__main__":
    main()
