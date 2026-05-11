'use client';
import { useState } from 'react';
import { useQuery } from '@tanstack/react-query';
import { teachersApi } from '@/lib/api';
import { Plus, Search } from 'lucide-react';
import { getInitials } from '@/lib/utils';
import type { Teacher } from '@/types';

export default function TeachersPage() {
  const [search, setSearch] = useState('');
  const { data, isLoading } = useQuery({
    queryKey: ['teachers', search],
    queryFn: () => teachersApi.list({ search }).then((r) => r.data.data),
  });
  const teachers: Teacher[] = data?.results ?? [];

  return (
    <div className="space-y-5">
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-xl font-bold text-gray-900">Teachers</h1>
          <p className="text-sm text-gray-500">{data?.count ?? 0} registered teachers</p>
        </div>
        <button className="flex items-center gap-2 px-4 py-2 bg-green-600 text-white rounded-xl text-sm font-medium hover:bg-green-700 transition">
          <Plus size={16} /> Add Teacher
        </button>
      </div>
      <div className="relative max-w-sm">
        <Search size={14} className="absolute left-3 top-1/2 -translate-y-1/2 text-gray-400" />
        <input value={search} onChange={(e) => setSearch(e.target.value)}
          placeholder="Search teachers…"
          className="w-full pl-8 pr-4 py-2 border border-gray-200 rounded-xl text-sm focus:outline-none focus:ring-2 focus:ring-green-500" />
      </div>
      <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 gap-4">
        {isLoading
          ? Array.from({ length: 6 }).map((_, i) => (
            <div key={i} className="bg-white rounded-2xl p-5 border border-gray-100 h-28 animate-pulse" />
          ))
          : teachers.map((t) => (
            <div key={t.id} className="bg-white rounded-2xl p-5 border border-gray-100 shadow-sm hover:shadow-md transition-shadow">
              <div className="flex items-center gap-3">
                <div className="w-10 h-10 bg-purple-100 text-purple-700 rounded-full flex items-center justify-center font-bold">
                  {getInitials(`${t.user.first_name} ${t.user.last_name}`)}
                </div>
                <div className="flex-1 min-w-0">
                  <p className="font-semibold text-gray-800 truncate">{t.user.first_name} {t.user.last_name}</p>
                  <p className="text-xs text-gray-400 truncate">{t.employee_id} · {t.specialization}</p>
                </div>
                <span className={`flex-shrink-0 px-2 py-0.5 rounded-full text-xs font-medium ${t.is_active ? 'bg-green-50 text-green-700' : 'bg-gray-100 text-gray-500'}`}>
                  {t.is_active ? 'Active' : 'Inactive'}
                </span>
              </div>
              <p className="mt-3 text-xs text-gray-500">{t.qualification}</p>
            </div>
          ))
        }
      </div>
    </div>
  );
}
