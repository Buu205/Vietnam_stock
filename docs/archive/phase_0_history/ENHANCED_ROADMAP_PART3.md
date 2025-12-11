# 🚀 ENHANCED ROADMAP PART 3 - AI APIs, Web Dashboard & Analysis

**Continuation from ENHANCED_ROADMAP_PART2.md**

---

## 🤖 PHASE 5: AI API INTEGRATION LAYER (1-2 weeks)

### 5.1. AI Architecture Overview

```
┌────────────────────────────────────────────────────────────────┐
│                      AI ECOSYSTEM                               │
├────────────────────────────────────────────────────────────────┤
│                                                                 │
│  ┌─────────────────┐    ┌─────────────────┐    ┌───────────┐ │
│  │  Claude API     │    │  OpenAI API     │    │  Custom   │ │
│  │                 │    │                 │    │  Models   │ │
│  │  - Analysis     │    │  - Embeddings   │    │  - LSTM   │ │
│  │  - Insights     │    │  - Completion   │    │  - XGBoost│ │
│  │  - Reports      │    │  - Fine-tuned   │    │  - Prophet│ │
│  └─────────────────┘    └─────────────────┘    └───────────┘ │
│           │                       │                     │       │
│           └───────────────────────┴─────────────────────┘       │
│                                   │                             │
│                    ┌──────────────▼──────────────┐             │
│                    │   AI Service Layer          │             │
│                    │   - Context Management      │             │
│                    │   - Prompt Engineering      │             │
│                    │   - Response Validation     │             │
│                    │   - Caching                 │             │
│                    └─────────────────────────────┘             │
│                                   │                             │
│                    ┌──────────────▼──────────────┐             │
│                    │   RAG (Retrieval Augmented  │             │
│                    │         Generation)          │             │
│                    │                             │             │
│                    │  ┌────────┐   ┌─────────┐ │             │
│                    │  │Retriever│───│Generator│ │             │
│                    │  └────────┘   └─────────┘ │             │
│                    │       │                     │             │
│                    │  ┌────▼─────┐              │             │
│                    │  │  Qdrant  │              │             │
│                    │  │ (Vectors)│              │             │
│                    │  └──────────┘              │             │
│                    └─────────────────────────────┘             │
└────────────────────────────────────────────────────────────────┘
```

### 5.2. AI Service Layer Implementation

```python
# src/stock_dashboard/ai/clients/claude_client.py
"""
Claude API client with advanced features:
- Streaming responses
- Function calling
- Caching
- Rate limiting
"""

from typing import List, Dict, Any, Optional, AsyncGenerator
from anthropic import AsyncAnthropic
from anthropic.types import Message, MessageStreamEvent
import asyncio
from functools import lru_cache
import hashlib
import json
from loguru import logger

from stock_dashboard.settings import settings
from stock_dashboard.database.repositories import CacheRepository

class ClaudeClient:
    """Enhanced Claude API client."""

    def __init__(self):
        self.client = AsyncAnthropic(api_key=settings.ai.ANTHROPIC_API_KEY)
        self.model = settings.ai.CLAUDE_MODEL
        self.cache_repo = CacheRepository()

        # Rate limiting (100 requests per minute)
        self.rate_limiter = asyncio.Semaphore(100)
        self.request_times: List[float] = []

    async def generate(
        self,
        prompt: str,
        max_tokens: int = 1024,
        temperature: float = 0.7,
        system: Optional[str] = None,
        tools: Optional[List[Dict]] = None,
        use_cache: bool = True,
        stream: bool = False
    ) -> str:
        """
        Generate response from Claude.

        Args:
            prompt: User prompt
            max_tokens: Max tokens to generate
            temperature: Sampling temperature (0-1)
            system: System prompt
            tools: Function calling tools
            use_cache: Use cached response if available
            stream: Stream response

        Returns:
            Generated text
        """

        # Check cache
        if use_cache:
            cache_key = self._get_cache_key(prompt, system, temperature)
            cached = await self.cache_repo.get(cache_key)
            if cached:
                logger.info(f"Cache hit for prompt: {prompt[:50]}...")
                return cached

        # Rate limiting
        await self._rate_limit()

        # Make API call
        try:
            if stream:
                async for chunk in self._stream_generate(prompt, max_tokens, temperature, system, tools):
                    yield chunk
            else:
                response = await self.client.messages.create(
                    model=self.model,
                    max_tokens=max_tokens,
                    temperature=temperature,
                    system=system if system else [],
                    tools=tools if tools else [],
                    messages=[{"role": "user", "content": prompt}]
                )

                result = response.content[0].text

                # Cache result
                if use_cache:
                    await self.cache_repo.set(cache_key, result, ttl=3600)  # 1 hour

                return result

        except Exception as e:
            logger.error(f"Claude API error: {e}")
            raise

    async def _stream_generate(
        self,
        prompt: str,
        max_tokens: int,
        temperature: float,
        system: Optional[str],
        tools: Optional[List[Dict]]
    ) -> AsyncGenerator[str, None]:
        """Stream generate response."""

        async with self.client.messages.stream(
            model=self.model,
            max_tokens=max_tokens,
            temperature=temperature,
            system=system if system else [],
            tools=tools if tools else [],
            messages=[{"role": "user", "content": prompt}]
        ) as stream:
            async for text in stream.text_stream:
                yield text

    async def analyze_with_tools(
        self,
        prompt: str,
        tools: List[Dict],
        max_iterations: int = 5
    ) -> Dict[str, Any]:
        """
        Analyze with function calling (tool use).

        Args:
            prompt: User query
            tools: Available tools
            max_iterations: Max tool call iterations

        Returns:
            Final response with tool results
        """

        messages = [{"role": "user", "content": prompt}]
        iterations = 0

        while iterations < max_iterations:
            iterations += 1

            response = await self.client.messages.create(
                model=self.model,
                max_tokens=4096,
                tools=tools,
                messages=messages
            )

            # Check if tool use
            if response.stop_reason == "tool_use":
                # Extract tool calls
                tool_results = []

                for block in response.content:
                    if block.type == "tool_use":
                        # Execute tool
                        tool_result = await self._execute_tool(
                            block.name,
                            block.input
                        )

                        tool_results.append({
                            "type": "tool_result",
                            "tool_use_id": block.id,
                            "content": json.dumps(tool_result)
                        })

                # Add assistant response and tool results to messages
                messages.append({"role": "assistant", "content": response.content})
                messages.append({"role": "user", "content": tool_results})

            else:
                # No more tool use, return final response
                return {
                    "response": response.content[0].text,
                    "tool_calls": iterations - 1,
                    "messages": messages
                }

        return {
            "error": "Max iterations reached",
            "messages": messages
        }

    async def _execute_tool(self, tool_name: str, tool_input: Dict) -> Any:
        """Execute MCP tool."""

        # Import tool executors
        from stock_dashboard.mcp.tools import execute_tool

        result = await execute_tool(tool_name, tool_input)
        return result

    def _get_cache_key(self, prompt: str, system: Optional[str], temperature: float) -> str:
        """Generate cache key."""

        content = f"{prompt}|{system}|{temperature}"
        return f"claude:{hashlib.md5(content.encode()).hexdigest()}"

    async def _rate_limit(self):
        """Implement rate limiting."""

        import time

        async with self.rate_limiter:
            current_time = time.time()

            # Remove old timestamps (older than 1 minute)
            self.request_times = [
                t for t in self.request_times
                if current_time - t < 60
            ]

            # Check if limit exceeded
            if len(self.request_times) >= 100:
                wait_time = 60 - (current_time - self.request_times[0])
                if wait_time > 0:
                    logger.warning(f"Rate limit reached, waiting {wait_time:.2f}s")
                    await asyncio.sleep(wait_time)

            self.request_times.append(current_time)

# ============================================================
# OpenAI Client for Embeddings
# ============================================================

class OpenAIClient:
    """OpenAI API client for embeddings."""

    def __init__(self):
        from openai import AsyncOpenAI

        self.client = AsyncOpenAI(api_key=settings.ai.OPENAI_API_KEY)
        self.embedding_model = settings.ai.EMBEDDING_MODEL

    async def create_embedding(
        self,
        text: str,
        model: Optional[str] = None
    ) -> List[float]:
        """
        Create embedding for text.

        Args:
            text: Input text
            model: Embedding model (default: text-embedding-3-small)

        Returns:
            Embedding vector
        """

        if model is None:
            model = self.embedding_model

        try:
            response = await self.client.embeddings.create(
                input=text,
                model=model
            )

            embedding = response.data[0].embedding
            return embedding

        except Exception as e:
            logger.error(f"OpenAI embedding error: {e}")
            raise

    async def batch_create_embeddings(
        self,
        texts: List[str],
        model: Optional[str] = None,
        batch_size: int = 100
    ) -> List[List[float]]:
        """
        Create embeddings in batches.

        Args:
            texts: List of texts
            model: Embedding model
            batch_size: Batch size

        Returns:
            List of embedding vectors
        """

        embeddings = []

        for i in range(0, len(texts), batch_size):
            batch = texts[i:i + batch_size]

            response = await self.client.embeddings.create(
                input=batch,
                model=model or self.embedding_model
            )

            batch_embeddings = [data.embedding for data in response.data]
            embeddings.extend(batch_embeddings)

            logger.info(f"Created embeddings for batch {i//batch_size + 1}/{len(texts)//batch_size + 1}")

        return embeddings
```

### 5.3. RAG (Retrieval Augmented Generation)

```python
# src/stock_dashboard/ai/rag/retriever.py
"""
RAG Retriever using Qdrant vector database.
Enables semantic search over financial documents.
"""

from typing import List, Dict, Any, Optional
from qdrant_client import AsyncQdrantClient
from qdrant_client.models import Distance, VectorParams, PointStruct, Filter, FieldCondition, MatchValue
from loguru import logger

from stock_dashboard.settings import settings
from stock_dashboard.ai.clients import OpenAIClient

class FinancialRetriever:
    """Retriever for financial documents using semantic search."""

    def __init__(self):
        self.qdrant = AsyncQdrantClient(
            url=str(settings.database.QDRANT_URL),
            api_key=settings.database.QDRANT_API_KEY
        )
        self.embedder = OpenAIClient()
        self.collection_name = "financial_documents"

    async def initialize(self):
        """Initialize Qdrant collection."""

        # Check if collection exists
        collections = await self.qdrant.get_collections()
        exists = any(col.name == self.collection_name for col in collections.collections)

        if not exists:
            # Create collection
            await self.qdrant.create_collection(
                collection_name=self.collection_name,
                vectors_config=VectorParams(
                    size=1536,  # text-embedding-3-small dimension
                    distance=Distance.COSINE
                )
            )
            logger.info(f"Created Qdrant collection: {self.collection_name}")

    async def index_document(
        self,
        doc_id: str,
        text: str,
        metadata: Dict[str, Any]
    ):
        """
        Index a document.

        Args:
            doc_id: Unique document ID
            text: Document text
            metadata: Metadata (symbol, date, type, etc.)
        """

        # Create embedding
        embedding = await self.embedder.create_embedding(text)

        # Index in Qdrant
        point = PointStruct(
            id=doc_id,
            vector=embedding,
            payload={
                "text": text,
                **metadata
            }
        )

        await self.qdrant.upsert(
            collection_name=self.collection_name,
            points=[point]
        )

        logger.info(f"Indexed document: {doc_id}")

    async def batch_index_documents(
        self,
        documents: List[Dict[str, Any]]
    ):
        """
        Batch index documents.

        Args:
            documents: List of dicts with keys: doc_id, text, metadata
        """

        # Extract texts
        texts = [doc['text'] for doc in documents]

        # Create embeddings in batch
        embeddings = await self.embedder.batch_create_embeddings(texts)

        # Prepare points
        points = [
            PointStruct(
                id=doc['doc_id'],
                vector=embedding,
                payload={
                    "text": doc['text'],
                    **doc['metadata']
                }
            )
            for doc, embedding in zip(documents, embeddings)
        ]

        # Upsert to Qdrant
        await self.qdrant.upsert(
            collection_name=self.collection_name,
            points=points
        )

        logger.info(f"Batch indexed {len(documents)} documents")

    async def search(
        self,
        query: str,
        symbol: Optional[str] = None,
        doc_type: Optional[str] = None,
        top_k: int = 5
    ) -> List[Dict[str, Any]]:
        """
        Semantic search for relevant documents.

        Args:
            query: Search query
            symbol: Filter by symbol
            doc_type: Filter by document type (news, analysis, report)
            top_k: Number of results

        Returns:
            List of relevant documents with scores
        """

        # Create query embedding
        query_embedding = await self.embedder.create_embedding(query)

        # Build filter
        must_conditions = []

        if symbol:
            must_conditions.append(
                FieldCondition(key="symbol", match=MatchValue(value=symbol))
            )

        if doc_type:
            must_conditions.append(
                FieldCondition(key="type", match=MatchValue(value=doc_type))
            )

        query_filter = Filter(must=must_conditions) if must_conditions else None

        # Search
        results = await self.qdrant.search(
            collection_name=self.collection_name,
            query_vector=query_embedding,
            query_filter=query_filter,
            limit=top_k
        )

        # Format results
        documents = [
            {
                "id": result.id,
                "text": result.payload["text"],
                "metadata": {k: v for k, v in result.payload.items() if k != "text"},
                "score": result.score
            }
            for result in results
        ]

        return documents

# ============================================================
# RAG Generator
# ============================================================

class RAGGenerator:
    """Generate responses using RAG."""

    def __init__(self):
        self.retriever = FinancialRetriever()
        self.claude = ClaudeClient()

    async def generate_with_context(
        self,
        query: str,
        symbol: Optional[str] = None,
        doc_type: Optional[str] = None,
        top_k: int = 5
    ) -> Dict[str, Any]:
        """
        Generate response with retrieved context.

        Args:
            query: User query
            symbol: Filter documents by symbol
            doc_type: Filter by document type
            top_k: Number of documents to retrieve

        Returns:
            Dict with response and sources
        """

        # Retrieve relevant documents
        documents = await self.retriever.search(
            query=query,
            symbol=symbol,
            doc_type=doc_type,
            top_k=top_k
        )

        if not documents:
            return {
                "response": "Không tìm thấy thông tin liên quan.",
                "sources": []
            }

        # Build context from retrieved documents
        context_parts = []
        for i, doc in enumerate(documents, 1):
            context_parts.append(f"""
[Tài liệu {i}] (Độ liên quan: {doc['score']:.2f})
{doc['text']}
Metadata: {doc['metadata']}
""")

        context = "\n\n".join(context_parts)

        # Build prompt
        prompt = f"""
Bạn là chuyên gia phân tích tài chính. Dựa trên các tài liệu được cung cấp, hãy trả lời câu hỏi của người dùng.

## Tài liệu tham khảo:
{context}

## Câu hỏi:
{query}

Hãy trả lời dựa trên thông tin trong tài liệu. Nếu thông tin không đủ, hãy nói rõ.
Trả lời bằng tiếng Việt, ngắn gọn và dễ hiểu.
"""

        # Generate response
        response = await self.claude.generate(
            prompt=prompt,
            max_tokens=2048,
            temperature=0.3
        )

        return {
            "response": response,
            "sources": [
                {
                    "text": doc['text'][:200] + "...",
                    "metadata": doc['metadata'],
                    "score": doc['score']
                }
                for doc in documents
            ],
            "num_sources": len(documents)
        }
```

### 5.4. Custom ML Models

```python
# src/stock_dashboard/ai/models/price_predictor.py
"""
Custom ML models for price prediction.
Using LSTM, XGBoost, and Prophet.
"""

import numpy as np
import pandas as pd
from typing import Dict, Any, List, Optional
from loguru import logger

# LSTM
from tensorflow.keras.models import Sequential, load_model
from tensorflow.keras.layers import LSTM, Dense, Dropout
from sklearn.preprocessing import MinMaxScaler

# XGBoost
import xgboost as xgb

# Prophet
from prophet import Prophet

class PricePredictor:
    """Price prediction using multiple models."""

    def __init__(self, model_type: str = "lstm"):
        """
        Initialize predictor.

        Args:
            model_type: Model type (lstm, xgboost, prophet, ensemble)
        """
        self.model_type = model_type
        self.model = None
        self.scaler = MinMaxScaler()

    def train_lstm(
        self,
        data: pd.DataFrame,
        lookback: int = 60,
        epochs: int = 50,
        batch_size: int = 32
    ):
        """
        Train LSTM model.

        Args:
            data: DataFrame with 'close' prices
            lookback: Number of days to look back
            epochs: Training epochs
            batch_size: Batch size
        """

        # Prepare data
        prices = data['close'].values.reshape(-1, 1)
        scaled_data = self.scaler.fit_transform(prices)

        X, y = [], []
        for i in range(lookback, len(scaled_data)):
            X.append(scaled_data[i-lookback:i, 0])
            y.append(scaled_data[i, 0])

        X, y = np.array(X), np.array(y)
        X = X.reshape(X.shape[0], X.shape[1], 1)

        # Build model
        self.model = Sequential([
            LSTM(units=50, return_sequences=True, input_shape=(X.shape[1], 1)),
            Dropout(0.2),
            LSTM(units=50, return_sequences=True),
            Dropout(0.2),
            LSTM(units=50),
            Dropout(0.2),
            Dense(units=1)
        ])

        self.model.compile(optimizer='adam', loss='mean_squared_error')

        # Train
        self.model.fit(X, y, epochs=epochs, batch_size=batch_size, verbose=1)

        logger.info("LSTM model trained")

    def predict_lstm(
        self,
        recent_data: pd.DataFrame,
        days_ahead: int = 5
    ) -> List[float]:
        """
        Predict future prices using LSTM.

        Args:
            recent_data: Recent price data (at least 60 days)
            days_ahead: Number of days to predict

        Returns:
            List of predicted prices
        """

        if self.model is None:
            raise ValueError("Model not trained")

        # Prepare input
        prices = recent_data['close'].values.reshape(-1, 1)
        scaled_data = self.scaler.transform(prices)

        predictions = []
        current_batch = scaled_data[-60:].reshape(1, 60, 1)

        for _ in range(days_ahead):
            # Predict next day
            pred = self.model.predict(current_batch, verbose=0)[0]
            predictions.append(pred)

            # Update batch
            current_batch = np.append(current_batch[:, 1:, :], [[pred]], axis=1)

        # Inverse transform
        predictions = self.scaler.inverse_transform(np.array(predictions).reshape(-1, 1))
        return predictions.flatten().tolist()

    def train_xgboost(
        self,
        data: pd.DataFrame,
        features: List[str]
    ):
        """
        Train XGBoost model.

        Args:
            data: DataFrame with features and target
            features: Feature column names
        """

        X = data[features].values
        y = data['close'].shift(-1).fillna(method='ffill').values  # Next day price

        # Split train/test
        split = int(0.8 * len(X))
        X_train, X_test = X[:split], X[split:]
        y_train, y_test = y[:split], y[split:]

        # Train
        self.model = xgb.XGBRegressor(
            objective='reg:squarederror',
            n_estimators=100,
            max_depth=5,
            learning_rate=0.1
        )

        self.model.fit(X_train, y_train)

        # Evaluate
        score = self.model.score(X_test, y_test)
        logger.info(f"XGBoost R² score: {score:.4f}")

    def train_prophet(
        self,
        data: pd.DataFrame
    ):
        """
        Train Prophet model.

        Args:
            data: DataFrame with 'date' and 'close' columns
        """

        # Prepare data for Prophet
        df = data[['date', 'close']].copy()
        df.columns = ['ds', 'y']

        # Train
        self.model = Prophet(
            yearly_seasonality=True,
            weekly_seasonality=True,
            daily_seasonality=False
        )

        self.model.fit(df)
        logger.info("Prophet model trained")

    def predict_prophet(
        self,
        days_ahead: int = 30
    ) -> pd.DataFrame:
        """
        Predict using Prophet.

        Args:
            days_ahead: Number of days to forecast

        Returns:
            DataFrame with predictions
        """

        if self.model is None:
            raise ValueError("Model not trained")

        # Make future dataframe
        future = self.model.make_future_dataframe(periods=days_ahead)

        # Predict
        forecast = self.model.predict(future)

        return forecast[['ds', 'yhat', 'yhat_lower', 'yhat_upper']].tail(days_ahead)
```

### ✅ Ưu điểm Phase 5

1. **Powerful AI**: Claude + OpenAI + Custom models
2. **RAG enables**: Semantic search, contextual answers
3. **Flexible**: Easy to add new AI providers
4. **Cached**: Reduce API costs
5. **Production-ready**: Rate limiting, error handling

### ⚠️ Nhược điểm Phase 5

1. **API costs**: Can be expensive at scale
2. **Complexity**: Many AI components to maintain
3. **Accuracy**: AI can hallucinate, needs validation
4. **Latency**: API calls add 2-5s latency

### 💰 Chi phí Phase 5

- **Development**: 1-2 weeks
- **Monthly costs**:
  - Claude API: $10-100 (depends on usage)
  - OpenAI Embeddings: $5-20
  - Qdrant: $0 (self-hosted) or $25 (cloud)
  - GPU for custom models: $0 (CPU) or $50-200 (GPU cloud)
- **Total**: $15-345/month

---

## 🌐 PHASE 6: WEB DASHBOARD WITH LIVE UPDATES (1 week)

### 6.1. FastAPI Backend

```python
# src/stock_dashboard/web/api/main.py
"""
FastAPI backend for web dashboard.
Provides REST API + WebSocket for live updates.
"""

from fastapi import FastAPI, WebSocket, WebSocketDisconnect, Depends, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from typing import List, Dict, Any
import asyncio
from loguru import logger

from stock_dashboard.web.api.routers import stocks, alerts, analysis, portfolio
from stock_dashboard.alerts.notifiers import WebSocketNotifier

# Create FastAPI app
app = FastAPI(
    title="Stock Dashboard API",
    description="API for Vietnamese Stock Market Dashboard",
    version="2.0.0"
)

# CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # In production, specify domains
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"]
)

# Include routers
app.include_router(stocks.router, prefix="/api/stocks", tags=["Stocks"])
app.include_router(alerts.router, prefix="/api/alerts", tags=["Alerts"])
app.include_router(analysis.router, prefix="/api/analysis", tags=["Analysis"])
app.include_router(portfolio.router, prefix="/api/portfolio", tags=["Portfolio"])

# WebSocket manager
class ConnectionManager:
    def __init__(self):
        self.active_connections: List[WebSocket] = []

    async def connect(self, websocket: WebSocket):
        await websocket.accept()
        self.active_connections.append(websocket)
        logger.info(f"WebSocket connected: {len(self.active_connections)} active")

    def disconnect(self, websocket: WebSocket):
        self.active_connections.remove(websocket)
        logger.info(f"WebSocket disconnected: {len(self.active_connections)} active")

    async def broadcast(self, message: Dict[str, Any]):
        for connection in self.active_connections:
            try:
                await connection.send_json(message)
            except:
                pass

manager = ConnectionManager()

@app.websocket("/ws")
async def websocket_endpoint(websocket: WebSocket):
    """WebSocket endpoint for live updates."""

    await manager.connect(websocket)

    try:
        while True:
            # Receive message from client
            data = await websocket.receive_json()

            # Handle subscription
            if data.get("action") == "subscribe":
                symbols = data.get("symbols", [])
                # Store subscription (implementation depends on your needs)
                await websocket.send_json({
                    "status": "subscribed",
                    "symbols": symbols
                })

    except WebSocketDisconnect:
        manager.disconnect(websocket)

@app.get("/")
async def root():
    """Root endpoint."""
    return {
        "message": "Stock Dashboard API",
        "version": "2.0.0",
        "docs": "/docs"
    }

@app.get("/health")
async def health_check():
    """Health check endpoint."""
    return {"status": "healthy"}
```

### 6.2. Stock API Router

```python
# src/stock_dashboard/web/api/routers/stocks.py
"""
Stock data API endpoints.
"""

from fastapi import APIRouter, Query, HTTPException
from typing import List, Optional
from datetime import datetime, timedelta
from pydantic import BaseModel

from stock_dashboard.database.repositories import (
    OHLCVRepository,
    TechnicalRepository,
    CompanyRepository
)

router = APIRouter()

# Response models
class StockPrice(BaseModel):
    date: datetime
    open: float
    high: float
    low: float
    close: float
    volume: int

class StockInfo(BaseModel):
    symbol: str
    name: str
    exchange: str
    industry: str
    market_cap: float

@router.get("/search")
async def search_stocks(
    q: str = Query(..., min_length=1, description="Search query"),
    limit: int = Query(10, ge=1, le=50)
) -> List[StockInfo]:
    """Search for stocks by symbol or name."""

    # Implementation
    repo = CompanyRepository()
    results = await repo.search(query=q, limit=limit)

    return results

@router.get("/{symbol}/price")
async def get_stock_price(
    symbol: str,
    start_date: Optional[datetime] = Query(None),
    end_date: Optional[datetime] = Query(None),
    interval: str = Query("1D", regex="^(1D|1W)$")
) -> List[StockPrice]:
    """Get historical prices for a stock."""

    # Default to last 90 days
    if start_date is None:
        start_date = datetime.now() - timedelta(days=90)

    if end_date is None:
        end_date = datetime.now()

    repo = OHLCVRepository()
    data = await repo.get_prices(
        symbol=symbol,
        start_date=start_date,
        end_date=end_date,
        interval=interval
    )

    if data.empty:
        raise HTTPException(status_code=404, detail=f"No data found for {symbol}")

    # Convert to response model
    prices = [
        StockPrice(
            date=row.name,
            open=row['open'],
            high=row['high'],
            low=row['low'],
            close=row['close'],
            volume=row['volume']
        )
        for _, row in data.iterrows()
    ]

    return prices

@router.get("/{symbol}/indicators")
async def get_technical_indicators(
    symbol: str,
    start_date: Optional[datetime] = Query(None),
    end_date: Optional[datetime] = Query(None)
) -> Dict[str, Any]:
    """Get technical indicators for a stock."""

    if start_date is None:
        start_date = datetime.now() - timedelta(days=90)

    if end_date is None:
        end_date = datetime.now()

    repo = TechnicalRepository()
    data = await repo.get_indicators(
        symbol=symbol,
        start_date=start_date,
        end_date=end_date
    )

    if data.empty:
        raise HTTPException(status_code=404, detail=f"No indicators for {symbol}")

    return {
        "symbol": symbol,
        "data": data.to_dict('records')
    }
```

### 6.3. Modern Web Dashboard (React)

```html
<!-- public/modern-dashboard.html -->
<!DOCTYPE html>
<html lang="vi">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Stock Dashboard - Modern UI</title>

    <!-- Tailwind CSS -->
    <script src="https://cdn.tailwindcss.com"></script>

    <!-- Chart.js -->
    <script src="https://cdn.jsdelivr.net/npm/chart.js"></script>

    <!-- Alpine.js for reactivity -->
    <script defer src="https://cdn.jsdelivr.net/npm/alpinejs@3.x.x/dist/cdn.min.js"></script>

    <style>
        [x-cloak] { display: none !important; }
    </style>
</head>
<body class="bg-gray-50">
    <div x-data="dashboardApp()" x-init="init()" class="min-h-screen">
        <!-- Header -->
        <header class="bg-white shadow-sm border-b">
            <div class="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-4">
                <div class="flex justify-between items-center">
                    <div class="flex items-center space-x-4">
                        <h1 class="text-2xl font-bold text-gray-900">
                            📈 Stock Dashboard
                        </h1>

                        <!-- Connection status -->
                        <span
                            :class="wsConnected ? 'bg-green-100 text-green-800' : 'bg-red-100 text-red-800'"
                            class="px-3 py-1 rounded-full text-xs font-medium"
                        >
                            <span x-show="wsConnected">● Connected</span>
                            <span x-show="!wsConnected">● Disconnected</span>
                        </span>
                    </div>

                    <!-- Search -->
                    <div class="relative">
                        <input
                            type="text"
                            x-model="searchQuery"
                            @input.debounce.300ms="searchStocks()"
                            placeholder="Tìm kiếm mã CK..."
                            class="w-64 px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent"
                        >

                        <!-- Search results dropdown -->
                        <div
                            x-show="searchResults.length > 0"
                            x-cloak
                            class="absolute top-full mt-2 w-full bg-white rounded-lg shadow-lg border z-10"
                        >
                            <template x-for="stock in searchResults" :key="stock.symbol">
                                <div
                                    @click="selectStock(stock.symbol)"
                                    class="px-4 py-2 hover:bg-gray-50 cursor-pointer border-b last:border-b-0"
                                >
                                    <div class="font-semibold" x-text="stock.symbol"></div>
                                    <div class="text-sm text-gray-600" x-text="stock.name"></div>
                                </div>
                            </template>
                        </div>
                    </div>
                </div>
            </div>
        </header>

        <!-- Main Content -->
        <main class="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
            <!-- Stock Info Card -->
            <div x-show="selectedSymbol" class="bg-white rounded-lg shadow-sm border p-6 mb-6">
                <div class="flex justify-between items-start">
                    <div>
                        <h2 class="text-3xl font-bold text-gray-900" x-text="selectedSymbol"></h2>
                        <p class="text-gray-600" x-text="stockInfo.name"></p>
                    </div>

                    <div class="text-right">
                        <div class="text-3xl font-bold" x-text="formatPrice(latestPrice)"></div>
                        <div
                            :class="priceChange >= 0 ? 'text-green-600' : 'text-red-600'"
                            class="text-lg font-semibold"
                        >
                            <span x-text="priceChange >= 0 ? '+' : ''"></span>
                            <span x-text="formatPrice(priceChange)"></span>
                            (<span x-text="priceChangePct.toFixed(2)"></span>%)
                        </div>
                    </div>
                </div>

                <!-- Stats -->
                <div class="grid grid-cols-4 gap-4 mt-6">
                    <div class="text-center">
                        <div class="text-sm text-gray-600">Open</div>
                        <div class="text-lg font-semibold" x-text="formatPrice(stockStats.open)"></div>
                    </div>
                    <div class="text-center">
                        <div class="text-sm text-gray-600">High</div>
                        <div class="text-lg font-semibold text-green-600" x-text="formatPrice(stockStats.high)"></div>
                    </div>
                    <div class="text-center">
                        <div class="text-sm text-gray-600">Low</div>
                        <div class="text-lg font-semibold text-red-600" x-text="formatPrice(stockStats.low)"></div>
                    </div>
                    <div class="text-center">
                        <div class="text-sm text-gray-600">Volume</div>
                        <div class="text-lg font-semibold" x-text="formatVolume(stockStats.volume)"></div>
                    </div>
                </div>
            </div>

            <!-- Charts Grid -->
            <div class="grid grid-cols-2 gap-6 mb-6">
                <!-- Price Chart -->
                <div class="bg-white rounded-lg shadow-sm border p-6">
                    <h3 class="text-lg font-semibold mb-4">Price Chart</h3>
                    <canvas id="priceChart"></canvas>
                </div>

                <!-- Volume Chart -->
                <div class="bg-white rounded-lg shadow-sm border p-6">
                    <h3 class="text-lg font-semibold mb-4">Volume</h3>
                    <canvas id="volumeChart"></canvas>
                </div>

                <!-- RSI Indicator -->
                <div class="bg-white rounded-lg shadow-sm border p-6">
                    <h3 class="text-lg font-semibold mb-4">RSI Indicator</h3>
                    <canvas id="rsiChart"></canvas>
                </div>

                <!-- MACD Indicator -->
                <div class="bg-white rounded-lg shadow-sm border p-6">
                    <h3 class="text-lg font-semibold mb-4">MACD</h3>
                    <canvas id="macdChart"></canvas>
                </div>
            </div>

            <!-- AI Analysis -->
            <div x-show="aiAnalysis" class="bg-gradient-to-r from-purple-50 to-blue-50 rounded-lg shadow-sm border p-6">
                <div class="flex items-center mb-4">
                    <span class="text-2xl mr-2">🤖</span>
                    <h3 class="text-lg font-semibold">AI Analysis</h3>
                </div>

                <div class="prose max-w-none">
                    <div x-html="aiAnalysis"></div>
                </div>

                <button
                    @click="refreshAIAnalysis()"
                    class="mt-4 px-4 py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700 transition"
                >
                    Refresh Analysis
                </button>
            </div>
        </main>
    </div>

    <script>
        function dashboardApp() {
            return {
                // State
                wsConnected: false,
                ws: null,
                selectedSymbol: null,
                searchQuery: '',
                searchResults: [],
                stockInfo: {},
                latestPrice: 0,
                priceChange: 0,
                priceChangePct: 0,
                stockStats: {},
                priceData: [],
                indicators: {},
                aiAnalysis: null,

                // Charts
                priceChart: null,
                volumeChart: null,
                rsiChart: null,
                macdChart: null,

                // Initialize
                async init() {
                    this.connectWebSocket();
                    this.initCharts();
                },

                // WebSocket
                connectWebSocket() {
                    this.ws = new WebSocket('ws://localhost:8000/ws');

                    this.ws.onopen = () => {
                        this.wsConnected = true;
                        console.log('WebSocket connected');
                    };

                    this.ws.onmessage = (event) => {
                        const data = JSON.parse(event.data);
                        this.handleWebSocketMessage(data);
                    };

                    this.ws.onclose = () => {
                        this.wsConnected = false;
                        console.log('WebSocket disconnected');

                        // Reconnect after 3s
                        setTimeout(() => this.connectWebSocket(), 3000);
                    };

                    this.ws.onerror = (error) => {
                        console.error('WebSocket error:', error);
                    };
                },

                handleWebSocketMessage(data) {
                    if (data.type === 'price_update' && data.symbol === this.selectedSymbol) {
                        this.updatePrice(data);
                    } else if (data.type === 'alert') {
                        this.showAlert(data);
                    }
                },

                // Stock search
                async searchStocks() {
                    if (this.searchQuery.length < 1) {
                        this.searchResults = [];
                        return;
                    }

                    try {
                        const response = await fetch(`http://localhost:8000/api/stocks/search?q=${this.searchQuery}`);
                        this.searchResults = await response.json();
                    } catch (error) {
                        console.error('Search error:', error);
                    }
                },

                // Select stock
                async selectStock(symbol) {
                    this.selectedSymbol = symbol;
                    this.searchResults = [];
                    this.searchQuery = '';

                    // Subscribe via WebSocket
                    if (this.ws && this.ws.readyState === WebSocket.OPEN) {
                        this.ws.send(JSON.stringify({
                            action: 'subscribe',
                            symbols: [symbol]
                        }));
                    }

                    // Load stock data
                    await Promise.all([
                        this.loadPriceData(symbol),
                        this.loadIndicators(symbol),
                        this.loadAIAnalysis(symbol)
                    ]);
                },

                // Load price data
                async loadPriceData(symbol) {
                    try {
                        const response = await fetch(`http://localhost:8000/api/stocks/${symbol}/price`);
                        this.priceData = await response.json();

                        if (this.priceData.length > 0) {
                            const latest = this.priceData[this.priceData.length - 1];
                            const previous = this.priceData[this.priceData.length - 2];

                            this.latestPrice = latest.close;
                            this.priceChange = latest.close - previous.close;
                            this.priceChangePct = (this.priceChange / previous.close) * 100;

                            this.stockStats = {
                                open: latest.open,
                                high: latest.high,
                                low: latest.low,
                                volume: latest.volume
                            };

                            this.updatePriceChart();
                            this.updateVolumeChart();
                        }
                    } catch (error) {
                        console.error('Load price error:', error);
                    }
                },

                // Load indicators
                async loadIndicators(symbol) {
                    try {
                        const response = await fetch(`http://localhost:8000/api/stocks/${symbol}/indicators`);
                        const data = await response.json();
                        this.indicators = data.data;

                        this.updateRSIChart();
                        this.updateMACDChart();
                    } catch (error) {
                        console.error('Load indicators error:', error);
                    }
                },

                // Load AI analysis
                async loadAIAnalysis(symbol) {
                    try {
                        const response = await fetch(`http://localhost:8000/api/analysis/${symbol}/comprehensive`);
                        const data = await response.json();
                        this.aiAnalysis = data.ai_insights;
                    } catch (error) {
                        console.error('Load AI analysis error:', error);
                    }
                },

                // Initialize charts
                initCharts() {
                    const commonOptions = {
                        responsive: true,
                        maintainAspectRatio: true,
                        plugins: {
                            legend: {
                                display: true,
                                position: 'top'
                            }
                        }
                    };

                    this.priceChart = new Chart(
                        document.getElementById('priceChart'),
                        {
                            type: 'line',
                            data: { labels: [], datasets: [] },
                            options: commonOptions
                        }
                    );

                    this.volumeChart = new Chart(
                        document.getElementById('volumeChart'),
                        {
                            type: 'bar',
                            data: { labels: [], datasets: [] },
                            options: commonOptions
                        }
                    );

                    this.rsiChart = new Chart(
                        document.getElementById('rsiChart'),
                        {
                            type: 'line',
                            data: { labels: [], datasets: [] },
                            options: commonOptions
                        }
                    );

                    this.macdChart = new Chart(
                        document.getElementById('macdChart'),
                        {
                            type: 'line',
                            data: { labels: [], datasets: [] },
                            options: commonOptions
                        }
                    );
                },

                // Update charts
                updatePriceChart() {
                    const labels = this.priceData.map(d => new Date(d.date).toLocaleDateString());
                    const prices = this.priceData.map(d => d.close);

                    this.priceChart.data.labels = labels;
                    this.priceChart.data.datasets = [{
                        label: 'Close Price',
                        data: prices,
                        borderColor: 'rgb(59, 130, 246)',
                        backgroundColor: 'rgba(59, 130, 246, 0.1)',
                        tension: 0.1
                    }];
                    this.priceChart.update();
                },

                updateVolumeChart() {
                    const labels = this.priceData.map(d => new Date(d.date).toLocaleDateString());
                    const volumes = this.priceData.map(d => d.volume);

                    this.volumeChart.data.labels = labels;
                    this.volumeChart.data.datasets = [{
                        label: 'Volume',
                        data: volumes,
                        backgroundColor: 'rgba(59, 130, 246, 0.5)'
                    }];
                    this.volumeChart.update();
                },

                updateRSIChart() {
                    if (!this.indicators || this.indicators.length === 0) return;

                    const labels = this.indicators.map(d => new Date(d.time).toLocaleDateString());
                    const rsi = this.indicators.map(d => d.rsi);

                    this.rsiChart.data.labels = labels;
                    this.rsiChart.data.datasets = [{
                        label: 'RSI',
                        data: rsi,
                        borderColor: 'rgb(168, 85, 247)',
                        backgroundColor: 'rgba(168, 85, 247, 0.1)',
                        tension: 0.1
                    }];
                    this.rsiChart.update();
                },

                updateMACDChart() {
                    if (!this.indicators || this.indicators.length === 0) return;

                    const labels = this.indicators.map(d => new Date(d.time).toLocaleDateString());
                    const macd = this.indicators.map(d => d.macd);
                    const signal = this.indicators.map(d => d.macd_signal);
                    const histogram = this.indicators.map(d => d.macd_histogram);

                    this.macdChart.data.labels = labels;
                    this.macdChart.data.datasets = [
                        {
                            label: 'MACD',
                            data: macd,
                            borderColor: 'rgb(59, 130, 246)',
                            backgroundColor: 'rgba(59, 130, 246, 0.1)',
                            type: 'line'
                        },
                        {
                            label: 'Signal',
                            data: signal,
                            borderColor: 'rgb(239, 68, 68)',
                            backgroundColor: 'rgba(239, 68, 68, 0.1)',
                            type: 'line'
                        },
                        {
                            label: 'Histogram',
                            data: histogram,
                            backgroundColor: 'rgba(16, 185, 129, 0.5)',
                            type: 'bar'
                        }
                    ];
                    this.macdChart.update();
                },

                // Update price from WebSocket
                updatePrice(data) {
                    this.latestPrice = data.price;
                    this.priceChange = data.change;
                    this.priceChangePct = data.change_pct;

                    // Add to chart data
                    this.priceData.push({
                        date: new Date().toISOString(),
                        close: data.price,
                        volume: data.volume
                    });

                    // Keep last 100 points
                    if (this.priceData.length > 100) {
                        this.priceData.shift();
                    }

                    this.updatePriceChart();
                },

                // Refresh AI analysis
                async refreshAIAnalysis() {
                    await this.loadAIAnalysis(this.selectedSymbol);
                },

                // Helpers
                formatPrice(value) {
                    return new Intl.NumberFormat('vi-VN').format(value);
                },

                formatVolume(value) {
                    if (value >= 1000000) {
                        return (value / 1000000).toFixed(1) + 'M';
                    } else if (value >= 1000) {
                        return (value / 1000).toFixed(1) + 'K';
                    }
                    return value.toString();
                },

                showAlert(alert) {
                    // Implement toast notification
                    console.log('Alert:', alert);
                }
            }
        }
    </script>
</body>
</html>
```

### ✅ Ưu điểm Phase 6

1. **Modern UI**: Clean, responsive design
2. **Real-time updates**: WebSocket for live data
3. **Interactive charts**: Chart.js with multiple indicators
4. **Fast**: FastAPI backend, Alpine.js frontend
5. **AI integration**: Real-time AI analysis display

### ⚠️ Nhược điểm Phase 6

1. **Single page**: Not a full SPA (can upgrade to React/Vue later)
2. **Limited customization**: Need more work for advanced features
3. **No authentication**: Would need to add auth layer

### 💰 Chi phí Phase 6

- **Development**: 1 week
- **Infrastructure**:
  - FastAPI hosting: $0 (same server as Streamlit)
  - CDN for static assets: $0 (can use free CDNs)
- **Total**: $0 additional cost

---

Tôi sẽ tạo file cuối cùng với phân tích so sánh chi tiết, cost analysis và risk assessment. Tiếp tục nhé!