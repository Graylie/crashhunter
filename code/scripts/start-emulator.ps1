param(
    [string]$SdkPath = 'E:\AndroidStudio\Sdk',
    [string]$AvdName = 'Medium_Phone_API_37.0',
    [string]$AvdHome = 'E:\AndroidStudio\Avd'
)

$ErrorActionPreference = 'Stop'
$emulatorPath = Join-Path $SdkPath 'emulator\emulator.exe'
if (-not (Test-Path -LiteralPath $emulatorPath)) {
    throw "Emulator not found: $emulatorPath"
}
& $emulatorPath -accel-check
if ($LASTEXITCODE -ne 0) { throw 'Hardware acceleration is unavailable.' }
$env:ANDROID_AVD_HOME = $AvdHome
$env:ANDROID_SDK_ROOT = $SdkPath
# Keep the virtual device's configuration and runtime files on the selected drive.
& $emulatorPath -avd $AvdName -no-snapshot -no-boot-anim
