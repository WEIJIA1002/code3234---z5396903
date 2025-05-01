from flask import Flask, render_template, request, jsonify
import pandas as pd
import openai
import os

app = Flask(__name__)

# 设置 OpenAI API Key
OPENAI_API_KEY = "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"
openai.api_key = OPENAI_API_KEY

# 处理 CSV 文件并生成分析报告
def analyze_csv(file_path):
    try:
        df = pd.read_csv(file_path)
        sample_data = df.head(10).to_csv(index=False)
        response = openai.ChatCompletion.create(
            model="gpt-4",
            messages=[{"role": "system", "content": "Analyze the following CSV data and provide insights."},
                      {"role": "user", "content": sample_data}]
        )
        return response["choices"][0]["message"]["content"]
    except Exception as e:
        return f"Error processing CSV: {e}"

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/analyze', methods=['POST'])
def analyze():
    if 'file' not in request.files:
        return jsonify({'error': 'No file uploaded'}), 400
    file = request.files['file']
    if file.filename == '':
        return jsonify({'error': 'No selected file'}), 400
    file_path = os.path.join("uploads", file.filename)
    file.save(file_path)
    
    # 读取 CSV 并准备图表数据
    df = pd.read_csv(file_path)
    chart_data = {
    "labels": df["Property Type"].tolist(),
    "values": df["Price ($)"].tolist(),
    "landSizes": df["Land Size (sqm)"].tolist()
    }

    
    result = analyze_csv(file_path)
    return jsonify({'result': result, 'chartData': chart_data})

@app.route("/init_data", methods=["GET"])
def init_data():
    file_path = "static/data/house_property_data.csv"  # 新的简洁命名路径

    try:
        df = pd.read_csv(file_path)

        chart_data = {
            "labels": df["Property Type"].tolist(),
            "values": df["Price ($)"].tolist()
        }

        result = analyze_csv(file_path)
        return jsonify({"result": result, "chartData": chart_data})
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route("/compare_regions", methods=["POST"])
def compare_regions():
    
    region1 = request.form.get("region1", "Region 1")
    region2 = request.form.get("region2", "Region 2")
    preferences = request.form.get("preferences", "[]")
    preferences = eval(preferences) if preferences else []
    
    custom_data_text = ""
    if 'customFile' in request.files:
        file = request.files['customFile']
        if file.filename.endswith(".csv"):
            df = pd.read_csv(file)
            custom_data_text = df.head(10).to_csv(index=False)
        elif file.filename.endswith(".xlsx"):
            df = pd.read_excel(file)
            custom_data_text = df.head(10).to_csv(index=False)

    prompt = ""
    if custom_data_text:
        prompt += (
            f"The user has uploaded the following data for reference:\n"
            f"{custom_data_text}\n\n"
        )

    prompt += (
    f"You're helping a user compare two areas for potential living in New South Wales.\n\n"
    f"Please respond using the following format:\n"
    f"Region 1 Analysis:\n[...]\n\n"
    f"Region 2 Analysis:\n[...]\n\n"
    f"In conclusion:\n[...]\n\n"
    f"The areas are:\n- Region 1: {region1}\n- Region 2: {region2}\n"
    f"The user's preferences include: {', '.join(preferences)}.\n"
    f"Compare both areas based on those preferences and recommend which one is more suitable."
    f"Also include:\nRegion 1 Average Price: $xxx\nRegion 2 Average Price: $xxx\n"
    )
    


    try:
        response = openai.ChatCompletion.create(
            model="gpt-4",
            messages=[
                {"role": "system", "content": "You're a helpful urban planning assistant."},
                {"role": "user", "content": prompt}
            ]
        )
        result_text = response["choices"][0]["message"]["content"]
        return jsonify({"result": result_text})
    except Exception as e:
        return jsonify({"error": str(e)}), 500

if __name__ == '__main__':
    if not os.path.exists("uploads"):
        os.makedirs("uploads")
    app.run(debug=True)


