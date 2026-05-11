import 'package:flutter/material.dart';

class AppConstants {
  static const String baseUrl = 'http://10.0.2.2:8000/api/v1';
  static const String wsBaseUrl = 'ws://10.0.2.2:8000/ws';

  static const String accessTokenKey = 'access_token';
  static const String refreshTokenKey = 'refresh_token';
  static const String userKey = 'user_data';
  static const String roleKey = 'user_role';

  static const int connectTimeout = 30;
  static const int receiveTimeout = 60;

  static const List<String> classLevels = ['P1', 'P2', 'P3', 'P4', 'P5', 'P6', 'P7'];
  static const List<int> terms = [1, 2, 3];

  static const Map<String, String> subjectIcons = {
    'Mathematics': '➕',
    'English Language': '📚',
    'Science': '🔬',
    'Social Studies': '🌍',
    'Luganda': '🗣️',
    'CRE': '✝️',
    'IRE': '☪️',
    'Music': '🎵',
    'Art & Craft': '🎨',
    'Physical Education': '⚽',
    'Agriculture': '🌱',
    'Technology': '💻',
  };

  static const Map<String, Color> difficultyColors = {};

  static const Map<int, String> termNames = {
    1: 'Term 1',
    2: 'Term 2',
    3: 'Term 3',
  };

  static const Map<String, String> gradeDescriptions = {
    'D1': 'Excellent (85-100%)',
    'D2': 'Very Good (75-84%)',
    'C3': 'Good (65-74%)',
    'C4': 'Fair (55-64%)',
    'C5': 'Satisfactory (45-54%)',
    'C6': 'Pass (40-44%)',
    'P7': 'Below Average (35-39%)',
    'P8': 'Poor (30-34%)',
    'F9': 'Fail (Below 30%)',
  };
}
