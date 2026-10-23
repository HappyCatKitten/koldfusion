-- ======================================================================
--  KoldFusion Demo Gallery datasource: BTG
--  Backing store for /demos/btg-contacts/ ("Bridge The Gap" volunteer
--  contact list by Cheri Jones, GPL-3.0). The schema below was inferred
--  from the application's .cfm files (CFQUERY / CFINSERT / CFUPDATE).
--  Every person, address, phone number and e-mail address here is
--  FICTIONAL. Phone numbers use the 555-01xx range, e-mail uses
--  example.com/.org/.net.
--
--  Demo logins (plaintext, exactly as the 2000s-era app expects):
--     username  password   level  district
--     admin     bridge     2      1        (state admin: sees everything,
--                                           gets the "District Admin" buttons)
--     dist5     coffee     1      5        (district admin: district 5 only)
--     dist12    pancake    1      12       (district admin: district 12 only)
--
--  Load: delete kfroot/db/btg and start the server.
-- ======================================================================

DROP TABLE IF EXISTS login;
DROP TABLE IF EXISTS contacts;
DROP TABLE IF EXISTS statepart;

-- ------------------------------------------------------------------- login
-- loginpost.cfm: SELECT * FROM login WHERE username='#user#'
-- admin3a.cfm:   CFINSERT formfields username, password, district, adminlevel
-- admin4b.cfm:   CFUPDATE formfields userid, username, password, district, adminlevel
CREATE TABLE login (
    userid      COUNTER PRIMARY KEY,
    username    VARCHAR(30) NOT NULL,
    password    VARCHAR(30) NOT NULL,
    adminlevel  INTEGER,
    district    INTEGER
);

INSERT INTO login (username, password, adminlevel, district) VALUES
    ('admin',  'bridge',  2, 1),
    ('dist5',  'coffee',  1, 5),
    ('dist12', 'pancake', 1, 12);

-- --------------------------------------------------------------- statepart
-- add1.cfm: SELECT * FROM statepart  (CFSELECT value="part" display="part")
CREATE TABLE statepart (
    partid      COUNTER PRIMARY KEY,
    part        VARCHAR(30) NOT NULL
);

INSERT INTO statepart (part) VALUES
    ('Northwest'),
    ('Northeast'),
    ('Central'),
    ('Kansas City Metro'),
    ('St. Louis Metro'),
    ('Southwest'),
    ('Southeast / Bootheel');

-- ---------------------------------------------------------------- contacts
-- add2.cfm CFINSERT formfields: state, district, first, last, interest, city,
--   zip, county, phone, email, added, current, gender, age, flang
-- list pages also print: address, metro, statepart; update1/delete1 use contactid
-- interest: TF (treatment facility), CF (correctional facility) or Both
CREATE TABLE contacts (
    contactid   COUNTER PRIMARY KEY,
    first       VARCHAR(30),
    last        VARCHAR(30),
    address     VARCHAR(60),
    city        VARCHAR(30),
    zip         VARCHAR(10),
    county      VARCHAR(30),
    metro       VARCHAR(30),
    state       VARCHAR(2),
    statepart   VARCHAR(30),
    district    INTEGER,
    gender      VARCHAR(6),
    age         VARCHAR(3),
    phone       VARCHAR(20),
    email       VARCHAR(60),
    interest    VARCHAR(4),
    flang       VARCHAR(3),
    current     VARCHAR(3),
    added       DATE
);

INSERT INTO contacts (first, last, address, city, zip, county, metro, state, statepart, district, gender, age, phone, email, interest, flang, current, added) VALUES
    ('Harriet', 'Bellweather', '12 Persimmon Ln',   'Maryville',     '64468', 'Nodaway',     'St. Joseph',     'MO', 'Northwest',          1,  'Female', '52', '660-555-0112', 'hbellweather@example.com', 'Both', 'no',  'yes', #3/14/2003#),
    ('Walter',  'Quimby',    '408 Elm St',          'Kirksville',    '63501', 'Adair',       'Kirksville',     'MO', 'Northeast',          2,  'Male',   '61', '660-555-0147', 'wquimby@example.net',      'CF',   'no',  'yes', #7/2/2002#),
    ('Rosa',    'Delgado',   '77 Cottonwood Ct',    'Columbia',      '65201', 'Boone',       'Columbia',       'MO', 'Central',            3,  'Female', '38', '573-555-0163', 'rdelgado@example.org',     'TF',   'yes', 'yes', #11/20/2004#),
    ('Earl',    'Pennington','1900 Old Hwy 63',     'Jefferson City','65101', 'Cole',        'Jefferson City', 'MO', 'Central',            3,  'Male',   '47', '573-555-0188', 'earlp@example.com',        'Both', 'no',  'yes', #1/9/2005#),
    ('Dolores', 'Kettering', '5 Lakeview Terrace',  'Lee''s Summit', '64063', 'Jackson',     'Kansas City',    'MO', 'Kansas City Metro',  5,  'Female', '44', '816-555-0121', 'dkettering@example.com',   'TF',   'no',  'yes', #6/30/2003#),
    ('Marcus',  'Abernathy', '310 Grand Blvd',      'Kansas City',   '64106', 'Jackson',     'Kansas City',    'MO', 'Kansas City Metro',  5,  'Male',   '33', '816-555-0139', 'mabernathy@example.net',   'CF',   'yes', 'yes', #9/12/2004#),
    ('Inez',    'Fairweather','88 Sycamore Dr',     'Independence',  '64050', 'Jackson',     'Kansas City',    'MO', 'Kansas City Metro',  5,  'Female', '58', '816-555-0174', 'inezf@example.org',        'Both', 'yes', 'yes', #2/27/2002#),
    ('Gus',     'Hollander', '21 Riverfront Pl',    'St. Charles',   '63301', 'St. Charles', 'St. Louis',      'MO', 'St. Louis Metro',    8,  'Male',   '66', '636-555-0105', 'ghollander@example.com',   'TF',   'no',  'yes', #4/4/2001#),
    ('Opal',    'Whitcombe', '1515 Lindell Ave',    'St. Louis',     '63108', 'St. Louis City','St. Louis',    'MO', 'St. Louis Metro',    9,  'Female', '29', '314-555-0150', 'owhitcombe@example.net',   'CF',   'no',  'yes', #12/1/2005#),
    ('Theo',    'Marchetti', '44 Hampton Way',      'Kirkwood',      '63122', 'St. Louis',   'St. Louis',      'MO', 'St. Louis Metro',    9,  'Male',   '41', '314-555-0196', 'tmarchetti@example.org',   'Both', 'no',  'yes', #8/18/2003#),
    ('Lucille', 'Abbott',    '9 Dogwood Hollow',    'Rolla',         '65401', 'Phelps',      'Rolla',          'MO', 'Central',           10,  'Female', '55', '573-555-0127', 'labbott@example.com',      'TF',   'no',  'yes', #5/5/2004#),
    ('Javier',  'Montoya',   '230 Battlefield Rd',  'Springfield',   '65807', 'Greene',      'Springfield',    'MO', 'Southwest',         12,  'Male',   '36', '417-555-0144', 'jmontoya@example.net',     'CF',   'yes', 'yes', #10/10/2002#),
    ('Mavis',   'Thornbury', '17 Shoal Creek Rd',   'Joplin',        '64801', 'Jasper',      'Joplin',         'MO', 'Southwest',         12,  'Female', '63', '417-555-0181', 'mthornbury@example.org',   'Both', 'no',  'yes', #3/3/2005#),
    ('Clyde',   'Ashworth',  '602 Main St',         'Branson',       '65616', 'Taney',       'Springfield',    'MO', 'Southwest',         12,  'Male',   '50', '417-555-0168', 'cashworth@example.com',    'TF',   'no',  'yes', #7/21/2001#),
    ('Nadine',  'Pruitt',    '3 Cypress Bend',      'Cape Girardeau','63701', 'Cape Girardeau','Cape Girardeau','MO', 'Southeast / Bootheel',15, 'Female', '39', '573-555-0133', 'npruitt@example.net',      'CF',   'no',  'yes', #1/28/2006#),
    ('Amos',    'Fenwick',   '1120 Broadway',       'Poplar Bluff',  '63901', 'Butler',      'Poplar Bluff',   'MO', 'Southeast / Bootheel',16, 'Male',   '57', '573-555-0119', 'afenwick@example.org',     'Both', 'yes', 'yes', #6/6/2003#);
