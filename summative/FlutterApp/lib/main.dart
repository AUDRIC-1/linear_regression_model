import 'dart:convert';
import 'package:flutter/material.dart';
import 'package:http/http.dart' as http;

void main() {
  runApp(const MyApp());
}

class MyApp extends StatelessWidget {
  const MyApp({super.key});

  @override
  Widget build(BuildContext context) {
    return MaterialApp(
      title: 'Crop Yield Predictor',
      theme: ThemeData(primarySwatch: Colors.green, useMaterial3: true),
      home: const PredictionPage(),
    );
  }
}

class PredictionPage extends StatefulWidget {
  const PredictionPage({super.key});

  @override
  State<PredictionPage> createState() => _PredictionPageState();
}

class _PredictionPageState extends State<PredictionPage> {
  // change this to your live Render URL
  final String apiUrl =
      'https://linear-regression-model-g3rf.onrender.com/predict';

  final regionController = TextEditingController();
  final soilController = TextEditingController();
  final cropController = TextEditingController();
  final weatherController = TextEditingController();
  final rainfallController = TextEditingController();
  final temperatureController = TextEditingController();
  final fertilizerController = TextEditingController();
  final irrigationController = TextEditingController();
  final daysController = TextEditingController();

  String resultText = '';
  bool loading = false;

  Future<void> predict() async {
    setState(() {
      loading = true;
      resultText = '';
    });

    if (regionController.text.isEmpty ||
        soilController.text.isEmpty ||
        cropController.text.isEmpty ||
        weatherController.text.isEmpty ||
        rainfallController.text.isEmpty ||
        temperatureController.text.isEmpty ||
        fertilizerController.text.isEmpty ||
        irrigationController.text.isEmpty ||
        daysController.text.isEmpty) {
      setState(() {
        resultText = 'Please fill in all fields.';
        loading = false;
      });
      return;
    }

    try {
      final body = {
        'Region': regionController.text,
        'Soil_Type': soilController.text,
        'Crop': cropController.text,
        'Weather_Condition': weatherController.text,
        'Rainfall_mm': double.parse(rainfallController.text),
        'Temperature_Celsius': double.parse(temperatureController.text),
        'Fertilizer_Used': fertilizerController.text.toLowerCase() == 'true',
        'Irrigation_Used': irrigationController.text.toLowerCase() == 'true',
        'Days_to_Harvest': int.parse(daysController.text),
      };

      final response = await http.post(
        Uri.parse(apiUrl),
        headers: {'Content-Type': 'application/json'},
        body: jsonEncode(body),
      );

      if (response.statusCode == 200) {
        final data = jsonDecode(response.body);
        setState(() {
          resultText =
              'Predicted Yield: ${data['predicted_yield_tons_per_hectare'].toStringAsFixed(2)} tons/hectare';
        });
      } else {
        setState(() {
          resultText = 'Error: values out of range or invalid input.';
        });
      }
    } catch (e) {
      setState(() {
        resultText = 'Error: could not reach the prediction server.';
      });
    } finally {
      setState(() {
        loading = false;
      });
    }
  }

  Widget buildField(String label, TextEditingController controller,
      {String? hint}) {
    return Padding(
      padding: const EdgeInsets.symmetric(vertical: 6),
      child: TextField(
        controller: controller,
        decoration: InputDecoration(
          labelText: label,
          hintText: hint,
          border: const OutlineInputBorder(),
        ),
      ),
    );
  }

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      appBar: AppBar(title: const Text('Crop Yield Predictor')),
      body: SingleChildScrollView(
        padding: const EdgeInsets.all(16),
        child: Column(
          crossAxisAlignment: CrossAxisAlignment.stretch,
          children: [
            buildField('Region', regionController, hint: 'North/South/East/West'),
            buildField('Soil Type', soilController, hint: 'Sandy/Clay/Loam/Silt/Peaty/Chalky'),
            buildField('Crop', cropController, hint: 'e.g. Wheat, Rice, Maize'),
            buildField('Weather Condition', weatherController, hint: 'Sunny/Rainy/Cloudy'),
            buildField('Rainfall (mm)', rainfallController, hint: '0 - 3000'),
            buildField('Temperature (C)', temperatureController, hint: '-10 - 50'),
            buildField('Fertilizer Used', fertilizerController, hint: 'true/false'),
            buildField('Irrigation Used', irrigationController, hint: 'true/false'),
            buildField('Days to Harvest', daysController, hint: '1 - 365'),
            const SizedBox(height: 16),
            ElevatedButton(
              onPressed: loading ? null : predict,
              child: loading
                  ? const CircularProgressIndicator()
                  : const Text('Predict'),
            ),
            const SizedBox(height: 20),
            Container(
              width: double.infinity,
              padding: const EdgeInsets.all(16),
              decoration: BoxDecoration(
                color: Colors.green.shade50,
                borderRadius: BorderRadius.circular(8),
                border: Border.all(color: Colors.green.shade200),
              ),
              child: Text(
                resultText.isEmpty ? 'Prediction will appear here' : resultText,
                style: const TextStyle(fontSize: 16),
              ),
            ),
          ],
        ),
      ),
    );
  }
}
