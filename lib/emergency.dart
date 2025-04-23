import 'dart:convert';
import 'package:flutter/material.dart';
import 'package:http/http.dart' as http;
import 'package:shared_preferences/shared_preferences.dart';
import 'package:url_launcher/url_launcher.dart';

class EmergencyPage extends StatefulWidget {
  @override
  _EmergencyPageState createState() => _EmergencyPageState();
}

class _EmergencyPageState extends State<EmergencyPage> {
  final String baseUrl = "https://anees-rus4.onrender.com";
  List<Map<String, String>> emergencyContacts = [];
  List<Map<String, String>> emergencyLinks = [];

  final TextEditingController nameController = TextEditingController();
  final TextEditingController phoneController = TextEditingController();
  final TextEditingController linkNameController = TextEditingController();
  final TextEditingController linkUrlController = TextEditingController();

  @override
  void initState() {
    super.initState();
    loadFromStorage().then((_) => fetchEmergencyData());
  }

  Future<void> loadFromStorage() async {
    final prefs = await SharedPreferences.getInstance();
    final contactsJson = prefs.getString('emergencyContacts');
    final linksJson = prefs.getString('emergencyLinks');

    if (contactsJson != null) {
      emergencyContacts = List<Map<String, String>>.from(jsonDecode(contactsJson));
    }
    if (linksJson != null) {
      emergencyLinks = List<Map<String, String>>.from(jsonDecode(linksJson));
    }

    setState(() {});
  }

  Future<void> saveToStorage() async {
    final prefs = await SharedPreferences.getInstance();
    await prefs.setString('emergencyContacts', jsonEncode(emergencyContacts));
    await prefs.setString('emergencyLinks', jsonEncode(emergencyLinks));
  }

  Future<void> fetchEmergencyData() async {
    final prefs = await SharedPreferences.getInstance();
    final username = prefs.getString("username");
    if (username == null) return;

    try {
      final response = await http.get(Uri.parse("$baseUrl/emergency?username=$username"));
      if (response.statusCode == 200) {
        final data = jsonDecode(response.body);
        final serverContacts = List<Map<String, String>>.from(data["contacts"]);

        setState(() {
          emergencyContacts = serverContacts;
          emergencyLinks = [
            {
              "name": "المركز الوطني للصحة النفسية",
              "url": data["mental_health_center"]
            }
          ];
        });

        await saveToStorage();
      }
    } catch (e) {
      print("خطأ في جلب البيانات: $e");
    }
  }

  Future<void> sendToServer(String name, String phone) async {
    final prefs = await SharedPreferences.getInstance();
    final username = prefs.getString('username');
    if (username == null) return;

    try {
      final response = await http.post(
        Uri.parse('$baseUrl/add_emergency_contact'),
        headers: {'Content-Type': 'application/json'},
        body: jsonEncode({
          "username": username,
          "name": name,
          "phone": phone,
        }),
      );
      if (response.statusCode == 201) {
        print("تم الحفظ في قاعدة البيانات");
      } else {
        print("فشل الحفظ في قاعدة البيانات: ${response.body}");
      }
    } catch (e) {
      print("خطأ أثناء الإرسال: $e");
    }
  }

  void _callNumber(String number) async {
    final Uri phoneUri = Uri(scheme: 'tel', path: number);
    if (await canLaunchUrl(phoneUri)) {
      await launchUrl(phoneUri);
    }
  }

  void _openWebsite(String url) async {
    final Uri uri = Uri.parse(url);
    if (await canLaunchUrl(uri)) {
      await launchUrl(uri);
    }
  }

  void showContactDialog() {
    showDialog(
      context: context,
      builder: (context) {
        return AlertDialog(
          title: const Text("إضافة جهة اتصال جديدة"),
          content: Column(
            mainAxisSize: MainAxisSize.min,
            children: [
              TextField(controller: nameController, decoration: const InputDecoration(labelText: "اسم جهة الاتصال")),
              TextField(controller: phoneController, decoration: const InputDecoration(labelText: "رقم الهاتف"), keyboardType: TextInputType.phone),
            ],
          ),
          actions: [
            TextButton(
              onPressed: () {
                final name = nameController.text.trim();
                final phone = phoneController.text.trim();
                final contact = {"name": name, "phone": phone};

                if (name.isNotEmpty && phone.isNotEmpty &&
                    !emergencyContacts.any((c) => c["name"] == name && c["phone"] == phone)) {
                  setState(() {
                    emergencyContacts.add(contact);
                  });
                  saveToStorage();
                  sendToServer(name, phone);
                }

                nameController.clear();
                phoneController.clear();
                Navigator.pop(context);
              },
              child: const Text("حفظ"),
            ),
          ],
        );
      },
    );
  }

  Widget buildContactCard(String name, String phone) {
    return Container(
      margin: const EdgeInsets.symmetric(vertical: 5),
      padding: const EdgeInsets.all(15),
      decoration: BoxDecoration(color: Colors.white, borderRadius: BorderRadius.circular(15)),
      child: Row(
        mainAxisAlignment: MainAxisAlignment.spaceBetween,
        children: [
          IconButton(icon: const Icon(Icons.phone, color: Color(0xFF4F6DA3), size: 30), onPressed: () => _callNumber(phone)),
          Expanded(
            child: Column(
              crossAxisAlignment: CrossAxisAlignment.end,
              children: [
                Text(name, style: const TextStyle(fontSize: 18, fontWeight: FontWeight.bold)),
                Text(phone, style: const TextStyle(fontSize: 16, color: Colors.grey)),
              ],
            ),
          ),
          const Icon(Icons.person, color: Color(0xFF4F6DA3), size: 30),
        ],
      ),
    );
  }

  Widget buildAddButton(String text, VoidCallback onPressed) {
    return ElevatedButton.icon(
      onPressed: onPressed,
      icon: const Icon(Icons.add_circle_outline, color: Color(0xFF4F6DA3)),
      label: Text(text, style: const TextStyle(fontSize: 18, color: Color(0xFF4F6DA3))),
    );
  }

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      backgroundColor: const Color(0xFFC2D5F2),
      appBar: AppBar(
        backgroundColor: const Color(0xFF4F6DA3),
        elevation: 0,
        title: const Text("جهات الطوارئ", style: TextStyle(color: Colors.white, fontSize: 22)),
        centerTitle: true,
        leading: IconButton(
          icon: const Icon(Icons.arrow_back_ios, color: Colors.white),
          onPressed: () => Navigator.pop(context),
        ),
      ),
      body: Stack(
        children: [
          Positioned.fill(
            child: Opacity(
              opacity: 0.3,
              child: Image.asset("assets/h.png", fit: BoxFit.cover),
            ),
          ),
          Column(
            children: [
              const SizedBox(height: 20),
              const Text("جهات الاتصال الطارئة", style: TextStyle(fontSize: 22, fontWeight: FontWeight.bold, color: Color(0xFF4F6DA3))),
              Expanded(
                child: ListView(
                  padding: const EdgeInsets.symmetric(horizontal: 20),
                  children: [
                    for (var contact in emergencyContacts)
                      buildContactCard(contact["name"]!, contact["phone"]!),
                    buildAddButton("إضافة جهة اتصال أخرى", showContactDialog),
                  ],
                ),
              ),
              const SizedBox(height: 20),
              const Text("روابط الدعم النفسي", style: TextStyle(fontSize: 18, fontWeight: FontWeight.bold, color: Color(0xFF4F6DA3))),
              Expanded(
                child: ListView(
                  padding: const EdgeInsets.symmetric(horizontal: 20),
                  children: [
                    for (var link in emergencyLinks)
                      GestureDetector(
                        onTap: () => _openWebsite(link["url"]!),
                        child: Container(
                          margin: const EdgeInsets.symmetric(vertical: 5),
                          padding: const EdgeInsets.all(15),
                          decoration: BoxDecoration(color: Colors.white, borderRadius: BorderRadius.circular(15)),
                          child: Text(link["name"]!, style: const TextStyle(fontSize: 18, color: Colors.blue)),
                        ),
                      ),
                    buildAddButton("إضافة رابط آخر", showLinkDialog),
                  ],
                ),
              ),
              const SizedBox(height: 30),
            ],
          ),
        ],
      ),
    );
  }

  void showLinkDialog() {
    showDialog(
      context: context,
      builder: (context) {
        return AlertDialog(
          title: const Text("إضافة رابط جديد"),
          content: Column(
            mainAxisSize: MainAxisSize.min,
            children: [
              TextField(controller: linkNameController, decoration: const InputDecoration(labelText: "اسم الموقع أو الجهة")),
              TextField(controller: linkUrlController, decoration: const InputDecoration(labelText: "الرابط الإلكتروني"), keyboardType: TextInputType.url),
            ],
          ),
          actions: [
            TextButton(
              onPressed: () {
                final name = linkNameController.text.trim();
                final url = linkUrlController.text.trim();

                if (name.isNotEmpty && url.isNotEmpty) {
                  final Map<String, String> link = {"name": name, "url": url};

                  final exists = emergencyLinks.any((l) => l["url"] == url);
                  if (!exists) {
                    setState(() {
                      emergencyLinks.add(link);
                    });
                    saveToStorage();
                  }
                }

                linkNameController.clear();
                linkUrlController.clear();
                Navigator.pop(context);
              },
              child: const Text("حفظ"),
            ),
          ],
        );
      },
    );
  }
}
