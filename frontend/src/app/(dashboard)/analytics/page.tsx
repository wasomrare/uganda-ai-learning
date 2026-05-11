'use client';
import { useQuery } from '@tanstack/react-query';
import { analyticsApi } from '@/lib/api';
import { BarChart, Bar, XAxis, YAxis, CartesianGrid, Tooltip, ResponsiveContainer, RadarChart, Radar, PolarGrid, PolarAngleAxis } from 'recharts';
import { TrendingUp, TrendingDown, Minus } from 'lucide-react';

export default function AnalyticsPage() {
  const { data, isLoading } = useQuery({
    queryKey: ['admin-analytics'],
    queryFn: () => analyticsApi.admin().then((r) => r.data.data),
  });

  const mockMastery = [
    { subject: 'Mathematics', mastery: 68, attempts: 420 },
    { subject: 'English', mastery: 74, attempts: 380 },
    { subject: 'Science', mastery: 61, attempts: 290 },
    { subject: 'SST', mastery: 79, attempts: 310 },
    { subject: 'Luganda', mastery: 65, attempts: 250 },
    { subject: 'CRE', mastery: 82, attempts: 200 },
  ];

  const mockClassPerf = [
    { class: 'P1', avg: 81 }, { class: 'P2', avg: 78 }, { class: 'P3', avg: 74 },
    { class: 'P4', avg: 71 }, { class: 'P5', avg: 68 }, { class: 'P6', avg: 65 }, { class: 'P7', avg: 72 },
  ];

  return (
    <div className="space-y-6">
      <div>
        <h1 className="text-xl font-bold text-gray-900">Analytics</h1>
        <p className="text-sm text-gray-500">System-wide learning analytics</p>
      </div>

      <div className="grid grid-cols-1 lg:grid-cols-2 gap-5">
        <div className="bg-white rounded-2xl p-5 border border-gray-100 shadow-sm">
          <h3 className="text-sm font-semibold text-gray-800 mb-4">Subject Mastery Scores</h3>
          <ResponsiveContainer width="100%" height={220}>
            <BarChart data={mockMastery} margin={{ top: 0, right: 0, left: -20, bottom: 0 }}>
              <CartesianGrid strokeDasharray="3 3" stroke="#f0f0f0" />
              <XAxis dataKey="subject" tick={{ fontSize: 10 }} />
              <YAxis tick={{ fontSize: 11 }} domain={[0, 100]} />
              <Tooltip formatter={(v) => [`${v}%`, 'Mastery']} />
              <Bar dataKey="mastery" radius={[4, 4, 0, 0]} fill="#22c55e" />
            </BarChart>
          </ResponsiveContainer>
        </div>

        <div className="bg-white rounded-2xl p-5 border border-gray-100 shadow-sm">
          <h3 className="text-sm font-semibold text-gray-800 mb-4">Average Score by Class</h3>
          <ResponsiveContainer width="100%" height={220}>
            <BarChart data={mockClassPerf} margin={{ top: 0, right: 0, left: -20, bottom: 0 }}>
              <CartesianGrid strokeDasharray="3 3" stroke="#f0f0f0" />
              <XAxis dataKey="class" tick={{ fontSize: 11 }} />
              <YAxis tick={{ fontSize: 11 }} domain={[0, 100]} />
              <Tooltip formatter={(v) => [`${v}%`, 'Avg Score']} />
              <Bar dataKey="avg" radius={[4, 4, 0, 0]} fill="#3b82f6" />
            </BarChart>
          </ResponsiveContainer>
        </div>
      </div>

      <div className="bg-white rounded-2xl border border-gray-100 shadow-sm overflow-hidden">
        <div className="px-5 py-4 border-b border-gray-100">
          <h3 className="text-sm font-semibold text-gray-800">Subject Performance Breakdown</h3>
        </div>
        <div className="divide-y divide-gray-50">
          {mockMastery.map((s) => (
            <div key={s.subject} className="flex items-center px-5 py-3.5 gap-4">
              <div className="w-28 text-sm text-gray-700 font-medium flex-shrink-0">{s.subject}</div>
              <div className="flex-1">
                <div className="flex items-center gap-2 mb-1">
                  <div className="flex-1 h-2 bg-gray-100 rounded-full overflow-hidden">
                    <div className="h-full rounded-full transition-all duration-500"
                      style={{ width: `${s.mastery}%`, background: s.mastery >= 75 ? '#22c55e' : s.mastery >= 60 ? '#f59e0b' : '#ef4444' }} />
                  </div>
                  <span className="text-sm font-semibold text-gray-700 w-10 text-right">{s.mastery}%</span>
                </div>
              </div>
              <div className="text-xs text-gray-400 flex-shrink-0 w-24 text-right">{s.attempts} attempts</div>
              <div className="flex-shrink-0">
                {s.mastery >= 75 ? <TrendingUp size={14} className="text-green-500" /> :
                 s.mastery >= 60 ? <Minus size={14} className="text-yellow-500" /> :
                 <TrendingDown size={14} className="text-red-500" />}
              </div>
            </div>
          ))}
        </div>
      </div>
    </div>
  );
}
