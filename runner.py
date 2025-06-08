import subprocess
import sys
import time
from datetime import datetime, timedelta

def run_bot():
    print("Запускаю бота...")
    # Запускаем бота как отдельный процесс (он работает в фоне)
    return subprocess.Popen([sys.executable, "Your way to root bot script"])

def update_stock():
    print("Получаю сток...")
    subprocess.run([sys.executable, "Your way to get stock script"])
    print("Сток получен...")

def wait_until_next_minute_with_offset():
    while True:
        now = datetime.now()
        # Следующая минута + 5 секунд
        next_time = (now + timedelta(minutes=1)).replace(second=5, microsecond=0)
        wait = (next_time - now).total_seconds()
        if wait <= 0:
            break
        print(f"Жду {int(wait)} секунд до следующего обновления...")
        time.sleep(min(wait, 30))
        update_stock()

def main():
    bot_proc = run_bot()
    try:
        update_stock()  # Первое обновление при запуске
        while True:
            wait_until_next_minute_with_offset()
            update_stock()
    except KeyboardInterrupt:
        print("Останавливаем бота...")
        bot_proc.terminate()
        bot_proc.wait()
        print("Бот остановлен.")

if __name__ == "__main__":
    main()
