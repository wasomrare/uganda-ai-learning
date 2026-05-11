export interface User {
  id: string;
  username: string;
  email: string;
  first_name: string;
  last_name: string;
  full_name: string;
  role: 'super_admin' | 'teacher' | 'student' | 'parent';
  is_verified: boolean;
  avatar?: string;
}

export interface Student {
  id: string;
  user: User;
  admission_number: string;
  current_class: SchoolClass;
  date_of_birth: string;
  gender: 'M' | 'F';
  is_active: boolean;
  created_at: string;
}

export interface Teacher {
  id: string;
  user: User;
  employee_id: string;
  qualification: string;
  specialization: string;
  is_active: boolean;
}

export interface SchoolClass {
  id: string;
  name: string;
  level: string;
  stream: string;
  academic_year: number;
  term: number;
  student_count: number;
  class_teacher?: Teacher;
}

export interface Subject {
  id: string;
  name: string;
  code: string;
  category: string;
  class_levels: string[];
  icon: string;
  color: string;
}

export interface Assessment {
  id: string;
  title: string;
  assessment_type: string;
  class_level: string;
  subject: Subject;
  school_class: SchoolClass;
  term: number;
  total_marks: number;
  duration_minutes: number;
  status: 'draft' | 'active' | 'closed';
  question_count: number;
  attempt_count: number;
  average_score?: number;
  created_at: string;
}

export interface Question {
  id: string;
  question_type: string;
  question_text: string;
  marks: number;
  difficulty: 'easy' | 'medium' | 'hard';
  class_level: string;
  subject: Subject;
  is_approved: boolean;
  options?: MCQOption[];
}

export interface MCQOption {
  id: string;
  option_label: string;
  option_text: string;
  is_correct: boolean;
  order: number;
}

export interface DashboardStats {
  total_students: number;
  total_teachers: number;
  total_classes: number;
  total_assessments: number;
  active_assessments: number;
  average_score: number;
  ai_questions_generated: number;
  ai_status: string;
}

export interface Notification {
  id: string;
  title: string;
  message: string;
  notification_type: string;
  is_read: boolean;
  created_at: string;
}

export interface Badge {
  id: string;
  name: string;
  description: string;
  icon: string;
  rarity: string;
  xp_reward: number;
}

export interface LeaderboardEntry {
  rank: number;
  student_name: string;
  class_name: string;
  score: number;
  xp: number;
  badge_count: number;
}

export interface ApiResponse<T> {
  status: string;
  message: string;
  data: T;
}

export interface PaginatedResponse<T> {
  count: number;
  next: string | null;
  previous: string | null;
  results: T[];
}
