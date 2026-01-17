import React from 'react';

interface ClinicalReport {
  session_summary: string;
  diagnostic_assessment: string;
  recommendations: string;
  transcript_length: number;
  key_symptoms: string[];
  risk_factors: string[];
}

interface ClinicalReportViewProps {
  report: ClinicalReport;
  onClose: () => void;
}

export const ClinicalReportView: React.FC<ClinicalReportViewProps> = ({ report, onClose }) => {
  const downloadReport = () => {
    const reportText = `
CLINICAL SESSION REPORT
Generated: ${new Date().toLocaleString()}

SESSION SUMMARY:
${report.session_summary}

DIAGNOSTIC ASSESSMENT:
${report.diagnostic_assessment}

RECOMMENDATIONS:
${report.recommendations}

KEY SYMPTOMS IDENTIFIED:
${report.key_symptoms.join(', ') || 'None identified'}

RISK FACTORS:
${report.risk_factors.join(', ') || 'None identified'}

TRANSCRIPT LENGTH: ${report.transcript_length} words
    `.trim();

    const blob = new Blob([reportText], { type: 'text/plain' });
    const url = URL.createObjectURL(blob);
    const a = document.createElement('a');
    a.href = url;
    a.download = `clinical-report-${new Date().toISOString().split('T')[0]}.txt`;
    document.body.appendChild(a);
    a.click();
    document.body.removeChild(a);
    URL.revokeObjectURL(url);
  };

  return (
    <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center p-4 z-50">
      <div className="bg-white rounded-lg shadow-xl max-w-4xl w-full max-h-[90vh] overflow-hidden">
        {/* Header */}
        <div className="bg-indigo-600 text-white p-6">
          <div className="flex items-center justify-between">
            <div className="flex items-center space-x-3">
              <svg className="w-6 h-6" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9 12h6m-6 4h6m2 5H7a2 2 0 01-2-2V5a2 2 0 012-2h5.586a1 1 0 01.707.293l5.414 5.414a1 1 0 01.293.707V19a2 2 0 01-2 2z" />
              </svg>
              <h2 className="text-xl font-bold">Clinical Session Report</h2>
            </div>
            <div className="flex items-center space-x-2">
              <button
                onClick={downloadReport}
                className="flex items-center space-x-2 px-3 py-1 bg-indigo-700 hover:bg-indigo-800 rounded transition-colors"
              >
                <svg className="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M12 10v6m0 0l-3-3m3 3l3-3m2 8H7a2 2 0 01-2-2V5a2 2 0 012-2h5.586a1 1 0 01.707.293l5.414 5.414a1 1 0 01.293.707V19a2 2 0 01-2 2z" />
                </svg>
                <span>Download</span>
              </button>
              <button
                onClick={onClose}
                className="text-indigo-200 hover:text-white transition-colors"
              >
                <svg className="w-6 h-6" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M6 18L18 6M6 6l12 12" />
                </svg>
              </button>
            </div>
          </div>
          <div className="flex items-center space-x-4 mt-2 text-indigo-200">
            <div className="flex items-center space-x-1">
              <svg className="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M8 7V3a2 2 0 012-2h4a2 2 0 012 2v4m-6 0V6a2 2 0 012-2h4a2 2 0 012 2v1m-6 0h6m-6 0l-.5 9a2 2 0 002 2h3a2 2 0 002-2L16 7m-6 0V6a2 2 0 012-2h4a2 2 0 012 2v1" />
              </svg>
              <span>{new Date().toLocaleDateString()}</span>
            </div>
            <div className="flex items-center space-x-1">
              <svg className="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9 12h6m-6 4h6m2 5H7a2 2 0 01-2-2V5a2 2 0 012-2h5.586a1 1 0 01.707.293l5.414 5.414a1 1 0 01.293.707V19a2 2 0 01-2 2z" />
              </svg>
              <span>{report.transcript_length} words</span>
            </div>
          </div>
        </div>

        {/* Content */}
        <div className="p-6 overflow-y-auto max-h-[calc(90vh-120px)]">
          <div className="space-y-6">
            {/* Session Summary */}
            <section>
              <h3 className="text-lg font-semibold text-gray-900 mb-3 flex items-center">
                <svg className="w-5 h-5 mr-2" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M16 7a4 4 0 11-8 0 4 4 0 018 0zM12 14a7 7 0 00-7 7h14a7 7 0 00-7-7z" />
                </svg>
                Session Summary
              </h3>
              <div className="bg-gray-50 p-4 rounded-lg">
                <p className="text-gray-800 leading-relaxed whitespace-pre-wrap">
                  {report.session_summary}
                </p>
              </div>
            </section>

            {/* Key Symptoms & Risk Factors */}
            <div className="grid md:grid-cols-2 gap-6">
              <section>
                <h3 className="text-lg font-semibold text-gray-900 mb-3">Key Symptoms</h3>
                <div className="bg-blue-50 p-4 rounded-lg">
                  {report.key_symptoms.length > 0 ? (
                    <div className="flex flex-wrap gap-2">
                      {report.key_symptoms.map((symptom, index) => (
                        <span
                          key={index}
                          className="px-3 py-1 bg-blue-100 text-blue-800 rounded-full text-sm font-medium"
                        >
                          {symptom}
                        </span>
                      ))}
                    </div>
                  ) : (
                    <p className="text-gray-600 italic">No specific symptoms identified</p>
                  )}
                </div>
              </section>

              <section>
                <h3 className="text-lg font-semibold text-gray-900 mb-3 flex items-center">
                  <svg className="w-5 h-5 mr-2 text-orange-500" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                    <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M12 9v2m0 4h.01m-6.938 4h13.856c1.54 0 2.502-1.667 1.732-2.5L13.732 4c-.77-.833-1.964-.833-2.732 0L4.082 16.5c-.77.833.192 2.5 1.732 2.5z" />
                  </svg>
                  Risk Factors
                </h3>
                <div className="bg-orange-50 p-4 rounded-lg">
                  {report.risk_factors.length > 0 ? (
                    <div className="flex flex-wrap gap-2">
                      {report.risk_factors.map((risk, index) => (
                        <span
                          key={index}
                          className="px-3 py-1 bg-orange-100 text-orange-800 rounded-full text-sm font-medium"
                        >
                          {risk}
                        </span>
                      ))}
                    </div>
                  ) : (
                    <p className="text-gray-600 italic">No significant risk factors identified</p>
                  )}
                </div>
              </section>
            </div>

            {/* Diagnostic Assessment */}
            <section>
              <h3 className="text-lg font-semibold text-gray-900 mb-3">Diagnostic Assessment</h3>
              <div className="bg-yellow-50 p-4 rounded-lg border-l-4 border-yellow-400">
                <p className="text-gray-800 leading-relaxed whitespace-pre-wrap">
                  {report.diagnostic_assessment}
                </p>
              </div>
            </section>

            {/* Recommendations */}
            <section>
              <h3 className="text-lg font-semibold text-gray-900 mb-3">Recommendations</h3>
              <div className="bg-green-50 p-4 rounded-lg border-l-4 border-green-400">
                <p className="text-gray-800 leading-relaxed whitespace-pre-wrap">
                  {report.recommendations}
                </p>
              </div>
            </section>
          </div>
        </div>

        {/* Footer */}
        <div className="bg-gray-50 px-6 py-3 border-t">
          <p className="text-sm text-gray-600">
            This report is generated for clinical decision support purposes only. 
            Always consult with qualified mental health professionals for diagnosis and treatment decisions.
          </p>
        </div>
      </div>
    </div>
  );
};
