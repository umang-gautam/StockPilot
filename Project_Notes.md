Project Name: StockPilot

Tagline:
Smart Inventory. Smarter Business.

Tech Stack:
- Python
- Flask
- MySQL
- HTML
- CSS
- JavaScript
- Chart.js

Goal:
To build an inventory management system for my father's sanitary business using real business data.

Started On:
10 July 2026

Day 2

- Created professional Flask project structure.
- Learned templates and static folders.
- Connected HTML with CSS.
- Created first landing page of StockPilot.
- Understood render_template() and url_for().

Day 3 onwards – Database & Backend Development

- Designed the MySQL database for StockPilot.
- Created the main products table to store:
  - Product Code
  - Product Name
  - MRP
  - Current Stock
  - Minimum Stock
  - Brand ID
  - User ID
- Created stock_history to maintain a record of stock movements.
- Connected the Flask application with MySQL using mysql-connector-python.
- Tested database connectivity and SQL queries from Flask.
- Learned how Flask routes communicate with the MySQL database.
- Implemented INSERT, SELECT and UPDATE operations.

--------------------------------------------------

Product Management

- Created the Products section of StockPilot.
- Implemented product search using Product Code and Product Name.
- Created Add Product functionality.
- Added fields for:
  - Product Code
  - Product Name
  - MRP
  - Current Stock
  - Minimum Stock
  - Brand ID
- Implemented View Products functionality.
- Implemented Edit Product functionality.
- Added product information validation and database updates.
- Created a separate product search page for quickly finding products.

--------------------------------------------------

Excel Import System

- Added Excel import functionality to StockPilot.
- Integrated Pandas and OpenPyXL for reading Excel files.
- Added support for .xlsx files.
- Added support for .xlsb files using pyxlsb.
- Implemented automatic sheet detection.
- If multiple sheets are present, the application looks for the MRP sheet.
- Added flexible column detection for different Excel column names.
- Mapped possible Excel columns such as:
  - Material / Product Code / SKU / Item Code
  - Description / Product Name / Item Name / Name
  - MRP / Price / Selling Price
- Imported the existing sanitary shop product data into MySQL.
- Successfully worked with approximately 12,500+ products.
- Imported product data initially with current stock and minimum stock values set appropriately for later inventory management.

--------------------------------------------------

Authentication System

- Created user signup functionality.
- Created login functionality.
- Added session-based authentication using Flask sessions.
- Added logout functionality.
- Connected logged-in user information with the dashboard.
- Added shop/owner information to the dashboard.
- Implemented protected application pages so the user must be logged in.
- Fixed navigation and login redirection issues during development.

--------------------------------------------------

Dashboard

- Created the main StockPilot dashboard.
- Added personalized greeting for the logged-in user.
- Added shop/business name display.
- Added dashboard summary cards:
  - Total Products
  - Low Stock Items
  - Today's Stock In
  - Today's Stock Out
- Connected dashboard statistics to live MySQL data.
- Added navigation cards for:
  - Products
  - Inventory
  - Settings
- Implemented SQL queries for calculating dashboard statistics.
- Added SUM and COUNT queries for inventory statistics.
- Added low-stock calculation based on Minimum Stock.
- Added today's Stock In and Stock Out calculations using stock history.
- Fixed a dashboard routing issue where the wrong dashboard was being displayed.
- Added no-cache response headers to prevent old dashboard pages from appearing after login/logout.

--------------------------------------------------

Inventory Management

- Created the Inventory section.
- Added Stock In functionality.
- Added Stock Out functionality.
- Stock In increases the current stock of a selected product.
- Stock Out decreases the current stock of a selected product.
- Added validation to prevent Stock Out quantity from exceeding available stock.
- Added success/error messages for inventory operations.
- Connected inventory changes directly to the products table.

--------------------------------------------------

Stock History

- Created the stock_history table and connected it with inventory operations.
- Every Stock In operation creates a history record.
- Every Stock Out operation creates a history record.
- History records contain:
  - Product Code
  - Product Name
  - Action (IN/OUT)
  - Quantity
  - Date
  - Time
- Created the Stock History page.
- Used database records to maintain a chronological history of stock movement.
- Connected stock history with dashboard Stock In and Stock Out statistics.

--------------------------------------------------

Low Stock Management

- Added Minimum Stock to each product.
- Implemented low-stock detection using:
  
  Current Stock <= Minimum Stock

- Added Low Stock Items count to the dashboard.
- Created the Low Stock page to identify products requiring attention.
- Tested the low-stock calculation with actual product data.

--------------------------------------------------

Settings

- Created the Settings section.
- Added account/settings navigation.
- Created Change Password functionality.
- Added settings-related pages and navigation.
- Connected settings pages with the logged-in user's session.

--------------------------------------------------

Employee Management

- Added Employee Management functionality.
- Created employee management interface.
- Added employee-related templates and backend routes.
- Worked on separating employee access from owner/admin access.
- Tested navigation and dashboard behavior for different users.
- Fixed issues where an employee dashboard was being displayed instead of the expected owner dashboard.

--------------------------------------------------

UI/UX Development

- Reworked the overall StockPilot interface to make it more professional and consistent.
- Created a common navigation bar across application pages.
- Added StockPilot branding with the rocket logo.
- Added personalized user information in the navigation bar.
- Added consistent Dashboard and Logout navigation.
- Designed cards, buttons, forms and sections with a clean modern layout.
- Added rounded cards, shadows and spacing for a professional dashboard appearance.
- Created a consistent color scheme using dark navy, white and light gray.
- Improved form layouts for product and inventory pages.
- Added responsive spacing and cleaner page layouts.
- Fixed pages that were accidentally loading without the CSS stylesheet.
- Fixed navigation button styling.
- Fixed Logout link styling and hover behavior.
- Ensured all major pages use the common style.css file.

--------------------------------------------------

Bug Fixes & Debugging

- Fixed Flask TemplateNotFound errors caused by template/file changes.
- Fixed login and dashboard redirection issues.
- Fixed incorrect dashboard loading for users.
- Fixed browser caching problems after authentication changes.
- Added no-cache headers to important Flask responses.
- Fixed MySQL authentication/connection errors by correcting database credentials.
- Tested Flask application repeatedly through the local development server.
- Checked terminal logs for HTTP requests and application errors.
- Fixed missing template and routing issues.
- Tested pages individually after major changes.

--------------------------------------------------

Final V1 Features

StockPilot V1 currently includes:

- User Signup
- User Login
- Logout
- Personalized Dashboard
- Product Management
- Add Product
- Search Product
- View Products
- Edit Product
- Excel Product Import
- Inventory Management
- Stock In
- Stock Out
- Stock History
- Low Stock Detection
- Settings
- Change Password
- Employee Management
- Dashboard Statistics
- MySQL Database Integration
- Professional UI/UX
- Flask Backend
- Session-based Authentication

--------------------------------------------------

V1 Status

- StockPilot V1 development is complete.
- All major planned V1 modules have been implemented and tested locally.
- The application is currently running successfully on the local Flask development server.
- The next major phase is deployment so that StockPilot can be accessed outside the local computer.

--------------------------------------------------

Deployment Preparation

- Created requirements.txt containing the project's Python dependencies.
- Added Gunicorn as the production WSGI server.
- Generated the requirements file using pip freeze.
- Reviewed the project structure before deployment.
- Reviewed unnecessary templates and removed unused files.
- Prepared the application for deployment.
- Identified database credentials and configuration that need to be secured before pushing the project to GitHub.
- Next step: secure configuration, GitHub setup, production MySQL database, deployment and live testing.

--------------------------------------------------

Current Project Architecture

StockPilot currently follows a Flask-based web application structure:

StockPilot/
│
├── app.py
├── requirements.txt
├── static/
│   └── css/
│       └── style.css
│
├── templates/
│   ├── login.html
│   ├── signup.html
│   ├── dashboard.html
│   ├── products.html
│   ├── add_product.html
│   ├── edit_product.html
│   ├── view_products.html
│   ├── search_product.html
│   ├── import_excel.html
│   ├── inventory.html
│   ├── stock_in.html
│   ├── stock_out.html
│   ├── stock_history.html
│   ├── low_stock.html
│   ├── settings.html
│   ├── change_password.html
│   └── employee_management.html
│
└── uploads/

--------------------------------------------------

Important Development Learning

During the development of StockPilot, I learned:

- Flask application structure
- Flask routing
- Jinja2 templates
- Static files and CSS integration
- HTML forms and POST requests
- Session-based authentication
- MySQL connectivity with Python
- SQL CRUD operations
- Database-driven dashboards
- Pandas and OpenPyXL for Excel processing
- File uploads in Flask
- Inventory management logic
- SQL aggregation using COUNT and SUM
- Stock validation
- Maintaining transaction history
- Debugging Flask applications
- Handling template and routing errors
- Preparing a Flask application for production deployment

--------------------------------------------------

Next Phase

1. Secure database credentials and secret keys.
2. Push the project to GitHub.
3. Set up a production MySQL database.
4. Connect the deployed application to the production database.
5. Deploy the Flask application.
6. Test all major features on the live website.
7. Fix any deployment-specific issues.
8. Document the final architecture and deployment process.
9. Prepare the final project report and presentation.
10. Add future improvements after V1 is stable.

--------------------------------------------------