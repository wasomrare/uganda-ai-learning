import { type ClassValue, clsx } from 'clsx';
import { twMerge } from 'tailwind-merge';

export function cn(...inputs: ClassValue[]) {
  return twMerge(clsx(inputs));
}

export function formatDate(date: string | Date): string {
  return new Date(date).toLocaleDateString('en-UG', {
    day: '2-digit', month: 'short', year: 'numeric',
  });
}

export function formatTime(date: string | Date): string {
  return new Date(date).toLocaleTimeString('en-UG', {
    hour: '2-digit', minute: '2-digit',
  });
}

export function getInitials(name: string): string {
  return name.split(' ').map(n => n[0]).join('').toUpperCase().slice(0, 2);
}

export function getGradeColor(grade: string): string {
  const map: Record<string, string> = {
    D1: 'text-green-600 bg-green-50',
    D2: 'text-green-500 bg-green-50',
    C3: 'text-yellow-600 bg-yellow-50',
    C4: 'text-orange-500 bg-orange-50',
    C5: 'text-orange-600 bg-orange-50',
    C6: 'text-red-400 bg-red-50',
    P7: 'text-red-500 bg-red-50',
    P8: 'text-red-600 bg-red-50',
    F9: 'text-red-700 bg-red-50',
  };
  return map[grade] ?? 'text-gray-600 bg-gray-50';
}

export function getMasteryColor(score: number): string {
  if (score >= 90) return 'text-green-600';
  if (score >= 75) return 'text-lime-600';
  if (score >= 60) return 'text-yellow-600';
  if (score >= 40) return 'text-orange-500';
  return 'text-red-500';
}
