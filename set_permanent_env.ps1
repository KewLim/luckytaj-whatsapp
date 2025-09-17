# PowerShell script to set permanent Android SDK environment variables
Write-Host "===============================================" -ForegroundColor Cyan
Write-Host "    SETTING PERMANENT ANDROID ENVIRONMENT" -ForegroundColor Cyan
Write-Host "===============================================" -ForegroundColor Cyan
Write-Host ""

# Get the current directory path for android-sdk
$currentDir = Get-Location
$androidSdkPath = Join-Path $currentDir "android-sdk"

Write-Host "Setting Android SDK environment variables..." -ForegroundColor Yellow
Write-Host "Android SDK Path: $androidSdkPath" -ForegroundColor Green

try {
    # Set ANDROID_HOME for current user
    [Environment]::SetEnvironmentVariable("ANDROID_HOME", $androidSdkPath, "User")
    Write-Host "✅ ANDROID_HOME set to: $androidSdkPath" -ForegroundColor Green

    # Set ANDROID_SDK_ROOT for current user
    [Environment]::SetEnvironmentVariable("ANDROID_SDK_ROOT", $androidSdkPath, "User")
    Write-Host "✅ ANDROID_SDK_ROOT set to: $androidSdkPath" -ForegroundColor Green

    # Get current PATH
    $currentPath = [Environment]::GetEnvironmentVariable("PATH", "User")
    $platformToolsPath = Join-Path $androidSdkPath "platform-tools"

    # Add platform-tools to PATH if not already there
    if ($currentPath -notlike "*$platformToolsPath*") {
        $newPath = "$currentPath;$platformToolsPath"
        [Environment]::SetEnvironmentVariable("PATH", $newPath, "User")
        Write-Host "✅ Added platform-tools to PATH: $platformToolsPath" -ForegroundColor Green
    } else {
        Write-Host "ℹ️ Platform-tools already in PATH" -ForegroundColor Blue
    }

    Write-Host ""
    Write-Host "🎉 Environment variables set successfully!" -ForegroundColor Green
    Write-Host ""
    Write-Host "IMPORTANT: You need to restart the following for changes to take effect:" -ForegroundColor Yellow
    Write-Host "1. Close and reopen any Command Prompt/PowerShell windows" -ForegroundColor White
    Write-Host "2. Close and reopen Appium Inspector" -ForegroundColor White
    Write-Host "3. Restart any IDEs or development tools" -ForegroundColor White
    Write-Host ""
    Write-Host "After restarting, you can verify with:" -ForegroundColor Cyan
    Write-Host "echo `$env:ANDROID_HOME" -ForegroundColor White
    Write-Host "echo `$env:ANDROID_SDK_ROOT" -ForegroundColor White

} catch {
    Write-Host "❌ Error setting environment variables: $($_.Exception.Message)" -ForegroundColor Red
    Write-Host ""
    Write-Host "Try running PowerShell as Administrator if this fails." -ForegroundColor Yellow
}

Write-Host ""
Write-Host "Press any key to continue..."
Read-Host