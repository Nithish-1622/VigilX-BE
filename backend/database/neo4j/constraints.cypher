// Neo4j Initialization Script
// Execute this script against a fresh Neo4j instance to ensure schema integrity and performance.

// 1. Uniqueness Constraints
// Ensure all entities have a unique 'id'
CREATE CONSTRAINT unique_case_id IF NOT EXISTS FOR (c:Case) REQUIRE c.id IS UNIQUE;
CREATE CONSTRAINT unique_person_id IF NOT EXISTS FOR (p:Person) REQUIRE p.id IS UNIQUE;
CREATE CONSTRAINT unique_accused_id IF NOT EXISTS FOR (a:Accused) REQUIRE a.id IS UNIQUE;
CREATE CONSTRAINT unique_victim_id IF NOT EXISTS FOR (v:Victim) REQUIRE v.id IS UNIQUE;
CREATE CONSTRAINT unique_witness_id IF NOT EXISTS FOR (w:Witness) REQUIRE w.id IS UNIQUE;

// 2. Performance Indexes
// Indexes for common search fields
CREATE INDEX idx_case_number IF NOT EXISTS FOR (c:Case) ON (c.case_number);
CREATE INDEX idx_case_status IF NOT EXISTS FOR (c:Case) ON (c.status);
CREATE INDEX idx_person_age IF NOT EXISTS FOR (p:Person) ON (p.age_group);
