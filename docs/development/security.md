## Database Security

RLS (Row Level Security) is currently disabled on `prediction_logs`
and `drift_reports` tables. These tables are written to exclusively
by the FastAPI backend via service role credentials — RLS is not
required for backend-only access.

RLS will be enabled when the Next.js frontend connects directly
to Supabase in Phase 7.