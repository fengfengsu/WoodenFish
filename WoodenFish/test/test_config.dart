/**
 * Flutter测试配置
 * 包含测试环境配置、模拟数据、测试工具函数
 */

import 'package:flutter_test/flutter_test.dart';
import 'package:integration_test/integration_test.dart';
import 'package:flutter/material.dart';
import 'dart:math';

class TestConfig {
  /// 测试服务器地址
  static const String testServerUrl = 'http://localhost:8000';

  /// 测试超时时间
  static const Duration defaultTimeout = Duration(seconds: 30);
  static const Duration longTimeout = Duration(minutes: 2);

  /// 测试用户数据
  static Map<String, String> generateTestUser() {
    final timestamp = DateTime.now().millisecondsSinceEpoch;
    return {
      'username': 'testuser_$timestamp',
      'email': 'test$timestamp@woodenfish.test',
      'password': 'Test123456!',
    };
  }

  /// 生成随机冥想数据
  static Map<String, dynamic> generateMeditationData() {
    final random = Random();
    return {
      'duration': random.nextInt(1800) + 60, // 1-30分钟
      'tap_count': random.nextInt(500) + 10,
      'session_type': ['木鱼', '钟声', '静坐'][random.nextInt(3)],
      'notes': '自动化测试冥想会话',
    };
  }
}

class TestHelpers {
  /// 等待元素出现
  static Future<bool> waitForElement(WidgetTester tester, Finder finder,
      {Duration timeout = const Duration(seconds: 10)}) async {
    final endTime = DateTime.now().add(timeout);

    while (DateTime.now().isBefore(endTime)) {
      await tester.pump(const Duration(milliseconds: 100));
      if (finder.evaluate().isNotEmpty) {
        return true;
      }
    }
    return false;
  }

  /// 安全点击（等待元素出现后点击）
  static Future<bool> safeTap(WidgetTester tester, Finder finder,
      {Duration timeout = const Duration(seconds: 5)}) async {
    if (await waitForElement(tester, finder, timeout: timeout)) {
      await tester.tap(finder);
      await tester.pumpAndSettle();
      return true;
    }
    return false;
  }

  /// 安全输入文本
  static Future<bool> safeEnterText(
      WidgetTester tester, Finder finder, String text,
      {Duration timeout = const Duration(seconds: 5)}) async {
    if (await waitForElement(tester, finder, timeout: timeout)) {
      await tester.enterText(finder, text);
      await tester.pump(const Duration(milliseconds: 300));
      return true;
    }
    return false;
  }

  /// 滚动到元素
  static Future<void> scrollToElement(
      WidgetTester tester, Finder listFinder, Finder itemFinder) async {
    while (itemFinder.evaluate().isEmpty) {
      await tester.drag(listFinder, const Offset(0, -100));
      await tester.pumpAndSettle();
    }
  }

  /// 错误恢复
  static Future<void> recoverFromError(
      WidgetTester tester, String errorContext) async {
    print('🔧 错误恢复: $errorContext');

    // 尝试返回主页
    final homeButton = find.byIcon(Icons.home);
    if (homeButton.evaluate().isNotEmpty) {
      await tester.tap(homeButton);
      await tester.pumpAndSettle();
      return;
    }

    // 尝试点击返回按钮
    final backButton = find.byIcon(Icons.arrow_back);
    if (backButton.evaluate().isNotEmpty) {
      await tester.tap(backButton);
      await tester.pumpAndSettle();
      return;
    }

    // 尝试关闭对话框
    final closeButton = find.byIcon(Icons.close);
    if (closeButton.evaluate().isNotEmpty) {
      await tester.tap(closeButton);
      await tester.pumpAndSettle();
      return;
    }

    print('⚠️  无法自动恢复，测试继续执行...');
  }
}

class TestData {
  /// 测试成就数据
  static final List<Map<String, dynamic>> achievements = [
    {
      'name': '初心者',
      'description': '完成第一次冥想',
      'icon': Icons.star,
      'requirement': 1,
    },
    {
      'name': '坚持者',
      'description': '连续冥想7天',
      'icon': Icons.local_fire_department,
      'requirement': 7,
    },
    {
      'name': '功德圆满',
      'description': '累计敲击1000次',
      'icon': Icons.emoji_events,
      'requirement': 1000,
    },
  ];

  /// 测试统计数据
  static Map<String, dynamic> get sampleStats => {
        'total_sessions': Random().nextInt(50) + 10,
        'total_duration': Random().nextInt(10000) + 1000,
        'total_taps': Random().nextInt(5000) + 500,
        'average_session_duration': Random().nextInt(600) + 180,
        'streak_days': Random().nextInt(30) + 1,
      };
}

/// 测试断言扩展
extension TestAssertions on WidgetTester {
  /// 验证页面标题
  Future<void> expectPageTitle(String expectedTitle) async {
    await pumpAndSettle();
    expect(find.text(expectedTitle), findsOneWidget);
  }

  /// 验证错误消息
  Future<void> expectErrorMessage() async {
    await pumpAndSettle();
    final errorMessages = [
      find.textContaining('错误'),
      find.textContaining('失败'),
      find.textContaining('异常'),
      find.byIcon(Icons.error),
    ];

    bool foundError = false;
    for (final finder in errorMessages) {
      if (finder.evaluate().isNotEmpty) {
        foundError = true;
        break;
      }
    }
    expect(foundError, isTrue);
  }

  /// 验证成功消息
  Future<void> expectSuccessMessage() async {
    await pumpAndSettle();
    final successMessages = [
      find.textContaining('成功'),
      find.textContaining('完成'),
      find.byIcon(Icons.check_circle),
    ];

    bool foundSuccess = false;
    for (final finder in successMessages) {
      if (finder.evaluate().isNotEmpty) {
        foundSuccess = true;
        break;
      }
    }
    expect(foundSuccess, isTrue);
  }
}
