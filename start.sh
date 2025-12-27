#!/bin/bash
# اسکریپت شروع ربات irProLink

cd "$(dirname "$0")"

# فعال کردن محیط مجازی اگر وجود دارد
if [ -d "venv" ]; then
    source venv/bin/activate
fi

# اجرای ربات
python3 main.py
