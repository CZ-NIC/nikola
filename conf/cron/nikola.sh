#!/bin/sh
# Copyright (C) 2013 CZ.NIC z.s.p.o. <stepan.henek@nic.cz>

. $IPKG_INSTROOT/lib/functions.sh

config_load nikola

get_parameter() {
    local sec="$1"
    local var="$2"
    local val

    config_get val "$sec" "$var"
    echo "$val"
}

get_bool_parameter() {
    local sec="$1"
    local var="$2"
    local val

    config_get_bool val "$sec" "$var" "$3"
    echo "$val"
}

server_addr=$(get_parameter server address)
max_count=$(get_parameter server max_count)

log_file=$(get_parameter logfile path)
date_format=$(get_parameter logfile date_format)

log_rotate_conf=$(get_parameter logrotate path)

debug=$(get_bool_parameter main debug 0)

optional=""
if [ -n "$max_count" ]; then
    optional="$optional -m '$max_count'"
fi
if [ -n "$log_file" ]; then
    optional="$optional -l '$log_file'"
fi
if [ -n "$date_format" ]; then
    optional="$optional -f '$date_format'"
fi
if [ -n "$log_rotate_conf" ]; then
    optional="$optional -r '$log_rotate_conf'"
fi

if [ "$debug" = 1 ]; then
    optional="$optional -d"
fi

eval nikola "$server_addr" "$optional"
