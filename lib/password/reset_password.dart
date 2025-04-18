import 'dart:convert';
import 'package:flutter/material.dart';
import 'package:http/http.dart' as http;

class ResetPasswordPage extends StatefulWidget {
  final String email;

  const ResetPasswordPage({super.key, required this.email});

  @override
  _ResetPasswordPageState createState() => _ResetPasswordPageState();
}

class _ResetPasswordPageState extends State<ResetPasswordPage> {
  final TextEditingController passwordController = TextEditingController();
  final TextEditingController confirmPasswordController = TextEditingController();

  bool isLoading = false;

  Future<void> resetPassword() async {
    final String baseUrl = "https://anees-rus4.onrender.com";
    final Uri url = Uri.parse("$baseUrl/reset_password_without_code");

    String password = passwordController.text.trim();
    String confirmPassword = confirmPasswordController.text.trim();

    if (password.isEmpty || confirmPassword.isEmpty || password != confirmPassword) {
      ScaffoldMessenger.of(context).showSnackBar(
        const SnackBar(content: Text("تأكد من تطابق كلمتي المرور وأنها غير فارغة")),
      );
      return;
    }

    setState(() {
      isLoading = true;
    });

    final response = await http.post(
      url,
      headers: {"Content-Type": "application/json"},
      body: jsonEncode({
        "email": widget.email,
        "new_password": password,
      }),
    );

    setState(() {
      isLoading = false;
    });

    if (response.statusCode == 200) {
      ScaffoldMessenger.of(context).showSnackBar(
        const SnackBar(content: Text("تم تغيير كلمة المرور بنجاح")),
      );
      Navigator.pop(context);
    } else {
      ScaffoldMessenger.of(context).showSnackBar(
        SnackBar(content: Text("فشل تغيير كلمة المرور: ${response.body}")),
      );
    }
  }

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      backgroundColor: const Color(0xFFC2D5F2),
      body: Padding(
        padding: const EdgeInsets.symmetric(horizontal: 24, vertical: 60),
        child: Column(
          children: [
            Image.asset("assets/انيس.png", height: 120),
            const SizedBox(height: 30),
            const Text(
              "تحديث كلمة المرور",
              style: TextStyle(
                color: Color(0xFF4F6DA3),
                fontSize: 24,
                fontWeight: FontWeight.bold,
              ),
            ),
            const SizedBox(height: 20),

            buildPasswordField("كلمة المرور الجديدة", passwordController),
            const SizedBox(height: 16),
            buildPasswordField("تأكيد كلمة المرور", confirmPasswordController),
            const SizedBox(height: 24),

            isLoading
                ? const CircularProgressIndicator(color: Color(0xFF4F6DA3))
                : buildButton("تحديث كلمة المرور", resetPassword),
          ],
        ),
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
            fontFamily: 'Tienne',
          ),
          textDirection: TextDirection.rtl,
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
            textAlign: TextAlign.right,
            obscureText: true,
            decoration: const InputDecoration(
              hintText: '••••••••',
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
