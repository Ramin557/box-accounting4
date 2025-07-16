# Accounting Dashboard for Box Manufacturing

## Overview

This is a Flask-based accounting and inventory management system specifically designed for a box manufacturing business. The application tracks materials, products, sales, expenses, and workers with Persian/Farsi language support and Jalali calendar integration.

## User Preferences

Preferred communication style: Simple, everyday language.
Languages: Persian/Farsi interface with RTL layout

## Recent Changes (January 2025)

- **2025-07-16:** Fixed database connection parsing error - app now handles missing DATABASE_URL gracefully
- **2025-07-16:** Installed missing gunicorn package for proper application deployment
- **2025-07-16:** Updated database configuration to use SQLite fallback when PostgreSQL unavailable
- **2025-07-16:** Application successfully running on port 5000 with all features functional
- **2025-07-16:** Comprehensive code cleanup and optimization:
  - Removed unused files: backup_cli.py, scheduler.py, attached_assets folder
  - Cleaned up dependencies: removed 7 unused packages (email-validator, flask-dance, flask-login, oauthlib, pyjwt, twilio, schedule)
  - Removed cache files and temporary files
  - Verified all remaining code is functional and necessary
- Fixed template URL routing issues causing application startup failures
- Resolved circular import problems between app.py, routes.py, and models.py
- Fixed JSON serialization issues in reports page for database Row objects
- Successfully tested all form submissions and data persistence
- Verified financial calculations working correctly with sample data
- Application now fully functional with Persian interface and database integration

## System Architecture

### Backend Architecture
- **Framework**: Flask web framework with SQLAlchemy ORM
- **Database**: SQLite for development (configurable via DATABASE_URL environment variable)
- **Session Management**: Flask sessions with secret key configuration
- **Middleware**: ProxyFix for handling reverse proxy headers

### Frontend Architecture
- **Template Engine**: Jinja2 templates with Bootstrap 5 RTL support
- **UI Framework**: Bootstrap 5 with RTL (Right-to-Left) layout for Persian language
- **Styling**: Custom CSS with dark theme and Persian typography (Tahoma font)
- **JavaScript**: Vanilla JavaScript for form validation and chart rendering
- **Charts**: Chart.js library for financial data visualization

### Database Schema
The application uses five main entities:
- **Materials**: Raw materials with cost tracking and date stamps
- **Products**: Manufactured products with unit costs and quantities
- **Sales**: Sales records with pricing and revenue calculation
- **Expenses**: General business expenses (referenced but model not shown)
- **Workers**: Employee wage tracking (referenced but model not shown)

## Key Components

### Models (models.py)
- **Material Model**: Tracks raw material purchases with cost and date
- **Product Model**: Manages manufactured products with calculated total costs
- **Sale Model**: Records sales transactions with automatic revenue calculation
- Each model includes timestamp tracking and Persian string representation

### Routes (routes.py)
- **Dashboard Route**: Main interface for data entry and overview
- **Form Handling**: Processes material, product, and sales submissions
- **Data Validation**: Validates dates, numeric values, and required fields
- **Flash Messaging**: Provides user feedback in Persian

### Utilities (utils.py)
- **Date Conversion**: Bidirectional conversion between Gregorian and Jalali calendars
- **PDF Export**: ReportLab integration for generating financial reports
- **Data Validation**: Date format validation and sanitization

### Templates
- **Base Template**: Common layout with navigation and Bootstrap RTL
- **Dashboard**: Main data entry interface with forms and tables
- **Reports**: Financial reporting with charts and filtering capabilities

## Data Flow

1. **Data Entry**: Users input materials, products, and sales through dashboard forms
2. **Validation**: Server-side validation ensures data integrity and proper formatting
3. **Storage**: Data is persisted to SQLite database with automatic timestamp tracking
4. **Display**: Information is retrieved and displayed with Jalali date conversion
5. **Reporting**: Financial calculations and chart generation for business insights

## External Dependencies

### Python Packages
- **Flask**: Web framework and routing
- **SQLAlchemy**: Database ORM and migrations
- **jdatetime**: Persian calendar support and date conversion
- **ReportLab**: PDF generation for reports
- **Werkzeug**: WSGI utilities and proxy handling

### Frontend Libraries
- **Bootstrap 5 RTL**: UI framework with right-to-left language support
- **Font Awesome**: Icon library for enhanced UI
- **Chart.js**: JavaScript charting library for financial visualizations

### Development Tools
- **Flask Debug Mode**: Enabled for development environment
- **Logging**: Configured for debugging and monitoring

## Deployment Strategy

### Environment Configuration
- **Database URL**: Configurable via environment variable (defaults to SQLite)
- **Session Secret**: Configurable secret key for session management
- **Debug Mode**: Enabled in development, should be disabled in production

### Database Management
- **Auto-creation**: Tables are automatically created on application startup
- **Connection Pooling**: Configured with connection recycling and health checks
- **Migration Support**: Uses SQLAlchemy's declarative base for schema management

### Static Assets
- **CSS**: Custom styling for Persian/RTL layout and dark theme
- **JavaScript**: Client-side validation and interactive features
- **Font Support**: Tahoma font family for proper Persian text rendering

### Production Considerations
- Environment variables should be properly configured for production database
- Session secret should be set to a secure random value
- Debug mode should be disabled
- Consider using a production WSGI server instead of Flask's development server