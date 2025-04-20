import 'package:flutter/material.dart';

class ProfileUpdatePage extends StatefulWidget {
  final String? userName;

  ProfileUpdatePage({this.userName});

  @override
  _ProfileUpdatePageState createState() => _ProfileUpdatePageState();
}

class _ProfileUpdatePageState extends State<ProfileUpdatePage> {
  final TextEditingController usernameController = TextEditingController();
  final TextEditingController ageController = TextEditingController();
  final TextEditingController emailController = TextEditingController();
  final TextEditingController passwordController = TextEditingController();
  final TextEditingController botNameController = TextEditingController();
  final TextEditingController chatpasswordController = TextEditingController();

  @override
  void initState() {
    super.initState();
    usernameController.text = widget.userName ?? "أنيس";
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
                    Positioned(
                      bottom: 5,
                      right: 5,
                      child: CircleAvatar(
                        radius: 15,
                        backgroundColor: Colors.white,
                        child: Icon(Icons.edit, size: 18, color: Color(0xFF4F6DA3)),
                      ),
                    ),
                  ],
                ),
                const SizedBox(height: 10),
                Text(
                  "مرحبًا ${widget.userName ?? "أنيس"}!",
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
                          buildProfileField("إسم المستخدم", usernameController),
                          buildProfileField("العمر", ageController),
                          buildProfileField("البريد الإلكتروني", emailController),
                          buildProfileField("كلمة المرور", passwordController, isPassword: true),
                          buildProfileField("إسم البوت", botNameController),
                          buildProfileField("رمز المحادثة", chatpasswordController),
                          const SizedBox(height: 20),
                          TextButton(
                            onPressed: () {
                              print(" تسجيل الخروج");
                            },
                            child: const Text(
                              "تسجيل الخروج",
                              style: TextStyle(
                                color: Colors.red,
                                fontSize: 18,
                                fontWeight: FontWeight.bold,
                              ),
                            ),
                          ),
                        ],
                      ),
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
          currentIndex: 0,
          items: const [
            BottomNavigationBarItem(icon: Icon(Icons.person), label: "حسابي"),
            BottomNavigationBarItem(icon: Icon(Icons.bar_chart), label: "التقارير"),
            BottomNavigationBarItem(icon: Icon(Icons.home), label: "الرئيسية"),
          ],
        ),
      ),
    );
  }

  Widget buildProfileField(String title, TextEditingController controller, {bool isPassword = false}) {
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
            obscureText: isPassword,
            textAlign: TextAlign.right,
            decoration: InputDecoration(
              contentPadding: const EdgeInsets.symmetric(horizontal: 12, vertical: 8),
              filled: true,
              fillColor: const Color(0xFFE9F1F4),
              border: OutlineInputBorder(
                borderRadius: BorderRadius.circular(32),
                borderSide: BorderSide.none,
              ),
              hintText: null, 
              hintStyle: const TextStyle(color: Colors.grey),
            ),
          ),
        ],
      ),
    );
  }
}
