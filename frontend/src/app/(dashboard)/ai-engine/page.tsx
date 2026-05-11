'use client';
import { useQuery } from '@tanstack/react-query';
import { aiApi } from '@/lib/api';
import { Brain, CheckCircle, XCircle, Loader2 } from 'lucide-react';

export default function AiEnginePage() {
  const { data, isLoading, refetch } = useQuery({
    queryKey: ['ai-status'],
    queryFn: () => aiApi.status().then((r: any) => r.data.data),
    refetchInterval: 30000,
  });

  const engines: Array<{ key: string; label: string; description: string }> = [
    { key: 'ollama', label: 'Ollama (Local)', description: 'Primary on-premise AI engine running locally' },
    { key: 'openai', label: 'OpenAI GPT-4', description: 'Fallback cloud AI — requires API key' },
    { key: 'gemini', label: 'Google Gemini', description: 'Secondary fallback — requires API key' },
  ];

  return (
    <div className="space-y-5">
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-xl font-bold text-gray-900">AI Engine Status</h1>
          <p className="text-sm text-gray-500">Primary → Ollama → OpenAI → Gemini → Rule-based fallback</p>
        </div>
        <button onClick={() => refetch()}
          className="flex items-center gap-2 px-4 py-2 text-sm border border-gray-200 rounded-xl hover:bg-gray-50 transition">
          <Loader2 size={14} className={isLoading ? 'animate-spin' : ''} /> Refresh
        </button>
      </div>

      <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
        {engines.map(({ key, label, description }) => {
          const alive = data?.[key]?.alive ?? false;
          const model = data?.[key]?.model ?? 'N/A';
          return (
            <div key={key} className="bg-white rounded-2xl border border-gray-100 shadow-sm p-5">
              <div className="flex items-center justify-between mb-3">
                <div className="w-10 h-10 bg-purple-50 rounded-xl flex items-center justify-center">
                  <Brain size={18} className="text-purple-600" />
                </div>
                {isLoading
                  ? <Loader2 size={16} className="animate-spin text-gray-300" />
                  : alive
                    ? <CheckCircle size={18} className="text-green-500" />
                    : <XCircle size={18} className="text-red-400" />
                }
              </div>
              <p className="font-semibold text-sm text-gray-900">{label}</p>
              <p className="text-xs text-gray-500 mt-1">{description}</p>
              <div className={`mt-3 inline-flex items-center px-2 py-0.5 rounded-full text-xs font-medium ${alive ? 'bg-green-50 text-green-700' : 'bg-red-50 text-red-600'}`}>
                {isLoading ? 'Checking...' : alive ? `Online · ${model}` : 'Offline'}
              </div>
            </div>
          );
        })}
      </div>

      {data?.active_engine && (
        <div className="bg-green-50 border border-green-200 rounded-2xl p-4 text-sm text-green-800">
          <strong>Active engine:</strong> {data.active_engine}
        </div>
      )}
    </div>
  );
}
