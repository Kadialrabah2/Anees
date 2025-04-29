import 'package:flutter/material.dart';
import 'dart:convert';
import 'package:http/http.dart' as http;
import 'package:shared_preferences/shared_preferences.dart';
import 'package:anees/app_localizations.dart';

class TalkToMePage extends StatefulWidget {
  const TalkToMePage({Key? key}) : super(key: key);

  @override
  _TalkToMePageState createState() => _TalkToMePageState();
}

class _TalkToMePageState extends State<TalkToMePage> {
  final TextEditingController _messageController = TextEditingController();
  final List<Map<String, dynamic>> _messages = [];
  final String baseUrl = "https://anees-rus4.onrender.com";
  String _userName = "رفيق أنيس";

  @override
  void initState() {
    super.initState();
    _loadUserName();
  }

  Future<void> _loadUserName() async {
    final prefs = await SharedPreferences.getInstance();
    final savedName = prefs.getString('username') ?? "رفيق أنيس";
    setState(() {
      _userName = savedName;
      _messages.add({
        "text": AppLocalizations.of(context)
            .translate('talk_to_me_welcome')
            .replaceFirst("{user}", savedName),
        "isUser": false,
      });
    });
  }

  void _sendMessage() async {
    final text = _messageController.text.trim();
    if (text.isEmpty) return;

    setState(() {
      _messages.add({"text": text, "isUser": true});
      _messageController.clear();
    });

    try {
      final response = await http.post(
        Uri.parse('$baseUrl/diagnosis'),
        headers: {"Content-Type": "application/json"},
        body: jsonEncode({
          "username": _userName,
          "message": text,
        }),
      );

      if (response.statusCode == 200) {
        final data = jsonDecode(response.body);
        final rawReply = data["response"];
        final cleanedReply = rawReply
            .replaceAll(RegExp(r'\\[nrt]'), '\n')
            .replaceAll(RegExp(r'\\+'), '')
            .replaceAll(RegExp(r'\s{2,}'), ' ')
            .replaceAll(RegExp(r'[^\u0600-\u06FF\u0750-\u077F\u08A0-\u08FF\uFB50-\uFDFF\uFE70-\uFEFFa-zA-Z0-9.,?!؛،…\s]'), '')
            .trim();

        setState(() {
          _messages.add({"text": cleanedReply, "isUser": false});
        });
      } else {
        setState(() {
          _messages.add({
            "text":
                AppLocalizations.of(context).translate("server_failure"),
            "isUser": false
          });
        });
      }
    } catch (e) {
      setState(() {
        _messages.add({
          "text":
              AppLocalizations.of(context).translate("server_failure"),
          "isUser": false
        });
      });
    }
  }

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      backgroundColor: const Color(0xFFC2D5F2),
      body: Stack(
        children: [
          Positioned.fill(
            child: Opacity(opacity: 0.4, child: Image.asset("assets/h.png")),
          ),
          Column(
            children: [
              Container(
                padding: const EdgeInsets.only(left: 15, top: 50),
                alignment: Alignment.centerLeft,
                color: const Color(0xFF4F6DA3),
                height: 95,
                child: IconButton(
                  icon: const Icon(Icons.arrow_back_ios, color: Colors.white),
                  onPressed: () => Navigator.pop(context),
                ),
              ),
              Expanded(
                child: ListView.builder(
                  padding: const EdgeInsets.all(15),
                  itemCount: _messages.length,
                  itemBuilder: (context, index) {
                    final isUser = _messages[index]["isUser"];
                    return Align(
                      alignment:
                          isUser ? Alignment.centerRight : Alignment.centerLeft,
                      child: Container(
                        margin: const EdgeInsets.symmetric(vertical: 5),
                        padding: const EdgeInsets.symmetric(
                            horizontal: 15, vertical: 10),
                        decoration: BoxDecoration(
                          color:
                              isUser ? Colors.white : const Color(0xFF4F6DA3),
                          borderRadius: BorderRadius.only(
                            topLeft: Radius.circular(20),
                            topRight: Radius.circular(20),
                            bottomLeft:
                                isUser ? Radius.circular(20) : Radius.zero,
                            bottomRight:
                                isUser ? Radius.zero : Radius.circular(20),
                          ),
                        ),
                        child: Text(
                          _messages[index]["text"],
                          style: TextStyle(
                            color: isUser ? Colors.black : Colors.white,
                            fontSize: 16,
                          ),
                        ),
                      ),
                    );
                  },
                ),
              ),
              Container(
                padding: const EdgeInsets.all(10),
                decoration: const BoxDecoration(
                  color: Color(0xFF4F6DA3),
                  borderRadius: BorderRadius.only(
                    topLeft: Radius.circular(25),
                    topRight: Radius.circular(25),
                  ),
                ),
                child: Row(
                  children: [
                    Expanded(
                      child: Container(
                        padding: const EdgeInsets.symmetric(horizontal: 15),
                        decoration: BoxDecoration(
                          color: Colors.white,
                          borderRadius: BorderRadius.circular(25),
                        ),
                        child: TextField(
                          controller: _messageController,
                          textAlign: TextAlign.right,
                          decoration: InputDecoration(
                            border: InputBorder.none,
                            hintText: AppLocalizations.of(context)
                                .translate("write_message_hint"),
                            hintStyle: TextStyle(color: Colors.grey),
                          ),
                        ),
                      ),
                    ),
                    const SizedBox(width: 10),
                    GestureDetector(
                      onTap: _sendMessage,
                      child: const CircleAvatar(
                        backgroundColor: Colors.white,
                        radius: 25,
                        child: Icon(Icons.send,
                            color: Color(0xFF4F6DA3), size: 28),
                      ),
                    ),
                  ],
                ),
              ),
            ],
          ),
        ],
      ),
    );
  }
}
