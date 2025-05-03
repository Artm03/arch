#!/bin/bash

test_endpoint() {
    endpoint=$1
    threads=$2
    connections=$3
    duration=$4
    name=$5

    echo "Testing $name with $threads threads"
    echo "========================================"
    wrk -t$threads -c$connections -d$duration --latency http://localhost:8000$endpoint
    echo "========================================"
    echo ""
}

TOKEN=$(curl -s -X POST "http://localhost:8000/token" \
     -H "Content-Type: application/json" \
     -d '{"username":"admin", "password":"secret"}' | jq -r '.access_token')

cat > auth.lua << EOF
wrk.headers["Authorization"] = "Bearer $TOKEN"
EOF

# Тестирование endpoint /users/list (без кеша)
for threads in 1 5 10
do
    test_endpoint "/users/list" $threads $threads "10s" "Users List without cache (threads: $threads)"
done

# Тестирование endpoint /users/cached/list (с кешем)
for threads in 1 5 10
do
    test_endpoint "/users/cached/list" $threads $threads "10s" "Users List with cache (threads: $threads)"
done

# Тестирование endpoint /users/details (без кеша)
for threads in 1 5 10
do
    test_endpoint "/users/details?user_id=1" $threads $threads "10s" "User Details without cache (threads: $threads)"
done

# Тестирование endpoint /users/cached/details (с кешем)
for threads in 1 5 10
do
    test_endpoint "/users/cached/details?user_id=1" $threads $threads "10s" "User Details with cache (threads: $threads)"
done

rm auth.lua
