def normalize_date(date):
    if len(date) <= 4:
        return str(date)+'-01-01'
    elif len(date) == 7:
        return str(date) + '-01'
    return date
        