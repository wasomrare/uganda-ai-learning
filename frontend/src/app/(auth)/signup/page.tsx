'use client';
import { useState } from 'react';
import { useRouter } from 'next/navigation';
import Link from 'next/link';
import { useForm } from 'react-hook-form';
import { zodResolver } from '@hookform/resolvers/zod';
import { z } from 'zod';
import { BookOpen, Eye, EyeOff, Loader2 } from 'lucide-react';
import { authApi } from '@/lib/api';
import { useAuthStore } from '@/store/auth';

const schema = z.object({
  first_name: z.string().min(1, 'First name is required'),
  last_name: z.string().min(1, 'Last name is required'),
  username: z.string().min(3, 'Username must be at least 3 characters').regex(/^\S+$/, 'No spaces allowed'),
  email: z.string().email('Invalid email').optional().or(z.literal('')),
  password: z.string().min(6, 'Password must be at least 6 characters'),
  confirm_password: z.string().min(1, 'Please confirm your password'),
  role: z.enum(['student', 'teacher', 'parent']),
}).refine(d => d.password === d.confirm_password, {
  message: 'Passwords do not match',
  path: ['confirm_password'],
});

type SignupForm = z.infer<typeof schema>;

const ROLES = [
  { value: 'student', label: 'Student', desc: 'P.1 – P.7 Learner' },
  { value: 'teacher', label: 'Teacher', desc: 'Classroom Teacher' },
  { value: 'parent', label: 'Parent', desc: 'Parent / Guardian' },
];

export default function SignupPage() {
  const router = useRouter();
  const { setAuth } = useAuthStore();
  const [showPw, setShowPw] = useState(false);
  const [showPw2, setShowPw2] = useState(false);
  const [error, setError] = useState('');

  const { register, handleSubmit, watch, setValue, formState: { errors, isSubmitting } } = useForm<SignupForm>({
    resolver: zodResolver(schema),
    defaultValues: { role: 'student' },
  });

  const selectedRole = watch('role');

  const onSubmit = async (data: SignupForm) => {
    setError('');
    try {
      const res = await authApi.register({
        first_name: data.first_name,
        last_name: data.last_name,
        username: data.username,
        email: data.email || undefined,
        password: data.password,
        confirm_password: data.confirm_password,
        role: data.role,
      });
      const { access, refresh, user } = res.data.data;
      setAuth(user, access, refresh);
      router.push('/dashboard');
    } catch (err: unknown) {
      const e = err as { response?: { data?: { errors?: Record<string, string[]>; message?: string; error?: string } } };
      const errs = e?.response?.data?.errors;
      if (errs && typeof errs === 'object') {
        const first = Object.values(errs)[0];
        setError(Array.isArray(first) ? first[0] : String(first));
      } else {
        setError(e?.response?.data?.message ?? e?.response?.data?.error ?? 'Registration failed. Please try again.');
      }
    }
  };

  return (
    <div className="min-h-screen flex items-center justify-center bg-gradient-to-br from-green-50 via-white to-yellow-50 py-8">
      <div className="w-full max-w-lg px-6">
        {/* Logo */}
        <div className="text-center mb-6">
          <div className="inline-flex items-center justify-center w-14 h-14 bg-green-600 rounded-2xl mb-3 shadow-lg">
            <BookOpen className="w-7 h-7 text-white" />
          </div>
          <h1 className="text-2xl font-bold text-gray-900">Create Your Account</h1>
          <p className="text-sm text-gray-500 mt-1">Uganda Primary AI Learning System</p>
        </div>

        <div className="bg-white rounded-2xl shadow-xl border border-gray-100 p-7">
          {error && (
            <div className="mb-4 p-3 bg-red-50 border border-red-200 rounded-lg text-red-600 text-sm">{error}</div>
          )}

          <form onSubmit={handleSubmit(onSubmit)} className="space-y-4">
            {/* Role selector */}
            <div>
              <label className="block text-sm font-medium text-gray-700 mb-2">I am a…</label>
              <div className="grid grid-cols-3 gap-2">
                {ROLES.map(r => (
                  <button
                    key={r.value}
                    type="button"
                    onClick={() => setValue('role', r.value as 'student' | 'teacher' | 'parent')}
                    className={`p-3 rounded-xl border-2 text-center transition text-sm ${
                      selectedRole === r.value
                        ? 'border-green-500 bg-green-50 text-green-700 font-semibold'
                        : 'border-gray-200 text-gray-600 hover:border-green-300'
                    }`}
                  >
                    <div className="font-medium">{r.label}</div>
                    <div className="text-xs opacity-70 mt-0.5">{r.desc}</div>
                  </button>
                ))}
              </div>
            </div>

            {/* Name row */}
            <div className="grid grid-cols-2 gap-3">
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-1.5">First Name</label>
                <input {...register('first_name')} placeholder="First name"
                  className="w-full px-3 py-2.5 border border-gray-300 rounded-xl text-sm focus:outline-none focus:ring-2 focus:ring-green-500 focus:border-transparent" />
                {errors.first_name && <p className="text-red-500 text-xs mt-1">{errors.first_name.message}</p>}
              </div>
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-1.5">Last Name</label>
                <input {...register('last_name')} placeholder="Last name"
                  className="w-full px-3 py-2.5 border border-gray-300 rounded-xl text-sm focus:outline-none focus:ring-2 focus:ring-green-500 focus:border-transparent" />
                {errors.last_name && <p className="text-red-500 text-xs mt-1">{errors.last_name.message}</p>}
              </div>
            </div>

            {/* Username */}
            <div>
              <label className="block text-sm font-medium text-gray-700 mb-1.5">Username</label>
              <input {...register('username')} placeholder="Choose a username (no spaces)"
                autoComplete="username"
                className="w-full px-4 py-2.5 border border-gray-300 rounded-xl text-sm focus:outline-none focus:ring-2 focus:ring-green-500 focus:border-transparent" />
              {errors.username && <p className="text-red-500 text-xs mt-1">{errors.username.message}</p>}
            </div>

            {/* Email (optional) */}
            <div>
              <label className="block text-sm font-medium text-gray-700 mb-1.5">Email <span className="text-gray-400 font-normal">(optional)</span></label>
              <input {...register('email')} type="email" placeholder="your@email.com"
                autoComplete="email"
                className="w-full px-4 py-2.5 border border-gray-300 rounded-xl text-sm focus:outline-none focus:ring-2 focus:ring-green-500 focus:border-transparent" />
              {errors.email && <p className="text-red-500 text-xs mt-1">{errors.email.message}</p>}
            </div>

            {/* Password row */}
            <div className="grid grid-cols-2 gap-3">
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-1.5">Password</label>
                <div className="relative">
                  <input {...register('password')} type={showPw ? 'text' : 'password'} placeholder="Min 6 chars"
                    autoComplete="new-password"
                    className="w-full px-3 py-2.5 pr-9 border border-gray-300 rounded-xl text-sm focus:outline-none focus:ring-2 focus:ring-green-500 focus:border-transparent" />
                  <button type="button" onClick={() => setShowPw(!showPw)}
                    className="absolute right-2.5 top-1/2 -translate-y-1/2 text-gray-400">
                    {showPw ? <EyeOff size={14} /> : <Eye size={14} />}
                  </button>
                </div>
                {errors.password && <p className="text-red-500 text-xs mt-1">{errors.password.message}</p>}
              </div>
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-1.5">Confirm Password</label>
                <div className="relative">
                  <input {...register('confirm_password')} type={showPw2 ? 'text' : 'password'} placeholder="Repeat password"
                    autoComplete="new-password"
                    className="w-full px-3 py-2.5 pr-9 border border-gray-300 rounded-xl text-sm focus:outline-none focus:ring-2 focus:ring-green-500 focus:border-transparent" />
                  <button type="button" onClick={() => setShowPw2(!showPw2)}
                    className="absolute right-2.5 top-1/2 -translate-y-1/2 text-gray-400">
                    {showPw2 ? <EyeOff size={14} /> : <Eye size={14} />}
                  </button>
                </div>
                {errors.confirm_password && <p className="text-red-500 text-xs mt-1">{errors.confirm_password.message}</p>}
              </div>
            </div>

            <button type="submit" disabled={isSubmitting}
              className="w-full flex items-center justify-center gap-2 py-3 bg-green-600 hover:bg-green-700 text-white font-semibold rounded-xl transition disabled:opacity-60 disabled:cursor-not-allowed mt-2">
              {isSubmitting && <Loader2 size={16} className="animate-spin" />}
              {isSubmitting ? 'Creating account…' : 'Create Account'}
            </button>
          </form>

          <p className="text-center text-sm text-gray-500 mt-5">
            Already have an account?{' '}
            <Link href="/login" className="text-green-600 font-medium hover:underline">Sign in</Link>
          </p>
        </div>

        <p className="text-center text-xs text-gray-400 mt-5">
          Uganda Primary AI Learning System &copy; 2026 designed by twiina
        </p>
      </div>
    </div>
  );
}
