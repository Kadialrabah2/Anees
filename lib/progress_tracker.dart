import 'dart:convert';
import 'package:flutter/material.dart';
import 'package:http/http.dart' as http;
import 'package:percent_indicator/circular_percent_indicator.dart';
import 'package:shared_preferences/shared_preferences.dart';
import 'home.dart';
import 'app_localizations.dart';


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
    final loc = AppLocalizations.of(context);
    final prefs = await SharedPreferences.getInstance();
    _username = prefs.getString('username') ?? '';

    if (_username.isEmpty) {
      if (mounted) {
        ScaffoldMessenger.of(context).showSnackBar(
           SnackBar(content: Text(loc.translate("username_not_found"))),
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
    final loc = AppLocalizations.of(context);
    final response = await http.get(
      Uri.parse('$baseUrl/user_aggregated_mood_data/$_username'),
    );

    if (response.statusCode == 200) {
      final Map<String, dynamic> json = jsonDecode(response.body);
      final mood = json['average_mood_levels'];
      return {
        loc.translate("stress_level"): (mood['stress'] ?? 0).toDouble(),
        loc.translate("anxiety_level"): (mood['anxiety'] ?? 0).toDouble(),
        loc.translate("panic_level"): (mood['panic'] ?? 0).toDouble(),
        loc.translate("loneliness_level"): (mood['loneliness'] ?? 0).toDouble(),
        loc.translate("burnout_level"): (mood['burnout'] ?? 0).toDouble(),
        loc.translate("depression_level"): (mood['depression'] ?? 0).toDouble(),
      };
    } else if (response.statusCode == 404) {
      return {
        loc.translate("stress_level"): 0,
        loc.translate("anxiety_level"): 0,
        loc.translate("panic_level"): 0,
        loc.translate("loneliness_level"): 0,
        loc.translate("burnout_level"): 0,
        loc.translate("depression_level"): 0,
      };
    } else {
      throw Exception('${loc.translate("sign_in_failed")}- status: ${response.statusCode}');
    }
  }

  Future<List<Map<String, dynamic>>> _fetchWeeklyMood() async {
    final response = await http.get(
      Uri.parse('$baseUrl/get-weekly-mood/$_username'),
    );

    if (response.statusCode == 200) {
      final Map<String, dynamic> json = jsonDecode(response.body);
      final moods = json['weekly_mood'] as List<dynamic>;

      return moods.map((e) {
        return {
          'date': DateTime.parse(e['date']),
          'mood_value': e['mood_value'],
        };
      }).toList();
    } else {
      throw Exception(AppLocalizations.of(context).translate("fetch_weekly_mood_failed"));
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
         Padding(
          padding: EdgeInsets.only(top: 20, bottom: 8),
          child: Align(
            alignment: Alignment.centerRight,
            child: Text(
              AppLocalizations.of(context).translate("mood_summary"),
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
            body: Center(child: Text('${AppLocalizations.of(context).translate("unable_to_display_data")}:\n${snapshot.error}')),
          );
        }

        try {
          final Map<String, double> moodData = snapshot.data![0];
          final List<Map<String, dynamic>> weeklyMood = snapshot.data![1];

          return Directionality(
            textDirection: TextDirection.rtl,
            child: Scaffold(
              backgroundColor: const Color(0xFFC2D5F2),
              body: Stack(
                children: [
                  Positioned.fill(
                    child: Opacity(
                      opacity: 0.7,
                      child: Image.asset("assets/h.png"),
                    ),
                  ),
                  SafeArea(
                    child: Padding(
                      padding: const EdgeInsets.symmetric(horizontal: 16),
                      child: ListView(
                        children: [
                          const SizedBox(height: 70),
                          ...moodData.entries.map((e) => _buildIndicator(e.key, e.value)).toList(),
                          const SizedBox(height: 12),
                          _buildMoodSummary(weeklyMood),
                          const SizedBox(height: 30),
                        ],
                      ),
                    ),
                  ),
                  Positioned(
                    top: 50,
                    left: 15,
                    child: IconButton(
                      icon: const Icon(Icons.arrow_forward_ios, color: Color(0xFF4F6DA3), size: 30),
                      onPressed: () {
                        Navigator.pushAndRemoveUntil(
                          context,
                          MaterialPageRoute(builder: (context) => const HomePage()),
                          (route) => false,
                        );
                      },
                    ),
                  ),
                ],
              ),
            ),
          );
        } catch (e) {
          return Scaffold(
            body: Center(child: Text("${AppLocalizations.of(context).translate("unable_to_display_data")}: $e")),
          );
        }
      },
    );
  }
}
