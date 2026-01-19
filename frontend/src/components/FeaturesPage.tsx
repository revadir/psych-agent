import React from 'react';

const FeaturesPage: React.FC = () => {
  const features = [
    {
      icon: '🧠',
      title: 'DSM-5-TR Integration',
      description: 'Complete diagnostic criteria database with real-time citations and ICD codes'
    },
    {
      icon: '💬',
      title: 'AI-Powered Chat',
      description: 'Intelligent psychiatric consultation with evidence-based responses'
    },
    {
      icon: '📝',
      title: 'Clinical Scribe',
      description: 'AI-powered note-taking with structured clinical documentation'
    },
    {
      icon: '🔍',
      title: 'Multi-Source RAG',
      description: 'Retrieval from DSM-5-TR, ICD-11, and clinical knowledge bases'
    },
    {
      icon: '📊',
      title: 'Analytics Dashboard',
      description: 'Feedback analysis and usage insights for continuous improvement'
    },
    {
      icon: '🔒',
      title: 'HIPAA Compliant',
      description: 'Secure, encrypted, and privacy-focused clinical decision support'
    }
  ];

  return (
    <div className="min-h-screen bg-gray-900 p-6">
      <div className="max-w-6xl mx-auto">
        {/* Header */}
        <div className="text-center mb-12">
          <h1 className="text-4xl font-bold text-white mb-4">Features</h1>
          <p className="text-xl text-gray-400 max-w-3xl mx-auto">
            Comprehensive psychiatric clinical decision support powered by AI and evidence-based medicine
          </p>
        </div>

        {/* Features Grid */}
        <div className="grid md:grid-cols-2 lg:grid-cols-3 gap-8">
          {features.map((feature, index) => (
            <div
              key={index}
              className="bg-gray-800 rounded-lg p-6 border border-gray-700 hover:border-amber-500 transition-colors"
            >
              <div className="text-4xl mb-4">{feature.icon}</div>
              <h3 className="text-xl font-semibold text-white mb-3">{feature.title}</h3>
              <p className="text-gray-400 leading-relaxed">{feature.description}</p>
            </div>
          ))}
        </div>

        {/* Technical Details */}
        <div className="mt-16 bg-gray-800 rounded-lg p-8">
          <h2 className="text-2xl font-bold text-white mb-6">Technical Capabilities</h2>
          <div className="grid md:grid-cols-2 gap-8">
            <div>
              <h3 className="text-lg font-semibold text-amber-400 mb-3">AI & Machine Learning</h3>
              <ul className="text-gray-300 space-y-2">
                <li>• Large Language Model integration (Ollama/Groq)</li>
                <li>• Vector database for semantic search</li>
                <li>• Real-time retrieval augmented generation (RAG)</li>
                <li>• Contextual conversation memory</li>
              </ul>
            </div>
            <div>
              <h3 className="text-lg font-semibold text-amber-400 mb-3">Clinical Integration</h3>
              <ul className="text-gray-300 space-y-2">
                <li>• DSM-5-TR diagnostic criteria</li>
                <li>• ICD-11 classification system</li>
                <li>• Evidence-based treatment recommendations</li>
                <li>• Clinical documentation templates</li>
              </ul>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
};

export default FeaturesPage;
