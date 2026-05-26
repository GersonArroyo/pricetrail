from scraper.scraper import run
from apscheduler.schedulers.blocking import BlockingScheduler

sched = BlockingScheduler()
sched.add_job(run, 'cron', hour=2) # Schedule the job to run every day at 2 AM

run() # Run the job immediately when the script is executed
sched.start()