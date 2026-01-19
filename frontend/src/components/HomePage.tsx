import React from 'react';
import { useNavigate } from 'react-router-dom';

const HomePage: React.FC = () => {
  const navigate = useNavigate();

  return (
    <div className="min-h-screen bg-gray-50">
      {/* Hero Section */}
      <div className="relative overflow-hidden">
        <div className="max-w-7xl mx-auto px-6 py-16">
          <div className="text-center">
            <div className="mb-8">
              <div className="w-24 h-24 bg-blue-600 rounded-2xl flex items-center justify-center mx-auto mb-6">
                <span className="text-white font-bold text-3xl">PA</span>
              </div>
              <h1 className="text-5xl font-bold text-gray-900 mb-6">
                Psych Agent
              </h1>
              <p className="text-xl text-gray-600 max-w-3xl mx-auto mb-8">
                AI-powered psychiatric clinical decision support system with DSM-5-TR integration, 
                intelligent documentation, and evidence-based treatment recommendations.
              </p>
            </div>

            {/* CTA Buttons */}
            <div className="flex flex-col sm:flex-row gap-4 justify-center mb-16">
              <button
                onClick={() => navigate('/chat')}
                className="bg-blue-600 hover:bg-blue-700 text-white px-8 py-4 rounded-lg font-semibold text-lg transition-colors"
              >
                Start Consultation
              </button>
              <button
                onClick={() => navigate('/scribe')}
                className="bg-gray-600 hover:bg-gray-700 text-white px-8 py-4 rounded-lg font-semibold text-lg transition-colors"
              >
                Clinical Scribe
              </button>
            </div>
          </div>
        </div>
      </div>

      {/* Key Features */}
      <div className="max-w-7xl mx-auto px-6 py-16">
        <div className="grid md:grid-cols-3 gap-8">
          <div className="text-center">
            <div className="w-16 h-16 bg-blue-600 rounded-xl flex items-center justify-center mx-auto mb-4">
              <span className="text-2xl">🧠</span>
            </div>
            <h3 className="text-xl font-semibold text-gray-900 mb-3">DSM-5-TR Powered</h3>
            <p className="text-gray-600">
              Complete diagnostic criteria with real-time citations and evidence-based recommendations
            </p>
          </div>
          
          <div className="text-center">
            <div className="w-16 h-16 bg-blue-600 rounded-xl flex items-center justify-center mx-auto mb-4">
              <span className="text-2xl">📝</span>
            </div>
            <h3 className="text-xl font-semibold text-gray-900 mb-3">Intelligent Documentation</h3>
            <p className="text-gray-600">
              AI-powered clinical note generation with structured templates and automated insights
            </p>
          </div>
          
          <div className="text-center">
            <div className="w-16 h-16 bg-blue-600 rounded-xl flex items-center justify-center mx-auto mb-4">
              <span className="text-2xl">🔒</span>
            </div>
            <h3 className="text-xl font-semibold text-gray-900 mb-3">Privacy First</h3>
            <p className="text-gray-600">
              HIPAA-compliant design with local processing and encrypted data handling
            </p>
          </div>
        </div>
      </div>

      {/* How It Works */}
      <div className="bg-white py-16">
        <div className="max-w-7xl mx-auto px-6">
          <h2 className="text-3xl font-bold text-gray-900 text-center mb-12">How It Works</h2>
          
          <div className="grid md:grid-cols-4 gap-8">
            <div className="text-center">
              <div className="w-12 h-12 bg-blue-600 rounded-full flex items-center justify-center mx-auto mb-4 text-white font-bold">
                1
              </div>
              <h4 className="text-lg font-semibold text-gray-900 mb-2">Ask Questions</h4>
              <p className="text-gray-600 text-sm">
                Query diagnostic criteria, treatment options, or clinical guidelines
              </p>
            </div>
            
            <div className="text-center">
              <div className="w-12 h-12 bg-blue-600 rounded-full flex items-center justify-center mx-auto mb-4 text-white font-bold">
                2
              </div>
              <h4 className="text-lg font-semibold text-gray-900 mb-2">AI Analysis</h4>
              <p className="text-gray-600 text-sm">
                Advanced AI processes your query against DSM-5-TR and clinical databases
              </p>
            </div>
            
            <div className="text-center">
              <div className="w-12 h-12 bg-blue-600 rounded-full flex items-center justify-center mx-auto mb-4 text-white font-bold">
                3
              </div>
              <h4 className="text-lg font-semibold text-gray-900 mb-2">Evidence-Based Response</h4>
              <p className="text-gray-600 text-sm">
                Receive detailed answers with citations and treatment recommendations
              </p>
            </div>
            
            <div className="text-center">
              <div className="w-12 h-12 bg-blue-600 rounded-full flex items-center justify-center mx-auto mb-4 text-white font-bold">
                4
              </div>
              <h4 className="text-lg font-semibold text-gray-900 mb-2">Clinical Documentation</h4>
              <p className="text-gray-600 text-sm">
                Generate structured notes and treatment plans automatically
              </p>
            </div>
          </div>
        </div>
      </div>

      {/* Stats */}
      <div className="max-w-7xl mx-auto px-6 py-16">
        <div className="grid md:grid-cols-4 gap-8 text-center">
          <div>
            <div className="text-3xl font-bold text-blue-600 mb-2">500+</div>
            <div className="text-gray-600">Diagnostic Criteria</div>
          </div>
          <div>
            <div className="text-3xl font-bold text-blue-600 mb-2">24/7</div>
            <div className="text-gray-600">Availability</div>
          </div>
          <div>
            <div className="text-3xl font-bold text-blue-600 mb-2">100%</div>
            <div className="text-gray-600">HIPAA Compliant</div>
          </div>
          <div>
            <div className="text-3xl font-bold text-blue-600 mb-2">AI</div>
            <div className="text-gray-600">Powered Insights</div>
          </div>
        </div>
      </div>
    </div>
  );
};

export default HomePage;
