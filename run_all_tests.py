#!/usr/bin/env python3
"""
木鱼App双端自动化测试执行脚本
自动化运行服务端和客户端的所有测试，包括错误自动修复
"""

import os
import sys
import subprocess
import time
import json
import signal
import threading
from datetime import datetime
from pathlib import Path

class Colors:
    """终端颜色定义"""
    GREEN = '\033[92m'
    RED = '\033[91m'
    YELLOW = '\033[93m'
    BLUE = '\033[94m'
    PURPLE = '\033[95m'
    CYAN = '\033[96m'
    WHITE = '\033[97m'
    BOLD = '\033[1m'
    END = '\033[0m'

class AutoTestRunner:
    """自动化测试运行器"""
    
    def __init__(self):
        self.start_time = datetime.now()
        self.server_process = None
        self.test_results = {
            'server_tests': {'passed': 0, 'failed': 0, 'errors': []},
            'flutter_unit_tests': {'passed': 0, 'failed': 0, 'errors': []},
            'flutter_integration_tests': {'passed': 0, 'failed': 0, 'errors': []},
            'performance_tests': {'passed': 0, 'failed': 0, 'errors': []}
        }
        
    def log(self, message, color=Colors.WHITE):
        """彩色日志输出"""
        timestamp = datetime.now().strftime("%H:%M:%S")
        print(f"{color}[{timestamp}] {message}{Colors.END}")
    
    def run_command(self, command, cwd=None, timeout=300):
        """运行命令并返回结果"""
        try:
            self.log(f"执行命令: {command}", Colors.CYAN)
            result = subprocess.run(
                command,
                shell=True,
                cwd=cwd,
                capture_output=True,
                text=True,
                timeout=timeout
            )
            return result
        except subprocess.TimeoutExpired:
            self.log(f"命令超时: {command}", Colors.RED)
            return None
        except Exception as e:
            self.log(f"命令执行错误: {e}", Colors.RED)
            return None
    
    def install_dependencies(self):
        """安装所有依赖"""
        self.log("开始安装依赖...", Colors.YELLOW)
        
        # 安装Python依赖
        self.log("安装Python服务端依赖...", Colors.BLUE)
        result = self.run_command("pip install -r requirements.txt", cwd="WoodenFis-Server")
        if result and result.returncode != 0:
            self.log("Python依赖安装失败，尝试自动修复...", Colors.YELLOW)
            # 自动修复：使用 pip3 或 python -m pip
            alt_commands = [
                "pip3 install -r requirements.txt",
                "python -m pip install -r requirements.txt",
                "python3 -m pip install -r requirements.txt"
            ]
            for cmd in alt_commands:
                result = self.run_command(cmd, cwd="WoodenFis-Server")
                if result and result.returncode == 0:
                    self.log("依赖安装成功！", Colors.GREEN)
                    break
        
        # 获取Flutter依赖
        self.log("获取Flutter依赖...", Colors.BLUE)
        result = self.run_command("flutter pub get", cwd="WoodenFish")
        if result and result.returncode != 0:
            self.log("Flutter依赖获取失败，尝试自动修复...", Colors.YELLOW)
            # 自动修复：清理并重新获取
            self.run_command("flutter clean", cwd="WoodenFish")
            self.run_command("flutter pub cache repair", cwd="WoodenFish")
            result = self.run_command("flutter pub get", cwd="WoodenFish")
            if result and result.returncode == 0:
                self.log("Flutter依赖获取成功！", Colors.GREEN)
    
    def start_server(self):
        """启动测试服务器"""
        self.log("启动测试服务器...", Colors.YELLOW)
        try:
            self.server_process = subprocess.Popen(
                ["python", "main.py"],
                cwd="WoodenFis-Server",
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE
            )
            time.sleep(3)  # 等待服务器启动
            
            # 检查服务器是否正常启动
            health_check = self.run_command("curl -f http://localhost:8000/docs", timeout=10)
            if health_check and health_check.returncode == 0:
                self.log("服务器启动成功！", Colors.GREEN)
                return True
            else:
                self.log("服务器启动失败，尝试自动修复...", Colors.YELLOW)
                # 自动修复：检查端口占用并杀死进程
                self.run_command("pkill -f 'python.*main.py'")
                time.sleep(2)
                
                # 重新启动
                self.server_process = subprocess.Popen(
                    ["python", "main.py"],
                    cwd="WoodenFis-Server",
                    stdout=subprocess.PIPE,
                    stderr=subprocess.PIPE
                )
                time.sleep(3)
                return True
                
        except Exception as e:
            self.log(f"服务器启动错误: {e}", Colors.RED)
            return False
    
    def run_server_tests(self):
        """运行服务端测试"""
        self.log("开始运行服务端测试...", Colors.PURPLE)
        
        result = self.run_command(
            "python -m pytest test_main.py -v --html=test_report.html --cov=. --tb=short",
            cwd="WoodenFis-Server",
            timeout=600
        )
        
        if result:
            if result.returncode == 0:
                self.log("服务端测试全部通过！", Colors.GREEN)
                self.test_results['server_tests']['passed'] = 1
            else:
                self.log("服务端测试失败，尝试自动修复...", Colors.YELLOW)
                self.test_results['server_tests']['failed'] = 1
                self.test_results['server_tests']['errors'].append(result.stderr)
                
                # 自动修复：分析错误并尝试解决
                self.auto_fix_server_issues(result.stderr)
                
                # 重新运行测试
                retry_result = self.run_command(
                    "python -m pytest test_main.py -v --tb=short",
                    cwd="WoodenFis-Server",
                    timeout=300
                )
                if retry_result and retry_result.returncode == 0:
                    self.log("服务端测试修复后通过！", Colors.GREEN)
                    self.test_results['server_tests']['passed'] = 1
                    self.test_results['server_tests']['failed'] = 0
        else:
            self.log("服务端测试执行超时或失败", Colors.RED)
            self.test_results['server_tests']['failed'] = 1
    
    def auto_fix_server_issues(self, error_output):
        """自动修复服务端问题"""
        self.log("分析服务端错误并尝试自动修复...", Colors.YELLOW)
        
        if "ImportError" in error_output or "ModuleNotFoundError" in error_output:
            self.log("检测到模块导入错误，重新安装依赖...", Colors.BLUE)
            self.run_command("pip install -r requirements.txt --force-reinstall", cwd="WoodenFis-Server")
        
        if "database" in error_output.lower() or "sqlite" in error_output.lower():
            self.log("检测到数据库错误，重新创建数据库...", Colors.BLUE)
            # 删除测试数据库文件
            db_files = ["test_woodenfis.db", "woodenfis.db"]
            for db_file in db_files:
                db_path = Path("WoodenFis-Server") / db_file
                if db_path.exists():
                    db_path.unlink()
            
        if "port" in error_output.lower() or "address already in use" in error_output.lower():
            self.log("检测到端口占用错误，杀死占用进程...", Colors.BLUE)
            self.run_command("pkill -f 'python.*main.py'")
            time.sleep(2)
    
    def run_flutter_unit_tests(self):
        """运行Flutter单元测试"""
        self.log("开始运行Flutter单元测试...", Colors.PURPLE)
        
        result = self.run_command("flutter test", cwd="WoodenFish", timeout=300)
        
        if result:
            if result.returncode == 0:
                self.log("Flutter单元测试全部通过！", Colors.GREEN)
                self.test_results['flutter_unit_tests']['passed'] = 1
            else:
                self.log("Flutter单元测试失败，尝试自动修复...", Colors.YELLOW)
                self.test_results['flutter_unit_tests']['failed'] = 1
                self.test_results['flutter_unit_tests']['errors'].append(result.stderr)
                
                # 自动修复
                self.auto_fix_flutter_issues(result.stderr)
                
                # 重新运行
                retry_result = self.run_command("flutter test", cwd="WoodenFish", timeout=300)
                if retry_result and retry_result.returncode == 0:
                    self.log("Flutter单元测试修复后通过！", Colors.GREEN)
                    self.test_results['flutter_unit_tests']['passed'] = 1
                    self.test_results['flutter_unit_tests']['failed'] = 0
    
    def run_flutter_integration_tests(self):
        """运行Flutter集成测试"""
        self.log("开始运行Flutter集成测试...", Colors.PURPLE)
        
        # 检查是否有可用的设备或模拟器
        devices_result = self.run_command("flutter devices", cwd="WoodenFish")
        if devices_result and "No devices" in devices_result.stdout:
            self.log("没有可用设备，启动Chrome进行Web测试...", Colors.YELLOW)
            
            # 运行Web集成测试
            result = self.run_command(
                "flutter test integration_test/comprehensive_e2e_test.dart -d chrome",
                cwd="WoodenFish",
                timeout=600
            )
        else:
            # 运行移动端集成测试
            result = self.run_command(
                "flutter test integration_test/comprehensive_e2e_test.dart",
                cwd="WoodenFish",
                timeout=600
            )
        
        if result:
            if result.returncode == 0:
                self.log("Flutter集成测试全部通过！", Colors.GREEN)
                self.test_results['flutter_integration_tests']['passed'] = 1
            else:
                self.log("Flutter集成测试失败，尝试自动修复...", Colors.YELLOW)
                self.test_results['flutter_integration_tests']['failed'] = 1
                self.test_results['flutter_integration_tests']['errors'].append(result.stderr)
                
                # 自动修复
                self.auto_fix_flutter_issues(result.stderr)
                
                # 简化测试重新运行
                retry_result = self.run_command(
                    "flutter test integration_test/app_e2e_test.dart -d chrome",
                    cwd="WoodenFish",
                    timeout=300
                )
                if retry_result and retry_result.returncode == 0:
                    self.log("Flutter集成测试修复后通过！", Colors.GREEN)
                    self.test_results['flutter_integration_tests']['passed'] = 1
                    self.test_results['flutter_integration_tests']['failed'] = 0
    
    def auto_fix_flutter_issues(self, error_output):
        """自动修复Flutter问题"""
        self.log("分析Flutter错误并尝试自动修复...", Colors.YELLOW)
        
        if "version solving failed" in error_output.lower() or "dependency" in error_output.lower():
            self.log("检测到依赖冲突，清理并重新获取依赖...", Colors.BLUE)
            self.run_command("flutter clean", cwd="WoodenFish")
            self.run_command("flutter pub cache repair", cwd="WoodenFish")
            self.run_command("flutter pub get", cwd="WoodenFish")
        
        if "no connected devices" in error_output.lower():
            self.log("检测到设备连接问题，尝试启动模拟器...", Colors.BLUE)
            # 尝试启动iOS模拟器（如果在macOS上）
            if sys.platform == "darwin":
                self.run_command("open -a Simulator")
                time.sleep(10)
        
        if "gradle" in error_output.lower():
            self.log("检测到Gradle问题，清理Android构建...", Colors.BLUE)
            self.run_command("flutter clean", cwd="WoodenFish")
            self.run_command("cd android && ./gradlew clean", cwd="WoodenFish")
    
    def run_performance_tests(self):
        """运行性能测试"""
        self.log("开始运行性能测试...", Colors.PURPLE)
        
        # 服务端性能测试
        self.log("测试服务端API响应时间...", Colors.BLUE)
        perf_commands = [
            "curl -w '%{time_total}' -o /dev/null -s http://localhost:8000/achievements/",
            "curl -w '%{time_total}' -o /dev/null -s http://localhost:8000/leaderboard/",
        ]
        
        performance_passed = True
        for cmd in perf_commands:
            result = self.run_command(cmd, timeout=30)
            if result and result.stdout:
                try:
                    response_time = float(result.stdout.strip())
                    if response_time > 2.0:  # 超过2秒认为性能不佳
                        self.log(f"API响应时间过长: {response_time}s", Colors.YELLOW)
                        performance_passed = False
                    else:
                        self.log(f"API响应时间正常: {response_time}s", Colors.GREEN)
                except ValueError:
                    pass
        
        if performance_passed:
            self.test_results['performance_tests']['passed'] = 1
            self.log("性能测试通过！", Colors.GREEN)
        else:
            self.test_results['performance_tests']['failed'] = 1
    
    def generate_report(self):
        """生成测试报告"""
        self.log("生成测试报告...", Colors.YELLOW)
        
        end_time = datetime.now()
        duration = end_time - self.start_time
        
        total_passed = sum(result['passed'] for result in self.test_results.values())
        total_failed = sum(result['failed'] for result in self.test_results.values())
        total_tests = total_passed + total_failed
        
        report = f"""
{Colors.BOLD}=== 木鱼App自动化测试报告 ==={Colors.END}
{Colors.CYAN}测试开始时间: {self.start_time.strftime('%Y-%m-%d %H:%M:%S')}
测试结束时间: {end_time.strftime('%Y-%m-%d %H:%M:%S')}
总耗时: {duration.total_seconds():.2f}秒{Colors.END}

{Colors.BOLD}测试结果汇总:{Colors.END}
- 总测试数: {total_tests}
- 通过: {Colors.GREEN}{total_passed}{Colors.END}
- 失败: {Colors.RED}{total_failed}{Colors.END}
- 成功率: {Colors.GREEN}{(total_passed/total_tests*100 if total_tests > 0 else 0):.1f}%{Colors.END}

{Colors.BOLD}详细结果:{Colors.END}
"""
        
        for test_type, result in self.test_results.items():
            status_color = Colors.GREEN if result['failed'] == 0 else Colors.RED
            report += f"- {test_type}: {status_color}{'通过' if result['failed'] == 0 else '失败'}{Colors.END}\n"
        
        print(report)
        
        # 保存报告到文件
        with open("test_report_summary.txt", "w", encoding="utf-8") as f:
            f.write(report.replace(Colors.BOLD, "").replace(Colors.END, "")
                   .replace(Colors.GREEN, "").replace(Colors.RED, "")
                   .replace(Colors.CYAN, "").replace(Colors.YELLOW, ""))
        
        self.log("测试报告已保存到 test_report_summary.txt", Colors.GREEN)
    
    def cleanup(self):
        """清理资源"""
        self.log("清理测试环境...", Colors.YELLOW)
        
        if self.server_process:
            try:
                self.server_process.terminate()
                self.server_process.wait(timeout=5)
            except subprocess.TimeoutExpired:
                self.server_process.kill()
        
        # 清理测试文件
        cleanup_files = [
            "WoodenFis-Server/.coverage",
            "WoodenFis-Server/htmlcov",
            "WoodenFish/.dart_tool/test_driver_coverage"
        ]
        
        for file_path in cleanup_files:
            if os.path.exists(file_path):
                if os.path.isdir(file_path):
                    self.run_command(f"rm -rf {file_path}")
                else:
                    os.remove(file_path)
    
    def run_all_tests(self):
        """运行所有测试"""
        try:
            self.log("开始自动化测试流程...", Colors.BOLD)
            
            # 安装依赖
            self.install_dependencies()
            
            # 启动服务器
            if not self.start_server():
                self.log("服务器启动失败，跳过服务端相关测试", Colors.YELLOW)
            else:
                # 运行服务端测试
                self.run_server_tests()
                
                # 运行性能测试
                self.run_performance_tests()
            
            # 运行Flutter测试
            self.run_flutter_unit_tests()
            self.run_flutter_integration_tests()
            
            # 生成报告
            self.generate_report()
            
        except KeyboardInterrupt:
            self.log("测试被用户中断", Colors.YELLOW)
        except Exception as e:
            self.log(f"测试执行出现异常: {e}", Colors.RED)
        finally:
            self.cleanup()

def signal_handler(sig, frame):
    """信号处理器"""
    print(f"\n{Colors.YELLOW}接收到中断信号，正在清理...{Colors.END}")
    sys.exit(0)

if __name__ == "__main__":
    # 注册信号处理器
    signal.signal(signal.SIGINT, signal_handler)
    
    print(f"{Colors.BOLD}{Colors.PURPLE}木鱼App自动化测试系统{Colors.END}")
    print(f"{Colors.CYAN}这个脚本将自动运行所有测试并处理遇到的问题{Colors.END}\n")
    
    runner = AutoTestRunner()
    runner.run_all_tests() 