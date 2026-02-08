#!/bin/bash

# CONFIGURATION
URL="http://192.168.58.2:30005/upload" 
URL="http://127.0.0.1:58331/upload" 
FILE="test.jpg"
REQUESTS=20

echo "--- Starting Load Test: Distributed Processing ---"

START_TIME=$(date +%s)

# Function to send request and print worker name
send_request() {
    # 1. Send Request
    # 2. Grep for the pod name in the JSON response
    # 3. Print it nicely
    RESPONSE=$(curl -s -F "file=@$FILE" -F "effects=blur" "$URL")
    
    # Extract Pod Name using grep/sed (simple JSON parsing)
    POD_NAME=$(echo "$RESPONSE" | grep -o '"processed_by_pod":"[^"]*"' | cut -d'"' -f4)
    
    if [ -z "$POD_NAME" ]; then
        echo "Request Failed or Timed Out"
    else
        echo "✅ Request handled by: $POD_NAME"
    fi
}

# Loop to fire requests in parallel
for ((i=1; i<=REQUESTS; i++)); do
    send_request & 
done

# Wait for all background jobs
wait

END_TIME=$(date +%s)
DURATION=$((END_TIME - START_TIME))

echo ""
echo "--- Finished in ${DURATION} seconds ---"