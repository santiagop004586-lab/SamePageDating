"""
Geocoding service - convert addresses to coordinates
"""
import logging
from typing import Optional, Tuple, List
import httpx
from app.core.config import settings

logger = logging.getLogger(__name__)


def get_zip_codes_for_viewport(min_lat: float, max_lat: float, min_lon: float, max_lon: float) -> List[str]:
    """
    Sample the viewport with a small grid of points and reverse-geocode each to
    get the ZIP/postal codes that fall within it.  Used to discover new areas that
    have no property data in the DB yet.

    Returns a deduplicated list of US ZIP codes (may be empty if Mapbox token is
    not configured or all calls fail).
    """
    if not settings.MAPBOX_TOKEN:
        return []

    # Sample up to 9 points (3x3 grid) across the viewport
    lat_steps = [min_lat + (max_lat - min_lat) * i / 2 for i in range(3)]
    lon_steps = [min_lon + (max_lon - min_lon) * i / 2 for i in range(3)]
    sample_points = [(lat, lon) for lat in lat_steps for lon in lon_steps]

    zip_codes: set = set()
    try:
        with httpx.Client(timeout=5.0) as client:
            for lat, lon in sample_points:
                try:
                    url = f"https://api.mapbox.com/geocoding/v5/mapbox.places/{lon},{lat}.json"
                    resp = client.get(url, params={
                        "types": "postcode",
                        "country": "US",
                        "access_token": settings.MAPBOX_TOKEN,
                        "limit": 1,
                    })
                    resp.raise_for_status()
                    features = resp.json().get("features", [])
                    if features:
                        zip_codes.add(features[0]["text"])
                except Exception:
                    pass  # skip failed point
    except Exception as e:
        logger.warning(f"Mapbox geocoding session error: {e}")

    return list(zip_codes)



def geocode_address(address: str) -> Optional[Tuple[float, float]]:
    """
    Geocode an address to latitude/longitude using Mapbox Geocoding API.
    
    Args:
        address: Full address string
    
    Returns:
        Tuple of (latitude, longitude) or None if geocoding fails
    """
    if not settings.MAPBOX_TOKEN:
        logger.warning(f"Mapbox token not configured, cannot geocode: {address}")
        return None
    
    if not address or not address.strip():
        logger.warning("Empty address provided to geocode_address")
        return None
    
    # URL-encode the address
    from urllib.parse import quote
    encoded_address = quote(address)
    
    url = f"https://api.mapbox.com/geocoding/v5/mapbox.places/{encoded_address}.json"
    params = {
        "access_token": settings.MAPBOX_TOKEN,
        "limit": 1,
        "country": "US"  # Restrict to US addresses for Cleveland focus
    }
    
    try:
        with httpx.Client(timeout=10.0) as client:
            response = client.get(url, params=params)
            response.raise_for_status()
            
            data = response.json()
            
            if data.get('features') and len(data['features']) > 0:
                feature = data['features'][0]
                longitude, latitude = feature['geometry']['coordinates']
                logger.info(f"Geocoded '{address}' to ({latitude}, {longitude})")
                return latitude, longitude
            else:
                logger.warning(f"No geocoding results found for: {address}")
                return None
                
    except httpx.HTTPStatusError as e:
        logger.error(f"Mapbox geocoding HTTP error for '{address}': {e.response.status_code}")
        return None
    except httpx.RequestError as e:
        logger.error(f"Mapbox geocoding request error for '{address}': {e}")
        return None
    except Exception as e:
        logger.error(f"Unexpected geocoding error for '{address}': {e}")
        return None
