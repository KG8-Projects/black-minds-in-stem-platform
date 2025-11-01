# BMIS App v2.0 - Professional Multi-Tab Application

## Overview

The redesigned BMIS (Black Minds in STEM) app is a professional, multi-tab web application that helps Black students discover STEM opportunities through AI-powered personalized recommendations.

**Key Features:**
- 🏠 Welcome page with clear value proposition
- 🎯 Personalized recommendations using ML
- 🔍 Browse and search 2,200+ STEM resources
- 💬 Feedback collection system
- 📊 Anonymous usage analytics
- 🎨 Modern dark theme with electric blue branding
- 📱 Mobile-responsive design
- ⚡ K-12 grade level support

---

## What's New in v2.0

### UI/UX Improvements
- ✅ Professional 4-tab structure (Home, Get Recommendations, Browse All, Share Feedback)
- ✅ Dark theme with electric blue/cyan color scheme
- ✅ Improved card-based resource display
- ✅ Better mobile responsiveness
- ✅ Enhanced loading states and error handling
- ✅ Hidden Streamlit branding for clean look

### Feature Additions
- ✅ K-12 grade level support (previously 6-12 only)
- ✅ Browse all resources tab with search and filters
- ✅ Feedback collection system
- ✅ Anonymous usage logging for analytics
- ✅ Pagination for browse results
- ✅ Success/warning/info message boxes

### Form Enhancements
- ✅ 2-column form layout for better UX
- ✅ Expanded time availability slider (0-40 hours)
- ✅ "No preference" option for location
- ✅ Better field organization and labeling
- ✅ Improved placeholder text and help tooltips

### Analytics & Tools
- ✅ Usage logging (session-based, anonymous)
- ✅ Feedback CSV storage
- ✅ Analytics dashboard script
- ✅ Link verification script

---

## Installation & Setup

### Prerequisites
- Python 3.8 or higher
- pip package manager

### Steps

1. **Install dependencies:**
```bash
cd bmis_ml_pipeline
pip install -r requirements.txt
```

2. **Ensure your ML models are trained:**
```bash
# If not already done
python src/recommendation_engine.py
```

3. **Verify your dataset is present:**
```
data/bmis_final_ml_ready_dataset_cs_refined.csv
```

4. **Run the app:**
```bash
streamlit run app.py
```

5. **Access the app:**
- Open browser to http://localhost:8501
- The app should load with the Home tab visible

---

## File Structure

```
bmis_ml_pipeline/
├── app.py                          # Main Streamlit app (redesigned)
├── verify_links.py                 # Link verification script
├── analytics_dashboard.py          # Analytics analysis script
├── src/
│   └── recommendation_engine.py    # ML backend
├── data/
│   └── bmis_final_ml_ready_dataset_cs_refined.csv
├── models/                         # Trained ML models
├── logs/                           # Generated logs (created at runtime)
│   ├── usage_log.csv              # Anonymous usage data
│   ├── feedback.csv               # User feedback
│   └── analytics_summary_*.json   # Generated reports
└── requirements.txt
```

---

## Usage Guide

### For Students

#### Home Tab (🏠)
- See what BMIS offers
- Click "Get Started" to begin

#### Get Recommendations Tab (🎯)
1. Fill out your profile:
   - Grade level (K-12)
   - Financial situation
   - Location preference
   - Academic level
   - STEM interests
   - Preferred program types
2. Click "Get My Recommendations"
3. View 20 personalized results
4. Use filters to refine by location or grade
5. Download results as CSV

#### Browse All Tab (🔍)
1. Search by keywords
2. Filter by category, STEM field, cost, location
3. Sort results
4. Browse 20 results per page
5. Download filtered results

#### Share Feedback Tab (💬)
1. Rate your experience (1-5 stars)
2. Share what you liked
3. Suggest improvements
4. Report if you found new resources
5. (Optional) Share success story
6. (Optional) Leave email for follow-up

### For Developers

#### Running Link Verification
```bash
python verify_links.py
```
This will:
- Test all 2,200+ URLs in the dataset
- Generate a report with working/broken links
- Save results to `logs/link_verification_*.csv`
- Save broken links to `logs/broken_links_*.csv`

#### Analyzing Usage Data
```bash
python analytics_dashboard.py
```
This will:
- Analyze usage logs and feedback
- Generate statistics (users, searches, ratings, etc.)
- Print key highlights for college essay
- Save JSON report to `logs/analytics_summary_*.json`

---

## Analytics & Privacy

### What We Track (Anonymous)
- Session IDs (randomly generated UUIDs)
- Event types (search, browse, feedback)
- Profile data (aggregated: grade level, financial situation, etc.)
- Search counts and timestamps
- Feedback ratings and responses

### What We DON'T Track
- Names or personal identifiers
- IP addresses
- Exact geolocation
- Browsing history outside the app

### Data Storage
- All logs stored locally in `logs/` folder
- CSV format for easy analysis
- Can be deleted anytime

---

## Customization

### Changing Colors
Edit the CSS in `app.py` (lines 32-337):
- Primary: `#00D9FF` (electric blue)
- Secondary: `#0A1628` (deep navy)
- Accent colors for badges

### Adjusting Recommendation Count
In `app.py`, find:
```python
recommendations = engine.get_recommendations(
    student_profile,
    top_n=20,  # Change this number
    ...
)
```

### Modifying Form Fields
Edit the form in `render_recommendations_tab()` function to add/remove fields.

---

## Troubleshooting

### App won't start
- Check Python version: `python --version` (need 3.8+)
- Reinstall dependencies: `pip install -r requirements.txt --force-reinstall`
- Check for port conflicts (Streamlit uses 8501)

### No recommendations appearing
- Ensure ML models are trained
- Check `models/` folder for .pkl files
- Verify dataset is in `data/` folder
- Check console for error messages

### Styling looks broken
- Clear browser cache
- Try different browser
- Check if custom CSS loaded (view page source)

### Logs not generating
- Check write permissions for `logs/` folder
- Ensure folder exists (created automatically)
- Check Python traceback in terminal

---

## Performance Tips

### For 100+ concurrent users:

1. **Deploy to cloud:**
   - Streamlit Cloud (free tier)
   - Heroku
   - AWS/GCP/Azure

2. **Optimize caching:**
   - ML models are cached with `@st.cache_resource`
   - Dataset loaded once per request

3. **Database upgrade:**
   - Consider PostgreSQL for logs (currently CSV)
   - Use Google Sheets API for feedback

4. **Monitor usage:**
   - Run `analytics_dashboard.py` daily
   - Watch for errors in logs

---

## Launch Checklist (Oct 31-Nov 1)

### Day Before Launch
- [ ] Test all 4 tabs thoroughly
- [ ] Verify forms submit correctly
- [ ] Test on mobile device
- [ ] Run link verification
- [ ] Clear test data from logs
- [ ] Create logs/ folder if missing
- [ ] Test CSV downloads
- [ ] Check all buttons work
- [ ] Verify filters function correctly

### Launch Day
- [ ] Start app: `streamlit run app.py`
- [ ] Test from different devices
- [ ] Share link with first users
- [ ] Monitor terminal for errors
- [ ] Be available for bug fixes

### Post-Launch (Daily for first week)
- [ ] Run analytics dashboard
- [ ] Check feedback submissions
- [ ] Monitor error logs
- [ ] Respond to user issues
- [ ] Back up logs folder

---

## Data for College Essay

After launching to 100+ users, run:
```bash
python analytics_dashboard.py
```

**Key metrics to highlight:**
- Total unique users
- Total searches performed
- Average user rating
- Resource discovery rate
- Number of success stories
- Grade level distribution (showing K-12 reach)
- Financial situation breakdown (showing accessibility focus)

**Sample essay talking points:**
- "Reached X students across Y grade levels"
- "Achieved Z/5.0 average user satisfaction"
- "Helped A% of users discover new STEM opportunities"
- "Collected B success stories from students who..."

---

## Support & Contact

**For bugs or issues:**
1. Check this README first
2. Search existing issues (if using GitHub)
3. Create new issue with:
   - Error message
   - Steps to reproduce
   - Browser/device info
   - Screenshot if applicable

**For feature requests:**
- Document use case
- Explain expected behavior
- Prioritize (must-have vs nice-to-have)

---

## Future Enhancements (Post-Launch)

### Phase 2 (Optional):
- [ ] Save favorite resources (localStorage)
- [ ] PDF export option
- [ ] Email notification system
- [ ] Social media sharing
- [ ] Advanced search with autocomplete
- [ ] Resource ratings and reviews
- [ ] Admin dashboard
- [ ] A/B testing for recommendations
- [ ] Multilingual support
- [ ] Integration with external APIs

### Technical Debt:
- [ ] Unit tests for ML engine
- [ ] Integration tests for tabs
- [ ] Performance benchmarking
- [ ] Security audit
- [ ] Accessibility audit (WCAG compliance)
- [ ] SEO optimization

---

## Credits

**Created by:** [Your Name]
**Version:** 2.0 Professional
**Launch Date:** Oct 31-Nov 1, 2025
**Purpose:** College application project + community impact

**Technologies:**
- Python 3.8+
- Streamlit 1.28+
- Pandas
- Scikit-learn
- TF-IDF
- K-Means Clustering

**Dataset:**
- 2,200+ STEM resources for Black students
- Categories: Scholarships, Programs, Competitions, etc.
- Curated and refined for ML training

---

## License

This project is for educational and community benefit purposes.

---

## Changelog

### v2.0 - Professional Redesign (Oct 2025)
- Complete UI/UX overhaul
- Added multi-tab structure
- K-12 grade support
- Browse all resources feature
- Feedback collection system
- Usage analytics
- Link verification tool
- Analytics dashboard
- Dark theme with electric blue branding

### v1.1 - Beta (Previous)
- Basic Streamlit app
- Sidebar form
- Recommendation display
- Location and grade filters
- CSV export

---

**Good luck with your launch! 🚀**
