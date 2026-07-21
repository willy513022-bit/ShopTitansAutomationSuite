@echo off
cd /d "%~dp0"
python -m pytest tests\test_notification_state.py tests\test_world_state.py tests\test_world_state_builder.py tests\test_world_state_models.py tests\test_popup_models.py tests\test_popup_parser.py tests\test_popup_priority.py tests\test_popup_detector.py tests\test_notification_models.py tests\test_notification_parser.py tests\test_notification_detector.py tests\test_template_matcher.py -v
pause
