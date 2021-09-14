from celery import Celery

app = Celery("terralego")


@app.on_after_finalize.connect
def setup_periodic_tasks(sender, **kwargs):
    # Calls refresh check every 25 minutes
    sender.add_periodic_task(60 * 25, run_auto_refresh_source.s())


app.config_from_object("django.conf:settings", namespace="CELERY")

app.autodiscover_tasks()


@app.task
def run_auto_refresh_source():
    from django_geosource.periodics import auto_refresh_source

    auto_refresh_source()
