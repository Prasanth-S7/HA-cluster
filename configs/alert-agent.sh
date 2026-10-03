#!/bin/sh

: ${CRM_alert_recipient:=""}
: ${CRM_alert_node_sequence:=""}
: ${CRM_alert_timestamp:=""}
: ${CRM_alert_kind:=""}
: ${CRM_alert_node:=""}
: ${CRM_alert_desc:=""}
: ${CRM_alert_task:=""}
: ${CRM_alert_rsc:=""}
: ${CRM_alert_attribute_name:=""}
: ${CRM_alert_attribute_value:=""}
: ${CRM_alert_rc:="-1"}
: ${CRM_alert_target_rc:="-1"}

LOGFILE="/var/log/crm_alerts_log.log"

# Ignore routine successful monitor passes
if [ "$CRM_alert_kind" = "resource" ] && [ "$CRM_alert_task" = "monitor" ]; then
    if [ "$CRM_alert_rc" -eq "$CRM_alert_target_rc" ]; then
        exit 0
    fi
fi

# Ignore internal cancellations
if [ "$CRM_alert_desc" = "Cancelled" ]; then
    exit 0
fi

# Defaults (in case kind doesn't match any known branch below)
status="info"
message="Unhandled alert kind: $CRM_alert_kind"

# Resource alerts
if [ "$CRM_alert_kind" = "resource" ]; then
    if [ "$CRM_alert_task" = "monitor" ]; then
        if [ "$CRM_alert_rc" -eq 7 ]; then
            status="error"
            message="Resource $CRM_alert_rsc on node $CRM_alert_node is NOT RUNNING ($CRM_alert_desc)"
        else
            status="error"
            message="Resource $CRM_alert_rsc on node $CRM_alert_node is in an unexpected state"
        fi
    elif [ "$CRM_alert_task" = "start" ] || [ "$CRM_alert_task" = "stop" ]; then
        if [ "$CRM_alert_rc" -ne 0 ]; then
            status="error"
            message="Resource $CRM_alert_rsc on node $CRM_alert_node failed to $CRM_alert_task ($CRM_alert_desc)"
        else
            status="info"
            message="Resource $CRM_alert_rsc on node $CRM_alert_node successfully completed $CRM_alert_task ($CRM_alert_desc)"
        fi
    else
        status="error"
        message="Resource $CRM_alert_rsc on node $CRM_alert_node is in an unexpected state ($CRM_alert_desc)"
    fi
fi

# Node alerts
if [ "$CRM_alert_kind" = "node" ]; then
    if [ "$CRM_alert_desc" = "member" ]; then
        status="info"
        message="Node $CRM_alert_node has joined the cluster"
    elif [ "$CRM_alert_desc" = "lost" ]; then
        status="error"
        message="Node $CRM_alert_node has been lost (OFFLINE)"
    fi
fi

# Write one JSON object per alert
{
    printf '{\n'
    printf '    "timestamp": "%s",\n' "$CRM_alert_timestamp"
    printf '    "status": "%s",\n' "$status"
    printf '    "kind": "%s",\n' "$CRM_alert_kind"
    printf '    "node": "%s",\n' "$CRM_alert_node"
    printf '    "resource": "%s",\n' "$CRM_alert_rsc"
    printf '    "desc": "%s"\n' "$message"
    printf '}\n'
} >> "$LOGFILE"