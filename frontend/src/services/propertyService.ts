import api from './api';
import { PropertyCollection, Property, CompsAnalysis } from '../types/property';
import { PropertyFilters, BoundingBox, InvestmentAssumptions } from '../types/filters';

export const propertyService = {
  /**
   * Get properties in bounding box with optional filters and investment assumptions.
   * Only returns properties from the daily city-based sweep - no on-demand syncing.
   */
  async getPropertiesInViewport(
    bbox: BoundingBox,
    filters?: PropertyFilters,
    assumptions?: InvestmentAssumptions
  ): Promise<PropertyCollection> {
    // Filter out undefined/null values from assumptions to prevent URL param pollution
    const cleanedAssumptions = assumptions ? 
      Object.fromEntries(
        Object.entries(assumptions).filter(([_, value]) => value !== undefined && value !== null)
      ) : {};
    
    const params = {
      ...bbox,
      ...filters,
      ...cleanedAssumptions,
    };

    const response = await api.get<PropertyCollection>('/api/v1/properties', { params });
    return response.data;
  },

  /**
   * Look up the bounding box for a US ZIP code using Mapbox geocoding.
   * Returns null if the ZIP cannot be resolved.
   */
  async getZipBbox(zipCode: string): Promise<BoundingBox | null> {
    const token = process.env.REACT_APP_MAPBOX_TOKEN;
    if (!token) return null;
    try {
      const resp = await fetch(
        `https://api.mapbox.com/geocoding/v5/mapbox.places/${encodeURIComponent(zipCode)}.json?types=postcode&country=US&access_token=${token}&limit=1`
      );
      const data = await resp.json();
      const feature = data.features?.[0];
      if (!feature) return null;
      if (feature.bbox) {
        const [min_lon, min_lat, max_lon, max_lat] = feature.bbox;
        return { min_lon, min_lat, max_lon, max_lat };
      }
      // Fallback: use centre point ± ~0.1°
      const [lon, lat] = feature.center;
      return { min_lon: lon - 0.15, min_lat: lat - 0.15, max_lon: lon + 0.15, max_lat: lat + 0.15 };
    } catch {
      return null;
    }
  },

  /**
   * Get single property details
   */
  async getPropertyById(id: number): Promise<Property> {
    const response = await api.get<Property>(`/api/v1/properties/${id}`);
    return response.data;
  },

  /**
   * Get comparable sales for a property
   */
  async getPropertyComps(id: number): Promise<CompsAnalysis> {
    const response = await api.get<CompsAnalysis>(`/api/v1/analytics/comps/${id}`);
    return response.data;
  },

  /**
   * Calculate metrics with custom assumptions
   */
  async calculateMetrics(
    propertyId: number,
    assumptions?: any
  ): Promise<any> {
    const params = { property_id: propertyId };
    // Filter out undefined/null values from assumptions
    const cleanedAssumptions = assumptions ? 
      Object.fromEntries(
        Object.entries(assumptions).filter(([_, value]) => value !== undefined && value !== null)
      ) : {};
    const response = await api.post('/api/v1/properties/calculate', cleanedAssumptions, { params });
    return response.data;
  },
};

export default propertyService;
