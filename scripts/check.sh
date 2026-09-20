URL="http://host.docker.internal:8000/health"

if curl -s -f "$URL" > /dev/null; then
    echo "API is UP"
else
    echo "API is DOWN"
fi