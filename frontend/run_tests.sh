#!/bin/bash

# 起了吗 App 测试运行脚本
# 支持运行所有测试、单元测试、特定模块测试，并生成覆盖率报告

set -e

# 颜色定义
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# 帮助信息
show_help() {
    echo "起了吗 App 测试运行脚本"
    echo ""
    echo "用法: ./run_tests.sh [选项]"
    echo ""
    echo "选项:"
    echo "  all                运行所有测试"
    echo "  unit               运行单元测试"
    echo "  core               运行核心模块测试"
    echo "  models             运行数据模型测试"
    echo "  features           运行功能模块测试"
    echo "  coverage           生成测试覆盖率报告"
    echo "  coverage:html      生成HTML格式的覆盖率报告"
    echo "  watch              监视模式运行测试"
    echo "  help               显示此帮助信息"
    echo ""
    echo "示例:"
    echo "  ./run_tests.sh                    # 默认运行所有测试"
    echo "  ./run_tests.sh unit               # 只运行单元测试"
    echo "  ./run_tests.sh coverage:html      # 生成HTML覆盖率报告"
    echo ""
}

# 打印带颜色的消息
print_info() {
    echo -e "${BLUE}[INFO]${NC} $1"
}

print_success() {
    echo -e "${GREEN}[SUCCESS]${NC} $1"
}

print_error() {
    echo -e "${RED}[ERROR]${NC} $1"
}

print_warning() {
    echo -e "${YELLOW}[WARNING]${NC} $1"
}

# 运行所有测试
run_all_tests() {
    print_info "运行所有测试..."
    flutter test --no-pub
    print_success "所有测试通过!"
}

# 运行单元测试
run_unit_tests() {
    print_info "运行单元测试..."
    flutter test test/unit --no-pub
    print_success "单元测试通过!"
}

# 运行核心模块测试
run_core_tests() {
    print_info "运行核心模块测试..."
    flutter test test/unit/core --no-pub
    print_success "核心模块测试通过!"
}

# 运行数据模型测试
run_models_tests() {
    print_info "运行数据模型测试..."
    flutter test test/unit/core --no-pub
    print_success "数据模型测试通过!"
}

# 运行功能模块测试
run_features_tests() {
    print_info "运行功能模块测试..."
    flutter test test/unit/features --no-pub
    print_success "功能模块测试通过!"
}

# 生成覆盖率报告
run_coverage() {
    print_info "生成测试覆盖率报告..."
    flutter test --coverage --no-pub
    print_success "覆盖率报告已生成到 coverage/lcov.info"
}

# 生成HTML格式的覆盖率报告
run_coverage_html() {
    print_info "生成HTML格式的覆盖率报告..."
    flutter test --coverage --no-pub
    
    # 检查是否安装了 lcov
    if command -v lcov &> /dev/null; then
        lcov --remove coverage/lcov.info 'lib/**/*.g.dart' 'lib/**/*.freezed.dart' -o coverage/lcov_clean.info
        genhtml coverage/lcov_clean.info -o coverage/html
        print_success "HTML覆盖率报告已生成到 coverage/html/index.html"
        print_info "请在浏览器中打开 coverage/html/index.html 查看报告"
    else
        print_warning "未安装 lcov，跳过HTML报告生成"
        print_info "可以使用 'brew install lcov' 安装 lcov"
        print_success "覆盖率数据已保存到 coverage/lcov.info"
    fi
}

# 监视模式运行测试
run_watch() {
    print_info "以监视模式运行测试..."
    print_info "按 'q' 退出，按 'r' 重新运行"
    flutter test --watch --no-pub
}

# 主函数
main() {
    # 检查是否在正确的目录
    if [ ! -f "pubspec.yaml" ]; then
        print_error "请在项目根目录运行此脚本"
        exit 1
    fi

    # 获取命令参数
    COMMAND=${1:-all}

    case $COMMAND in
        all)
            run_all_tests
            ;;
        unit)
            run_unit_tests
            ;;
        core)
            run_core_tests
            ;;
        models)
            run_models_tests
            ;;
        features)
            run_features_tests
            ;;
        coverage)
            run_coverage
            ;;
        coverage:html)
            run_coverage_html
            ;;
        watch)
            run_watch
            ;;
        help|--help|-h)
            show_help
            ;;
        *)
            print_error "未知命令: $COMMAND"
            echo ""
            show_help
            exit 1
            ;;
    esac
}

# 运行主函数
main "$@"
