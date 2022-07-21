import streamlit as st
import pandas as pd
from PIL import Image
import subprocess
import os
import base64
import pickle

# Molecular descriptor calculator
def desc_calc():
    # Performs the descriptor calculation
    bashCommand = "java -Xms2G -Xmx2G -Djava.awt.headless=true -jar ./PaDEL-Descriptor/PaDEL-Descriptor.jar -removesalt -standardizenitro -fingerprints -descriptortypes ./PaDEL-Descriptor/PubchemFingerprinter.xml -dir ./ -file descriptors_output.csv"
    process = subprocess.Popen(bashCommand.split(), stdout=subprocess.PIPE)
    output, error = process.communicate()
    os.remove('molecule.smi')

# File download
def filedownload(df):
    csv = df.to_csv(index=False)
    b64 = base64.b64encode(csv.encode()).decode()  # strings <-> bytes conversions
    href = f'<a href="data:file/csv;base64,{b64}" download="prediction.csv">下载预测结果</a>'
    return href

# Model building
def build_model(input_data):
    # Reads in saved regression model
    load_model = pickle.load(open('acetylcholinesterase_model.pkl', 'rb'))
    # Apply model to make predictions
    prediction = load_model.predict(input_data)
    st.header('**预测结果**')
    prediction_output = pd.Series(prediction, name='pIC50')
    molecule_name = pd.Series(load_data[1], name='molecule_name')
    df = pd.concat([molecule_name, prediction_output], axis=1)
    st.write(df)
    st.markdown(filedownload(df), unsafe_allow_html=True)

# Logo image
image = Image.open('logo.png')

st.image(image, use_column_width=True)

# Page title
st.markdown("""
# 生物活性预测应用程序（乙酰胆碱酯酶）

这个应用程序允许您预测抑制“乙酰胆碱酯酶”的生物活性。 ”乙酰胆碱酯酶“是阿尔茨海默病的药物靶点。

**Credits**
- 该应用使用 `Python` + `Streamlit` 制作 [左政]
- 分子描述符计算使用： [PaDEL-Descriptor](http://www.yapcwsoft.com/dd/padeldescriptor/) [[原文链接]](https://doi.org/10.1002/jcc.21707).
---
""")

# Sidebar
with st.sidebar.header('1. 上传您的CSV数据'):
    uploaded_file = st.sidebar.file_uploader("上传您的输入文件", type=['txt'])
    st.sidebar.markdown("""
[输入样例](https://raw.githubusercontent.com/Zheng-Zuo/Bioactivity_Prediction/main/example_acetylcholinesterase.txt)
""")

if st.sidebar.button('预测'):
    load_data = pd.read_table(uploaded_file, sep=' ', header=None)
    load_data.to_csv('molecule.smi', sep = '\t', header = False, index = False)

    st.header('**原始输入数据**')
    st.write(load_data)

    with st.spinner("正在计算分子描述符..."):
        desc_calc()

    # Read in calculated descriptors and display the dataframe
    st.header('**计算所得分子描述符**')
    desc = pd.read_csv('descriptors_output.csv')
    st.write(desc)
    st.write(desc.shape)

    # Read descriptor list used in previously built model
    st.header('**模型中的描述符子集**')
    Xlist = list(pd.read_csv('descriptor_list.csv').columns)
    desc_subset = desc[Xlist]
    st.write(desc_subset)
    st.write(desc_subset.shape)

    # Apply trained model to make prediction on query compounds
    build_model(desc_subset)
else:
    st.info('在侧边栏中上传输入数据开始预测!')
