@echo off
title NSIA Call Center - Patronne
echo Installation des dependances...
pip install -r requirements.txt
echo.
echo Lancement de l'application...
streamlit run app.py
pause
