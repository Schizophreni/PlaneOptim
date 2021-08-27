"""
解析各个excel函数集合
"""
import pandas as pd
import numpy as np


def parse_Q1(file_path='../data/data_Q1.xlsx'):
    print('[!!!] Parse excel file: {}'.format(file_path))
    fuel_curve = pd.read_excel(file_path) ### 读取供油曲线
    theta_curve = pd.read_excel(file_path, '飞行器俯仰角')
    
    fuel_curve = np.array(fuel_curve) ### 时间，1号，2号，...，6号
    theta_curve = np.array(theta_curve) ### 时间，角度
    return fuel_curve, theta_curve
    