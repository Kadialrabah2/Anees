import 'package:flutter/material.dart';
import 'chat/physical_activity.dart';
import 'chat/mindfulness.dart';
import 'chat/cognitive_therapy.dart';
import 'chat/chat_password.dart';
import 'app_localizations.dart';


class TreatmentPage extends StatelessWidget {
  const TreatmentPage({Key? key}) : super(key: key);

  @override
  Widget build(BuildContext context) {
    final loc = AppLocalizations.of(context);
    return Scaffold(
      backgroundColor: const Color(0xFFC2D5F2),
      body: Stack(
        children: [
          Positioned.fill(
            child: Opacity(
              opacity: 0.7,
              child: Image.asset("assets/h.png"),
            ),
          ),
          Positioned(
            top: 50,
            left: 15,
            child: IconButton(
              icon: const Icon(Icons.arrow_back_ios, color: Color(0xFF4F6DA3), size: 30),
              onPressed: () => Navigator.pop(context),
            ),
          ),
          Column(
            mainAxisAlignment: MainAxisAlignment.center,
            children: [
              Expanded(
                child: Padding(
                  padding: const EdgeInsets.symmetric(horizontal: 38),
                  child: Column(
                    mainAxisAlignment: MainAxisAlignment.center,
                    children: [
                      buildTreatmentButton(
                        context,
                        loc.translate("treatment_physical"),
                        Icons.directions_run,
                        () => Navigator.push(
                          context,
                          MaterialPageRoute(
                            builder: (_) => const ChatPasswordPage(
                              nextPage: PhysicalActivityPage(),
                            ),
                          ),
                        ),
                      ),
                      const SizedBox(height: 20),
                      buildTreatmentButton(
                        context,
                        loc.translate("treatment_mindfulness"),
                        Icons.psychology,
                        () => Navigator.push(
                          context,
                          MaterialPageRoute(
                            builder: (_) => const ChatPasswordPage(
                              nextPage: MindfulnessPage(),
                            ),
                          ),
                        ),
                      ),
                      const SizedBox(height: 20),
                      buildTreatmentButton(
                        context,
                        loc.translate("treatment_cognitive"),
                        Icons.favorite,
                        () => Navigator.push(
                          context,
                          MaterialPageRoute(
                            builder: (_) => const ChatPasswordPage(
                              nextPage: CognitiveTherapyPage(),
                            ),
                          ),
                        ),
                      ),
                    ],
                  ),
                ),
              ),
            ],
          ),
        ],
      ),
    );
  }

  Widget buildTreatmentButton(BuildContext context, String text, IconData icon, VoidCallback onPressed) {
    return ElevatedButton(
      onPressed: onPressed,
      style: ElevatedButton.styleFrom(
        backgroundColor: Colors.white,
        padding: const EdgeInsets.symmetric(vertical: 28, horizontal: 20),
        shape: RoundedRectangleBorder(
          borderRadius: BorderRadius.circular(20),
        ),
        elevation: 4,
        shadowColor: Colors.black.withOpacity(0.7),
      ),
      child: Row(
        mainAxisAlignment: MainAxisAlignment.start,
        children: [
          Icon(icon, size: 53, color: Color(0xFF4F6DA3)),
          const SizedBox(width: 23),
          Expanded(
            child: Text(
              text,
              style: const TextStyle(
                color: Color(0xFF4F6DA3),
                fontSize: 26,
                fontWeight: FontWeight.bold,
              ),
            ),
          ),
        ],
      ),
    );
  }
}
