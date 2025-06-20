import 'dart:convert';
import 'package:http/http.dart' as http;

/// API服务类，负责与后端FastAPI进行通信
class ApiService {
  static const String baseUrl = 'http://118.178.243.73:8080';

  /// 用户注册
  /// @param username 用户名
  /// @param email 邮箱
  /// @param password 密码
  /// @return 注册成功返回用户信息，否则返回null
  Future<Map<String, dynamic>?> register(
    String username,
    String email,
    String password,
  ) async {
    final response = await http.post(
      Uri.parse('$baseUrl/users/register'),
      headers: {'Content-Type': 'application/json'},
      body: jsonEncode({
        'username': username,
        'email': email,
        'password': password,
      }),
    );
    if (response.statusCode == 200) {
      return jsonDecode(response.body);
    }
    return null;
  }

  /// 获取用户信息
  /// @param userId 用户ID
  /// @return 用户信息Map，失败返回null
  Future<Map<String, dynamic>?> getUser(int userId) async {
    final response = await http.get(Uri.parse('$baseUrl/users/$userId'));
    if (response.statusCode == 200) {
      return jsonDecode(response.body);
    }
    return null;
  }

  /// 获取用户统计
  /// @param userId 用户ID
  /// @return 统计信息Map，失败返回null
  Future<Map<String, dynamic>?> getUserStat(int userId) async {
    final response = await http.get(Uri.parse('$baseUrl/stats/$userId'));
    if (response.statusCode == 200) {
      return jsonDecode(response.body);
    }
    return null;
  }

  /// 创建冥想会话
  /// @param userId 用户ID
  /// @param duration 冥想时长（秒）
  /// @param tapCount 敲击次数
  /// @return 创建成功返回会话信息，否则返回null
  Future<Map<String, dynamic>?> createMeditationSession(
    int userId,
    int duration,
    int tapCount,
  ) async {
    final response = await http.post(
      Uri.parse('$baseUrl/meditation/$userId/sessions'),
      headers: {'Content-Type': 'application/json'},
      body: jsonEncode({'duration': duration, 'tap_count': tapCount}),
    );
    if (response.statusCode == 200) {
      return jsonDecode(response.body);
    }
    return null;
  }

  /// 获取冥想会话列表
  /// @param userId 用户ID
  /// @return 会话列表，失败返回null
  Future<List<dynamic>?> getMeditationSessions(int userId) async {
    final response = await http.get(
      Uri.parse('$baseUrl/meditation/$userId/sessions'),
    );
    if (response.statusCode == 200) {
      return jsonDecode(response.body);
    }
    return null;
  }

  /// 获取成就列表
  /// @return 成就列表，失败返回null
  Future<List<dynamic>?> getAchievements() async {
    final response = await http.get(Uri.parse('$baseUrl/achievements/'));
    if (response.statusCode == 200) {
      return jsonDecode(response.body);
    }
    return null;
  }

  /// 解锁成就
  /// @param userId 用户ID
  /// @param achievementId 成就ID
  /// @return 解锁结果，失败返回null
  Future<Map<String, dynamic>?> unlockAchievement(
    int userId,
    int achievementId,
  ) async {
    final response = await http.post(
      Uri.parse('$baseUrl/achievements/$userId/unlock/$achievementId'),
    );
    if (response.statusCode == 200) {
      return jsonDecode(response.body);
    }
    return null;
  }

  /// 获取用户成就
  /// @param userId 用户ID
  /// @return 用户成就列表，失败返回null
  Future<List<dynamic>?> getUserAchievements(int userId) async {
    final response = await http.get(
      Uri.parse('$baseUrl/achievements/$userId/user'),
    );
    if (response.statusCode == 200) {
      return jsonDecode(response.body);
    }
    return null;
  }

  /// 获取排行榜
  /// @param period 排行榜周期（如 day/week/month）
  /// @return 排行榜列表，失败返回null
  Future<List<dynamic>?> getLeaderboard(String period) async {
    final response = await http.get(Uri.parse('$baseUrl/leaderboard/$period'));
    if (response.statusCode == 200) {
      return jsonDecode(response.body);
    }
    return null;
  }

  /// 获取分享任务
  /// @return 分享任务列表，失败返回null
  Future<List<dynamic>?> getShareTasks() async {
    final response = await http.get(Uri.parse('$baseUrl/share/tasks'));
    if (response.statusCode == 200) {
      return jsonDecode(response.body);
    }
    return null;
  }

  /// 完成分享任务
  /// @param userId 用户ID
  /// @param taskId 任务ID
  /// @return 完成结果，失败返回null
  Future<Map<String, dynamic>?> completeShareTask(
    int userId,
    int taskId,
  ) async {
    final response = await http.post(
      Uri.parse('$baseUrl/share/$userId/complete/$taskId'),
    );
    if (response.statusCode == 200) {
      return jsonDecode(response.body);
    }
    return null;
  }

  /// 获取用户分享任务
  /// @param userId 用户ID
  /// @return 用户分享任务列表，失败返回null
  Future<List<dynamic>?> getUserShareTasks(int userId) async {
    final response = await http.get(Uri.parse('$baseUrl/share/$userId/user'));
    if (response.statusCode == 200) {
      return jsonDecode(response.body);
    }
    return null;
  }

  /// 使用Apple ID登录
  /// @param identityToken Apple提供的Identity Token
  /// @param authorizationCode Apple提供的Authorization Code
  /// @param fullName 用户提供的全名 (可选)
  /// @param email 用户提供的邮箱 (可选)
  /// @return 登录成功返回用户信息，否则返回null
  Future<Map<String, dynamic>?> loginWithApple({
    required String identityToken,
    required String authorizationCode,
    String? fullName,
    String? email,
  }) async {
    final response = await http.post(
      Uri.parse('$baseUrl/users/login/apple'),
      headers: {'Content-Type': 'application/json'},
      body: jsonEncode({
        'identity_token': identityToken,
        'authorization_code': authorizationCode,
        'full_name': fullName,
        'email': email,
      }),
    );
    if (response.statusCode == 200) {
      return jsonDecode(response.body);
    }
    return null;
  }
}
