 import 'dart:convert';
import 'dart:io';
import 'package:flutter/material.dart';
import 'package:http/http.dart' as http;
import 'package:percent_indicator/circular_percent_indicator.dart';
import 'package:shared_preferences/shared_preferences.dart';

class ProgressTrackerPage extends StatefulWidget {
  const ProgressTrackerPage({Key? key}) : super(key: key);

  @override
  _ProgressTrackerPageState createState() => _ProgressTrackerPageState();
}

class _ProgressTrackerPageState extends State<ProgressTrackerPage> {
  final String baseUrl = "https://anees-rus4.onrender.com";
  Future<List<dynamic>>? _combinedFuture;
  String _username = "";

  @override
  void initState() {
    super.initState();
    _initializeData();
  }

  Future<void> _initializeData() async {
    final prefs = await SharedPreferences.getInstance();
    _username = prefs.getString('username') ?? '';

    if (_username.isEmpty) {
      if (mounted) {
        ScaffoldMessenger.of(context).showSnackBar(
          const SnackBar(content: Text("اسم المستخدم غير متوفر")),
        );
      }
      return;
    }

    setState(() {
      _combinedFuture = Future.wait([
        _fetchMoodLevels(),
        _fetchWeeklyMood(),
      ]);
    });
  }

  Future<Map<String, double>> _fetchMoodLevels() async {
    final response = await http.get(
      Uri.parse('$baseUrl/user_aggregated_mood_data/$_username'),
    );

    if (response.statusCode == 200) {
      final Map<String, dynamic> json = jsonDecode(response.body);
      final mood = json['average_mood_levels'];
      return {
        'مستوى التوتر': (mood['stress'] ?? 0).toDouble(),
        'مستوى الإجهاد': (mood['anxiety'] ?? 0).toDouble(),
        'مستوى نوبات الهلع': (mood['panic'] ?? 0).toDouble(),
        'مستوى الشعور بالوحدة': (mood['loneliness'] ?? 0).toDouble(),
        'مستوى الإرهاق': (mood['burnout'] ?? 0).toDouble(),
        'مستوى الإكتئاب': (mood['depression'] ?? 0).toDouble(),
      };
    } else if (response.statusCode == 404) {
      return {
        'مستوى التوتر': 0,
        'مستوى الإجهاد': 0,
        'مستوى نوبات الهلع': 0,
        'مستوى الشعور بالوحدة': 0,
        'مستوى الإرهاق': 0,
        'مستوى الإكتئاب': 0,
      };
    } else {
      throw Exception('فشل الاتصال بالسيرفر - status: ${response.statusCode}');
    }
  }

  Future<List<Map<String, dynamic>>> _fetchWeeklyMood() async {
    final response = await http.get(
      Uri.parse('$baseUrl/get-weekly-mood/$_username'),
    );

    if (response.statusCode == 200) {
      final Map<String, dynamic> json = jsonDecode(response.body);
      final moods = json['weekly_moods'] as List<dynamic>;

      return moods.map((e) {
        return {
          'date': HttpDate.parse(e['date']),
          'mood_value': e['mood_value'],
        };
      }).toList();
    } else {
      throw Exception('فشل في جلب بيانات المزاج الأسبوعي');
    }
  }

  Widget _buildIndicator(String label, double value) {
    return AnimatedContainer(
      duration: const Duration(milliseconds: 150),
      margin: const EdgeInsets.only(bottom: 16),
      padding: const EdgeInsets.symmetric(horizontal: 16, vertical: 10),
      decoration: BoxDecoration(
        color: Colors.white.withOpacity(0.9),
        borderRadius: BorderRadius.circular(20),
        boxShadow: [
          BoxShadow(
            color: Colors.black.withOpacity(0.05),
            blurRadius: 6,
            offset: const Offset(0, 3),
          ),
        ],
      ),
      child: Row(
        children: [
          CircularPercentIndicator(
            radius: 30,
            lineWidth: 7,
            percent: (value / 100).clamp(0.0, 1.0),
            animation: true,
            animationDuration: 500,
            center: Text(
              "${value.toInt()}",
              style: const TextStyle(
                fontSize: 16,
                fontWeight: FontWeight.w900,
                color: Color(0xFF4F6DA3),
              ),
            ),
            progressColor: const Color(0xFF4F6DA3),
            backgroundColor: Colors.grey.shade300,
          ),
          const SizedBox(width: 16),
          Expanded(
            child: Text(
              label,
              style: const TextStyle(
                fontSize: 17,
                fontWeight: FontWeight.w900,
                color: Color(0xFF4F6DA3),
              ),
              textDirection: TextDirection.rtl,
              textAlign: TextAlign.right,
            ),
          ),
        ],
      ),
    );
  }

  Widget _buildMoodSummary(List<Map<String, dynamic>> weeklyMood) {
    const moodIcons = [
      Icons.sentiment_very_dissatisfied,
      Icons.sentiment_dissatisfied,
      Icons.sentiment_neutral,
      Icons.sentiment_satisfied,
      Icons.sentiment_very_satisfied,
    ];

    const daysAr = ['إثنين', 'ثلاثاء', 'أربعاء', 'خميس', 'جمعة', 'سبت', 'أحد'];

    final Map<int, int> moodMap = {};
    for (var entry in weeklyMood) {
      final date = entry['date'] as DateTime;
      final mood = entry['mood_value'] as int;
      moodMap[date.weekday] = mood;
    }

    return Column(
      crossAxisAlignment: CrossAxisAlignment.end,
      children: [
        const Padding(
          padding: EdgeInsets.only(top: 20, bottom: 8),
          child: Align(
            alignment: Alignment.centerRight,
            child: Text(
              'ملخص مزاجك',
              style: TextStyle(
                fontSize: 20,
                fontWeight: FontWeight.w900,
                color: Color(0xFF4F6DA3),
              ),
              textAlign: TextAlign.right,
            ),
          ),
        ),
        const SizedBox(height: 10),
        Row(
          mainAxisAlignment: MainAxisAlignment.spaceBetween,
          children: List.generate(7, (index) {
            final dayIndex = index + 1;
            final moodValue = moodMap[dayIndex] ?? 0;
            final iconIndex = moodValue.clamp(1, 5) - 1;
            final dayName = daysAr[index % 7];

            return Column(
              children: [
                Icon(
                  moodValue == 0 ? Icons.remove : moodIcons[iconIndex],
                  size: 30,
                  color: const Color(0xFF4F6DA3),
                ),
                const SizedBox(height: 4),
                Text(
                  dayName,
                  style: const TextStyle(
                    fontSize: 12,
                    fontWeight: FontWeight.w900,
                    color: Color(0xFF4F6DA3),
                  ),
                ),
              ],
            );
          }),
        ),
      ],
    );
  }

  Widget _buildRecommendationItem(String text) {
    return Container(
      margin: const EdgeInsets.symmetric(vertical: 6),
      padding: const EdgeInsets.symmetric(vertical: 14),
      width: double.infinity,
      decoration: BoxDecoration(
        color: Colors.white,
        borderRadius: BorderRadius.circular(30),
        boxShadow: [
          BoxShadow(
            color: Colors.black.withOpacity(0.08),
            blurRadius: 10,
            offset: const Offset(0, 4),
          ),
        ],
      ),
      alignment: Alignment.center,
      child: Text(
        text,
        style: const TextStyle(
          color: Color(0xFF4F6DA3),
          fontSize: 16,
          fontWeight: FontWeight.w900,
        ),
      ),
    );
  }

  @override
  Widget build(BuildContext context) {
    if (_combinedFuture == null) {
      return const Scaffold(
        body: Center(child: CircularProgressIndicator()),
      );
    }

    return FutureBuilder<List<dynamic>>(
      future: _combinedFuture,
      builder: (context, snapshot) {
        if (snapshot.connectionState != ConnectionState.done) {
          return const Scaffold(body: Center(child: CircularProgressIndicator()));
        }

        if (snapshot.hasError) {
          return Scaffold(
            body: Center(child: Text('تعذر عرض البيانات:\n${snapshot.error}')),
          );
        }

        try {
          final Map<String, double> moodData = snapshot.data![0];
          final List<Map<String, dynamic>> weeklyMood = snapshot.data![1];

          return Directionality(
            textDirection: TextDirection.rtl,
            child: Scaffold(
              backgroundColor: const Color(0xFFC2D5F2),
              body: SafeArea(
                child: Padding(
                  padding: const EdgeInsets.symmetric(horizontal: 16),
                  child: ListView(
                    children: [
                      const SizedBox(height: 20),
                      ...moodData.entries.map((e) => _buildIndicator(e.key, e.value)).toList(),
                      const SizedBox(height: 12),
                      _buildMoodSummary(weeklyMood),
                      const SizedBox(height: 30),
                      const Text(
                        'توصيات',
                        style: TextStyle(
                          fontSize: 20,
                          fontWeight: FontWeight.w900,
                          color: Color(0xFF4F6DA3),
                        ),
                        textAlign: TextAlign.right,
                      ),
                      const SizedBox(height: 8),
                      _buildRecommendationItem("المشاركة في الأنشطة الإجتماعية"),
                      _buildRecommendationItem("ممارسة الرياضة بانتظام"),
                      const SizedBox(height: 30),
                    ],
                  ),
                ),
              ),
            ),
          );
        } catch (e) {
          return Scaffold(
            body: Center(child: Text("تعذر عرض البيانات: $e")),
          );
        }
      },
    );
  }
}