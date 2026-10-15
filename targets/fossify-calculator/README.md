# 实测对象：Fossify Calculator 1.4.0

来源：[官方 GitHub Release](https://github.com/FossifyOrg/Calculator/releases/tag/1.4.0)。

在项目根目录下载：

```powershell
New-Item -ItemType Directory -Path targets/fossify-calculator -Force
Invoke-WebRequest -Uri 'https://github.com/FossifyOrg/Calculator/releases/download/1.4.0/calculator-10-foss-release.apk' -OutFile targets/fossify-calculator/calculator-1.4.0.apk
Get-FileHash targets/fossify-calculator/calculator-1.4.0.apk -Algorithm SHA256
```

实测 SHA-256：`7c5443c22d6d62c67dfe80df33ea9161ff0fa440f92590bcb45d7008b57613ed`。

包名：`org.fossify.math`。APK 不纳入本仓库，使用官方发布文件。平台可测试其他目录中的独立 APK。
