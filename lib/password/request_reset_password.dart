import 'package:flutter/material.dart';
import 'verify_code.dart'; 
import 'package:http/http.dart' as http;
import 'package:anees/app_localizations.dart';


class RequestResetPasswordPage extends StatefulWidget {
  const RequestResetPasswordPage({super.key});

  @override
  State<RequestResetPasswordPage> createState() =>
      _RequestResetPasswordPageState();
}

class _RequestResetPasswordPageState extends State<RequestResetPasswordPage> {
  final TextEditingController emailController = TextEditingController();

  void goToVerifyPage() async {
  String email = emailController.text.trim();

  if (email.isEmpty || !email.contains('@')) {
    ScaffoldMessenger.of(context).showSnackBar(
       SnackBar(content: Text(AppLocalizations.of(context).translate("error_invalid_email"))),
    );
    return;
  }

  final String baseUrl = "https://anees-rus4.onrender.com";
  final Uri url = Uri.parse("$baseUrl/request_reset_password");

  try {
    final response = await http.post(
      url,
      headers: {"Content-Type": "application/json"},
      body: '{"email": "$email"}',
    );

    if (response.statusCode == 200) {
      ScaffoldMessenger.of(context).showSnackBar(
         SnackBar(content: Text(AppLocalizations.of(context).translate("code_sent_to_email"))),
      );

      Navigator.push(
        context,
        MaterialPageRoute(
          builder: (context) => VerifyCodePage(email: email),
        ),
      );
    } else {
      ScaffoldMessenger.of(context).showSnackBar(
        SnackBar(content: Text("${AppLocalizations.of(context).translate("error_server")} ${response.body}")),
      );
    }
  } catch (e) {
    ScaffoldMessenger.of(context).showSnackBar(
      SnackBar(content: Text("${AppLocalizations.of(context).translate("error_connection")} $e")),
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
              icon: const Icon(Icons.arrow_back_ios,
                  color: Color(0xFF4F6DA3), size: 30),
              onPressed: () => Navigator.pop(context),
            ),
          ),
          Center(
            child: SingleChildScrollView(
              padding: const EdgeInsets.symmetric(horizontal: 24, vertical: 32),
              child: Column(
                children: [
                  Image.asset("assets/انيس.png", height: 250, width: 300),
                  const SizedBox(height: 20),
                   Text(
                    AppLocalizations.of(context).translate("reset_password_button"),
                    style: TextStyle(
                      color: Color(0xFF4F6DA3),
                      fontSize: 24,
                      fontWeight: FontWeight.bold,
                    ),
                    textAlign: TextAlign.center,
                  ),
                  const SizedBox(height: 10),
                   Text(
                    AppLocalizations.of(context).translate("enter_email"),
                    style: TextStyle(
                      color: Color(0xFF4F6DA3),
                      fontSize: 16,
                    ),
                    textAlign: TextAlign.center,
                  ),
                  const SizedBox(height: 20),
                  buildEmailField(),
                  const SizedBox(height: 24),
                  buildButton(AppLocalizations.of(context).translate("send_verification_code"), goToVerifyPage),
                ],
              ),
            ),
          ),
        ],
      ),
    );
  }

  Widget buildEmailField() {
    return Column(
      crossAxisAlignment: CrossAxisAlignment.end,
      children: [
         Text(
          AppLocalizations.of(context).translate("email"),
          style: TextStyle(
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
            controller: emailController,
            keyboardType: TextInputType.emailAddress,
            textAlign: TextAlign.right,
            decoration:  InputDecoration(
              hintText: AppLocalizations.of(context).translate("enter_email"),
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
          shape:
              RoundedRectangleBorder(borderRadius: BorderRadius.circular(30)),
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

