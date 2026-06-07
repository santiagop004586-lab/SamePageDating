export interface PropertyFilters {
  price_min?: number;
  price_max?: number;
  bedrooms_min?: number;
  bedrooms_max?: number;
  baths_min?: number;
  sqft_min?: number;
  sqft_max?: number;
  year_built_min?: number;
  year_built_max?: number;
  cash_flow_min?: number;
  cap_rate_min?: number;
  coc_return_min?: number;
  roi_min?: number;
  status?: string[];
  property_type?: string[];
}

export interface InvestmentAssumptions {
  down_payment_pct?: number;
  down_payment_fixed?: number;
  interest_rate?: number;
  loan_term_years?: number;
  closing_costs_pct?: number;
  closing_costs_fixed?: number;
  closing_costs_mode?: 'pct' | 'fixed';
  escrow_pct?: number;
  escrow_fixed?: number;
  property_tax_rate?: number;
  property_tax_fixed?: number;
  insurance_pct?: number;
  insurance_fixed?: number;
  maintenance_pct?: number;
  maintenance_fixed?: number;
  property_mgmt_pct?: number;
  property_mgmt_fixed?: number;
  vacancy_rate?: number;
  vacancy_fixed?: number;
  capex_reserve_pct?: number;
  reserves_amount?: number;
  pmi_rate?: number;
  rehab_cost?: number;
  arv_override?: number;
  purchase_price_override?: number;
}

export interface BoundingBox {
  min_lat: number;
  max_lat: number;
  min_lon: number;
  max_lon: number;
}
