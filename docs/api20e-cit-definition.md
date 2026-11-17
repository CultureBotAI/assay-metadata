# API 20E CIT procedure definition

The manufacturer identifies the CIT well as a citrate utilization test. The
previous shared chemical description combined utilization and fermentation,
which does not distinguish this well's procedure. The simplified exporter now
uses a description scoped to API 20E CIT. Other kits and global well records
retain their existing descriptions pending their own source review.

Source: bioMerieux API 20 E insert, revision 07584J, 2010/05, multilingual
reading table IV, PDF page 8:
[manufacturer insert hosted by Jeulin](https://jeulin.com/media/akeneo_connector/asset_files/F/i/Fiche_Biomerieux_Galerie_API_20E_117389_FR_3910.pdf).
The CIT row names trisodium citrate and citrate utilization. It lists pale
green/yellow as negative and blue-green/blue as positive, with reading in the
aerobic cupule. This defines a procedure and readout, without asserting any
organism result or changing the imported chemical identifiers.

Captured privately during EdgeMech round02 on 2026-11-16 via CBORG Tavily,
request `26950591-035a-4f21-b3e5-66e8df8b1843`. The source document is not
redistributed in this repository. Related tracking: CultureBotAI/EdgeMech#166.

Run `python -m pytest -q` for the CLI export regression. Refresh the retained
simplified JSON with `python scripts/adhoc/refresh_api20e_cit_20261116.py --input
data/assay_kits_simple.json`. A bounded input is used before the full derivative;
the script preserves all other records and verifies the expected single well.
The historical EdgeMech sampled node remains unchanged.
