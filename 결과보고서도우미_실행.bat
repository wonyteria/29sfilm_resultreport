@echo off
chcp 65001 > nul
cd /d "%~dp0"
python run_app.py
if errorlevel 1 (
  echo.
  echo 프로그램 실행 중 오류가 발생했습니다.
  echo 이 창의 오류 내용을 개발 담당자에게 전달해 주세요.
  pause
)
