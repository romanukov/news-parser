from django_db_geventpool.backends.postgresql_psycopg2 import base
import tsvector_field


class DatabaseWrapper(base.DatabaseWrapper):
    SchemaEditorClass = tsvector_field.DatabaseSchemaEditor
