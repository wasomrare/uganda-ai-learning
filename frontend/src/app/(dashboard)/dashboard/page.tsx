'use client';
import { useQuery } from '@tanstack/react-query';
import { dashboardApi, aiApi } from '@/lib/api';
import {
  Users, GraduationCap, School, ClipboardList,
  TrendingUp, Sparkles, Activity, Trophy, ArrowUp, ArrowDown,
} from 'lucide-react';
import { AreaChart, Area, XAxis, YAxis, CartesianGrid, Tooltip, ResponsiveContainer, BarChart, Bar, PieChart, Pie, Cell } from 'recharts';

const COLORS = ['#22c55e', '#3b82f6', '#f59e0b', '#ef4444', '#8b5cf6'];

function StatCard({
  title, value, icon: Icon, color, change, suffix = '',
}: {
  title: string; value: number | string; icon: React.ElementType;
  color: string; change?: number; suffix?: string;
}) {
  return (
    <div className="bg-white rounded-2xl p-5 border border-gray-100 shadow-sm hover:shadow-md transition-shadow">
      <div className="flex items-start justify-between">
        <div>
          <p className="text-xs font-medium text-gray-500 uppercase tracking-wider">{title}</p>
          <p className="text-2xl font-bold text-gray-900 mt-1">{value}{suffix}</p>
          {change !== undefined && (
            <p className={`flex items-center gap-1 text-xs mt-1.5 ${change >= 0 ? 'text-green-600' : 'text-red-500'}`}>
              {change >= 0 ? <ArrowUp size={10} /> : <ArrowDown size={10} />}
              {Math.abs(change)}% from last term
            </p>
          )}
        </div>
        <div className={`w-10 h-10 ${color} rounded-xl flex items-center justify-center`}>
          <Icon size={20} className="text-white" />
        </div>
      </div>
    </div>
  );
}

const mockWeeklyActivity = [
  { day: 'Mon', sessions: 145, assessments: 32 },
  { day: 'Tue', sessions: 189, assessments: 45 },
  { day: 'Wed', sessions: 167, assessments: 38 },
  { day: 'Thu', sessions: 210, assessments: 62 },
  { day: 'Fri', sessions: 198, assessments: 55 },
  { day: 'Sat', sessions: 88, assessments: 20 },
  { day: 'Sun', sessions: 52, assessments: 12 },
];

const mockSubjectPerf = [
  { subject: 'Mathematics', avg: 72 },
  { subject: 'English', avg: 78 },
  { subject: 'Science', avg: 65 },
  { subject: 'SST', avg: 81 },
  { subject: 'Luganda', avg: 69 },
];

const mockClassDist = [
  { name: 'P1-P2', value: 24 },
  { name: 'P3-P4', value: 38 },
  { name: 'P5-P6', value: 31 },
  { name: 'P7', value: 7 },
];

export default function DashboardPage() {
  const { data: dashboard, isLoading } = useQuery({
    queryKey: ['admin-dashboard'],
    queryFn: () => dashboardApi.admin().then(r => r.data.data),
  });

  const { data: aiStatus } = useQuery({
    queryKey: ['ai-status'],
    queryFn: () => aiApi.status().then(r => r.data.data),
    refetchInterval: 60_000,
  });

  return (
    <div className="space-y-6">
      {/* Page heading */}
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-xl font-bold text-gray-900">Dashboard</h1>
          <p className="text-sm text-gray-500">Uganda Primary AI Learning System — Overview</p>
        </div>
        <div className={`flex items-center gap-2 px-3 py-1.5 rounded-full text-xs font-medium ${
          aiStatus?.ollama?.available ? 'bg-green-50 text-green-700' : 'bg-yellow-50 text-yellow-700'
        }`}>
          <Sparkles size={12} />
          AI: {aiStatus?.primary_provider ?? 'checking…'} {aiStatus?.ollama?.available ? '✓' : '(fallback)'}
        </div>
      </div>

      {/* Stats grid */}
      {isLoading ? (
        <div className="grid grid-cols-2 lg:grid-cols-4 gap-4">
          {Array.from({ length: 4 }).map((_, i) => (
            <div key={i} className="bg-white rounded-2xl p-5 border border-gray-100 h-28 animate-pulse" />
          ))}
        </div>
      ) : (
        <div className="grid grid-cols-2 lg:grid-cols-4 gap-4">
          <StatCard title="Total Students" value={dashboard?.total_students ?? 0} icon={Users} color="bg-blue-500" change={5} />
          <StatCard title="Teachers" value={dashboard?.total_teachers ?? 0} icon={GraduationCap} color="bg-purple-500" change={2} />
          <StatCard title="Classes" value={dashboard?.total_classes ?? 0} icon={School} color="bg-amber-500" />
          <StatCard title="Avg Score" value={dashboard?.average_score ?? 0} icon={TrendingUp} color="bg-green-500" suffix="%" change={3} />
        </div>
      )}

      {/* Secondary stats */}
      <div className="grid grid-cols-2 lg:grid-cols-4 gap-4">
        <StatCard title="Active Assessments" value={dashboard?.active_assessments ?? 0} icon={ClipboardList} color="bg-indigo-500" />
        <StatCard title="AI Questions Generated" value={dashboard?.ai_questions_generated ?? 0} icon={Sparkles} color="bg-pink-500" />
        <StatCard title="Daily Active Students" value={dashboard?.daily_active_students ?? 0} icon={Activity} color="bg-teal-500" />
        <StatCard title="Badges Earned" value={dashboard?.badges_earned ?? 0} icon={Trophy} color="bg-orange-500" />
      </div>

      {/* Charts row */}
      <div className="grid grid-cols-1 lg:grid-cols-3 gap-4">
        {/* Weekly Activity */}
        <div className="lg:col-span-2 bg-white rounded-2xl p-5 border border-gray-100 shadow-sm">
          <h3 className="text-sm font-semibold text-gray-800 mb-4">Weekly Activity</h3>
          <ResponsiveContainer width="100%" height={200}>
            <AreaChart data={mockWeeklyActivity} margin={{ top: 0, right: 0, left: -20, bottom: 0 }}>
              <defs>
                <linearGradient id="sessions" x1="0" y1="0" x2="0" y2="1">
                  <stop offset="5%" stopColor="#22c55e" stopOpacity={0.15} />
                  <stop offset="95%" stopColor="#22c55e" stopOpacity={0} />
                </linearGradient>
              </defs>
              <CartesianGrid strokeDasharray="3 3" stroke="#f0f0f0" />
              <XAxis dataKey="day" tick={{ fontSize: 11 }} />
              <YAxis tick={{ fontSize: 11 }} />
              <Tooltip />
              <Area type="monotone" dataKey="sessions" stroke="#22c55e" fill="url(#sessions)" strokeWidth={2} name="Study Sessions" />
              <Area type="monotone" dataKey="assessments" stroke="#3b82f6" fill="none" strokeWidth={2} name="Assessments" />
            </AreaChart>
          </ResponsiveContainer>
        </div>

        {/* Class Distribution */}
        <div className="bg-white rounded-2xl p-5 border border-gray-100 shadow-sm">
          <h3 className="text-sm font-semibold text-gray-800 mb-4">Student Distribution</h3>
          <ResponsiveContainer width="100%" height={160}>
            <PieChart>
              <Pie data={mockClassDist} cx="50%" cy="50%" innerRadius={45} outerRadius={70} paddingAngle={3} dataKey="value">
                {mockClassDist.map((_, i) => <Cell key={i} fill={COLORS[i % COLORS.length]} />)}
              </Pie>
              <Tooltip />
            </PieChart>
          </ResponsiveContainer>
          <div className="space-y-1.5 mt-3">
            {mockClassDist.map((d, i) => (
              <div key={d.name} className="flex items-center justify-between text-xs">
                <div className="flex items-center gap-1.5">
                  <div className="w-2 h-2 rounded-full" style={{ background: COLORS[i] }} />
                  <span className="text-gray-600">{d.name}</span>
                </div>
                <span className="font-medium text-gray-800">{d.value}%</span>
              </div>
            ))}
          </div>
        </div>
      </div>

      {/* Subject Performance */}
      <div className="bg-white rounded-2xl p-5 border border-gray-100 shadow-sm">
        <h3 className="text-sm font-semibold text-gray-800 mb-4">Average Score by Subject (This Term)</h3>
        <ResponsiveContainer width="100%" height={160}>
          <BarChart data={mockSubjectPerf} margin={{ top: 0, right: 0, left: -20, bottom: 0 }}>
            <CartesianGrid strokeDasharray="3 3" stroke="#f0f0f0" />
            <XAxis dataKey="subject" tick={{ fontSize: 11 }} />
            <YAxis tick={{ fontSize: 11 }} domain={[0, 100]} />
            <Tooltip formatter={(v) => [`${v}%`, 'Average']} />
            <Bar dataKey="avg" radius={[4, 4, 0, 0]}>
              {mockSubjectPerf.map((d, i) => (
                <Cell key={i} fill={d.avg >= 75 ? '#22c55e' : d.avg >= 60 ? '#f59e0b' : '#ef4444'} />
              ))}
            </Bar>
          </BarChart>
        </ResponsiveContainer>
      </div>
    </div>
  );
}
