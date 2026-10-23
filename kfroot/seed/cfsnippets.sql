-- ======================================================================
--  KoldFusion 4.5 example datasource: CFSNIPPETS
--  Used by the CFML Language Reference examples and the Getting Started
--  applications. All people, companies and messages here are fictional.
--  Load with sql_exec_script() into kfroot/db/cfsnippets/.
-- ======================================================================

DROP TABLE IF EXISTS Employees;
DROP TABLE IF EXISTS Departments;
DROP TABLE IF EXISTS Courses;
DROP TABLE IF EXISTS GuestBook;
DROP TABLE IF EXISTS Products;
DROP TABLE IF EXISTS Messages;
DROP TABLE IF EXISTS CourseList;
DROP TABLE IF EXISTS Parks;
DROP TABLE IF EXISTS Comments;
DROP TABLE IF EXISTS Registrations;

-- ---------------------------------------------------------------- Departments
CREATE TABLE Departments (
    Dept_ID     INTEGER PRIMARY KEY,
    Dept_Name   VARCHAR(30) NOT NULL UNIQUE,
    Location    VARCHAR(40)
);

INSERT INTO Departments (Dept_ID, Dept_Name, Location) VALUES
    (1, 'Sales',          'Boston, MA'),
    (2, 'Marketing',      'Boston, MA'),
    (3, 'Engineering',    'Cambridge, MA'),
    (4, 'Accounting',     'Burlington, MA'),
    (5, 'Administration', 'Boston, MA'),
    (6, 'Training',       'Waltham, MA');

-- ------------------------------------------------------------------ Employees
CREATE TABLE Employees (
    Emp_ID      COUNTER PRIMARY KEY,
    FirstName   VARCHAR(30) NOT NULL,
    LastName    VARCHAR(30) NOT NULL,
    Email       VARCHAR(60),
    Phone       VARCHAR(20),
    Department  VARCHAR(30),
    StartDate   DATE,
    Salary      MONEY,
    Contract    BIT DEFAULT 0
);

INSERT INTO Employees (FirstName, LastName, Email, Phone, Department, StartDate, Salary, Contract) VALUES
    ('Carol',    'Reardon',    'creardon@cfsnippets.example',  '617-555-0101', 'Sales',          #3/14/1994#,  58000, 0),
    ('Doug',     'Whitfield',  'dwhitfield@cfsnippets.example','617-555-0102', 'Sales',          #6/1/1996#,   52500, 0),
    ('Gina',     'Alvarez',    'galvarez@cfsnippets.example',  '617-555-0103', 'Sales',          #10/22/1999#, 41000, 1),
    ('Harold',   'Pemberton',  'hpemberton@cfsnippets.example','617-555-0104', 'Sales',          #1/9/1992#,   67250, 0),
    ('Ellen',    'O''Malley',  'eomalley@cfsnippets.example',  '617-555-0111', 'Marketing',      #4/18/1995#,  61000, 0),
    ('Frank',    'Ngata',      'fngata@cfsnippets.example',    '617-555-0112', 'Marketing',      #9/7/1998#,   47500, 1),
    ('Priya',    'Raman',      'praman@cfsnippets.example',    '617-555-0113', 'Marketing',      #2/2/1997#,   53800, 0),
    ('Marcus',   'Feld',       'mfeld@cfsnippets.example',     '617-555-0114', 'Marketing',      #11/15/1999#, 39500, 1),
    ('Jack',     'Lindqvist',  'jlindqvist@cfsnippets.example','617-555-0121', 'Engineering',    #8/3/1993#,   88000, 0),
    ('Beatriz',  'Okafor',     'bokafor@cfsnippets.example',   '617-555-0122', 'Engineering',    #5/20/1996#,  79500, 0),
    ('Tomasz',   'Wren',       'twren@cfsnippets.example',     '617-555-0123', 'Engineering',    #7/12/1998#,  71000, 0),
    ('Lena',     'Hartmann',   'lhartmann@cfsnippets.example', '617-555-0124', 'Engineering',    #1/4/1999#,   64000, 1),
    ('Samir',    'Haddad',     'shaddad@cfsnippets.example',   '617-555-0125', 'Engineering',    #6/28/1999#,  69500, 0),
    ('Wendy',    'Castellano', 'wcastellano@cfsnippets.example','617-555-0126','Engineering',    #12/1/1997#,  75250, 0),
    ('Ida',      'Kowalski',   'ikowalski@cfsnippets.example', '617-555-0131', 'Accounting',     #3/3/1991#,   62500, 0),
    ('Oscar',    'Brandt',     'obrandt@cfsnippets.example',   '617-555-0132', 'Accounting',     #10/10/1995#, 54000, 0),
    ('Rosa',     'Delgado',    'rdelgado@cfsnippets.example',  '617-555-0133', 'Accounting',     #2/14/1998#,  46750, 0),
    ('Hank',     'Brewster',   'hbrewster@cfsnippets.example', '617-555-0141', 'Administration', #5/5/1990#,   49000, 0),
    ('Nadia',    'Petrova',    'npetrova@cfsnippets.example',  '617-555-0142', 'Administration', #9/21/1997#,  36500, 0),
    ('Quentin',  'Achebe',     'qachebe@cfsnippets.example',   '617-555-0143', 'Administration', #4/1/1999#,   33000, 1),
    ('Yuki',     'Tanabe',     'ytanabe@cfsnippets.example',   '617-555-0151', 'Training',       #7/7/1996#,   57000, 0),
    ('Victor',   'Lemaire',    'vlemaire@cfsnippets.example',  '617-555-0152', 'Training',       #3/30/1998#,  51500, 0),
    ('Abigail',  'Moss',       'amoss@cfsnippets.example',     '617-555-0153', 'Training',       #8/16/1999#,  44000, 1),
    ('Felix',    'Ogundipe',   'fogundipe@cfsnippets.example', '617-555-0127', 'Engineering',    #9/13/1999#,  58500, 1),
    ('Martha',   'Quill',      'mquill@cfsnippets.example',    '617-555-0105', 'Sales',          #12/6/1999#,  38000, 0);

-- -------------------------------------------------------------------- Courses
CREATE TABLE Courses (
    Course_ID   COUNTER PRIMARY KEY,
    Number      VARCHAR(10) NOT NULL,
    Descript    MEMO,
    Dept_ID     INTEGER
);

INSERT INTO Courses (Number, Descript, Dept_ID) VALUES
    ('KF101', 'Fast Track to KoldFusion: CFML basics, CFQUERY and CFOUTPUT in three days.', 6),
    ('KF201', 'Advanced KoldFusion Development: custom tags, CFX, application framework and session state.', 6),
    ('KF210', 'Building E-Commerce Storefronts: shopping carts, CFMAIL receipts and secure checkout pages.', 6),
    ('SQL110', 'SQL for Web Developers: SELECT, joins, aggregates and keeping Access databases healthy.', 6),
    ('HTML100', 'HTML 4.0 and Cascading Style Sheets for both major browsers.', 6),
    ('JS150', 'Client-side JavaScript: form validation, rollovers and the DOM wars.', 3),
    ('NET220', 'Intranet Networking: TCP/IP, NT 4.0 domains and dial-up access.', 3),
    ('Y2K100', 'Year 2000 Readiness: finding two-digit years before they find you.', 3),
    ('SAL300', 'Consultative Selling on the Web.', 1),
    ('MKT210', 'Banner Ads, Click-Throughs and Measuring Eyeballs.', 2),
    ('ACC150', 'Expense Reports and the New Purchasing System.', 4);

-- ------------------------------------------------------------------ GuestBook
CREATE TABLE GuestBook (
    ID          COUNTER PRIMARY KEY,
    Name        VARCHAR(50) NOT NULL,
    Email       VARCHAR(60),
    Comments    MEMO,
    Posted      DATETIME DEFAULT NOW()
);

INSERT INTO GuestBook (Name, Email, Comments, Posted) VALUES
    ('Webmaster Dave', 'dave@homepage.example', 'First post! Welcome to the new guestbook. Please sign in and tell us how you found the site.', {ts '1999-03-02 09:15:00'}),
    ('Sk8rGrl', 'sk8rgrl@freemail.example', 'Kewl site!! Added you to my webring. Your animated GIFs rock.', {ts '1999-04-11 22:47:13'}),
    ('Bob from Ohio', NULL, 'Page looks funny in my browser. Best viewed in Netscape 4.7 at 800x600, I guess?', {ts '1999-06-30 18:02:44'}),
    ('Linda K.', 'lindak@isp.example', 'Is your web site Y2K compliant? Mine says the year is 19100.', {ts '1999-09-09 09:09:09'}),
    ('Anonymous', NULL, 'Under construction pages are so 1997. Finish the site already ;-)', {ts '1999-11-25 13:30:00'}),
    ('Millennium Mike', 'mike@partyof2000.example', 'Happy New Year from the other side! The lights stayed on, the toaster still works.', {ts '2000-01-01 00:04:51'});

-- ------------------------------------------------------------------- Products
CREATE TABLE Products (
    ProductID   COUNTER PRIMARY KEY,
    Name        VARCHAR(80) NOT NULL,
    Description MEMO,
    Price       MONEY,
    Category    VARCHAR(30),
    InStock     INTEGER DEFAULT 0
);

INSERT INTO Products (Name, Description, Price, Category, InStock) VALUES
    ('56K V.90 External Fax/Modem', 'Upgradeable flash ROM, blinking lights included. Serial cable not included.', 129.99, 'Modems', 42),
    ('33.6K Internal Modem (ISA)', 'For the budget-minded. Jumper-configurable COM port.', 49.95, 'Modems', 17),
    ('Zip 100MB Disks (3-pack)', 'Removable storage for the serious power user.', 39.99, 'Storage', 120),
    ('Zip 250MB Drive, Parallel Port', 'Back up your entire hard drive to a handful of disks.', 179.00, 'Storage', 8),
    ('1.44MB Floppy Disks (box of 25)', 'Pre-formatted, colourful labels.', 9.99, 'Storage', 300),
    ('Netscape Navigator 4.7 CD-ROM', 'The full Communicator suite with Messenger and Composer, on CD so you can skip the 18MB download.', 9.95, 'Software', 75),
    ('Web Page Builder Deluxe 3.0', 'WYSIWYG editing, frames wizard and 500 animated GIFs.', 59.95, 'Software', 23),
    ('Y2K Fix-It Toolkit', 'Scans your PC BIOS and spreadsheets for two-digit years.', 29.95, 'Software', 0),
    ('17-inch SVGA Monitor', '0.26 dot pitch, up to 1280x1024. Weighs about as much as a small car.', 349.00, 'Hardware', 5),
    ('10Base-T Network Card (PCI)', 'Plug and Play. Mostly.', 39.00, 'Hardware', 31),
    ('Ergonomic Keyboard', 'Split keys and a wrist rest for long nights of coding.', 69.99, 'Hardware', 12),
    ('Webcam (Parallel Port)', 'Live 160x120 video at up to 10 frames per second.', 99.00, 'Hardware', 3);

-- ------------------------------------------------------------------- Messages
CREATE TABLE Messages (
    MsgID       COUNTER PRIMARY KEY,
    ParentID    INTEGER DEFAULT 0,
    Subject     VARCHAR(100) NOT NULL,
    Author      VARCHAR(50),
    Body        MEMO,
    Posted      DATETIME
);

INSERT INTO Messages (ParentID, Subject, Author, Body, Posted) VALUES
    (0, 'Too few parameters. Expected 1.', 'newbie99', 'My CFQUERY against Access keeps failing with this error. The table definitely exists. Help!', {ts '1999-05-03 10:12:00'}),
    (1, 'RE: Too few parameters. Expected 1.', 'cfguru', 'That message usually means a column name is misspelled, or a text value is missing its single quotes.', {ts '1999-05-03 10:40:00'}),
    (1, 'RE: Too few parameters. Expected 1.', 'newbie99', 'Thanks, it was LastNmae instead of LastName. Doh.', {ts '1999-05-03 11:02:00'}),
    (0, 'Storing dates for Y2K', 'datadan', 'Should I be using CreateODBCDate everywhere? Some of our forms still accept two-digit years.', {ts '1999-08-19 15:25:00'}),
    (4, 'RE: Storing dates for Y2K', 'cfguru', 'Yes - pass real date objects to the database and validate four-digit years on the form side too.', {ts '1999-08-19 16:03:00'}),
    (0, 'Session variables vs. cookies', 'webweaver', 'Which is better for a shopping cart, SESSION scope or client cookies? We have two servers behind a load balancer.', {ts '1999-10-22 21:42:00'}),
    (6, 'RE: Session variables vs. cookies', 'datadan', 'With two servers use CLIENT variables in a database, or sticky sessions on the balancer.', {ts '1999-10-23 08:15:00'}),
    (0, 'CFMAIL stops after 100 messages?', 'listmom', 'Our newsletter run stalls part-way through. The spool directory fills up and nothing leaves.', {ts '2000-02-14 09:00:00'});

-- ----------------------------------------------------------------- CourseList
-- Used by the CFML Language Reference snippets (CFOUTPUT GROUP, CFINSERT, ...)
CREATE TABLE CourseList (
    Course_ID   COUNTER PRIMARY KEY,
    Dept_ID     VARCHAR(10) NOT NULL,
    CorNumber   INTEGER NOT NULL,
    CorName     VARCHAR(60) NOT NULL,
    CorLevel    VARCHAR(20),
    CorDesc     MEMO,
    LastUpdate  DATETIME
);

INSERT INTO CourseList (Dept_ID, CorNumber, CorName, CorLevel, CorDesc, LastUpdate) VALUES
    ('BIOL', 100, 'Introductory Biology',          'Basic',        'Cells, genes and the occasional frog. Lab fee applies.', {ts '1999-01-11 09:00:00'}),
    ('BIOL', 210, 'Field Botany',                  'Intermediate', 'Identify 200 plants of the northern woods before the first frost.', {ts '1999-02-03 10:30:00'}),
    ('BIOL', 340, 'Molecular Genetics',            'Advanced',     'Sequencing, recombination and why the lab smells like that.', {ts '1999-03-15 14:00:00'}),
    ('CHEM', 101, 'General Chemistry I',           'Basic',        'Stoichiometry, gas laws and safety goggles.', {ts '1998-12-01 08:15:00'}),
    ('CHEM', 230, 'Organic Chemistry',             'Intermediate', 'Carbon in all its many moods.', {ts '1999-01-20 11:45:00'}),
    ('CHEM', 410, 'Physical Chemistry',            'Advanced',     'Thermodynamics and quantum mechanics for the brave.', {ts '1999-04-02 13:00:00'}),
    ('CS',   101, 'Introduction to Programming',   'Basic',        'Variables, loops and the art of the semicolon.', {ts '1999-05-10 09:00:00'}),
    ('CS',   150, 'Web Publishing with HTML',      'Basic',        'Tables, frames and animated GIFs, done tastefully.', {ts '1999-06-01 09:00:00'}),
    ('CS',   220, 'Database Design',               'Intermediate', 'Normal forms, keys and SQL for web applications.', {ts '1999-06-14 10:00:00'}),
    ('CS',   250, 'Server-Side Web Applications',  'Intermediate', 'Building dynamic sites with CFML and an ODBC data source.', {ts '1999-07-19 10:00:00'}),
    ('CS',   330, 'Operating Systems',             'Advanced',     'Processes, threads, and why Windows NT needs a reboot.', {ts '1999-08-23 15:30:00'}),
    ('CS',   480, 'Year 2000 Remediation',         'Advanced',     'Find, fix and test two-digit year fields before midnight strikes.', {ts '1999-09-09 09:09:09'}),
    ('ENGL', 110, 'Composition and Rhetoric',      'Basic',        'Writing clearly, including e-mail and the occasional memo.', {ts '1998-11-30 12:00:00'}),
    ('ENGL', 260, 'Science Fiction Literature',    'Intermediate', 'From Wells to Gibson: imagining the networked future.', {ts '1999-02-22 16:00:00'}),
    ('ENGL', 390, 'Technical Writing',             'Advanced',     'Manuals, release notes and online help nobody reads.', {ts '1999-10-04 10:00:00'}),
    ('MATH', 120, 'College Algebra',               'Basic',        'Functions, graphs and the quadratic formula.', {ts '1998-10-05 08:00:00'}),
    ('MATH', 241, 'Calculus I',                    'Intermediate', 'Limits, derivatives and integrals of one variable.', {ts '1999-01-04 08:00:00'}),
    ('MATH', 352, 'Discrete Mathematics',          'Intermediate', 'Sets, logic, graphs and counting for computer scientists.', {ts '1999-03-01 09:30:00'}),
    ('MATH', 470, 'Cryptography',                  'Advanced',     'Ciphers old and new. Do not use XOR in production.', {ts '1999-11-11 11:11:00'}),
    ('PHYS', 105, 'Physics for Poets',             'Basic',        'The universe explained without calculus.', {ts '1999-05-05 13:30:00'}),
    ('PHYS', 315, 'Electromagnetism',              'Advanced',     'Maxwell''s equations and the occasional shock.', {ts '1999-12-31 23:59:00'});

-- ---------------------------------------------------------------------- Parks
-- Fictional parks in real states, used by the drill-down and CFOUTPUT examples.
CREATE TABLE Parks (
    ParkName    VARCHAR(60) NOT NULL,
    ParkType    VARCHAR(30),
    Region      VARCHAR(30),
    State       VARCHAR(2),
    City        VARCHAR(40)
);

INSERT INTO Parks (ParkName, ParkType, Region, State, City) VALUES
    ('Granite Hollow National Park',          'National Park',         'Northeast',       'ME', 'Bar Harbor'),
    ('Mill River National Historic Site',     'National Historic Site','Northeast',       'MA', 'Lowell'),
    ('Copper Kettle Lakeshore',               'National Lakeshore',    'Midwest',         'MI', 'Munising'),
    ('Pine Barrens National Reserve',         'National Reserve',      'Northeast',       'NJ', 'Chatsworth'),
    ('Old Forge Battlefield',                 'National Battlefield',  'Southeast',       'VA', 'Fredericksburg'),
    ('Blue Ridge Overlook Parkway',           'Parkway',               'Southeast',       'NC', 'Asheville'),
    ('Cypress Bend National Preserve',        'National Preserve',     'Southeast',       'FL', 'Everglades City'),
    ('Sea Oats National Seashore',            'National Seashore',     'Southeast',       'NC', 'Manteo'),
    ('Thunder Canyon National Park',          'National Park',         'Southwest',       'AZ', 'Page'),
    ('Painted Mesa National Monument',        'National Monument',     'Southwest',       'NM', 'Gallup'),
    ('Red Arch National Park',                'National Park',         'Southwest',       'UT', 'Moab'),
    ('Saguaro Flats National Monument',       'National Monument',     'Southwest',       'AZ', 'Tucson'),
    ('Big Sky Bison Range',                   'National Wildlife Area','Rocky Mountain',  'MT', 'Moiese'),
    ('Glacier Lily National Park',            'National Park',         'Rocky Mountain',  'MT', 'West Glacier'),
    ('Steamvent Plateau National Park',       'National Park',         'Rocky Mountain',  'WY', 'Cody'),
    ('Silver Spur Mining Camp',               'National Historic Site','Rocky Mountain',  'CO', 'Leadville'),
    ('Sandhill Crane National Wildlife Refuge','National Wildlife Area','Midwest',        'NE', 'Kearney'),
    ('Prairie Wind National Grassland',       'National Grassland',    'Midwest',         'KS', 'Elkhart'),
    ('Voyageur Waters National Park',         'National Park',         'Midwest',         'MN', 'International Falls'),
    ('Ozark Springs National Riverway',       'National River',        'Midwest',         'MO', 'Van Buren'),
    ('Iron Range Heritage Area',              'National Heritage Area','Midwest',         'MN', 'Hibbing'),
    ('Frostbite Falls State Recreation Area', 'State Park',            'Midwest',         'MN', 'Frostbite Falls'),
    ('Redwood Cathedral National Park',       'National Park',         'Pacific West',    'CA', 'Crescent City'),
    ('Fog Harbor National Seashore',          'National Seashore',     'Pacific West',    'CA', 'Point Reyes Station'),
    ('Cinder Cone Volcanic Monument',         'National Monument',     'Pacific West',    'CA', 'Mineral'),
    ('Rainshadow National Park',              'National Park',         'Pacific West',    'WA', 'Port Angeles'),
    ('Crater Mirror National Park',           'National Park',         'Pacific West',    'OR', 'Klamath Falls'),
    ('Lava Tube National Monument',           'National Monument',     'Pacific West',    'ID', 'Arco'),
    ('Kilauea Steam National Park',           'National Park',         'Pacific West',    'HI', 'Volcano'),
    ('Northern Lights National Preserve',     'National Preserve',     'Alaska',          'AK', 'Fairbanks'),
    ('Tidewater Glacier National Park',       'National Park',         'Alaska',          'AK', 'Seward'),
    ('Caribou Crossing Wilderness',           'National Preserve',     'Alaska',          'AK', 'Kotzebue'),
    ('Liberty Bell Independence Park',        'National Historical Park','Northeast',     'PA', 'Philadelphia'),
    ('Canal Towpath National Park',           'National Historical Park','Northeast',     'MD', 'Hagerstown'),
    ('Bayou Lafitte Heritage Park',           'National Historical Park','Southeast',     'LA', 'New Orleans'),
    ('Smoky Hollow National Park',            'National Park',         'Southeast',       'TN', 'Gatlinburg'),
    ('Mammoth Echo Cave National Park',       'National Park',         'Southeast',       'KY', 'Cave City'),
    ('Big Bend of the Rio National Park',     'National Park',         'Southwest',       'TX', 'Alpine'),
    ('Gypsum Dunes National Monument',        'National Monument',     'Southwest',       'NM', 'Alamogordo'),
    ('Hot Springs Bathhouse Row',             'National Park',         'Southwest',       'AR', 'Hot Springs'),
    ('Badlands Fossil Beds',                  'National Monument',     'Midwest',         'SD', 'Wall'),
    ('Dune Ridge National Lakeshore',         'National Lakeshore',    'Midwest',         'IN', 'Porter');

-- ------------------------------------------------------------------- Comments
-- Feedback messages for the CFINSERT / CFUPDATE / CFMAIL examples.
CREATE TABLE Comments (
    CommentID   COUNTER PRIMARY KEY,
    Email       VARCHAR(60),
    FromUser    VARCHAR(50),
    Subject     VARCHAR(100),
    CommtType   VARCHAR(20),
    MessText    MEMO,
    Posted      DATETIME,
    Processed   BIT DEFAULT 0
);

INSERT INTO Comments (Email, FromUser, Subject, CommtType, MessText, Posted, Processed) VALUES
    ('jdoe@dialup.example',   'Jane Doe',     'Love the new site',       'Praise',     'The frames load fast even on my 28.8 modem. Great job!', {ts '1999-04-01 09:12:00'}, 1),
    ('webguy@isp.example',    'Web Guy',      'Broken link on home page','Bug Report', 'The "What''s New" link points to a page that is under construction.', {ts '1999-06-17 14:30:00'}, 1),
    ('pat@corp.example',      'Pat Kowal',    'Y2K question',            'Question',   'Will your online catalog still work on January 1, 2000?', {ts '1999-09-30 16:45:00'}, 0),
    ('surfer@freemail.example','Net Surfer',  'Please add a guestbook',  'Suggestion', 'Every good site has a guestbook and a hit counter. Just saying.', {ts '1999-11-02 20:05:00'}, 0),
    ('chris@school.example',  'Chris Lee',    'Course list is great',    'Praise',     'Found the database course I needed in thirty seconds.', {ts '2000-01-03 08:00:00'}, 0);

-- -------------------------------------------------------------- Registrations
-- Filled in by /CFDOCS/registration.cfm (the product registration card).
CREATE TABLE Registrations (
    RegID       COUNTER PRIMARY KEY,
    FirstName   VARCHAR(30) NOT NULL,
    LastName    VARCHAR(30) NOT NULL,
    Company     VARCHAR(60),
    Email       VARCHAR(60),
    Platform    VARCHAR(40),
    WebServer   VARCHAR(40),
    Modem       VARCHAR(30),
    HeardFrom   VARCHAR(40),
    Y2KReady    BIT DEFAULT 0,
    Newsletter  BIT DEFAULT 0,
    Comments    MEMO,
    Registered  DATETIME
);

INSERT INTO Registrations (FirstName, LastName, Company, Email, Platform, WebServer, Modem, HeardFrom, Y2KReady, Newsletter, Comments, Registered) VALUES
    ('Gil', 'Bates', 'Macrohard Corp.', 'gil@macrohard.example', 'Windows NT 4.0 SP4', 'IIS 4.0', 'T1', 'Trade magazine', 1, 1, 'Very nice. We may buy you.', {ts '1999-11-15 10:00:00'});
