'use client';
import { useQuery } from '@tanstack/react-query';
import { gamificationApi, leaderboardsApi } from '@/lib/api';
import { Trophy, Star, Flame, Zap } from 'lucide-react';
import { cn } from '@/lib/utils';

export default function GamificationPage() {
  const { data: leaderboard } = useQuery({
    queryKey: ['leaderboard'],
    queryFn: () => leaderboardsApi.weekly().then((r: any) => r.data.data),
  });
  const { data: badges } = useQuery({
    queryKey: ['badges'],
    queryFn: () => gamificationApi.badges().then((r: any) => r.data.data),
  });

  const top = leaderboard?.results ?? [];
  const allBadges = badges?.results ?? [];
  const medals = ['🥇', '🥈', '🥉'];

  return (
    <div className="space-y-6">
      <div>
        <h1 className="text-xl font-bold text-gray-900">Gamification</h1>
        <p className="text-sm text-gray-500">XP leaderboard, badges and rewards</p>
      </div>

      <div className="grid grid-cols-1 lg:grid-cols-2 gap-5">
        {/* Leaderboard */}
        <div className="bg-white rounded-2xl border border-gray-100 shadow-sm overflow-hidden">
          <div className="flex items-center gap-2 px-5 py-4 border-b border-gray-100">
            <Trophy size={16} className="text-yellow-500" />
            <span className="text-sm font-semibold text-gray-800">Weekly Leaderboard</span>
          </div>
          <div className="divide-y divide-gray-50">
            {top.slice(0, 10).map((entry: any, i: number) => (
              <div key={entry.id ?? i} className={cn('flex items-center gap-3 px-5 py-3', i < 3 && 'bg-yellow-50/40')}>
                <div className="w-8 text-center font-bold text-sm text-gray-500">
                  {i < 3 ? medals[i] : i + 1}
                </div>
                <div className="w-8 h-8 bg-green-100 text-green-700 rounded-full flex items-center justify-center text-xs font-bold flex-shrink-0">
                  {entry.user_name?.[0]?.toUpperCase() ?? '?'}
                </div>
                <div className="flex-1 min-w-0">
                  <p className="font-medium text-sm text-gray-800 truncate">{entry.user_name}</p>
                  <p className="text-xs text-gray-400">{entry.class_level} · Level {entry.level}</p>
                </div>
                <div className="flex items-center gap-1 flex-shrink-0">
                  <Zap size={12} className="text-yellow-500" />
                  <span className="text-sm font-semibold text-gray-700">{entry.total_xp}</span>
                </div>
              </div>
            ))}
          </div>
        </div>

        {/* Badges */}
        <div className="bg-white rounded-2xl border border-gray-100 shadow-sm overflow-hidden">
          <div className="flex items-center gap-2 px-5 py-4 border-b border-gray-100">
            <Star size={16} className="text-yellow-500" />
            <span className="text-sm font-semibold text-gray-800">All Badges ({allBadges.length})</span>
          </div>
          <div className="p-4 grid grid-cols-3 gap-3">
            {allBadges.map((badge: any) => (
              <div key={badge.id} className="flex flex-col items-center gap-2 p-3 rounded-xl bg-gray-50 border border-gray-100">
                <div className="text-2xl">{badge.icon ?? '🏅'}</div>
                <p className="text-xs font-semibold text-gray-700 text-center leading-tight">{badge.name}</p>
                <p className="text-xs text-gray-400 text-center line-clamp-2">{badge.description}</p>
                <span className="text-xs px-2 py-0.5 bg-yellow-50 text-yellow-600 rounded-full font-medium">+{badge.xp_reward} XP</span>
              </div>
            ))}
          </div>
        </div>
      </div>
    </div>
  );
}
