# AutoEval Testing Guide

## Pre-Testing Checklist

- [ ] Python 3.8+ installed
- [ ] Dependencies installed (`pip install -r requirements.txt`)
- [ ] `.env` file created with valid OpenAI API key
- [ ] Application running on `http://localhost:5000`

## Test Workflow

### Test 1: Create a Hackathon (Host Flow)

1. Navigate to `http://localhost:5000/host`
2. Fill in the form:
   - **Name**: "AI Innovation Challenge"
   - **Description**: "Build an AI-powered tool that solves a real-world problem"
   - **Evaluation Prompt**: "Evaluate projects based on innovation, technical implementation, code quality, and documentation completeness"
   - **Host Email**: your@email.com
   - **Deadline**: (select tomorrow's date)
3. Click **Create Hackathon**
4. **Expected**: Success message appears, hackathon appears in "My Hackathons" list

### Test 2: Submit a Project (Participant Flow)

1. Navigate to `http://localhost:5000/participant`
2. Fill in the form:
   - **Select Hackathon**: Choose "AI Innovation Challenge"
   - **Team Name**: "Test Team"
   - **Team Email**: test@team.com
   - **Project Name**: "Smart Calculator"
   - **Project Description**: "An advanced calculator with AI-powered features"
3. Upload files:
   - Upload `test_sample.py`
   - Upload `test_README.md`
4. Click **Submit Project**
5. **Expected**: 
   - Loading overlay appears
   - Success message after ~30-60 seconds
   - Automatic redirect to results page

### Test 3: View Results

1. After submission, you should be on the results page
2. **Expected to see**:
   - Overall score (0-10)
   - Four category scores:
     * Relevance
     * Technical Complexity
     * Creativity
     * Documentation
   - AI-generated feedback paragraph
   - Progress bars for each score
3. **Validation**: All scores should be between 0-10

### Test 4: View Leaderboard

1. Navigate to `http://localhost:5000/results?hackathon_id=1`
2. **Expected**:
   - Hackathon name displayed
   - Table showing all submissions
   - Submissions ranked by overall score
   - Top 3 have medal emojis (🥇🥈🥉)

### Test 5: Multiple Submissions

1. Create 2-3 more submissions with different content
2. Vary the quality:
   - One with minimal documentation
   - One with comprehensive README
   - One with complex code
3. **Expected**: Different scores based on content quality

### Test 6: Host Dashboard - View Submissions

1. Navigate to `http://localhost:5000/host`
2. Click **View Submissions** on your hackathon
3. **Expected**:
   - Table showing all submissions
   - Status badges (Evaluated/Pending)
   - Scores displayed
   - Action buttons work

## API Testing

### Test API Endpoints

#### 1. Get All Hackathons
```bash
curl http://localhost:5000/api/hackathons
```
Expected: JSON array of hackathons

#### 2. Get Specific Hackathon
```bash
curl http://localhost:5000/api/hackathon/1
```
Expected: JSON object with hackathon details

#### 3. Get Submissions
```bash
curl http://localhost:5000/api/hackathon/1/submissions
```
Expected: JSON array of submissions

#### 4. Get Leaderboard
```bash
curl http://localhost:5000/api/leaderboard/1
```
Expected: JSON with ranked submissions

## UI/UX Testing

### Responsive Design
- [ ] Test on desktop (1920x1080)
- [ ] Test on tablet (768x1024)
- [ ] Test on mobile (375x667)
- [ ] All elements remain usable and readable

### Browser Compatibility
- [ ] Chrome
- [ ] Firefox
- [ ] Safari
- [ ] Edge

### Visual Testing
- [ ] Logo displays correctly
- [ ] Navigation works on all pages
- [ ] Cards have proper shadows and hover effects
- [ ] Buttons change on hover
- [ ] Forms are properly aligned
- [ ] Progress bars animate correctly
- [ ] Badges display with correct colors

## Error Handling Tests

### Test 1: Missing Required Fields
1. Try to create hackathon without name
2. **Expected**: Form validation prevents submission

### Test 2: Invalid File Types
1. Try to upload .exe or .dll file
2. **Expected**: File rejected or ignored

### Test 3: No OpenAI API Key
1. Remove API key from `.env`
2. Try to submit a project
3. **Expected**: Fallback scores (5.0) assigned

### Test 4: Invalid Hackathon ID
1. Navigate to `http://localhost:5000/results?hackathon_id=999`
2. **Expected**: Error message displayed

## Performance Testing

### File Upload
- [ ] Upload single small file (< 1MB) - should be instant
- [ ] Upload multiple files - should handle correctly
- [ ] Upload .zip archive - should extract and process
- [ ] Upload 10MB+ file - should complete within reasonable time

### AI Evaluation Speed
- [ ] Small submission (< 100 lines): ~15-30 seconds
- [ ] Medium submission (100-500 lines): ~30-60 seconds
- [ ] Large submission (500+ lines): ~60-90 seconds

## Database Testing

### Data Persistence
1. Create hackathon and submissions
2. Stop the server
3. Restart the server
4. **Expected**: All data still present

### Relationships
1. Delete a hackathon (manually via database)
2. **Expected**: Related submissions also deleted (CASCADE)

## Edge Cases

### Test 1: Empty Submission
- Submit with minimal/no code
- **Expected**: Low scores, feedback mentions lack of content

### Test 2: Excellent Submission
- Submit well-documented, complex code
- **Expected**: High scores (8-10 range)

### Test 3: Same Team Multiple Submissions
- Submit multiple projects from same team
- **Expected**: All submissions tracked independently

### Test 4: Concurrent Submissions
- Have multiple people submit simultaneously
- **Expected**: All processed correctly, no conflicts

## Security Testing

### Input Validation
- [ ] SQL injection attempts in forms
- [ ] XSS attempts in text fields
- [ ] Malicious file uploads
- **Expected**: All handled safely

### File Security
- [ ] Uploaded files stored securely
- [ ] No direct access to uploaded files via URL
- [ ] File size limits enforced (16MB)

## Success Criteria

✅ All hackathon CRUD operations work
✅ File uploads handle various formats
✅ AI evaluation returns valid scores (0-10)
✅ Leaderboard ranks correctly
✅ All pages render without errors
✅ Responsive on mobile/tablet/desktop
✅ Error messages are user-friendly
✅ Loading states appear during async operations
✅ Navigation works between all pages
✅ Data persists after server restart

## Known Limitations

1. OpenAI API required (costs money for GPT-4 calls)
2. Evaluation speed depends on submission size
3. SQLite not suitable for high-concurrency production
4. File uploads limited to 16MB
5. No user authentication/authorization

## Recommended Improvements for Production

1. Add user authentication
2. Implement rate limiting
3. Use PostgreSQL or MySQL
4. Add caching for leaderboards
5. Implement WebSocket for real-time updates
6. Add email notifications
7. Create admin panel
8. Add submission deadline enforcement
9. Implement API key rotation
10. Add comprehensive logging

