/**
 * Client-side investment metrics calculator
 * Mirrors backend logic for instant recalculation when assumptions change
 */

import { InvestmentAssumptions } from '../types/filters';
import { Property } from '../types/property';

interface MetricsResult {
  monthly_mortgage: number;
  monthly_cash_flow: number;
  cap_rate: number;
  cash_on_cash_return: number;
  annual_noi: number;
  effective_rent: number;
  breakeven_years: number | null;
  expense_breakdown: {
    property_tax: number;
    insurance: number;
    maintenance: number;
    property_mgmt: number;
    capex_reserve: number;
    vacancy: number;
    pmi: number;
    operating_expenses: number;
    total: number;
  };
}

export class MetricsCalculator {
  private assumptions: InvestmentAssumptions;

  constructor(assumptions: InvestmentAssumptions) {
    this.assumptions = {
      down_payment_pct: assumptions.down_payment_pct ?? 0.20,
      down_payment_fixed: assumptions.down_payment_fixed,
      interest_rate: assumptions.interest_rate ?? 0.07,
      loan_term_years: assumptions.loan_term_years ?? 30,
      closing_costs_pct: assumptions.closing_costs_pct ?? 0.035,
      closing_costs_fixed: assumptions.closing_costs_fixed,
      escrow_pct: assumptions.escrow_pct ?? 0.03,
      escrow_fixed: assumptions.escrow_fixed,
      property_tax_rate: assumptions.property_tax_rate ?? 0.011,
      property_tax_fixed: assumptions.property_tax_fixed,
      insurance_pct: assumptions.insurance_pct ?? 0.01,
      insurance_fixed: assumptions.insurance_fixed,
      maintenance_pct: assumptions.maintenance_pct ?? 0.013,
      maintenance_fixed: assumptions.maintenance_fixed,
      property_mgmt_pct: assumptions.property_mgmt_pct ?? 0.10,
      property_mgmt_fixed: assumptions.property_mgmt_fixed,
      vacancy_rate: assumptions.vacancy_rate ?? 0.08,
      vacancy_fixed: assumptions.vacancy_fixed,
      capex_reserve_pct: assumptions.capex_reserve_pct ?? 0.10,
      pmi_rate: assumptions.pmi_rate ?? 0.0,
      reserves_amount: assumptions.reserves_amount ?? 5000,
    };
  }

  /**
   * Calculate monthly mortgage payment using standard amortization formula
   */
  calculateMonthlyMortgage(purchasePrice: number): number {
    const downPayment = this.assumptions.down_payment_fixed !== undefined
      ? this.assumptions.down_payment_fixed
      : purchasePrice * (this.assumptions.down_payment_pct ?? 0.20);
    
    const loanAmount = purchasePrice - downPayment;
    const monthlyRate = (this.assumptions.interest_rate ?? 0.07) / 12;
    const numPayments = (this.assumptions.loan_term_years ?? 30) * 12;

    if (monthlyRate === 0) {
      return loanAmount / numPayments;
    }

    const mortgage = loanAmount * (
      monthlyRate * Math.pow(1 + monthlyRate, numPayments)
    ) / (
      Math.pow(1 + monthlyRate, numPayments) - 1
    );

    return Math.round(mortgage * 100) / 100;
  }

  /**
   * Calculate monthly expenses breakdown
   */
  calculateMonthlyExpenses(propertyValue: number, grossRent: number) {
    // Property taxes
    const propertyTax = this.assumptions.property_tax_fixed !== undefined
      ? this.assumptions.property_tax_fixed
      : (propertyValue * (this.assumptions.property_tax_rate ?? 0.011)) / 12;

    // Insurance
    const insurance = this.assumptions.insurance_fixed !== undefined
      ? this.assumptions.insurance_fixed
      : (propertyValue * (this.assumptions.insurance_pct ?? 0.01)) / 12;

    // Maintenance (based on RENT, not property value)
    const maintenance = this.assumptions.maintenance_fixed !== undefined
      ? this.assumptions.maintenance_fixed
      : grossRent * (this.assumptions.maintenance_pct ?? 0.013);

    // Property management (based on rent)
    const propertyMgmt = this.assumptions.property_mgmt_fixed !== undefined
      ? this.assumptions.property_mgmt_fixed
      : grossRent * (this.assumptions.property_mgmt_pct ?? 0.10);

    // CapEx reserve (based on rent)
    const capexReserve = grossRent * (this.assumptions.capex_reserve_pct ?? 0.10);

    // Vacancy loss (based on rent)
    const vacancy = this.assumptions.vacancy_fixed !== undefined
      ? this.assumptions.vacancy_fixed
      : grossRent * (this.assumptions.vacancy_rate ?? 0.08);

    // PMI (based on loan amount)
    const pmiRate = this.assumptions.pmi_rate ?? 0.0;
    const downPayment = this.assumptions.down_payment_fixed !== undefined
      ? this.assumptions.down_payment_fixed
      : propertyValue * (this.assumptions.down_payment_pct ?? 0.20);
    const loanAmount = propertyValue - downPayment;
    const pmi = (loanAmount * pmiRate) / 12;

    // Operating expenses (for NOI) = Taxes + HOI + Maintenance + Management
    const operatingExpenses = propertyTax + insurance + maintenance + propertyMgmt;

    // Total expenses (includes vacancy and capex)
    const total = propertyTax + insurance + maintenance + propertyMgmt + capexReserve + vacancy + pmi;

    return {
      property_tax: Math.round(propertyTax * 100) / 100,
      insurance: Math.round(insurance * 100) / 100,
      maintenance: Math.round(maintenance * 100) / 100,
      property_mgmt: Math.round(propertyMgmt * 100) / 100,
      capex_reserve: Math.round(capexReserve * 100) / 100,
      vacancy: Math.round(vacancy * 100) / 100,
      pmi: Math.round(pmi * 100) / 100,
      operating_expenses: Math.round(operatingExpenses * 100) / 100,
      total: Math.round(total * 100) / 100,
    };
  }

  /**
   * Calculate all metrics for a property
   */
  calculateMetrics(property: Property): MetricsResult {
    const purchasePrice = property.purchase_price ?? property.list_price ?? 0;
    const renovations = property.renovations || 0;
    const totalInvestment = purchasePrice + renovations;  // Total investment = purchase price + renovations
    const arv = property.arv || totalInvestment;
    const grossRent = property.section8_rent || 0;
    const vacancyRate = this.assumptions.vacancy_rate ?? 0.08;

    // Calculate components
    const mortgage = this.calculateMonthlyMortgage(totalInvestment);
    const expenses = this.calculateMonthlyExpenses(arv, grossRent);

    // Effective rent = Gross Rent × (1 - Vacancy%)
    const effectiveRent = grossRent * (1 - vacancyRate);

    // Cash flow = Effective Rent - Operating Expenses - CapEx - PMI - Mortgage
    // Note: Vacancy is already accounted for in effectiveRent, so we don't subtract it again
    const cashFlow = effectiveRent - expenses.operating_expenses - expenses.capex_reserve - expenses.pmi - mortgage;

    // Annual calculations
    const annualEffectiveRent = effectiveRent * 12;
    const annualOperatingExpenses = expenses.operating_expenses * 12;
    const annualNOI = annualEffectiveRent - annualOperatingExpenses;
    const annualCashFlow = cashFlow * 12;

    // Cap rate = NOI / Total Investment
    const capRate = totalInvestment > 0 ? (annualNOI / totalInvestment) * 100 : 0;

    // Total cash invested
    const downPayment = this.assumptions.down_payment_fixed !== undefined
      ? this.assumptions.down_payment_fixed
      : totalInvestment * (this.assumptions.down_payment_pct ?? 0.20);
    
    const closingCosts = this.assumptions.closing_costs_fixed !== undefined
      ? this.assumptions.closing_costs_fixed
      : totalInvestment * (this.assumptions.closing_costs_pct ?? 0.035);
    
    const escrow = this.assumptions.escrow_fixed !== undefined
      ? this.assumptions.escrow_fixed
      : totalInvestment * (this.assumptions.escrow_pct ?? 0.03);
    
    const rehabCost = property.estimated_rehab || 0;
    const reserves = this.assumptions.reserves_amount ?? 5000;
    const totalCashInvested = downPayment + closingCosts + escrow + rehabCost + reserves;

    // Cash-on-cash return
    const cashOnCash = totalCashInvested > 0 ? (annualCashFlow / totalCashInvested) * 100 : 0;

    // Breakeven years (payback period) = 100 / cash_on_cash_return
    // This represents how many years until cumulative cash flow returns the initial investment
    const breakevenYears = cashOnCash > 0 ? 100 / cashOnCash : null;

    return {
      monthly_mortgage: Math.round(mortgage * 100) / 100,
      monthly_cash_flow: Math.round(cashFlow * 100) / 100,
      cap_rate: Math.round(capRate * 100) / 100,
      cash_on_cash_return: Math.round(cashOnCash * 100) / 100,
      annual_noi: Math.round(annualNOI * 100) / 100,
      effective_rent: Math.round(effectiveRent * 100) / 100,
      breakeven_years: breakevenYears !== null ? Math.round(breakevenYears * 10) / 10 : null,
      expense_breakdown: expenses,
    };
  }

  /**
   * Recalculate metrics for multiple properties
   */
  recalculateProperties(properties: Property[]): Property[] {
    console.log('[MetricsCalculator] recalculateProperties called with', properties.length, 'properties');
    console.log('[MetricsCalculator] Using assumptions:', {
      down_payment_pct: this.assumptions.down_payment_pct,
      down_payment_fixed: this.assumptions.down_payment_fixed,
      interest_rate: this.assumptions.interest_rate
    });
    
    const result = properties.map((prop, index) => {
      const metrics = this.calculateMetrics(prop);
      if (index === 0) {
        console.log('[MetricsCalculator] First property metrics:', {
          propertyId: prop.id,
          purchasePrice: prop.list_price,
          cash_flow: metrics.monthly_cash_flow,
          cash_on_cash: metrics.cash_on_cash_return,
          mortgage: metrics.monthly_mortgage
        });
      }
      return {
        ...prop,
        monthly_mortgage: metrics.monthly_mortgage,
        monthly_cash_flow: metrics.monthly_cash_flow,
        cap_rate: metrics.cap_rate,
        cash_on_cash_return: metrics.cash_on_cash_return,
        noi: metrics.annual_noi,  // Annual NOI for cap rate calculation
        breakeven_years: metrics.breakeven_years ?? undefined,
        expense_breakdown: metrics.expense_breakdown,
      };
    });
    
    return result;
  }
}

/**
 * Debounce function to limit API calls
 */
export function debounce<T extends (...args: any[]) => any>(
  func: T,
  wait: number
): (...args: Parameters<T>) => void {
  let timeout: NodeJS.Timeout | null = null;
  
  return function executedFunction(...args: Parameters<T>) {
    const later = () => {
      timeout = null;
      func(...args);
    };
    
    if (timeout) {
      clearTimeout(timeout);
    }
    timeout = setTimeout(later, wait);
  };
}
