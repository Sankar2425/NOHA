@echo off
cd /d C:\PROJECTS\noha
call noha_env\Scripts\activate
uvicorn main:app --reload
pause