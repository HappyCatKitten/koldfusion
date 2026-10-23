-- ======================================================================
--  KoldFusion 4.5 example datasource: COMPANYINFO
--  Used by the "Human Resources Employee Manager" example application
--  (/CFDOCS/exampleapp/HRApp/) and the Developing Web Applications
--  tutorial. Everyone listed here is fictional.
-- ======================================================================

DROP TABLE IF EXISTS Employees;
DROP TABLE IF EXISTS Departments;

CREATE TABLE Departments (
    Department_ID    COUNTER PRIMARY KEY,
    Department_Name  VARCHAR(40) NOT NULL,
    Location         VARCHAR(40)
);

INSERT INTO Departments (Department_Name, Location) VALUES
    ('Accounting',       'Cambridge'),
    ('Customer Service', 'Tulsa'),
    ('Engineering',      'Boulder'),
    ('Human Resources',  'Cambridge'),
    ('Marketing',        'Providence'),
    ('Sales',            'Tulsa'),
    ('Training',         'Boulder');

CREATE TABLE Employees (
    Employee_ID      COUNTER PRIMARY KEY,
    FirstName        VARCHAR(30) NOT NULL,
    LastName         VARCHAR(30) NOT NULL,
    Department_ID    INTEGER,
    StartDate        DATE,
    Salary           MONEY,
    Contract         BIT DEFAULT 0
);

INSERT INTO Employees (FirstName, LastName, Department_ID, StartDate, Salary, Contract) VALUES
    ('Oliver',    'Brennan',    1, #4/12/1993#,  48500, 0),
    ('Celia',     'Ng',         1, #9/1/1997#,   39000, 0),
    ('Martin',    'Vasquez',    1, #2/16/1999#,  31000, 1),
    ('Delphine',  'Moreau',     2, #6/30/1995#,  33500, 0),
    ('Kwame',     'Asante',     2, #11/11/1998#, 29000, 0),
    ('Hollis',    'Becker',     2, #3/22/1999#,  27500, 1),
    ('Ingrid',    'Solberg',    3, #1/5/1991#,   71000, 0),
    ('Rajesh',    'Iyer',       3, #8/19/1996#,  64000, 0),
    ('Fiona',     'Gallagher',  3, #5/10/1999#,  58000, 1),
    ('Theo',      'Papadakis',  3, #10/4/1999#,  55500, 0),
    ('Wanda',     'Cheswick',   4, #7/7/1990#,   52000, 0),
    ('Luis',      'Ortega',     4, #12/13/1996#, 41000, 0),
    ('Annabel',   'Fairweather',5, #2/2/1994#,   57000, 0),
    ('Grady',     'Hollister',  5, #4/28/1998#,  43500, 1),
    ('Sofia',     'Lindgren',   6, #9/15/1992#,  62000, 0),
    ('Jerome',    'Whitcombe',  6, #3/3/1997#,   47500, 0),
    ('Bettina',   'Ruiz',       6, #6/21/1999#,  38000, 1),
    ('Malcolm',   'Ferris',     7, #1/18/1995#,  45000, 0),
    ('Noriko',    'Tanabe',     7, #8/8/1998#,   42000, 1);
