import math
from datetime import datetime, timezone

def calculate_haversine_distance(lat1: float, lon1: float, lat2: float, lon2: float) -> float:
    """
    Calculate the great circle distance between two points on Earth in kilometers.
    """
    if not (lat1 and lon1 and lat2 and lon2):
        return 0.0

    R = 6371.0 # Earth's radius in kilometers

    dlat = math.radians(lat2 - lat1)
    dlon = math.radians(lon2 - lon1)
    a = (math.sin(dlat / 2) ** 2 +
         math.cos(math.radians(lat1)) * math.cos(math.radians(lat2)) * math.sin(dlon / 2) ** 2)
    c = 2 * math.atan2(math.sqrt(a), math.sqrt(1 - a))
    distance = R * c
    return round(distance, 1)


def humanize_time_ago(dt: datetime) -> str:
    """
    Converts a datetime into a human-readable 'time ago' string.
    Explicitly satisfies requirement for: 'Last updated: 10 minutes ago' etc.
    """
    if not dt:
        return "Unknown"

    now = datetime.utcnow()
    diff = now - dt

    seconds = int(diff.total_seconds())
    if seconds < 0:
        return "Just now"

    if seconds < 60:
        return "Just now"
    elif seconds < 3600:
        mins = seconds // 60
        return f"{mins} minute{'s' if mins > 1 else ''} ago"
    elif seconds < 86400:
        hours = seconds // 3600
        return f"{hours} hour{'s' if hours > 1 else ''} ago"
    elif seconds < 604800:
        days = seconds // 86400
        return f"{days} day{'s' if days > 1 else ''} ago"
    else:
        return dt.strftime('%b %d, %Y at %I:%M %p')


def sanitize_search_query(query: str) -> str:
    """Strip dangerous characters and trim spaces from search input."""
    if not query:
        return ""
    return "".join(c for c in query if c.isalnum() or c in " -_./%").strip()
