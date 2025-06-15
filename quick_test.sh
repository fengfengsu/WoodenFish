#!/bin/bash

# 木鱼App快速测试脚本
# 用于快速验证核心功能是否正常

set -e  # 遇到错误立即退出

# 颜色定义
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# 日志函数
log() {
    echo -e "${BLUE}[$(date +'%H:%M:%S')] $1${NC}"
}

success() {
    echo -e "${GREEN}✅ $1${NC}"
}

error() {
    echo -e "${RED}❌ $1${NC}"
}

warning() {
    echo -e "${YELLOW}⚠️  $1${NC}"
}

# 检查依赖
check_dependencies() {
    log "检查依赖..."
    
    # 检查Python
    if ! command -v python3 &> /dev/null; then
        error "Python3 未安装"
        exit 1
    fi
    
    # 检查Flutter
    if ! command -v flutter &> /dev/null; then
        error "Flutter 未安装"
        exit 1
    fi
    
    # 检查pip
    if ! command -v pip &> /dev/null && ! command -v pip3 &> /dev/null; then
        error "pip 未安装"
        exit 1
    fi
    
    success "依赖检查通过"
}

# 安装依赖
install_dependencies() {
    log "安装Python依赖..."
    cd WoodenFis-Server
    
    # 尝试不同的pip命令
    if pip install -r requirements.txt; then
        success "Python依赖安装成功"
    elif pip3 install -r requirements.txt; then
        success "Python依赖安装成功"  
    elif python -m pip install -r requirements.txt; then
        success "Python依赖安装成功"
    else
        error "Python依赖安装失败"
        cd ..
        exit 1
    fi
    
    cd ..
    
    log "获取Flutter依赖..."
    cd WoodenFish
    if flutter pub get; then
        success "Flutter依赖获取成功"
    else
        warning "Flutter依赖获取失败，尝试修复..."
        flutter clean
        flutter pub get
        if [ $? -eq 0 ]; then
            success "Flutter依赖修复成功"
        else
            error "Flutter依赖获取失败"
            cd ..
            exit 1
        fi
    fi
    cd ..
}

# 启动服务器
start_server() {
    log "启动测试服务器..."
    cd WoodenFis-Server
    
    # 杀死可能存在的进程
    pkill -f "python.*main.py" 2>/dev/null || true
    
    # 启动服务器
    python3 main.py &
    SERVER_PID=$!
    
    # 等待服务器启动
    sleep 3
    
    # 检查服务器是否正常启动
    if curl -f http://localhost:8000/docs &>/dev/null; then
        success "服务器启动成功 (PID: $SERVER_PID)"
        cd ..
        return 0
    else
        error "服务器启动失败"
        kill $SERVER_PID 2>/dev/null || true
        cd ..
        return 1
    fi
}

# 运行服务端测试
test_server() {
    log "运行服务端快速测试..."
    cd WoodenFis-Server
    
    # 运行核心测试
    if python3 -m pytest test_main.py::TestUserAPI::test_create_user_success -v; then
        success "服务端核心测试通过"
        cd ..
        return 0
    else
        error "服务端测试失败"
        cd ..
        return 1
    fi
}

# 运行Flutter测试
test_flutter() {
    log "运行Flutter快速测试..."
    cd WoodenFish
    
    # 运行单元测试
    if flutter test test/widget_test.dart; then
        success "Flutter单元测试通过"
    else
        warning "Flutter单元测试失败，继续执行..."
    fi
    
    # 运行简单的集成测试
    log "尝试运行集成测试..."
    if flutter test integration_test/app_e2e_test.dart -d chrome --timeout=60s; then
        success "Flutter集成测试通过"
    else
        warning "Flutter集成测试失败或超时"
    fi
    
    cd ..
}

# 性能快速检测
performance_check() {
    log "执行性能快速检测..."
    
    # 检查API响应时间
    response_time=$(curl -w '%{time_total}' -o /dev/null -s http://localhost:8000/achievements/ 2>/dev/null || echo "999")
    
    if (( $(echo "$response_time < 2.0" | bc -l) )); then
        success "API响应时间正常: ${response_time}s"
    else
        warning "API响应时间较慢: ${response_time}s"
    fi
}

# 清理资源
cleanup() {
    log "清理测试环境..."
    
    # 杀死服务器进程
    if [ ! -z "$SERVER_PID" ]; then
        kill $SERVER_PID 2>/dev/null || true
    fi
    
    # 杀死所有可能的测试进程
    pkill -f "python.*main.py" 2>/dev/null || true
    pkill -f "flutter.*test" 2>/dev/null || true
    
    success "清理完成"
}

# 主函数
main() {
    echo -e "${BLUE}🎯 木鱼App快速测试${NC}"
    echo "================================"
    
    # 设置清理陷阱
    trap cleanup EXIT
    
    # 执行测试步骤
    check_dependencies
    install_dependencies
    
    if start_server; then
        test_server
        performance_check
    else
        warning "服务器启动失败，跳过服务端测试"
    fi
    
    test_flutter
    
    echo "================================"
    success "快速测试完成！"
    
    echo -e "\n${YELLOW}💡 提示：${NC}"
    echo "- 要运行完整测试，请使用: python run_all_tests.py"
    echo "- 要查看详细测试报告，请检查生成的报告文件"
}

# 执行主函数
main "$@" 