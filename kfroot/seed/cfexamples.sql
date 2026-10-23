-- ======================================================================
--  KoldFusion 4.5 example datasource: CFEXAMPLES
--  Backs the Example Applications under /CFDOCS/exampleapp/:
--    * GlobalCorp intranet  (directory, forum, catalog, scheduler, news)
--    * National Parks drill-down
--    * CFGRID / CFTREE widget demo
--  GlobalCorp Industries, its people, products and headlines are all
--  fictional. Park names are real places; the blurbs are original.
-- ======================================================================

DROP TABLE IF EXISTS Departments;
DROP TABLE IF EXISTS Employees;
DROP TABLE IF EXISTS Users;
DROP TABLE IF EXISTS Topics;
DROP TABLE IF EXISTS Messages;
DROP TABLE IF EXISTS Categories;
DROP TABLE IF EXISTS Products;
DROP TABLE IF EXISTS Orders;
DROP TABLE IF EXISTS OrderItems;
DROP TABLE IF EXISTS Rooms;
DROP TABLE IF EXISTS Bookings;
DROP TABLE IF EXISTS Headlines;
DROP TABLE IF EXISTS Quotes;
DROP TABLE IF EXISTS Parks;
DROP TABLE IF EXISTS Vendors;

-- ---------------------------------------------------------------- Departments
CREATE TABLE Departments (
    Dept_ID     COUNTER PRIMARY KEY,
    DeptName    VARCHAR(40) NOT NULL UNIQUE,
    Building    VARCHAR(40),
    MailStop    VARCHAR(10),
    Manager     VARCHAR(50)
);

INSERT INTO Departments (DeptName, Building, MailStop, Manager) VALUES
    ('Office of the President', 'Tower, 12th Floor',      'T-1200', 'Evelyn Marchetti'),
    ('Engineering',             'Lab Annex',              'L-100',  'Howard Teague'),
    ('Sales',                   'Tower, 6th Floor',       'T-600',  'Brenda Okafor'),
    ('Marketing',               'Tower, 7th Floor',       'T-700',  'Felix Arcand'),
    ('Finance',                 'Tower, 10th Floor',      'T-1000', 'Winston Pruett'),
    ('Human Resources',         'Tower, 2nd Floor',       'T-200',  'Lorraine Ybarra'),
    ('Information Technology',  'Lab Annex, Lower Level', 'L-010',  'Desmond Kowalczyk'),
    ('Facilities',              'Service Building',       'S-001',  'Gus Hrabowski');

-- ------------------------------------------------------------------ Employees
CREATE TABLE Employees (
    Emp_ID      COUNTER PRIMARY KEY,
    FirstName   VARCHAR(30) NOT NULL,
    LastName    VARCHAR(30) NOT NULL,
    Title       VARCHAR(60),
    Dept_ID     INTEGER,
    Email       VARCHAR(60),
    Phone       VARCHAR(20),
    Office      VARCHAR(20),
    StartDate   DATE,
    Photo       VARCHAR(40),
    Notes       MEMO
);

INSERT INTO Employees (FirstName, LastName, Title, Dept_ID, Email, Phone, Office, StartDate, Photo, Notes) VALUES
    ('Evelyn',   'Marchetti', 'President',                       1, 'emarchetti@globalcorp.example', '555-0100 x1201', 'T-1201', #3/1/1985#,  'photo_1.gif', 'Founded the widget division in a rented garage. Still answers her own phone.'),
    ('Philip',   'Sandoval',  'Chief Operating Officer',         1, 'psandoval@globalcorp.example',  '555-0100 x1202', 'T-1204', #8/15/1988#, 'photo_2.gif', 'Ask him about the 1991 trade show in Duluth.'),
    ('Gwen',     'Thorsby',   'Executive Assistant',             1, 'gthorsby@globalcorp.example',   '555-0100 x1203', 'T-1210', #2/2/1994#,  'photo_3.gif', 'Keeper of the executive calendar and the good stapler.'),
    ('Howard',   'Teague',    'VP, Engineering',                 2, 'hteague@globalcorp.example',    '555-0100 x3101', 'L-110',  #6/6/1989#,  'photo_4.gif', 'Holds four patents on rotary widget couplings.'),
    ('Priya',    'Raman',     'Senior Design Engineer',          2, 'praman@globalcorp.example',     '555-0100 x3102', 'L-114',  #9/12/1993#, 'photo_1.gif', 'Lead designer of the Model 900 desktop widget.'),
    ('Tobias',   'Lindqvist', 'Design Engineer',                 2, 'tlindqvist@globalcorp.example', '555-0100 x3103', 'L-116',  #1/20/1997#, 'photo_2.gif', 'Runs the lunchtime CAD users group.'),
    ('Marisol',  'Quintero',  'Test Engineer',                   2, 'mquintero@globalcorp.example',  '555-0100 x3104', 'L-120',  #5/3/1998#,  'photo_3.gif', 'If it can be dropped, Marisol has dropped it.'),
    ('Arthur',   'Bellweather','Technician',                     2, 'abellweather@globalcorp.example','555-0100 x3105', 'L-122', #11/9/1999#, 'photo_4.gif', NULL),
    ('Brenda',   'Okafor',    'VP, Sales',                       3, 'bokafor@globalcorp.example',    '555-0100 x6101', 'T-601',  #4/18/1990#, 'photo_1.gif', 'Top regional rep three years running before joining management.'),
    ('Dale',     'Fitzhugh',  'Regional Sales Manager, East',    3, 'dfitzhugh@globalcorp.example',  '555-0100 x6102', 'T-604',  #7/7/1992#,  'photo_2.gif', NULL),
    ('Lucinda',  'Park',      'Regional Sales Manager, West',    3, 'lpark@globalcorp.example',      '555-0100 x6103', 'T-605',  #3/30/1995#, 'photo_3.gif', 'Works out of the Portland field office most weeks.'),
    ('Ned',      'Abernathy', 'Account Representative',          3, 'nabernathy@globalcorp.example', '555-0100 x6104', 'T-612',  #10/1/1997#, 'photo_4.gif', NULL),
    ('Yolanda',  'Briggs',    'Account Representative',          3, 'ybriggs@globalcorp.example',    '555-0100 x6105', 'T-613',  #2/14/1999#, 'photo_1.gif', 'Speaks Spanish and Portuguese.'),
    ('Felix',    'Arcand',    'Director of Marketing',           4, 'farcand@globalcorp.example',    '555-0100 x7101', 'T-701',  #8/1/1991#,  'photo_2.gif', NULL),
    ('Imogen',   'Strand',    'Web Producer',                    4, 'istrand@globalcorp.example',    '555-0100 x7102', 'T-708',  #4/5/1998#,  'photo_3.gif', 'Built the first version of this intranet over a long weekend.'),
    ('Calvin',   'Duvall',    'Product Marketing Manager',       4, 'cduvall@globalcorp.example',    '555-0100 x7103', 'T-710',  #9/9/1996#,  'photo_4.gif', NULL),
    ('Winston',  'Pruett',    'Controller',                      5, 'wpruett@globalcorp.example',    '555-0100 x1001', 'T-1001', #1/15/1987#, 'photo_1.gif', 'Expense reports are due on the 5th. He means it.'),
    ('Agnes',    'Kowalski',  'Accounts Payable Specialist',     5, 'akowalski@globalcorp.example',  '555-0100 x1002', 'T-1008', #6/22/1994#, 'photo_2.gif', NULL),
    ('Ravi',     'Chandran',  'Financial Analyst',               5, 'rchandran@globalcorp.example',  '555-0100 x1003', 'T-1009', #7/12/1999#, 'photo_3.gif', NULL),
    ('Lorraine', 'Ybarra',    'Director of Human Resources',     6, 'lybarra@globalcorp.example',    '555-0100 x2001', 'T-201',  #10/3/1990#, 'photo_4.gif', NULL),
    ('Shawn',    'McAllister','Recruiter',                       6, 'smcallister@globalcorp.example','555-0100 x2002', 'T-205',  #3/8/1998#,  'photo_1.gif', 'Always looking for KoldFusion developers. Referral bonus available.'),
    ('Desmond',  'Kowalczyk', 'Director of IT',                  7, 'dkowalczyk@globalcorp.example', '555-0100 x4001', 'L-011',  #5/5/1992#,  'photo_2.gif', 'Chairs the Y2K readiness committee.'),
    ('Hannah',   'Oyelaran',  'Network Administrator',           7, 'hoyelaran@globalcorp.example',  '555-0100 x4002', 'L-014',  #8/18/1996#, 'photo_3.gif', NULL),
    ('Marcus',   'Feld',      'KoldFusion Developer',            7, 'mfeld@globalcorp.example',      '555-0100 x4003', 'L-015',  #2/1/1999#,  'photo_4.gif', 'Wrote the meeting room scheduler. Bug reports to x4003.'),
    ('Tessa',    'Grunwald',  'Help Desk Analyst',               7, 'tgrunwald@globalcorp.example',  '555-0100 x4004', 'L-016',  #9/27/1999#, 'photo_1.gif', 'Have you tried turning it off and on again?'),
    ('Gus',      'Hrabowski', 'Facilities Manager',              8, 'ghrabowski@globalcorp.example', '555-0100 x5001', 'S-002',  #4/11/1986#, 'photo_2.gif', NULL),
    ('Rosa',     'Delacroix', 'Mail Room Coordinator',           8, 'rdelacroix@globalcorp.example', '555-0100 x5002', 'S-010',  #12/1/1997#, 'photo_3.gif', 'Outgoing mail leaves at 3:30 sharp.');

-- ---------------------------------------------------------------------- Users
-- Sample intranet logins (shown on the login page; this is a demo!)
CREATE TABLE Users (
    UserName    VARCHAR(20) PRIMARY KEY,
    Password    VARCHAR(20) NOT NULL,
    Emp_ID      INTEGER,
    FullName    VARCHAR(50),
    IsAdmin     BIT DEFAULT 0
);

INSERT INTO Users (UserName, Password, Emp_ID, FullName, IsAdmin) VALUES
    ('guest',    'guest',     NULL, 'Guest Visitor',     0),
    ('mfeld',    'widget',    24,   'Marcus Feld',       1),
    ('ybriggs',  'sales99',   13,   'Yolanda Briggs',    0),
    ('lybarra',  'hr4all',    20,   'Lorraine Ybarra',   1);

-- --------------------------------------------------------------- Forum topics
CREATE TABLE Topics (
    Topic_ID    COUNTER PRIMARY KEY,
    TopicName   VARCHAR(60) NOT NULL,
    Description VARCHAR(200),
    SortOrder   INTEGER
);

INSERT INTO Topics (TopicName, Description, SortOrder) VALUES
    ('Company Announcements', 'Questions and comments about news from around GlobalCorp.', 1),
    ('Year 2000 Readiness',   'Is your PC, spreadsheet or fax machine ready for the rollover? Ask here.', 2),
    ('Help Desk Tips',        'Share shortcuts, fixes and workarounds with your coworkers.', 3),
    ('Cafeteria Feedback',    'Tell the kitchen what you think. Be nice to Chef Bernard.', 4),
    ('Classifieds',           'Carpools, things for sale, lost and found.', 5);

-- --------------------------------------------------------------- Forum posts
CREATE TABLE Messages (
    Msg_ID      COUNTER PRIMARY KEY,
    Topic_ID    INTEGER NOT NULL,
    ParentID    INTEGER DEFAULT 0,
    ThreadID    INTEGER DEFAULT 0,
    Subject     VARCHAR(100) NOT NULL,
    Body        MEMO,
    Author      VARCHAR(50),
    Email       VARCHAR(60),
    Posted      DATETIME
);

INSERT INTO Messages (Topic_ID, ParentID, ThreadID, Subject, Body, Author, Email, Posted) VALUES
    (1, 0, 1, 'Will the new parking garage be open by spring?',
     'The memo said construction finishes in March. Does anyone know if that is still the plan? Circling the lot at 8:55 is getting old.',
     'Ned Abernathy', 'nabernathy@globalcorp.example', {ts '1999-11-02 08:58:00'}),
    (1, 1, 1, 'Re: Will the new parking garage be open by spring?',
     'Facilities says the top deck needs one more pour, weather permitting. Late April is more realistic.',
     'Gus Hrabowski', 'ghrabowski@globalcorp.example', {ts '1999-11-02 10:14:00'}),
    (1, 2, 1, 'Re: Re: Will the new parking garage be open by spring?',
     'Weather permitting. In this town. I will keep circling.',
     'Ned Abernathy', 'nabernathy@globalcorp.example', {ts '1999-11-02 10:40:00'}),
    (1, 1, 1, 'Re: Will the new parking garage be open by spring?',
     'There is a carpool board in Classifieds if anyone wants to share a spot in the meantime.',
     'Yolanda Briggs', 'ybriggs@globalcorp.example', {ts '1999-11-03 09:05:00'}),
    (2, 0, 5, 'My spreadsheet thinks 00 is 1900',
     'The budget template from 1996 shows the year 2000 column as 1900. Is there a fix or do I re-key everything?',
     'Ravi Chandran', 'rchandran@globalcorp.example', {ts '1999-10-18 14:22:00'}),
    (2, 5, 5, 'Re: My spreadsheet thinks 00 is 1900',
     'Enter four-digit years and re-format the column. The Help Desk has a macro that converts the old templates; call x4004.',
     'Tessa Grunwald', 'tgrunwald@globalcorp.example', {ts '1999-10-18 15:03:00'}),
    (2, 0, 7, 'Rollover night volunteers needed',
     'IT is staffing the data center from 10pm Dec 31 to 4am Jan 1. Pizza provided, champagne afterwards. Reply here to sign up.',
     'Desmond Kowalczyk', 'dkowalczyk@globalcorp.example', {ts '1999-11-15 11:30:00'}),
    (2, 7, 7, 'Re: Rollover night volunteers needed',
     'Count me in. I will bring the backup tapes and a deck of cards.',
     'Hannah Oyelaran', 'hoyelaran@globalcorp.example', {ts '1999-11-15 13:12:00'}),
    (2, 7, 7, 'Re: Rollover night volunteers needed',
     'I can do the 10pm to 1am shift.',
     'Marcus Feld', 'mfeld@globalcorp.example', {ts '1999-11-16 09:47:00'}),
    (2, 9, 7, 'Re: Re: Rollover night volunteers needed',
     'Thanks Marcus, you are on the list. Bring a sweater, the raised floor is cold.',
     'Desmond Kowalczyk', 'dkowalczyk@globalcorp.example', {ts '1999-11-16 10:20:00'}),
    (3, 0, 11, 'Ctrl+Alt+Del is not a greeting',
     'Friendly reminder: lock your workstation with Ctrl+Alt+Del then Enter when you step away. Several screens were left logged in over lunch.',
     'Tessa Grunwald', 'tgrunwald@globalcorp.example', {ts '1999-12-06 12:45:00'}),
    (3, 11, 11, 'Re: Ctrl+Alt+Del is not a greeting',
     'Is there a way to make the screen saver ask for a password automatically?',
     'Agnes Kowalski', 'akowalski@globalcorp.example', {ts '1999-12-06 13:30:00'}),
    (3, 12, 11, 'Re: Re: Ctrl+Alt+Del is not a greeting',
     'Yes: Display Properties, Screen Saver tab, tick Password protected. Ten minutes is a good wait time.',
     'Tessa Grunwald', 'tgrunwald@globalcorp.example', {ts '1999-12-06 14:02:00'}),
    (3, 0, 14, 'Getting more out of your 56K modem at home',
     'If you dial in from home, turn off call waiting first (*70, before the number). Dropped connections went away for me.',
     'Hannah Oyelaran', 'hoyelaran@globalcorp.example', DATEADD('d', -2, NOW())),
    (4, 0, 15, 'Bring back the Thursday chili',
     'Since the menu changed there has been no chili on Thursdays. Please reconsider. Signed, hungry in Engineering.',
     'Tobias Lindqvist', 'tlindqvist@globalcorp.example', {ts '1999-10-07 12:10:00'}),
    (4, 15, 15, 'Re: Bring back the Thursday chili',
     'Seconded. The vegetarian one too.',
     'Priya Raman', 'praman@globalcorp.example', {ts '1999-10-07 12:31:00'}),
    (4, 15, 15, 'Re: Bring back the Thursday chili',
     'Chef Bernard says chili returns next week, both kinds. Cornbread is on him.',
     'Gus Hrabowski', 'ghrabowski@globalcorp.example', DATEADD('d', -1, NOW())),
    (5, 0, 18, 'Carpool from the north side',
     'Looking for one or two riders from the Maple Ridge area, leaving 7:30 and heading home at 5:15. Non-smoking car.',
     'Lucinda Park', 'lpark@globalcorp.example', {ts '1999-11-20 16:40:00'}),
    (5, 0, 19, 'FOR SALE: Pentium 166 tower, 32 MB RAM',
     'Upgraded at home and the old machine needs a new desk to sit under. 2 GB disk, 8x CD-ROM, 15 inch monitor included. Make an offer.',
     'Arthur Bellweather', 'abellweather@globalcorp.example', DATEADD('d', -3, NOW())),
    (5, 19, 19, 'Re: FOR SALE: Pentium 166 tower, 32 MB RAM',
     'Does it come with a modem? My kid wants to get on the Internet.',
     'Rosa Delacroix', 'rdelacroix@globalcorp.example', DATEADD('h', -20, NOW()));

-- ----------------------------------------------------------- Catalog: categories
CREATE TABLE Categories (
    Category_ID  COUNTER PRIMARY KEY,
    CategoryName VARCHAR(40) NOT NULL,
    Blurb        VARCHAR(200),
    SortOrder    INTEGER
);

INSERT INTO Categories (CategoryName, Blurb, SortOrder) VALUES
    ('Desktop Widgets',      'The GlobalCorp line of precision desktop widgets, from the trusty Model 100 to the flagship Model 900.', 1),
    ('Computer Accessories', 'Keyboards, pointing devices and storage to keep your workstation humming.', 2),
    ('Office Supplies',      'Everything for the well-equipped cubicle.', 3),
    ('Company Store',        'Show your GlobalCorp pride with logo merchandise.', 4);

-- ------------------------------------------------------------- Catalog: products
CREATE TABLE Products (
    Product_ID   COUNTER PRIMARY KEY,
    Category_ID  INTEGER NOT NULL,
    SKU          VARCHAR(12) NOT NULL UNIQUE,
    ProductName  VARCHAR(60) NOT NULL,
    ShortDesc    VARCHAR(150),
    LongDesc     MEMO,
    Price        MONEY,
    InStock      INTEGER,
    Featured     BIT DEFAULT 0
);

INSERT INTO Products (Category_ID, SKU, ProductName, ShortDesc, LongDesc, Price, InStock, Featured) VALUES
    (1, 'GW-100', 'Model 100 Desktop Widget', 'Our original widget. Simple, sturdy, beige.',
     'The Model 100 has been on desks since 1986. One rotary coupling, a cast base and a five-year warranty. Many customers report theirs still working after a decade of daily use.', 49.95, 140, 0),
    (1, 'GW-300', 'Model 300 Dual-Action Widget', 'Two couplings for twice the action.',
     'The Model 300 adds a second rotary coupling and a smoked acrylic cover. Popular with accounting departments for reasons nobody has been able to explain.', 89.95, 75, 0),
    (1, 'GW-500', 'Model 500 Widget, Translucent Blue', 'The widget that matches your new computer.',
     'Translucent blue housing with a soft-touch dial. Fully Year 2000 compliant, which is easy when you have no clock.', 119.00, 60, 1),
    (1, 'GW-900', 'Model 900 Professional Widget', 'Our flagship: titanium couplings and a lifetime warranty.',
     'Designed by GlobalCorp Engineering, the Model 900 features titanium couplings, a weighted base, and a serial port for future expansion. Includes a padded carrying case.', 349.00, 18, 1),
    (2, 'CA-210', 'Ergonomic Split Keyboard', 'Reduce wrist strain with a split-and-tented layout.',
     'A full 104-key layout split down the middle and tented at 8 degrees. PS/2 connector with AT adapter included.', 64.50, 40, 0),
    (2, 'CA-220', 'Three-Button Wheel Mouse', 'Scroll long web pages without touching the scroll bar.',
     'The scroll wheel doubles as a third button. Works with any PS/2 port; serial adapter included.', 29.95, 210, 1),
    (2, 'CA-230', '100 MB Removable Disk, 3-Pack', 'Back up your work: about 70 floppies per disk.',
     'Three 100 MB removable cartridges in a stackable case. Compatible with most parallel and SCSI removable drives.', 39.95, 95, 0),
    (2, 'CA-240', '56K External Modem', 'V.90 standard, upgradeable firmware, blinking lights.',
     'An external 56K modem with a full set of status lights so you can see exactly what it is doing. Serial cable and fax software included.', 119.95, 32, 0),
    (2, 'CA-250', 'Surge Protector, 6 Outlet', 'Protect your PC and modem from spikes.',
     'Six outlets, phone line protection and a lighted switch. Mounts under the desk.', 24.95, 120, 0),
    (3, 'OS-300', 'Gel Wrist Rest', 'Comfort for long days of data entry.',
     'A cool gel wrist rest in charcoal gray. Pairs nicely with the Ergonomic Split Keyboard.', 12.95, 300, 0),
    (3, 'OS-310', 'Dot-Matrix Printer Paper, 2500 Sheets', 'Continuous feed with tear-off edges.',
     'Standard 9.5 x 11 inch continuous feed paper, 20 lb, with perforated tractor edges. Green bar available on request.', 32.00, 88, 0),
    (3, 'OS-320', 'Desk Organizer, Smoke Acrylic', 'Five compartments, room for a widget.',
     'Holds pens, paper clips, sticky notes and, conveniently, one Model 100 Desktop Widget.', 18.50, 64, 0),
    (3, 'OS-330', 'Sticky Notes, Neon, 12 Pads', 'Bright reminders for your monitor bezel.',
     'Twelve pads of 3 x 3 inch notes in five neon colors.', 9.95, 400, 0),
    (4, 'CS-400', 'GlobalCorp Logo Polo Shirt', 'Navy pique cotton with embroidered logo.',
     'A comfortable navy polo with the GlobalCorp globe embroidered in gold. Sizes S to XXL; specify at checkout.', 28.00, 150, 0),
    (4, 'CS-410', 'GlobalCorp Coffee Mug', 'Holds 14 oz. of the break room''s finest.',
     'Stoneware mug, navy with white logo. Dishwasher and microwave safe.', 7.50, 500, 1),
    (4, 'CS-420', 'Y2K Survivor T-Shirt', 'Commemorate the rollover in 100% cotton.',
     'Gray tee reading I SURVIVED THE ROLLOVER above a small GlobalCorp globe. Limited printing.', 14.00, 200, 0);

-- ------------------------------------------------------------- Catalog: orders
CREATE TABLE Orders (
    Order_ID    COUNTER PRIMARY KEY,
    UserName    VARCHAR(20),
    ShipName    VARCHAR(60) NOT NULL,
    Email       VARCHAR(60),
    MailStop    VARCHAR(20),
    Notes       VARCHAR(255),
    OrderTotal  MONEY,
    OrderDate   DATETIME
);

CREATE TABLE OrderItems (
    Item_ID     COUNTER PRIMARY KEY,
    Order_ID    INTEGER NOT NULL,
    Product_ID  INTEGER NOT NULL,
    Quantity    INTEGER,
    UnitPrice   MONEY
);

-- --------------------------------------------------------------- Meeting rooms
CREATE TABLE Rooms (
    Room_ID     COUNTER PRIMARY KEY,
    RoomName    VARCHAR(40) NOT NULL,
    Location    VARCHAR(40),
    Capacity    INTEGER,
    Equipment   VARCHAR(120)
);

INSERT INTO Rooms (RoomName, Location, Capacity, Equipment) VALUES
    ('Boardroom',        'Tower, 12th Floor', 20, 'Speakerphone, overhead projector, whiteboard'),
    ('Summit Room',      'Tower, 6th Floor',  10, 'Speakerphone, whiteboard'),
    ('Coupling Lab',     'Lab Annex',          6, 'Workbench, oscilloscope, coffee maker'),
    ('Training Center',  'Tower, 2nd Floor',  24, 'Twelve networked PCs, LCD projector'),
    ('Huddle Room B',    'Lab Annex',          4, 'Whiteboard');

-- ---------------------------------------------------------------- Bookings
-- Times are stored as HHMM integers (900 = 9:00 AM, 1330 = 1:30 PM)
CREATE TABLE Bookings (
    Booking_ID  COUNTER PRIMARY KEY,
    Room_ID     INTEGER NOT NULL,
    MeetingDate DATE NOT NULL,
    StartTime   INTEGER NOT NULL,
    EndTime     INTEGER NOT NULL,
    Purpose     VARCHAR(80),
    BookedBy    VARCHAR(50)
);

INSERT INTO Bookings (Room_ID, MeetingDate, StartTime, EndTime, Purpose, BookedBy) VALUES
    (1, DATEADD('d', 1, DATE()),  900, 1030, 'Quarterly operations review',  'Gwen Thorsby'),
    (2, DATEADD('d', 1, DATE()), 1300, 1400, 'Sales forecast, West region',  'Lucinda Park'),
    (3, DATEADD('d', 2, DATE()), 1000, 1200, 'Model 900 drop testing',       'Marisol Quintero'),
    (4, DATEADD('d', 3, DATE()),  830, 1630, 'KoldFusion 4.5 training',      'Marcus Feld'),
    (1, DATEADD('d', 6, DATE()), 1400, 1530, 'Board prep',                   'Gwen Thorsby'),
    (5, DATE(),                  1100, 1130, 'Help desk stand-up',           'Tessa Grunwald'),
    (2, DATEADD('d', 8, DATE()),  930, 1100, 'Trade show planning',          'Calvin Duvall'),
    (4, DATEADD('d', -4, DATE()), 900, 1200, 'New hire orientation',         'Shawn McAllister'),
    (3, DATEADD('d', 10, DATE()),1300, 1500, 'Coupling design review',       'Howard Teague');

-- ------------------------------------------------------------ What's New
CREATE TABLE Headlines (
    Headline_ID COUNTER PRIMARY KEY,
    Headline    VARCHAR(120) NOT NULL,
    Story       MEMO,
    Posted      DATETIME
);

INSERT INTO Headlines (Headline, Story, Posted) VALUES
    ('Model 900 Wins Best of Show at Widget Expo',
     'The judges singled out the titanium couplings and the serial expansion port. Congratulations to the Engineering team.',
     DATEADD('d', -1, NOW())),
    ('Open Enrollment Ends Friday',
     'Benefit elections for next year must be submitted to Human Resources by 5 pm Friday. Forms are on the HR page and outside T-201.',
     DATEADD('d', -3, NOW())),
    ('Intranet Adds Meeting Room Scheduler',
     'No more sign-up sheets taped to doors. Book the Boardroom, Summit Room and three others from the Scheduler page.',
     DATEADD('d', -6, NOW())),
    ('Help Desk Hours Extended',
     'The Help Desk is now staffed from 7 am to 7 pm on weekdays. After hours, page the on-call analyst at x4999.',
     DATEADD('d', -12, NOW())),
    ('Parking Garage Topped Out',
     'The final concrete deck has been poured. Facilities expects to open the garage within a few weeks.',
     DATEADD('d', -20, NOW()));

-- ------------------------------------------------------------- Stock quotes
-- Served by /CFDOCS/exampleapp/GlobalCorp/quoteserver/ and fetched with CFHTTP
CREATE TABLE Quotes (
    Symbol      VARCHAR(8) PRIMARY KEY,
    Company     VARCHAR(50),
    LastPrice   FLOAT,
    PrevClose   FLOAT
);

INSERT INTO Quotes (Symbol, Company, LastPrice, PrevClose) VALUES
    ('GLBC', 'GlobalCorp Industries',      42.125, 41.750),
    ('WDGT', 'Consolidated Widget Supply', 17.500, 17.875),
    ('CPLR', 'Coupler Dynamics',            8.250,  8.000),
    ('NETZ', 'Netzwerk Online',           112.375, 104.500);

-- -------------------------------------------------------------------- Parks
CREATE TABLE Parks (
    Park_ID     COUNTER PRIMARY KEY,
    ParkName    VARCHAR(70) NOT NULL,
    ParkType    VARCHAR(40),
    State       CHAR(2),
    City        VARCHAR(40),
    Region      VARCHAR(30),
    Highlights  MEMO
);

INSERT INTO Parks (ParkName, ParkType, State, City, Region, Highlights) VALUES
    ('Denali',                         'National Park and Preserve', 'AK', 'Healy',             'Alaska',        'Tundra, braided rivers and the tallest peak on the continent, when the clouds allow.'),
    ('Glacier Bay',                    'National Park and Preserve', 'AK', 'Gustavus',          'Alaska',        'Tidewater glaciers calve into a fjord best seen from the deck of a boat.'),
    ('Kenai Fjords',                   'National Park',              'AK', 'Seward',            'Alaska',        'An icefield spills glaciers down to a coast patrolled by sea otters.'),
    ('Sitka',                          'National Historical Park',   'AK', 'Sitka',             'Alaska',        'Totem poles line a coastal trail through tall spruce.'),
    ('Grand Canyon',                   'National Park',              'AZ', 'Grand Canyon',      'Intermountain', 'A mile-deep gorge that shows off two billion years of rock layers.'),
    ('Petrified Forest',               'National Park',              'AZ', 'Holbrook',          'Intermountain', 'Logs turned to stone lie scattered across the painted desert.'),
    ('Saguaro',                        'National Park',              'AZ', 'Tucson',            'Intermountain', 'Forests of giant cactus on either side of a desert city.'),
    ('Organ Pipe Cactus',              'National Monument',          'AZ', 'Ajo',               'Intermountain', 'Sonoran desert plants that grow almost nowhere else in the country.'),
    ('Canyon de Chelly',               'National Monument',          'AZ', 'Chinle',            'Intermountain', 'Sheer red walls shelter cliff dwellings and working farms.'),
    ('Montezuma Castle',               'National Monument',          'AZ', 'Camp Verde',        'Intermountain', 'A five-story dwelling tucked into a limestone cliff.'),
    ('Hot Springs',                    'National Park',              'AR', 'Hot Springs',       'Midwest',       'A row of historic bathhouses fed by thermal springs.'),
    ('Yosemite',                       'National Park',              'CA', 'Yosemite Village',  'Pacific West',  'Granite domes, giant sequoias and waterfalls that roar in late spring.'),
    ('Sequoia',                        'National Park',              'CA', 'Three Rivers',      'Pacific West',  'Home of the largest trees on Earth by volume.'),
    ('Kings Canyon',                   'National Park',              'CA', 'Three Rivers',      'Pacific West',  'A deep glacial canyon and groves of big trees next door to Sequoia.'),
    ('Death Valley',                   'National Park',              'CA', 'Furnace Creek',     'Pacific West',  'Salt flats, sand dunes and record summer heat below sea level.'),
    ('Joshua Tree',                    'National Park',              'CA', 'Twentynine Palms',  'Pacific West',  'Where two deserts meet among boulder piles and spiky trees.'),
    ('Redwood',                        'National Park',              'CA', 'Crescent City',     'Pacific West',  'Coast redwoods tower over fern-filled valleys near the ocean.'),
    ('Lassen Volcanic',                'National Park',              'CA', 'Mineral',           'Pacific West',  'Boiling mud pots and steam vents around a dormant volcano.'),
    ('Channel Islands',                'National Park',              'CA', 'Ventura',           'Pacific West',  'Five islands off the coast with sea caves and island foxes.'),
    ('Point Reyes',                    'National Seashore',          'CA', 'Point Reyes Station','Pacific West', 'Foggy headlands, tule elk and a lighthouse down 300 steps.'),
    ('Muir Woods',                     'National Monument',          'CA', 'Mill Valley',       'Pacific West',  'An old-growth redwood grove a short drive from the city.'),
    ('Golden Gate',                    'National Recreation Area',   'CA', 'San Francisco',     'Pacific West',  'Beaches, coastal forts and the island prison in the bay.'),
    ('Cabrillo',                       'National Monument',          'CA', 'San Diego',         'Pacific West',  'Tide pools and a lighthouse at the mouth of the harbor.'),
    ('Rocky Mountain',                 'National Park',              'CO', 'Estes Park',        'Intermountain', 'A high road climbs above treeline among elk and alpine lakes.'),
    ('Mesa Verde',                     'National Park',              'CO', 'Cortez',            'Intermountain', 'Cliff dwellings built into alcoves of a high green mesa.'),
    ('Great Sand Dunes',               'National Monument',          'CO', 'Mosca',             'Intermountain', 'The tallest dunes in North America piled against the mountains.'),
    ('Black Canyon of the Gunnison',   'National Monument',          'CO', 'Montrose',          'Intermountain', 'A narrow, dark gorge with walls so steep sunlight barely reaches the river.'),
    ('Everglades',                     'National Park',              'FL', 'Homestead',         'Southeast',     'A slow river of grass with alligators, wading birds and mangroves.'),
    ('Biscayne',                       'National Park',              'FL', 'Homestead',         'Southeast',     'Mostly underwater: coral reefs and keys best seen by boat.'),
    ('Dry Tortugas',                   'National Park',              'FL', 'Key West',          'Southeast',     'A huge brick fort on a tiny island far out in the Gulf.'),
    ('Canaveral',                      'National Seashore',          'FL', 'Titusville',        'Southeast',     'Undeveloped beaches within sight of the launch pads.'),
    ('Hawaii Volcanoes',               'National Park',              'HI', 'Volcano',           'Pacific West',  'Lava flows still add new land to the island.'),
    ('Haleakala',                      'National Park',              'HI', 'Kula',              'Pacific West',  'Sunrise from the rim of a vast volcanic crater above the clouds.'),
    ('Acadia',                         'National Park',              'ME', 'Bar Harbor',        'Northeast',     'Granite mountains meet the sea along carriage roads and rocky shores.'),
    ('Isle Royale',                    'National Park',              'MI', 'Houghton',          'Midwest',       'A roadless island in Lake Superior, famous for its wolves and moose.'),
    ('Sleeping Bear Dunes',            'National Lakeshore',         'MI', 'Empire',            'Midwest',       'Towering dunes above the clear water of Lake Michigan.'),
    ('Voyageurs',                      'National Park',              'MN', 'International Falls','Midwest',      'A water park in the original sense: lakes, islands and houseboats.'),
    ('Glacier',                        'National Park',              'MT', 'West Glacier',      'Intermountain', 'A mountain road crosses the Continental Divide past hanging valleys.'),
    ('Great Basin',                    'National Park',              'NV', 'Baker',             'Pacific West',  'Ancient bristlecone pines and a marble cave under a lonely peak.'),
    ('Carlsbad Caverns',               'National Park',              'NM', 'Carlsbad',          'Intermountain', 'A vast underground chamber and a nightly flight of bats.'),
    ('White Sands',                    'National Monument',          'NM', 'Alamogordo',        'Intermountain', 'Rolling dunes of white gypsum you can sled down.'),
    ('Bandelier',                      'National Monument',          'NM', 'Los Alamos',        'Intermountain', 'Ladders lead up to rooms carved in soft volcanic rock.'),
    ('Statue of Liberty',              'National Monument',          'NY', 'New York',          'Northeast',     'The copper lady in the harbor and the immigration station beside her.'),
    ('Fire Island',                    'National Seashore',          'NY', 'Patchogue',         'Northeast',     'A barrier island of dunes and a sunken forest of holly.'),
    ('Great Smoky Mountains',          'National Park',              'TN', 'Gatlinburg',        'Southeast',     'Misty ridges, old farmsteads and an astonishing variety of salamanders.'),
    ('Cape Hatteras',                  'National Seashore',          'NC', 'Manteo',            'Southeast',     'The tallest brick lighthouse in the country guards shifting shoals.'),
    ('Theodore Roosevelt',             'National Park',              'ND', 'Medora',            'Midwest',       'Badlands and bison where a future president once ranched.'),
    ('Crater Lake',                    'National Park',              'OR', 'Crater Lake',       'Pacific West',  'Deep blue water filling the caldera of a collapsed volcano.'),
    ('Gettysburg',                     'National Military Park',     'PA', 'Gettysburg',        'Northeast',     'Monuments and fields where a three-day battle turned the war.'),
    ('Badlands',                       'National Park',              'SD', 'Interior',          'Midwest',       'Eroded buttes in bands of color above the prairie.'),
    ('Wind Cave',                      'National Park',              'SD', 'Hot Springs',       'Midwest',       'Boxwork formations below and bison grazing above.'),
    ('Mount Rushmore',                 'National Memorial',          'SD', 'Keystone',          'Midwest',       'Four presidents carved into a granite mountain.'),
    ('Big Bend',                       'National Park',              'TX', 'Big Bend',          'Intermountain', 'Desert, mountains and a river canyon on the border.'),
    ('Guadalupe Mountains',            'National Park',              'TX', 'Salt Flat',         'Intermountain', 'The highest point in the state rises from an ancient reef.'),
    ('Padre Island',                   'National Seashore',          'TX', 'Corpus Christi',    'Intermountain', 'The longest undeveloped barrier island in the world.'),
    ('Zion',                           'National Park',              'UT', 'Springdale',        'Intermountain', 'Hike up the river through a slot canyon with walls of red and cream.'),
    ('Bryce Canyon',                   'National Park',              'UT', 'Bryce Canyon',      'Intermountain', 'Amphitheaters filled with orange spires called hoodoos.'),
    ('Arches',                         'National Park',              'UT', 'Moab',              'Intermountain', 'More than two thousand natural stone arches.'),
    ('Canyonlands',                    'National Park',              'UT', 'Moab',              'Intermountain', 'Rivers have cut the desert into a maze of mesas and canyons.'),
    ('Capitol Reef',                   'National Park',              'UT', 'Torrey',            'Intermountain', 'A wrinkle in the earth, with orchards you can pick in season.'),
    ('Natural Bridges',                'National Monument',          'UT', 'Blanding',          'Intermountain', 'Three great stone bridges carved by flowing water.'),
    ('Shenandoah',                     'National Park',              'VA', 'Luray',             'Northeast',     'A scenic drive along the crest of the Blue Ridge.'),
    ('Assateague Island',              'National Seashore',          'MD', 'Berlin',            'Northeast',     'Wild horses roam the beach and salt marsh.'),
    ('Olympic',                        'National Park',              'WA', 'Port Angeles',      'Pacific West',  'Glaciated peaks, rain forest and wild coast in one park.'),
    ('Mount Rainier',                  'National Park',              'WA', 'Ashford',           'Pacific West',  'Wildflower meadows ring a glacier-clad volcano.'),
    ('North Cascades',                 'National Park',              'WA', 'Marblemount',       'Pacific West',  'Jagged peaks hold more glaciers than anywhere else in the lower 48.'),
    ('Yellowstone',                    'National Park',              'WY', 'Yellowstone',       'Intermountain', 'The first national park: geysers, hot springs and roaming bison.'),
    ('Grand Teton',                    'National Park',              'WY', 'Moose',             'Intermountain', 'Sawtooth peaks rise straight out of a valley of lakes.'),
    ('Devils Tower',                   'National Monument',          'WY', 'Devils Tower',      'Intermountain', 'A great column of fluted rock rising over the plains.'),
    ('Mammoth Cave',                   'National Park',              'KY', 'Mammoth Cave',      'Southeast',     'The longest known cave system in the world.'),
    ('Virgin Islands',                 'National Park',              'VI', 'St. John',          'Southeast',     'White beaches and coral gardens on a Caribbean island.');

-- ---------------------------------------------------------- CFGRID demo table
CREATE TABLE Vendors (
    Vendor_ID   COUNTER PRIMARY KEY,
    VendorName  VARCHAR(50) NOT NULL,
    Contact     VARCHAR(40),
    Phone       VARCHAR(20),
    City        VARCHAR(30),
    Rating      INTEGER
);

INSERT INTO Vendors (VendorName, Contact, Phone, City, Rating) VALUES
    ('Northstar Castings',       'Ilse Brandt',     '555-0141', 'Duluth',       4),
    ('Precision Coupling Co.',   'Walt Emerson',    '555-0177', 'Akron',        5),
    ('Acrylic Arts',             'Dora Fenwick',    '555-0123', 'Tacoma',       3),
    ('Bluewater Packaging',      'Samir Haddad',    '555-0190', 'Savannah',     4),
    ('Tri-County Freight',       'Joe Lindgren',    '555-0108', 'Fargo',        2),
    ('Paper Trail Office Supply','Mavis Okonkwo',   '555-0156', 'Harrisburg',   4);
