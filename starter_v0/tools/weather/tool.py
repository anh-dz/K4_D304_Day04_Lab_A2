from typing import Any

def get_weather(location: str) -> dict[str, Any]:
    """Get the current weather for a given location."""
    # Mock data for demonstration purposes
    return {
        "tool": "get_weather",
        "location": location,
        "temperature": "25°C",
        "condition": "Sunny",
        "humidity": "60%",
        "forecast": "Clear skies throughout the day."
    }
