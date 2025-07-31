# 🎫 Updated Graph Structure - Flight Booking Agent

## 🔄 **Graph Structure (CẢI TIẾN)**

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

## 📊 **Chi tiết Graph Structure**

### **Nodes:**
1. **START** - Entry point
2. **classify_intent** - Phân loại intent
3. **route_based_on_intent** - Routing logic đầu tiên
4. **collect_info** - Thu thập thông tin (có thể kết thúc luồng)
5. **route_after_collect_info** - Routing logic sau collect_info
6. **process_booking** - Xử lý chính với tools
7. **END** - Exit point

### **Edges:**

```python
# 1. START → classify_intent
workflow.add_edge(START, "classify_intent")

# 2. classify_intent → route_based_on_intent
workflow.add_conditional_edges(
    "classify_intent",
    self.route_based_on_intent,
    {
        "collect_info": "collect_info",
        "process_booking": "process_booking"
    }
)

# 3. collect_info → route_after_collect_info
workflow.add_conditional_edges(
    "collect_info",
    self.route_after_collect_info,
    {
        "process_booking": "process_booking",
        "end": END
    }
)

# 4. process_booking → END
workflow.add_edge("process_booking", END)
```

## 🔄 **Luồng xử lý chi tiết**

### **Flow 1: Thiếu thông tin**
```
START
  ↓
classify_intent (intent: book_flight, confidence: 0.95)
  ↓
route_based_on_intent → "collect_info" (missing fields)
  ↓
collect_info (missing: date, passenger_name, email)
  ↓
route_after_collect_info → "end" (current_step: "collecting_info")
  ↓
END
```

### **Flow 2: Đủ thông tin**
```
START
  ↓
classify_intent (intent: book_flight, confidence: 0.95)
  ↓
route_based_on_intent → "collect_info" (missing fields)
  ↓
collect_info (all fields complete)
  ↓
route_after_collect_info → "process_booking" (current_step: "info_complete")
  ↓
process_booking (use tools)
  ↓
END
```

### **Flow 3: Intent đơn giản**
```
START
  ↓
classify_intent (intent: check_weather, confidence: 0.92)
  ↓
route_based_on_intent → "process_booking" (no missing fields)
  ↓
process_booking (use get_weather tool)
  ↓
END
```

### **Flow 4: Confidence thấp**
```
START
  ↓
classify_intent (intent: book_flight, confidence: 0.45)
  ↓
route_based_on_intent → "process_booking" (confidence < 0.6)
  ↓
process_booking (LLM hỏi lại)
  ↓
END
```

## 🎯 **Routing Logic**

### **route_based_on_intent:**
```python
def route_based_on_intent(self, state) -> "collect_info" | "process_booking":
    intent = state.get("intent", "")
    confidence = state.get("intent_confidence", 0.5)
    
    # 1. Confidence thấp → process_booking
    if confidence < 0.6 and intent not in ["greeting", "general_inquiry"]:
        return "process_booking"
    
    # 2. Intent booking + thiếu info → collect_info
    if intent in ["book_flight", "search_flights"]:
        missing_fields = [field for field in required_fields if not booking_info.get(field)]
        if missing_fields and current_step != "info_complete":
            return "collect_info"
    
    # 3. Có đủ info hoặc inquiry đơn giản → process_booking
    return "process_booking"
```

### **route_after_collect_info:**
```python
def route_after_collect_info(self, state) -> "process_booking" | "end":
    current_step = state.get("current_step", "")
    
    # 1. Đang thu thập info → kết thúc luồng
    if current_step == "collecting_info":
        return "end"
    
    # 2. Info đã đủ → tiếp tục đến process_booking
    if current_step == "info_complete":
        return "process_booking"
    
    # 3. Default → process_booking
    return "process_booking"
```

## 📈 **State Transitions**

### **State trong classify_intent:**
```python
{
    "intent": "book_flight",
    "intent_confidence": 0.95,
    "booking_info": {},
    "current_step": ""
}
```

### **State trong collect_info (thiếu info):**
```python
{
    "intent": "book_flight",
    "intent_confidence": 0.95,
    "booking_info": {
        "departure_city": "New York",
        "arrival_city": "London"
    },
    "current_step": "collecting_info",
    "final_response": "I need a few more details: travel date, passenger name, email address..."
}
```

### **State trong collect_info (đủ info):**
```python
{
    "intent": "book_flight",
    "intent_confidence": 0.95,
    "booking_info": {
        "departure_city": "New York",
        "arrival_city": "London",
        "date": "March 15th",
        "passenger_name": "John Smith",
        "email": "john@example.com"
    },
    "current_step": "info_complete"
}
```

### **State trong process_booking:**
```python
{
    "intent": "book_flight",
    "intent_confidence": 0.95,
    "booking_info": {...},
    "final_response": "I found 3 flights from New York to London...",
    "current_step": "completed"
}
```

## 🚀 **Lợi ích của Graph Structure mới**

### **1. Efficient Flow Control**
- `collect_info` có thể kết thúc luồng ngay khi thiếu thông tin
- Không đi qua `process_booking` node không cần thiết
- Giảm thời gian xử lý và token usage

### **2. Clear Separation of Concerns**
- Mỗi node có trách nhiệm rõ ràng
- Routing logic tách biệt
- Dễ debug và maintain

### **3. Flexible Routing**
- Conditional edges cho phép routing linh hoạt
- Dựa trên state để quyết định next step
- Support multiple flow paths

### **4. Improved User Experience**
- Response nhanh hơn khi thiếu thông tin
- Flow tự nhiên và intuitive
- Không có delay không cần thiết

## 🔧 **Configuration**

Graph structure này được config qua:

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

Graph structure này đảm bảo agent hoạt động hiệu quả và tự nhiên, với khả năng kết thúc luồng ngay khi cần thiết! 🎯 