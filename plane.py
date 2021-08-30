"""
对飞行器飞行过程中油耗问题进行建模
"""
import matplotlib.pyplot as plt
import numpy as np


class FuelTank:
    """
    邮箱建模
    """
    def __init__(self, length=0, width=0, height=0, init_volume=0.0, 
                 center_x=0, center_y=0, center_z=0, max_speed=0.0):
        self.length = length
        self.width = width
        self.height = height
        self.volume = init_volume ### 初始容量
        self.max_speed = max_speed
        
        ### 邮箱质心
        self.x = center_x
        self.y = center_y
        self.z = center_z
            
    def consume(self, t, consume_speed): ### 耗油
        volume = self.volume - t*consume_speed 
        assert volume >=0, 'not enough fuel to consume'
        self.volume = volume
    
    def charge(self, t, consume_speed):  ### 加油
        volume = self.volume + t*consume_speed
        self.volume = volume
    
    def pose(self, theta=0):
        """
        邮箱姿态，根据角度和油量计算邮箱的质心
        """
        Vol = self.length*self.width*self.height ### 总容积
        if theta == 0:
            ### 单独考虑无角度
            x_bias = self.x
            y_bias = self.y
            z_bias = self.z - 1/2*(self.height-self.volume/(self.length*self.width))
            return x_bias, y_bias, z_bias
        ### 倾斜情况
        abs_theta = abs(theta) ### theta为正负时具有对称性，x坐标关于中心对称
        
        l1 = np.sqrt(2*self.volume/(self.width*np.tan(theta))) ### 三角形界面
        l2 = np.sqrt(2*(Vol-self.volume)/(self.width*np.tan(theta))) ### 五边形截面
        l3 = (self.volume-1/2*self.length**2*self.width*np.tan(theta))/(self.length*self.width) ### 四边形截面
        l4 = (self.volume-1/2*self.height**2*self.width/np.tan(theta))/(self.width*self.height)
        if l1<= self.length and l1*np.tan(theta) <= self.height:
            ### 三角形截面
            if theta > 0:
                x_bias = self.x-1/2*self.length+1/3*l1
            else:
                x_bias = self.x + 1/2*self.length - 1/3*l1
            y_bias = self.y
            z_bias = self.z-1/2*self.height+1/3*l1*np.tan(theta)
        elif l4 <= self.length and l4*np.tan(theta) <= self.height:
            ### 五边形截面
            if theta > 0:
                x_bias = self.x-1/2*self.length+1/self.volume*(1/2*Vol*self.length-(Vol-self.volume)*(self.length-1/3*l2))
            else:
                x_bias = self.x+1/2*self.length-1/self.volume*(1/2*Vol*self.length-(Vol-self.volume)*(self.length-1/3*l2))
            y_bias = self.y
            z_bias = self.z-1/2*self.height+1/self.volume*(1/2*Vol*self.height-(Vol-self.volume)*(self.height-1/3*l2*np.tan(theta)))
        elif l3 >= 0 and l3 < self.height:
            ### 四边形截面并且没淹没油箱高
            if theta>0:
                x_bias = self.x - 1/2*self.length + 1/2*self.length - self.length**3*self.width*np.tan(theta)/(12*self.volume)
            else:
                x_bias = self.x + 1/2*self.length - 1/2*self.length + self.length**3*self.width*np.tan(theta)/(12*self.volume)
            y_bias = self.y
            z_bias = self.z - 1/2*self.height+ self.volume(2*self.length*self.width) + self.length**3*self.width*np.tan(theta)**2/(24*self.volume)
        elif l4 >= 0 and l4 <= self.length:
            ### 四边形截面并且淹没油箱长
            if theta > 0:
                x_bias = self.x - 1/2*self.length + self.volume(2*self.width*self.height) + self.width*self.height**3/(24*self.volume*np.tan(theta)**2)
            else:
                x_bias = self.x + 1/2*self.length - self.volume(2*self.width*self.height) - self.width*self.height**3/(24*self.volume*np.tan(theta)**2)
            y_bias = self.y
            z_bias = 1/2*self.height - self.width*self.height**3/(12*self.volume*np.tan(theta))
        else:
            raise Exception('No such case')
            
        return x_bias, y_bias, z_bias

class Plane:
    def __init__(self, mass, rho):
        ### 建模飞机
        self.mass = mass
        self.rho = rho ### 油密度
        self.add_fueltank() ### 添加邮箱
        self.center_x = 0.0
        self.center_y = 0.0
        self.center_z = 0.0 ### 初始化质心坐标
    
    def add_fueltank(self):
        ### 解析油箱，省略从xlsx文件读取过程，直接填入数值，待后续优化
        ft1 = FuelTank(1.5, 0.9, 0.3, 0.3, 8.9130435, 1.20652174, 0.61669004, 1.1)
        ft2 = FuelTank(2.2, 0.8, 1.1, 1.5, 6.9130435, -1.39347826, 0.21669004, 1.8)
        ft3 = FuelTank(2.4, 1.1, 0.9, 2.1, -1.686957, 1.20652174, -0.28330996, 1.7)
        ft4 = FuelTank(1.7, 1.3, 1.2, 1.9, 3.1130345, 0.60652174, -0.18330996, 1.5)
        ft5 = FuelTank(2.4, 1.2, 1.0, 2.6, -5.286957, -0.29347826, 0.41669004, 1.6)
        ft6 = FuelTank(2.4, 1.0, 0.5, 0.8, -2.086957, -1.49347826, 0.21669004, 1.1)
        self.fueltanks = [ft1, ft2, ft3, ft4, ft5, ft6]
    
    def move(self, t, speeds):
        """
        飞机移动，更新邮箱油量，同时更新
        :param t: time_interval
        :param speeds: 所有邮箱输油速度
        :param theta: 俯仰角度
        """
        ### 1号给二号补油
        self.fueltanks[0].consume(t, consume_speed=speeds[0]/self.rho)
        self.fueltanks[1].charge(t, consume_speed=speeds[0]/self.rho)
        ### 2号消耗
        self.fueltanks[1].consume(t, consume_speed=speeds[1]/self.rho)
        ### 3号消耗
        self.fueltanks[2].consume(t, consume_speed=speeds[2]/self.rho)
        ### 4号消耗
        self.fueltanks[3].consume(t, consume_speed=speeds[3]/self.rho)
        ### 6号消耗给5号补油
        self.fueltanks[5].consume(t, consume_speed=speeds[5]/self.rho)
        self.fueltanks[4].charge(t, consume_speed=speeds[5]/self.rho)
        ### 5号消耗
        self.fueltanks[4].consume(t, consume_speed=speeds[4]/self.rho)
    
    def compute_center(self, theta):
        """
        计算瞬时质心坐标
        """
        total_mass = self.mass
        x_accu = 0 ### 累积x偏移
        y_accu = 0 ### 累积y偏移
        z_accu = 0 ### 累积z偏移
        if theta == 0:
            for fueltank in self.fueltanks:
                x_bias, y_bias, z_bias = fueltank.pose(theta) ### 计算油箱坐标
                x_accu += fueltank.volume*self.rho*x_bias
                y_accu += fueltank.volume*self.rho*y_bias
                z_accu += fueltank.volume*self.rho*z_bias
                total_mass += fueltank.volume*self.rho
            self.center_x = x_accu / total_mass
            self.center_y = y_accu / total_mass
            self.center_z = z_accu / total_mass
        else:
            pass ### 当飞机倾斜时，油面水平，需要进行计算
    
    def travel(self, fuel_curve, theta_curve, plot=False):
        """
        旅行函数，根据输入供油曲线和角度曲线，返回质心曲线
        """
        center_x_curve = []
        center_y_curve = []
        center_z_curve = [] ### 初始质心曲线
        for i in range(fuel_curve.shape[0]):
            t = 1 ### 1s采集一次
            speeds = fuel_curve[i, 1:] ### 供油
            theta = theta_curve[i, 1]
            self.move(t, speeds)
            self.compute_center(theta=0) ### theta=theta_curve[i, 1]
            center_x_curve.append(self.center_x)
            center_y_curve.append(self.center_y)
            center_z_curve.append(self.center_z)
        
        if plot:
            ### 描绘质心曲线
            plt.figure(figsize=(8, 6))
            ts = fuel_curve[:, 0]
            plt.plot(ts, center_x_curve,  label='x center', linewidth=1.0)
            plt.plot(ts, center_y_curve,  label='y center', linewidth=1.0)
            plt.plot(ts, center_z_curve,  label='z center', linewidth=1.0)
            plt.title('X, Y, Z Center Curve of Plane')
            plt.legend()
            # plt.show()
            plt.savefig('results/Q1.png')
        return center_x_curve, center_y_curve, center_z_curve


if __name__ == '__main__':
    from utils.parse_xlsx import *
    fuel_curve, theta_curve = parse_Q1(file_path='data/data_Q1.xlsx')
    plane = Plane(mass=3000, rho=850)
    xs, ys, zs = plane.travel(fuel_curve, theta_curve, plot=True)
    print(xs[:100])
            
            
            
                
        