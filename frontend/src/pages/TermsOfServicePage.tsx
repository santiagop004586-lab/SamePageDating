import React from 'react';
import { Link } from 'react-router-dom';

export default function TermsOfServicePage() {
  return (
    <div className="min-h-screen bg-gray-50 py-12 px-4 sm:px-6 lg:px-8">
      <div className="max-w-4xl mx-auto bg-white shadow-sm rounded-lg p-8">
        <h1 className="text-3xl font-bold text-gray-900 mb-2">Terms of Service</h1>
        <p className="text-sm text-gray-500 mb-8">Last Updated: March 22, 2026</p>

        <div className="prose prose-blue max-w-none space-y-6">
          <section>
            <h2 className="text-2xl font-semibold text-gray-900 mt-8 mb-4">1. Agreement to Terms</h2>
            <p className="text-gray-700 leading-relaxed">
              By accessing or using SamePageDating ("Service", "Platform", or "we"), you agree to be bound by these Terms of Service. 
              If you do not agree to these terms, you may not access or use the Service.
            </p>
          </section>

          <section>
            <h2 className="text-2xl font-semibold text-gray-900 mt-8 mb-4">2. Description of Service</h2>
            <p className="text-gray-700 leading-relaxed">
              SamePageDating is a compatibility-first dating platform that uses a detailed questionnaire to match users based on their 
              values, goals, and relationship preferences. The Service helps users find meaningful connections with compatible partners.
            </p>
            <p className="text-gray-700 leading-relaxed mt-4">
              <strong>Service Features Include:</strong>
            </p>
            <ul className="list-disc pl-6 text-gray-700 space-y-2 mt-2">
              <li>Real-time property listings from third-party data sources</li>
              <li>Section 8 rental analysis and cash flow calculations</li>
              <li>Investment metrics (ROI, cap rate, cash-on-cash return, BRRRR analysis)</li>
              <li>Interactive map-based property search</li>
              <li>Custom market analysis tools</li>
            </ul>
          </section>

          <section>
            <h2 className="text-2xl font-semibold text-gray-900 mt-8 mb-4">3. Subscription and Billing</h2>
            
            <h3 className="text-xl font-semibold text-gray-800 mt-6 mb-3">3.1 Subscription Plans</h3>
            <p className="text-gray-700 leading-relaxed">
              The Service is offered on a subscription basis for $19.99 per month. All new subscriptions include a 30-day free trial period. 
              You will not be charged until the trial period ends.
            </p>

            <h3 className="text-xl font-semibold text-gray-800 mt-6 mb-3">3.2 Automatic Renewal</h3>
            <p className="text-gray-700 leading-relaxed">
              Your subscription will automatically renew at the end of each billing period unless you cancel before the renewal date. 
              You will be charged the then-current subscription fee.
            </p>

            <h3 className="text-xl font-semibold text-gray-800 mt-6 mb-3">3.3 Payment Method</h3>
            <p className="text-gray-700 leading-relaxed">
              You agree to provide current, complete, and accurate payment information. All billing is handled securely through 
              Stripe, Inc. We do not store your payment card information on our servers.
            </p>

            <h3 className="text-xl font-semibold text-gray-800 mt-6 mb-3">3.4 Failed Payments</h3>
            <p className="text-gray-700 leading-relaxed">
              If a payment fails, your subscription will be suspended and you will lose access to the Service. We will attempt to 
              re-process the payment. If payment remains unsuccessful after 7 days, your account may be canceled.
            </p>
          </section>

          <section>
            <h2 className="text-2xl font-semibold text-gray-900 mt-8 mb-4">4. Cancellation and Refunds</h2>
            
            <h3 className="text-xl font-semibold text-gray-800 mt-6 mb-3">4.1 Cancellation</h3>
            <p className="text-gray-700 leading-relaxed">
              You may cancel your subscription at any time through your account settings or the Stripe billing portal. 
              Cancellation will take effect at the end of the current billing period. You will retain access until that date.
            </p>

            <h3 className="text-xl font-semibold text-gray-800 mt-6 mb-3">4.2 No Refunds Policy</h3>
            <p className="text-gray-700 leading-relaxed font-semibold">
              ALL SUBSCRIPTION FEES ARE NON-REFUNDABLE. Once charged, fees will not be refunded for any reason, including but not 
              limited to: early cancellation, dissatisfaction with the Service, or lack of use.
            </p>
            <p className="text-gray-700 leading-relaxed mt-4">
              We strongly encourage you to take advantage of the 30-day free trial to evaluate the Service before committing to a paid subscription.
            </p>

            <h3 className="text-xl font-semibold text-gray-800 mt-6 mb-3">4.3 Free Trial Cancellation</h3>
            <p className="text-gray-700 leading-relaxed">
              You may cancel during the free trial period without any charge. If you do not cancel before the trial ends, 
              you will be charged the monthly subscription fee.
            </p>
          </section>

          <section>
            <h2 className="text-2xl font-semibold text-gray-900 mt-8 mb-4">5. User Accounts</h2>
            
            <h3 className="text-xl font-semibold text-gray-800 mt-6 mb-3">5.1 Account Creation</h3>
            <p className="text-gray-700 leading-relaxed">
              You must create an account to use the Service. You agree to provide accurate, current, and complete information 
              during registration and to update such information as necessary.
            </p>

            <h3 className="text-xl font-semibold text-gray-800 mt-6 mb-3">5.2 Account Security</h3>
            <p className="text-gray-700 leading-relaxed">
              You are responsible for maintaining the confidentiality of your account credentials and for all activities that occur under your account. 
              You must immediately notify us of any unauthorized use of your account.
            </p>

            <h3 className="text-xl font-semibold text-gray-800 mt-6 mb-3">5.3 Account Termination</h3>
            <p className="text-gray-700 leading-relaxed">
              We reserve the right to suspend or terminate your account at any time for violation of these Terms, fraudulent activity, 
              or for any other reason at our sole discretion.
            </p>
          </section>

          <section>
            <h2 className="text-2xl font-semibold text-gray-900 mt-8 mb-4">6. Data and Information Disclaimer</h2>
            
            <h3 className="text-xl font-semibold text-gray-800 mt-6 mb-3">6.1 Third-Party Data</h3>
            <p className="text-gray-700 leading-relaxed">
              Property listings and market data are obtained from third-party sources. We make no representations or warranties regarding 
              the accuracy, completeness, or timeliness of such data.
            </p>

            <h3 className="text-xl font-semibold text-gray-800 mt-6 mb-3">6.2 Not Financial Advice</h3>
            <p className="text-gray-700 leading-relaxed font-semibold">
              THE SERVICE PROVIDES ANALYTICAL TOOLS AND DATA FOR INFORMATIONAL PURPOSES ONLY. IT DOES NOT CONSTITUTE FINANCIAL, 
              INVESTMENT, LEGAL, OR TAX ADVICE. You should consult with appropriate professionals before making any investment decisions.
            </p>

            <h3 className="text-xl font-semibold text-gray-800 mt-6 mb-3">6.3 Investment Risk</h3>
            <p className="text-gray-700 leading-relaxed">
              Real estate investment involves substantial risk. Past performance does not guarantee future results. You are solely 
              responsible for evaluating the risks and merits of any investment decision.
            </p>

            <h3 className="text-xl font-semibold text-gray-800 mt-6 mb-3">6.4 No Guarantee of Results</h3>
            <p className="text-gray-700 leading-relaxed">
              We make no guarantees regarding the profitability of properties analyzed through the Service. Calculations and projections 
              are estimates only and may not reflect actual outcomes.
            </p>
          </section>

          <section>
            <h2 className="text-2xl font-semibold text-gray-900 mt-8 mb-4">7. Acceptable Use</h2>
            <p className="text-gray-700 leading-relaxed">You agree not to:</p>
            <ul className="list-disc pl-6 text-gray-700 space-y-2 mt-2">
              <li>Use the Service for any illegal purpose or in violation of any laws</li>
              <li>Scrape, copy, or redistribute data from the Service</li>
              <li>Attempt to gain unauthorized access to any part of the Service</li>
              <li>Use automated tools (bots, scrapers) to access the Service</li>
              <li>Share your account credentials with others</li>
              <li>Use the Service to harass, abuse, or harm others</li>
              <li>Upload malicious code or attempt to disrupt the Service</li>
            </ul>
          </section>

          <section>
            <h2 className="text-2xl font-semibold text-gray-900 mt-8 mb-4">8. Intellectual Property</h2>
            <p className="text-gray-700 leading-relaxed">
              The Service, including all content, features, and functionality, is owned by SamePageDating and is protected by 
              copyright, trademark, and other intellectual property laws. You may not copy, modify, distribute, or create derivative 
              works based on the Service without our express written permission.
            </p>
          </section>

          <section>
            <h2 className="text-2xl font-semibold text-gray-900 mt-8 mb-4">9. Limitation of Liability</h2>
            <p className="text-gray-700 leading-relaxed font-semibold">
              TO THE MAXIMUM EXTENT PERMITTED BY LAW, SAMEPAGEDATING SHALL NOT BE LIABLE FOR ANY INDIRECT, INCIDENTAL, SPECIAL, 
              CONSEQUENTIAL, OR PUNITIVE DAMAGES, OR ANY LOSS OF PROFITS OR REVENUES, WHETHER INCURRED DIRECTLY OR INDIRECTLY, 
              OR ANY LOSS OF DATA, USE, GOODWILL, OR OTHER INTANGIBLE LOSSES, RESULTING FROM:
            </p>
            <ul className="list-disc pl-6 text-gray-700 space-y-2 mt-4">
              <li>Your use or inability to use the Service</li>
              <li>Any investment decisions made based on data from the Service</li>
              <li>Unauthorized access to or alteration of your data</li>
              <li>Errors, inaccuracies, or omissions in the data provided</li>
              <li>Any other matter relating to the Service</li>
            </ul>
            <p className="text-gray-700 leading-relaxed mt-4">
              Our total liability for any claim arising out of or relating to the Service shall not exceed the amount you paid us 
              in the 12 months preceding the claim.
            </p>
          </section>

          <section>
            <h2 className="text-2xl font-semibold text-gray-900 mt-8 mb-4">10. Disclaimer of Warranties</h2>
            <p className="text-gray-700 leading-relaxed font-semibold">
              THE SERVICE IS PROVIDED "AS IS" AND "AS AVAILABLE" WITHOUT WARRANTIES OF ANY KIND, EITHER EXPRESS OR IMPLIED, 
              INCLUDING BUT NOT LIMITED TO WARRANTIES OF MERCHANTABILITY, FITNESS FOR A PARTICULAR PURPOSE, AND NON-INFRINGEMENT.
            </p>
            <p className="text-gray-700 leading-relaxed mt-4">
              We do not warrant that the Service will be uninterrupted, error-free, or secure, or that defects will be corrected.
            </p>
          </section>

          <section>
            <h2 className="text-2xl font-semibold text-gray-900 mt-8 mb-4">11. Indemnification</h2>
            <p className="text-gray-700 leading-relaxed">
              You agree to indemnify, defend, and hold harmless SamePageDating, its officers, directors, employees, and agents from 
              any claims, damages, losses, liabilities, and expenses (including attorney fees) arising out of or relating to your use 
              of the Service, your violation of these Terms, or your violation of any rights of another party.
            </p>
          </section>

          <section>
            <h2 className="text-2xl font-semibold text-gray-900 mt-8 mb-4">12. Changes to Terms</h2>
            <p className="text-gray-700 leading-relaxed">
              We reserve the right to modify these Terms at any time. We will provide notice of material changes by posting the updated 
              Terms on this page and updating the "Last Updated" date. Your continued use of the Service after such changes constitutes 
              acceptance of the new Terms.
            </p>
          </section>

          <section>
            <h2 className="text-2xl font-semibold text-gray-900 mt-8 mb-4">13. Governing Law and Dispute Resolution</h2>
            
            <h3 className="text-xl font-semibold text-gray-800 mt-6 mb-3">13.1 Governing Law</h3>
            <p className="text-gray-700 leading-relaxed">
              These Terms shall be governed by and construed in accordance with the laws of the State of Ohio, United States, 
              without regard to its conflict of law provisions.
            </p>

            <h3 className="text-xl font-semibold text-gray-800 mt-6 mb-3">13.2 Arbitration</h3>
            <p className="text-gray-700 leading-relaxed">
              Any dispute arising out of or relating to these Terms or the Service shall be resolved through binding arbitration 
              in accordance with the American Arbitration Association's rules. The arbitration shall be conducted in Cleveland, Ohio.
            </p>

            <h3 className="text-xl font-semibold text-gray-800 mt-6 mb-3">13.3 Class Action Waiver</h3>
            <p className="text-gray-700 leading-relaxed font-semibold">
              YOU AGREE TO RESOLVE DISPUTES ONLY ON AN INDIVIDUAL BASIS AND NOT AS PART OF ANY CLASS, CONSOLIDATED, OR 
              REPRESENTATIVE ACTION. You waive any right to participate in a class action lawsuit or class-wide arbitration.
            </p>
          </section>

          <section>
            <h2 className="text-2xl font-semibold text-gray-900 mt-8 mb-4">14. Severability</h2>
            <p className="text-gray-700 leading-relaxed">
              If any provision of these Terms is found to be unenforceable or invalid, that provision will be limited or eliminated 
              to the minimum extent necessary, and the remaining provisions will remain in full force and effect.
            </p>
          </section>

          <section>
            <h2 className="text-2xl font-semibold text-gray-900 mt-8 mb-4">15. Contact Information</h2>
            <p className="text-gray-700 leading-relaxed">
              If you have questions about these Terms, please contact us at:
            </p>
            <p className="text-gray-700 mt-4">
              <strong>Email:</strong> support@samepagedating.com<br />
              <strong>Website:</strong> <a href="https://samepagedating.com" className="text-blue-600 hover:underline">samepagedating.com</a>
            </p>
          </section>

          <div className="mt-12 pt-8 border-t border-gray-200">
            <p className="text-sm text-gray-600">
              By using SamePageDating, you acknowledge that you have read, understood, and agree to be bound by these Terms of Service.
            </p>
          </div>
        </div>

        <div className="mt-8 pt-6 border-t border-gray-200 flex gap-6">
          <Link to="/privacy-policy" className="text-blue-600 hover:underline">Privacy Policy</Link>
          <Link to="/affiliate-agreement" className="text-blue-600 hover:underline">Affiliate Agreement</Link>
          <Link to="/" className="text-blue-600 hover:underline">← Back to Home</Link>
        </div>
      </div>
    </div>
  );
}
