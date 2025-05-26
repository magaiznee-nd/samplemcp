from fastmcp import FastMCP
import uvicorn
from pydantic import BaseModel, Field
import logging
from typing import List, Optional, Dict, Any
import httpx
import os
import json

# Logging configuration
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)

logger = logging.getLogger("weather_mcp_service")

# Create FastMCP object
mcp = FastMCP(title="Weather Information MCP Service", description="Example MCP service providing weather information")

# Get default API key from environment variables (for development, in production keys are received in API calls)
DEFAULT_WEATHER_API_KEY = os.environ.get("WEATHER_API_KEY", "demo_api_key")

# Input model definitions
class WeatherRequest(BaseModel):
    city: str = Field(..., description="City name to check the weather for")
    country_code: Optional[str] = Field(None, description="Country code (e.g., 'US', 'UK')")
    days: int = Field(3, description="Number of days for the forecast", ge=1, le=7)
    api_key: Optional[str] = Field(None, description="Weather API key (uses default if not provided)")

class ForecastDay(BaseModel):
    date: str = Field(..., description="Forecast date (YYYY-MM-DD)")
    min_temp: float = Field(..., description="Minimum temperature (Celsius)")
    max_temp: float = Field(..., description="Maximum temperature (Celsius)")
    condition: str = Field(..., description="Weather condition")
    
class WeatherResponse(BaseModel):
    city: str = Field(..., description="City name")
    country: str = Field(..., description="Country")
    current_temp: float = Field(..., description="Current temperature (Celsius)")
    current_condition: str = Field(..., description="Current weather condition")
    forecast: List[ForecastDay] = Field(..., description="Daily forecast list")

class AirQualityRequest(BaseModel):
    city: str = Field(..., description="City name to check air quality for")
    country_code: Optional[str] = Field(None, description="Country code (e.g., 'US', 'UK')")
    api_key: Optional[str] = Field(None, description="Air quality API key (uses default if not provided)")

@mcp.tool()
async def health():
    """Service status check"""
    return {"status": "ok"}

@mcp.tool()
async def get_weather(request: WeatherRequest) -> Dict[str, Any]:
    """Provides current weather and forecast for a specific city.
    
    Args:
        request: Weather request information
        
    Returns:
        Current weather and forecast information
    """
    logger.info(f"Weather request for city: {request.city}, days: {request.days}")
    
    try:
        # Set API key (use key provided in request or default value)
        api_key = request.api_key or DEFAULT_WEATHER_API_KEY
        
        # In a real implementation, call an actual weather API
        # Here we return demo data
        
        # Example of actual API call (commented out)
        """
        async with httpx.AsyncClient() as client:
            response = await client.get(
                "https://api.weatherapi.com/v1/forecast.json",
                params={
                    "key": api_key,
                    "q": request.city,
                    "days": request.days,
                    "aqi": "no"
                }
            )
            
            if response.status_code != 200:
                logger.error(f"Weather API error: {response.text}")
                return {"error": "Weather service error", "details": response.text}
                
            weather_data = response.json()
            # Process data...
        """
        
        # Demo data
        forecast_days = []
        for i in range(request.days):
            forecast_days.append({
                "date": f"2025-05-{27+i}",
                "min_temp": 18 + i * 0.5,
                "max_temp": 25 + i * 0.7,
                "condition": "Sunny" if i % 2 == 0 else "Cloudy"
            })
        
        result = {
            "city": request.city,
            "country": request.country_code or "US",
            "current_temp": 23.5,
            "current_condition": "Sunny",
            "forecast": forecast_days
        }
        
        logger.info(f"Weather data retrieved successfully for {request.city}")
        return result
            
    except Exception as e:
        logger.exception("Error retrieving weather data")
        return {"error": str(e)}

@mcp.tool()
async def get_air_quality(request: AirQualityRequest) -> Dict[str, Any]:
    """Provides air quality information for a specific city.
    
    Args:
        request: Air quality request information
        
    Returns:
        Air quality information
    """
    logger.info(f"Air quality request for city: {request.city}")
    
    try:
        # Set API key (use key provided in request or default value)
        api_key = request.api_key or DEFAULT_WEATHER_API_KEY
        
        # Demo data
        result = {
            "city": request.city,
            "country": request.country_code or "US",
            "aqi": 45,
            "quality_level": "Good",
            "pollutants": {
                "pm2_5": 12.5,
                "pm10": 25.3,
                "o3": 68.2,
                "no2": 15.7,
                "so2": 5.2,
                "co": 0.8
            },
            "health_recommendations": "Air quality is good. Suitable for outdoor activities."
        }
        
        logger.info(f"Air quality data retrieved successfully for {request.city}")
        return result
            
    except Exception as e:
        logger.exception("Error retrieving air quality data")
        return {"error": str(e)}

# Tool definition JSON generation function
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
        },
        {
            "name": "get_air_quality",
            "description": "Provides air quality information for a specific city.",
            "parameters": {
                "type": "object",
                "properties": {
                    "city": {
                        "type": "string",
                        "description": "City name to check air quality for"
                    },
                    "country_code": {
                        "type": "string",
                        "description": "Country code (e.g., 'US', 'UK')"
                    },
                    "api_key": {
                        "type": "string",
                        "description": "Air quality API key (uses default if not provided)"
                    }
                },
                "required": ["city"]
            }
        }
    ]
    
    return tools

@mcp.tool()
async def get_tool_definitions():
    """Provides MCP tool definitions in JSON format."""
    return {"tools": generate_tool_definitions()}

# For direct server execution
if __name__ == "__main__":
    # Generate tool definition JSON file
    with open("tool_definitions.json", "w", encoding="utf-8") as f:
        json.dump({"tools": generate_tool_definitions()}, f, ensure_ascii=False, indent=2)
    print("Tool definition JSON file has been generated: tool_definitions.json")
    
    uvicorn.run(mcp, host="0.0.0.0", port=8000)
