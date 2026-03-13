/**
 * Error Boundary 组件
 * 捕获 React 组件树中的 JavaScript 错误，防止整个应用崩溃
 */
import React, { Component, ErrorInfo, ReactNode } from 'react';
import { View, Text, StyleSheet, TouchableOpacity, SafeAreaView } from 'react-native';
import { Colors, Typography, Spacing, BorderRadius } from '@/constants/theme-warm';

interface Props {
  children: ReactNode;
  fallback?: ReactNode;
  onError?: (error: Error, errorInfo: ErrorInfo) => void;
  onReset?: () => void;
}

interface State {
  hasError: boolean;
  error: Error | null;
  errorInfo: ErrorInfo | null;
}

const styles = StyleSheet.create({
  container: {
    flex: 1,
    backgroundColor: Colors.backgroundRoot,
  },
  content: {
    flex: 1,
    justifyContent: 'center',
    alignItems: 'center',
    paddingHorizontal: Spacing.xl,
  },
  icon: {
    fontSize: 64,
    marginBottom: Spacing.lg,
  },
  title: {
    ...Typography.h2,
    color: Colors.textPrimary,
    textAlign: 'center',
    marginBottom: Spacing.md,
  },
  message: {
    ...Typography.body,
    color: Colors.textSecondary,
    textAlign: 'center',
    marginBottom: Spacing.xl,
    lineHeight: 24,
  },
  errorDetails: {
    backgroundColor: Colors.backgroundTertiary,
    borderRadius: BorderRadius.lg,
    padding: Spacing.lg,
    marginBottom: Spacing.xl,
    width: '100%',
    maxHeight: 200,
  },
  errorText: {
    ...Typography.small,
    color: Colors.error,
    fontFamily: 'monospace',
  },
  button: {
    backgroundColor: Colors.primary,
    paddingVertical: Spacing.md,
    paddingHorizontal: Spacing.xl,
    borderRadius: BorderRadius.xl,
    minWidth: 200,
    alignItems: 'center',
  },
  buttonText: {
    ...Typography.bodyMedium,
    color: Colors.backgroundDefault,
  },
  secondaryButton: {
    marginTop: Spacing.md,
    paddingVertical: Spacing.sm,
    paddingHorizontal: Spacing.lg,
  },
  secondaryButtonText: {
    ...Typography.body,
    color: Colors.textSecondary,
  },
});

/**
 * 默认错误回退 UI
 */
function DefaultFallback({
  error,
  onReset,
}: {
  error: Error | null;
  onReset: () => void;
}) {
  return (
    <SafeAreaView style={styles.container}>
      <View style={styles.content}>
        <Text style={styles.icon}>⚠️</Text>
        <Text style={styles.title}>出错了</Text>
        <Text style={styles.message}>
          应用遇到了问题，请尝试重新加载页面。
          如果问题持续存在，请联系客服支持。
        </Text>

        {__DEV__ && error && (
          <View style={styles.errorDetails}>
            <Text style={styles.errorText} numberOfLines={10}>
              {error.message}
            </Text>
          </View>
        )}

        <TouchableOpacity style={styles.button} onPress={onReset} activeOpacity={0.8}>
          <Text style={styles.buttonText}>重新加载</Text>
        </TouchableOpacity>

        {__DEV__ && (
          <TouchableOpacity style={styles.secondaryButton} onPress={onReset}>
            <Text style={styles.secondaryButtonText}>忽略错误继续</Text>
          </TouchableOpacity>
        )}
      </View>
    </SafeAreaView>
  );
}

/**
 * Error Boundary 类组件
 * 用于捕获子组件树中的 JavaScript 错误
 */
export class ErrorBoundary extends Component<Props, State> {
  constructor(props: Props) {
    super(props);
    this.state = {
      hasError: false,
      error: null,
      errorInfo: null,
    };
  }

  static getDerivedStateFromError(error: Error): State {
    // 更新 state 使下一次渲染显示降级 UI
    return {
      hasError: true,
      error,
      errorInfo: null,
    };
  }

  componentDidCatch(error: Error, errorInfo: ErrorInfo) {
    // 记录错误信息
    this.setState({
      error,
      errorInfo,
    });

    // 调用错误回调
    if (this.props.onError) {
      this.props.onError(error, errorInfo);
    }

    // 开发环境打印错误
    if (__DEV__) {
      console.error('ErrorBoundary caught an error:', error, errorInfo);
    }

    // 生产环境可以在这里上报错误到监控服务
    // 例如：Sentry, Bugsnag 等
    // if (!__DEV__) {
    //   reportError(error, errorInfo);
    // }
  }

  handleReset = () => {
    this.setState({
      hasError: false,
      error: null,
      errorInfo: null,
    });

    if (this.props.onReset) {
      this.props.onReset();
    }
  };

  render() {
    if (this.state.hasError) {
      // 自定义 fallback UI
      if (this.props.fallback) {
        return this.props.fallback;
      }

      // 默认 fallback UI
      return <DefaultFallback error={this.state.error} onReset={this.handleReset} />;
    }

    return this.props.children;
  }
}

export default ErrorBoundary;
