# 🚀 ENHANCED ROADMAP - Real-time Alerts, Custom MCP & Scalable Database

**Version:** 2.0
**Date:** 2025-12-05
**Author:** Claude Code Analysis + User Requirements

---

## 📋 TABLE OF CONTENTS

1. [Executive Summary](#executive-summary)
2. [Phase 1: Foundation Refactoring](#phase-1-foundation-refactoring-1-2-weeks)
3. [Phase 2: Real-time Alert System](#phase-2-real-time-alert-system-1-2-weeks)
4. [Phase 3: Custom MCP Servers](#phase-3-custom-mcp-servers-for-analysis-2-3-weeks)
5. [Phase 4: Scalable Database Architecture](#phase-4-scalable-database-architecture-2-weeks)
6. [Phase 5: AI API Integration Layer](#phase-5-ai-api-integration-layer-1-2-weeks)
7. [Phase 6: Web Dashboard with Live Updates](#phase-6-web-dashboard-with-live-updates-1-week)
8. [Architecture Comparison](#architecture-comparison)
9. [Cost Analysis](#cost-analysis)
10. [Risk Assessment](#risk-assessment)

---

## 📊 EXECUTIVE SUMMARY

### Mục tiêu mở rộng

1. **Real-time Alerts** 🔔
   - Telegram bot cảnh báo tín hiệu giao dịch
   - Email alerts cho các sự kiện quan trọng
   - Website HTML với live updates (WebSocket)

2. **Custom MCP Servers** 🛠️
   - MCP cho phân tích báo cáo tài chính
   - MCP cho technical analysis với AI
   - MCP cho portfolio optimization
   - MCP cho news sentiment tracking

3. **Scalable Database** 💾
   - Time-series DB cho OHLCV (InfluxDB/TimescaleDB)
   - Document DB cho news/reports (MongoDB)
   - Vector DB cho AI embeddings (Pinecone/Qdrant)
   - Cache layer (Redis)

4. **AI API Integration** 🤖
   - Claude API cho analysis
   - OpenAI Embeddings cho semantic search
   - Custom fine-tuned models
   - RAG (Retrieval Augmented Generation)

### Timeline tổng thể

| Phase | Duration | Dependencies |
|-------|----------|--------------|
| Phase 1: Foundation | 1-2 weeks | None |
| Phase 2: Real-time Alerts | 1-2 weeks | Phase 1 |
| Phase 3: Custom MCP | 2-3 weeks | Phase 1 |
| Phase 4: Database Migration | 2 weeks | Phase 1 |
| Phase 5: AI APIs | 1-2 weeks | Phase 3, 4 |
| Phase 6: Web Dashboard | 1 week | Phase 2, 5 |

**Total:** 8-12 weeks (2-3 months)

---

## 🏗️ PHASE 1: FOUNDATION REFACTORING (1-2 weeks)

### Mục tiêu
- Migrate sang vnstock_ta, vnstock_pipeline
- Refactor BaseCalculator
- Clean up technical debt

### Chi tiết triển khai

#### 1.1. Project Structure Migration

```bash
stock_dashboard/
├── src/stock_dashboard/
│   ├── __init__.py
│   ├── settings.py                    # Pydantic settings
│   │
│   ├── core/
│   │   ├── __init__.py
│   │   ├── config.py
│   │   ├── constants.py
│   │   ├── exceptions.py             # Custom exceptions
│   │   └── logging_config.py         # Centralized logging
│   │
│   ├── data/                          # Data pipeline layer
│   │   ├── fetchers/
│   │   │   ├── __init__.py
│   │   │   ├── base_fetcher.py
│   │   │   ├── ohlcv_fetcher.py      # vnstock_data
│   │   │   ├── fundamental_fetcher.py
│   │   │   └── news_fetcher.py        # vnstock_news
│   │   ├── validators/
│   │   │   ├── __init__.py
│   │   │   ├── ohlcv_validator.py
│   │   │   └── fundamental_validator.py
│   │   ├── transformers/
│   │   │   ├── __init__.py
│   │   │   ├── technical_transformer.py  # ⭐ vnstock_ta
│   │   │   ├── fundamental_transformer.py
│   │   │   └── ai_enrichment.py
│   │   └── exporters/
│   │       ├── __init__.py
│   │       ├── parquet_exporter.py
│   │       ├── database_exporter.py
│   │       └── redis_exporter.py      # ⭐ Cache layer
│   │
│   ├── processors/                     # Business logic
│   │   ├── base/
│   │   │   ├── __init__.py
│   │   │   └── base_calculator.py
│   │   ├── valuation/
│   │   │   ├── __init__.py
│   │   │   ├── pe_calculator.py
│   │   │   ├── pb_calculator.py
│   │   │   └── ev_calculator.py
│   │   └── pipelines/
│   │       ├── __init__.py
│   │       ├── daily_ohlcv_pipeline.py
│   │       ├── daily_valuation_pipeline.py
│   │       └── daily_technical_pipeline.py
│   │
│   ├── alerts/                         # ⭐ NEW: Alert system
│   │   ├── __init__.py
│   │   ├── alert_engine.py
│   │   ├── notifiers/
│   │   │   ├── telegram_notifier.py
│   │   │   ├── email_notifier.py
│   │   │   └── websocket_notifier.py
│   │   └── rules/
│   │       ├── price_alert.py
│   │       ├── technical_alert.py
│   │       └── fundamental_alert.py
│   │
│   ├── mcp/                           # ⭐ MCP servers
│   │   ├── __init__.py
│   │   ├── servers/
│   │   │   ├── data_server.py
│   │   │   ├── analysis_server.py
│   │   │   ├── portfolio_server.py
│   │   │   └── alert_server.py
│   │   └── tools/
│   │       ├── query_tools.py
│   │       ├── analysis_tools.py
│   │       └── chart_tools.py
│   │
│   ├── database/                      # ⭐ Database layer
│   │   ├── __init__.py
│   │   ├── models/                    # SQLAlchemy/Pydantic models
│   │   │   ├── ohlcv.py
│   │   │   ├── fundamental.py
│   │   │   ├── news.py
│   │   │   └── alerts.py
│   │   ├── repositories/              # Repository pattern
│   │   │   ├── base_repository.py
│   │   │   ├── timeseries_repo.py    # InfluxDB/TimescaleDB
│   │   │   ├── document_repo.py      # MongoDB
│   │   │   ├── vector_repo.py        # Pinecone/Qdrant
│   │   │   └── cache_repo.py         # Redis
│   │   └── migrations/                # Alembic migrations
│   │
│   ├── ai/                            # ⭐ AI integration
│   │   ├── __init__.py
│   │   ├── clients/
│   │   │   ├── claude_client.py
│   │   │   ├── openai_client.py
│   │   │   └── custom_model_client.py
│   │   ├── embeddings/
│   │   │   ├── text_embedder.py
│   │   │   └── financial_embedder.py
│   │   ├── rag/
│   │   │   ├── retriever.py
│   │   │   ├── context_builder.py
│   │   │   └── generator.py
│   │   └── prompts/
│   │       ├── analysis_prompts.py
│   │       ├── report_prompts.py
│   │       └── alert_prompts.py
│   │
│   ├── web/                           # Streamlit + FastAPI
│   │   ├── streamlit/
│   │   │   ├── pages/
│   │   │   ├── components/
│   │   │   └── app.py
│   │   └── api/                       # ⭐ NEW: REST API
│   │       ├── __init__.py
│   │       ├── main.py               # FastAPI app
│   │       ├── routers/
│   │       │   ├── stocks.py
│   │       │   ├── alerts.py
│   │       │   ├── analysis.py
│   │       │   └── websocket.py      # Live updates
│   │       └── schemas/
│   │
│   └── reports/
│       ├── pdf/
│       └── excel/
│
├── configs/                           # Configuration files
│   ├── alerts.yaml                    # Alert rules
│   ├── database.yaml                  # DB connections
│   ├── mcp_servers.yaml               # MCP configs
│   └── ai_models.yaml                 # AI model configs
│
├── .claude/                           # Claude Code
│   ├── commands/
│   └── skills/
│
└── docker/                            # ⭐ Docker deployment
    ├── docker-compose.yml
    ├── timescaledb/
    ├── mongodb/
    ├── redis/
    └── qdrant/
```

#### 1.2. Settings Configuration

```python
# src/stock_dashboard/settings.py
from pydantic_settings import BaseSettings
from pydantic import Field, PostgresDsn, MongoDsn, HttpUrl
from pathlib import Path
from typing import Optional, List

class DatabaseSettings(BaseSettings):
    """Database configurations."""

    # TimescaleDB for time-series (OHLCV, technical indicators)
    TIMESCALEDB_URI: PostgresDsn = Field(
        default="postgresql://user:pass@localhost:5432/stock_timeseries",
        env="TIMESCALEDB_URI"
    )

    # MongoDB for documents (news, reports, analysis)
    MONGODB_URI: MongoDsn = Field(
        default="mongodb://localhost:27017/stock_documents",
        env="MONGODB_URI"
    )

    # Redis for caching and pub/sub
    REDIS_URI: str = Field(
        default="redis://localhost:6379/0",
        env="REDIS_URI"
    )

    # Qdrant for vector search (AI embeddings)
    QDRANT_URL: HttpUrl = Field(
        default="http://localhost:6333",
        env="QDRANT_URL"
    )
    QDRANT_API_KEY: Optional[str] = Field(default=None, env="QDRANT_API_KEY")

class AlertSettings(BaseSettings):
    """Alert system configurations."""

    # Telegram
    TELEGRAM_BOT_TOKEN: str = Field(..., env="TELEGRAM_BOT_TOKEN")
    TELEGRAM_CHAT_IDS: List[str] = Field(default=[], env="TELEGRAM_CHAT_IDS")

    # Email
    SMTP_HOST: str = Field(default="smtp.gmail.com", env="SMTP_HOST")
    SMTP_PORT: int = Field(default=587, env="SMTP_PORT")
    SMTP_USER: str = Field(..., env="SMTP_USER")
    SMTP_PASSWORD: str = Field(..., env="SMTP_PASSWORD")
    EMAIL_RECIPIENTS: List[str] = Field(default=[], env="EMAIL_RECIPIENTS")

    # WebSocket
    WS_ENABLED: bool = Field(default=True, env="WS_ENABLED")
    WS_PORT: int = Field(default=8765, env="WS_PORT")

class AISettings(BaseSettings):
    """AI integration configurations."""

    # Anthropic Claude
    ANTHROPIC_API_KEY: str = Field(..., env="ANTHROPIC_API_KEY")
    CLAUDE_MODEL: str = Field(default="claude-sonnet-4-5-20250929", env="CLAUDE_MODEL")

    # OpenAI (for embeddings)
    OPENAI_API_KEY: str = Field(..., env="OPENAI_API_KEY")
    EMBEDDING_MODEL: str = Field(default="text-embedding-3-small", env="EMBEDDING_MODEL")

    # Custom models
    CUSTOM_MODEL_ENDPOINT: Optional[HttpUrl] = Field(default=None, env="CUSTOM_MODEL_ENDPOINT")

class Settings(BaseSettings):
    """Main application settings."""

    # Project paths
    PROJECT_ROOT: Path = Path(__file__).parents[2]
    DATA_DIR: Path = PROJECT_ROOT / "data"
    LOGS_DIR: Path = PROJECT_ROOT / "logs"

    # Sub-settings
    database: DatabaseSettings = DatabaseSettings()
    alerts: AlertSettings = AlertSettings()
    ai: AISettings = AISettings()

    # Processing
    MAX_WORKERS: int = Field(default=10, env="MAX_WORKERS")
    BATCH_SIZE: int = Field(default=1000, env="BATCH_SIZE")

    # API
    API_HOST: str = Field(default="0.0.0.0", env="API_HOST")
    API_PORT: int = Field(default=8000, env="API_PORT")

    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"
        env_nested_delimiter = "__"

# Global settings instance
settings = Settings()
```

### ✅ Ưu điểm Phase 1

1. **Clean Architecture**: Separation of concerns rõ ràng
2. **Type Safety**: Pydantic validation cho configs
3. **Maintainable**: Dễ mở rộng và maintain
4. **Testable**: Dễ viết unit tests
5. **Production-ready**: Logging, error handling đầy đủ

### ⚠️ Nhược điểm Phase 1

1. **Migration effort**: Cần refactor toàn bộ codebase
2. **Breaking changes**: Phải update tất cả imports
3. **Learning curve**: Team cần học Pydantic, new patterns
4. **Time-consuming**: 1-2 tuần chỉ cho refactoring

### 💰 Chi phí Phase 1

- **Developer time**: 1-2 weeks × 1 developer
- **Infrastructure**: $0 (no new services)
- **Risk**: Medium (code changes)

---

## 🔔 PHASE 2: REAL-TIME ALERT SYSTEM (1-2 weeks)

### 2.1. Architecture Overview

```
┌─────────────────────────────────────────────────────────────┐
│                    ALERT ENGINE                              │
├─────────────────────────────────────────────────────────────┤
│                                                              │
│  ┌──────────────┐    ┌──────────────┐    ┌──────────────┐ │
│  │ Data Stream  │───▶│ Rule Engine  │───▶│  Notifiers   │ │
│  └──────────────┘    └──────────────┘    └──────────────┘ │
│         │                    │                     │        │
│         ▼                    ▼                     ▼        │
│  ┌──────────────┐    ┌──────────────┐    ┌──────────────┐ │
│  │ Redis Pub/Sub│    │ Alert Rules  │    │  Telegram    │ │
│  │              │    │  - Price     │    │  Email       │ │
│  │  ├─OHLCV     │    │  - Technical │    │  WebSocket   │ │
│  │  ├─Technical │    │  - News      │    │  Push Notify │ │
│  │  └─News      │    │  - Volatility│    └──────────────┘ │
│  └──────────────┘    └──────────────┘                      │
└─────────────────────────────────────────────────────────────┘
```

### 2.2. Alert Engine Implementation

```python
# src/stock_dashboard/alerts/alert_engine.py
from typing import List, Dict, Any, Optional
from dataclasses import dataclass
from datetime import datetime
import asyncio
import redis.asyncio as redis
from loguru import logger

from stock_dashboard.settings import settings
from stock_dashboard.alerts.notifiers import TelegramNotifier, EmailNotifier, WebSocketNotifier
from stock_dashboard.alerts.rules import (
    PriceAlertRule,
    TechnicalAlertRule,
    FundamentalAlertRule,
    VolumeAlertRule,
    VolatilityAlertRule
)

@dataclass
class Alert:
    """Alert data structure."""
    alert_id: str
    symbol: str
    alert_type: str  # price, technical, fundamental, news
    severity: str    # info, warning, critical
    title: str
    message: str
    data: Dict[str, Any]
    timestamp: datetime

    def to_telegram_message(self) -> str:
        """Format alert for Telegram."""
        emoji_map = {
            "info": "ℹ️",
            "warning": "⚠️",
            "critical": "🚨"
        }

        emoji = emoji_map.get(self.severity, "📊")

        return f"""{emoji} **{self.title}**

📈 Symbol: `{self.symbol}`
🕐 Time: {self.timestamp.strftime('%Y-%m-%d %H:%M:%S')}

{self.message}

Data:
```
{self._format_data()}
```
"""

    def _format_data(self) -> str:
        """Format data dict as readable string."""
        lines = []
        for key, value in self.data.items():
            if isinstance(value, float):
                lines.append(f"{key}: {value:,.2f}")
            else:
                lines.append(f"{key}: {value}")
        return "\n".join(lines)

class AlertEngine:
    """Real-time alert engine với multiple notification channels."""

    def __init__(self):
        self.redis_client = redis.from_url(settings.database.REDIS_URI)
        self.rules: List[AlertRule] = []
        self.notifiers = {
            "telegram": TelegramNotifier(settings.alerts.TELEGRAM_BOT_TOKEN),
            "email": EmailNotifier(
                smtp_host=settings.alerts.SMTP_HOST,
                smtp_port=settings.alerts.SMTP_PORT,
                smtp_user=settings.alerts.SMTP_USER,
                smtp_password=settings.alerts.SMTP_PASSWORD
            ),
            "websocket": WebSocketNotifier(port=settings.alerts.WS_PORT)
        }

        # Load alert rules from config
        self._load_rules()

    def _load_rules(self):
        """Load alert rules from configuration."""
        # Price alerts
        self.rules.append(PriceAlertRule(
            name="price_change_5pct",
            condition=lambda data: abs(data.get("price_change_pct", 0)) >= 5.0,
            severity="warning"
        ))

        self.rules.append(PriceAlertRule(
            name="price_change_10pct",
            condition=lambda data: abs(data.get("price_change_pct", 0)) >= 10.0,
            severity="critical"
        ))

        # Technical alerts
        self.rules.append(TechnicalAlertRule(
            name="rsi_oversold",
            condition=lambda data: data.get("rsi", 50) < 30,
            severity="info",
            message="RSI indicates oversold condition"
        ))

        self.rules.append(TechnicalAlertRule(
            name="rsi_overbought",
            condition=lambda data: data.get("rsi", 50) > 70,
            severity="info",
            message="RSI indicates overbought condition"
        ))

        self.rules.append(TechnicalAlertRule(
            name="macd_crossover",
            condition=lambda data: (
                data.get("macd_signal", "") == "bullish_crossover" or
                data.get("macd_signal", "") == "bearish_crossover"
            ),
            severity="warning",
            message="MACD crossover detected"
        ))

        # Volume alerts
        self.rules.append(VolumeAlertRule(
            name="volume_spike",
            condition=lambda data: data.get("volume_ratio", 1.0) >= 3.0,
            severity="warning",
            message="Volume spike detected (3x average)"
        ))

        logger.info(f"Loaded {len(self.rules)} alert rules")

    async def start(self):
        """Start alert engine."""
        logger.info("Starting alert engine...")

        # Start WebSocket notifier
        await self.notifiers["websocket"].start()

        # Subscribe to Redis channels
        pubsub = self.redis_client.pubsub()
        await pubsub.subscribe(
            "stock:ohlcv",
            "stock:technical",
            "stock:news",
            "stock:fundamental"
        )

        logger.info("Alert engine started, listening for events...")

        # Process messages
        async for message in pubsub.listen():
            if message["type"] == "message":
                await self._process_message(message)

    async def _process_message(self, message: Dict[str, Any]):
        """Process incoming message and check alert rules."""
        try:
            channel = message["channel"].decode()
            data = json.loads(message["data"])

            symbol = data.get("symbol")

            # Check all rules
            for rule in self.rules:
                if rule.matches(data):
                    alert = Alert(
                        alert_id=f"{symbol}_{rule.name}_{int(time.time())}",
                        symbol=symbol,
                        alert_type=channel.split(":")[-1],
                        severity=rule.severity,
                        title=rule.get_title(data),
                        message=rule.get_message(data),
                        data=rule.extract_relevant_data(data),
                        timestamp=datetime.now()
                    )

                    await self._send_alert(alert)

        except Exception as e:
            logger.error(f"Error processing message: {e}")

    async def _send_alert(self, alert: Alert):
        """Send alert through all enabled notifiers."""
        logger.info(f"Sending alert: {alert.symbol} - {alert.title}")

        # Send to all notifiers concurrently
        tasks = []

        if settings.alerts.TELEGRAM_BOT_TOKEN:
            tasks.append(self.notifiers["telegram"].send(alert))

        if settings.alerts.SMTP_USER:
            tasks.append(self.notifiers["email"].send(
                alert,
                recipients=settings.alerts.EMAIL_RECIPIENTS
            ))

        if settings.alerts.WS_ENABLED:
            tasks.append(self.notifiers["websocket"].broadcast(alert))

        await asyncio.gather(*tasks, return_exceptions=True)

        # Store alert in database
        await self._store_alert(alert)

    async def _store_alert(self, alert: Alert):
        """Store alert in database for history."""
        from stock_dashboard.database.repositories import AlertRepository

        repo = AlertRepository()
        await repo.create(alert)
```

### 2.3. Telegram Notifier

```python
# src/stock_dashboard/alerts/notifiers/telegram_notifier.py
from telegram import Bot
from telegram.error import TelegramError
from loguru import logger
from typing import List

from stock_dashboard.alerts.alert_engine import Alert

class TelegramNotifier:
    """Send alerts via Telegram bot."""

    def __init__(self, bot_token: str):
        self.bot = Bot(token=bot_token)

    async def send(self, alert: Alert, chat_ids: List[str] = None):
        """Send alert to Telegram chats."""
        if chat_ids is None:
            from stock_dashboard.settings import settings
            chat_ids = settings.alerts.TELEGRAM_CHAT_IDS

        message = alert.to_telegram_message()

        for chat_id in chat_ids:
            try:
                await self.bot.send_message(
                    chat_id=chat_id,
                    text=message,
                    parse_mode="Markdown"
                )
                logger.info(f"Sent alert to Telegram chat {chat_id}")
            except TelegramError as e:
                logger.error(f"Failed to send to {chat_id}: {e}")
```

### 2.4. WebSocket Notifier (cho website HTML)

```python
# src/stock_dashboard/alerts/notifiers/websocket_notifier.py
import asyncio
import json
from typing import Set
import websockets
from websockets.server import WebSocketServerProtocol
from loguru import logger

from stock_dashboard.alerts.alert_engine import Alert

class WebSocketNotifier:
    """WebSocket server for real-time browser updates."""

    def __init__(self, port: int = 8765):
        self.port = port
        self.clients: Set[WebSocketServerProtocol] = set()

    async def start(self):
        """Start WebSocket server."""
        server = await websockets.serve(
            self._handle_client,
            "0.0.0.0",
            self.port
        )
        logger.info(f"WebSocket server started on port {self.port}")
        return server

    async def _handle_client(self, websocket: WebSocketServerProtocol, path: str):
        """Handle new WebSocket connection."""
        self.clients.add(websocket)
        logger.info(f"New WebSocket client connected: {websocket.remote_address}")

        try:
            async for message in websocket:
                # Handle client messages (subscriptions, etc.)
                await self._handle_message(websocket, message)
        except websockets.exceptions.ConnectionClosed:
            pass
        finally:
            self.clients.remove(websocket)
            logger.info(f"WebSocket client disconnected: {websocket.remote_address}")

    async def _handle_message(self, websocket: WebSocketServerProtocol, message: str):
        """Handle message from client."""
        try:
            data = json.loads(message)
            action = data.get("action")

            if action == "subscribe":
                symbols = data.get("symbols", [])
                # Store subscription preferences
                websocket.subscriptions = symbols
                await websocket.send(json.dumps({
                    "status": "subscribed",
                    "symbols": symbols
                }))

        except Exception as e:
            logger.error(f"Error handling client message: {e}")

    async def broadcast(self, alert: Alert):
        """Broadcast alert to all connected clients."""
        if not self.clients:
            return

        message = json.dumps({
            "type": "alert",
            "alert_id": alert.alert_id,
            "symbol": alert.symbol,
            "alert_type": alert.alert_type,
            "severity": alert.severity,
            "title": alert.title,
            "message": alert.message,
            "data": alert.data,
            "timestamp": alert.timestamp.isoformat()
        })

        # Send to all clients (filter by subscriptions if set)
        tasks = []
        for client in self.clients.copy():
            # Check if client is subscribed to this symbol
            subscriptions = getattr(client, 'subscriptions', None)
            if subscriptions is None or alert.symbol in subscriptions:
                tasks.append(self._safe_send(client, message))

        await asyncio.gather(*tasks, return_exceptions=True)

    async def _safe_send(self, client: WebSocketServerProtocol, message: str):
        """Safely send message to client."""
        try:
            await client.send(message)
        except Exception as e:
            logger.error(f"Failed to send to client: {e}")
```

### 2.5. HTML Website với Live Updates

```html
<!-- public/live-dashboard.html -->
<!DOCTYPE html>
<html lang="vi">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Live Stock Alerts Dashboard</title>
    <style>
        * {
            margin: 0;
            padding: 0;
            box-sizing: border-box;
        }

        body {
            font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            min-height: 100vh;
            padding: 20px;
        }

        .container {
            max-width: 1400px;
            margin: 0 auto;
        }

        .header {
            background: white;
            padding: 20px;
            border-radius: 10px;
            box-shadow: 0 4px 6px rgba(0,0,0,0.1);
            margin-bottom: 20px;
        }

        .status {
            display: inline-block;
            padding: 5px 15px;
            border-radius: 20px;
            font-size: 12px;
            font-weight: bold;
        }

        .status.connected {
            background: #10b981;
            color: white;
        }

        .status.disconnected {
            background: #ef4444;
            color: white;
        }

        .alerts-grid {
            display: grid;
            grid-template-columns: repeat(auto-fill, minmax(350px, 1fr));
            gap: 20px;
        }

        .alert-card {
            background: white;
            border-radius: 10px;
            padding: 20px;
            box-shadow: 0 4px 6px rgba(0,0,0,0.1);
            animation: slideIn 0.3s ease-out;
            border-left: 4px solid;
        }

        .alert-card.info {
            border-left-color: #3b82f6;
        }

        .alert-card.warning {
            border-left-color: #f59e0b;
        }

        .alert-card.critical {
            border-left-color: #ef4444;
            animation: pulse 2s infinite;
        }

        .alert-header {
            display: flex;
            justify-content: space-between;
            align-items: center;
            margin-bottom: 10px;
        }

        .alert-symbol {
            font-size: 24px;
            font-weight: bold;
            color: #1f2937;
        }

        .alert-time {
            font-size: 12px;
            color: #6b7280;
        }

        .alert-title {
            font-size: 16px;
            font-weight: 600;
            color: #374151;
            margin-bottom: 8px;
        }

        .alert-message {
            font-size: 14px;
            color: #6b7280;
            line-height: 1.5;
            margin-bottom: 12px;
        }

        .alert-data {
            background: #f3f4f6;
            padding: 10px;
            border-radius: 5px;
            font-size: 12px;
            font-family: 'Courier New', monospace;
        }

        .alert-data-row {
            display: flex;
            justify-content: space-between;
            padding: 4px 0;
        }

        .alert-data-key {
            color: #6b7280;
        }

        .alert-data-value {
            font-weight: bold;
            color: #1f2937;
        }

        @keyframes slideIn {
            from {
                opacity: 0;
                transform: translateY(-20px);
            }
            to {
                opacity: 1;
                transform: translateY(0);
            }
        }

        @keyframes pulse {
            0%, 100% {
                box-shadow: 0 4px 6px rgba(0,0,0,0.1);
            }
            50% {
                box-shadow: 0 4px 20px rgba(239, 68, 68, 0.4);
            }
        }

        .subscription-panel {
            background: white;
            padding: 20px;
            border-radius: 10px;
            box-shadow: 0 4px 6px rgba(0,0,0,0.1);
            margin-bottom: 20px;
        }

        .subscription-input {
            display: flex;
            gap: 10px;
        }

        .subscription-input input {
            flex: 1;
            padding: 10px;
            border: 2px solid #e5e7eb;
            border-radius: 5px;
            font-size: 14px;
        }

        .subscription-input button {
            padding: 10px 20px;
            background: #3b82f6;
            color: white;
            border: none;
            border-radius: 5px;
            font-weight: bold;
            cursor: pointer;
            transition: background 0.2s;
        }

        .subscription-input button:hover {
            background: #2563eb;
        }

        .subscribed-symbols {
            margin-top: 10px;
            display: flex;
            flex-wrap: wrap;
            gap: 8px;
        }

        .symbol-tag {
            background: #ede9fe;
            color: #7c3aed;
            padding: 5px 12px;
            border-radius: 15px;
            font-size: 12px;
            font-weight: 600;
            display: flex;
            align-items: center;
            gap: 8px;
        }

        .symbol-tag button {
            background: none;
            border: none;
            color: #7c3aed;
            cursor: pointer;
            font-weight: bold;
        }
    </style>
</head>
<body>
    <div class="container">
        <!-- Header -->
        <div class="header">
            <h1>🔔 Live Stock Alerts Dashboard</h1>
            <p>Real-time alerts from Vietnamese Stock Market</p>
            <div style="margin-top: 10px;">
                <span id="status" class="status disconnected">Disconnected</span>
                <span style="margin-left: 10px; color: #6b7280;">
                    Alerts received: <strong id="alertCount">0</strong>
                </span>
            </div>
        </div>

        <!-- Subscription Panel -->
        <div class="subscription-panel">
            <h3>Subscribe to Symbols</h3>
            <div class="subscription-input">
                <input
                    type="text"
                    id="symbolInput"
                    placeholder="Enter stock symbol (e.g., VCB, ACB, HPG)"
                    onkeypress="handleKeyPress(event)"
                >
                <button onclick="subscribeSymbol()">Subscribe</button>
            </div>
            <div id="subscribedSymbols" class="subscribed-symbols"></div>
        </div>

        <!-- Alerts Grid -->
        <div id="alertsGrid" class="alerts-grid"></div>
    </div>

    <script>
        let ws;
        let alertCount = 0;
        let subscribedSymbols = new Set();

        // Connect to WebSocket
        function connect() {
            ws = new WebSocket('ws://localhost:8765');

            ws.onopen = () => {
                console.log('Connected to WebSocket server');
                updateStatus(true);
            };

            ws.onmessage = (event) => {
                const data = JSON.parse(event.data);

                if (data.type === 'alert') {
                    handleAlert(data);
                }
            };

            ws.onerror = (error) => {
                console.error('WebSocket error:', error);
            };

            ws.onclose = () => {
                console.log('Disconnected from WebSocket server');
                updateStatus(false);

                // Reconnect after 3 seconds
                setTimeout(connect, 3000);
            };
        }

        function updateStatus(connected) {
            const statusEl = document.getElementById('status');
            statusEl.className = `status ${connected ? 'connected' : 'disconnected'}`;
            statusEl.textContent = connected ? 'Connected' : 'Disconnected';
        }

        function handleAlert(alert) {
            alertCount++;
            document.getElementById('alertCount').textContent = alertCount;

            // Create alert card
            const card = createAlertCard(alert);

            // Add to grid (prepend to show newest first)
            const grid = document.getElementById('alertsGrid');
            grid.insertBefore(card, grid.firstChild);

            // Limit to 50 alerts
            while (grid.children.length > 50) {
                grid.removeChild(grid.lastChild);
            }

            // Play notification sound (optional)
            if (alert.severity === 'critical') {
                playNotificationSound();
            }
        }

        function createAlertCard(alert) {
            const card = document.createElement('div');
            card.className = `alert-card ${alert.severity}`;

            const time = new Date(alert.timestamp).toLocaleString('vi-VN');

            let dataHTML = '';
            for (const [key, value] of Object.entries(alert.data)) {
                dataHTML += `
                    <div class="alert-data-row">
                        <span class="alert-data-key">${key}:</span>
                        <span class="alert-data-value">${formatValue(value)}</span>
                    </div>
                `;
            }

            card.innerHTML = `
                <div class="alert-header">
                    <div class="alert-symbol">${alert.symbol}</div>
                    <div class="alert-time">${time}</div>
                </div>
                <div class="alert-title">${getEmoji(alert.severity)} ${alert.title}</div>
                <div class="alert-message">${alert.message}</div>
                <div class="alert-data">${dataHTML}</div>
            `;

            return card;
        }

        function getEmoji(severity) {
            const emojiMap = {
                'info': 'ℹ️',
                'warning': '⚠️',
                'critical': '🚨'
            };
            return emojiMap[severity] || '📊';
        }

        function formatValue(value) {
            if (typeof value === 'number') {
                return value.toLocaleString('vi-VN', {
                    minimumFractionDigits: 2,
                    maximumFractionDigits: 2
                });
            }
            return value;
        }

        function playNotificationSound() {
            // Create audio element for notification
            const audio = new Audio('data:audio/wav;base64,UklGRnoGAABXQVZFZm10IBAAAAABAAEAQB8AAEAfAAABAAgAZGF0YQoGAACBhYqFbF1fdJivrJBhNjVgodDbq2EcBj+a2/LDciUFLIHO8tiJNwgZaLvt559NEAxQp+PwtmMcBjiR1/LMeSwFJHfH8N2QQAoUXrTp66hVFApGn+DyvmwhBzGH0fPTgjMGHm7A7+OZVA0NVKzo8K9fGQc+ktXy0n0pBSl+zO/aiDsIDV6x6u2kUxELTKXh8bllHAc2jdXzzYE');
            audio.play().catch(e => console.log('Could not play sound:', e));
        }

        function subscribeSymbol() {
            const input = document.getElementById('symbolInput');
            const symbol = input.value.trim().toUpperCase();

            if (symbol && !subscribedSymbols.has(symbol)) {
                subscribedSymbols.add(symbol);
                updateSubscribedSymbols();

                // Send subscription to server
                if (ws && ws.readyState === WebSocket.OPEN) {
                    ws.send(JSON.stringify({
                        action: 'subscribe',
                        symbols: Array.from(subscribedSymbols)
                    }));
                }

                input.value = '';
            }
        }

        function unsubscribeSymbol(symbol) {
            subscribedSymbols.delete(symbol);
            updateSubscribedSymbols();

            // Send updated subscription to server
            if (ws && ws.readyState === WebSocket.OPEN) {
                ws.send(JSON.stringify({
                    action: 'subscribe',
                    symbols: Array.from(subscribedSymbols)
                }));
            }
        }

        function updateSubscribedSymbols() {
            const container = document.getElementById('subscribedSymbols');
            container.innerHTML = '';

            if (subscribedSymbols.size === 0) {
                container.innerHTML = '<p style="color: #6b7280; font-size: 14px;">No symbols subscribed. Add symbols above to start receiving alerts.</p>';
                return;
            }

            subscribedSymbols.forEach(symbol => {
                const tag = document.createElement('div');
                tag.className = 'symbol-tag';
                tag.innerHTML = `
                    ${symbol}
                    <button onclick="unsubscribeSymbol('${symbol}')">×</button>
                `;
                container.appendChild(tag);
            });
        }

        function handleKeyPress(event) {
            if (event.key === 'Enter') {
                subscribeSymbol();
            }
        }

        // Initialize
        connect();
        updateSubscribedSymbols();
    </script>
</body>
</html>
```

### 2.6. Alert Rules Configuration

```yaml
# configs/alerts.yaml
price_alerts:
  - name: "Large Price Increase"
    condition: "price_change_pct >= 5.0"
    severity: "warning"
    channels: ["telegram", "email"]

  - name: "Critical Price Drop"
    condition: "price_change_pct <= -5.0"
    severity: "critical"
    channels: ["telegram", "email", "websocket"]

  - name: "Price Near 52-Week High"
    condition: "price >= high_52w * 0.98"
    severity: "info"
    channels: ["telegram"]

technical_alerts:
  - name: "RSI Oversold"
    condition: "rsi < 30"
    severity: "info"
    message: "Stock may be oversold based on RSI"
    channels: ["telegram", "websocket"]

  - name: "RSI Overbought"
    condition: "rsi > 70"
    severity: "info"
    message: "Stock may be overbought based on RSI"
    channels: ["telegram", "websocket"]

  - name: "MACD Bullish Crossover"
    condition: "macd_signal == 'bullish_crossover'"
    severity: "warning"
    message: "MACD bullish crossover - potential buy signal"
    channels: ["telegram", "email"]

  - name: "MACD Bearish Crossover"
    condition: "macd_signal == 'bearish_crossover'"
    severity: "warning"
    message: "MACD bearish crossover - potential sell signal"
    channels: ["telegram", "email"]

  - name: "Golden Cross"
    condition: "sma_50 > sma_200 and prev_sma_50 <= prev_sma_200"
    severity: "warning"
    message: "Golden Cross detected - long-term bullish signal"
    channels: ["telegram", "email"]

  - name: "Death Cross"
    condition: "sma_50 < sma_200 and prev_sma_50 >= prev_sma_200"
    severity: "warning"
    message: "Death Cross detected - long-term bearish signal"
    channels: ["telegram", "email"]

volume_alerts:
  - name: "Volume Spike"
    condition: "volume_ratio >= 3.0"
    severity: "warning"
    message: "Trading volume is 3x above average"
    channels: ["telegram", "websocket"]

  - name: "Unusual Volume"
    condition: "volume_ratio >= 5.0"
    severity: "critical"
    message: "Extremely high trading volume detected"
    channels: ["telegram", "email", "websocket"]

volatility_alerts:
  - name: "High Volatility"
    condition: "volatility_30d > volatility_90d * 1.5"
    severity: "warning"
    message: "30-day volatility significantly higher than average"
    channels: ["telegram"]

  - name: "Price Breakout"
    condition: "price > bollinger_upper"
    severity: "info"
    message: "Price broke above upper Bollinger Band"
    channels: ["telegram", "websocket"]

  - name: "Price Breakdown"
    condition: "price < bollinger_lower"
    severity: "info"
    message: "Price broke below lower Bollinger Band"
    channels: ["telegram", "websocket"]

news_alerts:
  - name: "Negative News Sentiment"
    condition: "news_sentiment < -0.5 and news_count >= 3"
    severity: "warning"
    message: "Multiple negative news articles detected"
    channels: ["telegram", "email"]

  - name: "Positive News Surge"
    condition: "news_sentiment > 0.7 and news_count >= 3"
    severity: "info"
    message: "Multiple positive news articles detected"
    channels: ["telegram"]
```

### ✅ Ưu điểm Phase 2

1. **Real-time alerts**: Phản ứng ngay lập tức với thị trường
2. **Multi-channel**: Telegram, Email, WebSocket
3. **Flexible rules**: Dễ thêm/sửa rules qua YAML config
4. **Scalable**: Redis Pub/Sub handle high throughput
5. **User-friendly**: HTML dashboard đẹp, responsive

### ⚠️ Nhược điểm Phase 2

1. **Complexity**: Nhiều components phải maintain
2. **False positives**: Có thể báo alert thừa
3. **Infrastructure**: Cần Redis, WebSocket server
4. **Network dependency**: Phụ thuộc vào network stability

### 💰 Chi phí Phase 2

- **Developer time**: 1-2 weeks
- **Infrastructure**:
  - Redis: $0 (self-hosted) hoặc $5-10/month (Redis Cloud)
  - Telegram Bot: Free
  - Email SMTP: Free (Gmail) hoặc $5/month (SendGrid)
  - WebSocket: Free (self-hosted)
- **Total monthly**: $5-15

---

Tôi sẽ tiếp tục với Phase 3, 4, 5, 6 trong file tiếp theo. Bạn muốn tôi tiếp tục không?