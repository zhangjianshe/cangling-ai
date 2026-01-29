#!/bin/bash
export KAFKA_SERVER_IP_PORT="127.0.0.1:6111"
export KAFKA_TOPIC="your_topic_name"
export KAFKA_TASK_ID="task-dev-001"
python3 ../cangling/workflow/workflow.py