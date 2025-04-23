import 'package:flutter/material.dart';
import 'dart:convert';
import 'package:http/http.dart' as http;
import 'package:shared_preferences/shared_preferences.dart';

class ChatPasswordPage extends StatefulWidget {
  final Widget nextPage;

  const ChatPasswordPage({super.key, required this.nextPage});

  @override
  _ChatPasswordPageState createState() => _ChatPasswordPageState();
}

class _ChatPasswordPageState extends State<ChatPasswordPage> {
  final TextEditingController passwordController = TextEditingController();
  bool isLoading = false;

  final String baseUrl = "https://anees-rus4.onrender.com";

  Future<void> _checkPassword() async {
    final enteredPassword = passwordController.text.trim();

    if (enteredPassword.isEmpty || enteredPassword.length != 6 || !RegExp(r'^\d{6}$').hasMatch(enteredPassword)) {
      ScaffoldMessenger.of(context).showSnackBar(
        const SnackBar(content: Text("يرجى إدخال كلمة مرور مكونة من 6 أرقام")),
      );
      return;
    }

    final prefs = await SharedPreferences.getInstance();
    final username = prefs.getString('username') ?? '';

    if (username.isEmpty) {
      ScaffoldMessenger.of(context).showSnackBar(
        const SnackBar(content: Text("يرجى تسجيل الدخول أولًا")),
      );
      return;
    }

    setState(() => isLoading = true);

    final url = Uri.parse("$baseUrl/chat_password");
    try {
      final response = await http.post(
        url,
        headers: {"Content-Type": "application/json"},
        body: jsonEncode({
          "username": username,
          "password": enteredPassword,
        }),
      );

      setState(() => isLoading = false);

      if (response.statusCode == 200) {
        Navigator.pushReplacement(
          context,
          MaterialPageRoute(builder: (_) => widget.nextPage),
        );
      } else if (response.statusCode == 403) {
        ScaffoldMessenger.of(context).showSnackBar(
          const SnackBar(content: Text("كلمة المرور غير صحيحة")),
        );
      } else if (response.statusCode == 401) {
        ScaffoldMessenger.of(context).showSnackBar(
          const SnackBar(content: Text("يرجى تسجيل الدخول أولًا")),
        );
      } else {
        ScaffoldMessenger.of(context).showSnackBar(
          const SnackBar(content: Text("حدث خطأ، حاول مجددًا")),
        );
      }
    } catch (e) {
      setState(() => isLoading = false);
      ScaffoldMessenger.of(context).showSnackBar(
        SnackBar(content: Text("فشل الاتصال: $e")),
      );
    }
  }

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      backgroundColor: const Color(0xFFC2D5F2),
      body: Stack(
        children: [
          Positioned(
            top: 50,
            left: 15,
            child: IconButton(
              icon: const Icon(Icons.arrow_back_ios, color: Color(0xFF4F6DA3), size: 30),
              onPressed: () => Navigator.pop(context),
            ),
          ),
          Padding(
            padding: const EdgeInsets.fromLTRB(24, 140, 24, 40),
            child: Column(
              children: [
                Image.asset("assets/انيس.png", height: 240),
                const SizedBox(height: 40),
                const Text(
                  "كلمة مرور الدخول إلى الشات",
                  style: TextStyle(
                    color: Color(0xFF4F6DA3),
                    fontSize: 26,
                    fontWeight: FontWeight.bold,
                  ),
                  textAlign: TextAlign.center,
                ),
                const SizedBox(height: 14),
                const Text(
                  "يرجى إدخال كلمة مرور مكونة من 6 أرقام",
                  style: TextStyle(
                    color: Colors.black54,
                    fontSize: 16,
                  ),
                  textAlign: TextAlign.center,
                ),
                const SizedBox(height: 40),
                buildPasswordField("كلمة المرور", passwordController),
                const SizedBox(height: 30),
                isLoading
                    ? const CircularProgressIndicator(color: Color(0xFF4F6DA3))
                    : buildButton("دخول", _checkPassword),
              ],
            ),
          ),
        ],
      ),
    );
  }

  Widget buildPasswordField(String label, TextEditingController controller) {
    return Column(
      crossAxisAlignment: CrossAxisAlignment.end,
      children: [
        Text(
          label,
          style: const TextStyle(
            color: Color(0xFF4F6DA3),
            fontWeight: FontWeight.bold,
            fontSize: 17,
          ),
        ),
        const SizedBox(height: 8),
        Container(
          padding: const EdgeInsets.symmetric(horizontal: 16, vertical: 8),
          decoration: BoxDecoration(
            color: const Color(0xFFE9F1F4),
            borderRadius: BorderRadius.circular(32),
          ),
          child: TextField(
            controller: controller,
            textAlign: TextAlign.center,
            obscureText: true,
            keyboardType: TextInputType.number,
            decoration: const InputDecoration(
              border: InputBorder.none,
            ),
          ),
        ),
      ],
    );
  }

  Widget buildButton(String text, VoidCallback onPressed) {
    return SizedBox(
      width: double.infinity,
      child: ElevatedButton(
        onPressed: onPressed,
        style: ElevatedButton.styleFrom(
          backgroundColor: const Color(0xFF4F6DA3),
          padding: const EdgeInsets.symmetric(vertical: 16),
          shape: RoundedRectangleBorder(borderRadius: BorderRadius.circular(30)),
        ),
        child: Text(
          text,
          style: const TextStyle(color: Colors.white, fontSize: 18, fontWeight: FontWeight.bold),
        ),
      ),
    );
  }
}
