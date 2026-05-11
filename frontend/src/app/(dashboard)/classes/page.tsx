'use client';
import { useQuery } from '@tanstack/react-query';
import { classesApi } from '@/lib/api';
import { School, Users } from 'lucide-react';

export default function ClassesPage() {
  const { data, isLoading } = useQuery({
    queryKey: ['classes'],
    queryFn: () => classesApi.list().then((r: any) => r.data.data),
  });
  const classes = data?.results ?? [];

  return (
    <div className="space-y-5">
      <div>
        <h1 className="text-xl font-bold text-gray-900">Classes</h1>
        <p className="text-sm text-gray-500">{classes.length} classes registered</p>
      </div>
      <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 gap-4">
        {isLoading
          ? Array.from({ length: 6 }).map((_, i) => (
            <div key={i} className="bg-white rounded-2xl border border-gray-100 p-5 space-y-3 animate-pulse">
              <div className="h-4 bg-gray-100 rounded w-1/2" />
              <div className="h-3 bg-gray-100 rounded w-3/4" />
            </div>
          ))
          : classes.map((c: any) => (
            <div key={c.id} className="bg-white rounded-2xl border border-gray-100 shadow-sm p-5 hover:shadow-md transition">
              <div className="flex items-center gap-3 mb-3">
                <div className="w-10 h-10 bg-green-50 rounded-xl flex items-center justify-center">
                  <School size={18} className="text-green-600" />
                </div>
                <div>
                  <p className="font-semibold text-sm text-gray-900">{c.name}</p>
                  <p className="text-xs text-gray-400">{c.class_level} · {c.stream ?? 'Main'}</p>
                </div>
              </div>
              <div className="flex items-center gap-2 text-xs text-gray-500">
                <Users size={13} />
                <span>{c.student_count ?? 0} students</span>
              </div>
            </div>
          ))
        }
      </div>
    </div>
  );
}
