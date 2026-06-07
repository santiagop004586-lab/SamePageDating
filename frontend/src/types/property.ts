export interface UnitDetail {
  unit: number;
  bedrooms: number;
  bathrooms: number;
  rent?: number;
}

export interface PropertyEstimate {
  estimate?: number;
  value?: number;
  price?: number;
  source?: string | { name?: string; type?: string; __typename?: string };
  date?: string;
  estimate_high?: number;
  estimate_low?: number;
}

export interface HistoricalEstimateGroup {
  source: { name?: string; type?: string; __typename?: string };
  estimates: Array<{
    date: string;
    estimate: number;
    __typename?: string;
  }>;
  __typename?: string;
}

export interface PropertyEstimates {
  current_values?: PropertyEstimate[];
  historical_values?: HistoricalEstimateGroup[];
  forecast_values?: HistoricalEstimateGroup[];
}

export interface ExpenseBreakdown {
  property_tax: number;
  insurance: number;
  maintenance: number;
  property_mgmt: number;
  capex_reserve: number;
  vacancy: number;
  pmi?: number;
  total?: number;
}

export interface BRRRRMetrics {
  // Step 1: BUY
  purchase_price: number;
  down_payment_pct: number;
  original_loan: number;
  
  // Step 2: REHAB
  rehab_cost: number;
  total_investment: number;
  
  // Step 3: ARV
  arv: number;
  potential_equity: number;
  
  // Step 4: REFINANCE
  refinance_ltv: number;
  refinance_loan_amount: number;
  gross_refi_proceeds?: number;
  refi_closing_costs?: number;
  cash_pulled_out: number;
  
  // Step 5: POST REFINANCE
  equity_remaining: number;
  cash_left_in_deal: number;
  
  // Step 6: RETURNS
  refinance_monthly_payment?: number;
  actual_cash_invested?: number;
  monthly_cash_flow: number;
  annual_cash_flow: number;
  cash_on_cash_after_refinance: number;
  
  // Validation
  has_warnings?: boolean;
  warnings?: string[];
}

export interface AppreciationMetrics {
  appreciation_rate: number;
  appreciation_rate_source?: 'user' | 'zip' | 'metro' | 'zhvf' | 'zhvi_cagr';
  zip_code?: string;
  current_value: number;
  value_1yr: number;
  value_5yr: number;
  value_10yr: number;
  equity_gain_1yr: number;
  equity_gain_5yr: number;
  equity_gain_10yr: number;
  total_return_5yr: number;
  total_return_10yr: number;
}

export interface Property {
  id: number;
  external_id?: string;
  address: string;
  city?: string;
  state?: string;
  zip_code?: string;
  latitude?: number;
  longitude?: number;
  bedrooms?: number;
  bathrooms?: number;
  sqft?: number;
  year_built?: number;
  property_type?: string;
  list_price?: number;
  purchase_price?: number;  // User-adjusted purchase/offer price (defaults to list_price)
  renovations?: number;  // User-estimated renovation costs (defaults to 0)
  photo_url?: string;
  photos?: string[];
  unit_details?: UnitDetail[];
  arv?: number;
  estimated_rehab?: number;
  market_rent?: number;
  section8_rent?: number;
  property_tax_rate?: number;
  estimates?: PropertyEstimates;
  total_project_cost?: number;
  monthly_cash_flow?: number;
  monthly_mortgage?: number;
  expense_breakdown?: ExpenseBreakdown;
  brrrr?: BRRRRMetrics;
  appreciation?: AppreciationMetrics;
  cap_rate?: number;
  cash_on_cash_return?: number;
  deal_spread?: number;
  break_even_price?: number;
  median_estimate?: number;
  roi?: number;
  breakeven_years?: number;
  noi?: number;
}

export interface PropertyFeature {
  type: 'Feature';
  id: string;
  geometry: {
    type: 'Point';
    coordinates: [number, number]; // [longitude, latitude]
  };
  properties: {
    id: number;
    address: string;
    city?: string;
    state?: string;
    zip_code?: string;
    price?: number;
    list_price?: number;
    status?: string;
    bedrooms?: number;
    bathrooms?: number;
    sqft?: number;
    year_built?: number;
    property_type?: string;
    photo_url?: string;
    photos?: string[];
    unit_details?: UnitDetail[];
    arv?: number;
    estimated_rehab?: number;
    market_rent?: number;
    section8_rent?: number;
    property_tax_rate?: number;
    estimates?: PropertyEstimates;
    total_project_cost?: number;
    monthly_cash_flow?: number;
    monthly_mortgage?: number;
    expense_breakdown?: ExpenseBreakdown;
    brrrr?: BRRRRMetrics;
    appreciation?: AppreciationMetrics;
    cap_rate?: number;
    cash_on_cash_return?: number;
    deal_spread?: number;
    break_even_price?: number;
    median_estimate?: number;
    roi?: number;
    breakeven_years?: number;
    noi?: number;
    marker_color: string;
  };
}

export interface PropertyCollection {
  type: 'FeatureCollection';
  features: PropertyFeature[];
  total_count: number;
  latest_property_update?: string;  // ISO timestamp of most recent property update
  last_sync_run?: string;  // ISO timestamp of when ETL job last synced from RapidAPI
}

export interface ComparableSale {
  id: number;
  address: string;
  bedrooms?: number;
  bathrooms?: number;
  sqft?: number;
  sale_price?: number;
  sale_date?: string;
  distance_miles?: number;
  adjusted_value?: number;
  adjustment_amount?: number;
}

export interface CompsAnalysis {
  property_id: number;
  property_address: string;
  comps: ComparableSale[];
  estimated_arv?: number;
}
