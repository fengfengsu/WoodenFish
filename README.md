# 木鱼App (WoodenFish)

一个基于Flutter的冥想应用，包含iOS客户端和FastAPI后端服务器。

## 项目结构

```
woodenfish/
├── WoodenFish/              # Flutter客户端应用
│   ├── lib/                 # Flutter Dart源代码
│   ├── ios/                 # iOS平台代码
│   ├── android/             # Android平台代码
│   ├── test/                # 单元测试
│   ├── integration_test/    # 集成测试
│   └── pubspec.yaml         # Flutter依赖配置
├── WoodenFis-Server/        # FastAPI后端服务器
│   ├── api/                 # API路由模块
│   ├── models.py            # 数据模型
│   ├── database.py          # 数据库配置
│   ├── schemas.py           # 数据结构定义
│   └── main.py              # 服务器入口文件
├── .gitignore               # Git忽略文件配置
└── README.md                # 项目说明
```

## 功能特性

### Flutter客户端
- 🪵 木鱼敲击功能
- 🎵 多种音效选择
- ⏰ 冥想计时器
- 📊 统计数据
- 🏆 成就系统
- 📱 排行榜
- 💫 功德分享

### FastAPI后端
- 👤 用户管理系统
- 📈 统计数据收集
- 🏅 成就管理
- 🎯 冥想记录
- 📊 排行榜功能
- 🔗 分享功能

## 技术栈

- **前端**: Flutter (Dart)
- **后端**: FastAPI (Python)
- **数据库**: SQLite (SQLAlchemy ORM)
- **状态管理**: Provider
- **音频**: audioplayers
- **UI组件**: Material Design

## 开发指南

### 后端服务器启动
```bash
cd WoodenFis-Server
pip install fastapi uvicorn sqlalchemy
uvicorn main:app --reload
```

### Flutter应用开发
```bash
cd WoodenFish
flutter pub get
flutter run
```

## API文档

后端服务器启动后，访问 `http://localhost:8000/docs` 查看完整的API文档。

## 测试

项目包含完整的测试套件：
- 单元测试
- 集成测试
- UI自动化测试

## 贡献

欢迎提交Issue和Pull Request！

## 许可证

MIT License 