-- PostgreSQL Database Schema
-- Generated exactly from "Police FIR System — ER Diagram"
-- Data types translated from T-SQL to PostgreSQL where necessary (e.g. DATETIME -> TIMESTAMP, Nvarchar(Max) -> TEXT, BIT -> BOOLEAN)

-- ==========================================
-- 1. Master / Lookup Tables
-- ==========================================

CREATE TABLE State (
    StateID INTEGER PRIMARY KEY,
    StateName VARCHAR,
    NationalityID INTEGER,
    Active BOOLEAN -- 1=Active, 0=Inactive
);

CREATE TABLE CasteMaster (
    caste_master_id INTEGER PRIMARY KEY,
    caste_master_name VARCHAR
);

CREATE TABLE ReligionMaster (
    ReligionID INTEGER PRIMARY KEY,
    ReligionName VARCHAR
);

CREATE TABLE OccupationMaster (
    OccupationID INTEGER PRIMARY KEY,
    OccupationName VARCHAR
);

CREATE TABLE CaseStatusMaster (
    CaseStatusID INTEGER PRIMARY KEY,
    CaseStatusName VARCHAR
);

CREATE TABLE UnitType (
    UnitTypeID INTEGER PRIMARY KEY,
    UnitTypeName VARCHAR,
    CityDistState VARCHAR,
    Hierarchy INTEGER,
    Active BOOLEAN
);

CREATE TABLE Rank (
    RankID INTEGER PRIMARY KEY,
    RankName VARCHAR,
    Hierarchy INTEGER,
    Active BOOLEAN
);

CREATE TABLE Designation (
    DesignationID INTEGER PRIMARY KEY,
    DesignationName VARCHAR,
    Active BOOLEAN,
    SortOrder INTEGER
);

CREATE TABLE CaseCategory (
    CaseCategoryID INTEGER PRIMARY KEY,
    LookupValue VARCHAR
);

CREATE TABLE GravityOffence (
    GravityOffenceID INTEGER PRIMARY KEY,
    LookupValue VARCHAR
);

CREATE TABLE Act (
    ActCode VARCHAR PRIMARY KEY,
    ActDescription VARCHAR,
    ShortName VARCHAR,
    Active BOOLEAN
);

CREATE TABLE CrimeHead (
    CrimeHeadID INTEGER PRIMARY KEY,
    CrimeGroupName VARCHAR,
    Active BOOLEAN
);

-- ==========================================
-- 2. First-Level Dependencies
-- ==========================================

CREATE TABLE District (
    DistrictID INTEGER PRIMARY KEY,
    DistrictName VARCHAR,
    StateID INTEGER REFERENCES State(StateID),
    Active BOOLEAN
);

CREATE TABLE Section (
    SectionCode VARCHAR PRIMARY KEY, -- Inferred as PK based on relationships
    ActCode VARCHAR REFERENCES Act(ActCode),
    SectionDescription VARCHAR,
    Active BOOLEAN
);

CREATE TABLE CrimeSubHead (
    CrimeSubHeadID INTEGER PRIMARY KEY,
    CrimeHeadID INTEGER REFERENCES CrimeHead(CrimeHeadID),
    CrimeHeadName VARCHAR,
    SeqID INTEGER
);

CREATE TABLE CrimeHeadActSection (
    CrimeHeadID INTEGER REFERENCES CrimeHead(CrimeHeadID),
    ActCode VARCHAR REFERENCES Act(ActCode),
    SectionCode VARCHAR
    -- Note: PDF does not specify PK here, could be composite.
);

-- ==========================================
-- 3. Second-Level Dependencies
-- ==========================================

CREATE TABLE Court (
    CourtID INTEGER PRIMARY KEY,
    CourtName VARCHAR,
    DistrictID INTEGER REFERENCES District(DistrictID),
    StateID INTEGER REFERENCES State(StateID),
    Active BOOLEAN
);

CREATE TABLE Unit (
    UnitID INTEGER PRIMARY KEY,
    UnitName VARCHAR,
    TypeID INTEGER REFERENCES UnitType(UnitTypeID),
    ParentUnit INTEGER,
    NationalityID INTEGER,
    StateID INTEGER REFERENCES State(StateID),
    DistrictID INTEGER REFERENCES District(DistrictID),
    Active BOOLEAN
);

-- ==========================================
-- 4. Third-Level Dependencies
-- ==========================================

CREATE TABLE Employee (
    EmployeeID INTEGER PRIMARY KEY,
    DistrictID INTEGER REFERENCES District(DistrictID),
    UnitID INTEGER REFERENCES Unit(UnitID),
    RankID INTEGER REFERENCES Rank(RankID),
    DesignationID INTEGER REFERENCES Designation(DesignationID),
    KGID VARCHAR,
    FirstName VARCHAR,
    EmployeeDOB DATE,
    GenderID INTEGER,
    BloodGroupID INTEGER,
    PhysicallyChallenged BOOLEAN,
    AppointmentDate DATE
);

-- ==========================================
-- 5. Core Case Tables
-- ==========================================

CREATE TABLE CaseMaster (
    CaseMasterID INTEGER PRIMARY KEY,
    CrimeNo VARCHAR,
    CaseNo VARCHAR,
    CrimeRegisteredDate DATE,
    PolicePersonID INTEGER REFERENCES Employee(EmployeeID),
    PoliceStationID INTEGER REFERENCES Unit(UnitID),
    CaseCategoryID INTEGER REFERENCES CaseCategory(CaseCategoryID),
    GravityOffenceID INTEGER REFERENCES GravityOffence(GravityOffenceID),
    CrimeMajorHeadID INTEGER REFERENCES CrimeHead(CrimeHeadID),
    CrimeMinorHeadID INTEGER REFERENCES CrimeSubHead(CrimeSubHeadID),
    CaseStatusID INTEGER REFERENCES CaseStatusMaster(CaseStatusID),
    CourtID INTEGER REFERENCES Court(CourtID),
    IncidentFromDate TIMESTAMP,
    IncidentToDate TIMESTAMP,
    InfoReceivedPSDate TIMESTAMP,
    latitude DECIMAL,
    longitude DECIMAL,
    BriefFacts TEXT
);

-- ==========================================
-- 6. Case Association Tables
-- ==========================================

CREATE TABLE ComplainantDetails (
    ComplainantID INTEGER PRIMARY KEY,
    CaseMasterID INTEGER REFERENCES CaseMaster(CaseMasterID),
    ComplainantName VARCHAR,
    AgeYear INTEGER,
    OccupationID INTEGER REFERENCES OccupationMaster(OccupationID),
    ReligionID INTEGER REFERENCES ReligionMaster(ReligionID),
    CasteID INTEGER REFERENCES CasteMaster(caste_master_id),
    GenderID INTEGER
);

CREATE TABLE ActSectionAssociation (
    CaseMasterID INTEGER REFERENCES CaseMaster(CaseMasterID),
    -- PDF states these are INT, but parent keys are VARCHAR. Corrected to VARCHAR for valid SQL.
    ActID VARCHAR REFERENCES Act(ActCode),
    SectionID VARCHAR REFERENCES Section(SectionCode),
    ActOrderID INTEGER,
    SectionOrderID INTEGER
);

CREATE TABLE Victim (
    VictimMasterID INTEGER PRIMARY KEY,
    CaseMasterID INTEGER REFERENCES CaseMaster(CaseMasterID),
    VictimName VARCHAR,
    AgeYear INTEGER,
    GenderID INTEGER,
    VictimPolice VARCHAR
);

CREATE TABLE Accused (
    AccusedMasterID INTEGER PRIMARY KEY,
    CaseMasterID INTEGER REFERENCES CaseMaster(CaseMasterID),
    AccusedName VARCHAR,
    AgeYear INTEGER,
    GenderID INTEGER,
    PersonID VARCHAR
);

CREATE TABLE ChargesheetDetails (
    CSID INTEGER PRIMARY KEY,
    CaseMasterID INTEGER REFERENCES CaseMaster(CaseMasterID),
    csdate TIMESTAMP,
    cstype CHAR,
    PolicePersonID INTEGER REFERENCES Employee(EmployeeID)
);

-- ==========================================
-- 7. Event & Junction Tables
-- ==========================================

CREATE TABLE ArrestSurrender (
    ArrestSurrenderID INTEGER PRIMARY KEY,
    CaseMasterID INTEGER REFERENCES CaseMaster(CaseMasterID),
    ArrestSurrenderTypeID INTEGER,
    ArrestSurrenderDate DATE,
    ArrestSurrenderStateId INTEGER REFERENCES State(StateID),
    ArrestSurrenderDistrictId INTEGER REFERENCES District(DistrictID),
    PoliceStationID INTEGER REFERENCES Unit(UnitID),
    IOID INTEGER REFERENCES Employee(EmployeeID),
    CourtID INTEGER REFERENCES Court(CourtID),
    AccusedMasterID INTEGER REFERENCES Accused(AccusedMasterID),
    IsAccused BOOLEAN,
    IsComplainantAccused BOOLEAN
);

CREATE TABLE inv_arrestsurrenderaccused (
    ArrestSurrenderID INTEGER REFERENCES ArrestSurrender(ArrestSurrenderID),
    AccusedMasterID INTEGER REFERENCES Accused(AccusedMasterID)
);

CREATE TABLE Inv_OccuranceTime (
    CaseMasterID INTEGER REFERENCES CaseMaster(CaseMasterID)
);
