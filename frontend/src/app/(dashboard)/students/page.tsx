'use client';
import { useState } from 'react';
import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query';
import { studentsApi, classesApi } from '@/lib/api';
import { Users, Plus, Search, ToggleLeft, ToggleRight, Loader2, UserCheck, UserX, X, Copy, Check, Eye, EyeOff } from 'lucide-react';
import { cn, formatDate, getInitials } from '@/lib/utils';
import type { Student } from '@/types';

function CreateStudentModal({ classes, onClose, onCreated }: {
  classes: { id: string; name: string; class_level: string }[];
  onClose: () => void;
  onCreated: (data: { student: Student; temporary_password: string }) => void;
}) {
  const [form, setForm] = useState({ first_name: '', last_name: '', username: '', class_id: '', gender: '', stream: '', date_of_birth: '' });
  const [error, setError] = useState('');
  const [loading, setLoading] = useState(false);
  const set = (k: string, v: string) => setForm(f => ({ ...f, [k]: v }));

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!form.first_name || !form.last_name || !form.username) { setError('First name, last name, and username are required.'); return; }
    setError('');
    setLoading(true);
    try {
      const payload: Record<string, string> = { first_name: form.first_name, last_name: form.last_name, username: form.username };
      if (form.class_id) payload.class_id = form.class_id;
      if (form.gender) payload.gender = form.gender;
      if (form.stream) payload.stream = form.stream;
      if (form.date_of_birth) payload.date_of_birth = form.date_of_birth;
      const res = await studentsApi.create(payload);
      onCreated(res.data.data);
    } catch (err: unknown) {
      const e = err as { response?: { data?: { errors?: Record<string, string[]>; message?: string; error?: string } } };
      const errs = e?.response?.data?.errors;
      if (errs) { const first = Object.values(errs)[0]; setError(Array.isArray(first) ? first[0] : String(first)); }
      else setError(e?.response?.data?.message ?? e?.response?.data?.error ?? 'Failed to create student.');
    } finally { setLoading(false); }
  };

  return (
    <div className="fixed inset-0 z-50 flex items-center justify-center bg-black/40 px-4">
      <div className="bg-white rounded-2xl shadow-2xl w-full max-w-lg max-h-[90vh] overflow-y-auto">
        <div className="flex items-center justify-between p-6 border-b border-gray-100">
          <h2 className="text-lg font-bold text-gray-900">Add New Student</h2>
          <button onClick={onClose} className="p-1.5 text-gray-400 hover:text-gray-600 hover:bg-gray-100 rounded-lg"><X size={18} /></button>
        </div>
        <form onSubmit={handleSubmit} className="p-6 space-y-4">
          {error && <div className="p-3 bg-red-50 border border-red-200 rounded-lg text-red-600 text-sm">{error}</div>}
          <div className="grid grid-cols-2 gap-3">
            <div>
              <label className="block text-sm font-medium text-gray-700 mb-1">First Name *</label>
              <input value={form.first_name} onChange={e => set('first_name', e.target.value)} placeholder="First name"
                className="w-full px-3 py-2 border border-gray-300 rounded-xl text-sm focus:outline-none focus:ring-2 focus:ring-green-500" />
            </div>
            <div>
              <label className="block text-sm font-medium text-gray-700 mb-1">Last Name *</label>
              <input value={form.last_name} onChange={e => set('last_name', e.target.value)} placeholder="Last name"
                className="w-full px-3 py-2 border border-gray-300 rounded-xl text-sm focus:outline-none focus:ring-2 focus:ring-green-500" />
            </div>
          </div>
          <div>
            <label className="block text-sm font-medium text-gray-700 mb-1">Username *</label>
            <input value={form.username} onChange={e => set('username', e.target.value)} placeholder="e.g. john_doe"
              className="w-full px-3 py-2 border border-gray-300 rounded-xl text-sm focus:outline-none focus:ring-2 focus:ring-green-500" />
          </div>
          <div className="grid grid-cols-2 gap-3">
            <div>
              <label className="block text-sm font-medium text-gray-700 mb-1">Class</label>
              <select value={form.class_id} onChange={e => set('class_id', e.target.value)}
                className="w-full px-3 py-2 border border-gray-300 rounded-xl text-sm focus:outline-none focus:ring-2 focus:ring-green-500 bg-white">
                <option value="">Select class</option>
                {classes.map(c => <option key={c.id} value={c.id}>{c.name}</option>)}
              </select>
            </div>
            <div>
              <label className="block text-sm font-medium text-gray-700 mb-1">Gender</label>
              <select value={form.gender} onChange={e => set('gender', e.target.value)}
                className="w-full px-3 py-2 border border-gray-300 rounded-xl text-sm focus:outline-none focus:ring-2 focus:ring-green-500 bg-white">
                <option value="">Select gender</option>
                <option value="male">Male</option>
                <option value="female">Female</option>
              </select>
            </div>
          </div>
          <div className="grid grid-cols-2 gap-3">
            <div>
              <label className="block text-sm font-medium text-gray-700 mb-1">Stream</label>
              <input value={form.stream} onChange={e => set('stream', e.target.value)} placeholder="e.g. A, B"
                className="w-full px-3 py-2 border border-gray-300 rounded-xl text-sm focus:outline-none focus:ring-2 focus:ring-green-500" />
            </div>
            <div>
              <label className="block text-sm font-medium text-gray-700 mb-1">Date of Birth</label>
              <input type="date" value={form.date_of_birth} onChange={e => set('date_of_birth', e.target.value)}
                className="w-full px-3 py-2 border border-gray-300 rounded-xl text-sm focus:outline-none focus:ring-2 focus:ring-green-500" />
            </div>
          </div>
          <p className="text-xs text-gray-400">A temporary password will be generated automatically.</p>
          <div className="flex gap-3 pt-2">
            <button type="button" onClick={onClose} className="flex-1 py-2.5 border border-gray-300 rounded-xl text-sm font-medium text-gray-600 hover:bg-gray-50 transition">Cancel</button>
            <button type="submit" disabled={loading}
              className="flex-1 flex items-center justify-center gap-2 py-2.5 bg-green-600 hover:bg-green-700 text-white rounded-xl text-sm font-semibold transition disabled:opacity-60">
              {loading && <Loader2 size={14} className="animate-spin" />}
              {loading ? 'Creating…' : 'Create Student'}
            </button>
          </div>
        </form>
      </div>
    </div>
  );
}

function PasswordRevealModal({ name, username, password, onClose }: { name: string; username: string; password: string; onClose: () => void }) {
  const [copied, setCopied] = useState(false);
  const [show, setShow] = useState(false);
  const copy = () => { navigator.clipboard.writeText(password); setCopied(true); setTimeout(() => setCopied(false), 2000); };
  return (
    <div className="fixed inset-0 z-50 flex items-center justify-center bg-black/40 px-4">
      <div className="bg-white rounded-2xl shadow-2xl w-full max-w-sm p-6">
        <div className="text-center mb-4">
          <div className="w-12 h-12 bg-green-100 rounded-full flex items-center justify-center mx-auto mb-3">
            <UserCheck size={22} className="text-green-600" />
          </div>
          <h2 className="text-lg font-bold text-gray-900">{name} created!</h2>
          <p className="text-sm text-gray-500 mt-1">Share these login credentials with the student.</p>
        </div>
        <div className="bg-gray-50 rounded-xl p-4 space-y-3 mb-4">
          <div><p className="text-xs text-gray-400 mb-0.5">Username</p><p className="font-mono text-sm font-semibold text-gray-800">{username}</p></div>
          <div>
            <p className="text-xs text-gray-400 mb-0.5">Temporary Password</p>
            <div className="flex items-center gap-2">
              <p className="font-mono text-sm font-semibold text-gray-800 flex-1">{show ? password : '••••••••••'}</p>
              <button onClick={() => setShow(!show)} className="text-gray-400 hover:text-gray-600">{show ? <EyeOff size={14} /> : <Eye size={14} />}</button>
              <button onClick={copy} className="text-gray-400 hover:text-green-600 transition">{copied ? <Check size={14} className="text-green-500" /> : <Copy size={14} />}</button>
            </div>
          </div>
        </div>
        <p className="text-xs text-amber-600 bg-amber-50 border border-amber-200 rounded-lg px-3 py-2 mb-4">⚠ Save this password now. It won&apos;t be shown again.</p>
        <button onClick={onClose} className="w-full py-2.5 bg-green-600 hover:bg-green-700 text-white rounded-xl text-sm font-semibold transition">Done</button>
      </div>
    </div>
  );
}

export default function StudentsPage() {
  const qc = useQueryClient();
  const [search, setSearch] = useState('');
  const [classFilter, setClassFilter] = useState('');
  const [page, setPage] = useState(1);
  const [showCreate, setShowCreate] = useState(false);
  const [createdResult, setCreatedResult] = useState<{ student: Student; temporary_password: string } | null>(null);

  const { data, isLoading } = useQuery({
    queryKey: ['students', search, classFilter, page],
    queryFn: () => studentsApi.list({ search, class_level: classFilter, page }).then(r => r.data.data),
    placeholderData: (prev) => prev,
  });

  const { data: classes } = useQuery({
    queryKey: ['classes'],
    queryFn: () => classesApi.list().then(r => r.data.data.results),
  });

  const toggleMutation = useMutation({
    mutationFn: (id: string) => studentsApi.toggleActive(id),
    onSuccess: () => qc.invalidateQueries({ queryKey: ['students'] }),
  });

  const students: Student[] = data?.results ?? [];
  const total = data?.count ?? 0;

  return (
    <div className="space-y-5">
      {showCreate && (
        <CreateStudentModal
          classes={classes ?? []}
          onClose={() => setShowCreate(false)}
          onCreated={(data) => { setShowCreate(false); setCreatedResult(data); qc.invalidateQueries({ queryKey: ['students'] }); }}
        />
      )}
      {createdResult && (
        <PasswordRevealModal
          name={`${createdResult.student.user.first_name} ${createdResult.student.user.last_name}`}
          username={createdResult.student.user.username}
          password={createdResult.temporary_password}
          onClose={() => setCreatedResult(null)}
        />
      )}

      {/* Header */}
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-xl font-bold text-gray-900">Students</h1>
          <p className="text-sm text-gray-500">{total} total enrolled students</p>
        </div>
        <button onClick={() => setShowCreate(true)}
          className="flex items-center gap-2 px-4 py-2 bg-green-600 text-white rounded-xl text-sm font-medium hover:bg-green-700 transition">
          <Plus size={16} /> Add Student
        </button>
      </div>

      {/* Filters */}
      <div className="flex flex-wrap gap-3">
        <div className="relative flex-1 min-w-48">
          <Search size={14} className="absolute left-3 top-1/2 -translate-y-1/2 text-gray-400" />
          <input value={search} onChange={e => { setSearch(e.target.value); setPage(1); }}
            placeholder="Search by name or admission no…"
            className="w-full pl-8 pr-4 py-2 border border-gray-200 rounded-xl text-sm focus:outline-none focus:ring-2 focus:ring-green-500" />
        </div>
        <select value={classFilter} onChange={e => { setClassFilter(e.target.value); setPage(1); }}
          className="px-3 py-2 border border-gray-200 rounded-xl text-sm focus:outline-none focus:ring-2 focus:ring-green-500 bg-white">
          <option value="">All Classes</option>
          {['P1','P2','P3','P4','P5','P6','P7'].map(l => (
            <option key={l} value={l}>{l}</option>
          ))}
        </select>
      </div>

      {/* Table */}
      <div className="bg-white rounded-2xl border border-gray-100 shadow-sm overflow-hidden">
        <div className="overflow-x-auto">
          <table className="w-full text-sm">
            <thead>
              <tr className="border-b border-gray-100 bg-gray-50">
                <th className="text-left px-5 py-3 text-xs font-semibold text-gray-500 uppercase tracking-wider">Student</th>
                <th className="text-left px-5 py-3 text-xs font-semibold text-gray-500 uppercase tracking-wider">Admission No.</th>
                <th className="text-left px-5 py-3 text-xs font-semibold text-gray-500 uppercase tracking-wider">Class</th>
                <th className="text-left px-5 py-3 text-xs font-semibold text-gray-500 uppercase tracking-wider">Gender</th>
                <th className="text-left px-5 py-3 text-xs font-semibold text-gray-500 uppercase tracking-wider">Enrolled</th>
                <th className="text-left px-5 py-3 text-xs font-semibold text-gray-500 uppercase tracking-wider">Status</th>
                <th className="px-5 py-3" />
              </tr>
            </thead>
            <tbody className="divide-y divide-gray-50">
              {isLoading
                ? Array.from({ length: 8 }).map((_, i) => (
                  <tr key={i}><td colSpan={7} className="px-5 py-4"><div className="h-4 bg-gray-100 rounded animate-pulse" /></td></tr>
                ))
                : students.length === 0
                ? <tr><td colSpan={7} className="text-center py-12 text-gray-400">No students found.</td></tr>
                : students.map((s) => (
                  <tr key={s.id} className="hover:bg-gray-50 transition-colors">
                    <td className="px-5 py-3.5">
                      <div className="flex items-center gap-3">
                        <div className="w-8 h-8 bg-blue-100 text-blue-700 rounded-full flex items-center justify-center text-xs font-bold flex-shrink-0">
                          {getInitials(`${s.user.first_name} ${s.user.last_name}`)}
                        </div>
                        <div>
                          <p className="font-medium text-gray-800">{s.user.first_name} {s.user.last_name}</p>
                          <p className="text-xs text-gray-400">@{s.user.username}</p>
                        </div>
                      </div>
                    </td>
                    <td className="px-5 py-3.5 text-gray-600 font-mono text-xs">{s.admission_number}</td>
                    <td className="px-5 py-3.5">
                      <span className="px-2 py-0.5 bg-blue-50 text-blue-700 rounded-full text-xs font-medium">
                        {s.current_class?.name ?? '—'}
                      </span>
                    </td>
                    <td className="px-5 py-3.5 text-gray-600">{s.gender === 'M' ? 'Male' : 'Female'}</td>
                    <td className="px-5 py-3.5 text-gray-500 text-xs">{formatDate(s.created_at)}</td>
                    <td className="px-5 py-3.5">
                      <span className={cn('inline-flex items-center gap-1 px-2 py-0.5 rounded-full text-xs font-medium',
                        s.is_active ? 'bg-green-50 text-green-700' : 'bg-red-50 text-red-600')}>
                        {s.is_active ? <UserCheck size={10} /> : <UserX size={10} />}
                        {s.is_active ? 'Active' : 'Inactive'}
                      </span>
                    </td>
                    <td className="px-5 py-3.5">
                      <button onClick={() => toggleMutation.mutate(s.id)}
                        disabled={toggleMutation.isPending}
                        className="p-1.5 text-gray-400 hover:text-gray-600 hover:bg-gray-100 rounded-lg transition"
                        title={s.is_active ? 'Deactivate' : 'Activate'}>
                        {toggleMutation.isPending ? <Loader2 size={14} className="animate-spin" /> : s.is_active ? <ToggleRight size={16} className="text-green-500" /> : <ToggleLeft size={16} />}
                      </button>
                    </td>
                  </tr>
                ))
              }
            </tbody>
          </table>
        </div>

        {/* Pagination */}
        {total > 20 && (
          <div className="flex items-center justify-between px-5 py-3 border-t border-gray-100">
            <p className="text-xs text-gray-500">Showing {Math.min((page-1)*20+1, total)}–{Math.min(page*20, total)} of {total}</p>
            <div className="flex gap-2">
              <button onClick={() => setPage(p => Math.max(1, p-1))} disabled={page === 1}
                className="px-3 py-1 text-xs border border-gray-200 rounded-lg disabled:opacity-40 hover:bg-gray-50">Previous</button>
              <button onClick={() => setPage(p => p+1)} disabled={page * 20 >= total}
                className="px-3 py-1 text-xs border border-gray-200 rounded-lg disabled:opacity-40 hover:bg-gray-50">Next</button>
            </div>
          </div>
        )}
      </div>
    </div>
  );
}
