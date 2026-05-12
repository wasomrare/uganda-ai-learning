'use client';
import { useEffect, useState } from 'react';
import { useRouter } from 'next/navigation';
import Cookies from 'js-cookie';
import Sidebar from '@/components/layout/Sidebar';
import Header from '@/components/layout/Header';
import { useAuthStore } from '@/store/auth';
import { authApi } from '@/lib/api';

export default function DashboardLayout({ children }: { children: React.ReactNode }) {
  const router = useRouter();
  const { user, setAuth } = useAuthStore();
  const [checking, setChecking] = useState(true);

  useEffect(() => {
    const token = Cookies.get('access_token');
    if (!token) { router.replace('/login'); return; }
    if (user) { setChecking(false); return; }
    authApi.me()
      .then((res) => {
        const u = res.data?.data ?? res.data;
        const refresh = Cookies.get('refresh_token') ?? '';
        setAuth(u, token, refresh);
      })
      .catch(() => {
        Cookies.remove('access_token');
        Cookies.remove('refresh_token');
        router.replace('/login');
      })
      .finally(() => setChecking(false));
  }, []); // eslint-disable-line react-hooks/exhaustive-deps

  if (checking) {
    return (
      <div className="flex h-screen items-center justify-center bg-gray-50">
        <div className="w-8 h-8 border-2 border-green-500 border-t-transparent rounded-full animate-spin" />
      </div>
    );
  }

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
