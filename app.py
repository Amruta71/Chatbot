from flask import Flask, render_template, request, jsonify, redirect, url_for
import pandas as pd
import seaborn as sns
import matplotlib.pyplot as plt
import io
import base64
import os

app = Flask(__name__)

# File path for user data storage
file_path = "user_data.csv"
if not os.path.exists(file_path):
    user_df = pd.DataFrame(columns=["age", "salary", "name", "address", "email_id", "mobile_no"])
    user_df.to_csv(file_path, index=False)
else:
    user_df = pd.read_csv(file_path)

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/add_data', methods=['POST'])
def add_data():
    # Add new data to the DataFrame
    new_data = pd.DataFrame({
        "age": [request.form['age']],
        "salary": [request.form['salary']],
        "name": [request.form['name']],
        "address": [request.form['address']],
        "email_id": [request.form['email_id']],
        "mobile_no": [request.form['mobile_no']]
    })
    global user_df
    user_df = pd.concat([user_df, new_data], ignore_index=True)
    user_df.to_csv(file_path, index=False)
    return redirect(url_for('index'))

def plot_data(df):
    # Plot age and salary distributions
    plt.figure(figsize=(12, 5))
    plt.subplot(1, 2, 1)
    sns.histplot(df['age'], bins=10, kde=True, color='skyblue')
    plt.title('Age Distribution')
    plt.xlabel('Age')
    plt.ylabel('Frequency')

    plt.subplot(1, 2, 2)
    sns.histplot(df['salary'], bins=10, kde=True, color='salmon')
    plt.title('Salary Distribution')
    plt.xlabel('Salary')
    plt.ylabel('Frequency')

    plt.tight_layout()
    img = io.BytesIO()
    plt.savefig(img, format='png')
    img.seek(0)
    plot_url = base64.b64encode(img.getvalue()).decode()
    plt.close()
    return plot_url

@app.route('/chat', methods=['POST'])
def chat():
    user_input = request.json.get("message").lower()
    response = ""

    # Ensure age and salary columns are numeric for calculations
    user_df["age"] = pd.to_numeric(user_df["age"], errors="coerce")
    user_df["salary"] = pd.to_numeric(user_df["salary"], errors="coerce")

    if "average age" in user_input:
        avg_age = user_df["age"].mean()
        response = f"The average age is {avg_age:.2f}."

    elif "average salary" in user_input:
        avg_salary = user_df["salary"].mean()
        response = f"The average salary is {avg_salary:.2f}."

    elif "plot" in user_input or "graph" in user_input:
        plot_url = plot_data(user_df)
        response = f"<img src='data:image/png;base64,{plot_url}'/>"

    elif "show data" in user_input:
        table_html = user_df.to_html(classes='table table-bordered table-striped', index=False)
        response = f"<h4>Employee Data</h4>{table_html}"

    elif "salary above" in user_input:  # For salary filtering
        salary_limit = int(user_input.split("salary above")[1].strip())
        filtered_data = user_df[user_df['salary'] > salary_limit]
        table_html = filtered_data.to_html(classes='table table-bordered table-striped', index=False)
        response = f"<h4>Employees with salary above {salary_limit}</h4>{table_html}"

    elif "find employees in" in user_input:  # For address filtering
        location = user_input.split("find employees in")[1].strip()
        filtered_data = user_df[user_df['address'].str.contains(location, case=False, na=False)]
        table_html = filtered_data.to_html(classes='table table-bordered table-striped', index=False)
        response = f"<h4>Employees in {location}</h4>{table_html}"

    elif "exit" in user_input:
        response = "Goodbye! Refresh the page if you want to start over."

    else:
        response = "I can help with average age, average salary, show data, or show plots. Type 'exit' to end."

    return jsonify({"response": response})

@app.route('/show_data')
def show_data():
    # Convert the user data to HTML table format
    table_html = user_df.to_html(classes='table table-bordered table-striped', index=False)
    return render_template('index.html', data=table_html)

if __name__ == '__main__':
    app.run(debug=True)
