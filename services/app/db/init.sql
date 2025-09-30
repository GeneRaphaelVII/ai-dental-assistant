-- DB init with availability, claims, and RLS
CREATE EXTENSION IF NOT EXISTS vector;

CREATE TABLE IF NOT EXISTS docs (
  id serial PRIMARY KEY,
  tenant_id text NOT NULL,
  doc_type text,
  effective_date date,
  chunk_text text,
  embedding vector(384),
  source_doc text
);

CREATE TABLE IF NOT EXISTS availability (
  id serial PRIMARY KEY,
  tenant_id text NOT NULL,
  start_time timestamptz NOT NULL,
  end_time timestamptz NOT NULL,
  booked boolean DEFAULT false,
  patient_name text
);

CREATE TABLE IF NOT EXISTS claims (
  id serial PRIMARY KEY,
  tenant_id text NOT NULL,
  claim_id text,
  patient_id text,
  status text,
  coverage_pct int
);

-- Enable RLS and policy for tenant isolation
ALTER TABLE docs ENABLE ROW LEVEL SECURITY;
CREATE POLICY tenant_isolation_docs ON docs
  USING (tenant_id = current_setting('app.current_tenant', true));

ALTER TABLE availability ENABLE ROW LEVEL SECURITY;
CREATE POLICY tenant_isolation_avail ON availability
  USING (tenant_id = current_setting('app.current_tenant', true));

ALTER TABLE claims ENABLE ROW LEVEL SECURITY;
CREATE POLICY tenant_isolation_claims ON claims
  USING (tenant_id = current_setting('app.current_tenant', true));

-- Seed some availability and claims
INSERT INTO availability (tenant_id, start_time, end_time, booked) VALUES
('clinic-123', '2025-10-01T09:00:00+08', '2025-10-01T09:30:00+08', false),
('clinic-123', '2025-10-01T10:00:00+08', '2025-10-01T10:30:00+08', false),
('clinic-456', '2025-10-02T14:00:00+08', '2025-10-02T14:30:00+08', false);

INSERT INTO claims (tenant_id, claim_id, patient_id, status, coverage_pct) VALUES
('clinic-123', 'C-1001', 'P-1', 'submitted', 80),
('clinic-123', 'C-1002', 'P-2', 'paid', 100),
('clinic-456', 'C-2001', 'P-3', 'denied', 0);
