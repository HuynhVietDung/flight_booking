## Cấu hình và biến môi trường

Nguồn: `src/config/settings.py`

- `Settings` là Singleton, tải `.env` tại project root, tạo sẵn thư mục `data/` và `logs/` nếu chưa có.
- Các nhóm cấu hình:
  - `LLMConfig`: `LLM_MODEL`, `LLM_TEMPERATURE`, `LLM_MAX_TOKENS`, `OPENAI_API_KEY`, `OPENAI_BASE_URL`
  - `AgentConfig`: `INTENT_CONFIDENCE_THRESHOLD`, `DEFAULT_PASSENGERS`, `DEFAULT_CLASS_TYPE`
  - `BookingConfig`: danh sách trường yêu cầu theo intent, tên thân thiện cho câu hỏi
  - `MockDataConfig`: airlines, cities (dùng cho mock)

### .env mẫu
```bash
# LLM
LLM_MODEL=gpt-4.1-mini
LLM_TEMPERATURE=0
LLM_MAX_TOKENS=1000

# Agent
INTENT_CONFIDENCE_THRESHOLD=0.6
DEFAULT_PASSENGERS=1
DEFAULT_CLASS_TYPE=economy

# OpenAI (bắt buộc)
OPENAI_API_KEY=your-openai-api-key
OPENAI_BASE_URL=https://api.openai.com/v1
```

### Validate cấu hình
- Hàm `settings.validate()` sẽ kiểm tra: có API key, dải giá trị hợp lệ cho temperature và confidence threshold.
