# 🎫 Flight Booking Agent - Graph Flow Diagram

## 🔄 **Luồng xử lý tổng quan**

```
START
  ↓
┌─────────────────┐
│ Intent          │ ← Phân loại intent của user
│ Classification  │   với confidence score
└─────────────────┘
  ↓
┌─────────────────┐
│ Route Based     │ ← Quyết định luồng tiếp theo
│ on Intent       │   dựa trên intent & confidence
└─────────────────┘
  ↓
┌─────────────────┐     ┌─────────────────┐
│ Collect Info    │ ←→ │ Process Booking │ ←→ END
│ (Can End Flow)  │     │ (Main Logic)    │
└─────────────────┘     └─────────────────┘
```

## 📊 **Chi tiết từng Node**

### **1. 🎯 Intent Classification Node**

**Input**: User message  
**Output**: Intent + Confidence score + Reasoning

```python
def classify_intent(self, state: FlightBookingState) -> FlightBookingState:
    # Phân tích message của user
    # Phân loại thành các intent:
    # - book_flight, search_flights, check_weather
    # - flight_status, booking_info, cancel_booking
    # - general_inquiry, greeting, provide_info
    
    # Trả về:
    # - intent: loại intent
    # - confidence: độ tin cậy (0-1)
    # - reasoning: lý do phân loại
```

**Intent Categories**:
- `book_flight` - Đặt vé máy bay
- `search_flights` - Tìm kiếm chuyến bay
- `check_weather` - Kiểm tra thời tiết
- `flight_status` - Trạng thái chuyến bay
- `booking_info` - Thông tin đặt vé
- `cancel_booking` - Hủy đặt vé
- `general_inquiry` - Câu hỏi chung
- `greeting` - Chào hỏi
- `provide_info` - Cung cấp thông tin

### **2. 🧭 Route Based on Intent Node**

**Input**: Intent + Confidence + Current state  
**Output**: Next node decision

```python
def route_based_on_intent(self, state) -> "collect_info" | "process_booking" | "end":
    # Logic routing:
    
    # 1. Confidence thấp → process_booking (để LLM hỏi lại)
    if confidence < threshold:
        return "process_booking"
    
    # 2. Intent booking + thiếu info → collect_info
    if intent in ["book_flight", "search_flights"]:
        if missing_fields:
            return "collect_info"
    
    # 3. Có đủ info hoặc inquiry đơn giản → process_booking
    return "process_booking"
```

**Routing Logic**:
- **Confidence < 0.6**: Chuyển sang `process_booking` để LLM hỏi lại
- **Booking intent + thiếu info**: Chuyển sang `collect_info`
- **Có đủ info hoặc inquiry đơn giản**: Chuyển sang `process_booking`

### **3. 📝 Collect Info Node (CẢI TIẾN)**

**Input**: Current booking info + User message  
**Output**: Updated booking info + Request for missing info OR Continue to process_booking

```python
def collect_booking_info(self, state: FlightBookingState) -> FlightBookingState:
    # 1. Extract info từ message hiện tại
    # 2. Merge với info đã có
    # 3. Check missing fields
    # 4. Nếu thiếu info → Trả về final_response và kết thúc
    # 5. Nếu đủ info → Tiếp tục đến process_booking
```

**NEW LOGIC**:
- **Thiếu thông tin**: Trả về `final_response` với câu hỏi và kết thúc luồng
- **Đủ thông tin**: Tiếp tục đến `process_booking`

### **4. 🚀 Process Booking Node**

**Input**: Intent + Booking info + User message  
**Output**: Final response + Tool results

```python
def process_booking(self, state: FlightBookingState) -> FlightBookingState:
    # 1. Tạo context-aware system prompt
    # 2. Bind tools với LLM
    # 3. Execute tool calls nếu có
    # 4. Combine response + tool results
```

**Tool Integration**:
- **search_flights**: Tìm chuyến bay
- **book_flight**: Đặt vé
- **get_weather**: Thông tin thời tiết
- **get_flight_status**: Trạng thái chuyến bay
- **get_booking_info**: Thông tin đặt vé
- **cancel_booking**: Hủy đặt vé

**Context-Aware Prompts**:
```python
system_prompts = {
    "book_flight": f"""You are a helpful flight booking assistant. The user wants to book a flight.
    
Current booking information:
- Departure: {departure_city}
- Destination: {arrival_city}
- Date: {date}
- Passenger: {passenger_name}
Use the available tools to help complete the booking.""",
    
    "search_flights": f"""You are a flight search assistant.
Search criteria:
- Departure: {departure_city}
- Destination: {arrival_city}
- Date: {date}
Use the search_flights tool to find flights."""
}
```

## 🔄 **Luồng xử lý chi tiết (CẢI TIẾN)**

### **Scenario 1: Đặt vé hoàn chỉnh**
```
User: "I want to book a flight from New York to London on March 15th"

1. Intent Classification:
   - Intent: book_flight
   - Confidence: 0.95

2. Route Based on Intent:
   - Intent: book_flight
   - Missing fields: [passenger_name, email]
   - Decision: collect_info

3. Collect Info:
   - Extract: departure_city="New York", arrival_city="London", date="March 15th"
   - Missing: passenger_name, email
   - Response: "I need a few more details: passenger name, email address. Could you provide this information?"
   - **KẾT THÚC LUỒNG** ← NEW!

4. User: "My name is John Smith, email is john@example.com"

5. Intent Classification (new turn):
   - Intent: provide_info
   - Confidence: 0.85

6. Route Based on Intent:
   - Intent: provide_info
   - Decision: collect_info

7. Collect Info:
   - Extract: passenger_name="John Smith", email="john@example.com"
   - All fields complete
   - Continue to process_booking

8. Process Booking:
   - Use search_flights tool
   - Show available flights
   - Help user book selected flight
```

### **Scenario 2: Tìm kiếm chuyến bay**
```
User: "Show me flights from Tokyo to Seoul"

1. Intent Classification:
   - Intent: search_flights
   - Confidence: 0.88

2. Route Based on Intent:
   - Intent: search_flights
   - Missing fields: [date]
   - Decision: collect_info

3. Collect Info:
   - Extract: departure_city="Tokyo", arrival_city="Seoul"
   - Missing: date
   - Response: "Could you please provide the travel date for your flight?"
   - **KẾT THÚC LUỒNG** ← NEW!

4. User: "On April 10th"

5. Intent Classification (new turn):
   - Intent: provide_info
   - Confidence: 0.90

6. Route Based on Intent:
   - Intent: provide_info
   - Decision: collect_info

7. Collect Info:
   - Extract: date="April 10th"
   - All fields complete
   - Continue to process_booking

8. Process Booking:
   - Use search_flights tool
   - Show flights Tokyo → Seoul on April 10th
```

### **Scenario 3: Câu hỏi đơn giản**
```
User: "What's the weather like in Paris?"

1. Intent Classification:
   - Intent: check_weather
   - Confidence: 0.92

2. Route Based on Intent:
   - Intent: check_weather
   - No missing fields needed
   - Decision: process_booking

3. Process Booking:
   - Use get_weather tool
   - Return weather information for Paris
```

## 🎯 **State Management (CẢI TIẾN)**

**FlightBookingState Structure**:
```python
class FlightBookingState(TypedDict):
    messages: Annotated[list[AnyMessage], add_messages]  # Conversation history
    intent: str                                          # Classified intent
    intent_confidence: float                             # Confidence score
    booking_info: dict                                   # Collected booking information
    conversation_history: list[dict]                     # Additional conversation data
    final_response: str                                  # Final agent response
    current_step: str                                    # Current processing step
```

**State Flow (CẢI TIẾN)**:
```
Initial State:
{
    "messages": [HumanMessage("I want to book a flight")],
    "intent": "",
    "intent_confidence": 0.0,
    "booking_info": {},
    "current_step": ""
}

After Intent Classification:
{
    "intent": "book_flight",
    "intent_confidence": 0.95,
    "messages": [..., AIMessage("Intent: book_flight (confidence: 0.95)")]
}

After Collect Info (Missing Info):
{
    "booking_info": {
        "departure_city": "New York",
        "arrival_city": "London",
        "date": "March 15th"
    },
    "current_step": "collecting_info",
    "final_response": "I need a few more details: passenger name, email address. Could you provide this information?"
}
← KẾT THÚC LUỒNG

After Collect Info (Complete Info):
{
    "booking_info": {
        "departure_city": "New York",
        "arrival_city": "London",
        "date": "March 15th",
        "passenger_name": "John Smith",
        "email": "john@example.com"
    },
    "current_step": "info_complete"
}
→ Tiếp tục đến Process Booking

After Process Booking:
{
    "final_response": "I found 3 flights from New York to London...",
    "current_step": "completed"
}
```

## 🔧 **Configuration & Settings**

**Intent Confidence Threshold**: 0.6 (có thể config trong .env)

**Required Fields Configuration**:
```python
required_fields = {
    "book_flight": ["departure_city", "arrival_city", "date", "passenger_name", "email"],
    "search_flights": ["departure_city", "arrival_city", "date"],
    "check_weather": ["city"],
    "flight_status": ["flight_number"]
}
```

**Field Names for User-Friendly Messages**:
```python
field_names = {
    "departure_city": "departure city",
    "arrival_city": "destination city", 
    "date": "travel date",
    "passenger_name": "passenger name",
    "email": "email address"
}
```

## 🎯 **Key Features (CẢI TIẾN)**

1. **Intelligent Intent Classification** với confidence scoring
2. **Context-Aware Information Extraction** từ user messages
3. **Dynamic Routing** dựa trên intent và state
4. **Tool Integration** với error handling
5. **Conversation Memory** qua message history
6. **Flexible Configuration** qua environment variables
7. **Natural Language Processing** cho user interaction
8. **Efficient Flow Control** - Kết thúc ngay khi thiếu thông tin
9. **Improved User Experience** - Không cần đi qua node không cần thiết 