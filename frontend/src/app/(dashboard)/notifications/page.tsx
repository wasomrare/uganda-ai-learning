'use client';
import { useState } from 'react';
import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query';
import { notificationsApi } from '@/lib/api';
import { Bell, CheckCheck, Loader2 } from 'lucide-react';
import { formatDate } from '@/lib/utils';

export default function NotificationsPage() {
  const qc = useQueryClient();
  const { data, isLoading } = useQuery({
    queryKey: ['notifications'],
    queryFn: () => notificationsApi.list().then((r: any) => r.data.data),
  });

  const markReadMutation = useMutation({
    mutationFn: (id: string) => notificationsApi.markRead(id),
    onSuccess: () => qc.invalidateQueries({ queryKey: ['notifications'] }),
  });

  const markAllMutation = useMutation({
    mutationFn: () => notificationsApi.markAllRead(),
    onSuccess: () => qc.invalidateQueries({ queryKey: ['notifications'] }),
  });

  const notifications = data?.results ?? [];
  const unread = notifications.filter((n: any) => !n.is_read).length;

  const typeIcons: Record<string, string> = {
    assessment: '📝', badge: '🏅', xp: '⭐', reminder: '⏰',
    announcement: '📢', system: '⚙️', grade: '📊',
  };

  return (
    <div className="space-y-5">
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-xl font-bold text-gray-900">Notifications</h1>
          <p className="text-sm text-gray-500">{unread} unread</p>
        </div>
        {unread > 0 && (
          <button
            onClick={() => markAllMutation.mutate()}
            disabled={markAllMutation.isPending}
            className="flex items-center gap-2 px-4 py-2 text-sm text-green-600 border border-green-200 rounded-xl hover:bg-green-50 transition"
          >
            {markAllMutation.isPending ? <Loader2 size={14} className="animate-spin" /> : <CheckCheck size={14} />}
            Mark all read
          </button>
        )}
      </div>

      <div className="bg-white rounded-2xl border border-gray-100 shadow-sm overflow-hidden divide-y divide-gray-50">
        {isLoading
          ? Array.from({ length: 5 }).map((_, i) => (
            <div key={i} className="p-4 flex gap-3">
              <div className="w-10 h-10 rounded-full bg-gray-100 animate-pulse flex-shrink-0" />
              <div className="flex-1 space-y-2">
                <div className="h-3 bg-gray-100 rounded animate-pulse w-3/4" />
                <div className="h-3 bg-gray-100 rounded animate-pulse w-1/2" />
              </div>
            </div>
          ))
          : notifications.length === 0
            ? (
              <div className="py-16 text-center text-gray-400">
                <Bell size={40} className="mx-auto mb-3 text-gray-200" />
                <p>No notifications yet</p>
              </div>
            )
            : notifications.map((n: any) => (
              <div
                key={n.id}
                onClick={() => !n.is_read && markReadMutation.mutate(n.id)}
                className={`flex gap-3 px-5 py-4 cursor-pointer hover:bg-gray-50 transition-colors ${!n.is_read ? 'bg-green-50/30' : ''}`}
              >
                <div className={`w-10 h-10 flex items-center justify-center rounded-full flex-shrink-0 text-lg ${!n.is_read ? 'bg-green-100' : 'bg-gray-100'}`}>
                  {typeIcons[n.notification_type] ?? '🔔'}
                </div>
                <div className="flex-1 min-w-0">
                  <p className={`text-sm ${!n.is_read ? 'font-semibold text-gray-800' : 'font-medium text-gray-700'}`}>{n.title}</p>
                  {n.message && <p className="text-xs text-gray-500 mt-0.5 line-clamp-2">{n.message}</p>}
                  <p className="text-xs text-gray-400 mt-1">{formatDate(n.created_at)}</p>
                </div>
                {!n.is_read && (
                  <div className="w-2 h-2 bg-green-500 rounded-full mt-2 flex-shrink-0" />
                )}
              </div>
            ))
        }
      </div>
    </div>
  );
}
