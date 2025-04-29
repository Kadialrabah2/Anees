import 'package:flutter/material.dart';
import 'treatment.dart';
import 'chat/talk_to_me.dart';
import 'chat/chat_password.dart';
import 'profile_update.dart';
import 'progress_tracker.dart';
import 'app_localizations.dart';
import 'main.dart';

class HomePage extends StatefulWidget {
  final int initialIndex;
  final String userName; 

  const HomePage({Key? key, required this.userName, this.initialIndex = 0}) : super(key: key);

  @override
  _HomePageState createState() => _HomePageState();
}

class _HomePageState extends State<HomePage> {
  late int _selectedIndex;
  late String _username; 

  @override
  void initState() {
    super.initState();
    _selectedIndex = widget.initialIndex;
    _username = widget.userName; // ✅ ناخذ اليوزر اللي جاينا
  }

  void _onItemTapped(int index) {
    if (index == 2) {
      Navigator.push(
        context,
        MaterialPageRoute(builder: (context) => ProfileUpdatePage(userName: _username)), // ✅ نمرره للصفحة
      );
    } else if (index == 1) {
      Navigator.push(
        context,
        MaterialPageRoute(builder: (context) => ProgressTrackerPage(userName: _username)
),
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
        automaticallyImplyLeading: false,
        title: const SizedBox.shrink(),
        backgroundColor: const Color(0xFFC2D5F2),
        elevation: 0, 
        actions: [
          IconButton(
            icon: const Icon(Icons.language, color: Color(0xFF4F6DA3)),
            onPressed: () {
              Locale currentLocale = Localizations.localeOf(context);
              Locale newLocale = currentLocale.languageCode == 'ar'
                  ? const Locale('en')
                  : const Locale('ar');
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
          ProgressTrackerPage(userName: _username),
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
        items: [
          BottomNavigationBarItem(
            icon: const Icon(Icons.home),
            label: AppLocalizations.of(context).translate("home"),
          ),
          BottomNavigationBarItem(
            icon: const Icon(Icons.bar_chart),
            label: AppLocalizations.of(context).translate("reports"),
          ),
          BottomNavigationBarItem(
            icon: const Icon(Icons.person),
            label: AppLocalizations.of(context).translate("my_account"),
          ),
        ],
      ),
    );
  }

  Widget buildMainHome(BuildContext context) {
    return Stack(
      children: [
        Positioned.fill(
          child: Opacity(
            opacity: 0.5,
            child: Image.asset("assets/h.png"),
          ),
        ),
        Center(
          child: Padding(
            padding: const EdgeInsets.symmetric(horizontal: 32), 
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
                    MaterialPageRoute(
                      builder: (context) => TreatmentPage(),
                    ),
                  ),
                ),
              ],
            ),
          ),
        ),
      ],
    );
  }

  Widget buildOptionButton(BuildContext context, String text, String? iconPath, VoidCallback onPressed) {
    return SizedBox(
      width: double.infinity,
      height: 100, 
      child: ElevatedButton(
        onPressed: onPressed,
        style: ElevatedButton.styleFrom(
          backgroundColor: Colors.white,
          padding: const EdgeInsets.symmetric(horizontal: 20),
          shape: RoundedRectangleBorder(borderRadius: BorderRadius.circular(30)),
          elevation: 4,
          shadowColor: Colors.black.withOpacity(0.4),
        ),
        child: Row(
          mainAxisAlignment: MainAxisAlignment.center,
          children: [
            if (iconPath != null) ...[
              Image.asset(iconPath, height: 65, width: 65), 
              const SizedBox(width: 10),
            ],
            Flexible(
              child: Text(
                text,
                style: const TextStyle(
                  color: Color(0xFF4F6DA3),
                  fontSize: 26,
                  fontWeight: FontWeight.bold,
                ),
                overflow: TextOverflow.ellipsis,
              ),
            ),
          ],
        ),
      ),
    );
  }
}
