import React from 'react';
import { Link } from 'react-router-dom';

export default function PrivacyPolicyPage() {
  return (
    <div className="min-h-screen bg-gray-50 py-12 px-4 sm:px-6 lg:px-8">
      <div className="max-w-4xl mx-auto bg-white shadow-sm rounded-lg p-8">
        <h1 className="text-3xl font-bold text-gray-900 mb-2">Privacy Policy</h1>
        <p className="text-sm text-gray-500 mb-8">Last Updated: March 22, 2026</p>

        <div className="prose prose-blue max-w-none space-y-6">
          <section>
            <h2 className="text-2xl font-semibold text-gray-900 mt-8 mb-4">1. Introduction</h2>
            <p className="text-gray-700 leading-relaxed">
              FindBestRentals ("we," "our," or "us") respects your privacy and is committed to protecting your personal information. 
              This Privacy Policy explains how we collect, use, disclose, and safeguard your information when you use our Service.
            </p>
            <p className="text-gray-700 leading-relaxed mt-4">
              By using FindBestRentals, you consent to the data practices described in this policy.
            </p>
          </section>

          <section>
            <h2 className="text-2xl font-semibold text-gray-900 mt-8 mb-4">2. Information We Collect</h2>
            
            <h3 className="text-xl font-semibold text-gray-800 mt-6 mb-3">2.1 Information You Provide</h3>
            <ul className="list-disc pl-6 text-gray-700 space-y-2">
              <li><strong>Account Information:</strong> Email address, password (encrypted), and name</li>
              <li><strong>Billing Information:</strong> Payment data is collected and processed by Stripe, Inc. We do not store credit card numbers on our servers.</li>
              <li><strong>Profile Information:</strong> Any additional information you choose to provide</li>
              <li><strong>Affiliate Information:</strong> If you join our affiliate program, we collect tax identification information (stored securely by Stripe Connect) and payout preferences</li>
            </ul>

            <h3 className="text-xl font-semibold text-gray-800 mt-6 mb-3">2.2 Automatically Collected Information</h3>
            <ul className="list-disc pl-6 text-gray-700 space-y-2">
              <li><strong>Usage Data:</strong> Pages viewed, features used, time spent on the Service</li>
              <li><strong>Device Information:</strong> IP address, browser type, operating system, device identifiers</li>
              <li><strong>Location Data:</strong> Approximate geographic location based on IP address</li>
              <li><strong>Cookies and Tracking:</strong> We use cookies and similar technologies to track activity and store preferences</li>
            </ul>

            <h3 className="text-xl font-semibold text-gray-800 mt-6 mb-3">2.3 Third-Party Data</h3>
            <p className="text-gray-700 leading-relaxed">
              We collect publicly available property listing data from third-party sources (Realtor.com via RapidAPI) and HUD Fair Market Rent data 
              to provide our Service. This data is not personally identifiable.
            </p>
          </section>

          <section>
            <h2 className="text-2xl font-semibold text-gray-900 mt-8 mb-4">3. How We Use Your Information</h2>
            <p className="text-gray-700 leading-relaxed">We use your information to:</p>
            <ul className="list-disc pl-6 text-gray-700 space-y-2 mt-2">
              <li>Provide, operate, and maintain the Service</li>
              <li>Process your subscription payments and renewals</li>
              <li>Send you account-related emails (billing, authentication, password resets)</li>
              <li>Respond to your inquiries and provide customer support</li>
              <li>Monitor and analyze usage patterns to improve the Service</li>
              <li>Detect, prevent, and address fraud and security issues</li>
              <li>Process affiliate commissions and payouts</li>
              <li>Track referrals and conversions for our affiliate program</li>
              <li>Enforce our Terms of Service</li>
              <li>Comply with legal obligations</li>
            </ul>
          </section>

          <section>
            <h2 className="text-2xl font-semibold text-gray-900 mt-8 mb-4">4. How We Share Your Information</h2>
            
            <h3 className="text-xl font-semibold text-gray-800 mt-6 mb-3">4.1 Service Providers</h3>
            <p className="text-gray-700 leading-relaxed">
              We share information with third-party service providers who perform services on our behalf:
            </p>
            <ul className="list-disc pl-6 text-gray-700 space-y-2 mt-2">
              <li><strong>Stripe, Inc.:</strong> Payment processing, subscription management, affiliate payouts, and tax compliance (1099 forms)</li>
              <li><strong>RapidAPI / Api Dojo:</strong> Property listing data (we do not share your personal information with them)</li>
              <li><strong>Cloud Hosting:</strong> Infrastructure providers for hosting our Service</li>
              <li><strong>Email Service:</strong> Transactional email delivery for account notifications</li>
            </ul>

            <h3 className="text-xl font-semibold text-gray-800 mt-6 mb-3">4.2 Legal Requirements</h3>
            <p className="text-gray-700 leading-relaxed">
              We may disclose your information if required by law, court order, or government regulation, or if we believe disclosure is 
              necessary to protect our rights, your safety, or the safety of others.
            </p>

            <h3 className="text-xl font-semibold text-gray-800 mt-6 mb-3">4.3 Business Transfers</h3>
            <p className="text-gray-700 leading-relaxed">
              If we are involved in a merger, acquisition, or sale of assets, your information may be transferred to the acquiring entity. 
              You will be notified of any such change.
            </p>

            <h3 className="text-xl font-semibold text-gray-800 mt-6 mb-3">4.4 With Your Consent</h3>
            <p className="text-gray-700 leading-relaxed">
              We may share your information for other purposes with your explicit consent.
            </p>

            <p className="text-gray-700 leading-relaxed font-semibold mt-4">
              We do not sell, rent, or trade your personal information to third parties for marketing purposes.
            </p>
          </section>

          <section>
            <h2 className="text-2xl font-semibold text-gray-900 mt-8 mb-4">5. Cookies and Tracking Technologies</h2>
            
            <h3 className="text-xl font-semibold text-gray-800 mt-6 mb-3">5.1 Cookies We Use</h3>
            <ul className="list-disc pl-6 text-gray-700 space-y-2">
              <li><strong>Authentication Cookies:</strong> Keep you logged in to your account</li>
              <li><strong>Referral Tracking Cookies:</strong> Track affiliate referrals (30-day cookie lifetime)</li>
              <li><strong>Preference Cookies:</strong> Remember your settings and preferences</li>
              <li><strong>Analytics Cookies:</strong> Help us understand how you use the Service</li>
            </ul>

            <h3 className="text-xl font-semibold text-gray-800 mt-6 mb-3">5.2 Managing Cookies</h3>
            <p className="text-gray-700 leading-relaxed">
              You can control cookies through your browser settings. However, disabling cookies may limit your ability to use certain features of the Service.
            </p>
          </section>

          <section>
            <h2 className="text-2xl font-semibold text-gray-900 mt-8 mb-4">6. Data Security</h2>
            <p className="text-gray-700 leading-relaxed">
              We implement appropriate technical and organizational measures to protect your personal information:
            </p>
            <ul className="list-disc pl-6 text-gray-700 space-y-2 mt-2">
              <li>Passwords are hashed using industry-standard encryption (bcrypt)</li>
              <li>All data transmission is encrypted using HTTPS/TLS</li>
              <li>Payment data is handled exclusively by PCI-compliant Stripe</li>
              <li>Access to personal data is restricted to authorized personnel only</li>
              <li>Regular security audits and monitoring for vulnerabilities</li>
            </ul>
            <p className="text-gray-700 leading-relaxed mt-4">
              However, no method of transmission over the Internet or electronic storage is 100% secure. While we strive to protect your 
              information, we cannot guarantee absolute security.
            </p>
          </section>

          <section>
            <h2 className="text-2xl font-semibold text-gray-900 mt-8 mb-4">7. Data Retention</h2>
            <p className="text-gray-700 leading-relaxed">
              We retain your personal information for as long as your account is active or as needed to provide the Service. 
              We will retain and use your information as necessary to:
            </p>
            <ul className="list-disc pl-6 text-gray-700 space-y-2 mt-2">
              <li>Comply with legal obligations (tax records, audit trails)</li>
              <li>Resolve disputes and enforce agreements</li>
              <li>Process affiliate commissions and payouts</li>
              <li>Maintain fraud detection records</li>
            </ul>
            <p className="text-gray-700 leading-relaxed mt-4">
              Affiliate tax records (1099 forms) are retained for 7 years as required by law. Commission records are retained indefinitely for accounting purposes.
            </p>
          </section>

          <section>
            <h2 className="text-2xl font-semibold text-gray-900 mt-8 mb-4">8. Your Privacy Rights</h2>
            
            <h3 className="text-xl font-semibold text-gray-800 mt-6 mb-3">8.1 Access and Correction</h3>
            <p className="text-gray-700 leading-relaxed">
              You may access and update your account information at any time through your account settings.
            </p>

            <h3 className="text-xl font-semibold text-gray-800 mt-6 mb-3">8.2 Account Deletion</h3>
            <p className="text-gray-700 leading-relaxed">
              You may request deletion of your account by contacting us. Upon deletion:
            </p>
            <ul className="list-disc pl-6 text-gray-700 space-y-2 mt-2">
              <li>Your account will be permanently deactivated</li>
              <li>Personal information will be deleted, except where retention is required by law</li>
              <li>Billing and commission records may be retained for tax and audit purposes</li>
              <li>Anonymized usage data may be retained for analytics</li>
            </ul>

            <h3 className="text-xl font-semibold text-gray-800 mt-6 mb-3">8.3 Marketing Communications</h3>
            <p className="text-gray-700 leading-relaxed">
              We currently do not send marketing emails. If this changes, you will have the option to opt out.
            </p>

            <h3 className="text-xl font-semibold text-gray-800 mt-6 mb-3">8.4 California Privacy Rights (CCPA)</h3>
            <p className="text-gray-700 leading-relaxed">
              If you are a California resident, you have the right to:
            </p>
            <ul className="list-disc pl-6 text-gray-700 space-y-2 mt-2">
              <li>Know what personal information we collect and how it is used</li>
              <li>Request deletion of your personal information</li>
              <li>Opt out of the sale of personal information (we do not sell your data)</li>
              <li>Non-discrimination for exercising your privacy rights</li>
            </ul>

            <h3 className="text-xl font-semibold text-gray-800 mt-6 mb-3">8.5 European Privacy Rights (GDPR)</h3>
            <p className="text-gray-700 leading-relaxed">
              If you are in the European Economic Area, you have additional rights under GDPR:
            </p>
            <ul className="list-disc pl-6 text-gray-700 space-y-2 mt-2">
              <li>Right to access your personal data</li>
              <li>Right to rectification of inaccurate data</li>
              <li>Right to erasure ("right to be forgotten")</li>
              <li>Right to restrict processing</li>
              <li>Right to data portability</li>
              <li>Right to object to processing</li>
              <li>Right to withdraw consent</li>
            </ul>
          </section>

          <section>
            <h2 className="text-2xl font-semibold text-gray-900 mt-8 mb-4">9. Children's Privacy</h2>
            <p className="text-gray-700 leading-relaxed">
              Our Service is not intended for children under 18 years of age. We do not knowingly collect personal information from 
              children under 18. If we discover that a child under 18 has provided us with personal information, we will delete it immediately.
            </p>
          </section>

          <section>
            <h2 className="text-2xl font-semibold text-gray-900 mt-8 mb-4">10. International Data Transfers</h2>
            <p className="text-gray-700 leading-relaxed">
              Your information may be transferred to and processed in the United States or other countries where our service providers operate. 
              These countries may have different data protection laws than your country of residence.
            </p>
            <p className="text-gray-700 leading-relaxed mt-4">
              By using our Service, you consent to the transfer of your information to the United States and other jurisdictions.
            </p>
          </section>

          <section>
            <h2 className="text-2xl font-semibold text-gray-900 mt-8 mb-4">11. Third-Party Links</h2>
            <p className="text-gray-700 leading-relaxed">
              The Service may contain links to third-party websites (e.g., Realtor.com property listings). We are not responsible for the 
              privacy practices of these external sites. We encourage you to review their privacy policies.
            </p>
          </section>

          <section>
            <h2 className="text-2xl font-semibold text-gray-900 mt-8 mb-4">12. Changes to This Privacy Policy</h2>
            <p className="text-gray-700 leading-relaxed">
              We may update this Privacy Policy from time to time. We will notify you of material changes by posting the updated policy 
              on this page and updating the "Last Updated" date. Your continued use of the Service after changes constitutes acceptance 
              of the new policy.
            </p>
          </section>

          <section>
            <h2 className="text-2xl font-semibold text-gray-900 mt-8 mb-4">13. Contact Us</h2>
            <p className="text-gray-700 leading-relaxed">
              If you have questions about this Privacy Policy or wish to exercise your privacy rights, please contact us:
            </p>
            <p className="text-gray-700 mt-4">
              <strong>Email:</strong> privacy@findbestrentals.com<br />
              <strong>Website:</strong> <a href="https://findbestrentals.com" className="text-blue-600 hover:underline">findbestrentals.com</a>
            </p>
            <p className="text-gray-700 leading-relaxed mt-4">
              We will respond to your request within 30 days.
            </p>
          </section>

          <div className="mt-12 pt-8 border-t border-gray-200">
            <p className="text-sm text-gray-600">
              This Privacy Policy complies with the California Consumer Privacy Act (CCPA) and the European General Data Protection Regulation (GDPR).
            </p>
          </div>
        </div>

        <div className="mt-8 pt-6 border-t border-gray-200 flex gap-6">
          <Link to="/terms-of-service" className="text-blue-600 hover:underline">Terms of Service</Link>
          <Link to="/affiliate-agreement" className="text-blue-600 hover:underline">Affiliate Agreement</Link>
          <Link to="/" className="text-blue-600 hover:underline">← Back to Home</Link>
        </div>
      </div>
    </div>
  );
}
