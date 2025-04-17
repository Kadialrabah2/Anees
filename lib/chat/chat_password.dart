import 'package:flutter/material.dart';

class ChatPasswordPage extends StatefulWidget {
  final Widget nextPage;

  const ChatPasswordPage({super.key, required this.nextPage});

  @override
  _ChatPasswordPageState createState() => _ChatPasswordPageState();
}

class _ChatPasswordPageState extends State<ChatPasswordPage> {
  final TextEditingController passwordController = TextEditingController();
  final String correctPassword = "123456";
  bool isLoading = false;

  void _checkPassword() {
    final enteredPassword = passwordController.text.trim();

    if (enteredPassword.isEmpty) {
      ScaffoldMessenger.of(context).showSnackBar(
        const SnackBar(content: Text("أدخل كلمة المرور")),
      );
      return;
    }

    setState(() => isLoading = true);

    Future.delayed(const Duration(milliseconds: 800), () {
      setState(() => isLoading = false);
      if (enteredPassword == correctPassword) {
        Navigator.pushReplacement(
          context,
          MaterialPageRoute(builder: (_) => widget.nextPage),
        );
      } else {
        ScaffoldMessenger.of(context).showSnackBar(
          const SnackBar(content: Text("كلمة المرور غير صحيحة")),
        );
      }
    });
  }

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      backgroundColor: const Color(0xFFC2D5F2),
      body: Padding(
        padding: const EdgeInsets.fromLTRB(24, 140, 24, 40), 
        child: Column(
          children: [
            Image.asset("assets/انيس.png", height:240), 
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
              "يرجى إدخال كلمة المرور",
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
            decoration: const InputDecoration(
              hintText: '••••••',
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