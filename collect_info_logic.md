# 📝 Collect Info Node - Logic Chi Tiết (CẢI TIẾN)

## 🎯 **Tổng quan Node Collect Info**

Node `collect_booking_info` có nhiệm vụ **thông minh thu thập thông tin đặt vé** từ user và quyết định có tiếp tục luồng hay kết thúc ngay.

## 🔄 **Flow Logic của Collect Info Node (CẢI TIẾN)**

```
Input: FlightBookingState
    ↓
┌─────────────────────────────────────┐
│ 1. Extract Information              │ ← Tự động extract thông tin từ 
│    from Multiple Messages           │   conversation history (up to 10 messages)
└─────────────────────────────────────┘
    ↓
┌─────────────────────────────────────┐
│ 2. Merge with Existing Info         │ ← Kết hợp với thông tin đã có
└─────────────────────────────────────┘
    ↓
┌─────────────────────────────────────┐
│ 3. Check Missing Fields             │ ← Kiểm tra thông tin còn thiếu
└─────────────────────────────────────┘
    ↓
┌─────────────────────────────────────┐
│ 4. Decision Point                   │
│                                     │
│ Missing Fields?                     │
│    ↓ YES → Generate Request         │
│    ↓      → Return final_response   │
│    ↓      → KẾT THÚC LUỒNG         │
│    ↓ NO                             │
│    ↓ YES → Continue to Process      │
│    ↓      → Booking                 │
└─────────────────────────────────────┘
```

## 📊 **Chi tiết từng bước (CẢI TIẾN)**

### **Bước 1: Extract Information from Multiple Messages**

```python
def collect_booking_info(self, state: FlightBookingState) -> FlightBookingState:
    current_info = state.get("booking_info", {})
    messages = state.get("messages", [])
    
    # Extract information from multiple messages (up to 10, or all if less than 10)
    if messages:
        # Get recent messages (up to 10, excluding intent messages)
        recent_messages = []
        for msg in messages[-10:]:  # Lấy 10 tin nhắn gần nhất
            if hasattr(msg, 'content') and not msg.content.startswith("Intent:"):
                recent_messages.append(msg.content)
        
        if recent_messages:
            # Combine all recent messages for extraction
            combined_text = " ".join(recent_messages)
            
            extraction_prompt = ChatPromptTemplate.from_messages([
                ("system", """Extract booking information from the user's conversation history. 
                Look for departure city, arrival city, date, passenger name, email, number of passengers, and class type.
                Consider information from all messages in the conversation.
                Return a JSON object with the extracted information."""),
                ("user", f"Extract booking info from conversation: {combined_text}")
            ])
            
            extraction_chain = extraction_prompt | self.llm | self.booking_parser
            
            try:
                extracted_info = extraction_chain.invoke({})
                # Merge extracted info with existing info
                for key, value in extracted_info.dict().items():
                    if value is not None:
                        current_info[key] = value
            except Exception:
                pass  # Continue with existing info if extraction fails
```

**Logic (CẢI TIẾN)**:
- Lấy **tối đa 10 tin nhắn gần nhất** từ conversation history
- Loại bỏ các message "Intent:" (internal messages)
- Kết hợp tất cả tin nhắn thành một text duy nhất
- Sử dụng LLM để extract thông tin từ toàn bộ conversation
- Parse kết quả thành JSON object
- Merge với thông tin đã có

**Ví dụ (CẢI TIẾN)**:
```
Messages: [
    "I want to book a flight",
    "From New York to London", 
    "On March 15th",
    "My name is John Smith",
    "Email is john@example.com"
]

Combined: "I want to book a flight From New York to London On March 15th My name is John Smith Email is john@example.com"

Extracted: {
    "departure_city": "New York",
    "arrival_city": "London", 
    "date": "March 15th",
    "passenger_name": "John Smith",
    "email": "john@example.com"
}
```

### **Bước 2: Merge with Existing Info**

```python
# Merge extracted info with existing info
for key, value in extracted_info.dict().items():
    if value is not None:
        current_info[key] = value
```

**Logic**:
- Chỉ update những field có giá trị (không phải None)
- Giữ nguyên thông tin đã có nếu không được update
- Không ghi đè thông tin đã có

**Ví dụ**:
```
Existing: {"departure_city": "New York", "arrival_city": "London"}
New: {"date": "March 15th", "passenger_name": "John Smith"}
Result: {"departure_city": "New York", "arrival_city": "London", "date": "March 15th", "passenger_name": "John Smith"}
```

### **Bước 3: Check Missing Fields**

```python
# Define required fields based on intent
intent = state.get("intent", "")
required_fields = settings.booking.required_fields.get(intent, [])

missing_fields = [field for field in required_fields if not current_info.get(field)]
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

**Logic**:
- Lấy required fields dựa trên intent hiện tại
- So sánh với thông tin đã có
- Tạo list các field còn thiếu

**Ví dụ**:
```
Intent: "book_flight"
Required: ["departure_city", "arrival_city", "date", "passenger_name", "email"]
Current: {"departure_city": "New York", "arrival_city": "London", "date": "March 15th", "passenger_name": "John Smith", "email": "john@example.com"}
Missing: []
```

### **Bước 4: Decision Point - Missing Fields?**

#### **Trường hợp 1: Có Missing Fields**

```python
if missing_fields:
    # Generate a natural request for the FIRST missing field only
    field_names = settings.booking.field_names
    first_missing_field = missing_fields[0]  # Chỉ lấy field đầu tiên
    
    prompt = f"Could you please provide the {field_names[first_missing_field]} for your flight?"
    
    # Return final response immediately when missing information
    return {
        "booking_info": current_info,
        "current_step": "collecting_info",
        "final_response": prompt,
        "messages": [AIMessage(content=prompt)]
    }
```

**Logic (CẢI TIẾN)**:
- **Chỉ hỏi 1 thông tin một lần** - lấy field đầu tiên trong danh sách missing fields
- Tạo câu hỏi tự nhiên cho field đó
- Sử dụng field names thân thiện với user
- **KẾT THÚC LUỒNG NGAY LẬP TỨC** với `final_response`

**Field Names Mapping**:
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

**Ví dụ (CẢI TIẾN)**:
```
Missing: ["passenger_name", "email"]
→ Chỉ hỏi: "Could you please provide the passenger name for your flight?"

Missing: ["date", "passenger_name", "email"]
→ Chỉ hỏi: "Could you please provide the travel date for your flight?"
```

#### **Trường hợp 2: Không có Missing Fields**

```python
else:
    # All information collected - continue to process_booking
    return {
        "booking_info": current_info,
        "current_step": "info_complete",
        "messages": [AIMessage(content="Perfect! I have all the information I need to help you.")]
    }
```

**Logic**:
- Tất cả thông tin đã đủ
- Set `current_step` = "info_complete"
- Tiếp tục đến `process_booking` node

## 🔄 **Các Scenario Cụ Thể (CẢI TIẾN)**

### **Scenario 1: Thu thập thông tin từ nhiều tin nhắn**

```
Input State:
{
    "intent": "book_flight",
    "booking_info": {},
    "messages": [
        HumanMessage("I want to book a flight"),
        HumanMessage("From New York to London"),
        HumanMessage("On March 15th"),
        HumanMessage("My name is John Smith"),
        HumanMessage("Email is john@example.com")
    ]
}

Step 1 - Extract from Multiple Messages:
- Combined: "I want to book a flight From New York to London On March 15th My name is John Smith Email is john@example.com"
- Extracted: {
    "departure_city": "New York",
    "arrival_city": "London",
    "date": "March 15th", 
    "passenger_name": "John Smith",
    "email": "john@example.com"
  }

Step 2 - Check Missing:
- Required: ["departure_city", "arrival_city", "date", "passenger_name", "email"]
- Missing: []

Step 3 - Decision:
- No missing fields → Continue to process_booking
- Return: current_step = "info_complete"
```

### **Scenario 2: Thu thập từng bước qua nhiều tin nhắn**

```
Input State:
{
    "intent": "search_flights",
    "booking_info": {"departure_city": "Tokyo"},
    "messages": [
        HumanMessage("I want to search for flights"),
        HumanMessage("From Tokyo"),
        HumanMessage("To Seoul"),
        HumanMessage("On April 10th")
    ]
}

Step 1 - Extract from Multiple Messages:
- Combined: "I want to search for flights From Tokyo To Seoul On April 10th"
- Extracted: {
    "departure_city": "Tokyo",
    "arrival_city": "Seoul",
    "date": "April 10th"
  }

Step 2 - Check Missing:
- Required: ["departure_city", "arrival_city", "date"]
- Missing: []

Step 3 - Decision:
- No missing fields → Continue to process_booking
- Return: current_step = "info_complete"
```

### **Scenario 3: Hỏi từng thông tin một (CẢI TIẾN)**

```
Input State:
{
    "intent": "book_flight",
    "booking_info": {},
    "messages": [
        HumanMessage("I want to book a flight"),
        HumanMessage("From Paris to Rome"),
        HumanMessage("On May 20th")
    ]
}

Step 1 - Extract from Multiple Messages:
- Combined: "I want to book a flight From Paris to Rome On May 20th"
- Extracted: {
    "departure_city": "Paris",
    "arrival_city": "Rome",
    "date": "May 20th"
  }

Step 2 - Check Missing:
- Required: ["departure_city", "arrival_city", "date", "passenger_name", "email"]
- Missing: ["passenger_name", "email"]

Step 3 - Decision:
- Missing fields → Hỏi field đầu tiên
- Prompt: "Could you please provide the passenger name for your flight?"
- Return: final_response + KẾT THÚC LUỒNG

User: "My name is John Smith"

Step 1 - Extract from Multiple Messages:
- Combined: "My name is John Smith"
- Extracted: {"passenger_name": "John Smith"}

Step 2 - Check Missing:
- Required: ["departure_city", "arrival_city", "date", "passenger_name", "email"]
- Missing: ["email"]

Step 3 - Decision:
- Missing fields → Hỏi field đầu tiên
- Prompt: "Could you please provide the email address for your flight?"
- Return: final_response + KẾT THÚC LUỒNG

User: "john@example.com"

Step 1 - Extract from Multiple Messages:
- Combined: "john@example.com"
- Extracted: {"email": "john@example.com"}

Step 2 - Check Missing:
- Required: ["departure_city", "arrival_city", "date", "passenger_name", "email"]
- Missing: []

Step 3 - Decision:
- No missing fields → Continue to process_booking
- Return: current_step = "info_complete"
```

## 🎯 **Key Features của Collect Info Node (CẢI TIẾN)**

### **1. Intelligent Information Extraction from Multiple Messages**
- Extract thông tin từ **tối đa 10 tin nhắn gần nhất**
- Kết hợp tất cả tin nhắn thành một context duy nhất
- Sử dụng LLM để hiểu context toàn bộ conversation
- Parse thành structured data

### **2. Context Preservation**
- Merge với thông tin đã có
- Không mất thông tin đã thu thập
- Maintain conversation context qua nhiều tin nhắn

### **3. Dynamic Field Requirements**
- Required fields dựa trên intent
- Flexible configuration
- Support multiple intent types

### **4. Natural Language Generation**
- Tạo câu hỏi tự nhiên
- Sử dụng user-friendly field names
- Support single và multiple field requests

### **5. Efficient Flow Control**
- Kết thúc luồng ngay khi thiếu thông tin
- Không đi qua node không cần thiết
- Clear decision points

### **6. Error Handling**
- Graceful handling khi extraction fails
- Fallback to existing information
- Continue processing even with errors

### **7. Conversation History Awareness (NEW)**
- Hiểu context từ toàn bộ conversation
- Không chỉ dựa vào tin nhắn cuối cùng
- Có thể extract thông tin từ nhiều tin nhắn khác nhau

## 📈 **State Transitions (CẢI TIẾN)**

### **Input State:**
```python
{
    "intent": "book_flight",
    "booking_info": {"departure_city": "New York"},
    "messages": [
        HumanMessage("I want to book a flight"),
        HumanMessage("From New York"),
        HumanMessage("To London on March 15th"),
        HumanMessage("My name is John Smith")
    ]
}
```

### **Output State (Missing Info):**
```python
{
    "intent": "book_flight",
    "booking_info": {
        "departure_city": "New York",
        "arrival_city": "London",
        "date": "March 15th",
        "passenger_name": "John Smith"
    },
    "current_step": "collecting_info",
    "final_response": "Could you please provide the email address for your flight?",
    "messages": [AIMessage(content="Could you please provide the email address for your flight?")]
}
```

### **Output State (Complete Info):**
```python
{
    "intent": "book_flight",
    "booking_info": {
        "departure_city": "New York",
        "arrival_city": "London",
        "date": "March 15th",
        "passenger_name": "John Smith",
        "email": "john@example.com"
    },
    "current_step": "info_complete",
    "messages": [AIMessage(content="Perfect! I have all the information I need to help you.")]
}
```

## 🚀 **Lợi ích của cải tiến**

### **1. Better Information Extraction**
- Không bỏ sót thông tin từ conversation history
- Có thể extract từ nhiều tin nhắn khác nhau
- Hiểu context toàn bộ conversation

### **2. Improved User Experience**
- Không cần user nhắc lại thông tin đã cung cấp
- Thu thập thông tin tự nhiên hơn
- **Hỏi từng thông tin một** - không overwhelm user với nhiều câu hỏi cùng lúc
- **Conversation flow tự nhiên hơn** - giống như chat với người thật

### **3. More Robust Processing**
- Xử lý được các trường hợp user cung cấp thông tin từng bước
- Không bị mất context giữa các tin nhắn
- Tăng độ chính xác của information extraction
- **Step-by-step approach** - dễ theo dõi và debug

### **4. Better Conversation Flow**
- **Không overwhelm user** với danh sách dài các thông tin cần cung cấp
- **Tập trung vào một thông tin** mỗi lần
- **Dễ trả lời** - user chỉ cần cung cấp một thông tin
- **Tự nhiên hơn** - giống như conversation thực tế 