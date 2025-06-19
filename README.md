# 📈 DailyInvestAI

**DailyInvestAI** is an AI-powered investment assistant designed to simplify market analysis and help users make informed financial decisions. Built with a focus on accessibility, especially for users in Tier‑2 and Tier‑3 cities, it provides personalized recommendations, real-time insights, and comprehensive analytics.

---

## 🏗️ Project Structure

```
DailyInvestAI/
│
├── backend/
│   ├── app/
│   │   ├── main.py          # Entry point for FastAPI backend
│   │   ├── routes/
│   │   │   ├── insights.py  # Handles investment insights API
│   │   │   ├── news.py      # Aggregates and processes news data
│   │   │   └── stocks.py    # Stock data fetching and processing
│   │   ├── services/
│   │   │   ├── ai.py        # Core AI and ML models
│   │   │   ├── utils.py     # Utility functions
│   │   │   └── config.py    # Configuration and environment settings
│   ├── tests/
│   │   ├── test_insights.py # Unit tests for insights
│   │   └── test_news.py     # Unit tests for news aggregation
│   └── requirements.txt     # Python dependencies
│
├── frontend/
│   ├── src/
│   │   ├── components/      # React components
│   │   ├── pages/           # Page-level React files
│   │   ├── App.js           # Main React application file
│   │   └── index.js         # Entry point for React app
│   ├── public/
│   │   └── index.html       # Main HTML template
│   ├── package.json         # Frontend dependencies
│   └── yarn.lock            # Dependency lock file
│
└── README.md                # Project documentation
```

---

## 🚀 Features

- **Real-time Stock Analysis:** Provides live updates on stock performance.
- **News Sentiment Analysis:** Aggregates and summarizes financial news, complete with sentiment evaluation.
- **AI-Driven Recommendations:** Offers daily personalized investment strategies.
- **User-Friendly Interface:** Simplified for accessibility across diverse audiences.
- **Multilingual Support:** Available in multiple languages for broader usability.

---

## 🛠️ Tech Stack

### Backend
- **Framework:** FastAPI
- **Machine Learning:** Scikit-Learn, Pandas, NumPy
- **API Integrations:** SEBI, NSE, BSE, Google News
- **Database:** SQLite (or your choice)

### Frontend
- **Framework:** React.js
- **State Management:** Redux
- **Styling:** Tailwind CSS
- **Deployment:** Docker, AWS, or GCP

---

## 📥 Installation

### Prerequisites
- Python 3.8+
- Node.js 14+
- Yarn or npm
- Docker (optional for deployment)

### Steps

#### 1. Clone the Repository
```bash
git clone https://github.com/InfinityWaveAI/DailyInvestAI.git
cd DailyInvestAI
```

#### 2. Set Up the Backend
```bash
cd backend
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
pip install -r requirements.txt
```

#### 3. Set Up the Frontend
```bash
cd frontend
yarn install  # Or use npm install
```

---

## 🌐 Running the Project

### Start the Backend
```bash
cd backend
uvicorn app.main:app --reload
```

### Start the Frontend
```bash
cd frontend
yarn start
```

Visit `http://localhost:3000` to access the web application.

---

## 🔧 Configuration

Create a `.env` file in the `backend/` directory:
```env
API_KEY_SEBI=your_sebi_api_key
API_KEY_NSE=your_nse_api_key
NEWS_API_KEY=your_news_api_key
SECRET_KEY=supersecretkey
```

---

## 🧪 Testing

Run tests using the following commands:

### Backend Tests
```bash
cd backend
pytest tests/
```

### Frontend Tests
```bash
cd frontend
yarn test
```

---

## 📚 Usage

1. **Login/Register:** Start by creating a user account.
2. **Set Preferences:** Choose investment preferences and risk tolerance.
3. **Daily Insights:** Access AI-driven recommendations and analytics.
4. **News & Sentiment:** View market news summaries and sentiment scores.
5. **Visualize Trends:** Explore charts and predictions.

---

## 📄 License

This project is licensed under the MIT License. See the [LICENSE](LICENSE) file for details.

---

## 🤝 Contributions

We welcome contributions! Follow these steps:

1. Fork the repository.
2. Create a feature branch (`git checkout -b feature-branch`).
3. Commit your changes (`git commit -m 'Add new feature'`).
4. Push to your branch (`git push origin feature-branch`).
5. Open a pull request.

---

## ✨ Acknowledgements

- **InfinityWaveAI Team**
- **APIs & Data Sources:** SEBI, NSE, BSE, Google News
- **Open Source Libraries:** FastAPI, React, Scikit-Learn, Tailwind CSS

---
