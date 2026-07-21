@echo off
cd /d "%~dp0"
python -m pytest tests\test_notification_models.py tests\test_notification_parser.py tests\test_notification_detector.py tests\test_template_matcher.py -v
pause
