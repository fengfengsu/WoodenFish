// This is a basic Flutter widget test.
//
// To perform an interaction with a widget in your test, use the WidgetTester
// utility in the flutter_test package. For example, you can send tap and scroll
// gestures. You can also use WidgetTester to find child widgets in the widget
// tree, read text, and verify that the values of widget properties are correct.

import 'package:flutter/material.dart';
import 'package:flutter_test/flutter_test.dart';

import 'package:muyu_app/main.dart';

void main() {
  testWidgets('木鱼App基本功能测试', (WidgetTester tester) async {
    // 构建应用并触发框架
    await tester.pumpWidget(const MuyuApp());

    // 等待应用完全加载
    await tester.pumpAndSettle();

    // 验证应用正常启动
    expect(find.byType(MaterialApp), findsOneWidget);

    // 验证主要文本存在（木鱼相关文本）
    final woodenFishTexts = [
      find.textContaining('木鱼'),
      find.textContaining('冥想'),
      find.textContaining('功德'),
    ];

    bool foundAnyText = false;
    for (final textFinder in woodenFishTexts) {
      if (textFinder.evaluate().isNotEmpty) {
        foundAnyText = true;
        break;
      }
    }

    // 至少要找到一个相关文本，证明应用正常加载
    expect(foundAnyText, isTrue, reason: '应用应该显示木鱼相关内容');
  });

  testWidgets('应用主题测试', (WidgetTester tester) async {
    await tester.pumpWidget(const MuyuApp());
    await tester.pumpAndSettle();

    // 验证MaterialApp存在
    final materialApp = tester.widget<MaterialApp>(find.byType(MaterialApp));
    expect(materialApp.title, equals('木鱼'));
    expect(materialApp.debugShowCheckedModeBanner, isFalse);
  });
}
