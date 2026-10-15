# Android 模拟器启动

本机 Android SDK 位于 `E:\AndroidStudio\Sdk`，虚拟设备配置和运行数据位于 `E:\AndroidStudio\Avd`。

在项目根目录运行：

```powershell
powershell -NoProfile -ExecutionPolicy Bypass -File .\code\scripts\start-emulator.ps1
```

检查设备连接：

```powershell
& 'E:\AndroidStudio\Sdk\platform-tools\adb.exe' devices -l
```

首次启动可能需要几分钟。出现 `emulator-5554 device` 后，可使用 ADB 安装 APK 和运行测试。

启动脚本支持 `-SdkPath`、`-AvdName` 和 `-AvdHome` 参数。运行时关闭快照，配置及用户数据保存在指定的虚拟设备目录。
