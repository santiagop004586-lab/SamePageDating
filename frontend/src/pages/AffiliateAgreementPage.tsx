import React from 'react';
import { Link } from 'react-router-dom';

export default function AffiliateAgreementPage() {
  return (
    <div className="min-h-screen bg-gray-50 py-12 px-4 sm:px-6 lg:px-8">
      <div className="max-w-4xl mx-auto bg-white shadow-sm rounded-lg p-8">
        <h1 className="text-3xl font-bold text-gray-900 mb-2">Affiliate Program Agreement</h1>
        <p className="text-sm text-gray-500 mb-8">Last Updated: March 22, 2026</p>

        <div className="prose prose-blue max-w-none space-y-6">
          <section>
            <h2 className="text-2xl font-semibold text-gray-900 mt-8 mb-4">1. Agreement to Terms</h2>
            <p className="text-gray-700 leading-relaxed">
              This Affiliate Program Agreement ("Agreement") is entered into between you ("Affiliate") and SamePageDating ("Company"). 
              By enrolling in the SamePageDating Affiliate Program, you agree to be bound by this Agreement and our{' '}
              <Link to="/terms-of-service" className="text-blue-600 hover:underline">Terms of Service</Link>.
            </p>
          </section>

          <section>
            <h2 className="text-2xl font-semibold text-gray-900 mt-8 mb-4">2. Program Overview</h2>
            <p className="text-gray-700 leading-relaxed">
              The SamePageDating Affiliate Program allows you to earn recurring commissions by referring new subscribers to our Service. 
              You will receive a unique referral link and code to share with potential customers.
            </p>
            
            <h3 className="text-xl font-semibold text-gray-800 mt-6 mb-3">2.1 Commission Structure</h3>
            <ul className="list-disc pl-6 text-gray-700 space-y-2">
              <li><strong>Commission Rate:</strong> 30% of the monthly subscription fee ($19.99 × 30% = $5.997 per month)</li>
              <li><strong>Commission Type:</strong> Recurring — You earn commission every month the referred user remains subscribed</li>
              <li><strong>Maximum Duration:</strong> Unlimited (as long as the user remains an active subscriber)</li>
              <li><strong>Cookie Duration:</strong> 30 days — Users who click your link have 30 days to sign up and be attributed to you</li>
            </ul>

            <h3 className="text-xl font-semibold text-gray-800 mt-6 mb-3">2.2 Example Commission Calculation</h3>
            <div className="bg-blue-50 border border-blue-200 rounded-lg p-4 mt-4">
              <p className="text-gray-700 font-semibold">Example: You refer 10 users who subscribe</p>
              <ul className="list-none mt-2 space-y-1 text-gray-700">
                <li>• Month 1: 10 users × $5.997 = <strong>$59.97</strong></li>
                <li>• Month 2: 9 users remain × $5.997 = <strong>$53.97</strong> (1 canceled)</li>
                <li>• Month 3: 9 users remain × $5.997 = <strong>$53.97</strong></li>
                <li className="pt-2 font-semibold">Total after 3 months: $167.91</li>
              </ul>
            </div>
          </section>

          <section>
            <h2 className="text-2xl font-semibold text-gray-900 mt-8 mb-4">3. Commission Hold Period and Anti-Fraud Protection</h2>
            
            <h3 className="text-xl font-semibold text-gray-800 mt-6 mb-3">3.1 90-Day Hold Period</h3>
            <p className="text-gray-700 leading-relaxed font-semibold">
              All commissions are subject to a 90-day hold period before approval and payout.
            </p>
            <p className="text-gray-700 leading-relaxed mt-4">
              <strong>How It Works:</strong>
            </p>
            <ol className="list-decimal pl-6 text-gray-700 space-y-2 mt-2">
              <li>User signs up via your referral link and subscribes (after 30-day free trial)</li>
              <li>Commission is created with status "pending" — Not yet payable</li>
              <li>90 days pass while the user remains subscribed</li>
              <li>Commission automatically changes to "approved" — Now eligible for payout</li>
              <li>Next monthly payout batch includes the approved commission</li>
            </ol>

            <h3 className="text-xl font-semibold text-gray-800 mt-6 mb-3">3.2 Purpose of Hold Period</h3>
            <p className="text-gray-700 leading-relaxed">
              The 90-day hold period protects against:
            </p>
            <ul className="list-disc pl-6 text-gray-700 space-y-2 mt-2">
              <li>Early cancellations and chargebacks</li>
              <li>Fraudulent referrals and fake signups</li>
              <li>Users who subscribe only to cancel immediately</li>
              <li>Credit card disputes and payment failures</li>
            </ul>

            <h3 className="text-xl font-semibold text-gray-800 mt-6 mb-3">3.3 Fraud Detection and Commission Cancellation</h3>
            <p className="text-gray-700 leading-relaxed">
              We employ automated fraud detection to monitor for suspicious activity:
            </p>
            <ul className="list-disc pl-6 text-gray-700 space-y-2 mt-2">
              <li><strong>IP Address Matching:</strong> Referrals from the same IP as the affiliate are flagged</li>
              <li><strong>Rapid Conversion Detection:</strong> Excessive signups in a short time period</li>
              <li><strong>Velocity Checks:</strong> Abnormally high signup rates</li>
              <li><strong>Churn Pattern Analysis:</strong> Referred users who cancel at unusually high rates</li>
            </ul>
            <p className="text-gray-700 leading-relaxed mt-4 font-semibold">
              Commissions flagged for fraud will be withheld and subject to manual review. We reserve the right to cancel commissions 
              and terminate affiliate accounts for fraudulent activity.
            </p>
          </section>

          <section>
            <h2 className="text-2xl font-semibold text-gray-900 mt-8 mb-4">4. Payout Terms</h2>
            
            <h3 className="text-xl font-semibold text-gray-800 mt-6 mb-3">4.1 Payout Method</h3>
            <p className="text-gray-700 leading-relaxed">
              All payouts are processed through <strong>Stripe Connect</strong>. You must complete Stripe Connect onboarding to receive payments. 
              Stripe handles:
            </p>
            <ul className="list-disc pl-6 text-gray-700 space-y-2 mt-2">
              <li>Direct deposit to your bank account</li>
              <li>Tax compliance (W-9 collection, 1099 form generation)</li>
              <li>Identity verification</li>
              <li>Secure storage of tax and banking information</li>
            </ul>

            <h3 className="text-xl font-semibold text-gray-800 mt-6 mb-3">4.2 Payout Schedule</h3>
            <p className="text-gray-700 leading-relaxed">
              Payouts are processed <strong>monthly on the 1st of each month</strong> at 12:00 PM UTC. Only commissions with status 
              "approved" (past the 90-day hold period) are included in the payout batch.
            </p>

            <h3 className="text-xl font-semibold text-gray-800 mt-6 mb-3">4.3 Minimum Payout Threshold</h3>
            <p className="text-gray-700 leading-relaxed">
              There is currently <strong>no minimum payout threshold</strong>. All approved commissions, regardless of amount, will be paid out monthly.
            </p>

            <h3 className="text-xl font-semibold text-gray-800 mt-6 mb-3">4.4 Payout Timeline</h3>
            <p className="text-gray-700 leading-relaxed">
              Once a payout batch is created:
            </p>
            <ol className="list-decimal pl-6 text-gray-700 space-y-2 mt-2">
              <li>Stripe Transfer is initiated on the 1st of the month</li>
              <li>Funds typically arrive in your bank account within 2-7 business days</li>
              <li>You will receive an email notification when the payout is sent</li>
            </ol>

            <h3 className="text-xl font-semibold text-gray-800 mt-6 mb-3">4.5 Failed Payouts</h3>
            <p className="text-gray-700 leading-relaxed">
              If a payout fails (e.g., invalid bank account, Stripe account issues), you will be notified and must update your 
              information. The payout will be retried in the next monthly cycle.
            </p>
          </section>

          <section>
            <h2 className="text-2xl font-semibold text-gray-900 mt-8 mb-4">5. Tax Compliance</h2>
            
            <h3 className="text-xl font-semibold text-gray-800 mt-6 mb-3">5.1 Tax Reporting</h3>
            <p className="text-gray-700 leading-relaxed">
              You are responsible for reporting all affiliate income to tax authorities. We will issue Form 1099-NEC if you earn $600 or more 
              in a calendar year (for U.S. affiliates).
            </p>

            <h3 className="text-xl font-semibold text-gray-800 mt-6 mb-3">5.2 W-9 Collection (U.S. Affiliates)</h3>
            <p className="text-gray-700 leading-relaxed">
              If you are a U.S. person or entity, you must provide your Tax Identification Number (TIN) or Social Security Number (SSN) 
              to Stripe during onboarding. This information is stored securely by Stripe, not by SamePageDating.
            </p>

            <h3 className="text-xl font-semibold text-gray-800 mt-6 mb-3">5.3 International Affiliates</h3>
            <p className="text-gray-700 leading-relaxed">
              International affiliates may be required to provide additional tax documentation. Stripe will collect the appropriate forms 
              (W-8BEN, etc.) during onboarding.
            </p>

            <h3 className="text-xl font-semibold text-gray-800 mt-6 mb-3">5.4 Tax Withholding</h3>
            <p className="text-gray-700 leading-relaxed">
              We do not withhold taxes from your commissions. You are responsible for paying all applicable taxes. Consult a tax professional 
              for guidance on your tax obligations.
            </p>
          </section>

          <section>
            <h2 className="text-2xl font-semibold text-gray-900 mt-8 mb-4">6. Prohibited Activities</h2>
            <p className="text-gray-700 leading-relaxed font-semibold">
              The following activities are strictly prohibited and will result in immediate termination and forfeiture of all commissions:
            </p>
            <ul className="list-disc pl-6 text-gray-700 space-y-2 mt-4">
              <li><strong>Self-Referrals:</strong> Signing up for the Service using your own referral link</li>
              <li><strong>Fake Accounts:</strong> Creating fake user accounts or using bots</li>
              <li><strong>Credit Card Fraud:</strong> Using stolen or invalid payment methods</li>
              <li><strong>Cookie Stuffing:</strong> Forcing referral cookies onto users' browsers without their knowledge</li>
              <li><strong>Trademark Bidding:</strong> Bidding on "SamePageDating" or related trademarks in paid search ads</li>
              <li><strong>Spam:</strong> Sending unsolicited emails or messages promoting your referral link</li>
              <li><strong>False Advertising:</strong> Making misleading claims about the Service or commission rates</li>
              <li><strong>Incentivized Signups:</strong> Offering cash or rewards in exchange for signups (unless pre-approved)</li>
              <li><strong>IP Address Fraud:</strong> Referring users from your own IP address or related IPs</li>
            </ul>
          </section>

          <section>
            <h2 className="text-2xl font-semibold text-gray-900 mt-8 mb-4">7. Promotional Guidelines</h2>
            
            <h3 className="text-xl font-semibold text-gray-800 mt-6 mb-3">7.1 Approved Promotion Methods</h3>
            <ul className="list-disc pl-6 text-gray-700 space-y-2">
              <li>Social media posts (organic, not spam)</li>
              <li>Blog posts and content marketing</li>
              <li>YouTube or podcast reviews</li>
              <li>Email newsletters to your own subscribers (with opt-in)</li>
              <li>Paid advertising (excluding trademark bidding)</li>
            </ul>

            <h3 className="text-xl font-semibold text-gray-800 mt-6 mb-3">7.2 Required Disclosures</h3>
            <p className="text-gray-700 leading-relaxed">
              You must disclose your affiliate relationship when promoting SamePageDating. Example disclosure:
            </p>
            <div className="bg-gray-100 border border-gray-300 rounded p-4 mt-2">
              <p className="text-sm text-gray-700 italic">
                "This post contains affiliate links. If you sign up through my link, I may earn a commission at no additional cost to you."
              </p>
            </div>
            <p className="text-gray-700 leading-relaxed mt-4">
              This complies with FTC guidelines on affiliate marketing disclosure.
            </p>

            <h3 className="text-xl font-semibold text-gray-800 mt-6 mb-3">7.3 Brand Usage</h3>
            <p className="text-gray-700 leading-relaxed">
              You may use the "SamePageDating" name and logo in your promotional materials, provided:
            </p>
            <ul className="list-disc pl-6 text-gray-700 space-y-2 mt-2">
              <li>You do not imply official partnership or endorsement</li>
              <li>You do not alter or modify our branding</li>
              <li>You do not bid on our trademarks in paid search ads</li>
            </ul>
          </section>

          <section>
            <h2 className="text-2xl font-semibold text-gray-900 mt-8 mb-4">8. Commission Cancellations and Adjustments</h2>
            
            <h3 className="text-xl font-semibold text-gray-800 mt-6 mb-3">8.1 When Commissions Are Canceled</h3>
            <p className="text-gray-700 leading-relaxed">
              Commissions may be canceled or reversed if:
            </p>
            <ul className="list-disc pl-6 text-gray-700 space-y-2 mt-2">
              <li>The referred user cancels their subscription before the 90-day hold period ends</li>
              <li>The referred user requests a chargeback or refund</li>
              <li>Fraudulent activity is detected</li>
              <li>The referral violates this Agreement</li>
            </ul>

            <h3 className="text-xl font-semibold text-gray-800 mt-6 mb-3">8.2 Recurring Commission Stops</h3>
            <p className="text-gray-700 leading-relaxed">
              If a referred user cancels their subscription, you will stop receiving commissions for that user starting in the next month. 
              Previously paid commissions will not be clawed back (unless fraud is detected).
            </p>

            <h3 className="text-xl font-semibold text-gray-800 mt-6 mb-3">8.3 Commission Rate Changes</h3>
            <p className="text-gray-700 leading-relaxed">
              We reserve the right to change commission rates at any time with 30 days' notice. Existing referrals will be grandfathered 
              at the original rate.
            </p>
          </section>

          <section>
            <h2 className="text-2xl font-semibold text-gray-900 mt-8 mb-4">9. Account Termination</h2>
            
            <h3 className="text-xl font-semibold text-gray-800 mt-6 mb-3">9.1 Termination by You</h3>
            <p className="text-gray-700 leading-relaxed">
              You may terminate your participation in the Affiliate Program at any time. Approved commissions will still be paid out 
              on the next monthly payout schedule.
            </p>

            <h3 className="text-xl font-semibold text-gray-800 mt-6 mb-3">9.2 Termination by Us</h3>
            <p className="text-gray-700 leading-relaxed">
              We may terminate your affiliate account immediately if you violate this Agreement or engage in fraudulent activity. 
              Upon termination for cause:
            </p>
            <ul className="list-disc pl-6 text-gray-700 space-y-2 mt-2">
              <li>All pending commissions (not yet approved) will be forfeited</li>
              <li>Approved commissions may be withheld pending investigation</li>
              <li>Your referral link will be deactivated</li>
            </ul>

            <h3 className="text-xl font-semibold text-gray-800 mt-6 mb-3">9.3 Program Discontinuation</h3>
            <p className="text-gray-700 leading-relaxed">
              We reserve the right to discontinue the Affiliate Program at any time with 60 days' notice. All approved commissions 
              will be paid out before program closure.
            </p>
          </section>

          <section>
            <h2 className="text-2xl font-semibold text-gray-900 mt-8 mb-4">10. Relationship Between Parties</h2>
            <p className="text-gray-700 leading-relaxed font-semibold">
              This Agreement does not create an employment, partnership, joint venture, or agency relationship. You are an independent contractor.
            </p>
            <p className="text-gray-700 leading-relaxed mt-4">
              You have no authority to make any commitments on behalf of SamePageDating. You are solely responsible for your own taxes, 
              insurance, and business expenses.
            </p>
          </section>

          <section>
            <h2 className="text-2xl font-semibold text-gray-900 mt-8 mb-4">11. Limitation of Liability</h2>
            <p className="text-gray-700 leading-relaxed">
              SamePageDating shall not be liable for any indirect, incidental, or consequential damages arising from your participation 
              in the Affiliate Program, including but not limited to lost commissions, lost referrals, or platform downtime.
            </p>
            <p className="text-gray-700 leading-relaxed mt-4">
              Our total liability for any claim shall not exceed the total commissions paid to you in the preceding 12 months.
            </p>
          </section>

          <section>
            <h2 className="text-2xl font-semibold text-gray-900 mt-8 mb-4">12. Changes to This Agreement</h2>
            <p className="text-gray-700 leading-relaxed">
              We may update this Affiliate Agreement from time to time. Material changes will be communicated via email or dashboard notification 
              with 30 days' notice. Your continued participation in the Affiliate Program after changes constitutes acceptance of the updated terms.
            </p>
          </section>

          <section>
            <h2 className="text-2xl font-semibold text-gray-900 mt-8 mb-4">13. Governing Law</h2>
            <p className="text-gray-700 leading-relaxed">
              This Agreement shall be governed by the laws of the State of Ohio, United States, without regard to conflict of law provisions. 
              Any disputes shall be resolved through binding arbitration in accordance with our Terms of Service.
            </p>
          </section>

          <section>
            <h2 className="text-2xl font-semibold text-gray-900 mt-8 mb-4">14. Contact Information</h2>
            <p className="text-gray-700 leading-relaxed">
              Questions about the Affiliate Program? Contact us:
            </p>
            <p className="text-gray-700 mt-4">
              <strong>Email:</strong> affiliates@samepagedating.com<br />
              <strong>Support:</strong> Dashboard → Settings → Help
            </p>
          </section>

          <div className="mt-12 pt-8 border-t border-gray-200 bg-blue-50 -mx-8 -mb-8 px-8 py-6 rounded-b-lg">
            <p className="text-sm font-semibold text-gray-800 mb-2">
              By enrolling in the SamePageDating Affiliate Program, you acknowledge that you have read, understood, and agree to be bound by this Agreement.
            </p>
            <p className="text-sm text-gray-600">
              This Agreement is effective as of the date you enroll in the Affiliate Program and remains in effect until terminated by either party.
            </p>
          </div>
        </div>

        <div className="mt-8 pt-6 border-t border-gray-200 flex gap-6">
          <Link to="/terms-of-service" className="text-blue-600 hover:underline">Terms of Service</Link>
          <Link to="/privacy-policy" className="text-blue-600 hover:underline">Privacy Policy</Link>
          <Link to="/affiliates/dashboard" className="text-blue-600 hover:underline">Affiliate Dashboard</Link>
          <Link to="/" className="text-blue-600 hover:underline">← Back to Home</Link>
        </div>
      </div>
    </div>
  );
}
