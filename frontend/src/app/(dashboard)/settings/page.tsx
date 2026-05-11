'use client';
import { useState } from 'react';
import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query';
import { settingsApi } from '@/lib/api';
import { Save, Loader2 } from 'lucide-react';

export default function SettingsPage() {
  const qc = useQueryClient();
  const { data, isLoading } = useQuery({
    queryKey: ['system-settings'],
    queryFn: () => settingsApi.list().then((r: any) => r.data.data),
  });

  const updateMutation = useMutation({
    mutationFn: (payload: Record<string, string>) => settingsApi.update(payload),
    onSuccess: () => qc.invalidateQueries({ queryKey: ['system-settings'] }),
  });

  const settings: Array<{ key: string; value: string; description: string }> = data?.results ?? [];
  const [edits, setEdits] = useState<Record<string, string>>({});

  const getValue = (key: string) => edits[key] ?? settings.find((s) => s.key === key)?.value ?? '';

  const handleSave = () => {
    updateMutation.mutate(edits);
    setEdits({});
  };

  const hasPendingEdits = Object.keys(edits).length > 0;

  return (
    <div className="space-y-5">
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-xl font-bold text-gray-900">System Settings</h1>
          <p className="text-sm text-gray-500">Global configuration for the platform</p>
        </div>
        {hasPendingEdits && (
          <button
            onClick={handleSave}
            disabled={updateMutation.isPending}
            className="flex items-center gap-2 px-4 py-2 bg-green-600 text-white rounded-xl text-sm font-medium hover:bg-green-700 transition"
          >
            {updateMutation.isPending ? <Loader2 size={14} className="animate-spin" /> : <Save size={14} />}
            Save Changes
          </button>
        )}
      </div>

      {updateMutation.isSuccess && (
        <div className="px-4 py-3 bg-green-50 border border-green-200 rounded-xl text-sm text-green-700">
          Settings saved successfully.
        </div>
      )}

      <div className="bg-white rounded-2xl border border-gray-100 shadow-sm overflow-hidden divide-y divide-gray-50">
        {isLoading
          ? Array.from({ length: 6 }).map((_, i) => (
            <div key={i} className="px-5 py-4 space-y-2">
              <div className="h-3 bg-gray-100 rounded w-1/4 animate-pulse" />
              <div className="h-8 bg-gray-100 rounded animate-pulse" />
            </div>
          ))
          : settings.map((s) => (
            <div key={s.key} className="px-5 py-4">
              <label className="block text-sm font-medium text-gray-700 mb-1">
                {s.key.replace(/_/g, ' ').replace(/\b\w/g, (c) => c.toUpperCase())}
              </label>
              {s.description && <p className="text-xs text-gray-400 mb-2">{s.description}</p>}
              <input
                type="text"
                value={getValue(s.key)}
                onChange={(e) => setEdits((prev) => ({ ...prev, [s.key]: e.target.value }))}
                className="w-full px-3 py-2 border border-gray-200 rounded-xl text-sm focus:outline-none focus:ring-2 focus:ring-green-500"
              />
            </div>
          ))
        }
      </div>
    </div>
  );
}
