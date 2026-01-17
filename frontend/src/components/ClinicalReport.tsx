import React, { useState } from 'react';

interface ClinicalReportProps {
  transcript: string;
  onClose: () => void;
}

interface ReportData {
  metadata: {
    generated_at: string;
    transcript_length: number;
    session_duration: string;
  };
  patient_presentation: string;
  clinical_assessment: string;
  diagnostic_considerations: string;
  risk_assessment: string;
  treatment_recommendations: string;
  next_steps: string;
}

const ClinicalReport: React.FC<ClinicalReportProps> = ({ transcript, onClose }) => {
  const [report, setReport] = useState<ReportData | null>(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);

  const generateReport = async () => {
    setLoading(true);
    setError(null);
    
    try {
      const response = await fetch('/api/asr/generate-report', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({ transcript }),
      });
      
      const data = await response.json();
      
      if (data.success) {
        setReport(data.report);
      } else {
        setError(data.error || 'Failed to generate report');
      }
    } catch (err) {
      setError('Network error occurred');
    } finally {
      setLoading(false);
    }
  };

  const downloadReport = () => {
    if (!report) return;
    
    const reportText = formatReportForDownload(report);
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

  const formatReportForDownload = (reportData: ReportData): string => {
    return `
CLINICAL REPORT
Generated: ${new Date(reportData.metadata.generated_at).toLocaleString()}
Session Duration: ${reportData.metadata.session_duration}
Transcript Length: ${reportData.metadata.transcript_length} words

PATIENT PRESENTATION
${reportData.patient_presentation}

CLINICAL ASSESSMENT
${reportData.clinical_assessment}

DIAGNOSTIC CONSIDERATIONS
${reportData.diagnostic_considerations}

RISK ASSESSMENT
${reportData.risk_assessment}

TREATMENT RECOMMENDATIONS
${reportData.treatment_recommendations}

NEXT STEPS
${reportData.next_steps}
    `.trim();
  };

  return (
    <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50 p-4">
      <div className="bg-gray-900 rounded-lg shadow-xl max-w-4xl w-full max-h-[90vh] overflow-hidden">
        {/* Header */}
        <div className="bg-gradient-to-r from-amber-600 to-amber-700 px-6 py-4 flex justify-between items-center">
          <h2 className="text-xl font-bold text-white">Clinical Report Generator</h2>
          <button
            onClick={onClose}
            className="text-white hover:text-gray-200 text-2xl font-bold"
          >
            ×
          </button>
        </div>

        <div className="p-6 overflow-y-auto" style={{ maxHeight: 'calc(90vh - 120px)' }}>
          {!report && !loading && (
            <div className="text-center py-8">
              <div className="mb-4">
                <svg className="mx-auto h-16 w-16 text-amber-500" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9 12h6m-6 4h6m2 5H7a2 2 0 01-2-2V5a2 2 0 012-2h5.586a1 1 0 01.707.293l5.414 5.414a1 1 0 01.293.707V19a2 2 0 01-2 2z" />
                </svg>
              </div>
              <h3 className="text-lg font-medium text-white mb-2">Generate Clinical Report</h3>
              <p className="text-gray-400 mb-6">
                Create a comprehensive clinical report from the session transcript
              </p>
              <button
                onClick={generateReport}
                className="bg-amber-600 hover:bg-amber-700 text-white px-6 py-3 rounded-lg font-medium transition-colors"
              >
                Generate Report
              </button>
            </div>
          )}

          {loading && (
            <div className="text-center py-12">
              <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-amber-500 mx-auto mb-4"></div>
              <p className="text-gray-400">Generating comprehensive clinical report...</p>
              <p className="text-sm text-gray-500 mt-2">This may take 30-60 seconds</p>
            </div>
          )}

          {error && (
            <div className="bg-red-900 border border-red-700 rounded-lg p-4 mb-4">
              <p className="text-red-200">{error}</p>
              <button
                onClick={generateReport}
                className="mt-2 bg-red-700 hover:bg-red-600 text-white px-4 py-2 rounded text-sm"
              >
                Try Again
              </button>
            </div>
          )}

          {report && (
            <div className="space-y-6">
              {/* Report Header */}
              <div className="bg-gray-800 rounded-lg p-4 border border-gray-700">
                <div className="flex justify-between items-start mb-4">
                  <h3 className="text-lg font-semibold text-white">Clinical Report</h3>
                  <button
                    onClick={downloadReport}
                    className="bg-amber-600 hover:bg-amber-700 text-white px-4 py-2 rounded text-sm flex items-center gap-2"
                  >
                    <svg className="w-4 h-4" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                      <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M12 10v6m0 0l-3-3m3 3l3-3m2 8H7a2 2 0 01-2-2V5a2 2 0 012-2h5.586a1 1 0 01.707.293l5.414 5.414a1 1 0 01.293.707V19a2 2 0 01-2 2z" />
                    </svg>
                    Download
                  </button>
                </div>
                <div className="grid grid-cols-3 gap-4 text-sm">
                  <div>
                    <span className="text-gray-400">Generated:</span>
                    <p className="text-white">{new Date(report.metadata.generated_at).toLocaleString()}</p>
                  </div>
                  <div>
                    <span className="text-gray-400">Duration:</span>
                    <p className="text-white">{report.metadata.session_duration}</p>
                  </div>
                  <div>
                    <span className="text-gray-400">Words:</span>
                    <p className="text-white">{report.metadata.transcript_length}</p>
                  </div>
                </div>
              </div>

              {/* Report Sections */}
              <ReportSection title="Patient Presentation" content={report.patient_presentation} />
              <ReportSection title="Clinical Assessment" content={report.clinical_assessment} />
              <ReportSection title="Diagnostic Considerations" content={report.diagnostic_considerations} />
              <ReportSection title="Risk Assessment" content={report.risk_assessment} />
              <ReportSection title="Treatment Recommendations" content={report.treatment_recommendations} />
              <ReportSection title="Next Steps" content={report.next_steps} />
            </div>
          )}
        </div>
      </div>
    </div>
  );
};

interface ReportSectionProps {
  title: string;
  content: string;
}

const ReportSection: React.FC<ReportSectionProps> = ({ title, content }) => {
  const formatContent = (text: string) => {
    // Split by bullet points and format nicely
    const lines = text.split('\n').filter(line => line.trim());
    
    return lines.map((line, index) => {
      const trimmed = line.trim();
      
      // Handle bullet points
      if (trimmed.startsWith('•') || trimmed.startsWith('-') || trimmed.startsWith('*')) {
        return (
          <div key={index} className="flex items-start gap-2 mb-2">
            <span className="text-amber-400 mt-1 text-sm">•</span>
            <span className="text-gray-200 leading-relaxed">{trimmed.replace(/^[•\-*]\s*/, '')}</span>
          </div>
        );
      }
      
      // Handle numbered items
      if (/^\d+\./.test(trimmed)) {
        return (
          <div key={index} className="flex items-start gap-2 mb-2">
            <span className="text-amber-400 font-medium text-sm">{trimmed.match(/^\d+\./)?.[0]}</span>
            <span className="text-gray-200 leading-relaxed">{trimmed.replace(/^\d+\.\s*/, '')}</span>
          </div>
        );
      }
      
      // Regular text
      if (trimmed) {
        return (
          <p key={index} className="text-gray-200 mb-2 leading-relaxed">
            {trimmed}
          </p>
        );
      }
      
      return null;
    });
  };

  return (
    <div className="bg-gray-800 rounded-lg p-4 border border-gray-700">
      <h4 className="text-lg font-semibold text-amber-400 mb-3 flex items-center gap-2">
        <span className="w-2 h-2 bg-amber-400 rounded-full"></span>
        {title}
      </h4>
      <div className="space-y-1">
        {formatContent(content)}
      </div>
    </div>
  );
};

export default ClinicalReport;
