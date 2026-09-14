-- ForgeOS operational data model. State-changing commands must run inside a transaction.
CREATE EXTENSION IF NOT EXISTS pgcrypto;

CREATE TABLE material_batches (
  id UUID PRIMARY KEY DEFAULT gen_random_uuid(), material_sku TEXT NOT NULL, supplier_lot TEXT NOT NULL,
  quantity_received NUMERIC NOT NULL CHECK (quantity_received >= 0), quantity_available NUMERIC NOT NULL CHECK (quantity_available >= 0),
  quantity_reserved NUMERIC NOT NULL DEFAULT 0 CHECK (quantity_reserved >= 0), quantity_consumed NUMERIC NOT NULL DEFAULT 0 CHECK (quantity_consumed >= 0),
  status TEXT NOT NULL CHECK (status IN ('AVAILABLE','RESERVED','IN_USE','ON_HOLD','EXHAUSTED')), received_at TIMESTAMPTZ NOT NULL DEFAULT now(), expiry_at TIMESTAMPTZ, current_location TEXT NOT NULL
);
CREATE TABLE machines (id UUID PRIMARY KEY DEFAULT gen_random_uuid(), machine_code TEXT UNIQUE NOT NULL, machine_type TEXT NOT NULL, line_id TEXT NOT NULL, status TEXT NOT NULL CHECK(status IN ('AVAILABLE','RESERVED','RUNNING','DOWN','ON_HOLD')), current_run_id UUID, last_calibrated_at TIMESTAMPTZ, status_changed_at TIMESTAMPTZ NOT NULL DEFAULT now());
CREATE TABLE operators (id UUID PRIMARY KEY DEFAULT gen_random_uuid(), employee_code TEXT UNIQUE NOT NULL, name TEXT NOT NULL, status TEXT NOT NULL CHECK(status IN ('AVAILABLE','ASSIGNED','OFF_SHIFT')), shift_id TEXT, active_run_id UUID);
CREATE TABLE operator_qualifications (operator_id UUID REFERENCES operators(id), machine_type TEXT NOT NULL, certification_code TEXT NOT NULL, valid_until TIMESTAMPTZ NOT NULL, PRIMARY KEY(operator_id,machine_type));
CREATE TABLE production_runs (id UUID PRIMARY KEY DEFAULT gen_random_uuid(), work_order_number TEXT UNIQUE NOT NULL, product_sku TEXT NOT NULL, planned_quantity NUMERIC NOT NULL, produced_quantity NUMERIC NOT NULL DEFAULT 0, status TEXT NOT NULL CHECK(status IN ('PLANNED','STAGED','ACTIVE','BLOCKED','COMPLETED')), planned_start_at TIMESTAMPTZ, actual_start_at TIMESTAMPTZ, actual_end_at TIMESTAMPTZ, priority INT NOT NULL DEFAULT 3, due_at TIMESTAMPTZ NOT NULL);
CREATE TABLE production_run_materials (id UUID PRIMARY KEY DEFAULT gen_random_uuid(), run_id UUID NOT NULL REFERENCES production_runs(id), material_batch_id UUID NOT NULL REFERENCES material_batches(id), planned_quantity NUMERIC NOT NULL, reserved_quantity NUMERIC NOT NULL DEFAULT 0, consumed_quantity NUMERIC NOT NULL DEFAULT 0, phase TEXT NOT NULL, status TEXT NOT NULL CHECK(status IN ('PLANNED','RESERVED','IN_USE','RELEASED')));
CREATE TABLE production_run_machines (id UUID PRIMARY KEY DEFAULT gen_random_uuid(), run_id UUID NOT NULL REFERENCES production_runs(id), machine_id UUID NOT NULL REFERENCES machines(id), planned_start_at TIMESTAMPTZ, planned_end_at TIMESTAMPTZ, actual_start_at TIMESTAMPTZ, actual_end_at TIMESTAMPTZ, status TEXT NOT NULL CHECK(status IN ('RESERVED','RUNNING','RELEASED')));
CREATE TABLE production_run_operators (id UUID PRIMARY KEY DEFAULT gen_random_uuid(), run_id UUID NOT NULL REFERENCES production_runs(id), operator_id UUID NOT NULL REFERENCES operators(id), role TEXT NOT NULL, assigned_at TIMESTAMPTZ NOT NULL DEFAULT now(), released_at TIMESTAMPTZ, status TEXT NOT NULL CHECK(status IN ('ASSIGNED','RELEASED')));
CREATE TABLE output_batches (id UUID PRIMARY KEY DEFAULT gen_random_uuid(), run_id UUID NOT NULL REFERENCES production_runs(id), batch_number TEXT UNIQUE NOT NULL, product_sku TEXT NOT NULL, quantity NUMERIC NOT NULL, status TEXT NOT NULL, created_at TIMESTAMPTZ NOT NULL DEFAULT now());
CREATE TABLE goods_trips (
  id UUID PRIMARY KEY DEFAULT gen_random_uuid(), reference TEXT UNIQUE NOT NULL,
  origin TEXT NOT NULL, destination TEXT NOT NULL, carrier TEXT, current_location TEXT,
  status TEXT NOT NULL CHECK(status IN ('CREATED','PICKED_UP','IN_TRANSIT','DELIVERED','CANCELLED')),
  expected_arrival_at TIMESTAMPTZ, delivered_at TIMESTAMPTZ, created_at TIMESTAMPTZ NOT NULL DEFAULT now()
);
CREATE TABLE trip_location_updates (
  id UUID PRIMARY KEY DEFAULT gen_random_uuid(), trip_id UUID NOT NULL REFERENCES goods_trips(id),
  location TEXT NOT NULL, status TEXT NOT NULL, recorded_at TIMESTAMPTZ NOT NULL DEFAULT now(), recorded_by TEXT
);
CREATE TABLE quality_holds (id UUID PRIMARY KEY DEFAULT gen_random_uuid(), target_type TEXT NOT NULL CHECK(target_type IN ('MATERIAL_BATCH','MACHINE','RUN','OUTPUT_BATCH','UNIT')), target_id UUID NOT NULL, reason_code TEXT NOT NULL, severity TEXT NOT NULL CHECK(severity IN ('WARNING','CRITICAL')), status TEXT NOT NULL CHECK(status IN ('ACTIVE','RELEASED')), raised_at TIMESTAMPTZ NOT NULL DEFAULT now(), raised_by TEXT NOT NULL, released_at TIMESTAMPTZ);
CREATE TABLE production_events (id UUID PRIMARY KEY DEFAULT gen_random_uuid(), event_type TEXT NOT NULL, occurred_at TIMESTAMPTZ NOT NULL, recorded_at TIMESTAMPTZ NOT NULL DEFAULT now(), aggregate_type TEXT NOT NULL, aggregate_id UUID NOT NULL, run_id UUID, material_batch_id UUID, machine_id UUID, operator_id UUID, output_batch_id UUID, traceable_unit_id UUID, previous_state JSONB, new_state JSONB, payload JSONB NOT NULL DEFAULT '{}', actor_type TEXT NOT NULL, actor_id TEXT, correlation_id UUID NOT NULL, causation_event_id UUID);
CREATE TABLE genealogy_edges (id UUID PRIMARY KEY DEFAULT gen_random_uuid(), source_type TEXT NOT NULL, source_id UUID NOT NULL, relationship_type TEXT NOT NULL, target_type TEXT NOT NULL, target_id UUID NOT NULL, run_id UUID, phase TEXT, quantity NUMERIC, occurred_at TIMESTAMPTZ NOT NULL, event_id UUID NOT NULL REFERENCES production_events(id));

-- Correctness lives in the database, not the UI.
CREATE UNIQUE INDEX one_active_material_reservation ON production_run_materials(material_batch_id) WHERE status IN ('RESERVED','IN_USE');
CREATE UNIQUE INDEX one_active_machine_assignment ON production_run_machines(machine_id) WHERE status IN ('RESERVED','RUNNING');
CREATE UNIQUE INDEX one_active_operator_assignment ON production_run_operators(operator_id) WHERE status = 'ASSIGNED';
CREATE INDEX active_holds_by_target ON quality_holds(target_type,target_id) WHERE status = 'ACTIVE';
CREATE INDEX events_by_run_time ON production_events(run_id,occurred_at DESC);
CREATE INDEX genealogy_lookup_source ON genealogy_edges(source_type,source_id,occurred_at DESC);
CREATE INDEX trip_updates_by_trip_time ON trip_location_updates(trip_id,recorded_at DESC);

-- Example reservation sequence (execute with parameters in application code):
-- BEGIN;
-- SELECT * FROM material_batches WHERE id = :batch_id FOR UPDATE;
-- Validate AVAILABLE balance, status, active hold, then INSERT reservation + UPDATE balances + INSERT event.
-- COMMIT; -- publish WebSocket/event consumer notification only after this point.
