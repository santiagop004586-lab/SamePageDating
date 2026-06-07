/**
 * Format number as currency
 */
export const formatCurrency = (value: number | undefined | null): string => {
  if (value === undefined || value === null) return 'N/A';
  
  return new Intl.NumberFormat('en-US', {
    style: 'currency',
    currency: 'USD',
    minimumFractionDigits: 0,
    maximumFractionDigits: 0,
  }).format(value);
};

/**
 * Format number as percentage
 */
export const formatPercent = (value: number | undefined | null): string => {
  if (value === undefined || value === null) return 'N/A';
  
  return `${value.toFixed(2)}%`;
};

/**
 * Format number with commas
 */
export const formatNumber = (value: number | undefined | null): string => {
  if (value === undefined || value === null) return 'N/A';
  
  return new Intl.NumberFormat('en-US').format(value);
};

/**
 * Format address for display
 */
export const formatAddress = (
  address: string,
  city?: string,
  state?: string,
  zip?: string
): string => {
  let formatted = address;
  
  if (city) formatted += `, ${city}`;
  if (state) formatted += `, ${state}`;
  if (zip) formatted += ` ${zip}`;
  
  return formatted;
};
