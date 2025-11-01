# BMIS Beta Deployment Guide

**Version**: 1.1 Beta
**Date**: 2025-10-15
**Status**: Ready for Beta Testing

---

## Quick Start (5 Minutes)

### 1. Install Dependencies

```bash
cd bmis_ml_pipeline
pip install -r requirements.txt
```

**Note**: Installation may take 3-5 minutes as it downloads Streamlit and dependencies.

### 2. Run the Web Application

```bash
streamlit run app.py
```

The app will automatically open in your web browser at `http://localhost:8501`

### 3. Test the Application

1. Fill out the student profile form in the left sidebar
2. Click "Find Resources" to generate recommendations
3. Use the location and grade filters to test filtering
4. Verify recommendations display correctly

---

## What's New in Beta Version

### ✅ Critical Fixes Implemented

**Phase 1 UI Enhancements** (addresses validation issues):

1. **Location Filter Dropdown** 🌐
   - Options: Show All, Virtual/Online Only, In-Person Only, Hybrid
   - **Mitigates**: 13% location alignment → allows users to filter to 100% match
   - **Impact**: Users can now self-select accessible resources

2. **Grade Level Filter Dropdown** 🎓
   - Options: Show All, My Grade Only, My Grade ±1 Year, My Grade ±2 Years, Elementary, Middle School, High School
   - **Mitigates**: 68% academic appropriateness → allows users to filter to age-appropriate resources
   - **Impact**: Students find resources at the right difficulty level

3. **Disclaimer & Guidance** ℹ️
   - Clear messaging about recommendation nature
   - Instructions for using filters
   - Filter state indicators showing "X of Y resources"

4. **Enhanced Recommendation Display** 📚
   - Color-coded location badges (🟢 Virtual, 🔵 In-person, 🟡 Hybrid)
   - Color-coded cost badges (💰 Low/Medium/High)
   - Grade level, category, and STEM field prominently displayed
   - Match score visible
   - Click-through to resource URLs

### ✅ Core System Performance

From comprehensive validation (45 diverse profiles):

- **93.3% success rate**: 42 of 45 profiles received 15+ recommendations
- **67.7% accessibility alignment**: Low-income students get affordable resources (Target: 60%)
- **6.13 average categories**: Excellent diversity in recommendation types
- **25.3% database coverage**: 565 unique resources surfaced

---

## System Architecture

### Backend: Python ML Pipeline

**Components**:
- `recommendation_engine.py` - Main recommendation logic
- 4 K-Means clustering models (accessibility, academic, STEM field, format)
- TF-IDF similarity engine (500-term vocabulary)
- 2,237 STEM resources database

**Performance**:
- Model loading: < 2 seconds
- Recommendation generation: < 0.5 seconds
- Suitable for real-time use

### Frontend: Streamlit Web App

**Components**:
- `app.py` - Main Streamlit application
- Sidebar form for student profile input
- Main area for recommendations display
- Client-side filtering (location & grade)

**Features**:
- Mobile-responsive design
- Professional styling with custom CSS
- Real-time filtering
- CSV export functionality

---

## User Flow

### Step 1: Profile Creation (3-5 minutes)

**Student fills out**:
- Grade level (6-12)
- Financial situation (Low/Medium/High)
- Location preference (Virtual/In-person/Hybrid)
- Transportation availability
- Academic level (Beginner/Intermediate/Advanced)
- Time availability (hours/week)
- Support needed (Low/Medium/High)
- STEM interests (free text - important for matching!)
- STEM fields (up to 5 selections)
- Format preferences (up to 5 selections)

### Step 2: Recommendation Generation (< 1 second)

**System processes**:
1. Encodes student profile for clustering
2. Finds top 5 clusters in each dimension (accessibility, academic, STEM, format)
3. Unions accessibility + academic clusters (broad match)
4. Intersects with STEM clusters (precision)
5. Ranks candidates by TF-IDF similarity to interests
6. Returns top 20 recommendations

### Step 3: Filtering & Exploration

**User can**:
- Filter by location (Virtual/In-person/Hybrid)
- Filter by grade appropriateness
- View detailed recommendation cards
- Click through to resource URLs
- Download recommendations as CSV

---

## Beta Testing Goals

### Primary Objectives

1. **Validate Accessibility Alignment**
   - Monitor: % Low/Free resources for low-income students
   - Target: Maintain ≥60% (currently 67.7%)
   - Alert if drops below threshold

2. **Test Filter Effectiveness**
   - Monitor: % of users who use filters
   - Monitor: User satisfaction with filtered results
   - Validate: Do filters solve location/grade issues?

3. **Collect User Feedback**
   - Survey users after first session (5 questions)
   - Track: Recommendation helpfulness (1-5 scale)
   - Track: Resource accessibility (Yes/No)
   - Track: Application conversion (how many applied?)

### Success Metrics

**Must Maintain**:
- Accessibility alignment ≥60%
- No critical system errors
- Recommendation generation success >95%

**Monitor & Improve**:
- User satisfaction >3.5/5
- Filter usage >30% of users
- Return rate >40%
- Application conversion >20%

---

## Deployment Options

### Option 1: Local Testing (Immediate)

**Best For**: Development, testing, demo

**How To Run**:
```bash
streamlit run app.py
```

**Access**: `http://localhost:8501`

**Pros**: Immediate, no setup, good for testing
**Cons**: Only accessible on your machine, not scalable

---

### Option 2: Streamlit Community Cloud (Recommended for Beta)

**Best For**: Beta testing with 50-100 users

**Steps**:

1. **Prepare Repository**:
   ```bash
   # Create git repository if not already
   git init
   git add .
   git commit -m "Beta deployment ready"
   ```

2. **Push to GitHub**:
   - Create GitHub repository: `bmis-recommendation-system`
   - Push code to GitHub
   ```bash
   git remote add origin https://github.com/yourusername/bmis-recommendation-system.git
   git push -u origin main
   ```

3. **Deploy to Streamlit Cloud**:
   - Go to https://share.streamlit.io/
   - Click "New app"
   - Connect your GitHub repository
   - Select `app.py` as main file
   - Click "Deploy"

4. **Get URL**:
   - Your app will be live at: `https://yourusername-bmis-recommendation-system.streamlit.app`
   - Share this URL with beta users

**Pros**:
- Free for public apps
- Automatic HTTPS
- Easy to update (git push to redeploy)
- Handles 50-100 concurrent users easily

**Cons**:
- Public apps only (code is visible)
- Limited compute resources
- Not for enterprise use

**Cost**: FREE

---

### Option 3: Heroku (Alternative)

**Best For**: More control, private deployments

**Steps**:

1. Create `Procfile`:
   ```
   web: streamlit run app.py --server.port=$PORT
   ```

2. Deploy to Heroku:
   ```bash
   heroku create bmis-recommendations
   git push heroku main
   ```

**Pros**: Private deployments, more resources
**Cons**: Costs $7/month minimum, more complex setup

---

### Option 4: AWS/Azure/GCP (Production)

**Best For**: Full production deployment

**Not Recommended Yet**: Wait until after beta validation

**Considerations**:
- Use AWS EC2 or AWS App Runner
- Or Azure App Service
- Or Google Cloud Run
- Requires: Domain, SSL cert, load balancer, monitoring
- Cost: $20-100/month depending on traffic
- Setup time: 1-2 weeks

---

## Recommended Beta Deployment (Week 1)

### Monday-Tuesday: Prepare for Deployment

**Tasks**:
- [x] Streamlit app built (`app.py`)
- [x] Filters implemented (location & grade)
- [x] Requirements.txt updated
- [ ] Test app locally with multiple profiles
- [ ] Test filters with edge cases
- [ ] Test on mobile devices (Chrome DevTools)
- [ ] Fix any bugs found

**Deliverable**: Working app tested locally

---

### Wednesday: Deploy to Streamlit Cloud

**Tasks**:
1. Create GitHub repository
2. Push code to GitHub
3. Deploy to Streamlit Community Cloud
4. Get public URL
5. Test deployed app
6. Verify performance (< 2 sec load time)

**Deliverable**: Live beta URL

---

### Thursday: Beta User Recruitment

**Tasks**:
1. Create beta sign-up form (Google Forms)
   - Name
   - Email
   - Grade level
   - STEM interests
   - Financial situation
   - Preferred contact method

2. Post recruitment message:
   - Jack and Jill regional groups
   - NSBE Jr. chapters
   - Local STEM clubs
   - Social media (if applicable)

**Target**: 50-100 beta signups

**Message Template**:
```
🔬 Beta Testers Needed! 🔬

Black Minds in STEM is launching a FREE platform to help Black high school
students (grades 6-12) find STEM opportunities - scholarships, competitions,
summer programs, research opportunities, and more!

We're looking for 50-100 beta testers to try the platform and provide feedback.

What you'll do:
✅ Fill out a 5-minute profile
✅ Get 20 personalized STEM resource recommendations
✅ Provide feedback on your experience
✅ Apply to resources that interest you!

What makes us different:
💰 We prioritize FREE and low-cost resources for students with limited budgets
🌐 We consider your location and transportation
🎓 We match your grade level and academic background
🤖 Powered by AI trained on 2,200+ STEM opportunities

Sign up: [Google Form URL]
Questions: [Contact Email]

Beta testing runs for 4 weeks starting [Date].
```

**Deliverable**: 50+ beta signups

---

### Friday: Onboarding & Monitoring Setup

**Tasks**:

1. **Create Welcome Email**:
   ```
   Subject: Welcome to Black Minds in STEM Beta! 🔬

   Hi [Name],

   Thank you for joining our beta testing program! Here's how to get started:

   1. Visit: [Streamlit App URL]
   2. Fill out your profile (5 minutes)
   3. Get your personalized recommendations
   4. Use the filters to refine by location and grade level
   5. Click through to resources that interest you
   6. Fill out the feedback survey [Survey URL] after your first session

   Tips for Best Results:
   - Be specific about your interests (e.g., "machine learning with Python"
     instead of just "computer science")
   - Select up to 5 STEM fields you're interested in
   - Use the filters if you need virtual-only or grade-specific resources

   Questions? Reply to this email or contact [Support Email]

   Happy exploring!
   The BMIS Team
   ```

2. **Set Up Feedback Survey** (Google Forms):
   - Q1: Were these recommendations helpful? (1-5 scale)
   - Q2: Did you find resources you can actually access? (Yes/No)
   - Q3: What would make recommendations more useful? (Open text)
   - Q4: How many recommendations did you apply to? (Number)
   - Q5: Would you recommend this platform to others? (1-5 scale)

3. **Create Monitoring Dashboard** (Google Sheets or Notion):
   - Track: Number of users per day
   - Track: Feedback responses
   - Track: Common complaints/issues
   - Track: Feature requests

**Deliverable**: Onboarding system ready

---

## Week 2-5: Beta Testing & Monitoring

### Daily Tasks

**Morning** (15 minutes):
- Check for new beta signups
- Send welcome emails
- Monitor for critical errors
- Review feedback submissions

**End of Week** (1 hour):
- Analyze feedback trends
- Calculate satisfaction scores
- Identify common issues
- Plan any hotfixes needed

### Weekly Reports

**Template**:
```
BMIS Beta Week [N] Report
Date: [Start] to [End]

Users:
- Total signups: [X]
- Active users: [Y]
- Return users: [Z]

Feedback:
- Average satisfaction: [X.X]/5
- % finding accessible resources: [X]%
- Common praise: [Top 3]
- Common complaints: [Top 3]

Metrics:
- Filter usage: [X]% of users
- Avg recommendations per user: [X]
- Avg session duration: [X] minutes

Action Items:
- [ ] Fix [Issue 1]
- [ ] Investigate [Issue 2]
- [ ] Consider enhancement [Feature]

Next Week Focus:
[Plan for Week N+1]
```

---

## Troubleshooting

### Issue: App Won't Start

**Error**: `No module named streamlit`

**Solution**:
```bash
pip install streamlit
```

---

### Issue: Models Not Loading

**Error**: `FileNotFoundError: data/bmis_final_ml_ready_dataset_cs_refined.csv`

**Solution**:
- Ensure you're running from `bmis_ml_pipeline/` directory
- Check that `data/`, `models/`, and `preprocessors/` folders exist
- Verify all model files are present

---

### Issue: Slow Performance

**Symptoms**: Recommendations take >5 seconds

**Solutions**:
1. Check model caching is working (`@st.cache_resource`)
2. Verify you're not reloading models on each request
3. Check internet connection (for Streamlit Cloud)
4. Consider upgrading to paid Streamlit hosting

---

### Issue: Filters Not Working

**Symptoms**: Filtering doesn't change results

**Debug**:
1. Check if recommendations DataFrame has required columns (`location_type`, `target_grade`)
2. Verify filter logic in `filter_recommendations()` function
3. Test with sample data to isolate issue

---

## Security Considerations

### Beta Deployment

✅ **Safe for Beta**:
- No user authentication (public app)
- No sensitive data collected
- Read-only access to dataset
- No financial transactions

⚠️ **Before Production**:
- Add user authentication (Auth0, Firebase, etc.)
- Implement rate limiting (prevent abuse)
- Add CAPTCHA to profile form
- Set up proper logging and monitoring
- Add SSL certificate (HTTPS)
- Add privacy policy and terms of service

---

## Data Privacy

### What We Collect (Beta)

**User Profile Data**:
- Grade level
- Financial situation (Low/Medium/High - NOT dollar amounts)
- STEM interests (text)
- Preferences (location, time, format)

**NOT Collected**:
- Names, emails (unless voluntarily submitted for feedback)
- Specific location (city/state - just preference Virtual/In-person)
- School information
- Financial details beyond Low/Medium/High

**Feedback Survey** (Optional):
- Satisfaction ratings
- Open text feedback
- Application count

### Data Storage

**Beta**:
- Streamlit Cloud: Session data only (not persisted)
- Google Forms: Feedback responses
- **No database**: Profile data is not saved

**Production Considerations**:
- Add database to save profiles (optional feature)
- Implement proper data encryption
- Add GDPR/CCPA compliance
- Allow data deletion requests

---

## Performance Benchmarks

### Expected Performance

| Metric | Target | Acceptable | Poor |
|--------|--------|------------|------|
| Model Loading | < 2 sec | < 5 sec | > 5 sec |
| Recommendation Gen | < 0.5 sec | < 2 sec | > 2 sec |
| Page Load | < 3 sec | < 5 sec | > 5 sec |
| Filter Response | Instant | < 1 sec | > 1 sec |

### Optimization Tips

**If Slow**:
1. Enable Streamlit caching (`@st.cache_resource`)
2. Reduce model size (already optimized)
3. Upgrade Streamlit Cloud tier
4. Move to dedicated server

**Current Status**: ✅ All metrics in "Target" range locally

---

## Backup & Rollback Plan

### If Critical Bug Found

**Immediate**:
1. Take app offline (delete Streamlit deployment)
2. Post message in beta group: "App temporarily down for maintenance"
3. Fix bug locally
4. Test thoroughly
5. Redeploy

**Rollback**:
```bash
git revert HEAD
git push origin main  # Streamlit auto-redeploys
```

### If Accessibility Alignment Drops

**If monitoring shows <60% Low/Free for low-income students**:

1. **Investigate**: Check recent code changes
2. **Analyze**: Run validation script on current code
3. **Compare**: Check against v1.1 benchmark (67.7%)
4. **Fix**: Revert to known-good version if needed
5. **Alert**: Notify beta users of temporary issue

---

## Success Criteria for Beta → Production

### Must Pass (Non-Negotiable)

- [x] Accessibility alignment maintained ≥60%
- [ ] User satisfaction ≥3.5/5
- [ ] No critical bugs affecting >10% of users
- [ ] Filters working correctly
- [ ] App stable for 4 weeks

### Should Pass (Important)

- [ ] Filter usage ≥30% of users
- [ ] Return rate ≥40%
- [ ] Application conversion ≥20%
- [ ] Mobile usability good

### Decision Matrix

**After 4 Weeks**:

| Satisfaction | Accessibility | Action |
|--------------|---------------|--------|
| ≥4.0/5 | ≥60% | ✅ Production Launch (Week 6) |
| 3.5-4.0/5 | ≥60% | ⚠️ Minor fixes, then production (Week 8) |
| 3.0-3.5/5 | ≥60% | ⚠️ Algorithm enhancements needed (Week 12) |
| <3.0/5 | ≥60% | ❌ Major redesign required |
| Any | <60% | ❌ Critical issue - pause and fix |

---

## Contact & Support

### For Beta Users

**Questions**: [Support Email]
**Bug Reports**: [GitHub Issues or Email]
**Feedback**: [Survey Link]

### For Development Team

**Deployment Issues**: Check Streamlit Cloud logs
**Model Issues**: Review `bmis_ml_pipeline/outputs/` reports
**Validation**: Re-run `testing/test_runner.py`

---

## Next Steps After Beta

### Phase 2 Enhancements (Optional)

**If beta feedback indicates need**:

1. **Location Algorithm Enhancement** (Week 6-7)
   - Implement location preference weighting
   - Target: 40-50% automatic match (up from 13%)
   - See `VALIDATION_REPORT.md` for implementation details

2. **Grade Appropriateness Algorithm** (Week 7-8)
   - Add grade-level filtering in engine
   - Target: 75%+ within ±2 grades (up from 68%)

3. **Dataset Expansion** (Week 8-10)
   - Add 100-200 middle school resources
   - Add career/technical resources
   - Improve niche interest coverage

### Production Launch (Week 10-12)

1. Re-validate with 30+ new profiles
2. Implement user authentication
3. Add analytics tracking
4. Set up production hosting
5. Create marketing materials
6. Launch to public!

---

## Timeline Summary

| Week | Phase | Deliverable |
|------|-------|-------------|
| 1 | Deployment Prep | Live beta URL |
| 1 | User Recruitment | 50+ beta signups |
| 2-5 | Beta Testing | User feedback, data collection |
| 6-7 | Analysis & Decision | Go/no-go for production |
| 8-10 | Enhancements (if needed) | Algorithm improvements |
| 11-12 | Production Launch | Public deployment |

**Total Timeline**: 12 weeks to production
**Buffer Before EA**: 6 weeks (plenty of time!)

---

## Final Checklist

### Pre-Launch (This Week)

- [x] Streamlit app built
- [x] Location filter implemented
- [x] Grade filter implemented
- [x] Disclaimer added
- [x] Recommendation cards styled
- [ ] Local testing complete
- [ ] Mobile testing complete
- [ ] Deploy to Streamlit Cloud
- [ ] Beta recruitment message posted
- [ ] Feedback survey created
- [ ] Welcome email template ready

### Week 1 Done When:

✅ App is live and accessible
✅ 50+ beta users recruited
✅ Onboarding system ready
✅ Monitoring dashboard set up
✅ No critical bugs

---

**You're ready for beta! Focus on getting that app deployed and recruiting users. The hard part (ML pipeline) is done - now it's time to let real users validate your work!** 🚀
