#!/bin/bash
set -ex

# Setup rabbit
rabbitmq-server -detached
sleep 20

# Create vhosts
rabbitmqctl add_vhost vh_sensors
rabbitmqctl add_vhost vh_sensors_testing

# Add permissions
rabbitmqctl set_permissions -p vh_sensors testuser ".*" ".*" ".*"
rabbitmqctl set_permissions -p vh_sensors_testing testuser ".*" ".*" ".*"

kill -9 $(ps aux | grep rabbitmq_server | grep erlang | awk '{print $2}') >/dev/null 2>&1
sleep 3

# Effective rabbit run
rabbitmq-server
