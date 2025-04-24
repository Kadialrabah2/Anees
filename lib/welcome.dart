import 'package:flutter/material.dart';
import 'signup.dart';
import 'signin.dart';
import 'package:flutter/services.dart';
import 'app_localizations.dart';


class WelcomePage extends StatelessWidget {
  @override
  Widget build(BuildContext context) {
    final loc = AppLocalizations.of(context);
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
              loc.translate("welcome_title"),
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
                  text:  TextSpan(
                    style: TextStyle(
                      color: Color(0xFF4F6DA3),
                      fontSize: 18,
                    ),
                    children: [
                      TextSpan(text:loc.translate("welcome_description_1")),
                      TextSpan(
                        text: loc.translate("welcome_app_name"),
                        style: TextStyle(fontWeight: FontWeight.bold),
                      ),
                      TextSpan(
                          text: loc.translate("welcome_description_2")),
                    ],
                  ),
                ),
              ),
            ),

            const SizedBox(height: 40),

          buildButton(loc.translate("sign_in"), () {
            Navigator.push(
            context,
            MaterialPageRoute(builder: (context) => SignInPage()),
            );
              }),
          const SizedBox(height: 15),
          buildButton(loc.translate("sign_up"), () {
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