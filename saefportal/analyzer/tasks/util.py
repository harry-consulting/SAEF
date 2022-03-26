from settings.util import send_email_using_settings


def send_run_email(context, job):
    """Send start, success or failure email, if alert email addresses are given in the job."""
    context_emails = getattr(job, f"alert_on_{context}_email")

    if context_emails:
        subject = f"Job {job.name} {context}"

        if context == "start":
            last_used_parameters = job.get_last_job_run().parameters

            message = f"Job \"{job.name}\" has started running \"{job.get_task()[2]}\" with parameters " \
                      f"{last_used_parameters}."
        elif context == "success":
            message = f"Job \"{job.name}\" has succeeded."
        else:
            message = f"Job \"{job.name}\" has failed."

        send_email_using_settings(subject, message, context_emails.replace(" ", "").split(","))
