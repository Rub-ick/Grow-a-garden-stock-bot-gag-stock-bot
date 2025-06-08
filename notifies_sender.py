import asyncio
from datetime import datetime, timedelta

async def periodic_notify_task_regular(bot, interval=5, delay_minutes=1, delay_seconds=30):
    from notify_utils import notify_users_if_fruits_in_stock
    while True:
        now = datetime.now()
        next_minute = ((now.minute // interval) + 1) * interval
        next_mark_time = now.replace(second=0, microsecond=0)
        if next_minute < 60:
            next_mark_time = next_mark_time.replace(minute=next_minute)
        else:
            next_mark_time = (next_mark_time.replace(minute=0) + timedelta(hours=1))
        notify_time = next_mark_time + timedelta(minutes=delay_minutes, seconds=delay_seconds)
        wait_sec = (notify_time - now).total_seconds()
        print(f"[NOTIFY] Regular: ждём {int(wait_sec)} сек ({notify_time.strftime('%H:%M:%S')})")
        await asyncio.sleep(wait_sec)
        await notify_users_if_fruits_in_stock(bot)

async def periodic_notify_task_event(bot, delay_minutes=0, delay_seconds=30):
    from notify_utils import notify_users_if_event_items_in_stock
    while True:
        now = datetime.now()
        # Следующий полный час
        next_hour = now.hour + 1 if now.minute > 0 or now.second > 0 else now.hour
        next_mark_time = now.replace(minute=0, second=0, microsecond=0)
        if next_hour > now.hour:
            next_mark_time += timedelta(hours=1, minutes=1, seconds=30)
        notify_time = next_mark_time + timedelta(minutes=delay_minutes, seconds=delay_seconds)
        wait_sec = (notify_time - now).total_seconds()
        print(f"[NOTIFY] Event: ждём {int(wait_sec)} сек ({notify_time.strftime('%H:%M:%S')})")
        await asyncio.sleep(wait_sec)
        await notify_users_if_event_items_in_stock(bot)
