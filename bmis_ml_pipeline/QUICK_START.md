# BMIS Beta - Quick Start Guide

**5-Minute Setup** | **Ready for 50-100 Beta Users** | **Zero Configuration**

---

## 1. Run Locally (30 seconds)

```bash
cd bmis_ml_pipeline
streamlit run app.py
```

**Done!** App opens automatically at `http://localhost:8501`

---

## 2. Deploy to Web (5 minutes)

### GitHub Setup
```bash
# Initialize git if needed
git init
git add .
git commit -m "Beta ready"

# Push to GitHub
git remote add origin https://github.com/YOUR-USERNAME/bmis-beta.git
git push -u origin main
```

### Streamlit Cloud Deployment

1. Go to **https://share.streamlit.io/**
2. Click **"New app"**
3. Connect your GitHub repo
4. Select `app.py` as main file
5. Click **"Deploy"**

**Done!** Get your URL: `https://YOUR-USERNAME-bmis-beta.streamlit.app`

---

## 3. Beta Testing

### Share with Users

**Your Beta URL**: `[Your Streamlit URL]`

**Beta Message Template**:
```
🔬 Try Black Minds in STEM Beta!

Get personalized STEM resource recommendations - scholarships,
competitions, summer programs, and more.

1. Visit: [Your URL]
2. Fill out profile (5 min)
3. Get 20 recommendations
4. Use filters to refine by location/grade

Free • For Black high school students (grades 6-12)
```

---

## Features

✅ **Location Filter**: Virtual/In-person/Hybrid
✅ **Grade Filter**: My Grade Only, ±1 Year, ±2 Years
✅ **67.7% Accessibility**: Low-income students get affordable resources
✅ **93.3% Success Rate**: 42 of 45 test profiles got 15+ recommendations
✅ **Mobile Responsive**: Works on phones and tablets
✅ **Export**: Download recommendations as CSV

---

## Monitoring

### Key Metrics to Track

**Must Maintain**:
- Accessibility alignment ≥60% for low-income students
- No critical errors
- Fast performance (<2 sec)

**Monitor**:
- User satisfaction (target: >3.5/5)
- Filter usage (target: >30%)
- Application conversion (target: >20%)

### Feedback Survey

Create Google Form with 5 questions:
1. Were recommendations helpful? (1-5 scale)
2. Did you find accessible resources? (Yes/No)
3. What would improve recommendations? (Open text)
4. How many did you apply to? (Number)
5. Would you recommend to others? (1-5 scale)

---

## Troubleshooting

### App won't start?
```bash
pip install -r requirements.txt
streamlit run app.py
```

### Models not loading?
```bash
# Make sure you're in bmis_ml_pipeline directory
cd bmis_ml_pipeline
ls models/  # Should show .pkl files
ls data/    # Should show .csv file
```

### Slow performance?
- Check models are cached (look for "Using cached" in terminal)
- Restart Streamlit: Ctrl+C, then `streamlit run app.py`
- For Streamlit Cloud: Check resource usage in dashboard

---

## Success Criteria

### Beta → Production (After 4 weeks)

**Go to Production if**:
- ✅ Accessibility ≥60% maintained
- ✅ User satisfaction ≥3.5/5
- ✅ No critical bugs
- ✅ Positive feedback trends

**Need Enhancements if**:
- ⚠️ Satisfaction 3.0-3.5/5
- ⚠️ Common location/grade complaints
- ⚠️ Low filter usage

**Major Redesign if**:
- ❌ Satisfaction <3.0/5
- ❌ Accessibility <60%
- ❌ High error rates

---

## Support

**Questions**: See `BETA_DEPLOYMENT_GUIDE.md` for full details
**Validation Report**: See `testing/VALIDATION_REPORT.md`
**System Status**: Run `python testing/test_runner.py` to re-validate

---

## Timeline

| Week | Milestone |
|------|-----------|
| 1 | Deploy + recruit 50 users |
| 2-5 | Beta testing + feedback |
| 6-7 | Analyze + decide on enhancements |
| 8-10 | Optional algorithm improvements |
| 11-12 | **Production launch** |

**You have 12 weeks to production, 18 weeks to EA deadline. You're on schedule!** ✅

---

**Ready to launch? Run `streamlit run app.py` and start testing!** 🚀
