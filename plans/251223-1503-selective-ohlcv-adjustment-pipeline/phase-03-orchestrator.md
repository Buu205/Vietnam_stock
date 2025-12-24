# Phase 03: Orchestrator Integration

## Objective

Integrate selective TA update into `ohlcv_adjustment_detector.py` with new `--cascade-selective` flag.

---

## Current State

```python
# ohlcv_adjustment_detector.py - current cascade
def _cascade_refresh_technical(self, n_sessions: int = 500):
    from PROCESSORS.pipelines.daily.daily_ta_complete import CompleteTAUpdatePipeline
    pipeline = CompleteTAUpdatePipeline()
    pipeline.run(n_sessions=n_sessions)  # Processes ALL 458 symbols
```

---

## Changes Required

### 1. Add `_cascade_refresh_selective()` method

```python
def _cascade_refresh_selective(self, symbols: List[str], n_sessions: int = 500):
    """
    Selective cascade refresh for affected symbols only.

    Steps:
    1. Recalc technical indicators for symbols
    2. Recalc alerts for symbols
    3. Recalc money flow for symbols
    4. ALWAYS recalc market breadth (full)
    """
    logger.info("=" * 60)
    logger.info(f"SELECTIVE CASCADE REFRESH: {len(symbols)} symbols")
    logger.info(f"Symbols: {', '.join(symbols[:10])}{'...' if len(symbols) > 10 else ''}")
    logger.info("=" * 60)

    try:
        from PROCESSORS.technical.indicators.technical_processor import TechnicalProcessor
        from PROCESSORS.technical.indicators.alert_detector import TechnicalAlertDetector
        from PROCESSORS.technical.indicators.money_flow import MoneyFlowAnalyzer

        # Step 1: Technical indicators (selective)
        logger.info("\n[1/4] Recalculating technical indicators...")
        processor = TechnicalProcessor()
        tech_df = processor.calculate_selective_indicators(symbols, n_sessions)
        if not tech_df.empty:
            processor.atomic_merge_basic_data(tech_df, symbols)
            logger.info(f"  ✅ Merged {len(symbols)} symbols into basic_data.parquet")

        # Step 2: Alerts (selective)
        logger.info("\n[2/4] Recalculating alerts...")
        detector = TechnicalAlertDetector()
        alerts = detector.detect_all_alerts(n_sessions=n_sessions, symbols=symbols)
        detector.merge_alerts_selective(alerts, symbols)
        logger.info(f"  ✅ Merged alerts for {len(symbols)} symbols")

        # Step 3: Money flow (selective)
        logger.info("\n[3/4] Recalculating money flow...")
        mf_analyzer = MoneyFlowAnalyzer()
        mf_df = mf_analyzer.calculate_all_money_flow(n_sessions=n_sessions, symbols=symbols)
        if not mf_df.empty:
            mf_analyzer.atomic_merge_money_flow(mf_df, symbols)
            logger.info(f"  ✅ Merged money flow for {len(symbols)} symbols")

        # Step 4: Market breadth (always full - needs all symbols for %)
        logger.info("\n[4/4] Recalculating market breadth (full)...")
        self._recalc_market_breadth()

        logger.info("\n✅ SELECTIVE CASCADE REFRESH COMPLETE")

    except Exception as e:
        logger.error(f"❌ Selective cascade failed: {e}")
        import traceback
        traceback.print_exc()

def _recalc_market_breadth(self):
    """Always full recalc - needs all symbols for % calculations."""
    from PROCESSORS.technical.indicators.sector_breadth import SectorBreadthAnalyzer
    from datetime import date

    breadth = SectorBreadthAnalyzer()
    df = breadth.calculate_sector_breadth(date=date.today())
    if not df.empty:
        breadth.save_sector_breadth(df)
        logger.info(f"  ✅ Market breadth recalculated")
```

### 2. Update `run()` method

Add `cascade_selective` parameter:

```python
def run(
    self,
    detect: bool = True,
    refresh: bool = False,
    symbols: Optional[List[str]] = None,
    dry_run: bool = False,
    threshold: Optional[float] = None,
    cascade: bool = False,
    cascade_selective: bool = False  # NEW
) -> Dict:
    ...

    # At end of refresh block:
    if cascade_selective and not dry_run and results['refresh']['success'] > 0:
        # Get list of symbols that were refreshed
        refreshed_symbols = results['refresh']['symbols_refreshed']
        self._cascade_refresh_selective(refreshed_symbols)
        results['cascade'] = True
        results['cascade_mode'] = 'selective'
    elif cascade and not dry_run and results['refresh']['success'] > 0:
        self._cascade_refresh_technical()
        results['cascade'] = True
        results['cascade_mode'] = 'full'
```

### 3. Update CLI

```python
parser.add_argument(
    '--cascade-selective',
    action='store_true',
    help='Selective cascade: only refresh TA for affected symbols (faster)'
)

# In main():
results = detector.run(
    ...
    cascade=args.cascade,
    cascade_selective=args.cascade_selective
)
```

---

## CLI Usage

```bash
# Full pipeline with selective cascade (RECOMMENDED)
python ohlcv_adjustment_detector.py --detect --refresh --cascade-selective

# Full pipeline with full cascade (slow, legacy)
python ohlcv_adjustment_detector.py --detect --refresh --cascade

# Force specific symbols with selective cascade
python ohlcv_adjustment_detector.py --symbols CTG,HDB --refresh --cascade-selective

# Detection only
python ohlcv_adjustment_detector.py --detect
```

---

## Validation Checklist

- [ ] `--cascade-selective` processes only detected/specified symbols
- [ ] basic_data.parquet row count unchanged after selective update
- [ ] Alerts for non-affected symbols preserved
- [ ] Money flow for non-affected symbols preserved
- [ ] Market breadth always recalculated
- [ ] Performance: ~15s for 20 symbols (vs 180s full)

---

## Test Commands

```bash
# Test selective with 3 symbols
python ohlcv_adjustment_detector.py --symbols ACB,VCB,TCB --refresh --cascade-selective

# Verify data integrity
python -c "
import pandas as pd
df = pd.read_parquet('DATA/processed/technical/basic_data.parquet')
print(f'Total symbols: {df.symbol.nunique()}')
print(f'Total rows: {len(df)}')
print(df[df.symbol.isin(['ACB','VCB','TCB'])].groupby('symbol').size())
"
```

---

## Dependencies

- Phase 01: TechnicalProcessor selective mode
- Phase 02: AlertDetector + MoneyFlowAnalyzer selective mode
