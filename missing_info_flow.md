# 🚨 Luồng xử lý khi thiếu thông tin (CẢI TIẾN)

## 🔄 **Tổng quan luồng xử lý thiếu thông tin**

```
User Input
    ↓
Intent Classification
    ↓
Route Based on Intent
    ↓
┌─────────────────────────────────────┐
│ Check Missing Information           │
│                                     │
│ 1. Confidence < 0.6?               │
│    ↓ YES → Process Booking         │
│    ↓ NO                            │
│                                     │
│ 2. Intent = booking related?       │
│    ↓ YES → Check Required Fields   │
│    ↓ NO → Process Booking          │
│                                     │
│ 3. Missing Required Fields?        │
│    ↓ YES → Collect Info            │
│    ↓ NO → Process Booking          │
└─────────────────────────────────────┘
    ↓
┌─────────────────────────────────────┐
│ Collect Info Node                   │
│                                     │
│ 1. Extract info từ message         │
│ 2. Merge với info đã có            │
│ 3. Check missing fields            │
│                                     │
│ 4. Missing fields?                 │
│    ↓ YES → Return final_response   │
│    ↓      → KẾT THÚC LUỒNG        │
│    ↓ NO                            │
│                                     │
│ 5. All fields complete?            │
│    ↓ YES → Continue to Process     │
│    ↓      → Booking                │
└─────────────────────────────────────┘
```

## 📊 **Chi tiết từng bước xử lý (CẢI TIẾN)**

### **1. 🎯 Intent Classification & Confidence Check**

```python
def route_based_on_intent(self, state: FlightBookingState):
    intent = state.get("intent", "")
    confidence = state.get("intent_confidence", 0.5)
    
    # Bước 1: Kiểm tra confidence
    if confidence < settings.agent.intent_confidence_threshold and intent not in ["greeting", "general_inquiry"]:
        return "process_booking"  # Để LLM hỏi lại
```

**Logic**:
- **Confidence < 0.6**: Chuyển sang `process_booking` để LLM tự nhiên hỏi lại
- **Confidence >= 0.6**: Tiếp tục kiểm tra thông tin

**Ví dụ**:
```
User: "I want something"
Intent: book_flight (confidence: 0.3)
→ Confidence thấp → Process Booking → LLM hỏi: "What would you like to do? Book a flight, search flights, or something else?"
```

### **2. 🔍 Intent Type Check**

```python
# Bước 2: Kiểm tra loại intent
if intent in ["book_flight", "search_flights"]:
    # Intent cần thu thập thông tin
    booking_info = state.get("booking_info", {})
    required_fields = settings.booking.required_fields.get(intent, [])
    
    missing_fields = [field for field in required_fields if not booking_info.get(field)]
    
    if missing_fields and current_step != "info_complete":
        return "collect_info"
```

**Required Fields by Intent**:
```python
required_fields = {
    "book_flight": ["departure_city", "arrival_city", "date", "passenger_name", "email"],
    "search_flights": ["departure_city", "arrival_city", "date"],
    "check_weather": ["city"],
    "flight_status": ["flight_number"]
}
```

### **3. 📝 Collect Info Node - Xử lý thiếu thông tin (CẢI TIẾN)**

```python
def collect_booking_info(self, state: FlightBookingState) -> FlightBookingState:
    current_info = state.get("booking_info", {})
    last_message = state["messages"][-1].content
    
    # Bước 1: Extract info từ message hiện tại
    if last_message and not last_message.startswith("Intent:"):
        extraction_chain = extraction_prompt | self.llm | self.booking_parser
        extracted_info = extraction_chain.invoke({})
        
        # Merge với thông tin đã có
        for key, value in extracted_info.dict().items():
            if value is not None:
                current_info[key] = value
    
    # Bước 2: Check missing fields
    intent = state.get("intent", "")
    required_fields = settings.booking.required_fields.get(intent, [])
    missing_fields = [field for field in required_fields if not current_info.get(field)]
    
    # Bước 3: NEW LOGIC - Kết thúc ngay khi thiếu thông tin
    if missing_fields:
        field_names = settings.booking.field_names
        
        if len(missing_fields) == 1:
            prompt = f"Could you please provide the {field_names[missing_fields[0]]} for your flight?"
        else:
            missing_list = ", ".join([field_names[field] for field in missing_fields])
            prompt = f"I need a few more details to help you: {missing_list}. Could you provide this information?"
        
        # KẾT THÚC LUỒNG NGAY LẬP TỨC
        return {
            "booking_info": current_info,
            "current_step": "collecting_info",
            "final_response": prompt,  # ← Trả về final_response
            "messages": [AIMessage(content=prompt)]
        }
    else:
        # Tất cả thông tin đã đủ - tiếp tục đến process_booking
        return {
            "booking_info": current_info,
            "current_step": "info_complete",
            "messages": [AIMessage(content="Perfect! I have all the information I need to help you.")]
        }
```

### **4. 🧭 Route After Collect Info (NEW)**

```python
def route_after_collect_info(self, state: FlightBookingState) -> Literal["process_booking", "end"]:
    current_step = state.get("current_step", "")
    
    # Nếu đang thu thập info → kết thúc luồng
    if current_step == "collecting_info":
        return "end"
    
    # Nếu info đã đủ → tiếp tục đến process_booking
    if current_step == "info_complete":
        return "process_booking"
    
    return "process_booking"
```

## 🔄 **Các scenario thiếu thông tin (CẢI TIẾN)**

### **Scenario 1: Thiếu một số thông tin cơ bản**

```
User: "I want to book a flight from New York to London"

1. Intent Classification:
   - Intent: book_flight
   - Confidence: 0.95

2. Route Based on Intent:
   - Required fields: ["departure_city", "arrival_city", "date", "passenger_name", "email"]
   - Current info: {"departure_city": "New York", "arrival_city": "London"}
   - Missing fields: ["date", "passenger_name", "email"]
   - Decision: collect_info

3. Collect Info:
   - Extract: departure_city="New York", arrival_city="London"
   - Missing: date, passenger_name, email
   - Response: "I need a few more details: travel date, passenger name, email address. Could you provide this information?"
   - **KẾT THÚC LUỒNG NGAY LẬP TỨC** ← NEW!

4. User: "On March 15th, my name is John Smith, email is john@example.com"

5. Intent Classification (new turn):
   - Intent: provide_info
   - Confidence: 0.85

6. Route Based on Intent:
   - Intent: provide_info
   - Decision: collect_info

7. Collect Info:
   - Extract: date="March 15th", passenger_name="John Smith", email="john@example.com"
   - All fields complete
   - Continue to process_booking

8. Process Booking:
   - Use search_flights tool
   - Show available flights
```

### **Scenario 2: Thiếu thông tin từng bước**

```
User: "I want to search for flights"

1. Intent Classification:
   - Intent: search_flights
   - Confidence: 0.88

2. Route Based on Intent:
   - Required fields: ["departure_city", "arrival_city", "date"]
   - Current info: {}
   - Missing fields: ["departure_city", "arrival_city", "date"]
   - Decision: collect_info

3. Collect Info:
   - Missing: departure_city, arrival_city, date
   - Response: "I need a few more details: departure city, destination city, travel date. Could you provide this information?"
   - **KẾT THÚC LUỒNG NGAY LẬP TỨC** ← NEW!

4. User: "From Tokyo to Seoul"

5. Intent Classification (new turn):
   - Intent: provide_info
   - Confidence: 0.90

6. Route Based on Intent:
   - Intent: provide_info
   - Decision: collect_info

7. Collect Info:
   - Extract: departure_city="Tokyo", arrival_city="Seoul"
   - Missing: date
   - Response: "Could you please provide the travel date for your flight?"
   - **KẾT THÚC LUỒNG NGAY LẬP TỨC** ← NEW!

8. User: "On April 10th"

9. Intent Classification (new turn):
   - Intent: provide_info
   - Confidence: 0.92

10. Route Based on Intent:
    - Intent: provide_info
    - Decision: collect_info

11. Collect Info:
    - Extract: date="April 10th"
    - All fields complete
    - Continue to process_booking

12. Process Booking:
    - Use search_flights tool
    - Show flights Tokyo → Seoul on April 10th
```

### **Scenario 3: Confidence thấp**

```
User: "I want something about flights"

1. Intent Classification:
   - Intent: book_flight (confidence: 0.45)
   - Reasoning: Unclear intent

2. Route Based on Intent:
   - Confidence: 0.45 < 0.6 (threshold)
   - Decision: process_booking

3. Process Booking:
   - LLM tự nhiên hỏi: "I'd be happy to help you with flights! What would you like to do? 
     - Book a flight
     - Search for available flights  
     - Check flight status
     - Get weather information
     - Or something else?"
```

### **Scenario 4: Intent đơn giản không cần thông tin**

```
User: "What's the weather like in Paris?"

1. Intent Classification:
   - Intent: check_weather
   - Confidence: 0.92

2. Route Based on Intent:
   - Required fields: ["city"]
   - Current info: {"city": "Paris"} (extracted từ message)
   - Missing fields: []
   - Decision: process_booking

3. Process Booking:
   - Use get_weather tool
   - Return weather information for Paris
```

## 🎯 **Field Names Mapping**

```python
field_names = {
    "departure_city": "departure city",
    "arrival_city": "destination city", 
    "date": "travel date",
    "passenger_name": "passenger name",
    "email": "email address",
    "passengers": "number of passengers",
    "class_type": "class type (economy, business, or first)",
    "city": "city name",
    "flight_number": "flight number"
}
```

## 🔧 **Configuration Settings**

```python
# Intent confidence threshold
INTENT_CONFIDENCE_THRESHOLD=0.6

# Required fields for each intent
required_fields = {
    "book_flight": ["departure_city", "arrival_city", "date", "passenger_name", "email"],
    "search_flights": ["departure_city", "arrival_city", "date"],
    "check_weather": ["city"],
    "flight_status": ["flight_number"]
}
```

## 🚀 **Key Features của luồng xử lý thiếu thông tin (CẢI TIẾN)**

### **1. Intelligent Information Extraction**
- Tự động extract thông tin từ user message
- Merge với thông tin đã có
- Không mất thông tin đã thu thập

### **2. Natural Language Requests**
- Tạo câu hỏi tự nhiên cho missing fields
- Sử dụng field names thân thiện với user
- Hỏi một hoặc nhiều fields cùng lúc

### **3. Context-Aware Processing**
- Dựa trên intent để xác định required fields
- Không hỏi thông tin không cần thiết
- Giữ context qua conversation

### **4. Flexible Routing**
- Confidence thấp → LLM tự nhiên hỏi lại
- Intent đơn giản → Xử lý trực tiếp
- Intent phức tạp → Thu thập thông tin từng bước

### **5. Error Handling**
- Fallback khi extraction fails
- Graceful handling của missing fields
- Clear error messages

### **6. Efficient Flow Control (NEW)**
- **Kết thúc luồng ngay khi thiếu thông tin**
- **Không đi qua node không cần thiết**
- **Improved performance và user experience**

## 📈 **State Flow khi thiếu thông tin (CẢI TIẾN)**

```
Initial State:
{
    "messages": [HumanMessage("I want to book a flight")],
    "intent": "",
    "booking_info": {},
    "current_step": ""
}

After Intent Classification:
{
    "intent": "book_flight",
    "intent_confidence": 0.95,
    "current_step": ""
}

After Route Check:
{
    "intent": "book_flight",
    "missing_fields": ["departure_city", "arrival_city", "date", "passenger_name", "email"],
    "current_step": "collecting_info"
}

After Collect Info (Missing Info):
{
    "booking_info": {
        "departure_city": "New York",
        "arrival_city": "London"
    },
    "missing_fields": ["date", "passenger_name", "email"],
    "current_step": "collecting_info",
    "final_response": "I need a few more details: travel date, passenger name, email address. Could you provide this information?"
}
← KẾT THÚC LUỒNG NGAY LẬP TỨC

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
```

## 🎯 **Lợi ích của cải tiến**

### **1. Hiệu quả hơn**
- Không đi qua `process_booking` node khi không cần thiết
- Giảm thời gian xử lý
- Tiết kiệm token usage

### **2. User Experience tốt hơn**
- Response nhanh hơn khi thiếu thông tin
- Không có delay không cần thiết
- Flow tự nhiên hơn

### **3. Logic rõ ràng hơn**
- `collect_info` node có trách nhiệm rõ ràng
- Separation of concerns tốt hơn
- Dễ debug và maintain

### **4. Scalability**
- Dễ thêm logic mới vào từng node
- Không ảnh hưởng đến node khác
- Modular design

Luồng xử lý cải tiến này đảm bảo agent hoạt động hiệu quả và tự nhiên hơn, giống như một agent thực sự! 