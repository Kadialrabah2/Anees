import 'package:flutter/material.dart';
import 'dart:convert';
import 'package:http/http.dart' as http;

class HealthyLifestyleService {
  final String baseUrl = "https://anees-rus4.onrender.com";

  Future<String> sendMessage(int userId, String message) async {
    final response = await http.post(
      Uri.parse('$baseUrl/cognitiveChat'),
      headers: {"Content-Type": "application/json"},
      body: jsonEncode({
        "user_id": userId,
        "message": message,
      }),
    );

    if (response.statusCode == 200) {
      final data = jsonDecode(response.body);
      return data["response"];
    } else {
      throw Exception("Server error: ${response.statusCode}");
    }
  }
}

class HealthyLifestylePage extends StatefulWidget {
  final String? userName;

  HealthyLifestylePage({this.userName});

  @override
  _HealthyLifestylePageState createState() => _HealthyLifestylePageState();
}

class _HealthyLifestylePageState extends State<HealthyLifestylePage> {
  final TextEditingController _messageController = TextEditingController();
  final List<Map<String, dynamic>> _messages = [];

  @override
  void initState() {
    super.initState();
    String name = widget.userName?.isNotEmpty == true ? widget.userName! : "رفيق أنيس";
    _messages.add({
      "text":
          "أهلًا بك $name\nهل هناك أفكار تشعر أنها تؤثر على حالتك النفسية مؤخرًا؟ أنا هنا لمساعدتك في فهمها والتعامل معها خطوة بخطوة",
      "isUser": false
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
      final reply = await HealthyLifestyleService().sendMessage(
        int.parse(widget.userName ?? "0"),
        text,
      );
      setState(() {
        _messages.add({"text": reply, "isUser": false});
      });
    } catch (e) {
      setState(() {
        _messages.add({"text": "❌ فشل الاتصال بالخادم", "isUser": false});
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
                          decoration: const InputDecoration(
                            border: InputBorder.none,
                            hintText: "...اكتب رسالتك هنا",
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
