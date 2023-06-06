from flask import Flask, render_template, request, jsonify
import mysql.connector
import hashlib

app = Flask(__name__)

# MySQL configuration
config = {
    'host': 'database-sample.cqzrtkfghhro.eu-north-1.rds.amazonaws.com',
    'user': 'admin',
    'password': 'bhavini16',
    'database': 'variant'
}

def connect_to_database():
    return mysql.connector.connect(**config)

@app.route('/')
def home_page():
    return render_template('index.html')

@app.route('/variant', methods=['GET'])
def get_variant():
    if 'variant_id' in request.args:
        variant_id = request.args.get('variant_id')
        try:
            variant_id = int(variant_id)
        except ValueError:
            return jsonify({'error': 'Invalid variant ID'})

        connection = connect_to_database()
        cursor = connection.cursor()
        cursor.execute("SELECT * FROM variants WHERE variant_id = %s", (variant_id,))
        variant = cursor.fetchone()
        cursor.close()
        connection.close()

        if variant:
            variant_info = variant[1]
            return render_template('variant.html', variant_id=variant_id, variant_info=variant_info,
                                   Message="Variant ID found")
        else:
            return jsonify({'error': 'Variant ID not found'})

    elif 'variant_info' in request.args:
        variant_info = request.args.get('variant_info')

        connection = connect_to_database()
        cursor = connection.cursor()
        cursor.execute("SELECT * FROM variants WHERE variant_hash = %s", (hash_variant_info(variant_info),))
        variant = cursor.fetchone()
        cursor.close()
        connection.close()

        if variant:
            variant_id = variant[0]
            return render_template('variant.html', variant_id=variant_id, variant_info=variant_info,
                                   Message="Variant info found")
        else:
            return jsonify({'error': 'Variant info not found'})

    elif 'add_entry' in request.args:
        variant_info = request.args['add_entry']
        if variant_info:
            connection = connect_to_database()
            cursor = connection.cursor()
            cursor.execute("SELECT * FROM variants WHERE variant_hash = %s", (hash_variant_info(variant_info),))
            variant = cursor.fetchone()

            if variant:
                variant_id = variant[0]
                cursor.close()
                connection.close()
                return render_template('variant.html', variant_id=variant_id, variant_info=variant_info,
                                       Message="Variant info already exists")
            else:
                cursor.execute("INSERT INTO variants (variant_info, variant_hash) VALUES (%s, %s)",
                               (variant_info, hash_variant_info(variant_info)))
                connection.commit()
                variant_id = cursor.lastrowid
                cursor.close()
                connection.close()
                return render_template('variant.html', variant_id=variant_id, variant_info=variant_info,
                                       Message="Variant info added successfully")
        else:
            return render_template('variant.html', Message="Error: Input cannot be empty")

    else:
        return jsonify({'error': 'Add: No variant_info provided'})

def hash_variant_info(variant_info):
    return hashlib.md5(variant_info.encode('utf-8')).hexdigest()

if __name__ == '__main__':
    app.run()
