# IT Job Trends – Airflow DAGs

This repository contains the Apache Airflow DAGs powering the **IT Job Trends** project (formerly known as the *hh project*), which collects and analyzes data from the HeadHunter (HH) job board API to provide real-time insights into the IT job market in Uzbekistan.

## 🧠 What is IT Job Trends?

**IT Job Trends** is an open-source initiative to track, analyze, and publish trends in the Uzbekistani IT job market. It scrapes public vacancy data from [hh.uz](https://hh.uz), processes and filters them for relevance, and loads the results into a PostgreSQL database hosted on [Supabase](https://supabase.com).

Use cases include:
- Monitoring demand for specific roles (e.g., backend, frontend, data).
- Tracking salary distributions over time.
- Highlighting in-demand skills and technologies.

## ⚙️ How the Airflow App Works

This app runs scheduled workflows using Apache Airflow to automate the end-to-end data pipeline.

### Key Features
- **Scheduled Fetching**: Periodically retrieves new job listings from the HH API.
- **Delta Collection**: Only fetches vacancies published *after* the latest stored vacancy to avoid duplicates.
- **Data Filtering & Preprocessing**: Keeps only relevant jobs and extracts structured data.
- **Database Loading**: Inserts cleaned data into a normalized PostgreSQL schema on Supabase.
- **Modular Design**: Utilities and database logic are separated for maintainability and testing.

### DAG Overview

- `hh_vacancies`: Main DAG responsible for:
  - Fetching roles to track
  - Retrieving newly published vacancies
  - Filtering relevant ones
  - Splitting nested data (skills, addresses, salaries, etc.)
  - Inserting into the database

## 🧰 Tech Stack

| Component       | Tool/Service                    |
|----------------|---------------------------------|
| Data Source     | [HeadHunter API](https://dev.hh.ru/) |
| Orchestration   | Apache Airflow (via Astronomer) |
| Backend DB      | PostgreSQL (hosted on Supabase) |
| Environment     | Python 3.12, Airflow DAGs       |
| Deployment      | Astronomer Runtime (Local/Cloud)|

## 🗃️ Database Schema

The database includes the following normalized tables:
- `job`
- `employer`
- `salary`
- `address`
- `job_languages`
- `job_skills`
- `job_roles`
- `roles`
- `areas`

See `models/index.py` for SQLAlchemy model definitions and refer to your Supabase schema for more.