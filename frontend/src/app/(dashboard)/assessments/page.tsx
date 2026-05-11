'use client';
import { useState } from 'react';
import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query';
import { assessmentsApi, subjectsApi } from '@/lib/api';
import { Plus, Search, Play, Lock, FileText, Eye, Loader2 } from 'lucide-react';
import { cn, formatDate } from '@/lib/utils';
import type { Assessment } from '@/types';

const TYPE_LABELS: Record<string, string> = {
  weekly_quiz: 'Weekly Quiz',
  monthly_test: 'Monthly Test',
  end_of_term: 'End of Term',
  diagnostic: 'Diagnostic',
  holiday_revision: 'Holiday',
  custom: 'Custom',
};

export default function AssessmentsPage() {
  const qc = useQueryClient();
  const [search, setSearch] = useState('');
  const [status, setStatus] = useState('');

  const { data, isLoading } = useQuery({
    queryKey: ['assessments', search, status],
    queryFn: () => assessmentsApi.list({ search, status }).then(r => r.data.data),
  });

  const publishMutation = useMutation({
    mutationFn: (id: string) => assessmentsApi.publish(id),
    onSuccess: () => qc.invalidateQueries({ queryKey: ['assessments'] }),
  });

  const closeMutation = useMutation({
    mutationFn: (id: string) => assessmentsApi.close(id),
    onSuccess: () => qc.invalidateQueries({ queryKey: ['assessments'] }),
  });

  const assessments: Assessment[] = data?.results ?? [];

  const statusBadge = (s: string) => ({
    draft: 'bg-gray-100 text-gray-600',
    active: 'bg-green-50 text-green-700',
    closed: 'bg-red-50 text-red-600',
  }[s] ?? 'bg-gray-100 text-gray-600');

  return (
    <div className="space-y-5">
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-xl font-bold text-gray-900">Assessments</h1>
          <p className="text-sm text-gray-500">{data?.count ?? 0} total assessments</p>
        </div>
        <button className="flex items-center gap-2 px-4 py-2 bg-green-600 text-white rounded-xl text-sm font-medium hover:bg-green-700 transition">
          <Plus size={16} /> New Assessment
        </button>
      </div>

      <div className="flex flex-wrap gap-3">
        <div className="relative flex-1 min-w-48">
          <Search size={14} className="absolute left-3 top-1/2 -translate-y-1/2 text-gray-400" />
          <input value={search} onChange={e => setSearch(e.target.value)}
            placeholder="Search assessments…"
            className="w-full pl-8 pr-4 py-2 border border-gray-200 rounded-xl text-sm focus:outline-none focus:ring-2 focus:ring-green-500" />
        </div>
        <select value={status} onChange={e => setStatus(e.target.value)}
          className="px-3 py-2 border border-gray-200 rounded-xl text-sm focus:outline-none bg-white">
          <option value="">All Status</option>
          <option value="draft">Draft</option>
          <option value="active">Active</option>
          <option value="closed">Closed</option>
        </select>
      </div>

      <div className="grid gap-3">
        {isLoading
          ? Array.from({ length: 5 }).map((_, i) => (
            <div key={i} className="bg-white rounded-2xl p-5 border border-gray-100 h-24 animate-pulse" />
          ))
          : assessments.length === 0
          ? (
            <div className="text-center py-16 bg-white rounded-2xl border border-gray-100">
              <FileText size={40} className="text-gray-200 mx-auto mb-3" />
              <p className="text-gray-400">No assessments found.</p>
            </div>
          )
          : assessments.map((a) => (
            <div key={a.id} className="bg-white rounded-2xl p-5 border border-gray-100 shadow-sm hover:shadow-md transition-shadow">
              <div className="flex items-start justify-between gap-4">
                <div className="flex-1 min-w-0">
                  <div className="flex items-center gap-2 flex-wrap">
                    <h3 className="font-semibold text-gray-900 truncate">{a.title}</h3>
                    <span className={cn('px-2 py-0.5 rounded-full text-xs font-medium', statusBadge(a.status))}>
                      {a.status}
                    </span>
                    <span className="px-2 py-0.5 bg-blue-50 text-blue-600 rounded-full text-xs">
                      {TYPE_LABELS[a.assessment_type] ?? a.assessment_type}
                    </span>
                  </div>
                  <div className="flex items-center gap-4 mt-2 text-xs text-gray-400 flex-wrap">
                    <span>{a.subject?.name} · {a.class_level}</span>
                    <span>{a.question_count} questions · {a.total_marks} marks · {a.duration_minutes} min</span>
                    <span>{a.attempt_count} attempts</span>
                    {a.average_score !== undefined && <span>Avg: {a.average_score.toFixed(1)}%</span>}
                    <span>Created {formatDate(a.created_at)}</span>
                  </div>
                </div>
                <div className="flex items-center gap-2 flex-shrink-0">
                  {a.status === 'draft' && (
                    <button onClick={() => publishMutation.mutate(a.id)} disabled={publishMutation.isPending}
                      className="flex items-center gap-1.5 px-3 py-1.5 bg-green-600 text-white rounded-lg text-xs font-medium hover:bg-green-700 transition disabled:opacity-50">
                      {publishMutation.isPending ? <Loader2 size={12} className="animate-spin" /> : <Play size={12} />}
                      Publish
                    </button>
                  )}
                  {a.status === 'active' && (
                    <button onClick={() => closeMutation.mutate(a.id)} disabled={closeMutation.isPending}
                      className="flex items-center gap-1.5 px-3 py-1.5 bg-red-500 text-white rounded-lg text-xs font-medium hover:bg-red-600 transition disabled:opacity-50">
                      {closeMutation.isPending ? <Loader2 size={12} className="animate-spin" /> : <Lock size={12} />}
                      Close
                    </button>
                  )}
                  <button className="p-1.5 text-gray-400 hover:text-gray-600 hover:bg-gray-100 rounded-lg transition">
                    <Eye size={16} />
                  </button>
                </div>
              </div>
            </div>
          ))
        }
      </div>
    </div>
  );
}
