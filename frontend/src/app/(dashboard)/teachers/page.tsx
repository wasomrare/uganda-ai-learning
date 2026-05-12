'use client';
import { useState } from 'react';
import { useQuery, useQueryClient } from '@tanstack/react-query';
import { teachersApi } from '@/lib/api';
import { Plus, Search, X, Copy, Check, Eye, EyeOff, Loader2, UserCheck } from 'lucide-react';
import { getInitials } from '@/lib/utils';
import type { Teacher } from '@/types';

function CreateTeacherModal({ onClose, onCreated }: {
  onClose: () => void;
  onCreated: (data: { teacher: Teacher; temporary_password: string }) => void;
}) {
  const [form, setForm] = useState({ first_name: '', last_name: '', username: '', email: '', phone: '', qualification: '', specialization: '', experience_years: '0' });
  const [error, setError] = useState('');
  const [loading, setLoading] = useState(false);
  const set = (k: string, v: string) => setForm(f => ({ ...f, [k]: v }));

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!form.first_name || !form.last_name || !form.username) { setError('First name, last name, and username are required.'); return; }
    setError('');
    setLoading(true);
    try {
      const payload: Record<string, unknown> = {
        first_name: form.first_name, last_name: form.last_name, username: form.username,
        experience_years: parseInt(form.experience_years) || 0,
      };
      if (form.email) payload.email = form.email;
      if (form.phone) payload.phone = form.phone;
      if (form.qualification) payload.qualification = form.qualification;
      if (form.specialization) payload.specialization = form.specialization;
      const res = await teachersApi.create(payload);
      onCreated(res.data.data);
    } catch (err: unknown) {
      const e = err as { response?: { data?: { errors?: Record<string, string[]>; message?: string; error?: string } } };
      const errs = e?.response?.data?.errors;
      if (errs) { const first = Object.values(errs)[0]; setError(Array.isArray(first) ? first[0] : String(first)); }
      else setError(e?.response?.data?.message ?? e?.response?.data?.error ?? 'Failed to create teacher.');
    } finally { setLoading(false); }
  };

  return (
    <div className="fixed inset-0 z-50 flex items-center justify-center bg-black/40 px-4">
      <div className="bg-white rounded-2xl shadow-2xl w-full max-w-lg max-h-[90vh] overflow-y-auto">
        <div className="flex items-center justify-between p-6 border-b border-gray-100">
          <h2 className="text-lg font-bold text-gray-900">Add New Teacher</h2>
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
          <div className="grid grid-cols-2 gap-3">
            <div>
              <label className="block text-sm font-medium text-gray-700 mb-1">Username *</label>
              <input value={form.username} onChange={e => set('username', e.target.value)} placeholder="e.g. teacher_john"
                className="w-full px-3 py-2 border border-gray-300 rounded-xl text-sm focus:outline-none focus:ring-2 focus:ring-green-500" />
            </div>
            <div>
              <label className="block text-sm font-medium text-gray-700 mb-1">Email</label>
              <input type="email" value={form.email} onChange={e => set('email', e.target.value)} placeholder="email@school.ug"
                className="w-full px-3 py-2 border border-gray-300 rounded-xl text-sm focus:outline-none focus:ring-2 focus:ring-green-500" />
            </div>
          </div>
          <div className="grid grid-cols-2 gap-3">
            <div>
              <label className="block text-sm font-medium text-gray-700 mb-1">Phone</label>
              <input value={form.phone} onChange={e => set('phone', e.target.value)} placeholder="07XXXXXXXX"
                className="w-full px-3 py-2 border border-gray-300 rounded-xl text-sm focus:outline-none focus:ring-2 focus:ring-green-500" />
            </div>
            <div>
              <label className="block text-sm font-medium text-gray-700 mb-1">Experience (yrs)</label>
              <input type="number" min="0" value={form.experience_years} onChange={e => set('experience_years', e.target.value)}
                className="w-full px-3 py-2 border border-gray-300 rounded-xl text-sm focus:outline-none focus:ring-2 focus:ring-green-500" />
            </div>
          </div>
          <div className="grid grid-cols-2 gap-3">
            <div>
              <label className="block text-sm font-medium text-gray-700 mb-1">Qualification</label>
              <input value={form.qualification} onChange={e => set('qualification', e.target.value)} placeholder="e.g. B.Ed"
                className="w-full px-3 py-2 border border-gray-300 rounded-xl text-sm focus:outline-none focus:ring-2 focus:ring-green-500" />
            </div>
            <div>
              <label className="block text-sm font-medium text-gray-700 mb-1">Specialization</label>
              <input value={form.specialization} onChange={e => set('specialization', e.target.value)} placeholder="e.g. Mathematics"
                className="w-full px-3 py-2 border border-gray-300 rounded-xl text-sm focus:outline-none focus:ring-2 focus:ring-green-500" />
            </div>
          </div>
          <p className="text-xs text-gray-400">A temporary password will be generated automatically.</p>
          <div className="flex gap-3 pt-2">
            <button type="button" onClick={onClose} className="flex-1 py-2.5 border border-gray-300 rounded-xl text-sm font-medium text-gray-600 hover:bg-gray-50 transition">Cancel</button>
            <button type="submit" disabled={loading}
              className="flex-1 flex items-center justify-center gap-2 py-2.5 bg-green-600 hover:bg-green-700 text-white rounded-xl text-sm font-semibold transition disabled:opacity-60">
              {loading && <Loader2 size={14} className="animate-spin" />}
              {loading ? 'Creating…' : 'Create Teacher'}
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
          <p className="text-sm text-gray-500 mt-1">Share these credentials with the teacher.</p>
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

export default function TeachersPage() {
  const qc = useQueryClient();
  const [search, setSearch] = useState('');
  const [showCreate, setShowCreate] = useState(false);
  const [createdResult, setCreatedResult] = useState<{ teacher: Teacher; temporary_password: string } | null>(null);

  const { data, isLoading } = useQuery({
    queryKey: ['teachers', search],
    queryFn: () => teachersApi.list({ search }).then((r) => r.data.data),
  });
  const teachers: Teacher[] = data?.results ?? [];

  return (
    <div className="space-y-5">
      {showCreate && (
        <CreateTeacherModal
          onClose={() => setShowCreate(false)}
          onCreated={(data) => { setShowCreate(false); setCreatedResult(data); qc.invalidateQueries({ queryKey: ['teachers'] }); }}
        />
      )}
      {createdResult && (
        <PasswordRevealModal
          name={`${createdResult.teacher.user.first_name} ${createdResult.teacher.user.last_name}`}
          username={createdResult.teacher.user.username}
          password={createdResult.temporary_password}
          onClose={() => setCreatedResult(null)}
        />
      )}

      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-xl font-bold text-gray-900">Teachers</h1>
          <p className="text-sm text-gray-500">{data?.count ?? 0} registered teachers</p>
        </div>
        <button onClick={() => setShowCreate(true)}
          className="flex items-center gap-2 px-4 py-2 bg-green-600 text-white rounded-xl text-sm font-medium hover:bg-green-700 transition">
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
          : teachers.length === 0
          ? <p className="text-gray-400 text-sm col-span-3 py-8 text-center">No teachers found.</p>
          : teachers.map((t) => (
            <div key={t.id} className="bg-white rounded-2xl p-5 border border-gray-100 shadow-sm hover:shadow-md transition-shadow">
              <div className="flex items-center gap-3">
                <div className="w-10 h-10 bg-purple-100 text-purple-700 rounded-full flex items-center justify-center font-bold text-sm">
                  {getInitials(`${t.user.first_name} ${t.user.last_name}`)}
                </div>
                <div className="flex-1 min-w-0">
                  <p className="font-semibold text-gray-800 truncate">{t.user.first_name} {t.user.last_name}</p>
                  <p className="text-xs text-gray-400 truncate">@{t.user.username} · {t.specialization}</p>
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
