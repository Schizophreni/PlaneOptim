"""
对飞行器飞行过程中油耗问题进行建模
"""

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
        self.x = x
        self.y = y
        self.z = z
    
    def consume(self, t, consume_speed): ### 耗油
        volume = self.volume - t*consume_spped 
        assert volume >=0, 'not enough fuel to consume'
        self.volume = volume
    
    def charge(self, t, consume_speed):  ### 加油
        volume = self.volume + t*consume_speed
        self.volume = volume

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
    
    def move(self, t, speeds, theta):
        """
        飞机移动，更新邮箱油量
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
                x_accu += fueltank.volume*self.rho*fueltank.x
                y_accu += fueltank.volume*self.rho*fueltank.y
                fuel_center_z = fueltank.z - 1/2*(fueltank.height - fueltank.volume/(fueltank.length*fueltank.width)) ### 油的z坐标
                z_accu += fueltank.volume*self.rho*fuel_center_z
                total_mass += fueltank.volume*self.rho
            self.center_x = x_accu / total_mass
            self.center_y = y_accu / total_mass
            self.center_z = z_accu / total_mass
        else:
            pass ### 当飞机倾斜时，油面水平，需要进行计算
            
            
                
        