'use client';
import { Bell, Search, Wifi, WifiOff } from 'lucide-react';
import { useAuthStore } from '@/store/auth';
import { cn, getInitials } from '@/lib/utils';
import { useState, useEffect } from 'react';

export default function Header({ title }: { title?: string }) {
  const { user } = useAuthStore();
  const [online, setOnline] = useState(true);

  useEffect(() => {
    const onOnline = () => setOnline(true);
    const onOffline = () => setOnline(false);
    window.addEventListener('online', onOnline);
    window.addEventListener('offline', onOffline);
    return () => { window.removeEventListener('online', onOnline); window.removeEventListener('offline', onOffline); };
  }, []);

  return (
    <header className="h-14 bg-white border-b border-gray-200 flex items-center justify-between px-6 flex-shrink-0">
      <div className="flex items-center gap-3">
        <div className="relative">
          <Search size={15} className="absolute left-3 top-1/2 -translate-y-1/2 text-gray-400" />
          <input
            type="text"
            placeholder="Search…"
            className="pl-9 pr-4 py-1.5 text-sm bg-gray-50 border border-gray-200 rounded-lg w-56 focus:outline-none focus:ring-1 focus:ring-green-500 focus:border-green-500"
          />
        </div>
      </div>

      <div className="flex items-center gap-3">
        <span className={cn('flex items-center gap-1.5 text-xs px-2 py-1 rounded-full',
          online ? 'text-green-600 bg-green-50' : 'text-red-500 bg-red-50')}>
          {online ? <Wifi size={12} /> : <WifiOff size={12} />}
          {online ? 'Online' : 'Offline'}
        </span>

        <button className="relative p-1.5 text-gray-500 hover:text-gray-800 hover:bg-gray-100 rounded-lg transition">
          <Bell size={18} />
          <span className="absolute top-0.5 right-0.5 w-2 h-2 bg-red-500 rounded-full" />
        </button>

        <div className="flex items-center gap-2">
          <div className="w-8 h-8 bg-green-500 rounded-full flex items-center justify-center text-white text-xs font-bold">
            {user ? getInitials(`${user.first_name} ${user.last_name}`) : 'U'}
          </div>
          <div className="hidden sm:block">
            <p className="text-sm font-medium text-gray-800">{user?.first_name} {user?.last_name}</p>
            <p className="text-xs text-gray-400 capitalize">{user?.role?.replace('_', ' ')}</p>
          </div>
        </div>
      </div>
    </header>
  );
}
