import os
import tempfile
from flask import Flask, render_template, request
import pyarrow.parquet as pq
import json

app = Flask(__name__)

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/process_parquet', methods=['POST'])
def process_parquet():
    if 'file' not in request.files:
        return "No file uploaded."

    uploaded_file = request.files['file']

    try:
        temp_dir = tempfile.mkdtemp()
        temp_file_path = os.path.join(temp_dir, "uploaded_file.parquet")

        uploaded_file.save(temp_file_path)

        table = pq.read_table(temp_file_path)
        df = table.to_pandas()
        table_html = df.head(10).to_html(index=False, classes="table table-striped")

        return render_template('result.html', table=table_html)
    except Exception as e:
        return f"Error processing the Parquet file: {str(e)}"

@app.route('/get_schema', methods=['POST'])
def get_schema():
    try:
        if 'file' not in request.files:
            return "No file uploaded."

        uploaded_file = request.files['file']

        temp_dir = tempfile.mkdtemp()
        temp_file_path = os.path.join(temp_dir, "uploaded_file.parquet")

        uploaded_file.save(temp_file_path)

        schema = pq.read_schema(temp_file_path)

        # Convert the schema to a list of dictionaries
        schema_list = [{'Column': field.name, 'Type': str(field.type)} for field in schema]

        schema_json = json.dumps(schema_list, indent=2)
        return schema_json.replace('\n', '<br>')
    except Exception as e:
        return f"Error getting the Parquet schema: {str(e)}"

if __name__ == '__main__':
    app.run(debug=True)
