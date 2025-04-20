 import 'package:flutter/material.dart';
import 'chat/physical_activity.dart';
import 'chat/mindfulness.dart';
import 'chat/cognitive_therapy.dart';

class TreatmentPage extends StatelessWidget {
  final String? userName;

  const TreatmentPage({Key? key, this.userName}) : super(key: key);
  @override
  Widget build(BuildContext context) {
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
                        "النشاط البدني",
                        Icons.directions_run,
                        () => Navigator.push(context, MaterialPageRoute(builder: (_) => PhysicalActivityPage(userName: userName))),
                      ),
                      const SizedBox(height: 20),
                      buildTreatmentButton(
                        context,
                        "الوعي الذاتي",
                        Icons.psychology,
                        () => Navigator.push(context, MaterialPageRoute(builder: (_) => MindfulnessPage(userName: userName))),
                      ),
                      const SizedBox(height: 20),
                      buildTreatmentButton(
                        context,
                        "العلاج المعرفي",
                        Icons.favorite,
                        () => Navigator.push(context, MaterialPageRoute(builder: (_) => HealthyLifestylePage(userName: userName))),
                      ),
                    ],
                  ),
                ),
              ),
            ],
          ),
        ],
      ),
      bottomNavigationBar: BottomNavigationBar(
        backgroundColor: Colors.white,
        selectedItemColor: const Color(0xFF4F6DA3),
        unselectedItemColor: Colors.grey,
        showSelectedLabels: false,
        showUnselectedLabels: false,
        items: const [
          BottomNavigationBarItem(icon: Icon(Icons.home), label: "الرئيسية"),
          BottomNavigationBarItem(icon: Icon(Icons.bar_chart), label: "التقارير"),
          BottomNavigationBarItem(icon: Icon(Icons.person), label: "حسابي"),
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