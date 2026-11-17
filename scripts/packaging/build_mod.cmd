@echo off
rem 用 Windows dotnet 构建并打包 game_mod；环境变量在这里显式设置，WSL 导出的不会传给 Windows 进程。
rem 用法：双击或在 Windows 侧执行 scripts\packaging\build_mod.cmd
cd /d D:\project\other\TFWR_Simulator
set TFWR_GAME_ROOT=D:\Steam\steamapps\common\The Farmer Was Replaced
set TFWR_BEPINEX_ROOT=C:\Users\MLJ\AppData\Roaming\r2modmanPlus-local\TheFarmerWasReplaced\profiles\Default\BepInEx
"C:\Program Files\dotnet\dotnet.exe" build game_mod\TFWROracleRunner.csproj -c Release -t:PackageThunderstore
