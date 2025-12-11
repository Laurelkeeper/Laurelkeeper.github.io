@echo off
setlocal enabledelayedexpansion

rem --- 1. Copy second-order subfolders ---
set "SRC=E:\CM\Exports"
set "DEST=E:\CM\MSEhub\sets"

for /d %%A in ("%SRC%\*") do (
    for /d %%B in ("%%A\*") do (
        echo Copying %%~nxB ...
        xcopy "%%B" "%DEST%\%%~nxB" /E /I /Y >nul
    )
)

rem --- 2. Run build_site.py ---
echo Running build_site.py...
pushd E:\CM\MSEhub
python scripts\build_site.py
popd

rem --- 3. Git add/commit/push ---
pushd E:\CM\MSEhub
git add -A
git commit -m "Automated update"
git push
popd

echo Done.
endlocal
