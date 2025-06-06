import 'dart:convert';
import 'package:flutter/material.dart';
import 'package:http/http.dart' as http;
import 'signin.dart';
import 'app_localizations.dart';
import 'package:shared_preferences/shared_preferences.dart';

class ProfileUpdatePage extends StatefulWidget {
  final String userName; 

  const ProfileUpdatePage({required this.userName, Key? key}) : super(key: key);

  @override
  _ProfileUpdatePageState createState() => _ProfileUpdatePageState();
}

class _ProfileUpdatePageState extends State<ProfileUpdatePage> {
  final TextEditingController usernameController = TextEditingController();
  final TextEditingController emailController = TextEditingController();
  final TextEditingController passwordController = TextEditingController();
  final TextEditingController botNameController = TextEditingController();
  final TextEditingController chatpasswordController = TextEditingController();

  final String baseUrl = "https://anees-rus4.onrender.com";
  String displayName = "أنيس";

  bool _isMainPasswordVisible = false;
  bool _isChatPasswordVisible = false;
  late String _username;

  @override
  void initState() {
    super.initState();
    _username = widget.userName; 
    fetchUserProfile(_username); 
  }

  Future<void> fetchUserProfile(String username) async {
    try {
      final response = await http.post(
        Uri.parse("$baseUrl/profile"),
        headers: {"Content-Type": "application/json"},
        body: jsonEncode({"username": username}),
      );

      print("Profile Response status: ${response.statusCode}");
      print("Profile Response body: ${response.body}");

      if (response.statusCode == 200) {
        final data = jsonDecode(response.body);
        setState(() {
          usernameController.text = data['username'] ?? "";
          displayName = data['username'] ?? "أنيس";
          emailController.text = data['email'] ?? "";
          passwordController.text = data['password'] ?? "";
          botNameController.text = data['bot_name'] ?? "";
          chatpasswordController.text = data['chat_password'] ?? "";
        });
      } else {
        ScaffoldMessenger.of(context).showSnackBar(
          SnackBar(content: Text(AppLocalizations.of(context).translate("failed_to_fetch_profile"))),
        );
      }
    } catch (e) {
      print("Exception during fetchProfile: $e");
      ScaffoldMessenger.of(context).showSnackBar(
        SnackBar(content: Text(AppLocalizations.of(context).translate("connection_error"))),
      );
    }
  }

  Future<void> updateUserProfile() async {
    final chatPassword = chatpasswordController.text.trim();
    if (chatPassword.length != 6 || !RegExp(r'^\d+$').hasMatch(chatPassword)) {
      ScaffoldMessenger.of(context).showSnackBar(
         SnackBar(content: Text(AppLocalizations.of(context).translate("chat_password_invalid"))),
      );
      return;
    }

    final response = await http.post(
      Uri.parse("$baseUrl/update_profile"),
      headers: {"Content-Type": "application/json"},
      body: jsonEncode({
        "username": usernameController.text.trim(),
        "email": emailController.text.trim(),
        "bot_name": botNameController.text.trim(),
        "chat_password": chatPassword,
      }),
    );

    if (response.statusCode == 200) {
      setState(() {
        displayName = usernameController.text.trim();
      });
      ScaffoldMessenger.of(context).showSnackBar(
         SnackBar(content: Text(AppLocalizations.of(context).translate("update_success"))),
      );
    } else {
      ScaffoldMessenger.of(context).showSnackBar(
         SnackBar(content: Text(AppLocalizations.of(context).translate("update_failed"))),
      );
    }
  }

  Future<void> _logout() async {
    final prefs = await SharedPreferences.getInstance();
    await prefs.clear();
    Navigator.pushAndRemoveUntil(
      context,
      MaterialPageRoute(builder: (_) => const SignInPage()),
      (route) => false,
    );
  }

  @override
  Widget build(BuildContext context) {
    return Directionality(
      textDirection: TextDirection.rtl,
      child: Scaffold(
        backgroundColor: const Color(0xFFC2D5F2),
        body: Stack(
          children: [
            Container(
              height: 250,
              decoration: const BoxDecoration(
                color: Color(0xFF4F6DA3),
                borderRadius: BorderRadius.only(
                  bottomLeft: Radius.circular(50),
                  bottomRight: Radius.circular(50),
                ),
              ),
            ),
            Column(
              children: [
                const SizedBox(height: 50),
                Padding(
                  padding: const EdgeInsets.symmetric(horizontal: 15),
                  child: Align(
                    alignment: Alignment.centerLeft,
                    child: IconButton(
                      icon: const Icon(Icons.arrow_forward_ios, color: Colors.white),
                      onPressed: () => Navigator.pop(context),
                    ),
                  ),
                ),
                const SizedBox(height: 10),
                Stack(
                  alignment: Alignment.center,
                  children: [
                    const CircleAvatar(
                      radius: 50,
                      backgroundColor: Colors.white,
                      child: Icon(Icons.person, size: 60, color: Color(0xFF4F6DA3)),
                    ),
                  ],
                ),
                const SizedBox(height: 10),
                Text(
                  "${AppLocalizations.of(context).translate("welcome")} $displayName",
                  style: const TextStyle(
                    fontSize: 22,
                    fontWeight: FontWeight.bold,
                    color: Colors.white,
                  ),
                ),
                const SizedBox(height: 10),
                Expanded(
                  child: SingleChildScrollView(
                    padding: const EdgeInsets.symmetric(horizontal: 20),
                    child: Container(
                      margin: const EdgeInsets.only(bottom: 20),
                      padding: const EdgeInsets.all(15),
                      decoration: BoxDecoration(
                        color: Colors.white,
                        borderRadius: BorderRadius.circular(20),
                      ),
                      child: Column(
                        children: [
                          buildProfileField(AppLocalizations.of(context).translate("username"), usernameController),
                          buildProfileField(AppLocalizations.of(context).translate("email"), emailController),
                          buildProfileField(AppLocalizations.of(context).translate("password"), passwordController, isPassword: true, isMainPassword: true),
                          buildProfileField(AppLocalizations.of(context).translate("bot_name"), botNameController),
                          buildProfileField(AppLocalizations.of(context).translate("chat_password"), chatpasswordController, isPassword: true),
                          const SizedBox(height: 25),
                          buildActionButton(AppLocalizations.of(context).translate("save"), updateUserProfile, const Color(0xFF4F6DA3)),
                          const SizedBox(height: 12),
                          buildActionButton(AppLocalizations.of(context).translate("logout"), _logout, const Color.fromARGB(255, 173, 72, 72)),
                        ],
                      ),
                    ),
                  ),
                ),
              ],
            ),
          ],
        ),
      ),
    );
  }

  Widget buildProfileField(String title, TextEditingController controller, {bool isPassword = false, bool isMainPassword = false}) {
    return Padding(
      padding: const EdgeInsets.only(bottom: 15),
      child: Column(
        crossAxisAlignment: CrossAxisAlignment.start,
        children: [
          Text(
            title,
            style: const TextStyle(
              fontSize: 16,
              fontWeight: FontWeight.bold,
              color: Color(0xFF4F6DA3),
            ),
          ),
          const SizedBox(height: 5),
          TextField(
            controller: controller,
            readOnly: isMainPassword,
            obscureText: isPassword
                ? (isMainPassword ? !_isMainPasswordVisible : !_isChatPasswordVisible)
                : false,
            textAlign: TextAlign.right,
            decoration: InputDecoration(
              contentPadding: const EdgeInsets.symmetric(horizontal: 12, vertical: 8),
              filled: true,
              fillColor: const Color(0xFFE9F1F4),
              border: OutlineInputBorder(
                borderRadius: BorderRadius.circular(32),
                borderSide: BorderSide.none,
              ),
              suffixIcon: isPassword
                  ? IconButton(
                      icon: Icon(
                        (isMainPassword ? _isMainPasswordVisible : _isChatPasswordVisible)
                            ? Icons.visibility
                            : Icons.visibility_off,
                        color: Colors.grey,
                      ),
                      onPressed: () {
                        setState(() {
                          if (isMainPassword) {
                            _isMainPasswordVisible = !_isMainPasswordVisible;
                          } else {
                            _isChatPasswordVisible = !_isChatPasswordVisible;
                          }
                        });
                      },
                    )
                  : null,
            ),
          ),
        ],
      ),
    );
  }

  Widget buildActionButton(String text, VoidCallback onPressed, Color color) {
    return SizedBox(
      width: double.infinity,
      child: ElevatedButton(
        onPressed: onPressed,
        style: ElevatedButton.styleFrom(
          backgroundColor: color,
          padding: const EdgeInsets.symmetric(vertical: 14),
          shape: RoundedRectangleBorder(borderRadius: BorderRadius.circular(32)),
        ),
        child: Text(text, style: const TextStyle(fontSize: 16, color: Colors.white)),
      ),
    );
  }
}
