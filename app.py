import os
import tempfile
from flask import Flask, render_template, request
from pyspark.sql import SparkSession
import json

app = Flask(__name__)

# Create a SparkSession
spark = SparkSession.builder.appName("Parquet +Viewer").getOrCreate()

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

        df1 = spark.read.parquet(temp_file_path)

        table_html = df1.limit(10).toPandas().to_html(index=False, classes="table table-striped")

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

        df1 = spark.read.parquet(temp_file_path)

        schema_json = df1.schema.json()

        schema_pretty = json.dumps(json.loads(schema_json), indent=2)
        return schema_pretty.replace('\n', '<br>') 
    except Exception as e:
        return f"Error getting the DataFrame schema: {str(e)}"

if __name__ == '__main__':
    app.run(debug=True)
