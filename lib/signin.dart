import 'dart:convert';
import 'package:flutter/material.dart';
import 'package:http/http.dart' as http;
import 'package:shared_preferences/shared_preferences.dart';
import 'password/request_reset_password.dart';
import 'describe_feeling.dart';

class SignInPage extends StatefulWidget {
  const SignInPage({Key? key}) : super(key: key);

  @override
  State<SignInPage> createState() => _SignInPageState();
}

class _SignInPageState extends State<SignInPage> {
  final TextEditingController usernameOrEmail = TextEditingController();
  final TextEditingController passwordController = TextEditingController();
  final String baseUrl = "https://anees-rus4.onrender.com";
  bool isPasswordVisible = false;

  Future<void> signInRequest(BuildContext context) async {
    final Uri url = Uri.parse("$baseUrl/signin");
    final username = usernameOrEmail.text.trim();
    final password = passwordController.text.trim();

    if (username.isEmpty || password.isEmpty) {
      ScaffoldMessenger.of(context).showSnackBar(
        const SnackBar(content: Text("الرجاء إدخال البريد الإلكتروني أو اسم المستخدم وكلمة المرور")),
      );
      return;
    }

    final requestData = {"username": username, "password": password};

    try {
      final response = await http.post(
        url,
        headers: {"Content-Type": "application/json"},
        body: jsonEncode(requestData),
      );

      final data = jsonDecode(response.body);

      if (response.statusCode == 200) {
        final prefs = await SharedPreferences.getInstance();
        await prefs.clear(); 
        await prefs.setString('username', username);
        await prefs.setString('password', password);

        ScaffoldMessenger.of(context).showSnackBar(
          const SnackBar(content: Text("تسجيل الدخول ناجح")),
        );

        Navigator.pushReplacement(
          context,
          MaterialPageRoute(builder: (context) => DescribeFeelingPage()),
        );
      } else {
        ScaffoldMessenger.of(context).showSnackBar(
          SnackBar(content: Text("فشل تسجيل الدخول: ${data['error'] ?? response.body}")),
        );
      }
    } catch (e) {
      ScaffoldMessenger.of(context).showSnackBar(
        SnackBar(content: Text("خطأ في الاتصال : $e")),
      );
    }
  }

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      backgroundColor: const Color(0xFFC2D5F2),
      body: Center(
        child: SingleChildScrollView(
          padding: const EdgeInsets.symmetric(horizontal: 24, vertical: 32),
          child: Column(
            children: [
              Image.asset("assets/انيس.png", height: 220, width: 300),
              const SizedBox(height: 20),
              buildTextField('البريد الإلكتروني أو اسم المستخدم', "ادخل البريد الإلكتروني أو اسم المستخدم", false, usernameOrEmail),
              const SizedBox(height: 10),
              buildTextField('كلمة المرور', 'ادخل كلمة المرور', true, passwordController),
              const SizedBox(height: 10),
              Align(
                alignment: Alignment.centerLeft,
                child: TextButton(
                  onPressed: () {
                    Navigator.push(
                      context,
                      MaterialPageRoute(builder: (context) => const RequestResetPasswordPage()),
                    );
                  },
                  child: const Text(
                    "نسيت كلمة المرور",
                    style: TextStyle(
                      color: Color(0xFF4F6DA3),
                      fontSize: 16,
                      fontWeight: FontWeight.bold,
                    ),
                  ),
                ),
              ),
              const SizedBox(height: 10),
              buildButton('تسجيل الدخول', () => signInRequest(context)),
              const SizedBox(height: 10),
              buildButton('إنشاء حساب', () {
                Navigator.pushNamed(context, "/signup");
              }),
            ],
          ),
        ),
      ),
    );
  }

  Widget buildTextField(String label, String hint, bool isPassword, TextEditingController controller) {
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
            letterSpacing: -0.16,
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
            obscureText: isPassword ? !isPasswordVisible : false,
            textAlign: TextAlign.right,
            decoration: InputDecoration(
              hintText: hint,
              hintStyle: TextStyle(color: Colors.black.withOpacity(0.4)),
              border: InputBorder.none,
              prefixIcon: isPassword
                  ? IconButton(
                      icon: Icon(
                        isPasswordVisible ? Icons.visibility : Icons.visibility_off,
                        color: Colors.grey,
                      ),
                      onPressed: () {
                        setState(() {
                          isPasswordVisible = !isPasswordVisible;
                        });
                      },
                    )
                  : null,
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
          shape: RoundedRectangleBorder(
            borderRadius: BorderRadius.circular(30),
          ),
        ),
        child: Text(
          text,
          style: const TextStyle(
            color: Colors.white,
            fontSize: 18,
            fontWeight: FontWeight.bold,
          ),
        ),
      ),
    );
  }
}
