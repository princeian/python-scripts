import re
from geopy.geocoders import Nominatim
import time

all_prov = {'AB','BC','MB','NB','NL','NT','NS','NU','ON','PE','QC','SK','YT'}

ufofile = open('nuforc_reports.csv', 'r', encoding="utf8")
ufofile2 = open('nuforc_reports_c.csv', 'w')

app = Nominatim(user_agent="ufo")

lines = ufofile.readlines()

loc1 = re.compile("\,[. a-zA-Z]+,[a-zA-Z]{2},")
loc2 = re.compile("\,\"[.\- \,()a-zA-Z\/]+\"+,,")
loc3 = re.compile("\,[.\- \,()a-zA-Z\/]+,,")
date_time = re.compile(",(\d\d\d\d-\d\d-\d\dT\d\d:\d\d:\d\d),")
shape_duration = re.compile("\,([a-zA-Z]+),([\- :0-9a-zA-Z.~]+),\"Occurred : ")
latitude = re.compile(",-?\d*\.\d+?,-?\d*\.\d+?$")
city = re.compile("([\-a-zA-Z. ]+) \(")
country = re.compile("\(([a-zA-Z \/]+)\)")

h = re.compile("([0-9]+) *[h|H]")
m = re.compile("([0-9]+) *[m|M]")
s = re.compile("([0-9]+) *[s|S]")

city2 = re.compile(",\"([-a-zA-Z. ]+),")
prov = re.compile(",([\-a-zA-Z ]+) \(")

count = 0
for line in lines:
    loc1_res = re.findall(loc1, line)
    date_time_res = re.findall(date_time, line)
    shape_duration_res = re.findall(shape_duration, line)
    latitude_res = re.findall(latitude, line)

    loc_str = ',,,'
    latitude_str = ',,'
    count += 1
    if len(loc1_res) > 0:
        loc_s = loc1_res[0].split(',')
        prov_str = loc_s[2]
        if prov_str in all_prov:
            loc_str = loc1_res[0]+'Canada'+','
        else:
            loc_str = loc1_res[0]+'USA'+','

        if len(latitude_res) > 0:
            latitude_str = latitude_res[0]
        else:
            city_str = loc_s[1]
            try:
                location = app.geocode(city_str).raw
                latitude_str = ',' + location['lat'] + ',' + location['lon']
                print(str(count) + '-' + city_str + ':' + latitude_str)
            except:
                print('error converting: ' + city_str)
        loc_str = loc_str[1:len(loc_str)]
    else:
        loc3_res = re.findall(loc3, line)        
        if len(loc3_res) > 0:
            loc3_l = loc3_res[0].split(',')
            if len(loc3_l[1]) > 0:
                city_res = re.findall(city, loc3_l[1])
                city_str = city_res[0] if len(city_res) > 0 else ''
                country_res = re.findall(country, loc3_l[1])
                country_str = country_res[0] if len(country_res) > 0 else ''
                loc_str = city_str.strip()+',,'+country_str.strip()+','
                if len(latitude_res) == 0:
                    try:
                        location = app.geocode(city_str).raw
                        latitude_str = ',' + location['lat'] + ',' + location['lon']
                        print(str(count) + '-' + city_str + ':' + latitude_str)
                    except:
                        print('error converting: ' + loc3_l[1])
                
        loc2_res = re.findall(loc2, line)
        if len(loc3_res) == 0 and len(loc2_res) > 0:
            city_res = re.findall(city2, loc2_res[0])
            city_str = city_res[0] if len(city_res) > 0 else ''
            prov_res = re.findall(prov, loc2_res[0])
            prov_str = prov_res[0] if len(prov_res) > 0 else ''
            country_res = re.findall(country, loc2_res[0])
            country_str = country_res[0] if len(country_res) > 0 else ''
            loc_str = city_str.strip()+','+prov_str.strip()+','+country_str.strip()+','
            if len(latitude_res) == 0:
                try:
                    location = app.geocode(city_str).raw
                    latitude_str = ',' + location['lat'] + ',' + location['lon']
                    print(str(count) + '-' + city_str + ':' + latitude_str)
                except:
                    print('error converting: ' + loc2_res[0])
            
    if len(date_time_res) > 0:
        date_time_str = date_time_res[0].replace('T', ' ') + ','
    else:
        date_time_str = ','

    if len(shape_duration_res) > 0:
        shape = shape_duration_res[0][0]
        shape = shape if len(shape) > 0 else 'unknown'                
        duration = shape_duration_res[0][1]
        shape_duration_str = shape_duration_res[0][0]+','+shape_duration_res[0][1]
        h_res = re.findall(h, duration)
        duration2 = int(h_res[0])*3600 if len(h_res) > 0 else 0
        if duration2 == 0:
            m_res = re.findall(m, duration)
            duration2 = int(m_res[0])*60 if len(m_res) > 0 else 0
        if duration2 == 0:
            s_res = re.findall(s, duration)
            duration2 = int(s_res[0]) if len(s_res) > 0 else 0
        if duration2 > 0:
            duration_in_sec = ',' + str(duration2)
        else:
            duration_in_sec = ','
    else:
        shape_duration_str = ','
        duration_in_sec = ','
    
    res_line = loc_str+date_time_str+shape_duration_str+latitude_str+duration_in_sec+'\n'
    if res_line != ',,,,,,,,\n':
        ufofile2.write(loc_str+date_time_str+shape_duration_str+latitude_str+duration_in_sec+'\n')
    
print(count)

ufofile.close()
ufofile2.close()