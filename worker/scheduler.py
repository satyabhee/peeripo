"""Entry point that runs all periodic jobs. The screenshot watcher runs separately
(it's event-driven, not polled) -- launch it with `python -m worker.screenshot_watcher`.
"""

from apscheduler.schedulers.blocking import BlockingScheduler

from . import canvas_poller, life360_poller, spotify_poller, stock_engine

scheduler = BlockingScheduler()

scheduler.add_job(life360_poller.poll_once, "interval", minutes=10, id="life360")
scheduler.add_job(canvas_poller.poll_once, "interval", hours=6, id="canvas")
scheduler.add_job(spotify_poller.poll_once, "interval", hours=6, id="spotify")
scheduler.add_job(stock_engine.run_daily_tick, "cron", hour=23, minute=59, id="stock_tick")

if __name__ == "__main__":
    print("PeerIPO worker scheduler starting...")
    scheduler.start()
