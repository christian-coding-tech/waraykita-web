# TODO: Enhanced Authentication & Animations

## Steps
- [x] 1. Add AJAX availability-check endpoints (`check_username`, `check_email`) in `views.py`
- [x] 2. Add URL routes for new endpoints in `urls.py`
- [x] 3. Restructure registration form into 3 steps in `login.html`
- [x] 4. Add system-wide loading overlay to `login.html`, `user_dashboard.html`, `admin_dashboard.html`
- [x] 5. Update `login.js` with step logic, validation, AJAX checks, password strength, loading
- [x] 6. Update `login.css` with step transitions, progress bar, validation states, loading overlay
- [x] 7. Add loading overlay styles to `dashboard.css`
- [x] 8. Verify server runs and features work

# TODO: Admin Dashboard Charts

## Steps
- [x] 1. Add chart analytics data to `admin_dashboard_view` context in `views.py`
- [x] 2. Add Chart.js CDN to `admin_dashboard.html`
- [x] 3. Add chart panels (roles pie, product color bar, user status donut, stock bar) to `admin_dashboard.html`
- [x] 4. Add `renderCharts()` JS script to `admin_dashboard.html`
- [x] 5. Add chart container styles to `dashboard.css`
- [x] 6. Verify Django system check passes and context variables match template
