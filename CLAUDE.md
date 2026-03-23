# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

VectorBT Playground — a stock backtesting tool. The backend exposes a single `POST /backtest/run` API that fetches historical OHLCV data from Yahoo Finance, runs a chosen trading strategy, and returns candlestick data, trade signals, indicator lines, and performance stats. The frontend renders this as an interactive chart.

## Commands

### Backend

```bash
# Dev server (hot reload)
uv run uvicorn main:app --reload
# API docs available at http://127.0.0.1:8000/docs

# Production (single server, serves frontend + API)
cd frontend && npm run build   # outputs to ../static/
cd ..
uv run uvicorn main:app
```

### Frontend

```bash
cd frontend
npm install       # first time
npm run dev       # dev server on http://localhost:5173
npm run build     # production build
npm run lint      # ESLint check
```

### Tests

```bash
uv run pytest                                          # all tests
uv run pytest tests/strategies/test_ma_cross.py       # single file
uv run pytest tests/strategies/test_ma_cross.py::TestMACrossSignals::test_golden_cross  # single test
```

### Load Testing (Locust)

```bash
# Start backend first, then:
uv run locust -f tests/locustfile.py --host=http://127.0.0.1:8000
# Open http://localhost:8089 to configure and start
```

## Architecture

### Request Flow

```
Frontend (React/Vite :5173)
  -> POST /backtest/run
  -> app/api/routes/backtest.py   (Pydantic validation, BacktestRequest -> BacktestConfig)
  -> app/services/backtest.py     (orchestrates: fetch data -> generate signals -> run portfolio -> serialize)
  -> app/services/data.py         (Yahoo Finance via vbt.YFData.download)
  -> app/strategies/<name>.py     (generate_signals + generate_indicators)
  -> vectorbt.Portfolio.from_signals
  <- returns { ohlcv, signals, trades, indicators, stats }
```

### Strategy System

All strategies live in `app/strategies/` and inherit `BaseStrategy` (`base.py`):

- `generate_signals(price, params, ohlcv) -> (entries, exits)` — **required**: returns two boolean pandas Series
- `generate_indicators(price, params, ohlcv) -> list[dict]` — **optional**: returns overlay lines for the chart

Strategies are registered by name in `app/strategies/__init__.py` (`STRATEGY_REGISTRY`). The same names must also appear in `frontend/src/strategies.ts` (`STRATEGIES` array) for them to show up in the UI.

**Adding a new strategy:**
1. Create `app/strategies/<name>.py`, subclass `BaseStrategy`
2. Add to `STRATEGY_REGISTRY` in `app/strategies/__init__.py`
3. Add a `StrategyMeta` entry to `STRATEGIES` in `frontend/src/strategies.ts`

### Frontend Structure

- `src/strategies.ts` — strategy metadata and parameter definitions (single source of truth for the UI)
- `src/api.ts` — API client
- `src/types.ts` — shared TypeScript types
- `src/pages/` — `StrategyList` (home) and `StrategyPage` (backtest view)
- `src/components/` — `Chart` (lightweight-charts candlestick), `StatsPanel`, `TradesTable`, `BacktestForm`, `StrategyForm`
- `src/i18n/` — i18n strings in `en.ts` and `zh.ts`; toggle via `LangToggle`

### Key Notes

- `_sanitize()` in `app/services/backtest.py` recursively converts all numpy/pandas types and NaN/Inf to JSON-safe Python primitives — call it on any new result dict fields.
- `indicator` data format expected by the frontend chart: `{ name: str, color: str, data: [{time: "YYYY-MM-DD", value: float}] }`.
- CORS is locked to `http://localhost:5173` in `main.py`.
- Package management uses `uv` (see `pyproject.toml`); dev dependencies (pytest, locust) are in the `[dependency-groups] dev` group.
