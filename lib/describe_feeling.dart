import 'dart:convert';
import 'package:flutter/material.dart';
import 'package:http/http.dart' as http;
import 'package:shared_preferences/shared_preferences.dart';
import 'home.dart';
import 'app_localizations.dart';



class DescribeFeelingPage extends StatefulWidget {
  @override
  _DescribeFeelingPageState createState() => _DescribeFeelingPageState();
}

class _DescribeFeelingPageState extends State<DescribeFeelingPage> {
  final TextEditingController _feelingController = TextEditingController();
  int _selectedMoodIndex = 4;
  late String _username = "";

  final List<IconData> moodIcons = [
    Icons.sentiment_very_dissatisfied,
    Icons.sentiment_dissatisfied,
    Icons.sentiment_neutral,
    Icons.sentiment_satisfied,
    Icons.sentiment_very_satisfied,
  ];

  @override
  void initState() {
    super.initState();
    _loadUsername();
  }

  Future<void> _loadUsername() async {
    final prefs = await SharedPreferences.getInstance();
    setState(() {
      _username = prefs.getString('username') ?? '';
    });
  }

  Future<void> _submitMood() async {
    if (_username.isEmpty) {
      ScaffoldMessenger.of(context).showSnackBar(
         SnackBar(content: Text(AppLocalizations.of(context).translate("username_not_found"))),
      );
      return;
    }

    print('Submitting mood for: $_username');

    final response = await http.post(
      Uri.parse('https://anees-rus4.onrender.com/save-daily-mood/'),
      headers: {'Content-Type': 'application/json'},
      body: jsonEncode({
        'username': _username,
        'mood_value': _selectedMoodIndex + 1,
      }),
    );

    print('Status Code: ${response.statusCode}');
    print('Response Body: ${response.body}');

    if (response.statusCode == 200) {
      Navigator.pushReplacement(
        context,
        MaterialPageRoute(builder: (context) => HomePage()),
      );
    } else {
      ScaffoldMessenger.of(context).showSnackBar(
        SnackBar(content: Text("${AppLocalizations.of(context).translate("mood_submit_failed")}: ${response.body}")),
      );
    }
  }

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      backgroundColor: const Color(0xFFC2D5F2),
      body: Stack(
        children: [
          Positioned.fill(
            child: Opacity(
              opacity: 0.3,
              child: Image.asset("assets/h.png"),
            ),
          ),
          Column(
            crossAxisAlignment: CrossAxisAlignment.center,
            children: [
              const SizedBox(height: 80),
               Text(
                AppLocalizations.of(context).translate("describe_feeling_title"),
                style: TextStyle(
                  fontSize: 30,
                  fontWeight: FontWeight.bold,
                  color: Color(0xFF4F6DA3),
                ),
              ),
              const SizedBox(height: 48),
              Padding(
                padding: const EdgeInsets.symmetric(horizontal: 25),
                child: Container(
                  height: 300,
                  padding: const EdgeInsets.all(15),
                  decoration: BoxDecoration(
                    color: Colors.white,
                    borderRadius: BorderRadius.circular(20),
                  ),
                  child: TextField(
                    controller: _feelingController,
                    maxLines: null,
                    keyboardType: TextInputType.multiline,
                    textAlign: TextAlign.right,
                    decoration:  InputDecoration(
                      border: InputBorder.none,
                      hintText: AppLocalizations.of(context).translate("express_your_feelings_here"),
                      hintStyle: TextStyle(color: Colors.grey),
                    ),
                  ),
                ),
              ),
              const SizedBox(height: 15),
              ElevatedButton(
                onPressed: _submitMood,
                style: ElevatedButton.styleFrom(
                  backgroundColor: const Color(0xFF4F6DA3),
                  padding: const EdgeInsets.symmetric(horizontal: 40, vertical: 12),
                  shape: RoundedRectangleBorder(
                    borderRadius: BorderRadius.circular(10),
                  ),
                ),
                child:  Text(
                  AppLocalizations.of(context).translate("submit_button"),
                  style: TextStyle(fontSize: 18, color: Colors.white),
                ),
              ),
              const SizedBox(height: 40),
               Text(
                AppLocalizations.of(context).translate("how_do_you_feel"),
                style: TextStyle(
                  fontSize: 22,
                  fontWeight: FontWeight.bold,
                  color: Color(0xFF4F6DA3),
                ),
              ),
              const SizedBox(height: 10),
              Padding(
                padding: const EdgeInsets.symmetric(horizontal: 15),
                child: Row(
                  mainAxisAlignment: MainAxisAlignment.spaceEvenly,
                  children: List.generate(moodIcons.length, (index) {
                    return GestureDetector(
                      onTap: () {
                        setState(() {
                          _selectedMoodIndex = index;
                        });
                      },
                      child: CircleAvatar(
                        radius: 30,
                        backgroundColor: _selectedMoodIndex == index ? Colors.white : Colors.transparent,
                        child: Icon(
                          moodIcons[index],
                          size: 40,
                          color: const Color(0xFF4F6DA3),
                        ),
                      ),
                    );
                  }),
                ),
              ),
            ],
          ),
        ],
      ),
    );
  }
}
