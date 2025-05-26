# MCP Service Development and Registration Guide

## 1. MCP Service Overview

### Definition and Purpose of MCP (Model-Connect Protocol)
MCP (Model-Context Protocol) is a protocol that standardizes communication between AI models and external services. This allows AI systems to access external tools and services to extend their functionality.

### How MCP Services Integrate with AI Systems
MCP services provide tools to AI systems. AI systems can call these tools to perform various tasks such as data retrieval, calculations, external API calls, and more. Each tool has a clear input schema and output format, enabling AI systems to use the tools effectively.

### MCP Hub Architecture Diagram

```
┌─────────────┐      ┌─────────────┐      ┌─────────────────┐
│             │      │             │      │                 │
│overdivecore │◄────►│  MCP Server │◄────►│   MCP Service   │
│             │      │             │      │  (Your Service) │
└─────────────┘      └─────────────┘      └─────────────────┘
                                                  ▲
                                                  │
                                                  ▼
                                          ┌─────────────────┐
                                          │                 │
                                          │External API/Svc │
                                          │                 │
                                          └─────────────────┘
```

## 2. Technical Requirements

- Python 3.11 or higher
- FastAPI and FastMCP framework
- Docker support
- Required packages list (requirements.txt example)

```
fastapi>=0.95.0
fastmcp>=0.1.0
uvicorn>=0.21.0
pydantic>=2.0.0
```

## 3. MCP Service Implementation Guide

### 3.1 Required Endpoints

#### `/health` Endpoint Implementation (Status Check)
All MCP services must implement a `/health` endpoint. This endpoint is used to check the status of the service.

#### Response Format: `{"status": "ok"}`

```python
@mcp.tool()
async def health():
    """Service status check"""
    return {"status": "ok"}
```

### 3.2 Tool Definition Method

#### How to Create Tool Schemas
Each tool must include the following elements:
- Name: Unique identifier for the tool
- Description: Description of the tool's functionality
- Input Schema: Definition of parameters the tool accepts

#### Name, Description, and Input Schema Definition
The FastMCP framework automatically generates the tool's schema using Python function type hints and docstrings.

#### Example Code

```python
@mcp.tool()
async def weather_forecast(city: str, days: int = 3):
    """Provides weather forecast for a specific city.
    
    Args:
        city: City name to check the weather for
        days: Number of days for the forecast (default: 3)
        
    Returns:
        Weather forecast information
    """
    # Tool logic implementation
    forecast = get_weather_data(city, days)
    return forecast
```

### 3.3 Tool Definition JSON Generation (Required)

#### Importance
MCP services MUST generate and provide tool definition JSON. This definition is essential for AI systems to understand and correctly call the tools.

#### Tool Definition JSON Structure
Tool definition JSON must follow this structure:
- Each tool must include `name`, `description`, and `parameters` fields.
- `parameters` must follow JSON Schema format.

#### Tool Definition JSON Generation and Provision Method

```python
# Tool definition JSON generation function (required implementation)
def generate_tool_definitions():
    tools = [
        {
            "name": "health",
            "description": "Service status check",
            "parameters": {
                "type": "object",
                "properties": {},
                "required": []
            }
        },
        {
            "name": "get_weather",
            "description": "Provides current weather and forecast for a specific city.",
            "parameters": {
                "type": "object",
                "properties": {
                    "city": {
                        "type": "string",
                        "description": "City name to check the weather for"
                    },
                    "country_code": {
                        "type": "string",
                        "description": "Country code (e.g., 'US', 'UK')"
                    },
                    "days": {
                        "type": "integer",
                        "description": "Number of days for the forecast",
                        "default": 3,
                        "minimum": 1,
                        "maximum": 7
                    },
                    "api_key": {
                        "type": "string",
                        "description": "Weather API key (uses default if not provided)"
                    }
                },
                "required": ["city"]
            }
        }
    ]
    
    return tools

# Endpoint to provide tool definitions (required implementation)
@mcp.tool()
async def get_tool_definitions():
    """Provides MCP tool definitions in JSON format."""
    return {"tools": generate_tool_definitions()}

# Generate tool definition JSON file on server start (optional)
if __name__ == "__main__":
    with open("tool_definitions.json", "w", encoding="utf-8") as f:
        json.dump({"tools": generate_tool_definitions()}, f, ensure_ascii=False, indent=2)
    print("Tool definition JSON file has been generated: tool_definitions.json")
```

### 3.4 Tool Implementation Method

#### Using the `@mcp.tool()` Decorator
Use the `@mcp.tool()` decorator provided by the FastMCP framework to register a function as an MCP tool.

#### Parameter Handling and Response Format
- Parameters are defined as function parameters.
- Responses must be JSON serializable objects.

#### Exception Handling Method

```python
@mcp.tool()
async def divide_numbers(a: float, b: float):
    """Divides two numbers.
    
    Args:
        a: Number to be divided
        b: Divisor
        
    Returns:
        Division result
    """
    try:
        if b == 0:
            raise ValueError("Cannot divide by zero.")
        return {"result": a / b}
    except Exception as e:
        # Exception handling
        return {"error": str(e)}
```

## 4. Deployment and Registration Method

### Dockerfile Example

```dockerfile
FROM python:3.11-slim

WORKDIR /app

COPY requirements.txt .
RUN pip install -r requirements.txt

COPY . .

ENV PYTHONPATH=/app

CMD ["python", "-m", "uvicorn", "server:mcp", "--host", "0.0.0.0", "--port", "8000"]
```

### Local Testing Method

1. Run the service in your local environment:
```bash
uvicorn server:mcp --host 0.0.0.0 --port 8000
```

2. Test the tools:
```bash
curl -X POST "http://localhost:8000/tools/sample_tool" -H "Content-Type: application/json" -d '{"arg1": "test", "arg2": 5}'
```

3. Check the status:
```bash
curl "http://localhost:8000/health"
```

### Registering with the MCP Server

1. Build your service as a Docker image:
```bash
docker build -t my-mcp-service:latest .
```

2. Push the image to a registry:
```bash
docker push my-registry/my-mcp-service:latest
```

3. Request service registration from the MCP server administrator:
   - Service name
   - Service description
   - List of tools and descriptions
   - Docker image location

## 5. Example Code

### 5.1 Basic MCP Service Template

```python
# server.py
from fastmcp import FastMCP
import uvicorn

# Create FastMCP object
mcp = FastMCP()

@mcp.tool()
async def health():
    """Service status check"""
    return {"status": "ok"}

@mcp.tool()
async def sample_tool(arg1: str, arg2: int = 10):
    """Sample tool implementation example
    
    Args:
        arg1: Description of the first argument
        arg2: Description of the second argument (default: 10)
        
    Returns:
        Processing result
    """
    # Tool logic implementation
    result = {"arg1": arg1, "arg2": arg2, "result": f"{arg1} processed with value {arg2}"}
    return result

# For direct server execution
if __name__ == "__main__":
    uvicorn.run(mcp, host="0.0.0.0", port=8000)
```

### 5.2 Advanced MCP Service Example

```python
# advanced_server.py
from fastmcp import FastMCP
from pydantic import BaseModel, Field
import uvicorn
import httpx
import logging

# Logging configuration
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("mcp_service")

# Create FastMCP object
mcp = FastMCP()

# Input model definition
class TranslationRequest(BaseModel):
    text: str = Field(..., description="Text to translate")
    source_lang: str = Field(..., description="Source language code (e.g., 'en', 'fr')")
    target_lang: str = Field(..., description="Target language code (e.g., 'en', 'fr')")

@mcp.tool()
async def health():
    """Service status check"""
    return {"status": "ok"}

@mcp.tool()
async def translate(req: TranslationRequest):
    """Translates text from one language to another.
    
    Args:
        req: Translation request information
        
    Returns:
        Translated text
    """
    logger.info(f"Translation request: {req}")
    
    try:
        # External translation API call (example)
        async with httpx.AsyncClient() as client:
            response = await client.post(
                "https://api.translation-service.com/translate",
                json={
                    "text": req.text,
                    "source": req.source_lang,
                    "target": req.target_lang
                },
                headers={"Authorization": "Bearer YOUR_API_KEY"}
            )
            
            if response.status_code != 200:
                logger.error(f"Translation API error: {response.text}")
                return {"error": "Translation service error", "details": response.text}
                
            translation_result = response.json()
            return {
                "original_text": req.text,
                "translated_text": translation_result["translated_text"],
                "source_language": req.source_lang,
                "target_language": req.target_lang
            }
            
    except Exception as e:
        logger.exception("Translation error")
        return {"error": str(e)}

# For direct server execution
if __name__ == "__main__":
    uvicorn.run(mcp, host="0.0.0.0", port=8000)
```
## 6. Security and Best Practices

### API Key Management

API keys should be received from the client through API calls. This allows different clients to use different API keys when accessing external services.

#### How to Receive API Keys

```python
# Add API key field to Pydantic model
class WeatherRequest(BaseModel):
    city: str = Field(..., description="City name to check the weather for")
    api_key: Optional[str] = Field(None, description="Weather API key")

# Use API key in tool implementation
@mcp.tool()
async def get_weather(request: WeatherRequest):
    # Extract API key
    api_key = request.api_key or DEFAULT_API_KEY
    
    # Use API key to call external service
    # ...
```

#### Setting Default API Keys (for fallback)

```python
# .env file
# API_KEY=default_api_key_for_development

# Get default value in code
import os
from dotenv import load_dotenv

load_dotenv()
DEFAULT_API_KEY = os.environ.get("API_KEY", "fallback_key")
```

### Request Validation

It's recommended to validate all input data using Pydantic models:

```python
from pydantic import BaseModel, Field, validator

class UserRequest(BaseModel):
    username: str = Field(..., min_length=3, max_length=50)
    email: str
    
    @validator('email')
    def validate_email(cls, v):
        if '@' not in v:
            raise ValueError('Not a valid email address')
        return v
```

### Performance Optimization

1. Asynchronous processing:
   - FastAPI and FastMCP support asynchronous processing. Use `async/await` to improve performance for I/O-heavy operations.

2. Caching:
   - Cache frequently used data to improve performance.

3. Request limiting:
   - Set request limits to prevent service overload.

```python
from fastapi import Depends
from fastapi.middleware.throttling import ThrottlingMiddleware

# Add request limiting middleware
mcp.add_middleware(
    ThrottlingMiddleware,
    rate_limit=100,  # Maximum requests per minute
    time_window=60   # Time window (seconds)
)
```
