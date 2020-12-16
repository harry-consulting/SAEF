from django import template
from saef.enums import MonitorStatus

register = template.Library()


@register.inclusion_tag('charts/chart_doughnut.html')
def chart_doughnut(session_meta_data, canvas_id):

    failed_bucket = []
    issue_bucket = []
    success_bucket = []
    for meta_data in session_meta_data:
        if meta_data.status_type == MonitorStatus.SUCCEEDED.value:
            success_bucket.append(meta_data)
        elif meta_data.status_type == MonitorStatus.SUCCEEDED_ISSUE.value:
            issue_bucket.append(meta_data)
        elif meta_data.status_type == MonitorStatus.FAILED.value:
            failed_bucket.append(meta_data)

    return {"success": len(success_bucket),
            "issue": len(issue_bucket),
            "failed": len(failed_bucket),
            "canvas_id": canvas_id}
