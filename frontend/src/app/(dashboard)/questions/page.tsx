'use client';
import { useState } from 'react';
import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query';
import { questionsApi } from '@/lib/api';
import { Plus, Search, CheckCircle, Sparkles, Loader2 } from 'lucide-react';
import { cn } from '@/lib/utils';
import type { Question } from '@/types';

const DIFF_COLOR: Record<string, string> = {
  easy: 'bg-green-50 text-green-700',
  medium: 'bg-yellow-50 text-yellow-700',
  hard: 'bg-red-50 text-red-600',
};

const TYPE_ICON: Record<string, string> = {
  mcq: 'MCQ',
  fill_blank: 'Fill',
  matching: 'Match',
  short_answer: 'Short',
  composition: 'Essay',
};

export default function QuestionsPage() {
  const qc = useQueryClient();
  const [search, setSearch] = useState('');
  const [type, setType] = useState('');

  const { data, isLoading } = useQuery({
    queryKey: ['questions', search, type],
    queryFn: () => questionsApi.list({ search, question_type: type }).then((r) => r.data.data),
  });

  const { data: stats } = useQuery({
    queryKey: ['question-stats'],
    queryFn: () => questionsApi.stats().then((r) => r.data.data),
  });

  const approveMutation = useMutation({
    mutationFn: (id: string) => questionsApi.approve(id),
    onSuccess: () => qc.invalidateQueries({ queryKey: ['questions'] }),
  });

  const questions: Question[] = data?.results ?? [];

  return (
    <div className="space-y-5">
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-xl font-bold text-gray-900">Question Bank</h1>
          <p className="text-sm text-gray-500">{data?.count ?? 0} questions · {stats?.approved ?? 0} approved</p>
        </div>
        <div className="flex gap-2">
          <button className="flex items-center gap-2 px-3 py-2 border border-gray-200 text-gray-700 rounded-xl text-sm font-medium hover:bg-gray-50 transition">
            <Sparkles size={15} className="text-purple-500" /> Generate with AI
          </button>
          <button className="flex items-center gap-2 px-4 py-2 bg-green-600 text-white rounded-xl text-sm font-medium hover:bg-green-700 transition">
            <Plus size={16} /> Add Question
          </button>
        </div>
      </div>

      <div className="flex flex-wrap gap-3">
        <div className="relative flex-1 min-w-48">
          <Search size={14} className="absolute left-3 top-1/2 -translate-y-1/2 text-gray-400" />
          <input value={search} onChange={(e) => setSearch(e.target.value)}
            placeholder="Search questions…"
            className="w-full pl-8 pr-4 py-2 border border-gray-200 rounded-xl text-sm focus:outline-none focus:ring-2 focus:ring-green-500" />
        </div>
        <select value={type} onChange={(e) => setType(e.target.value)}
          className="px-3 py-2 border border-gray-200 rounded-xl text-sm focus:outline-none bg-white">
          <option value="">All Types</option>
          <option value="mcq">MCQ</option>
          <option value="fill_blank">Fill in Blank</option>
          <option value="matching">Matching</option>
          <option value="short_answer">Short Answer</option>
          <option value="composition">Composition</option>
        </select>
      </div>

      <div className="bg-white rounded-2xl border border-gray-100 shadow-sm overflow-hidden">
        <table className="w-full text-sm">
          <thead>
            <tr className="border-b border-gray-100 bg-gray-50">
              <th className="text-left px-5 py-3 text-xs font-semibold text-gray-500 uppercase tracking-wider">Question</th>
              <th className="text-left px-5 py-3 text-xs font-semibold text-gray-500 uppercase tracking-wider">Type</th>
              <th className="text-left px-5 py-3 text-xs font-semibold text-gray-500 uppercase tracking-wider">Subject</th>
              <th className="text-left px-5 py-3 text-xs font-semibold text-gray-500 uppercase tracking-wider">Level</th>
              <th className="text-left px-5 py-3 text-xs font-semibold text-gray-500 uppercase tracking-wider">Difficulty</th>
              <th className="text-left px-5 py-3 text-xs font-semibold text-gray-500 uppercase tracking-wider">Status</th>
              <th className="px-5 py-3" />
            </tr>
          </thead>
          <tbody className="divide-y divide-gray-50">
            {isLoading
              ? Array.from({ length: 6 }).map((_, i) => (
                <tr key={i}><td colSpan={7} className="px-5 py-4"><div className="h-4 bg-gray-100 rounded animate-pulse" /></td></tr>
              ))
              : questions.map((q) => (
                <tr key={q.id} className="hover:bg-gray-50 transition-colors">
                  <td className="px-5 py-3.5 max-w-xs">
                    <p className="text-gray-800 truncate">{q.question_text}</p>
                    <p className="text-xs text-gray-400 mt-0.5">{q.marks} mark{q.marks !== 1 ? 's' : ''}</p>
                  </td>
                  <td className="px-5 py-3.5">
                    <span className="px-2 py-0.5 bg-blue-50 text-blue-600 rounded-full text-xs font-medium">
                      {TYPE_ICON[q.question_type] ?? q.question_type}
                    </span>
                  </td>
                  <td className="px-5 py-3.5 text-gray-600 text-xs">{q.subject?.name ?? '—'}</td>
                  <td className="px-5 py-3.5 text-gray-600 text-xs">{q.class_level}</td>
                  <td className="px-5 py-3.5">
                    <span className={cn('px-2 py-0.5 rounded-full text-xs font-medium capitalize', DIFF_COLOR[q.difficulty])}>
                      {q.difficulty}
                    </span>
                  </td>
                  <td className="px-5 py-3.5">
                    <span className={cn('px-2 py-0.5 rounded-full text-xs font-medium', q.is_approved ? 'bg-green-50 text-green-700' : 'bg-yellow-50 text-yellow-700')}>
                      {q.is_approved ? 'Approved' : 'Pending'}
                    </span>
                  </td>
                  <td className="px-5 py-3.5">
                    {!q.is_approved && (
                      <button onClick={() => approveMutation.mutate(q.id)} disabled={approveMutation.isPending}
                        className="flex items-center gap-1 px-2 py-1 text-xs text-green-600 border border-green-200 rounded-lg hover:bg-green-50 transition">
                        {approveMutation.isPending ? <Loader2 size={10} className="animate-spin" /> : <CheckCircle size={10} />}
                        Approve
                      </button>
                    )}
                  </td>
                </tr>
              ))
            }
          </tbody>
        </table>
      </div>
    </div>
  );
}
