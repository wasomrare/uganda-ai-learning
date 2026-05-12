'use client';
import Link from 'next/link';
import { usePathname } from 'next/navigation';
import {
  LayoutDashboard, Users, GraduationCap, School, BookOpen,
  ClipboardList, BarChart3, Trophy, Bell, Settings, LogOut,
  Sparkles, FileText, Layers, Brain, ChevronLeft, ChevronRight,
} from 'lucide-react';
import { cn } from '@/lib/utils';
import { useAuthStore } from '@/store/auth';
import { useState } from 'react';

const navItems = [
  { href: '/dashboard', label: 'Dashboard', icon: LayoutDashboard },
  { href: '/students', label: 'Students', icon: Users },
  { href: '/teachers', label: 'Teachers', icon: GraduationCap },
  { href: '/classes', label: 'Classes', icon: School },
  { href: '/subjects', label: 'Subjects', icon: BookOpen },
  { href: '/assessments', label: 'Assessments', icon: ClipboardList },
  { href: '/questions', label: 'Question Bank', icon: Layers },
  { href: '/ai-engine', label: 'AI Engine', icon: Brain },
  { href: '/analytics', label: 'Analytics', icon: BarChart3 },
  { href: '/gamification', label: 'Gamification', icon: Trophy },
  { href: '/notifications', label: 'Notifications', icon: Bell },
  { href: '/reports', label: 'Reports', icon: FileText },
  { href: '/settings', label: 'Settings', icon: Settings },
];

export default function Sidebar() {
  const pathname = usePathname();
  const { user, clearAuth } = useAuthStore();
  const [collapsed, setCollapsed] = useState(false);

  const handleLogout = () => {
    clearAuth();
    window.location.reload();
  };

  return (
    <aside className={cn(
      'flex flex-col h-screen bg-gray-900 text-white transition-all duration-300 relative',
      collapsed ? 'w-16' : 'w-64'
    )}>
      {/* Toggle */}
      <button onClick={() => setCollapsed(!collapsed)}
        className="absolute -right-3 top-6 z-10 w-6 h-6 bg-gray-900 border border-gray-700 rounded-full flex items-center justify-center text-gray-400 hover:text-white transition">
        {collapsed ? <ChevronRight size={12} /> : <ChevronLeft size={12} />}
      </button>

      {/* Logo */}
      <div className={cn('flex items-center gap-3 px-4 py-5 border-b border-gray-800', collapsed && 'justify-center')}>
        <div className="w-8 h-8 bg-green-500 rounded-lg flex items-center justify-center flex-shrink-0">
          <Sparkles size={16} className="text-white" />
        </div>
        {!collapsed && (
          <div className="overflow-hidden">
            <p className="font-bold text-sm leading-tight">Uganda AI</p>
            <p className="text-xs text-gray-400">Learning System</p>
          </div>
        )}
      </div>

      {/* Nav */}
      <nav className="flex-1 overflow-y-auto scrollbar-thin py-4 space-y-0.5 px-2">
        {navItems.map(({ href, label, icon: Icon }) => {
          const active = pathname === href || pathname.startsWith(href + '/');
          return (
            <Link key={href} href={href} title={collapsed ? label : undefined}
              className={cn(
                'flex items-center gap-3 px-3 py-2.5 rounded-lg text-sm font-medium transition-all',
                active
                  ? 'bg-green-600 text-white shadow-sm'
                  : 'text-gray-400 hover:bg-gray-800 hover:text-white',
                collapsed && 'justify-center'
              )}>
              <Icon size={18} className="flex-shrink-0" />
              {!collapsed && <span className="truncate">{label}</span>}
            </Link>
          );
        })}
      </nav>

      {/* User + Logout */}
      <div className="border-t border-gray-800 p-3">
        {!collapsed && (
          <div className="flex items-center gap-3 px-2 py-2 mb-2">
            <div className="w-8 h-8 bg-green-500 rounded-full flex items-center justify-center text-xs font-bold flex-shrink-0">
              {user ? `${user.first_name?.[0] ?? ''}${user.last_name?.[0] ?? ''}` : 'A'}
            </div>
            <div className="overflow-hidden">
              <p className="text-sm font-medium truncate">{user ? `${user.first_name} ${user.last_name}` : 'Admin'}</p>
              <p className="text-xs text-gray-400 truncate capitalize">{user?.role?.replace('_', ' ') ?? 'Super Admin'}</p>
            </div>
          </div>
        )}
        <button onClick={handleLogout} title={collapsed ? 'Logout' : undefined}
          className={cn(
            'w-full flex items-center gap-3 px-3 py-2 rounded-lg text-sm text-red-400 hover:bg-red-500/10 hover:text-red-300 transition',
            collapsed && 'justify-center'
          )}>
          <LogOut size={16} className="flex-shrink-0" />
          {!collapsed && <span>Logout</span>}
        </button>
      </div>
    </aside>
  );
}
