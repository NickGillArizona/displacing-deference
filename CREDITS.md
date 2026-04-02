# Credits and Attributions

## Data Sources

**CourtListener / Free Law Project**
Court opinion text was obtained via the [CourtListener REST API v4](https://www.courtlistener.com/api/rest/v4/), provided by the [Free Law Project](https://free.law). CourtListener is a free, open platform for legal data maintained by the Free Law Project, a 501(c)(3) nonprofit. If you use data derived from CourtListener, please attribute the Free Law Project accordingly.

**U.S. Census Bureau**
Housing cost-burden and disability analyses use data from the U.S. Census Bureau, [American Community Survey 2020-2024 5-Year Public Use Microdata Sample](https://api.census.gov/data/2024/acs/acs5/pums). The Census Bureau requires the following disclaimer: "This product uses the Census Bureau Data API but is not endorsed or certified by the Census Bureau."

**OpenRouter**
Multi-model LLM access for the classification pipeline was provided through the [OpenRouter API](https://openrouter.ai/). Individual model attributions (MiniMax M2.7, DeepSeek V3.2, Kimi K2.5, Claude Haiku 4.5, Claude Sonnet 4.6, Claude Opus 4.6) are documented in [`pipeline/model_configuration.md`](pipeline/model_configuration.md).

## Software Dependencies

This project relies on open-source Python libraries distributed under permissive licenses:

| Package | License |
|---------|---------|
| pandas | BSD 3-Clause |
| numpy | BSD 3-Clause |
| scipy | BSD 3-Clause |
| statsmodels | BSD 3-Clause |
| requests | Apache 2.0 |
| httpx | BSD 3-Clause |
| openpyxl | MIT |
| python-dotenv | BSD 3-Clause |
