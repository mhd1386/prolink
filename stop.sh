#!/bin/bash
# اسکریپت توقف ربات irProLink

# پیدا کردن PID ربات
PID=$(ps aux | grep "python3.*main.py" | grep -v grep | awk '{print $2}')

if [ -z "$PID" ]; then
    echo "ربات در حال اجرا نیست"
else
    kill $PID
    echo "ربات متوقف شد (PID: $PID)"
fi
