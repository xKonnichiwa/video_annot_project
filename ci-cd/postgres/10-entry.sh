psql db_name -U postgres -c "alter user postgres with encrypted password 'pass';"
psql db_name -U postgres -c "grant all privileges on database db_name to postgres;"

psql db_name -U postgres < /sql/dump.sql