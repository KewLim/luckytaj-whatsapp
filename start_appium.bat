@echo off
echo Starting Appium Server...
echo.
echo Server will run on: http://localhost:4723
echo Press Ctrl+C to stop the server
echo.
appium server --port 4723 --log-level info
pause