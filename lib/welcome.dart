import 'package:flutter/material.dart';
import 'signup.dart';
import 'signin.dart';

class WelcomePage extends StatelessWidget {
  @override
  Widget build(BuildContext context) {
    return Scaffold(
      backgroundColor: const Color(0xFFC2D5F2),
      body: Padding(
        padding: const EdgeInsets.symmetric(horizontal: 24, vertical: 40),
        child: Column(
          children: [
            const Spacer(),

            Image.asset("assets/انيس.png", height: 220),
            const SizedBox(height: 20),

            Text(
              "أهلًا بك في أنيس،\n حيث تجد من يصغي إليك دائمًا.",
              style: const TextStyle(
                color: Color(0xFF4F6DA3),
                fontSize: 25,
                fontWeight: FontWeight.bold,
              ),
              textAlign: TextAlign.center,
              textDirection: TextDirection.rtl,
            ),

            const SizedBox(height: 30),

            Expanded(
              child: Align(
                alignment: Alignment.bottomCenter,
                child: RichText(
                  textAlign: TextAlign.center,
                  textDirection: TextDirection.rtl,
                  text: const TextSpan(
                    style: TextStyle(
                      color: Color(0xFF4F6DA3),
                      fontSize: 18,
                      fontWeight: FontWeight.w500,
                    ),
                    children: [
                      TextSpan(text: "عبّر عن نفسك براحة وطمأنينة، "),
                      TextSpan(
                        text: "أنيس ",
                        style: TextStyle(fontWeight: FontWeight.bold),
                      ),
                      TextSpan(
                          text: "هنا\nليكون رفيق رحلتك نحو صحة نفسية أفضل."),
                    ],
                  ),
                ),
              ),
            ),

            const SizedBox(height: 40),

            buildButton(context, 'تسجيل الدخول', () {
              Navigator.push(
                context,
                MaterialPageRoute(builder: (context) => SignInPage()),
              );
            }),
            const SizedBox(height: 15),
            buildButton(context, 'إنشاء حساب', () {
              Navigator.push(
                context,
                MaterialPageRoute(builder: (context) => SignUpPage()),
              );
            }),

            const SizedBox(height: 50),
          ],
        ),
      ),
    );
  }

  Widget buildButton(BuildContext context, String text, VoidCallback onPressed) {
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
          elevation: 5,
        ),
        child: Text(
          text,
          style: const TextStyle(
            color: Colors.white,
            fontSize: 20,
          ),
        ),
      ),
    );
  }
}
