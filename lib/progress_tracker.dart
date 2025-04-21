import 'dart:convert'; 
import 'package:flutter/material.dart';
import 'package:http/http.dart' as http;
import 'package:percent_indicator/circular_percent_indicator.dart';

class ProgressTrackerPage extends StatelessWidget {
  const ProgressTrackerPage({super.key});

  Future<Map<String, double>> _fetchMoodLevels() async {
    try {
  final response = await http.post(
  Uri.parse('https://anees-rus4.onrender.com/diagnosis'),
  headers: {'Content-Type': 'application/json'},
  body: jsonEncode({
    "username": "testuser", 
    "message": "hi"
  }),
);


      print("🔍 Status Code: ${response.statusCode}");
      print("🔍 Response Body: ${response.body}");

      if (response.statusCode == 200) {
  final Map<String, dynamic> json = jsonDecode(response.body);
final mood = json['mood_scores'];

return {
  'مستوى التوتر': (mood['stress_level'] ?? 0).toDouble(),
  'مستوى الإجهاد': (mood['anxiety_level'] ?? 0).toDouble(),
  'مستوى نوبات الهلع': (mood['panic_level'] ?? 0).toDouble(),
  'مستوى الشعور بالوحدة': (mood['loneliness_level'] ?? 0).toDouble(),
  'مستوى الإرهاق': (mood['burnout_level'] ?? 0).toDouble(),
  'مستوى الإكتئاب': (mood['depression_level'] ?? 0).toDouble(),
};

      } else {
        throw Exception('فشل الاتصال بالسيرفر');
      }
    } catch (e) {
      print("❌ Error during fetching mood levels: $e");
      rethrow;
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

  Widget _buildMoodSummary() {
    const List<IconData> moodIcons = [
      Icons.sentiment_very_dissatisfied,
      Icons.sentiment_dissatisfied,
      Icons.sentiment_neutral,
      Icons.sentiment_satisfied,
      Icons.sentiment_very_satisfied,
      Icons.sentiment_neutral,
      Icons.sentiment_satisfied,
    ];

    const days = ['أحد', 'سبت', 'جمعة', 'خميس', 'أربعاء', 'ثلاثاء', 'إثنين'];

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
            return Column(
              children: [
                Icon(moodIcons[index], size: 30, color: Color(0xFF4F6DA3)),
                const SizedBox(height: 4),
                Text(
                  days[index],
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
  return FutureBuilder<Map<String, double>>(
    future: _fetchMoodLevels(),
    builder: (context, snapshot) {
      if (snapshot.connectionState == ConnectionState.waiting) {
        return const Scaffold(
          body: Center(child: CircularProgressIndicator()),
        );
      } else if (snapshot.hasError) {
        return Scaffold(
          body: Center(child: Text('خطأ: ${snapshot.error}')),
        );
      } else {
        final progressData = snapshot.data!;
        return Directionality(
          textDirection: TextDirection.rtl,
          child: Scaffold(
            backgroundColor: const Color(0xFFC2D5F2),
            body: Stack(
              children: [
                Positioned.fill(
                  child: Opacity(
                    opacity: 0.50,
                    child: Image.asset("assets/h.png"),
                  ),
                ),
                SafeArea(
                  child: Column(
                    children: [
                      Align(
                        alignment: Alignment.centerLeft,
                        child: Padding(
                          padding: const EdgeInsets.only(left: 15, top: 10),
                          child: IconButton(
                            icon: const Icon(Icons.arrow_forward_ios, color: Color(0xFF4F6DA3), size: 30),
                            onPressed: () => Navigator.pop(context),
                          ),
                        ),
                      ),
                      Expanded(
                        child: Padding(
                          padding: const EdgeInsets.symmetric(horizontal: 16),
                          child: ListView(
                            children: [
                              const SizedBox(height: 20),
                              ...progressData.entries.map((e) => _buildIndicator(e.key, e.value)).toList(),
                              const SizedBox(height: 12),
                              _buildMoodSummary(),
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
                    ],
                  ),
                ),
              ],
            ),
          ),
        );
      }
    },
  );
}}