from app.converter.core.models.platform_details import PlatformDetails

DEFAULT_MICROSOFT_SENTINEL_RULE = {
    "displayName": "Autogenerated Microsoft Sentinel Rule",
    "description": "Autogenerated Microsoft Sentinel Rule",
    "severity": "medium",
    "enabled": True,
    "query": "",
    "queryFrequency": "PT30M",
    "queryPeriod": "PT30M",
    "triggerOperator": "GreaterThan",
    "triggerThreshold": 0,
    "suppressionDuration": "PT2H30M",
    "suppressionEnabled": True,
    "tactics": [],
    "techniques": []
}

PLATFORM_DETAILS = {
    "group_id": "sentinel",
    "group_name": "Microsoft Sentinel"
}

MICROSOFT_SENTINEL_QUERY_DETAILS = {
    "siem_type": "sentinel-kql-query",
    "name": "Microsoft Sentinel Query",
    "platform_name": "Query (Kusto)",
    **PLATFORM_DETAILS
}

MICROSOFT_SENTINEL_RULE_DETAILS = {
    "siem_type": "sentinel-kql-rule",
    "name": "Microsoft Sentinel Rule",
    "platform_name": "Rule (Kusto)",
    "first_choice": 0,
    **PLATFORM_DETAILS
}

MICROSOFT_DEFENDER_DETAILS = {
    "siem_type": "mde-kql-query",
    "group_name": "Microsoft Defender for Endpoint",
    "name": "Microsoft Defender for Endpoint",
    "platform_name": "Query (Kusto)",
    "group_id": "microsoft-defender"
}


microsoft_defender_details = PlatformDetails(**MICROSOFT_DEFENDER_DETAILS)
microsoft_sentinel_query_details = PlatformDetails(**MICROSOFT_SENTINEL_QUERY_DETAILS)
microsoft_sentinel_rule_details = PlatformDetails(**MICROSOFT_SENTINEL_RULE_DETAILS)