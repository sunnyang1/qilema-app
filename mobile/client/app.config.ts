import { ExpoConfig, ConfigContext } from 'expo/config';

const appName = process.env.COZE_PROJECT_NAME || process.env.EXPO_PUBLIC_COZE_PROJECT_NAME || '应用';
const projectId = process.env.COZE_PROJECT_ID || process.env.EXPO_PUBLIC_COZE_PROJECT_ID;
const slugAppName = projectId ? `app${projectId}` : 'myapp';

// 安全的包名生成函数 - 确保 Android 包名符合规范
const getSafePackageName = (id?: string): string => {
  if (!id) return 'app';

  // 如果 ID 是纯数字，添加前缀
  if (/^\d+$/.test(id)) {
    return `app${id}`;
  }

  // 确保 ID 以字母开头
  if (/^\d/.test(id)) {
    return `app${id}`;
  }

  // 移除非法字符，只保留字母、数字和下划线
  return id.replace(/[^a-zA-Z0-9_]/g, '');
};

const safePackageName = getSafePackageName(projectId);
const packageName = `com.qilema.${safePackageName}`;

export default ({ config }: ConfigContext): ExpoConfig => {
  return {
    ...config,
    "name": appName,
    "slug": slugAppName,
    "version": "1.0.0",
    "orientation": "portrait",
    "icon": "./assets/images/icon.png",
    "scheme": "myapp",
    "userInterfaceStyle": "automatic",
    "newArchEnabled": true,
    "ios": {
      "supportsTablet": true,
      "bundleIdentifier": `com.qilema.${safePackageName}`
    },
    "android": {
      "adaptiveIcon": {
        "foregroundImage": "./assets/images/adaptive-icon.png",
        "backgroundColor": "#ffffff"
      },
      "package": packageName
    },
    "web": {
      "bundler": "metro",
      "output": "single",
      "favicon": "./assets/images/favicon.png"
    },
    "plugins": [
      process.env.EXPO_PUBLIC_BACKEND_BASE_URL ? [
        "expo-router",
        {
          "origin": process.env.EXPO_PUBLIC_BACKEND_BASE_URL
        }
      ] : 'expo-router',
      [
        "expo-splash-screen",
        {
          "image": "./assets/images/splash-icon.png",
          "imageWidth": 200,
          "resizeMode": "contain",
          "backgroundColor": "#ffffff"
        }
      ],
      [
        "expo-image-picker",
        {
          "photosPermission": `允许${appName}访问您的相册，以便您上传或保存图片。`,
          "cameraPermission": `允许${appName}使用您的相机，以便您直接拍摄照片上传。`,
          "microphonePermission": `允许${appName}访问您的麦克风，以便您拍摄带有声音的视频。`
        }
      ],
      [
        "expo-location",
        {
          "locationWhenInUsePermission": `${appName}需要访问您的位置以提供周边服务及导航功能。`
        }
      ],
      [
        "expo-camera",
        {
          "cameraPermission": `${appName}需要访问相机以拍摄照片和视频。`,
          "microphonePermission": `${appName}需要访问麦克风以录制视频声音。`,
          "recordAudioAndroid": true
        }
      ]
    ],
    "experiments": {
      "typedRoutes": true
    }
  }
}
