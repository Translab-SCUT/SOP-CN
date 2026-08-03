"""Print selected public PEV shares without running the private SOP-CN model."""

from pathlib import Path

from sopcn_public import load_public_market_shares, milestone_table, with_pev_share

ROOT = Path(__file__).resolve().parents[1]
DATA_PATH = ROOT / "data/public/national_market_share_2021_2060.csv"

data = with_pev_share(load_public_market_shares(DATA_PATH))
summary = milestone_table(data, years=(2025, 2035, 2050, 2060))
print(summary[["Market", "Year", "PEV_share_pct"]].to_string(index=False))

