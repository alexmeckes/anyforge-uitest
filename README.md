<div align="center">

# any-forge

[![Docs](https://github.com/mozilla-ai/any-forge/actions/workflows/docs.yaml/badge.svg)](https://github.com/mozilla-ai/any-forge/actions/workflows/docs.yaml/)
[![Linting](https://github.com/mozilla-ai/any-forge/actions/workflows/lint.yaml/badge.svg)](https://github.com/mozilla-ai/any-forge/actions/workflows/lint.yaml/)
[![Unit Tests](https://github.com/mozilla-ai/any-forge/actions/workflows/tests-unit.yaml/badge.svg)](https://github.com/mozilla-ai/any-forge/actions/workflows/tests-unit.yaml/)
[![Integration Tests](https://github.com/mozilla-ai/any-forge/actions/workflows/tests-integration.yaml/badge.svg)](https://github.com/mozilla-ai/any-forge/actions/workflows/tests-integration.yaml/)

![Python 3.11+](https://img.shields.io/badge/python-3.11%2B-blue.svg)
<a href="https://discord.gg/4gf3zXrQUc">
    <img src="https://img.shields.io/static/v1?label=Chat%20on&message=Discord&color=blue&logo=Discord&style=flat-square" alt="Discord">
</a>

</div>

## [Documentation](https://mozilla-ai.github.io/any-forge/)


## Quickstart

### Requirements

- Python 3.11 or newer
- API_KEYS to access whichever LLM + provider you want to use
- We use UV for python version management

### Install

```bash
uv venv
source .venv/bin/activate
uv sync --all-extras -U --python=3.13
```

### Run the Web App

```
streamlit run streamlit_app.py
```
