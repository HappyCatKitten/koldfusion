-- ======================================================================
--  KoldFusion Demo Gallery datasource: DEMOS
--  Shared scratch database for the scripts under /demos/:
--    event      - /demos/footballmitoo-eventcalendar/ (FootballMitoo "Diary")
--    Guestbook  - /demos/originals/guestbook.cfm
--    Counters   - /demos/originals/counter.cfm (persistent page counters)
--  Everything here is fictional.
--  Load: delete kfroot/db/demos and start the server.
-- ======================================================================

DROP TABLE IF EXISTS event;
DROP TABLE IF EXISTS Guestbook;
DROP TABLE IF EXISTS Counters;

-- ------------------------------------------------------------------- event
-- queries/qry_MonthsEvents.cfm:
--   SELECT DAY(EventDate) AS s_day, MONTH(EventDate) AS s_month FROM event
--   WHERE LeagueID = #request.LeagueID# AND MONTH(eventdate) = #URL.month_to_view#
-- Note the original query filters on the month only (not the year), so these
-- fixtures light up the same days every year. The demo league is LeagueID 1
-- (set by the companion Application.cfm); league 2 exists to prove the filter.
CREATE TABLE event (
    EventID     COUNTER PRIMARY KEY,
    EventDate   DATE NOT NULL,
    LeagueID    INTEGER NOT NULL,
    EventText   VARCHAR(80)
);

INSERT INTO event (EventDate, LeagueID, EventText) VALUES
    (#1/10/2026#,  1, 'Winter indoor five-a-side night'),
    (#1/24/2026#,  1, 'League committee meeting'),
    (#2/7/2026#,   1, 'County Cup quarter-finals'),
    (#2/21/2026#,  1, 'Referees refresher course'),
    (#3/7/2026#,   1, 'County Cup semi-finals'),
    (#3/28/2026#,  1, 'Fixtures catch-up Saturday'),
    (#4/11/2026#,  1, 'Easter tournament'),
    (#4/25/2026#,  1, 'County Cup final'),
    (#5/9/2026#,   1, 'Last day of the season'),
    (#5/23/2026#,  1, 'Annual awards dinner'),
    (#6/13/2026#,  1, 'AGM and fixtures draw'),
    (#7/18/2026#,  1, 'Pre-season friendlies begin'),
    (#8/1/2026#,   1, 'Registration deadline'),
    (#8/22/2026#,  1, 'Opening day of the season'),
    (#9/5/2026#,   1, 'League Cup round one'),
    (#9/19/2026#,  1, 'Under-12s festival'),
    (#10/3/2026#,  1, 'League Cup round two'),
    (#10/22/2026#, 1, 'Midweek floodlit fixtures'),
    (#10/31/2026#, 1, 'Fancy-dress charity match'),
    (#11/14/2026#, 1, 'Remembrance weekend - no fixtures'),
    (#11/28/2026#, 1, 'League Cup quarter-finals'),
    (#12/12/2026#, 1, 'Christmas cup'),
    (#12/26/2026#, 1, 'Boxing Day derby'),
    (#10/15/2026#, 2, 'Some other league - should not appear');

-- --------------------------------------------------------------- Guestbook
CREATE TABLE Guestbook (
    EntryID     COUNTER PRIMARY KEY,
    Name        VARCHAR(40) NOT NULL,
    Email       VARCHAR(60),
    Homepage    VARCHAR(100),
    Location    VARCHAR(40),
    HeardFrom   VARCHAR(30),
    Comments    VARCHAR(255) NOT NULL,
    Posted      DATETIME
);

INSERT INTO Guestbook (Name, Email, Homepage, Location, HeardFrom, Comments, Posted) VALUES
    ('WebMistress Kat', 'kat@example.com', 'http://www.example.com/~kat/', 'Cleveland, OH', 'Webring', 'Kewl site!!! Love the flaming GIFs. Added you to my links page :-)', {ts '1999-03-14 21:04:00'}),
    ('Dave from Doom2 Clan', '', 'http://members.example.net/doom2clan/', 'Leeds, UK', 'Search engine', 'Found you on AltaVista. Your CFML tips helped me with my clan roster page. Sign mine back!', {ts '1999-06-02 03:41:00'}),
    ('Y2K Prepper', 'bunker@example.org', '', 'Somewhere safe', 'Friend', 'Is this server Y2K compliant?? Stocking up on canned goods just in case.', {ts '1999-12-30 23:58:00'}),
    ('Jenny', 'jenny8675309@example.com', '', 'Portland, OR', 'Usenet', 'First time signing a guestbook. Hi everybody!', {ts '2000-01-01 00:02:00'});

-- ---------------------------------------------------------------- Counters
CREATE TABLE Counters (
    CounterName VARCHAR(40) PRIMARY KEY,
    Hits        INTEGER NOT NULL
);

INSERT INTO Counters (CounterName, Hits) VALUES
    ('originals/counter.cfm', 1337);
