# Get your Valorant MMR

## Requirements

Python 2.7 or Python 3.7+

## Usage

Download the script and run `python valorant_mmr.py` (Python 2) or `python valorant_mmr3.py` (Python 3) in your terminal.

## Rating calculation

Valorant does not provide a single MMR number. Instead, it tells you your tier (rank) plus your tier progress (out of 100).

The tiers start with Iron I = 3, up to Radiant = 24. This script calculates your MMR as `tier * 100 + progress`, so Iron I goes from 300 to 399. This might be different from other calculations that set tier 3 to 0 MMR. You would need to subtract 300 from the MMR that this script gives.
