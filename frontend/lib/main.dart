import 'package:flutter/material.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';
import 'package:flutter_localizations/flutter_localizations.dart';
import 'package:qilema_app/core/theme/app_theme.dart';
import 'package:qilema_app/core/router/app_router.dart';

void main() {
  runApp(
    const ProviderScope(
      child: QilemaApp(),
    ),
  );
}

class QilemaApp extends ConsumerWidget {
  const QilemaApp({super.key});

  @override
  Widget build(BuildContext context, WidgetRef ref) {
    return MaterialApp.router(
      title: '起了吗',
      debugShowCheckedModeBanner: false,
      theme: AppTheme.lightTheme,
      darkTheme: AppTheme.darkTheme,
      themeMode: ThemeMode.system,
      localizationsDelegates: const [
        GlobalMaterialLocalizations.delegate,
        GlobalWidgetsLocalizations.delegate,
        GlobalCupertinoLocalizations.delegate,
      ],
      supportedLocales: const [
        Locale('zh', 'CN'),
      ],
      routerConfig: AppRouter.router,
    );
  }
}
