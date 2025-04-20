import 'dart:convert';
import 'package:flutter/material.dart';
import 'package:http/http.dart' as http;
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
    fetchEmergencyData();
  }

  Future<void> fetchEmergencyData() async {
    try {
      final response = await http.get(Uri.parse("$baseUrl/emergency"));
      if (response.statusCode == 200) {
        final data = jsonDecode(response.body);
        setState(() {
          emergencyContacts = List<Map<String, String>>.from(data["contacts"]);
          emergencyLinks = List<Map<String, String>>.from(data["links"]);
        });
      }
    } catch (e) {
      print("خطأ في جلب البيانات: $e");
    }
  }

  void _callNumber(String number) async {
    final Uri phoneUri = Uri(scheme: 'tel', path: number);
    if (await canLaunchUrl(phoneUri)) {
      await launchUrl(phoneUri);
    } else {
      print("لا يمكن الاتصال بالرقم $number");
    }
  }

  void _openWebsite(String url) async {
    final Uri uri = Uri.parse(url);
    if (await canLaunchUrl(uri)) {
      await launchUrl(uri);
    } else {
      print("لا يمكن فتح الرابط");
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
              TextField(
                controller: nameController,
                decoration: const InputDecoration(labelText: "الاسم"),
              ),
              TextField(
                controller: phoneController,
                decoration: const InputDecoration(labelText: "رقم الهاتف"),
                keyboardType: TextInputType.phone,
              ),
            ],
          ),
          actions: [
            TextButton(
              onPressed: () {
                setState(() {
                  emergencyContacts.add({"name": nameController.text, "phone": phoneController.text});
                });
                nameController.clear();
                phoneController.clear();
                Navigator.pop(context);
              },
              child: const Text("إضافة"),
            ),
          ],
        );
      },
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
              TextField(
                controller: linkNameController,
                decoration: const InputDecoration(labelText: "اسم الموقع"),
              ),
              TextField(
                controller: linkUrlController,
                decoration: const InputDecoration(labelText: "الرابط"),
                keyboardType: TextInputType.url,
              ),
            ],
          ),
          actions: [
            TextButton(
              onPressed: () {
                setState(() {
                  emergencyLinks.add({"name": linkNameController.text, "url": linkUrlController.text});
                });
                linkNameController.clear();
                linkUrlController.clear();
                Navigator.pop(context);
              },
              child: const Text("إضافة"),
            ),
          ],
        );
      },
    );
  }

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      backgroundColor: const Color(0xFFC2D5F2),

    
      appBar: AppBar(
        backgroundColor: const Color(0xFF4F6DA3),
        elevation: 0,
        title: const Text(
          "الطوارئ",
          style: TextStyle(color: Colors.white, fontSize: 22),
        ),
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

              const Text(
                "جهة اتصال طارئة",
                style: TextStyle(fontSize: 22, fontWeight: FontWeight.bold, color: Color(0xFF4F6DA3)),
              ),

              Expanded(
                child: ListView(
                  padding: const EdgeInsets.symmetric(horizontal: 20),
                  children: [
                    for (var contact in emergencyContacts)
                      buildContactCard(contact["name"]!, contact["phone"]!),

                    GestureDetector(
                      onTap: showContactDialog,
                      child: buildAddButton("إضافة جهة اتصال أخرى", showContactDialog),
                    ),
                  ],
                ),
              ),

              const SizedBox(height: 20),

              const Text(
                "مراكز الصحة النفسية للمساعدة",
                style: TextStyle(fontSize: 18, fontWeight: FontWeight.bold, color: Color(0xFF4F6DA3)),
              ),

              Expanded(
                child: ListView(
                  padding: const EdgeInsets.symmetric(horizontal: 20),
                  children: [
                    for (var link in emergencyLinks)
                      buildLinkCard(link["name"]!, link["url"]!),

                    GestureDetector(
                      onTap: showLinkDialog,
                      child: buildAddButton("إضافة رابط آخر", showLinkDialog),
                    ),
                  ],
                ),
              ),

              const SizedBox(height: 30),
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
        currentIndex: 0,
        items: const [
          BottomNavigationBarItem(icon: Icon(Icons.home), label: "الرئيسية"),
          BottomNavigationBarItem(icon: Icon(Icons.bar_chart), label: "التقارير"),
          BottomNavigationBarItem(icon: Icon(Icons.person), label: "حسابي"),
        ],
      ),
    );
  }

  Widget buildContactCard(String name, String phone) {
    return Container(
      margin: const EdgeInsets.symmetric(vertical: 5),
      padding: const EdgeInsets.all(15),
      decoration: BoxDecoration(
        color: Colors.white,
        borderRadius: BorderRadius.circular(15),
      ),
      child: Row(
        mainAxisAlignment: MainAxisAlignment.spaceBetween,
        children: [
          IconButton(
            icon: const Icon(Icons.phone, color: Color(0xFF4F6DA3), size: 30),
            onPressed: () => _callNumber(phone),
          ),
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

  Widget buildLinkCard(String name, String url) {
    return GestureDetector(
      onTap: () => _openWebsite(url),
      child: Container(
        margin: const EdgeInsets.symmetric(vertical: 5),
        padding: const EdgeInsets.all(15),
        decoration: BoxDecoration(
          color: Colors.white,
          borderRadius: BorderRadius.circular(15),
        ),
        child: Text(name, style: const TextStyle(fontSize: 18, color: Colors.blue)),
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
}

