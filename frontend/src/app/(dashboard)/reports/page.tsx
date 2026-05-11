'use client';
import { useQuery } from '@tanstack/react-query';
import { reportsApi } from '@/lib/api';
import { FileText, Download } from 'lucide-react';
import { formatDate } from '@/lib/utils';

export default function ReportsPage() {
  const { data, isLoading } = useQuery({
    queryKey: ['reports'],
    queryFn: () => reportsApi.list().then((r: any) => r.data.data),
  });

  const reports = data?.results ?? [];
  const typeIcons: Record<string, string> = {
    student_performance: '📊', class_summary: '📋', assessment_report: '📝',
    subject_analysis: '🔬', ple_prediction: '🎓',
  };
  const typeLabels: Record<string, string> = {
    student_performance: 'Student Performance', class_summary: 'Class Summary',
    assessment_report: 'Assessment Report', subject_analysis: 'Subject Analysis', ple_prediction: 'PLE Prediction',
  };

  return (
    <div className="space-y-5">
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-xl font-bold text-gray-900">Reports</h1>
          <p className="text-sm text-gray-500">Generated performance reports</p>
        </div>
        <button className="flex items-center gap-2 px-4 py-2 bg-green-600 text-white rounded-xl text-sm font-medium hover:bg-green-700 transition">
          <FileText size={15} /> Generate Report
        </button>
      </div>

      <div className="bg-white rounded-2xl border border-gray-100 shadow-sm overflow-hidden">
        {isLoading
          ? Array.from({ length: 4 }).map((_, i) => (
            <div key={i} className="px-5 py-4 flex items-center gap-4 border-b border-gray-50">
              <div className="w-10 h-10 rounded-xl bg-gray-100 animate-pulse" />
              <div className="flex-1 space-y-2">
                <div className="h-3 bg-gray-100 rounded w-1/3 animate-pulse" />
                <div className="h-3 bg-gray-100 rounded w-1/4 animate-pulse" />
              </div>
            </div>
          ))
          : reports.length === 0
            ? (
              <div className="py-16 text-center text-gray-400">
                <FileText size={40} className="mx-auto mb-3 text-gray-200" />
                <p>No reports generated yet</p>
              </div>
            )
            : reports.map((r: any) => (
              <div key={r.id} className="flex items-center gap-4 px-5 py-4 border-b border-gray-50 last:border-0 hover:bg-gray-50 transition-colors">
                <div className="w-10 h-10 bg-blue-50 rounded-xl flex items-center justify-center text-xl flex-shrink-0">
                  {typeIcons[r.report_type] ?? '📄'}
                </div>
                <div className="flex-1 min-w-0">
                  <p className="font-medium text-sm text-gray-800">{r.title}</p>
                  <p className="text-xs text-gray-400 mt-0.5">
                    {typeLabels[r.report_type] ?? r.report_type} · {formatDate(r.created_at)}
                  </p>
                </div>
                {r.file_url && (
                  <a href={r.file_url} target="_blank" rel="noopener noreferrer"
                    className="flex items-center gap-1.5 px-3 py-1.5 text-xs text-blue-600 border border-blue-200 rounded-lg hover:bg-blue-50 transition flex-shrink-0">
                    <Download size={12} /> Download
                  </a>
                )}
              </div>
            ))
        }
      </div>
    </div>
  );
}
