import 'package:flutter_test/flutter_test.dart';
import 'package:integration_test/integration_test.dart';
import 'package:woodenfish/main.dart' as app;
import 'package:flutter/material.dart';

void main() {
  IntegrationTestWidgetsFlutterBinding.ensureInitialized();

  group('木鱼App端到端流程', () {
    testWidgets('注册-登录-冥想-统计-成就流程', (WidgetTester tester) async {
      app.main();
      await tester.pumpAndSettle();

      // 1. 注册流程
      final Finder registerButton = find.text('注册');
      if (registerButton.evaluate().isNotEmpty) {
        await tester.tap(registerButton);
        await tester.pumpAndSettle();
      }
      final Finder usernameField = find.byKey(const Key('register_username'));
      final Finder emailField = find.byKey(const Key('register_email'));
      final Finder passwordField = find.byKey(const Key('register_password'));
      final Finder submitRegister = find.byKey(const Key('register_submit'));
      await tester.enterText(
          usernameField, 'testuser_${DateTime.now().millisecondsSinceEpoch}');
      await tester.enterText(
          emailField, 'test${DateTime.now().millisecondsSinceEpoch}@test.com');
      await tester.enterText(passwordField, 'test1234');
      await tester.tap(submitRegister);
      await tester.pumpAndSettle(const Duration(seconds: 2));

      // 2. 登录流程（如有登录页）
      final Finder loginButton = find.text('登录');
      if (loginButton.evaluate().isNotEmpty) {
        await tester.tap(loginButton);
        await tester.pumpAndSettle();
      }
      // 可补充登录表单自动填充

      // 3. 冥想流程
      final Finder meditationTab = find.text('冥想');
      if (meditationTab.evaluate().isNotEmpty) {
        await tester.tap(meditationTab);
        await tester.pumpAndSettle();
      }
      final Finder startMeditation = find.byKey(const Key('start_meditation'));
      if (startMeditation.evaluate().isNotEmpty) {
        await tester.tap(startMeditation);
        await tester.pumpAndSettle(const Duration(seconds: 2));
        // 模拟敲击
        final Finder tapButton = find.byKey(const Key('tap_button'));
        for (int i = 0; i < 5; i++) {
          await tester.tap(tapButton);
          await tester.pump(const Duration(milliseconds: 300));
        }
        // 停止冥想
        final Finder stopMeditation = find.byKey(const Key('stop_meditation'));
        if (stopMeditation.evaluate().isNotEmpty) {
          await tester.tap(stopMeditation);
          await tester.pumpAndSettle();
        }
      }

      // 4. 查看统计
      final Finder statTab = find.text('统计');
      if (statTab.evaluate().isNotEmpty) {
        await tester.tap(statTab);
        await tester.pumpAndSettle();
      }

      // 5. 查看成就
      final Finder achievementTab = find.text('成就');
      if (achievementTab.evaluate().isNotEmpty) {
        await tester.tap(achievementTab);
        await tester.pumpAndSettle();
      }

      // 断言页面有主要内容
      expect(find.textContaining('功德'), findsWidgets);
    });
  });
}
