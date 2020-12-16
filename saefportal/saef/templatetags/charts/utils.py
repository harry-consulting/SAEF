
from saef.enums import MonitorStatus

def find_min_max_date(start_date, end_date, min_date, max_date):
    if not min_date or start_date < min_date:
        min_date = start_date
    if not max_date or end_date > max_date:
        max_date = end_date
    return min_date, max_date

def append_color(color, color_map):
    color_palette = {"color": color,
                    "dark": color,
                    "light": color}
    
    if color_palette not in color_map:
        color_map.append(color_palette)
    return color_map


def chart_session(session_metadata, session_data_method, start_only=False):
    min_date = None
    max_date = None
    session_ended = None
    chart_data = []
    color_map = []
    
    if start_only:
        session_last_date = max(session_metadata, key=lambda x: x.session_created())
        session_ended = session_last_date.session_ended().timestamp()
    
    for metadata in session_metadata:
        if metadata.status_type == MonitorStatus.SUCCEEDED.value:
            color_map = append_color('#008000', color_map)
        elif metadata.status_type == MonitorStatus.SUCCEEDED_ISSUE.value:
            color_map = append_color('#ff8c00', color_map)
        elif metadata.status_type == MonitorStatus.FAILED.value:
            color_map = append_color('#ff0000', color_map)

        min_date, max_date = find_min_max_date(metadata.session_created(), 
                                               metadata.session_ended(), 
                                               min_date, max_date)
        if not start_only:
            session_ended = metadata.session_ended().timestamp()
            
        chart_data.append(session_data_method(metadata, session_ended))
        
    width = 800
    if max_date:
        dynamic_width = int((max_date - min_date).total_seconds()/100)
    
        if dynamic_width > width:
            width = dynamic_width
        
    return {'chart_data': chart_data, 'color_map': color_map, 'width': width}