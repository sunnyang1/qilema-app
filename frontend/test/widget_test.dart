import 'package:flutter_test/flutter_test.dart';
import 'package:qilema_app/main.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';

void main() {
  testWidgets('App should launch without crashing', (WidgetTester tester) async {
    // Build our app and trigger a frame.
    await tester.pumpWidget(
      const ProviderScope(
        child: QilemaApp(),
      ),
    );

    // Verify that the app title is correct
    expect(find.text('起了吗'), findsOneWidget);
  });
}
