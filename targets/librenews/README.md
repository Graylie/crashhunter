# LibreNews 1.4 历史缺陷测试对象

官方 APK：[Release v1.4](https://github.com/milesmcc/LibreNews-Android/releases/tag/v1.4)。原始缺陷：[Issue #22](https://github.com/milesmcc/LibreNews-Android/issues/22)。

在项目根目录执行：

```powershell
New-Item -ItemType Directory -Path targets/librenews -Force
gh release download v1.4 --repo milesmcc/LibreNews-Android --pattern LibreNews-1.4.apk --dir targets/librenews
Get-FileHash targets/librenews/LibreNews-1.4.apk -Algorithm SHA256
```

实测 APK SHA-256：`80110343f0cbfa7fd8a99514425bf375a4dd2c36ae6b8f8c4ddf3d0ad8523d6a`。

包名：`app.librenews.io.librenews`；版本名 1.4、版本码 5、targetSdk 26。原始问题使用 F-Droid 1.4，本次使用官方 GitHub Release 1.4，实测捕获到相同异常和核心调用栈。APK 不提交到本仓库。

该用例是对已公开缺陷的复现，应用代码未修改。服务地址和自动刷新设置会被用例更改，建议在测试用模拟器运行。
