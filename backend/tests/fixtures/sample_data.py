"""Sample test data fixtures for testing."""

SAMPLE_LOCAL_GUIDES = [
    {
        "city": "Tokyo",
        "interests": ["food", "culture"],
        "description": "Visit Tsukiji Outer Market for fresh sushi breakfast, then explore Senso-ji Temple in Asakusa for traditional culture.",
        "source": "https://example.com/tokyo-guide"
    },
    {
        "city": "Tokyo",
        "interests": ["art", "architecture"],
        "description": "Explore the Mori Art Museum in Roppongi Hills, featuring contemporary Japanese art and stunning city views.",
        "source": "https://example.com/tokyo-art"
    },
    {
        "city": "Paris",
        "interests": ["food", "history"],
        "description": "Take a food tour through Le Marais, sampling traditional French pastries and visiting historic sites.",
        "source": "https://example.com/paris-food"
    },
    {
        "city": "Paris",
        "interests": ["art"],
        "description": "Visit the Musée d'Orsay to see Impressionist masterpieces in a converted railway station.",
        "source": "https://example.com/paris-art"
    },
    {
        "city": "New York",
        "interests": ["food", "culture"],
        "description": "Explore diverse neighborhoods like Chinatown and Little Italy, sampling authentic cuisine from around the world.",
        "source": "https://example.com/nyc-food"
    }
]

SAMPLE_TRIP_REQUEST = {
    "destination": "Tokyo, Japan",
    "duration": "7 days",
    "budget": "$2000",
    "interests": "food, culture",
    "travel_style": "standard"
}

