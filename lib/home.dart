import 'package:flutter/material.dart';
import 'treatment.dart';
import 'chat/talk_to_me.dart';
import 'chat/chat_password.dart';
import 'profile_update.dart';
import 'progress_tracker.dart';
import 'app_localizations.dart';
import 'package:flutter_localizations/flutter_localizations.dart';
import 'main.dart';


class HomePage extends StatefulWidget {
  
  final int initialIndex;
  const HomePage({Key? key, this.initialIndex = 0,}) : super(key: key);

  @override
  _HomePageState createState() => _HomePageState();
}

class _HomePageState extends State<HomePage> { 
  late int _selectedIndex;
  String errorMessage = "";

  @override
  void initState() {
    super.initState();
    _selectedIndex = widget.initialIndex;
  }

  void _onItemTapped(int index) {
    if (index == 2) {
      Navigator.push(
        context,
        MaterialPageRoute(builder: (context) => ProfileUpdatePage()),
      );
    } else if (index == 1) {
      Navigator.push(
        context,
        MaterialPageRoute(builder: (context) => const ProgressTrackerPage()),
      );
    } else {
      setState(() {
        _selectedIndex = index;
      });
    }
  }
 

  @override
  Widget build(BuildContext context) {
    
    return Scaffold(
      backgroundColor: const Color(0xFFC2D5F2),
      appBar: AppBar(
        title: Text(AppLocalizations.of(context).translate("home")),
        actions: [
          IconButton(
            icon: Icon(Icons.language),
            onPressed:() {
  Locale currentLocale = Localizations.localeOf(context);
  Locale newLocale = currentLocale.languageCode == 'ar' ? const Locale('en') : const Locale('ar');
  MyApp.setLocale(context, newLocale);
},
            tooltip: AppLocalizations.of(context).translate("switch_language"),
          ),
        ],
      ),
      body: IndexedStack(
        index: _selectedIndex,
        children: [
          buildMainHome(context),
          Container(),
          Container(),
        ],
      ),
      bottomNavigationBar: BottomNavigationBar(
        backgroundColor: Colors.white,
        selectedItemColor: const Color(0xFF4F6DA3),
        unselectedItemColor: Colors.grey,
        showSelectedLabels: false,
        showUnselectedLabels: false,
        currentIndex: _selectedIndex,
        onTap: _onItemTapped,
        items:  [
          BottomNavigationBarItem(icon: Icon(Icons.home), label: AppLocalizations.of(context).translate("home")),
          BottomNavigationBarItem(icon: Icon(Icons.bar_chart), label: AppLocalizations.of(context).translate("reports")),
          BottomNavigationBarItem(icon: Icon(Icons.person), label: AppLocalizations.of(context).translate("my_account")),
        ],
      ),
    );
  }

  Widget buildMainHome(BuildContext context) {
    return Stack(
      children: [
        Positioned.fill(
          child: Opacity(
            opacity: 0.9,
            child: Image.asset("assets/h.png"),
          ),
        ),
        Column(
          mainAxisAlignment: MainAxisAlignment.center,
          children: [
            Expanded(
              child: Padding(
                padding: const EdgeInsets.symmetric(horizontal: 44),
                child: Column(
                  mainAxisAlignment: MainAxisAlignment.center,
                  children: [
                    buildOptionButton(
                      context,
                      AppLocalizations.of(context).translate("talk_to_me"),
                      "assets/hs.png",
                      () => Navigator.push(
                        context,
                        MaterialPageRoute(
                          builder: (context) => ChatPasswordPage(
                            nextPage: TalkToMePage(),
                          ),
                        ),
                      ),
                    ),
                    const SizedBox(height: 20),
                    buildOptionButton(
                      context,
                      AppLocalizations.of(context).translate("start_treatment"),
                      "assets/f.png",
                      () => Navigator.push(
                        context,
                        MaterialPageRoute(builder: (context) => TreatmentPage()),
                      ),
                    ),
                  ],
                ),
              ),
            ),
            if (errorMessage.isNotEmpty)
              Padding(
                padding: const EdgeInsets.all(16),
                child: Text(
                  errorMessage,
                  style: const TextStyle(color: Colors.red, fontSize: 16),
                  textAlign: TextAlign.center,
                ),
              ),
          ],
        ),
      ],
    );
  }

  Widget buildOptionButton(BuildContext context, String text, String? iconPath, VoidCallback onPressed, {bool isMain = false}) {
    return ElevatedButton(
      onPressed: onPressed,
      style: ElevatedButton.styleFrom(
        backgroundColor: Colors.white,
        padding: isMain
            ? const EdgeInsets.symmetric(vertical: 10, horizontal: 30)
            : const EdgeInsets.all(20),
        shape: RoundedRectangleBorder(borderRadius: BorderRadius.circular(30)),
        elevation: 4,
        shadowColor: Colors.black.withOpacity(0.7),
      ),
      child: iconPath != null
          ? Row(
              mainAxisAlignment: MainAxisAlignment.center,
              children: [
                Image.asset(iconPath, height: 70, width: 70),
                const SizedBox(width: 10),
                Text(
                  text,
                  style: const TextStyle(color: Color(0xFF4F6DA3), fontSize: 28, fontWeight: FontWeight.bold),
                ),
              ],
            )
          : Text(
              text,
              style: const TextStyle(color: Color(0xFF4F6DA3), fontSize: 18, fontWeight: FontWeight.bold),
            ),
    );
  }
}