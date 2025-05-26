FROM python:3.11-slim

WORKDIR /app

COPY requirements.txt .
RUN pip install -r requirements.txt

COPY . .

ENV PYTHONPATH=/app

# ENV WEATHER_API_KEY="demo_api_key"

# 도구 정의 JSON 파일 생성 후 서버 시작
CMD ["sh", "-c", "python -c 'from server import generate_tool_definitions; import json; f=open(\"tool_definitions.json\", \"w\", encoding=\"utf-8\"); json.dump({\"tools\": generate_tool_definitions()}, f, ensure_ascii=False, indent=2); f.close()' && python -m uvicorn server:mcp --host 0.0.0.0 --port 8000"]
