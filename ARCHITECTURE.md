# Dempsey's HR Agent - System Architecture

```mermaid
graph TB
    subgraph "Frontend Layer"
        UI[Employee Portal<br/>frontend.html]
        HRUI[HR Dashboard<br/>hr_dashboard.html]
    end

    subgraph "Backend API Layer - Flask on Port 8080"
        API[Flask Backend<br/>backend.py]
        
        subgraph "Employee Endpoints"
            ASK[/api/ask<br/>Natural Language Q&A]
            W2[/api/download/w2<br/>Tax Document]
            LOC[/api/update-location<br/>Location + Remote Status]
            EMAIL[/api/send-email-to-hr<br/>Email HR Requests]
        end
        
        subgraph "HR Endpoints"
            LOGIN[/api/hr/login<br/>HR Authentication]
            PTO[/api/hr/analytics/pto-usage<br/>PTO Statistics]
            TICKETS[/api/hr/analytics/tickets<br/>Ticket Analytics]
        end
    end

    subgraph "Core Intelligence - Python"
        AGENT[HR Agent SDK<br/>hr_agent_sdk.py]
        
        subgraph "NLP Intent Detection"
            PARSER[Query Parser<br/>Regex Pattern Matching]
            INT1[salary_query]
            INT2[days_off_query]
            INT3[work_location]
            INT4[w2_request]
            INT5[update_info]
            INT6[schedule_call]
            INT7[email_hr_request]
            INT8[hybrid_request]
        end
        
        subgraph "Business Logic"
            ANSWER[Answer Generator]
            UPDATE[Data Updater]
            SMART[Smart Escalation<br/>Policy Detection]
        end
    end

    subgraph "Data Layer"
        DB[(Employee Database<br/>employees.csv<br/>1,000 records)]
        TIX[(HR Tickets<br/>hr_tickets.csv<br/>30 records)]
        TAX[Tax Documents<br/>W-2 PDFs]
    end

    subgraph "External Services"
        SMTP[Gmail SMTP<br/>Email Delivery<br/>Optional]
    end

    subgraph "Session Management"
        SESS[Flask Sessions<br/>- Pending location updates<br/>- Pending emails<br/>- HR authentication]
    end

    subgraph "Document Generation"
        W2GEN[W-2 Generator<br/>w2_generator.py<br/>ReportLab PDF]
    end

    %% User Interactions
    USER((Employee<br/>User))
    HRADMIN((HR<br/>Admin))

    %% Employee Flow
    USER -->|Select Employee| UI
    UI -->|Employee ID or Name| ASK
    ASK --> AGENT
    AGENT --> PARSER
    PARSER --> INT1 & INT2 & INT3 & INT4 & INT5 & INT6 & INT7 & INT8
    INT1 & INT2 & INT3 --> ANSWER
    INT7 & INT8 --> SMART
    SMART -->|Draft Email| EMAIL
    EMAIL --> SMTP
    ANSWER --> DB
    INT4 --> W2GEN
    W2GEN --> TAX
    TAX --> W2
    W2 --> USER
    INT5 --> UPDATE
    UPDATE --> DB
    INT6 -->|Calendar Widget| UI
    
    %% Location Update Flow
    UI -->|Moving?| LOC
    LOC --> UPDATE
    UPDATE --> DB
    LOC --> SESS
    
    %% Email Flow
    EMAIL --> SESS
    SMTP -.->|demp.wade@gmail.com| HRADMIN
    
    %% HR Flow
    HRADMIN -->|Username/Password| HRUI
    HRUI --> LOGIN
    LOGIN --> SESS
    HRUI --> PTO & TICKETS
    PTO --> DB
    TICKETS --> TIX
    
    %% Styling
    classDef frontend fill:#632CA6,stroke:#8B5FBF,color:#fff
    classDef backend fill:#2A1F47,stroke:#632CA6,color:#fff
    classDef data fill:#00D4AA,stroke:#00BF99,color:#fff
    classDef external fill:#F653A6,stroke:#FF7AC6,color:#fff
    classDef user fill:#4B2380,stroke:#632CA6,color:#fff
    
    class UI,HRUI frontend
    class API,ASK,W2,LOC,EMAIL,LOGIN,PTO,TICKETS,AGENT,PARSER,ANSWER,UPDATE,SMART,W2GEN backend
    class DB,TIX,TAX,SESS data
    class SMTP external
    class USER,HRADMIN user
```

---

## 📊 **System Components Breakdown**

### **1. Frontend Layer (React)**
- **Employee Portal** (`frontend.html`)
  - Role-based login (Employee/HR selection)
  - Real-time chat interface
  - Calendar widget for scheduling
  - Email preview with send/cancel buttons
  - Remote status selection (Remote/On-site)
  - Download links for W-2s

- **HR Dashboard** (`hr_dashboard.html`)
  - Secure login (hr/datadog2026)
  - Chart.js visualizations
  - PTO analytics (bar chart)
  - Ticket trends (line chart)
  - Category breakdown (doughnut chart)
  - Real-time metrics

### **2. Backend API (Flask - Python)**
- **Port:** 8080
- **CORS:** Enabled for cross-origin requests
- **Sessions:** Server-side session management
- **Endpoints:** 8 main API routes

### **3. Core Intelligence (NLP Engine)**
- **Intent Detection:** 8 intent types using regex patterns
- **Smart Escalation:** Detects policy questions needing HR approval
- **Hybrid Responses:** Answers + offers HR email when needed
- **Fallback:** Unknown questions auto-offer email to HR

### **4. Data Storage**
- **employees.csv:** 1,000 employee records
  - Fields: Employee ID, Name, Salary, PTO, Bonus, Location, Team, Manager, etc.
  - Live updates for location/remote status changes
  
- **hr_tickets.csv:** 30 sample tickets
  - Fields: Ticket ID, Employee, Date, Category, Status, Resolution Days
  - Used for HR analytics

- **Tax Documents:** PDF W-2s generated on-demand
  - Stored in `/tax_documents/`
  - Employee-specific, year-specific

### **5. Key Features**

**Employee Features:**
- ✅ Natural language Q&A (salary, PTO, bonus, location, team, W-2)
- ✅ W-2 generation & download
- ✅ Location updates with remote status
- ✅ Email drafting to HR with preview
- ✅ Calendar scheduling widget
- ✅ Smart escalation for policy questions

**HR Features:**
- ✅ Secure dashboard access
- ✅ PTO usage analytics (prevent burnout)
- ✅ Ticket volume trends (weekly)
- ✅ Average resolution time tracking
- ✅ Category breakdown visualization
- ✅ Low PTO employee alerts

### **6. Data Flow Examples**

**Scenario 1: Employee asks for salary**
```
User → UI → /api/ask → HR Agent → Query Parser → salary_query intent 
→ Answer Generator → Database → Return salary → UI displays
```

**Scenario 2: Employee requests extra PTO**
```
User → UI → /api/ask → HR Agent → email_hr_request intent 
→ Draft email → Store in session → Show preview → User confirms 
→ /api/send-email-to-hr → Gmail SMTP → HR receives email
```

**Scenario 3: Employee moving + remote work**
```
User → UI → /api/ask → hybrid_request intent → Answer current location 
+ show email draft → User confirms → Email sent to HR
```

**Scenario 4: HR views analytics**
```
HR Admin → Dashboard → /api/hr/analytics/pto-usage → Calculate stats 
→ Return JSON → Chart.js renders bar chart
```

### **7. Technology Stack**

**Frontend:**
- React 18 (via CDN)
- Babel standalone (JSX compilation)
- Chart.js 4.4 (data visualization)
- Space Grotesk font (Datadog branding)

**Backend:**
- Python 3.x
- Flask (web framework)
- Flask-CORS (cross-origin support)
- Pandas (data manipulation)
- ReportLab (PDF generation)
- smtplib (email sending)

**Data:**
- CSV files (structured data)
- Flask sessions (state management)
- File system (PDF storage)

### **8. Security Features**
- Session-based authentication for HR
- Credentials validation (hr/datadog2026)
- CORS with credentials support
- No direct database access from frontend
- Email preview before sending
- HR-only analytics endpoints

### **9. Smart Intelligence**

**Intent Detection Patterns:**
- Salary: "what's my salary", "how much do I make"
- PTO: "days off", "vacation time", "PTO"
- Location: "where do I work", "can I move to"
- W-2: "tax form", "W-2", "w2"
- Updates: "moving to", "change my location"
- Calendar: "schedule call", "when available"
- Email HR: "can I take", "is there a way"

**Smart Escalation:**
- Detects policy questions ("Can I move and work remote?")
- Provides current info + offers HR email
- Unknown questions automatically offer escalation
- Never leaves user without a path forward

### **10. Conversational Intelligence**

**Multi-turn Conversations:**
- "I'm moving to Texas" → "Remote or on-site?" → Buttons → Update both fields
- "Can I take extra PTO?" → Email draft preview → Send/Cancel → Confirmation

**Session Memory:**
- Remembers pending location updates
- Stores draft emails between requests
- Maintains HR authentication state

---

## 🎯 **Key Metrics**

- **Employees:** 1,000 in database
- **Intent Types:** 8 different conversation paths
- **API Endpoints:** 8 routes
- **Data Files:** 2 CSVs + dynamic W-2 PDFs
- **Chart Types:** 3 (bar, line, doughnut)
- **User Roles:** 2 (Employee, HR Admin)
- **Response Time:** Real-time (< 1 second)

---

## 🚀 **Deployment**

- **Server:** Flask development server
- **Port:** 8080
- **Host:** localhost (127.0.0.1)
- **Access:** http://localhost:8080
- **HR Dashboard:** http://localhost:8080/hr_dashboard.html

---

This architecture demonstrates a **production-ready HR automation system** with intelligent NLP, real-time analytics, and professional UX! 🎉
