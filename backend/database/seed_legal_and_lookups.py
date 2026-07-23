import os
import random
from datetime import datetime, timedelta
from faker import Faker
import psycopg2
from psycopg2.extras import execute_values
from dotenv import load_dotenv

load_dotenv(os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(__file__))), '.env'))
fake = Faker('en_IN')

def get_existing_data(cur):
    print("Fetching existing casemasterids and accusedmasterids...")
    cur.execute("SELECT casemasterid FROM casemaster")
    case_ids = [row[0] for row in cur.fetchall()]
    
    cur.execute("SELECT accusedmasterid, casemasterid FROM accused")
    accused_data = cur.fetchall()
    
    return case_ids, accused_data

def seed_lookups(cur):
    print("Seeding robust lookup and master tables...")
    
    # We already have State=1, District=1, Court=1, UnitType=1, Unit=1, Rank=1, Designation=1 in DB from previous run.
    # Let's add more
    states = [(2, 'Karnataka', 1, True), (3, 'Delhi', 1, True), (4, 'Tamil Nadu', 1, True)]
    execute_values(cur, "INSERT INTO State (StateID, StateName, NationalityID, Active) VALUES %s ON CONFLICT DO NOTHING", states)
    
    districts = [(2, 'Bengaluru', 2, True), (3, 'New Delhi', 3, True), (4, 'Chennai', 4, True)]
    execute_values(cur, "INSERT INTO District (DistrictID, DistrictName, StateID, Active) VALUES %s ON CONFLICT DO NOTHING", districts)
    
    courts = [(2, 'Bengaluru City Civil Court', 2, 2, True), (3, 'Delhi District Court', 3, 3, True)]
    execute_values(cur, "INSERT INTO Court (CourtID, CourtName, DistrictID, StateID, Active) VALUES %s ON CONFLICT DO NOTHING", courts)
    
    units = [(2, 'Indiranagar PS', 1, 1, 1, 2, 2, True), (3, 'Connaught Place PS', 1, 1, 1, 3, 3, True)]
    execute_values(cur, "INSERT INTO Unit (UnitID, UnitName, TypeID, ParentUnit, NationalityID, StateID, DistrictID, Active) VALUES %s ON CONFLICT DO NOTHING", units)
    
    ranks = [(2, 'Sub-Inspector', 2, True), (3, 'Constable', 3, True)]
    execute_values(cur, "INSERT INTO Rank (RankID, RankName, Hierarchy, Active) VALUES %s ON CONFLICT DO NOTHING", ranks)
    
    designations = [(2, 'Sub-Inspector', True, 2), (3, 'Constable', True, 3)]
    execute_values(cur, "INSERT INTO Designation (DesignationID, DesignationName, Active, SortOrder) VALUES %s ON CONFLICT DO NOTHING", designations)
    
    # 50 Employees
    employees = []
    for i in range(2, 52):
        dob = fake.date_of_birth(minimum_age=25, maximum_age=60)
        appt_date = dob + timedelta(days=25*365) # Appointed at ~25 years old
        employees.append((i, random.randint(1, 4), random.randint(1, 3), random.randint(1, 3), random.randint(1, 3), f'KG{i*123}', fake.first_name(), dob, 1, 1, False, appt_date))
    execute_values(cur, "INSERT INTO Employee (EmployeeID, DistrictID, UnitID, RankID, DesignationID, KGID, FirstName, EmployeeDOB, GenderID, BloodGroupID, PhysicallyChallenged, AppointmentDate) VALUES %s ON CONFLICT DO NOTHING", employees)

def seed_legal_data(cur, case_ids, accused_data):
    print("Seeding legal & investigation details...")
    
    # 1. Acts & Sections
    acts = [
        ('IPC', 'Indian Penal Code 1860', 'IPC', True),
        ('ITACT', 'Information Technology Act 2000', 'IT Act', True),
        ('NDPS', 'Narcotic Drugs and Psychotropic Substances Act 1985', 'NDPS', True)
    ]
    execute_values(cur, "INSERT INTO Act (ActCode, ActDescription, ShortName, Active) VALUES %s ON CONFLICT DO NOTHING", acts)
    
    sections = [
        ('302', 'IPC', 'Punishment for murder', True),
        ('379', 'IPC', 'Punishment for theft', True),
        ('420', 'IPC', 'Cheating and dishonestly inducing delivery of property', True),
        ('66C', 'ITACT', 'Punishment for identity theft', True),
        ('20', 'NDPS', 'Punishment for contravention in relation to cannabis plant and cannabis', True)
    ]
    execute_values(cur, "INSERT INTO Section (SectionCode, ActCode, SectionDescription, Active) VALUES %s ON CONFLICT DO NOTHING", sections)
    
    # 2. CrimeHeadActSection (mapping crimehead -> act -> section)
    chas = []
    # crimehead 1 is 'Theft' (from previous script)
    chas.append((1, 'IPC', '379'))
    execute_values(cur, "INSERT INTO CrimeHeadActSection (CrimeHeadID, ActCode, SectionCode) VALUES %s ON CONFLICT DO NOTHING", chas)
    
    # 3. ActSectionAssociation (for each case, assign a random section)
    asa_records = []
    for case_id in case_ids:
        sec = random.choice(sections)
        asa_records.append((case_id, sec[1], sec[0], 1, 1))
        
        # sometimes assign a second section
        if random.random() > 0.7:
            sec2 = random.choice(sections)
            if sec2[0] != sec[0]:
                asa_records.append((case_id, sec2[1], sec2[0], 2, 2))
                
    execute_values(cur, "INSERT INTO ActSectionAssociation (CaseMasterID, ActID, SectionID, ActOrderID, SectionOrderID) VALUES %s", asa_records)
    
    # 4. ArrestSurrender & inv_arrestsurrenderaccused & ChargesheetDetails
    arrest_records = []
    inv_arr_acc_records = []
    cs_records = []
    cs_id_counter = 1
    
    for idx, (accused_id, case_id) in enumerate(accused_data, start=1):
        # Generate an arrest for each accused
        arr_date = fake.date_between(start_date="-1y", end_date="today")
        # ArrestSurrender fields: ArrestSurrenderID, CaseMasterID, ArrestSurrenderTypeID, ArrestSurrenderDate, ArrestSurrenderStateId, ArrestSurrenderDistrictId, PoliceStationID, IOID, CourtID, AccusedMasterID, IsAccused, IsComplainantAccused
        arrest_records.append((
            idx, case_id, random.randint(1, 2), arr_date, random.randint(1, 4), random.randint(1, 4), random.randint(1, 3), random.randint(1, 51), random.randint(1, 3), accused_id, True, False
        ))
        
        # Junction
        inv_arr_acc_records.append((idx, accused_id))
        
        # Chargesheet (only for 50% of cases roughly)
        if random.random() > 0.5:
            cs_date = arr_date + timedelta(days=random.randint(10, 90))
            if cs_date > datetime.now().date():
                cs_date = datetime.now().date()
            cs_records.append((
                cs_id_counter, case_id, cs_date, random.choice(['F', 'S']), random.randint(1, 51)
            ))
            cs_id_counter += 1
            
    execute_values(cur, "INSERT INTO ArrestSurrender (ArrestSurrenderID, CaseMasterID, ArrestSurrenderTypeID, ArrestSurrenderDate, ArrestSurrenderStateId, ArrestSurrenderDistrictId, PoliceStationID, IOID, CourtID, AccusedMasterID, IsAccused, IsComplainantAccused) VALUES %s ON CONFLICT DO NOTHING", arrest_records)
    execute_values(cur, "INSERT INTO inv_arrestsurrenderaccused (ArrestSurrenderID, AccusedMasterID) VALUES %s", inv_arr_acc_records)
    execute_values(cur, "INSERT INTO ChargesheetDetails (CSID, CaseMasterID, csdate, cstype, PolicePersonID) VALUES %s ON CONFLICT DO NOTHING", cs_records)

    # 5. inv_occurancetime (Junction/Tracker for time)
    occ_time = [(c,) for c in case_ids]
    execute_values(cur, "INSERT INTO Inv_OccuranceTime (CaseMasterID) VALUES %s ON CONFLICT DO NOTHING", occ_time)

def main():
    print("--- Starting Legal & Lookup Seeding ---")
    db_url = os.getenv("DATABASE_URL")
    conn = psycopg2.connect(db_url)
    cur = conn.cursor()
    
    try:
        case_ids, accused_data = get_existing_data(cur)
        if not case_ids:
            print("No cases found in DB. Please run the primary seeder first.")
            return
            
        seed_lookups(cur)
        seed_legal_data(cur, case_ids, accused_data)
        
        conn.commit()
        print("--- Successfully seeded Legal & Lookup tables with NO null values! ---")
    except Exception as e:
        conn.rollback()
        print(f"Error occurred: {e}")
    finally:
        cur.close()
        conn.close()

if __name__ == "__main__":
    main()
