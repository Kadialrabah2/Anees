import 'dart:convert';
import 'package:flutter/material.dart';
import 'package:http/http.dart' as http;
import 'app_localizations.dart';

class SignUpPage extends StatefulWidget {
  @override
  _SignUpScreenState createState() => _SignUpScreenState();
}

class _SignUpScreenState extends State<SignUpPage> {
  final TextEditingController usernameController = TextEditingController();
  final TextEditingController emailController = TextEditingController();
  final TextEditingController passwordController = TextEditingController();
  bool isPasswordObscured = true;

  final String baseUrl = "https://anees-rus4.onrender.com";

  Future<void> signUp(BuildContext context) async {
  final Uri url = Uri.parse("$baseUrl/signup");

  try {
    final response = await http.post(
      url,
      headers: {"Content-Type": "application/json"},
      body: jsonEncode({
        "username": usernameController.text.trim(),
        "email": emailController.text.trim(),
        "password": passwordController.text.trim(),
      }),
    );

    final responseData = jsonDecode(response.body);


    final isSuccess = response.statusCode >= 200 && response.statusCode < 300;

    final message = isSuccess
        ? "${responseData['message'] ?? 'تم إنشاء الحساب بنجاح!'}"
        : "فشل إنشاء الحساب: ${responseData['error'] ?? response.body}";

    ScaffoldMessenger.of(context).showSnackBar(SnackBar(content: Text(message)));

    if (isSuccess) {
      Navigator.pushReplacementNamed(context, '/signin');
    }
  } catch (e) {
    ScaffoldMessenger.of(context).showSnackBar(
      SnackBar(content: Text("خطأ أثناء الاتصال بالسيرفر: $e")),
    );
  }
}


  @override
  Widget build(BuildContext context) {
    final loc = AppLocalizations.of(context);
    return Scaffold(
      backgroundColor: const Color(0xFFC2D5F2),
      body: Center(
        child: SingleChildScrollView(
          padding: const EdgeInsets.symmetric(horizontal: 24, vertical: 32),
          child: Column(
            children: [
              Image.asset("assets/انيس.png", height: 220, width: 300),
              const SizedBox(height: 20),
              buildTextField(loc.translate("username"), loc.translate("enter_username"), false, usernameController),
              const SizedBox(height: 10),
              buildTextField(loc.translate("email"), loc.translate("enter_email"), false, emailController),
              const SizedBox(height: 10),
              buildPasswordField(),
              const SizedBox(height: 30),
              buildButton(loc.translate("sign_up"), () => signUp(context)),
              const SizedBox(height: 10),
              buildButton(loc.translate("sign_in"), () {
                Navigator.pushReplacementNamed(context, '/signin');
              }),
            ],
          ),
        ),
      ),
    );
  }

  Widget buildTextField(String label, String hint, bool isPassword, TextEditingController controller, {bool isNumber = false}) {
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
            keyboardType: isNumber ? TextInputType.number : TextInputType.text,
            textAlign: TextAlign.right,
            obscureText: isPassword,
            decoration: InputDecoration(
              hintText: hint,
              hintStyle: TextStyle(
                color: Colors.black.withOpacity(0.4),
                fontSize: 15,
                fontFamily: 'Tienne',
              ),
              border: InputBorder.none,
            ),
          ),
        ),
      ],
    );
  }

  Widget buildPasswordField() {
    final loc = AppLocalizations.of(context);
    return Column(
      crossAxisAlignment: CrossAxisAlignment.end,
      children: [
         Text(
          loc.translate("password"),
          style: TextStyle(
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
            controller: passwordController,
            textAlign: TextAlign.right,
            obscureText: isPasswordObscured,
            decoration: InputDecoration(
              hintText: loc.translate("enter_password"),
              hintStyle: TextStyle(
                color: Colors.black.withOpacity(0.4),
                fontSize: 15,
                fontFamily: 'Tienne',
              ),
              border: InputBorder.none,
              prefixIcon: IconButton(
                icon: Icon(
                  isPasswordObscured ? Icons.visibility : Icons.visibility_off,
                  color: Colors.grey,
                ),
                onPressed: () {
                  setState(() {
                    isPasswordObscured = !isPasswordObscured;
                  });
                },
              ),
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
