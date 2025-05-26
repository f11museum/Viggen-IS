
import numpy
import math
import os

def get_bearing(lat1, long1, lat2, long2):
    lat1 = float(lat1)
    long1 = float(long1)
    lat2 = float(lat2)
    long2 = float(long2)
    
    dLon = (long2 - long1)
    x = math.cos(math.radians(lat2)) * math.sin(math.radians(dLon))
    y = math.cos(math.radians(lat1)) * math.sin(math.radians(lat2)) - math.sin(math.radians(lat1)) * math.cos(math.radians(lat2)) * math.cos(math.radians(dLon))
    brng = numpy.arctan2(x,y)
    brng = numpy.degrees(brng)

    return brng
    
def calcHeadding(lat_begin, lon_begin, lat_end, lon_end):
    return 123

def writeCSV(aptlist):
    # id;lat;lon;a_heading;a_lat;a_lon;a_heading;a_lat;a_lon;a_heading;a_lat;a_lon;a_heading;a_lat;a_lon;a_heading;a_lat;a_lon
    
    
    with open("apt.csv", "w") as csv_file:
        for apt in aptlist:
            id = apt["id"]
            
            alt = apt["alt"]
            lat = 0.0
            lon = 0.0
            a_heading = 0
            a_compass = 0
            a_surf = 0
            a_lat = 0.0
            a_lon = 0.0
            a_lat2 = 0.0
            a_lon2 = 0.0
            b_heading = 0
            b_compass = 0
            b_surf = 0
            b_lat = 0.0
            b_lon = 0.0
            b_lat2 = 0.0
            b_lon2 = 0.0
            c_heading = 0
            c_compass = 0
            c_surf = 0
            c_lat = 0.0
            c_lon = 0.0
            c_lat2 = 0.0
            c_lon2 = 0.0
            d_heading = 0
            d_compass = 0
            d_surf = 0
            d_lat = 0.0
            d_lon = 0.0
            d_lat2 = 0.0
            d_lon2 = 0.0
            e_heading = 0
            e_compass = 0
            e_surf = 0
            e_lat = 0.0
            e_lon = 0.0
            e_lat2 = 0.0
            e_lon2 = 0.0
            
            
            if(len(apt["runways"]) >=1):
                lat = apt["runways"][0]["lat_begin"]
                lon = apt["runways"][0]["lon_begin"]
                
                a_heading = apt["runways"][0]["heading"]
                a_lat = apt["runways"][0]["lat_begin"]
                a_lon = apt["runways"][0]["lon_begin"]
                a_lat2 = apt["runways"][0]["lat_end"]
                a_lon2 = apt["runways"][0]["lon_end"]
                a_compass = apt["runways"][0]["compass"]
                a_surf = apt["runways"][0]["surf"]
            if(len(apt["runways"]) >=2):
                b_heading = apt["runways"][1]["heading"]
                b_lat = apt["runways"][1]["lat_begin"]
                b_lon = apt["runways"][1]["lon_begin"]
                b_lat2 = apt["runways"][1]["lat_end"]
                b_lon2 = apt["runways"][1]["lon_end"]
                b_compass = apt["runways"][1]["compass"]
                b_surf = apt["runways"][1]["surf"]
            if(len(apt["runways"]) >=3):
                c_heading = apt["runways"][2]["heading"]
                c_lat = apt["runways"][2]["lat_begin"]
                c_lon = apt["runways"][2]["lon_begin"]
                c_lat2 = apt["runways"][2]["lat_end"]
                c_lon2 = apt["runways"][2]["lon_end"]
                c_compass = apt["runways"][2]["compass"]
                c_surf = apt["runways"][2]["surf"]
            if(len(apt["runways"]) >=4):
                d_heading = apt["runways"][3]["heading"]
                d_lat = apt["runways"][3]["lat_begin"]
                d_lon = apt["runways"][3]["lon_begin"]
                d_lat2 = apt["runways"][3]["lat_end"]
                d_lon2 = apt["runways"][3]["lon_end"]
                d_compass = apt["runways"][3]["compass"]
                d_surf = apt["runways"][3]["surf"]
            if(len(apt["runways"]) >=5):
                e_heading = apt["runways"][4]["heading"]
                e_lat = apt["runways"][4]["lat_begin"]
                e_lon = apt["runways"][4]["lon_begin"]
                e_lat2 = apt["runways"][4]["lat_end"]
                e_lon2 = apt["runways"][4]["lon_end"]
                e_compass = apt["runways"][4]["compass"]
                e_surf = apt["runways"][4]["surf"]
            
            csv_file.write(id)
            csv_file.write(";")
            csv_file.write(str(alt))
            csv_file.write(";")
            csv_file.write(str(lat))
            csv_file.write(";")
            csv_file.write(str(lon))
            csv_file.write(";")
            csv_file.write(str(a_heading))
            csv_file.write(";")
            csv_file.write(str(a_compass))
            csv_file.write(";")
            csv_file.write(str(a_surf))
            csv_file.write(";")
            csv_file.write(str(a_lat))
            csv_file.write(";")
            csv_file.write(str(a_lon))
            csv_file.write(";")
            csv_file.write(str(a_lat2))
            csv_file.write(";")
            csv_file.write(str(a_lon2))
            csv_file.write(";")
            csv_file.write(str(b_heading))
            csv_file.write(";")
            csv_file.write(str(b_compass))
            csv_file.write(";")
            csv_file.write(str(b_surf))
            csv_file.write(";")
            csv_file.write(str(b_lat))
            csv_file.write(";")
            csv_file.write(str(b_lon))
            csv_file.write(";")
            csv_file.write(str(b_lat2))
            csv_file.write(";")
            csv_file.write(str(b_lon2))
            csv_file.write(";")
            csv_file.write(str(c_heading))
            csv_file.write(";")
            csv_file.write(str(c_compass))
            csv_file.write(";")
            csv_file.write(str(c_surf))
            csv_file.write(";")
            csv_file.write(str(c_lat))
            csv_file.write(";")
            csv_file.write(str(c_lon))
            csv_file.write(";")
            csv_file.write(str(c_lat2))
            csv_file.write(";")
            csv_file.write(str(c_lon2))
            csv_file.write(";")
            csv_file.write(str(d_heading))
            csv_file.write(";")
            csv_file.write(str(d_compass))
            csv_file.write(";")
            csv_file.write(str(d_surf))
            csv_file.write(";")
            csv_file.write(str(d_lat))
            csv_file.write(";")
            csv_file.write(str(d_lon))
            csv_file.write(";")
            csv_file.write(str(d_lat2))
            csv_file.write(";")
            csv_file.write(str(d_lon2))
            csv_file.write(";")
            csv_file.write(str(e_heading))
            csv_file.write(";")
            csv_file.write(str(e_compass))
            csv_file.write(";")
            csv_file.write(str(e_surf))
            csv_file.write(";")
            csv_file.write(str(e_lat))
            csv_file.write(";")
            csv_file.write(str(e_lon))
            csv_file.write(";")
            csv_file.write(str(e_lat2))
            csv_file.write(";")
            csv_file.write(str(e_lon2))
            csv_file.write(";")
            
            csv_file.write("\n")
def createAptDict(textdata):
    textdata = "1 "+textdata
    out = {}
    lines = textdata.split("\n")
    
    firstLine = lines[0].split(" ")
    if (len(firstLine)>4):
        lines[0] = lines[0].replace("   ", " ")
        lines[0] = lines[0].replace("  ", " ")
        out["id"] = lines[0].split(" ")[4]
        print("hej",out["id"],"hopp", lines[0])
        print(lines[0].split(" ")[0])
        print(lines[0].split(" ")[1])
        print(lines[0].split(" ")[2])
        print(lines[0].split(" ")[3])
        print(lines[0].split(" ")[4])
        out["alt"] = lines[0].split(" ")[1]
        
        out["runways"] = []
        for line in lines:
            if (line.startswith("100 ")):
                runway = {}
                lin = line.split(" ")
                if (len(lin)>19):
                    runway["heading"] = lin[8]
                    runway["lat_begin"] = lin[9]
                    runway["lon_begin"] = lin[10]
                    
                    runway["lat_end"] = lin[18]
                    runway["lon_end"] = lin[19]
                    try:
                        runway["compass"] = get_bearing(runway["lat_begin"], runway["lon_begin"], runway["lat_end"], runway["lon_end"])
                    except:
                        runway["compass"] = runway["heading"]
                    runway["surf"] = lin[2]
                    out["runways"].append(runway)
                else:
                    print("error", firstLine)
        if(out["id"] == "ESKN"):    
            #print(textdata)
            print("start")
            print(out)
            print("end")
    return out

def readAptFile(filename):
    list = []
    with open(filename, "r", encoding="ISO-8859-1") as apt_file:
        data = apt_file.read().split("\n1    ")
        print("Airports found: ",len(data))
        apt_file.close()
        i = 0
        for d in data:
            d = d.replace("   ", " ")
            d = d.replace("  ", " ")
            x = createAptDict(d)
            if ("id" in x):
                list.append(x)
            # i = i+1
            # if i>5:
            #     break
    return list
#alist = []    
#alist = readAptFile("apt.dat")

#writeCSV(alist)



def findAllAptDatFiles(root_folder):
    apt_files = []
    for dirpath, dirnames, filenames in os.walk(root_folder):
        for file in filenames:
            if file.lower() == "apt.dat":
                full_path = os.path.join(dirpath, file)
                apt_files.append(full_path)
    return apt_files

# MAIN EXECUTION
root_folder = "/home/burns/X-Plane 12/"  # 👈 replace with your folder path
all_airports = []

apt_files = findAllAptDatFiles(root_folder)
print(f"Total apt.dat files found: {len(apt_files)}")

for apt_file in apt_files:
    airports = readAptFile(apt_file)
    all_airports.extend(airports)

writeCSV(all_airports)
