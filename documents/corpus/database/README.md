# Operational database export

Export date: 2026-07-21
System: Operational database
Format: CSV

## Tables

| Table | Rows |
|---|---|
| customer_history.csv | 2600 |
| customers.csv | 400 |
| employees.csv | 13 |
| invoices.csv | 2600 |
| jobs.csv | 2600 |
| pricing_history.csv | 4 |
| roster_history.csv | 89 |

## Join keys

- `customer_id` joins jobs/invoices to customers; `customer_name` is the denormalized display name.
- `tech_emp_id` on jobs joins to employees (`employee_id`); `tech_name` is the denormalized display name.
- `service_id` joins jobs/invoices to pricing_history.
- `job_id` joins invoices to jobs.