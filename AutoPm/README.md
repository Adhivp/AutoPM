# AutoPM - AI-Powered Project Management Assistant

AutoPM is an intelligent project management assistant that automates dashboards, provides real-time resource allocation insights, predicts risks and delays, and delivers natural language summaries for managers and stakeholders.

## 🚀 Features

### Core Capabilities
- **Auto-Generated Dashboards** - Integrate Jira, GitHub, and MS Teams data to create comprehensive project dashboards automatically
- **Resource Allocation Insights** - Real-time visibility into who is overloaded and who is available for new tasks
- **Risk & Delay Prediction** - AI-powered predictions using historical patterns and live progress signals
- **Natural Language Summaries** - Clear, actionable summaries for managers and stakeholders

### Integrations
- 🔷 **Jira** - Sync projects, issues, and sprints
- 💻 **GitHub** - Connect repositories, issues, and pull requests
- 💬 **MS Teams** - (Coming Soon) Team collaboration and notifications

## 🛠️ Tech Stack

### Frontend
- **React** - UI library
- **React Router** - Navigation
- **Tailwind CSS** - Styling
- **Framer Motion** - Animations
- **Axios** - API calls
- **Lucide React** - Icons
- **Vite** - Build tool

### Backend
- **FastAPI** - Python web framework
- **SQLAlchemy** - ORM
- **PostgreSQL** - Database
- **JWT** - Authentication
- **OAuth2** - GitHub & Jira integration

## 📦 Installation

### Prerequisites
- Node.js (v18 or higher)
- Python 3.11+
- PostgreSQL

### Frontend Setup

1. Navigate to the frontend directory:
```bash
cd AutoPm
```

2. Install dependencies:
```bash
npm install
```

3. Create a `.env` file:
```bash
cp .env.example .env
```

4. Update the `.env` file with your backend API URL:
```
VITE_API_URL=http://localhost:8000
```

5. Start the development server:
```bash
npm run dev
```

The frontend will be available at `http://localhost:5173`

### Backend Setup

1. Navigate to the backend directory:
```bash
cd fastapi_backend
```

2. Create and activate virtual environment:
```bash
python -m venv autopm_venv
source autopm_venv/bin/activate  # On Windows: autopm_venv\Scripts\activate
```

3. Install dependencies:
```bash
pip install -r requirements.txt
```

4. Create a `.env` file with your configuration:
```
DATABASE_URL=postgresql://user:password@localhost/autopm
SECRET_KEY=your-secret-key
GITHUB_CLIENT_ID=your-github-client-id
GITHUB_CLIENT_SECRET=your-github-client-secret
GITHUB_REDIRECT_URI=http://localhost:5173/profile
JIRA_CLIENT_ID=your-jira-client-id
JIRA_CLIENT_SECRET=your-jira-client-secret
JIRA_REDIRECT_URI=http://localhost:5173/profile
```

5. Run database migrations:
```bash
python -c "from database import init_db; init_db()"
```

6. Start the backend server:
```bash
uvicorn main:app --reload
```

The backend will be available at `http://localhost:8000`

## 🎨 Features Walkthrough

### 1. Landing Page
- Beautiful hero section with gradient backgrounds
- Feature showcase with animated cards
- Integration highlights
- Responsive design for all devices

### 2. Authentication
- User registration with email validation
- Secure login with JWT tokens
- Password encryption
- Protected routes

### 3. Dashboard
- Real-time project statistics
- Activity feed
- Quick actions
- AI-powered insights
- Coming soon features banner

### 4. Profile & Integrations
- User profile management
- GitHub integration with OAuth2
- Jira integration with OAuth2
- Connection status indicators
- Easy connect/disconnect functionality

## 🔒 Security Features

- JWT token-based authentication
- Encrypted password storage
- Secure OAuth2 flows
- HTTP-only authentication
- Protected API endpoints

## 📱 Responsive Design

AutoPM is fully responsive and works seamlessly on:
- Desktop (1920px and above)
- Laptop (1024px - 1919px)
- Tablet (768px - 1023px)
- Mobile (320px - 767px)

## 🎯 Future Enhancements

- MS Teams integration
- Advanced AI predictions
- Real-time collaboration
- Custom dashboard widgets
- Automated report generation
- Mobile apps (iOS & Android)
- Slack integration
- Trello integration

## 🤝 Contributing

Contributions are welcome! Please feel free to submit a Pull Request.

## 📄 License

This project is licensed under the MIT License.

## 📞 Support

For support, email support@autopm.com or open an issue on GitHub.

---

Built with ❤️ by the AutoPM Team
