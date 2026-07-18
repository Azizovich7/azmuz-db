# ⚡ azmuz-db

A zero-config, blazing-fast CLI tool that generates beautiful, interactive Markdown documentation directly from your PostgreSQL database.

Tired of taking screenshots of pgAdmin for your pull requests? `azmuz-db` connects to your local or remote database and builds a clean, FastAPI-style Markdown file (`schema.md`) outlining your tables, columns, required fields, and primary keys.

## 🌟 Why use `azmuz-db`?

- **Interactive Markdown:** Generates collapsible `<details>` sections for each table, keeping your documentation clean and scannable.
- **FastAPI-Style Badges:** Clearly highlights **Required** vs Optional fields and uses 🔑 tags for Primary Keys.
- **Zero Configuration:** Point it at your database connection, and it works instantly. No ORMs or complex config files required.
- **Table of Contents:** Automatically generates anchor links so developers can jump straight to the model they care about.

## 📦 Installation

Install `azmuz-db` globally via pip:

```bash
pip install azmuz-db