# Task: Add Settings functionality to Admin & User Dashboards

## Steps
- [x] 1. Add URL routes for admin_settings and user_settings in `users/urls.py`
- [x] 2. Create `users/templates/users/admin_settings.html`
- [x] 3. Create `users/templates/users/user_settings.html`
- [x] 4. Wire Settings sidebar link in `users/templates/users/admin_dashboard.html`
- [x] 5. Wire Settings sidebar link in `users/templates/users/user_dashboard.html`
- [x] 6. Update dashboard views to pass `profile` context
- [x] 7. Update sidebar footers to show uploaded avatar image
- [x] 9. Add function to Profile tab — wired as SPA tab with profile card + activity panel
- [x] 10. Added comprehensive settings options to Settings tab: theme customization (colors + presets), layout preferences (sidebar, density, card layout, animations), notification preferences (email, push, promo, auto-refresh), data & privacy (show email, clear local data, export favorites), account details
- [x] 11. Added JavaScript functions for all settings: applyTheme(), applyPreset(), resetTheme(), toggleSidebarPreference(), applyDisplayDensity(), applyCardLayout(), toggleAnimations(), saveNotifPrefs(), applyRefreshInterval(), savePrivacyPrefs(), clearLocalData(), exportFavorites()
- [x] 12. Settings changes persist via localStorage and apply globally across the system
- [x] 13. Verified Django app boots with `python manage.py check`
- [x] 14. Fixed sidebar Settings links in manage_users, manage_items, edit_user templates
- [x] 15. Added notification dropdowns to manage_users, manage_items templates
