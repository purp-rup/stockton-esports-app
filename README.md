# Esports Management Tool

## Highlights
- **Centralized Platform**: Combines scheduling, communication, and management features under one tool to reduce disorganization.  
- **Visual Calendar**: Customizable alerts for matches, practices, and community events.  
- **Team Management**: Game Managers can create and manage rosters, schedules, and match reminders.  
- **VOD Review**: Upload and annotate match recordings to provide structured feedback for players.  
- **Analytics Dashboard**: Administrators can track team data, event statistics, and community engagement.  
- **Free & Tailored**: Unlike existing paid platforms (e.g., RallyCry, LeagueSpot), this tool is designed specifically for Stockton Esports and provided at no cost.  

## Overview
The Esports Management Tool is a software application developed for the Stockton University Esports program. The project addresses long-standing organizational and communication challenges caused by reliance on fragmented tools like Discord, Google Drive, and Google Calendar.  

This solution focuses on both the **competitive** and **community** sides of Stockton Esports:  
- On the **competitive side**, it streamlines logistical tasks such as scheduling, team management, and match preparation, helping Game Managers and players stay aligned.  
- On the **community side**, it enhances engagement through better event visibility, attendance tracking, and customizable notifications.  

By integrating existing workflows into a single, intuitive platform, the tool reduces missed deadlines, improves coordination, and strengthens both team and community operations.  

### Design
This application was developed using the Flask framework, making use of HTML, Python, and MySQL.

### Dashboard preview
- After logging in, visit `/dashboard` (linked from the navigation bar) to see the current implementation of the Stockton Esports landing experience.
- The route is registered in `EsportsManagementTool/__init__.py` and queries both the signed-in user and upcoming events so the page populates with live data from MySQL.
- Styling assets live in `EsportsManagementTool/static/dashboard.css`, which mirrors the latest layout assets we have locally. Once the official Figma export is available, replace the placeholder styles in that file with the production-ready rules.

### Required MySQL tables
The Flask routes interact with the `users` and `generalevents` tables already present in the production database. Make sure your local environment mirrors the structure below so column lookups (like the dashboard's member-since date) resolve correctly.

```sql
CREATE TABLE IF NOT EXISTS users (
    id INT NOT NULL AUTO_INCREMENT,
    firstname VARCHAR(20) NOT NULL,
    lastname VARCHAR(20) NOT NULL,
    username VARCHAR(20) NOT NULL,
    email VARCHAR(100) NOT NULL,
    date TIMESTAMP NULL DEFAULT CURRENT_TIMESTAMP,
    password VARCHAR(255) NOT NULL,
    is_verified TINYINT(1) DEFAULT 0,
    verification_token VARCHAR(255) DEFAULT NULL,
    token_expiry DATETIME DEFAULT NULL,
    PRIMARY KEY (id),
    UNIQUE KEY uq_users_username (username)
);

CREATE TABLE IF NOT EXISTS generalevents (
    EventID INT NOT NULL AUTO_INCREMENT,
    EventName VARCHAR(60) NOT NULL,
    Date DATE NOT NULL,
    StartTime TIME NOT NULL,
    EndTime TIME NOT NULL,
    Description VARCHAR(250) NOT NULL,
    CreatedAt DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
    PRIMARY KEY (EventID)
);
```

Both tables rely on the connection settings defined in `EsportsManagementTool/__init__.py`. Run the statements above (after setting your `MYSQL_*` environment variables) before launching the Flask app, or adjust them to match your existing data types and lengths.

## Authors

This project was developed by [Jackson Campbell](https://github.com/JCamp74), [Rachel Hussmann](https://github.com/violetann894), [Hayden Seiberlich](https://github.com/seiberlichiamo), [Alexander DeSilvio](https://github.com/Alakazam936), and [Andrew Miraglia](https://github.com/purp-rup).
