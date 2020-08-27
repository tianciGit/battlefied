#-*-coding:utf-8-*-
from enum import Enum
import math, json
import numpy as np

from agent.agent import Agent
from env.env_cmd import EnvCmd
from env.env_def import UnitType, UnitStatus, RED_AIRPORT_ID

AIR_PATROL_HEIGHT = 8000
A2G_PATROL_HEIGHT = 7000
AWACS_PATROL_HEIGHT = 7500
DISTURB_PATROL_HEIGHT = 8500



# 无人机
# 北部侦察阵位(-105000, 65000)--距离北岛约35km, 突击北岛后可快速确认战果.
UAV_POINT1 = [-105000, 65000, 5000]
# 中部待命阵位(-125000, 0)--距离敌南/北岛距离均约88km, 距离己方北部干扰阵位约97km
UAV_POINT2 = [-125000, 0, 5000]
# 中北侦察阵位(-125000, 45000)--北岛南侧约47km, 突击北岛后快速确认战果(备选阵位)
UAV_POINT3 = [-125000, 45000, 5000]
# 中南侦察阵位(-125000, -45000)--南岛北侧约47km, 突击南岛后快速确认战果
UAV_POINT4 = [-125000, -45000, 5000]
# 南部待命阵位(-35000, -85000)--距离南岛约95km(敌地防视线内打击范围外), 距己北部干扰阵位约140km, 起吸引注意力作用
UAV_POINT5 = [-35000, -85000, 5000]
# 南部规避阵位(-35000, -55000)--向北部干扰阵位方向撤退30km
UAV_POINT6 = [-35000, -55000, 5000]
# 南部侦察阵位(-95000, -85000)--南岛东侧约37km, 突击南岛后快速确认战果
UAV_POINT7 = [-95000, -85000, 5000]
UAV_PATROL_PARAMS = [270, 20000, 20000, 190, 7200]
UAV_PATROL_PARAMS_0 = [270, 20000, 20000, 190, 7200, 0]
UAV_PATROL_PARAMS_1 = [270, 20000, 20000, 190, 7200, 1]

# 预警机
# 预警机待命阵位
AWACS_PATROL_POINT = [75000, 60000, AWACS_PATROL_HEIGHT]
# 预警机南部规避阵位
AWACS_SOUTH_POINT = [55000, -30000, AWACS_PATROL_HEIGHT]
# 预警机北部规避阵位
AWACS_NORTH_POINT = [55000, 30000, AWACS_PATROL_HEIGHT]
# dir, len, wid, speed, time, mode:0:air/1:surface/2:both
AWACS_PATROL_PARAMS = [270, 20000, 20000, 160, 7200, 2]

# 空中干扰
# 空中干扰待命阵位
AIR_DISTURB_POINT1 = [45000, 0, DISTURB_PATROL_HEIGHT]
# 空中干扰北部干扰阵位
AIR_DISTURB_POINT2 = [-45000, 55000, DISTURB_PATROL_HEIGHT]
# 空中干扰北部干扰规避阵位
AIR_DISTURB_POINT3 = [-25000, 55000, DISTURB_PATROL_HEIGHT]
# 空中干扰南部干扰阵位
AIR_DISTURB_POINT4 = [-45000, -55000, DISTURB_PATROL_HEIGHT]
# 空中干扰南部干扰规避阵位
AIR_DISTURB_POINT5 = [-25000, -55000, DISTURB_PATROL_HEIGHT]


# 北部航线干扰
class Point():
    def __init__(self, x, y, z):
        self.x = x
        self.y = y
        self.z = z


# NORTH_LINE = [{'x':45000,'y':0,'z':8500},{'x':-45000,'y':55000,'z':8500}]
NORTH_LINE = [Point(45000, 0, 8500), Point(25000, 50000, 8500), Point(-45000, 55000, 8500)]
# 南部航线干扰
# SOUTH_LINE = [{'x':-45000,'y':55000,'z':8500},{'x':-45000,'y':-55000,'z':8500}]
SOUTH_LINE = [Point(-45000, 55000, 8500), Point(-45000, -55000, 8500)]

DISTURB_PATROL_PARAMS = [270, 10000, 10000, 160, 7200]  # direction,length,width,speed,disturb_time,



# 护卫舰
# 北部巡逻阵位
SHIP_POINT1 = [45000, 25000, 0]
# 中部巡逻阵位
SHIP_POINT2 = [15000, 0, 0]
# 南部巡逻阵位
SHIP_POINT3 = [55000, -45000, 0]
SHIP_PATROL_PARAMS_0 = [90, 20000, 20000, 190, 7200, 0]



# 对空作战
AIR_PATROL_POINT1 = [-65000, 25000, AIR_PATROL_HEIGHT]
AIR_PATROL_POINT2 = [-65000, 35000, AIR_PATROL_HEIGHT]
AIR_PATROL_POINT3 = [-65000, 45000, AIR_PATROL_HEIGHT]
AIR_PATROL_POINT4 = [-75000, 25000, AIR_PATROL_HEIGHT]
AIR_PATROL_POINT5 = [-85000, 25000, AIR_PATROL_HEIGHT]
AIR_PATROL_POINT6 = [-95000, 25000, AIR_PATROL_HEIGHT]
AIR_PATROL_POINT7 = [-95000, -85000, AIR_PATROL_HEIGHT]
AIR_PATROL_POINT8 = [-35000, -85000, AIR_PATROL_HEIGHT]

# 北部警戒阵位1(-65000, 25000)--距离北部突击阵位约40AIR_PATROL_POINT7 = [-95000, -85000, AIR_PATROL_HEIGHT]km
# AIR_PATROL_POINT1 = [-65000, 25000, AIR_PATROL_HEIGHT]
# 北部警戒阵位2(-95000, 55000)--距离北部突击阵位约40km
# AIR_PATROL_POINT2 = [-95000, 55000, AIR_PATROL_HEIGHT]
# 中部阻援/集结阵位(-105000, 0)--距离南/北部干扰阵位均约78km, 可伏击敌增援北岛战机, 距离南岛约90km, 也是南下的集结阵位
# AIR_PATROL_POINT3 = [-105000, 0, AIR_PATROL_HEIGHT]
# 南部伏击阵位(-45000, -55000)--位于北部干扰阵位约110km(处于保护范围内), 可伏击敌南部出击的飞机
# AIR_PATROL_POINT4 = [-45000, -55000, AIR_PATROL_HEIGHT]
# 南部警戒阵位1(-125000, -45000)--南岛北侧约47km, 距离己南部干扰阵位80km
# AIR_PATROL_POINT5 = [-125000, -45000, AIR_PATROL_HEIGHT]
# 南部警戒阵位2(-105000, -65000)--南岛东北方向约37km
# AIR_PATROL_POINT6 = [-105000, -65000, AIR_PATROL_HEIGHT]
# 南部警戒阵位3(-95000, -85000)--南岛东侧约37km, 距离己南部干扰阵位60km
# AIR_PATROL_POINT7 = [-95000, -85000, AIR_PATROL_HEIGHT]

AIR_PATROL_PARAMS = [270, 10000, 10000, 160, 7200]
AIR_PATROL_PARAMS_0 = [270, 10000, 10000, 160, 7200, 0]
AIR_PATROL_PARAMS_1 = [270, 10000, 10000, 160, 7200, 1]

# 对地海打击
AREA_HUNT_POINT1 = [-65000, 65000, A2G_PATROL_HEIGHT]
AREA_HUNT_POINT2 = [-35000, 65000, A2G_PATROL_HEIGHT]
AREA_HUNT_POINT3 = [-80000, 65000, A2G_PATROL_HEIGHT]
AREA_HUNT_POINT4 = [-65000, 65001, A2G_PATROL_HEIGHT]
AREA_HUNT_POINT4_0 = [-125000, -85000, A2G_PATROL_HEIGHT]
AREA_HUNT_POINT5 = [0, 154000, A2G_PATROL_HEIGHT]
AREA_HUNT_POINT6 = [0, -154000, A2G_PATROL_HEIGHT]
#
# 北部突击阵位(-55000, 65000)--北部干扰阵位的左上区域, 距离北岛约78km
# AREA_HUNT_POINT1 = [-65000, 65000, A2G_PATROL_HEIGHT]
# AREA_HUNT_POINT0 = [-125000, 85000, A2G_PATROL_HEIGHT]
AREA_HUNT_POINT0 = [-129533.05624, 87664.0398, A2G_PATROL_HEIGHT]
# 北部规避阵位(-35000, 65000)--向己方半场后撤20km
# AREA_HUNT_POINT2 = [-35000, 65000, A2G_PATROL_HEIGHT]
# 中部待命阵位(-115000, 0)--距离敌南/北岛距离均约88km, 距离己方北部干扰阵位约90km(处于保护范围内)
# AREA_HUNT_POINT3 = [-115000, 0, A2G_PATROL_HEIGHT]
# 南部突击阵位(-55000, -65000)--南部干扰阵位的左下区域, 距离南岛约78km
# AREA_HUNT_POINT4 = [-55000, -65000, A2G_PATROL_HEIGHT]
# AREA_HUNT_POINT4_0 = [-125000, -85000, A2G_PATROL_HEIGHT]
# AREA_HUNT_POINT4_0 = [-131156.63859, -87887.86736, A2G_PATROL_HEIGHT]  # 南岛坐标
# 南部规避阵位(-35000, -65000)--向己方半场后撤20km


AREA_HUNT_PARAMS = [270, 1000, 1000]
AREA_PATROL_PARAMS = [270, 1000, 1000, 160, 7200]
AREA_HUNT_PARAMS_0 = [270, 1000, 1000, 160, 7200, 0]
AREA_HUNT_PARAMS_1 = [270, 1000, 1000, 160, 7200, 1]

AWACS_PATROL_TIME = 0
AWACS_ESCORT_TIME = 60

DISTURB_PATROL_TIME = 120
DISTURB_ESCORT_TIME = 280

AIR_PATROL_TIME11 = 300
AIR_PATROL_TIME12 = 420
AIR_DISTURB_TIME1 = 480

AIR_PATROL_TIME21 = 900
AIR_PATROL_TIME22 = 1020
AIR_DISTURB_TIME2 = 1080

AIR_PATROL_TIME31 = 1500
AIR_PATROL_TIME32 = 1620
AIR_DISTURB_TIME3 = 1680

AREA_HUNT_TIME11 = 2100
AREA_HUNT_TIME12 = 2400
HUNT_DISTURB_TIME1 = 3000

AREA_HUNT_TIME21 = 2700
AREA_HUNT_TIME22 = 3000
AREA_HUNT_TIME23 = 3300
HUNT_DISTURB_TIME2 = 3600

AIR_ATTACK_PERIOD = 10


class RedAgentState(Enum):
    first_time = 1
    second_time = 2
    AWACS_PATROL = 1
    AWACS_ESCORT = 2

    DISTURB_TAKEOFF = 3
    DISTURB_ESCORT = 4

    AIR_PATROL11 = 11
    AIR_PATROL12 = 12
    AIR_PATROL21 = 13
    AIR_PATROL22 = 14
    AIR_PATROL31 = 15
    AIR_PATROL32 = 16

    AREA_HUNT11 = 21
    AREA_HUNT12 = 22
    AREA_HUNT21 = 23
    AREA_HUNT22 = 24
    AREA_HUNT23 = 25
    AREA_HUNT24 = 26

    AIR_DISTURB1 = 51
    AIR_DISTURB2 = 52
    AIR_DISTURB3 = 53
    AIR_DISTURB4 = 54
    AIR_DISTURB5 = 55

    HUNT_DISTURB1 = 61
    HUNT_DISTURB2 = 62

    # 起飞全部结束
    END_TAKEOFF = 100
    END_DISTURB = 200

global blue_commandpost


class Yemo_Red_Agent(Agent):
    def __init__(self, name, config, **kwargs):
        ''''''
        super().__init__(name, config['side'])

        self._init()

    def _init(self):
        print("重置-红方-Agent!")
        self.aircraft_dict = {}

        self.a2a_list = []
        self.target_ship = {}
        self.ship_target = {}
        self.blue_list = [] #
        self.blue_dic = {} #

        self.attacking_targets = {}

        self.awacs_team_id = -1
        self.disturb_team_id = -1

        self.agent_state = 0
        self.disturb_state = RedAgentState.AIR_DISTURB1 #
        self.area_hurt_a = RedAgentState.AREA_HUNT11 #
        self.area_hurt_b = RedAgentState.AREA_HUNT11
        self.area_hurt_c = RedAgentState.AREA_HUNT11
        self.area_hurt_d = RedAgentState.AREA_HUNT11
        self.air_attack_time = 0
        self.a2g_ha = 0 #
        self.a2g_hb = 0 #
        self.team_id_dic = {} #
        self.Task = {} #
        self.a2a_num = 0
        self.a2g_num = 0

    def reset(self):
        self._init()

    def step(self, sim_time,obs_red,**kwargs):
        '''主攻北岛战略'''
        # 机场剩余战机数量
        if self.a2a_num != int(obs_red['airports'][0]['AIR']):
            print("机场剩余歼击机数量: ", obs_red['airports'][0]['AIR'])
            self.a2a_num = int(obs_red['airports'][0]['AIR'])

        if self.a2g_num != int(obs_red['airports'][0]['BOM']):
            print("机场剩余轰炸机的数量为: ", obs_red['airports'][0]['BOM'])
            self.a2g_num = int(obs_red['airports'][0]['BOM'])

        # 空中剩余战机数量
        Red_LX_list = []
        for a2a in obs_red['units']:
            Red_LX_list.append(a2a['LX'])
        air_a2a = []
        air_a2g = []
        for fighter in Red_LX_list:
            if fighter==11:
                air_a2a.append(fighter)
            elif fighter==15:
                air_a2g.append(fighter)


        # 敌方指挥所信息
        blue_commandpost = {}
        for commandpost in obs_red['qb']:
            if commandpost['LX'] == 41 and commandpost['Y']>0:
                blue_commandpost['north'] = commandpost
            elif commandpost['LX'] == 41 and commandpost['Y']<0:
                blue_commandpost['south'] = commandpost
        # print("敌方指挥所信息: ", blue_commandpost)


        self._parse_teams(obs_red)

        cmd_list = []
        a2a_hit_units = []
        for blue in obs_red['qb']:
            if blue['LX'] == 11 or blue['LX'] == 12 or blue['LX'] == 15:
                a2a_hit_units.append(blue)
        # 找出空中武器的类型列表


        if self.agent_state == 0:
            print("部署护卫舰!")
            index = 1
            for unit in obs_red['units']:
                if unit['LX'] == 21:
                    if index == 1:
                        cmd_list.extend(self._ship_movedeploy(unit['ID'], SHIP_POINT1))
                        print("1号护卫舰就位北部巡逻位置-RED")
                        index += 1
                        continue
                    if index == 2:
                        cmd_list.extend(self._ship_movedeploy(unit['ID'], SHIP_POINT3))
                        print("2号护卫舰就位南部巡逻位置-RED")
                        # index += 1
                        continue
            self.agent_state = 1

        if self.agent_state == 1:
            for awas in obs_red['units']:
                if awas['LX'] == 12:
                    cmd_list.extend(self._awacs_patrol(awas['ID'], AWACS_PATROL_POINT, AWACS_PATROL_PARAMS))
                    print('预警机到(25000, 0, 7500)进行区域巡逻-RED')
                    self.agent_state = 2

        if self.agent_state == 2:
            if 'YA' in list(self.team_id_dic.keys()):
                cmd_list.extend(self._awacs_escort(self.team_id_dic['YA'], 1))
                self.agent_state = 3

        # 干扰机的相关操作
        if self.agent_state == 3:
            cmd_list.extend(self._takeoff_areapatrol(1, 13, AIR_DISTURB_POINT1, DISTURB_PATROL_PARAMS))
            self.agent_state = 4

        if self.agent_state == 4:
            if 'RA' in list(self.team_id_dic.keys()):
                cmd_list.extend(self._disturb_escort(self.team_id_dic['RA'], 2))
                self.agent_state = 5

        if self.agent_state == 5 and sim_time>240:
            cmd_list.extend(self._takeoff_areapatrol(2, 11, AIR_PATROL_POINT8, AREA_PATROL_PARAMS))
            self.agent_state = 6

        if self.agent_state == 6 and sim_time>420:
            cmd_list.extend(self._takeoff_areapatrol(2, 15, AREA_HUNT_POINT1, AREA_PATROL_PARAMS))
            self.agent_state = 7
        if self.agent_state == 7:
            if 'HA' in list(self.team_id_dic.keys()):
                cmd_list.extend(self._A2G_escort(self.team_id_dic['HA'], 2))
                self.agent_state = 8

        if self.agent_state == 8:
            cmd_list.extend(self._takeoff_areapatrol(2, 11, AIR_PATROL_POINT1, AIR_PATROL_PARAMS))
            self.agent_state = 9
        if self.agent_state == 9:
            if 'JE' in list(self.team_id_dic.keys()):
                cmd_list.extend(self._takeoff_areapatrol(2, 11, AIR_PATROL_POINT2, AIR_PATROL_PARAMS))
                self.agent_state = 10
        if self.agent_state == 10:
            if 'JG' in list(self.team_id_dic.keys()):
                cmd_list.extend(self._takeoff_areapatrol(2, 11, AIR_PATROL_POINT3, AIR_PATROL_PARAMS))
                self.agent_state = 11

        if self.agent_state == 11:
            cmd_list.extend(self._takeoff_areahunt(2, AREA_HUNT_POINT0))
            cmd_list.extend(self._takeoff_areahunt(4, AREA_HUNT_POINT0))
            print('轰炸机HB起飞')
            self.agent_state = 12

        if self.agent_state == 12:
            if 'HB' in list(self.team_id_dic.keys()):
                cmd_list.extend(self._A2G_escort(self.team_id_dic['HB'], 2))
                self.agent_state = 13


        if sim_time>1500:
            if 11 not in Red_LX_list and obs_red['airports'][0]['AIR']>=2:
                cmd_list.extend(self._takeoff_areapatrol(2, 11, AIR_PATROL_POINT1, AIR_PATROL_PARAMS))

        if self.agent_state == 13 and sim_time>2400:
            cmd_list.extend(self._takeoff_areapatrol(4, 15, AREA_HUNT_POINT5, AIR_PATROL_PARAMS))
            self.agent_state = 14
        if self.agent_state == 14:
            if 'HC' in list(self.team_id_dic.keys()):
                if obs_red['airports'][0]['AIR']>=2:
                    cmd_list.extend(self._A2G_escort(self.team_id_dic['HC'], 2))
                self.agent_state = 15

        if self.agent_state == 15 and sim_time>3600:
            cmd_list.extend(self._targethunt(self.team_id_dic['HC'], obs_red['qb'][-1]['ID']))
            self.agent_state = 16

        if self.agent_state == 16 and sim_time>5400:
            if 'JF' in list(self.team_id_dic.keys()):
                cmd_list.extend(self._takeoff_areapatrol(4, 15, AREA_HUNT_POINT6, AIR_PATROL_PARAMS))
                self.agent_state = 17

        if self.agent_state == 17:
            if 'HD' in list(self.team_id_dic.keys()):
                cmd_list.extend(self._A2G_escort(self.team_id_dic['HD'], 4))
                self.agent_state = 18

        if self.agent_state == 18 and sim_time>6600:
            cmd_list.extend(self._targethunt(self.team_id_dic['HD'], blue_commandpost['south']['ID']))
            self.agent_state = 19


        for ship in obs_red['qb']:
            if ship['LX'] == 21 and ship['DA']<67:
                for a2g in obs_red['units']:
                    if a2g['LX']==15:
                        if a2g['Fuel']>3000 and '360' in list(a2g['WP'].keys()) and int(a2g['WP']['360'])>0:
                            distance = math.sqrt(math.pow(a2g['X'] - ship['X'], 2) + math.pow(a2g['Y'] - ship['Y'], 2))
                            if sim_time>6300:
                                if distance<80000:
                                    cmd_list.extend(self._targethunt(a2g['ID'], ship['ID']))
                                    print("红方轰炸机{0}攻击敌方护卫舰!".format(a2g['ID']))
                            else:
                                if distance<75000:
                                    cmd_list.extend(self._targethunt(a2g['ID'], ship['ID']))
                                    print("红方轰炸机{0}攻击敌方护卫舰!".format(a2g['ID']))
                        else:
                            cmd_list.extend(self._returntobase(a2g['ID']))


        # 如果敌方北岛附近舰船失去作战能力派出所有轰炸机攻击北岛,并所有歼击机进行护航
        # 如果北岛指挥所被打掉, 战机补给, 对北岛发动一次性进攻
        for ship in obs_red['qb']:
            if ship['LX'] == 21  and ship['DA']>=66:  # 舰船失去能力
                if 15 not in Red_LX_list:  # 空中轰炸机被打掉, 则派所有的轰炸机进行攻击
                    print("{0}机场剩余轰炸机数量为: {1}".format(sim_time, obs_red['airports'][0]['BOM']))

        blue_zhs = []
        for zhs in obs_red['qb']:
            if zhs['LX']==41:
                blue_zhs.append(zhs)
        if len(blue_zhs)==1:
            if sim_time>8990:
                print("蓝方剩余一个指挥所!")
        elif len(blue_zhs)==0:
            if sim_time > 8990:
                print("蓝方指挥所全部被打掉!")






        # 拦截
        for blue_unit in obs_red['qb']:
            # 获取蓝方单位并且是存活状态
            if blue_unit['LX'] == 11 or blue_unit['LX'] == 15 or blue_unit['LX'] == 12:  # 打掉歼击机,轰炸机,预警机
                if blue_unit['WH'] == 1 and blue_unit['ID'] not in self.blue_list:
                    dic_distance = {}
                    for a2a in obs_red['units']:
                        if a2a['LX'] == 11 and a2a['Fuel'] > 3000 and '170' in list(a2a['WP'].keys()) and int(a2a['WP']['170']) > 0:
                            distance = math.sqrt(math.pow(a2a['X'] - blue_unit['X'], 2) + math.pow(a2a['Y'] - blue_unit['Y'], 2))
                            dic_distance[distance] = a2a
                    list_distance = list(dic_distance.keys())
                    list_distance.sort()

                    # 派一架架飞机去拦截
                    for dis in list_distance:
                        if dis <= 70000:
                            cmd_list.extend(self._airattack(dic_distance[dis]['ID'], blue_unit['ID']))
                            self.blue_list.append(blue_unit['ID'])
                            self.blue_dic[dic_distance[dis]['ID']] = blue_unit['ID']
                            break

        # 红方将蓝方单位击落或者红方拦截飞机被蓝方击落
        blue = 0
        del_blue = False
        del_blue2 = False
        for blue_target in self.blue_list:
            for blue_unit in obs_red['qb']:
                if blue_target == blue_unit['ID']:
                    blue = 1  # 判断目标还在不在
                    break
            for a2a_id in list(self.blue_dic.keys()):  # 判断歼击机在打哪架飞机
                for a2a in obs_red['units']:  #
                    if a2a['ID'] == a2a_id:
                        del_blue = True  # 检查我方歼击机是否存在
                        break
                if del_blue is False:
                    self.blue_dic.pop(a2a_id)  # 如果不存在的话,就将这个编队删掉
            for a2a_id in list(self.blue_dic.keys()):
                if blue_target == self.blue_dic[a2a_id]:  # 查一下打他的飞机还在不在
                    del_blue2 = True  # 还有别的飞机在攻击这个目标
                    break
            if blue == 0 or del_blue is False or del_blue2 is False:
                # blue为0表示被打掉或者情报丢失
                self.blue_list.remove(blue_target)
                # 需根据红方飞机当前状态重新下指令
                for a2a in obs_red['units']:
                    # 遍历我方飞机谁在攻击当前的这个目标,因为目标没了,需要重新分配飞机指令
                    # 此时对状态为15 或 13 的蓝方飞机进行判断
                    if a2a['LX'] == 11 and a2a['ID'] in list(self.blue_dic.keys()) and self.blue_dic[
                        a2a['ID']] == blue_target:
                        if a2a['ST'] == 15 or a2a['ST'] == 13:
                            # 如果油量小于4000或者子弹数量为0则返航，否者去预定区域进行区域巡逻
                            if a2a['Fuel'] < 4000 or int(a2a['WP']['170']) == 0:
                                cmd_list.extend(self._returntobase(a2a['ID']))
                                print("红方歼击机{0}返航!".format(a2a['ID']))
                            else:
                                for Tid in list(self.team_id_dic.keys()):
                                    if a2a['TMID'] == self.team_id_dic[Tid]:
                                        if Tid == 'JA':
                                            cmd_list.extend(self._areapatrol(a2a['ID'], AWACS_PATROL_POINT,
                                                                             AIR_PATROL_PARAMS_0))
                                            print("歼击机前往预警机待命阵位巡逻-RED")
                                        if Tid == 'JB':
                                            cmd_list.extend(self._areapatrol(a2a['ID'], AIR_DISTURB_POINT2,
                                                                             AIR_PATROL_PARAMS_0))
                                            print("歼击机前往北部干扰阵位-RED")
                                        if Tid == 'JC':
                                            cmd_list.extend(self._areapatrol(a2a['ID'], AIR_PATROL_POINT1,AIR_PATROL_PARAMS_0))
                                            print("歼击机在北部警戒阵位1(-65000, 25000)--距离北部突击阵位约40km 区域巡逻-RED")
                                        if Tid == 'JD':
                                            cmd_list.extend(self._areapatrol(a2a['ID'], AIR_PATROL_POINT2,
                                                                             AIR_PATROL_PARAMS_0))
                                            print("歼击机在北部警戒阵位2(-95000, 55000)--距离北部突击阵位约40km 区域巡逻-RED")
                                        if Tid == 'JE':
                                            cmd_list.extend(self._areapatrol(a2a['ID'], AIR_PATROL_POINT3, AIR_PATROL_PARAMS_0))
                                            print("JE歼击机中部阻援/集结阵位(-105000, 0)--距离南/北部干扰阵位均约78km, 可伏击敌增援北岛战机, 距离南岛约90km, 也是南下的集结阵位处区域巡逻-RED")
                                        if Tid == 'JF':
                                            cmd_list.extend(self._areapatrol(a2a['ID'], AIR_PATROL_POINT3, AIR_PATROL_PARAMS_0))
                                            print("JF歼击机中部阻援/集结阵位(-105000, 0)--距离南/北部干扰阵位均约78km, 可伏击敌增援北岛战机, 距离南岛约90km, 也是南下的集结阵位处区域巡逻-RED")
                                        if Tid == 'JG':
                                            cmd_list.extend(self._areapatrol(a2a['ID'], AIR_PATROL_POINT5, AIR_PATROL_PARAMS_0))
                                            print("歼击机在南部警戒阵位1(-125000, -45000)--南岛北侧约47km, 距离己南部干扰阵位80km区域巡逻-RED")
                                        if Tid == 'JH':
                                            cmd_list.extend(self._areapatrol(a2a['ID'], AIR_PATROL_POINT6,
                                                                             AIR_PATROL_PARAMS_0))
                                            print("歼击机在南部警戒阵位2(-105000, -65000)--南岛东北方向约37km区域巡逻-RED")
                                        if Tid == 'JI':
                                            cmd_list.extend(self._areapatrol(a2a['ID'], AIR_PATROL_POINT7,
                                                                             AIR_PATROL_PARAMS_0))
                                            print(
                                                "JI歼击机在南部警戒阵位3(-95000, -85000)--南岛东侧约37km, 距离己南部干扰阵位60km区域巡逻-RED")
                                        if Tid == 'JJ':
                                            cmd_list.extend(self._areapatrol(a2a['ID'], AIR_PATROL_POINT7,
                                                                             AIR_PATROL_PARAMS_0))
                                            print(
                                                "JJ歼击机在南部警戒阵位3(-95000, -85000)--南岛东侧约37km, 距离己南部干扰阵位60km区域巡逻-RED")
                                        if Tid == 'JK':
                                            cmd_list.extend(self._areapatrol(a2a['ID'], AIR_PATROL_POINT7,AIR_PATROL_PARAMS_0))
                                            print(
                                                "JK歼击机在南部警戒阵位3(-95000, -85000)--南岛东侧约37km, 距离己南部干扰阵位60km区域巡逻-RED")
                                        if Tid == 'JL':
                                            cmd_list.extend(self._areapatrol(a2a['ID'], AIR_PATROL_POINT4,AIR_PATROL_PARAMS_0))
                                            print("歼击机在南部伏击阵位(-45000, -55000)--位于北部干扰阵位约110km(处于保护范围内)区域巡逻, 可伏击敌南部出击的飞机-RED")

        if sim_time>8990:
            print("self.team_id_dic is ", self.team_id_dic)
            print("空中剩余歼击机数量为: ", len(air_a2a))
            print("空中剩余轰炸机数量为: ", len(air_a2g))
            print("机场歼击机数量为: ", obs_red['airports'][0]['AIR'])
            print("机场轰炸机数量为: ", obs_red['airports'][0]['BOM'])
        return cmd_list

    # 获取编队ID
    def _parse_teams(self, red_dict):
        for team in red_dict['teams']:
            if team['Task']:
                self.Task = json.loads(team['Task'])

            # 预警机编队
            if team['LX'] == UnitType.AWACS:
                self.team_id_dic['YA'] = team['TMID']

            # 干扰机编队
            elif team['LX'] == UnitType.DISTURB:
                if 'fly_num' in list(self.Task.keys()):
                    if self.Task['point_x'] == AIR_DISTURB_POINT1[0] and self.Task['point_y'] == AIR_DISTURB_POINT1[1]:
                        self.team_id_dic['RA'] = team['TMID']

            # 轰炸机编队
            elif team['LX'] == UnitType.A2G:
                if 'fly_num' in list(self.Task.keys()) and team['Task']:

                    if self.Task['fly_num'] and self.Task['point_x'] == AREA_HUNT_POINT1[0] and self.Task['point_y'] == AREA_HUNT_POINT1[1]:
                        self.team_id_dic['HA'] = team['TMID']
                    # HB
                    elif self.Task['fly_num'] and self.Task['point_x'] == AREA_HUNT_POINT0[0] and self.Task['point_y'] == AREA_HUNT_POINT0[1]:
                        # 北岛指挥所坐标
                        self.team_id_dic['HB'] = team['TMID']
                    # HC
                    elif self.Task['fly_num'] and self.Task['point_x'] == AREA_HUNT_POINT5[0] and self.Task['point_y'] == AREA_HUNT_POINT5[1]:
                        self.team_id_dic['HC'] = team['TMID']
                    # HD
                    elif self.Task['fly_num'] and self.Task['point_x'] == AREA_HUNT_POINT6[0] and self.Task['point_y'] == AREA_HUNT_POINT6[1]:
                        self.team_id_dic['HD'] = team['TMID']

            # 歼击机编队
            elif team['LX'] == UnitType.A2A and len(self.Task) > 0:
                if self.Task['maintype'] == 'takeoffprotect':
                    print("self.team_id_dic is ", self.team_id_dic)
                    print("self.Task is ", self.Task)
                    # JA
                    if self.Task['cov_id'] == self.team_id_dic['YA']:
                        self.team_id_dic['JA'] = team['TMID']
                    # JB
                    elif self.Task['cov_id'] == self.team_id_dic['RA']:
                        self.team_id_dic['JB'] = team['TMID']
                    # JC
                    elif self.Task['cov_id'] == self.team_id_dic['HA']:
                        self.team_id_dic['JC'] = team['TMID']
                    # JD
                    elif self.Task['cov_id'] == self.team_id_dic['HB']:
                        self.team_id_dic['JD'] = team['TMID']
                    # JF

                    elif self.Task['cov_id'] == self.team_id_dic['HC']:
                        self.team_id_dic['JF'] = team['TMID']
                    # JL
                    elif self.Task['cov_id'] == self.team_id_dic['HD']:
                        self.team_id_dic['JL'] = team['TMID']
                elif 'fly_num' in list(self.Task.keys()):
                    # JE
                    if self.Task['fly_num'] and self.Task['point_x'] == AIR_PATROL_POINT1[0] and self.Task['point_y'] == AIR_PATROL_POINT1[1]:
                        self.team_id_dic['JE'] = team['TMID']
                    # JG
                    if self.Task['fly_num'] and self.Task['point_x'] == AIR_PATROL_POINT2[0] and self.Task['point_y'] == AIR_PATROL_POINT2[1]:
                        self.team_id_dic['JG'] = team['TMID']
                    # JH
                    if self.Task['fly_num'] and self.Task['point_x'] == AIR_PATROL_POINT3[0] and self.Task['point_y'] == AIR_PATROL_POINT3[1]:
                        self.team_id_dic['JH'] = team['TMID']
                    # JI
                    if self.Task['fly_num'] and self.Task['point_x'] == AIR_PATROL_POINT4[0] and self.Task['point_y'] == AIR_PATROL_POINT4[1]:
                        self.team_id_dic['JI'] = team['TMID']
                    # JJ
                    if self.Task['fly_num'] == 2 and self.Task['point_x'] == AIR_PATROL_POINT5[0] and self.Task['point_y'] == AIR_PATROL_POINT5[1]:
                        self.team_id_dic['JJ'] = team['TMID']
                    # JK
                    if self.Task['fly_num'] == 2 and self.Task['point_x'] == AIR_PATROL_POINT6[0] and self.Task['point_y'] == AIR_PATROL_POINT6[1]:
                        self.team_id_dic['JK'] = team['TMID']

                    if self.Task['fly_num'] and self.Task['point_x'] == AIR_PATROL_POINT8[0] and self.Task['point_y'] == AIR_PATROL_POINT8[1]:
                        self.team_id_dic['JL'] = team['TMID']


    # 计算距离
    @staticmethod
    def _get_distance(x1, y1, z1, x2, y2, z2):
        point1 = np.array([x1, y1, z1])
        point2 = np.array([x2, y2, z2])
        return np.sqrt(sum(np.power((point2 - point1), 2)))

    @staticmethod
    def _get_distance2(point_list1, point_list2):
        point1 = np.array(point_list1)
        point2 = np.array(point_list2)
        return np.sqrt(sum(np.power((point2 - point1), 2)))

    # 区域巡逻
    @staticmethod
    def _areapatrol(unit_id, patrol_point, patrol_params):
        print("红方{0}-区域巡逻-位置:{1}".format(unit_id, patrol_point))
        return [EnvCmd.make_areapatrol(unit_id, *patrol_point, *patrol_params)]

    # 起飞区域巡逻
    @staticmethod
    def _takeoff_areapatrol(num, lx, patrol_point, patrol_params):
        print("红方-执行-起飞区域巡逻-指令!起飞数量为: {0}!, 起飞战机类型为: {1}!".format(str(num), str(lx)))
        return [EnvCmd.make_takeoff_areapatrol(RED_AIRPORT_ID, num, lx, *patrol_point, *patrol_params)]

    # 航线巡逻(适用于飞机编队)
    @staticmethod
    def _make_linepatrol(self_id, speed, point_list):
        print("红方-{0}-航线干扰-指令!".format(self_id))
        return [EnvCmd.make_linepatrol(self_id, speed, 0, 'line', point_list)]


    # 起飞航线巡逻
    @staticmethod
    def _make_takeoff_linepatrol():
        pass

    # 轰炸机区域突击
    @staticmethod
    def _areahunt(self_id, point):
        print("红方-轰炸机-{0}-区域 突击-{1}!".format(self_id, point))
        return [EnvCmd.make_areahunt(self_id, 270, 80, *point, *AREA_HUNT_PARAMS)]

    # 轰炸机起飞区域突击
    @staticmethod
    def _takeoff_areahunt(num, area_hunt_point):
        print("红方-轰炸机 执行-起飞区域突击-指令!起飞数量为: {0}!".format(str(num)))
        return [EnvCmd.make_takeoff_areahunt(RED_AIRPORT_ID, num, 270, 80, *area_hunt_point, *[270, 1000, 1000, 160])]

    # 轰炸机目标突击
    @staticmethod
    def _targethunt(self_id, target_id):
        print("红方-轰炸机-{0}-目标 突击-{1}!".format(self_id, target_id))
        return [EnvCmd.make_targethunt(self_id, target_id, 270, 80)]

    # 起飞目标突击
    @staticmethod
    def _make_takeoff_targethunt(num, target_id, direction):
        return [EnvCmd.make_takeoff_targethunt(RED_AIRPORT_ID, num, target_id, direction, 55, 175)]

    # 预警机护航
    @staticmethod
    def _awacs_escort(awacs_team_id, num):
        print("红方-派{0}架歼击机-护航-预警机!".format(num))
        return [EnvCmd.make_takeoff_protect(RED_AIRPORT_ID, num, awacs_team_id, 0, 10, 180)]

    # 干扰机护航
    @staticmethod
    def _disturb_escort(disturb_team_id, num):
        print("红方-起飞护航指令-护航干扰机! 起飞数量: 2")
        return [EnvCmd.make_takeoff_protect(RED_AIRPORT_ID, num, disturb_team_id, 1, 20, 170)]

    # 轰炸机护航
    @staticmethod
    def _A2G_escort(a2g_team_id, num):
        print("红方-起飞护航指令-护航轰炸机! 起飞数量: {0}".format(num))
        return [EnvCmd.make_takeoff_protect(RED_AIRPORT_ID, num, a2g_team_id, 1, 20, 170)]

    # 歼击机空中拦截
    @staticmethod
    def _airattack(unit_id, target_id):
        print("红方歼击机-{0}-空中拦截-{1}".format(str(unit_id), str(target_id)))
        return [EnvCmd.make_airattack(unit_id, target_id, 0)]

    # 返航
    @staticmethod
    def _returntobase(unit_id):
        print('红方-{0}-返航!'.format(unit_id))
        return [EnvCmd.make_returntobase(unit_id, 30001)]

    # 护卫舰初始化部署
    @staticmethod
    def _ship_movedeploy(self_id, point):
        print("红方-护卫舰初始部署!")
        return [EnvCmd.make_ship_movedeploy(self_id, *point, 90, 1)]

    # 舰船添加制定目标
    @staticmethod
    def _ship_addtarget():
        pass
    # 舰船移除指定目标
    @staticmethod
    def _ship_removetarget():
        pass
    # 舰船雷达开关机
    @staticmethod
    def _ship_radarcontrol():
        pass
    # 舰船区域巡逻防控
    @staticmethod
    def _ship_areapatrol():
        pass

    # 预警机区域巡逻
    @staticmethod
    def _awacs_patrol(self_id, AWACS_PATROL_POINT, AWACS_PATROL_PARAMS):
        return [EnvCmd.make_awcs_areapatrol(self_id, *AWACS_PATROL_POINT, *AWACS_PATROL_PARAMS)]

    # 预警机航线巡逻
    @staticmethod
    def _awcs_linepatrol(self_id, point_list):
        print("红方预警机-航线巡逻")
        return [EnvCmd.make_awcs_linepatrol(self_id, 250, 0, 'line', point_list)]

    # 预警机探测模式
    @staticmethod
    def _make_awcs_mode(self_id, mode):
        y_mode = ''
        if mode==0:
            y_mode = "红方预警机-对空-探测"
        elif mode==1:
            y_mode = "红方预警机-对海-探测"
        elif mode==2:
            y_mode = "红方预警机-海空交替-探测"
        return [EnvCmd.make_awcs_mode(self_id, mode)]

    # 预警机雷达开关机
    @staticmethod
    def _awcs_radarcontrol(self_id, on_off):
        if on_off==0:
            print("红方预警机雷达-开!")
        if on_off==1:
            print("蓝方预警机雷达-关!")
        return [EnvCmd.make_awcs_radarcontrol(self_id, on_off)]

    # 预警机探测任务取消
    @staticmethod
    def _awcs_canceldetect(self_id):
        print("红方预警机-探测任务取消!")
        return [EnvCmd.make_awcs_canceldetect(self_id)]

    # 干扰机进行区域干扰
    @staticmethod
    def _disturb_patrol(disturb_team_id, patrol_point, patrol_params):
        print("红方-干扰机 执行-区域干扰-指令!")
        return [EnvCmd.make_disturb_areapatrol(disturb_team_id, *patrol_point, *patrol_params)]

    # 干扰机进行航线干扰,
    @staticmethod
    def _disturb_linepatrol(self_id, point_list):
        print("红方-干扰机 执行-航线干扰-指令! 完成后在终点附近盘旋!")
        return [EnvCmd.make_disturb_linepatrol(self_id, 160, 0, 'line', point_list)]

    # 干扰机关闭干扰
    @staticmethod
    def _disturb_close(self_id):
        return [EnvCmd.make_disturb_close(self_id)]
    # 干扰机结束干扰
    @staticmethod
    def _disturb_stop(self_id):
        return [EnvCmd.make_disturb_stop(self_id)]


    # 无人机区域巡逻侦查
    @staticmethod
    def _uav_areapatrol(uav_id, uav_point, uav_params):
        return [EnvCmd.make_uav_areapatrol(uav_id, *uav_point, *uav_params)]



    # 护卫舰区域巡逻
    @staticmethod
    def _ship_areapatrol( self_id, point):
        print("红方-护卫舰-区域巡逻防空!")
        return [EnvCmd.make_ship_areapatrol(self_id, *point, *SHIP_PATROL_PARAMS_0)]


