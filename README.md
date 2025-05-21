# Trend Advertising 🚀

**Trend Advertising** is an AI-powered trend forecasting platform that clusters emerging social media trends, viral advertisements, and creator content to help marketers and influencers stay ahead of what's next.

We use web scraping, natural language processing (NLP), and machine learning models to extract signals from platforms like Instagram and Twitter, then apply deep learning models to identify, classify, and predict trends in real-time.

---

## 🔧 Technologies Used

- **Web Scraping**
  - Instagram: [`Instaloader`](https://instaloader.github.io/)
  - Twitter: (<https://www.selenium.dev/documentation/ide/>)

- **Machine Learning**
  - **Transformers**: For contextual analysis of captions, posts, and time series analysis ([Intro to Transformers](https://www.youtube.com/watch?v=wjZofJX0v4M))
  - **CNN**: For visual content analysis (e.g. post thumbnails)
  - **LSTM / BiLSTM**: For modeling time-series trend evolution

- **Data Preprocessing**
  - Hashtag frequency tracking (Track what is in fashion and going out of fashion)
  - Sentiment analysis
  - Engagement metrics extraction

---

## 📊 Goal

The system aims to:
- Scrape and collect data from trending public posts
- Analyze and cluster text/image content
- Predict future trend trajectories and engagement potential
- Provide APIs or dashboards for clients to access insights

---

## 🚀 Future Plans

- TikTok scraping (browser automation)
- Multi-modal classification (text + image + metadata)
- Trend virality scoring
- Interactive trend dashboard
