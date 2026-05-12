'use client';
import { useEffect } from 'react';
import Sidebar from '@/components/layout/Sidebar';
import Header from '@/components/layout/Header';
import { useAuthStore } from '@/store/auth';
import api from '@/lib/api';

export default function DashboardLayout({ children }: { children: React.ReactNode }) {
  const { user, setAuth } = useAuthStore();

  useEffect(() => {
    if (user) return;
    api.get('/users/me/')
      .then((res) => {
        const u = res.data?.data ?? res.data;
        setAuth(u, '', '');
      })
      .catch(() => {/* silently ignore — proxy handles auth */});
  }, []); // eslint-disable-line react-hooks/exhaustive-deps

  return (
    <div className="flex h-screen bg-gray-50 overflow-hidden">
      <Sidebar />
      <div className="flex-1 flex flex-col min-w-0 overflow-hidden">
        <Header />
        <main className="flex-1 overflow-y-auto p-6">
          {children}
        </main>
      </div>
    </div>
  );
}
