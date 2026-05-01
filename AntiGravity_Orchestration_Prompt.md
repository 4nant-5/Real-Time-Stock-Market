# AntiGravity Real-Time Stock Analytics Pipeline — Orchestration Implementation Prompt

---

## CONTEXT & GOAL

You are building a **real-time stock analytics pipeline** that fetches live stock data, computes technical indicators, generates ML predictions, stores results, and visualizes insights in Power BI—all **automatically, reliably, and on schedule**.

Currently, your pipeline tasks (data ingestion, processing, modeling, storage, visualization) run independently. **Your goal**: Transform this into a unified, orchestrated system where tasks run in the correct sequence, handle failures gracefully, and require zero manual intervention.

---

## WHAT YOU NEED TO BUILD

### 1. **Modular Task Scripts** (If not already done)
Create independent Python scripts for each pipeline step:

```
project/
├── scripts/
│   ├── fetch_data.py           # Fetch stock data from Yahoo Finance
│   ├── compute_indicators.py   # Calculate technical indicators
│   ├── generate_predictions.py # Run ML models
│   ├── update_storage.py       # Write to database/cache
│   └── sync_visualization.py   # Refresh Power BI
├── config/
│   └── pipeline_config.yaml    # Centralized configuration
├── logs/
│   └── pipeline.log            # Execution logs
└── orchestrator.py             # Main orchestration script
```

**Requirements for each script**:
- Accept parameters (tickers, dates, intervals, paths)
- Return clear status: success/failure with details
- Include logging: `logging.info()`, `logging.error()`
- Handle errors gracefully: Raise exceptions, don't silently fail
- Be idempotent: Running twice with same inputs = same output (no side effects)

**Example structure**:
```python
# fetch_data.py
import logging

def fetch_stock_data(tickers, interval='5m'):
    """Fetch live stock data from Yahoo Finance."""
    logging.info(f"Fetching data for {tickers}")
    try:
        # YOUR CODE: Pull from Yahoo Finance
        data = yf.download(tickers, interval=interval)
        logging.info(f"Successfully fetched {len(data)} rows")
        return data
    except Exception as e:
        logging.error(f"Fetch failed: {e}")
        raise
```

---

### 2. **Configuration File** (YAML)
Create a single source of truth for pipeline settings:

```yaml
# config/pipeline_config.yaml

pipeline:
  name: "AntiGravity Stock Analytics"
  schedule:
    # Run every 5 minutes during market hours (9 AM–4 PM ET, Mon–Fri)
    interval_minutes: 5
    market_hours_only: true
    market_open_hour: 9
    market_close_hour: 16
    market_timezone: "America/New_York"
    active_days: [0, 1, 2, 3, 4]  # Monday=0, Friday=4
  
  # Global error handling
  retries: 3
  retry_delay_seconds: 30
  task_timeout_seconds: 300
  
  # Logging
  log_level: "INFO"
  log_file: "logs/pipeline.log"

# Task-specific configuration
tasks:
  fetch_data:
    enabled: true
    timeout_seconds: 30
    retries: 3
    tickers: ['AAPL', 'MSFT', 'GOOGL', 'TSLA', 'AMZN']
    data_source: 'yahoo_finance'
  
  compute_indicators:
    enabled: true
    timeout_seconds: 60
    retries: 2
    technical_indicators:
      - name: 'SMA'
        periods: [20, 50, 200]
      - name: 'RSI'
        period: 14
      - name: 'MACD'
        fast: 12
        slow: 26
      - name: 'Bollinger_Bands'
        period: 20
        std_dev: 2
  
  generate_predictions:
    enabled: true
    timeout_seconds: 120
    retries: 2
    model_path: 'models/xgboost_v2.pkl'
    confidence_threshold: 0.65
    prediction_types: ['price_direction', 'volatility', 'support_resistance']
  
  update_storage:
    enabled: true
    timeout_seconds: 45
    retries: 3
    database:
      type: 'postgresql'  # or 'sqlite', 'mysql', 'mongodb'
      connection_string: 'postgresql://user:pass@localhost/antigravity'
    cache:
      type: 'redis'
      connection_string: 'redis://localhost:6379'
  
  sync_visualization:
    enabled: true
    timeout_seconds: 60
    retries: 2
    power_bi:
      workspace_id: 'YOUR_WORKSPACE_ID'
      dataset_id: 'YOUR_DATASET_ID'
      refresh_endpoint: 'https://api.powerbi.com/v1.0/myorg/datasets/{dataset_id}/refreshes'
    alert_on_signals:
      enabled: true
      slack_webhook: 'https://hooks.slack.com/services/YOUR_WEBHOOK'

# Monitoring & Alerting
monitoring:
  alert_channels:
    - type: 'slack'
      webhook_url: 'YOUR_SLACK_WEBHOOK'
      notify_on: ['failure', 'sla_breach']
    - type: 'email'
      recipients: ['team@antigravity.com']
      notify_on: ['failure']
  
  metrics:
    track_execution_time: true
    track_success_rate: true
    sla_target_minutes: 5  # Pipeline should complete within 5 minutes
```

---

### 3. **Orchestrator Script** (Python with APScheduler)
This is the **core orchestration engine** that schedules, runs, and monitors all tasks.

**Start here** (Phase 1 — Lightweight, runs on single machine):

```python
# orchestrator.py
import yaml
import logging
import sys
from datetime import datetime
from apscheduler.schedulers.background import BackgroundScheduler
from apscheduler.triggers.cron import CronTrigger
import pytz

# Import your task scripts
from scripts.fetch_data import fetch_stock_data
from scripts.compute_indicators import compute_indicators
from scripts.generate_predictions import generate_predictions
from scripts.update_storage import update_storage
from scripts.sync_visualization import sync_visualization

# ============================================
# SETUP LOGGING
# ============================================
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('logs/pipeline.log'),
        logging.StreamHandler(sys.stdout)
    ]
)
logger = logging.getLogger('orchestrator')

# ============================================
# LOAD CONFIGURATION
# ============================================
def load_config(config_path='config/pipeline_config.yaml'):
    """Load pipeline configuration from YAML."""
    with open(config_path, 'r') as f:
        config = yaml.safe_load(f)
    return config

# ============================================
# PIPELINE EXECUTION
# ============================================
class PipelineOrchestrator:
    def __init__(self, config):
        self.config = config
        self.scheduler = BackgroundScheduler()
        self.run_id = None
        self.run_status = {}
    
    def run_pipeline(self):
        """Execute the complete pipeline with dependency management."""
        self.run_id = datetime.utcnow().strftime('%Y%m%d_%H%M%S')
        logger.info(f"[{self.run_id}] Starting pipeline execution")
        
        try:
            # Task 1: Fetch Data (Entry point)
            if self.config['tasks']['fetch_data']['enabled']:
                logger.info(f"[{self.run_id}] Task 1/5: Fetching data...")
                data = self._run_task_with_retry(
                    fetch_stock_data,
                    self.config['tasks']['fetch_data'],
                    tickers=self.config['tasks']['fetch_data']['tickers']
                )
                self.run_status['fetch_data'] = 'success'
            else:
                logger.warning(f"[{self.run_id}] Task 1 disabled, skipping")
                return
            
            # Task 2: Compute Indicators (Depends on Task 1)
            if self.config['tasks']['compute_indicators']['enabled']:
                logger.info(f"[{self.run_id}] Task 2/5: Computing indicators...")
                indicators = self._run_task_with_retry(
                    compute_indicators,
                    self.config['tasks']['compute_indicators'],
                    data=data,
                    config=self.config['tasks']['compute_indicators']
                )
                self.run_status['compute_indicators'] = 'success'
            
            # Task 3: Generate Predictions (Depends on Task 2)
            if self.config['tasks']['generate_predictions']['enabled']:
                logger.info(f"[{self.run_id}] Task 3/5: Generating predictions...")
                predictions = self._run_task_with_retry(
                    generate_predictions,
                    self.config['tasks']['generate_predictions'],
                    indicators=indicators,
                    model_path=self.config['tasks']['generate_predictions']['model_path']
                )
                self.run_status['generate_predictions'] = 'success'
            
            # Task 4: Update Storage (Depends on Task 3)
            if self.config['tasks']['update_storage']['enabled']:
                logger.info(f"[{self.run_id}] Task 4/5: Updating storage...")
                self._run_task_with_retry(
                    update_storage,
                    self.config['tasks']['update_storage'],
                    predictions=predictions,
                    connection_string=self.config['tasks']['update_storage']['database']['connection_string']
                )
                self.run_status['update_storage'] = 'success'
            
            # Task 5: Sync Visualization (Depends on Task 4)
            if self.config['tasks']['sync_visualization']['enabled']:
                logger.info(f"[{self.run_id}] Task 5/5: Syncing visualization...")
                self._run_task_with_retry(
                    sync_visualization,
                    self.config['tasks']['sync_visualization'],
                    pbi_config=self.config['tasks']['sync_visualization']['power_bi']
                )
                self.run_status['sync_visualization'] = 'success'
            
            # Pipeline completed successfully
            logger.info(f"[{self.run_id}] Pipeline completed successfully")
            self._log_run_summary(status='success')
            
        except Exception as e:
            logger.error(f"[{self.run_id}] Pipeline failed: {e}", exc_info=True)
            self._log_run_summary(status='failure', error=str(e))
            self._send_alert(f"Pipeline failed: {e}")
    
    def _run_task_with_retry(self, task_func, task_config, **kwargs):
        """Execute a task with automatic retry logic."""
        max_retries = task_config.get('retries', 3)
        retry_delay = self.config['pipeline'].get('retry_delay_seconds', 30)
        timeout = task_config.get('timeout_seconds', 300)
        
        for attempt in range(1, max_retries + 1):
            try:
                logger.info(f"[{self.run_id}] Attempt {attempt}/{max_retries} (timeout: {timeout}s)")
                result = task_func(**kwargs, timeout=timeout)
                logger.info(f"[{self.run_id}] Task succeeded")
                return result
            except Exception as e:
                logger.warning(f"[{self.run_id}] Attempt {attempt} failed: {e}")
                if attempt < max_retries:
                    logger.info(f"[{self.run_id}] Retrying in {retry_delay}s...")
                    import time
                    time.sleep(retry_delay)
                else:
                    logger.error(f"[{self.run_id}] All retries exhausted")
                    raise
    
    def _log_run_summary(self, status, error=None):
        """Log execution summary with metadata."""
        summary = {
            'run_id': self.run_id,
            'timestamp': datetime.utcnow().isoformat(),
            'overall_status': status,
            'tasks': self.run_status,
            'error': error
        }
        logger.info(f"Run summary: {summary}")
        # TODO: Store in metadata backend (database, Elasticsearch, etc.)
    
    def _send_alert(self, message):
        """Send alert to configured channels (Slack, email, etc.)."""
        slack_webhook = self.config['monitoring']['alert_channels'][0].get('webhook_url')
        if slack_webhook:
            import requests
            requests.post(slack_webhook, json={'text': f"⚠️ AntiGravity Alert: {message}"})
        logger.info(f"Alert sent: {message}")
    
    def schedule_pipeline(self):
        """Schedule pipeline to run on configured schedule."""
        config = self.config['pipeline']
        
        if config['market_hours_only']:
            # Cron: Every N minutes, 9 AM–4 PM ET, Mon–Fri
            cron_expr = f"*/{config['interval_minutes']} {config['market_open_hour']}-{config['market_close_hour']-1} * * 0-4"
            tz = pytz.timezone(config['market_timezone'])
            
            logger.info(f"Scheduling pipeline: {cron_expr} ({config['market_timezone']})")
            self.scheduler.add_job(
                self.run_pipeline,
                CronTrigger.from_crontab(cron_expr, timezone=tz),
                id='stock_pipeline',
                name='Stock Analytics Pipeline',
                misfire_grace_time=60
            )
        else:
            # Simple interval schedule
            logger.info(f"Scheduling pipeline: Every {config['interval_minutes']} minutes")
            self.scheduler.add_job(
                self.run_pipeline,
                'interval',
                minutes=config['interval_minutes'],
                id='stock_pipeline',
                name='Stock Analytics Pipeline'
            )
    
    def start(self):
        """Start the orchestrator."""
        logger.info("Starting orchestrator...")
        self.schedule_pipeline()
        self.scheduler.start()
        logger.info("Orchestrator running. Press Ctrl+C to stop.")
        
        try:
            import time
            while True:
                time.sleep(1)
        except KeyboardInterrupt:
            logger.info("Stopping orchestrator...")
            self.scheduler.shutdown()
            logger.info("Orchestrator stopped.")

# ============================================
# MAIN EXECUTION
# ============================================
if __name__ == '__main__':
    config = load_config('config/pipeline_config.yaml')
    orchestrator = PipelineOrchestrator(config)
    orchestrator.start()
```

---

### 4. **Installation & Dependencies**
Create a `requirements.txt`:

```
# Core
pyyaml==6.0
apscheduler==3.10.4
pytz==2024.1

# Data & ML
pandas==2.0.3
numpy==1.24.3
yfinance==0.2.32
scikit-learn==1.3.0
xgboost==2.0.0

# Database & Cache
psycopg2-binary==2.9.7  # PostgreSQL
redis==5.0.0
sqlalchemy==2.0.20

# API & Notifications
requests==2.31.0
slack-sdk==3.23.0

# Logging & Monitoring
python-json-logger==2.0.7
```

Install:
```bash
pip install -r requirements.txt
```

---

### 5. **Deployment Options**

#### **Option A: Local Machine (Development)**
```bash
# Run orchestrator in background
nohup python orchestrator.py > orchestrator.log 2>&1 &
```

#### **Option B: systemd Service (Linux)**
Create `/etc/systemd/system/antigravity-pipeline.service`:
```ini
[Unit]
Description=AntiGravity Stock Pipeline Orchestrator
After=network.target

[Service]
Type=simple
User=pipeline_user
WorkingDirectory=/path/to/project
ExecStart=/usr/bin/python3 /path/to/project/orchestrator.py
Restart=always
RestartSec=10

[Install]
WantedBy=multi-user.target
```

Enable & start:
```bash
sudo systemctl enable antigravity-pipeline
sudo systemctl start antigravity-pipeline
sudo systemctl status antigravity-pipeline
```

#### **Option C: Docker (Recommended for Scaling)**
Create `Dockerfile`:
```dockerfile
FROM python:3.11-slim

WORKDIR /app
COPY requirements.txt .
RUN pip install -r requirements.txt

COPY . .

CMD ["python", "orchestrator.py"]
```

Build & run:
```bash
docker build -t antigravity-pipeline .
docker run -d --name pipeline -v $(pwd)/logs:/app/logs antigravity-pipeline
```

#### **Option D: Cloud-Native (AWS, GCP, Azure)**
Deploy as:
- **AWS**: ECS task + EventBridge (scheduled trigger)
- **GCP**: Cloud Run + Cloud Scheduler
- **Azure**: Container Instance + Logic App

---

### 6. **Monitoring & Observability**

#### **Real-Time Monitoring Dashboard**
Create a simple Flask app to monitor runs:

```python
# monitor.py
from flask import Flask, jsonify
import json
import os
from datetime import datetime

app = Flask(__name__)

@app.route('/api/status', methods=['GET'])
def get_status():
    """Return latest pipeline run status."""
    if os.path.exists('logs/pipeline.log'):
        with open('logs/pipeline.log', 'r') as f:
            lines = f.readlines()[-50:]  # Last 50 lines
        return jsonify({'status': 'running', 'recent_logs': lines})
    return jsonify({'status': 'no_runs_yet'})

@app.route('/api/metrics', methods=['GET'])
def get_metrics():
    """Return pipeline metrics."""
    # TODO: Query from metadata backend
    return jsonify({
        'total_runs': 100,
        'success_rate': 0.98,
        'avg_duration_seconds': 45,
        'last_run': '2025-04-26T09:30:00Z'
    })

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=False)
```

Run monitoring dashboard:
```bash
python monitor.py
# Visit http://localhost:5000/api/status
```

---

### 7. **Testing & Validation**

#### **Unit Tests for Each Task**
```python
# tests/test_fetch_data.py
import pytest
from scripts.fetch_data import fetch_stock_data

def test_fetch_stock_data_success():
    """Test fetching data for valid tickers."""
    data = fetch_stock_data(['AAPL'], interval='1d')
    assert data is not None
    assert len(data) > 0

def test_fetch_stock_data_invalid_ticker():
    """Test error handling for invalid ticker."""
    with pytest.raises(Exception):
        fetch_stock_data(['INVALID_TICKER_XYZ'])
```

#### **Integration Test (End-to-End)**
```python
# tests/test_integration.py
def test_full_pipeline():
    """Test complete pipeline execution."""
    config = load_config('config/pipeline_config.yaml')
    orchestrator = PipelineOrchestrator(config)
    orchestrator.run_pipeline()
    assert orchestrator.run_status['fetch_data'] == 'success'
    assert orchestrator.run_status['compute_indicators'] == 'success'
    assert orchestrator.run_status['generate_predictions'] == 'success'
    assert orchestrator.run_status['update_storage'] == 'success'
    assert orchestrator.run_status['sync_visualization'] == 'success'
```

Run tests:
```bash
pytest tests/ -v
```

---

## IMPLEMENTATION CHECKLIST

- [ ] **Week 1: Foundation**
  - [ ] Create modular task scripts (fetch, indicators, models, storage, viz)
  - [ ] Write `pipeline_config.yaml` with all settings
  - [ ] Build core `orchestrator.py` with APScheduler
  - [ ] Set up logging and error handling
  - [ ] Test each task independently

- [ ] **Week 2: Validation**
  - [ ] Run full pipeline manually end-to-end
  - [ ] Validate data quality at each step
  - [ ] Add retry logic and timeouts
  - [ ] Set up Slack/email alerts
  - [ ] Write unit tests

- [ ] **Week 3: Deployment**
  - [ ] Deploy to systemd service or Docker
  - [ ] Configure for market hours (9 AM–4 PM ET, weekdays only)
  - [ ] Monitor first 50 automated runs
  - [ ] Fix any issues, adjust timeouts
  - [ ] Set up log archival and metadata tracking

- [ ] **Week 4: Optimization**
  - [ ] Build monitoring dashboard
  - [ ] Add data quality checks
  - [ ] Optimize slow tasks (parallel processing, caching)
  - [ ] Document runbooks and troubleshooting
  - [ ] Prepare for scaling to Airflow/Prefect

---

## SUCCESS CRITERIA

When your orchestration is working, you'll see:

✅ **Automated execution**: Pipeline runs every 5 minutes without manual triggers  
✅ **Reliable sequence**: Tasks always run in order (fetch → process → model → store → viz)  
✅ **Zero stale data**: Analytics always refreshed with latest 5-minute data  
✅ **Fault recovery**: Failed tasks retry automatically; alerts notify team  
✅ **Full visibility**: Logs show every task, every step, every error  
✅ **SLA compliance**: 99%+ successful runs, <5 minute end-to-end latency  
✅ **Scaling ready**: Adding new tickers requires only config change, no code changes  

---

## NEXT STEPS (After MVP)

Once Phase 1 is stable:

1. **Migrate to Prefect** (Week 5–6)
   - Define DAG visually in Prefect Cloud
   - Get rich monitoring UI + performance analytics
   - Enable distributed task execution

2. **Add Data Quality Monitoring** (Week 7)
   - Validate data freshness, completeness, accuracy
   - Halt pipeline if quality checks fail
   - Alert on anomalies

3. **Scale to Multiple Datasets** (Week 8+)
   - Manage 50+ tickers with separate pipeline instances
   - Parallel execution where possible
   - Optimize database writes with batch operations

4. **Implement SLA Tracking** (Week 9)
   - Track end-to-end latency
   - Identify bottleneck tasks
   - Auto-alert if SLA breached

---

## SUPPORT & DEBUGGING

### Common Issues & Solutions

**Pipeline doesn't start**:
- Check `pipeline_config.yaml` syntax: `python -c "import yaml; yaml.safe_load(open('config/pipeline_config.yaml'))"`
- Verify APScheduler installed: `pip install apscheduler`
- Check logs: `tail -f logs/pipeline.log`

**Task keeps failing**:
- Increase timeout in config: `timeout_seconds: 600`
- Check external API limits (Yahoo Finance rate limits)
- Verify database connection string is correct
- Run task manually to see exact error

**Missed runs**:
- Check cron expression: Use `crontab -e` to validate syntax
- Verify timezone is correct: `pytz.timezone('America/New_York')`
- Check system time is synchronized: `timedatectl`

**Power BI sync failing**:
- Verify API credentials and workspace/dataset IDs
- Check Power BI API rate limits (8 refreshes/hour)
- Add exponential backoff retry logic

---

## RESOURCES

- **APScheduler Docs**: https://apscheduler.readthedocs.io
- **Cron Expression Builder**: https://crontab.guru
- **Prefect Migration**: https://docs.prefect.io
- **Power BI REST API**: https://learn.microsoft.com/en-us/rest/api/power-bi/

---

**You now have everything needed to build a production-grade orchestration system. Start with the checklist, follow the code templates, and deploy with confidence.**
