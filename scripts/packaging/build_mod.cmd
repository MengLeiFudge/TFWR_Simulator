@echo off
setlocal
pushd "%~dp0..\.." || exit /b 1
py -3 game_control\tools\build_game_mod.py %*
set "build_status=%errorlevel%"
popd
exit /b %build_status%
