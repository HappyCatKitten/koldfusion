-- ======================================================================
--  KoldFusion 4.5 example datasource: EXAMPLEAPP
--  The "Company Example App" intranet: staff directory, departments,
--  training course catalog and a company news page. All people,
--  companies and headlines here are fictional.
--  Load with sql_exec_script() into kfroot/db/exampleapp/.
-- ======================================================================

DROP TABLE IF EXISTS Employees;
DROP TABLE IF EXISTS Departments;
DROP TABLE IF EXISTS Courses;
DROP TABLE IF EXISTS News;

-- ---------------------------------------------------------------- Departments
CREATE TABLE Departments (
    Dept_ID     COUNTER PRIMARY KEY,
    Dept_Name   VARCHAR(40) NOT NULL UNIQUE,
    Location    VARCHAR(40),
    Extension   VARCHAR(10)
);

INSERT INTO Departments (Dept_Name, Location, Extension) VALUES
    ('Executive',            'Building A, 4th Floor', '4000'),
    ('Sales',                'Building A, 2nd Floor', '4200'),
    ('Marketing',            'Building A, 3rd Floor', '4300'),
    ('Information Services', 'Building B, Basement',  '4500'),
    ('Human Resources',      'Building A, 1st Floor', '4100'),
    ('Customer Support',     'Building B, 1st Floor', '4600');

-- ------------------------------------------------------------------ Employees
CREATE TABLE Employees (
    Emp_ID      COUNTER PRIMARY KEY,
    FirstName   VARCHAR(30) NOT NULL,
    LastName    VARCHAR(30) NOT NULL,
    Title       VARCHAR(50),
    Dept_ID     INTEGER,
    Email       VARCHAR(60),
    Phone       VARCHAR(20),
    HireDate    DATE,
    Salary      MONEY,
    FullTime    BIT DEFAULT 1
);

INSERT INTO Employees (FirstName, LastName, Title, Dept_ID, Email, Phone, HireDate, Salary, FullTime) VALUES
    ('Margaret', 'Holloway',  'President and CEO',              1, 'mholloway@example.com',  'x4001', #2/1/1988#,   185000, 1),
    ('Charles',  'Ebbing',    'Chief Financial Officer',        1, 'cebbing@example.com',    'x4002', #6/15/1990#,  142000, 1),
    ('Diane',    'Fairbanks', 'Executive Assistant',            1, 'dfairbanks@example.com', 'x4003', #9/9/1996#,   41000,  1),
    ('Raymond',  'Szabo',     'VP of Sales',                    2, 'rszabo@example.com',     'x4201', #4/4/1991#,   118000, 1),
    ('Teresa',   'Lund',      'Account Executive',              2, 'tlund@example.com',      'x4202', #11/2/1995#,  64000,  1),
    ('Kevin',    'Marsh',     'Account Executive',              2, 'kmarsh@example.com',     'x4203', #3/17/1998#,  58500,  1),
    ('Alicia',   'Ferreira',  'Inside Sales Representative',    2, 'aferreira@example.com',  'x4204', #8/30/1999#,  36000,  0),
    ('Gordon',   'Pike',      'Marketing Director',             3, 'gpike@example.com',      'x4301', #1/12/1993#,  96000,  1),
    ('Joanna',   'Wexler',    'Web Content Producer',           3, 'jwexler@example.com',    'x4302', #5/24/1999#,  47000,  1),
    ('Leonard',  'Ashby',     'Director of Information Services', 4, 'lashby@example.com',   'x4501', #7/1/1992#,   104000, 1),
    ('Sunita',   'Bhatt',     'KoldFusion Developer',           4, 'sbhatt@example.com',     'x4502', #2/8/1998#,   72000,  1),
    ('Derek',    'Olsen',     'Network Administrator',          4, 'dolsen@example.com',     'x4503', #10/19/1996#, 66000,  1),
    ('Mei',      'Huang',     'Database Administrator',         4, 'mhuang@example.com',     'x4504', #6/7/1997#,   74500,  1),
    ('Carlos',   'Ibarra',    'Help Desk Technician',           4, 'cibarra@example.com',    'x4505', #11/29/1999#, 34000,  0),
    ('Patricia', 'Doyle',     'HR Manager',                     5, 'pdoyle@example.com',     'x4101', #3/3/1994#,   69000,  1),
    ('Simon',    'Achterberg','Benefits Coordinator',           5, 'sachterberg@example.com','x4102', #8/8/1997#,   43500,  1),
    ('Renee',    'Valois',    'Support Team Lead',              6, 'rvalois@example.com',    'x4601', #12/12/1995#, 55000,  1),
    ('Omar',     'Siddiqui',  'Support Specialist',             6, 'osiddiqui@example.com',  'x4602', #4/26/1999#,  38500,  1),
    ('Bethany',  'Crowe',     'Support Specialist',             6, 'bcrowe@example.com',     'x4603', #1/18/2000#,  37000,  0);

-- -------------------------------------------------------------------- Courses
CREATE TABLE Courses (
    Course_ID   COUNTER PRIMARY KEY,
    CourseNum   VARCHAR(10) NOT NULL UNIQUE,
    Title       VARCHAR(80) NOT NULL,
    Description MEMO,
    Dept_ID     INTEGER,
    Hours       INTEGER,
    StartDate   DATE
);

INSERT INTO Courses (CourseNum, Title, Description, Dept_ID, Hours, StartDate) VALUES
    ('IS-101', 'Getting Around the Intranet',         'Bookmarks, the staff directory, and finding the cafeteria menu online.', 4, 2, #1/10/2000#),
    ('IS-110', 'E-mail Etiquette',                    'Reply-all considered harmful. Signature files under four lines.',       4, 2, #1/17/2000#),
    ('IS-210', 'Building Pages with KoldFusion',      'CFQUERY, CFOUTPUT and CFIF for departmental web pages.',                4, 16, #2/7/2000#),
    ('IS-220', 'Spreadsheets for Managers',           'Formulas, charts and pivot tables for budget season.',                  4, 8, #2/21/2000#),
    ('SL-200', 'Selling Solutions, Not Boxes',        'Consultative sales techniques for the networked economy.',             2, 12, #3/6/2000#),
    ('MK-150', 'Your Brand on the Web',               'Logos, colour palettes and why the home page should load in under 30 seconds on a modem.', 3, 6, #3/13/2000#),
    ('HR-100', 'New Employee Orientation',            'Benefits, policies, and a tour of both buildings.',                     5, 4, #1/3/2000#),
    ('CS-120', 'Handling Difficult Calls',            'Listening, de-escalation and when to hand off to a team lead.',        6, 6, #2/14/2000#);

-- ----------------------------------------------------------------------- News
CREATE TABLE News (
    News_ID     COUNTER PRIMARY KEY,
    Headline    VARCHAR(120) NOT NULL,
    Story       MEMO,
    Category    VARCHAR(30),
    Author      VARCHAR(50),
    Posted      DATETIME
);

INSERT INTO News (Headline, Story, Category, Author, Posted) VALUES
    ('Intranet Goes Live on KoldFusion 4.5',
     'The new company intranet is up. Staff directory, course sign-ups and this news page now run from a single server in Building B.',
     'Company', 'Joanna Wexler', {ts '1999-06-01 09:00:00'}),
    ('Dial-Up Pool Expanded to 48 Lines',
     'Information Services has added 24 new 56K lines for remote staff. Busy signals after 8pm should now be rare.',
     'Technology', 'Derek Olsen', {ts '1999-07-19 14:30:00'}),
    ('Y2K Testing Weekend Scheduled for October',
     'All servers, PCs and the phone system will be rolled forward to 31 December 1999 and watched through midnight. Please log off before you leave Friday.',
     'Y2K', 'Leonard Ashby', {ts '1999-09-13 10:15:00'}),
    ('Analysts Debate Whether Online Bookstores Can Ever Turn a Profit',
     'Industry watchers remain split on web-only retailers, citing thin margins and expensive warehouses. Our sales team says customers still want a catalog they can hold.',
     'Industry', 'Gordon Pike', {ts '1999-10-04 08:45:00'}),
    ('Company Network Declared Year 2000 Ready',
     'The October test weekend found three spreadsheets and one fax machine with two-digit years. All have been fixed or retired.',
     'Y2K', 'Leonard Ashby', {ts '1999-10-25 16:00:00'}),
    ('New Web Browsers Arrive on Every Desktop',
     'Desktop images now ship with the latest browser versions. Pages built to the HTML 4.0 standard should look the same in both.',
     'Technology', 'Sunita Bhatt', {ts '1999-11-08 11:20:00'}),
    ('Holiday Party Moves Online - RSVP Through the Intranet',
     'Sign up for the December 17 party with the new RSVP form. Yes, it uses CFMAIL to send your confirmation.',
     'Company', 'Patricia Doyle', {ts '1999-11-22 12:00:00'}),
    ('Midnight Passes Quietly; Systems Report Normal',
     'The overnight crew reports all systems normal after the date rollover. The coffee machine, which was never tested, also survived.',
     'Y2K', 'Derek Olsen', {ts '2000-01-01 00:30:00'}),
    ('Leap Day Check: February 29, 2000 Is Real',
     'Some older software forgets that 2000 is a leap year. Please report any program that skips straight to March 1.',
     'Y2K', 'Mei Huang', {ts '2000-02-28 09:00:00'}),
    ('Wireless Networking Trial Begins in Conference Rooms',
     'A small pilot of 11 Mbps wireless access points is starting in Building A. Laptop PC cards are available from the help desk.',
     'Technology', 'Derek Olsen', {ts '2000-03-20 13:10:00'}),
    ('Tech Stocks Slide After a Record Run',
     'Technology shares fell sharply this week after months of gains. Our 401(k) provider reminds everyone to think long term.',
     'Industry', 'Charles Ebbing', {ts '2000-04-17 17:45:00'}),
    ('Customer Support Launches Web-Based Trouble Tickets',
     'Customers can now open and track support cases from our public site, cutting average phone hold time in half.',
     'Company', 'Renee Valois', {ts '2000-05-08 10:00:00'});
