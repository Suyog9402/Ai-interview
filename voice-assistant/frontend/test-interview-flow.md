# Interview Flow Test Guide

## 🧪 Testing the Complete Interview Flow

### **Step 1: Start Interview**

1. Navigate to `/interview`
2. Click "Start Call" button
3. Allow microphone access
4. Wait for AI interviewer to begin

### **Step 2: Complete Interview**

1. Answer the AI's questions (usually 3 questions)
2. Wait for the AI to say "Thank you" or "Have a great day"
3. **OR** Click the "End Call" button manually

### **Step 3: Verify Processing**

- ✅ **Loading Overlay**: Should show "Processing Interview" with spinner
- ✅ **Data Processing**: Interview data should be sent to backend
- ✅ **Navigation**: Should automatically redirect to `/result`

### **Step 4: Check Results**

- ✅ **Score Display**: Shows total score out of 100
- ✅ **Detailed Analysis**: Overall analysis of performance
- ✅ **Question Feedback**: Individual scores and feedback for each question
- ✅ **Recommendations**: Actionable improvement suggestions

## 🔧 Expected Behavior

### **When "End Call" is clicked:**

1. **Immediate Response**: Loading overlay appears instantly
2. **Data Processing**: All conversation data is captured and sent to backend
3. **AI Evaluation**: Backend processes the interview using Azure OpenAI
4. **Result Storage**: Results are stored in localStorage and database
5. **Navigation**: Redirects to `/result` page with comprehensive analysis

### **When Interview Ends Automatically:**

1. **Detection**: AI detects ending phrases ("thank you", "have a great day")
2. **Processing**: Same flow as manual end call
3. **Delay**: 1.2 second delay for better UX before redirect

## 🐛 Troubleshooting

### **If results don't appear:**

1. Check browser console for errors
2. Verify backend is running on port 8000
3. Check if Azure OpenAI is configured
4. Look for localStorage `interviewResult` data

### **If processing fails:**

1. Check network connectivity
2. Verify API endpoints are accessible
3. Check backend logs for errors
4. Ensure user is authenticated

## 📊 Expected API Calls

### **POST /api/v1/interview/evaluate**

```json
{
  "session_id": "session_1234567890_abc123",
  "conversation": [
    {
      "role": "assistant",
      "content": "Hello! I'm your AI interviewer...",
      "timestamp": "..."
    },
    {
      "role": "user",
      "content": "Tokenization is the process...",
      "timestamp": "..."
    }
  ],
  "questions": [
    "What does tokenization entail...",
    "How does attention work...",
    "What is zero-shot learning?"
  ],
  "answers": [
    "Tokenization is the process...",
    "The attention mechanism...",
    "Zero-shot learning is..."
  ]
}
```

### **Response:**

```json
{
  "session_id": "session_1234567890_abc123",
  "user_id": 1,
  "total_score": 85,
  "max_score": 100,
  "percentage": 85.0,
  "questions_evaluated": 3,
  "overall_analysis": "Strong technical understanding...",
  "detailed_feedback": [...],
  "strengths": ["Good technical knowledge", "Clear communication"],
  "areas_for_improvement": ["Could provide more examples"],
  "recommendations": ["Practice with more complex scenarios"]
}
```

## ✅ Success Criteria

- [ ] Interview starts successfully
- [ ] Conversation is captured in real-time
- [ ] End call button shows loading state
- [ ] Data is sent to backend for evaluation
- [ ] Results page displays comprehensive analysis
- [ ] Scores and feedback are accurate
- [ ] Navigation works smoothly
- [ ] Results are stored for history
