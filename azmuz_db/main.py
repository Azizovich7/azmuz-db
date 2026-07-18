import argparse
import psycopg2
import sys

class PostgresDocumenter:
    def __init__(self, host, port, dbname, user, password):
        try:
            self.conn = psycopg2.connect(
                host=host, port=port, dbname=dbname, user=user, password=password
            )
            self.cursor = self.conn.cursor()
        except psycopg2.Error as e:
            print(f"Error connecting to the database: {e}")
            sys.exit(1)

    def get_tables(self):
        self.cursor.execute("""
            SELECT table_name 
            FROM information_schema.tables 
            WHERE table_schema = 'public' AND table_type = 'BASE TABLE'
            ORDER BY table_name;
        """)
        return [row[0] for row in self.cursor.fetchall()]

    def get_primary_keys(self, table_name):
        """Finds the primary keys for a given table to make docs look professional."""
        self.cursor.execute("""
            SELECT kcu.column_name
            FROM information_schema.table_constraints tco
            JOIN information_schema.key_column_usage kcu 
              ON kcu.constraint_name = tco.constraint_name
              AND kcu.constraint_schema = tco.constraint_schema
            WHERE tco.constraint_type = 'PRIMARY KEY'
              AND tco.table_name = %s;
        """, (table_name,))
        return [row[0] for row in self.cursor.fetchall()]

    def get_columns(self, table_name):
        self.cursor.execute("""
            SELECT column_name, data_type, is_nullable, column_default
            FROM information_schema.columns
            WHERE table_schema = 'public' AND table_name = %s
            ORDER BY ordinal_position;
        """, (table_name,))
        return self.cursor.fetchall()

    def generate_markdown(self, output_file):
        tables = self.get_tables()
        
        try:
            with open(output_file, 'w', encoding='utf-8') as f:
                f.write("# ⚡ Database Schema Documentation\n\n")
                f.write("> Automatically generated from PostgreSQL using `azmuz-db`.\n\n")
                
                if not tables:
                    f.write("*No tables found in the public schema.*\n")
                    return

                f.write("## 📌 Models Overview\n\n")
                for table in tables:
                    f.write(f"- [`{table}`](#{table})\n")
                f.write("\n---\n\n")

                for table in tables:
                    pks = self.get_primary_keys(table)
                    columns = self.get_columns(table)
                    
                    f.write(f"<a id=\"{table}\"></a>\n")
                    f.write(f"### {table}\n\n")
                    f.write("<details>\n")
                    f.write(f"<summary><strong>View Schema ({len(columns)} columns)</strong></summary>\n\n")
                    f.write("| Name | Type | Attributes | Default |\n")
                    f.write("|---|---|---|---|\n")
                    
                    for col in columns:
                        name, dtype, nullable, default = col
                        
                        is_pk = "🔑 **PK**<br>" if name in pks else ""
                        req_status = "Optional" if nullable == 'YES' else "**Required**"
                        attributes = f"{is_pk}{req_status}"
                        default_val = f"`{str(default).replace('|', '&#124;')}`" if default else "_"
                        
                        f.write(f"| `{name}` | `{dtype}` | {attributes} | {default_val} |\n")
                    
                    f.write("\n</details>\n\n---\n\n")
            
            print(f"Success! Beautiful schema documentation generated at: {output_file}")
            
        except IOError as e:
            print(f"Error writing to file: {e}")
            
        finally:
            self.cursor.close()
            self.conn.close()

def main():
    # Update prog to reflect the new CLI command name
    parser = argparse.ArgumentParser(
        prog="azmuz-db",
        description="Generate beautiful, FastAPI-style Markdown documentation from a PostgreSQL database."
    )
    
    parser.add_argument('--host', type=str, default='localhost', help='Database host (default: localhost)')
    parser.add_argument('--port', type=str, default='5432', help='Database port (default: 5432)')
    parser.add_argument('--db', type=str, required=True, help='Database name')
    parser.add_argument('--user', type=str, required=True, help='Database user')
    parser.add_argument('--password', type=str, required=True, help='Database password')
    parser.add_argument('--out', type=str, default='schema.md', help='Output Markdown file path (default: schema.md)')

    args = parser.parse_args()

    documenter = PostgresDocumenter(
        host=args.host, port=args.port, dbname=args.db, user=args.user, password=args.password
    )
    documenter.generate_markdown(args.out)

if __name__ == "__main__":
    main()