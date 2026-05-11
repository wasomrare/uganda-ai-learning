'use client';
import { useQuery } from '@tanstack/react-query';
import { subjectsApi } from '@/lib/api';
import { BookOpen } from 'lucide-react';

export default function SubjectsPage() {
  const { data, isLoading } = useQuery({
    queryKey: ['subjects'],
    queryFn: () => subjectsApi.list().then((r: any) => r.data.data),
  });
  const subjects = data?.results ?? [];

  const colors = ['bg-green-50 text-green-600', 'bg-blue-50 text-blue-600', 'bg-purple-50 text-purple-600',
    'bg-orange-50 text-orange-600', 'bg-red-50 text-red-600', 'bg-teal-50 text-teal-600'];

  return (
    <div className="space-y-5">
      <div>
        <h1 className="text-xl font-bold text-gray-900">Subjects</h1>
        <p className="text-sm text-gray-500">{subjects.length} subjects in curriculum</p>
      </div>
      <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 gap-4">
        {isLoading
          ? Array.from({ length: 6 }).map((_, i) => (
            <div key={i} className="bg-white rounded-2xl border border-gray-100 p-5 space-y-3 animate-pulse">
              <div className="h-4 bg-gray-100 rounded w-1/2" />
              <div className="h-3 bg-gray-100 rounded w-3/4" />
            </div>
          ))
          : subjects.map((s: any, idx: number) => (
            <div key={s.id} className="bg-white rounded-2xl border border-gray-100 shadow-sm p-5 hover:shadow-md transition">
              <div className="flex items-center gap-3 mb-3">
                <div className={`w-10 h-10 rounded-xl flex items-center justify-center ${colors[idx % colors.length]}`}>
                  <BookOpen size={18} />
                </div>
                <div>
                  <p className="font-semibold text-sm text-gray-900">{s.name}</p>
                  <p className="text-xs text-gray-400">{s.code ?? ''}</p>
                </div>
              </div>
              {s.description && <p className="text-xs text-gray-500 line-clamp-2">{s.description}</p>}
            </div>
          ))
        }
      </div>
    </div>
  );
}
