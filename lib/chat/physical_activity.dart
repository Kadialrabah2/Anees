import 'package:flutter/material.dart';
import 'dart:convert';
import 'package:http/http.dart' as http;

class PhysicalActivityPage extends StatefulWidget {
  final String? userName;

  const PhysicalActivityPage({Key? key, this.userName}) : super(key: key);

  @override
  _PhysicalActivityPageState createState() => _PhysicalActivityPageState();
}

class _PhysicalActivityPageState extends State<PhysicalActivityPage> {
  final TextEditingController _messageController = TextEditingController();
  final List<Map<String, dynamic>> _messages = [];

  final String baseUrl = "https://anees-rus4.onrender.com";

  @override
  void initState() {
    super.initState();
    String name = widget.userName?.isNotEmpty == true ? widget.userName! : "رفيق أنيس";
    _messages.add({"text": "مرحبًا $name\nما هو نشاطك البدني اليوم؟", "isUser": false});
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
      Uri.parse('$baseUrl/physical'),
      headers: {"Content-Type": "application/json"},
      body: jsonEncode({
        "username": widget.userName ?? "unknown",
        "message": text,
      }),
    );

    if (response.statusCode == 200) {
      final data = jsonDecode(response.body);
      setState(() {
        _messages.add({"text": data["response"], "isUser": false});
      });
    } else {
      throw Exception("HTTP ${response.statusCode}");
    }
  } catch (e) {
    setState(() {
      _messages.add({"text": "فشل الاتصال بالسيرفر", "isUser": false});
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
                      alignment: isUser ? Alignment.centerRight : Alignment.centerLeft,
                      child: Container(
                        margin: const EdgeInsets.symmetric(vertical: 5),
                        padding: const EdgeInsets.symmetric(horizontal: 15, vertical: 10),
                        decoration: BoxDecoration(
                          color: isUser ? Colors.white : const Color(0xFF4F6DA3),
                          borderRadius: BorderRadius.only(
                            topLeft: Radius.circular(20),
                            topRight: Radius.circular(20),
                            bottomLeft: isUser ? Radius.circular(20) : Radius.zero,
                            bottomRight: isUser ? Radius.zero : Radius.circular(20),
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
                        child: Icon(Icons.send, color: Color(0xFF4F6DA3), size: 28),
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

