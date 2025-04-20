import 'package:flutter/material.dart';
import 'welcome.dart';
import 'signup.dart';
import 'signin.dart';
import 'home.dart'; 
import 'describe_feeling.dart';
import 'chat/talk_to_me.dart';
//import 'progress_tracker.dart'; 


void main() {
  runApp(MyApp());
}

class MyApp extends StatelessWidget {
  @override
  Widget build(BuildContext context) {
    return MaterialApp( 
      debugShowCheckedModeBanner: false,
      initialRoute:     '/welcome', 
      routes: {
        '/welcome': (context) => WelcomePage(), 
        '/signup': (context) => SignUpPage(),
        '/signin': (context) => SignInPage(),
        '/home': (context) => HomePage(),
        '/describe': (context) => DescribeFeelingPage(),
        '/chat': (context) => TalkToMePage(),
     //   '/progress': (context) => ProgressTrackerPage(), 
      },
    );
  }
}
