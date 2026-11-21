"""
Database Manager for Multi-City Traffic Congestion System.
Uses SQLite for persistent, zero-cost storage.
Preserves existing Bengaluru dataset and isolates city observations.
"""

import os
import sqlite3
import datetime
import html
import pandas as pd

DB_FILE = "traffic_system.db"
BENGALURU_EXCEL = "Bengaluru_Traffic_Condition_Dataset.xlsx"

# City metadata with verified coordinates
CITIES = {
    "Bengaluru": {
        "state": "Karnataka",
        "lat": 12.9716,
        "lon": 77.5946,
        "zoom": 11,
        "hotspots": [
            ("HS01", "Silk Board Junction", 12.9176, 77.6228),
            ("HS02", "Marathahalli Bridge", 12.9592, 77.6974),
            ("HS03", "KR Puram / Tin Factory Junction", 13.0046, 77.6679),
            ("HS04", "Hebbal Flyover", 13.0358, 77.5970),
            ("HS05", "Yeshwanthpur Junction", 13.0280, 77.5380),
            ("HS06", "Goraguntepalya Junction", 13.0285, 77.5250),
            ("HS07", "Electronic City Toll / Elevated Expressway", 12.8452, 77.6602),
            ("HS08", "Bellandur / Iblur Junction", 12.9260, 77.6784),
            ("HS09", "Kadubeesanahalli Junction", 12.9354, 77.6966),
            ("HS10", "Mahadevapura Junction", 12.9916, 77.6978),
            ("HS11", "Domlur Flyover", 12.9609, 77.6412),
            ("HS12", "Richmond Circle", 12.9668, 77.5969),
            ("HS13", "Trinity Circle", 12.9729, 77.6174),
            ("HS14", "Dairy Circle", 12.9430, 77.5967),
            ("HS15", "Banashankari 3rd Stage Junction", 12.9250, 77.5480),
            ("HS16", "Vijayanagar Traffic Junction", 12.9698, 77.5355),
            ("HS17", "Nayandahalli Junction", 12.9500, 77.5165),
            ("HS18", "BEL Circle", 13.0336, 77.5630),
            ("HS19", "Nagawara Junction", 13.0382, 77.6260),
            ("HS20", "Hennur Cross", 13.0355, 77.6467)
        ],
        "ambulance_corridors": [
            ("Silk Board -> St. John's Hospital", "Silk Board Junction", "St. John's Medical College Hospital", 12.9176, 77.6228, 12.9304, 77.6186),
            ("KR Puram -> Manipal Hospital", "KR Puram / Tin Factory Junction", "Manipal Hospital Old Airport Rd", 13.0046, 77.6679, 12.9583, 77.6485),
            ("Hebbal -> Baptist Hospital", "Hebbal Flyover", "Bangalore Baptist Hospital", 13.0358, 77.5970, 13.0232, 77.5912),
            ("Goraguntepalya -> Ramaiah Memorial", "Goraguntepalya Junction", "Ramaiah Memorial Hospital", 13.0285, 77.5250, 13.0306, 77.5658),
            ("Electronic City -> Narayana Hrudayalaya", "Electronic City Toll / Elevated Expressway", "Narayana Institute of Cardiac Sciences", 12.8452, 77.6602, 12.8123, 77.6980)
        ],
        "hospitals": [
            ("Apollo Hospitals (Bannerghatta Road)", 12.8953, 77.5986),
            ("St. John's Medical College Hospital (Hosur Road)", 12.9304, 77.6186),
            ("Manipal Hospital (Old Airport Road)", 12.9583, 77.6485),
            ("Bangalore Baptist Hospital (Bellary Road)", 13.0232, 77.5912),
            ("Ramaiah Memorial Hospital (MSR Nagar)", 13.0306, 77.5658),
            ("Narayana Institute of Cardiac Sciences (Electronic City)", 12.8123, 77.6980),
            ("Fortis Hospital (Bannerghatta Road)", 12.8940, 77.5980),
            ("Bowring and Lady Curzon Hospital (Shivajinagar)", 12.9830, 77.6040)
        ],
        "landmarks": [
            ("Silk Board Junction", 12.9176, 77.6228),
            ("Marathahalli Bridge", 12.9592, 77.6974),
            ("KR Puram / Tin Factory Junction", 13.0046, 77.6679),
            ("Hebbal Flyover", 13.0358, 77.5970),
            ("Yeshwanthpur Junction", 13.0280, 77.5380),
            ("Goraguntepalya Junction", 13.0285, 77.5250),
            ("Electronic City Toll Plaza", 12.8452, 77.6602),
            ("Indiranagar 100 Feet Road", 12.9784, 77.6408),
            ("Koramangala Sony World Signal", 12.9352, 77.6245),
            ("Majestic / Kempegowda Bus Station", 12.9778, 77.5726),
            ("Banashankari 3rd Stage Junction", 12.9250, 77.5480)
        ]
    },
    "Mumbai": {
        "state": "Maharashtra",
        "lat": 19.0760,
        "lon": 72.8777,
        "zoom": 11,
        "hotspots": [
            ("MUM01", "Western Express Highway / Andheri Flyover", 19.1197, 72.8464),
            ("MUM02", "Dadar TT Circle", 19.0178, 72.8478),
            ("MUM03", "Bandra-Kurla Complex (BKC) Junction", 19.0662, 72.8687),
            ("MUM04", "Sion Circle", 19.0375, 72.8617),
            ("MUM05", "Kalanagar Junction (Bandra East)", 19.0596, 72.8459),
            ("MUM06", "Eastern Express Highway / Ghatkopar", 19.0860, 72.9090),
            ("MUM07", "Lower Parel / Senapati Bapat Marg", 18.9950, 72.8290),
            ("MUM08", "Haji Ali Junction", 18.9775, 72.8105),
            ("MUM09", "Thane Teen Hath Naka", 19.1868, 72.9620),
            ("MUM10", "Borivali National Park Junction", 19.2288, 72.8631),
            ("MUM11", "CSMT / Fort Junction", 18.9400, 72.8354),
            ("MUM12", "JVLR / SEEPZ Junction", 19.1278, 72.8767),
            ("MUM13", "Kurla / LBS Marg Junction", 19.0700, 72.8800),
            ("MUM14", "Vashi Toll Naka (Navi Mumbai Entry)", 19.0667, 72.9833),
            ("MUM15", "Worli Naka", 19.0145, 72.8180),
            ("MUM16", "Chembur Naka / Sion-Panvel Highway", 19.0622, 72.8988),
            ("MUM17", "Malad / Link Road Junction", 19.1860, 72.8420),
            ("MUM18", "Mulund Toll Naka", 19.1720, 72.9560),
            ("MUM19", "Juhu Circle", 19.1120, 72.8270),
            ("MUM20", "Santacruz Airport Flyover Junction", 19.0880, 72.8480)
        ],
        "ambulance_corridors": [
            ("Dadar TT -> KEM Hospital Parel", "Dadar TT Circle", "KEM Hospital Parel", 19.0178, 72.8478, 19.0028, 72.8423),
            ("Bandra Kalanagar -> Lilavati Hospital", "Kalanagar Junction (Bandra East)", "Lilavati Hospital Bandra", 19.0596, 72.8459, 19.0515, 72.8290),
            ("Andheri Flyover -> Kokilaben Hospital", "Western Express Highway / Andheri Flyover", "Kokilaben Dhirubhai Ambani Hospital", 19.1197, 72.8464, 19.1311, 72.8252),
            ("Sion Circle -> Sion Hospital", "Sion Circle", "Lokmanya Tilak Municipal General Hospital", 19.0375, 72.8617, 19.0340, 72.8590)
        ],
        "hospitals": [
            ("KEM Hospital (Parel)", 19.0028, 72.8423),
            ("Lilavati Hospital (Bandra West)", 19.0515, 72.8290),
            ("Kokilaben Dhirubhai Ambani Hospital (Andheri West)", 19.1311, 72.8252),
            ("Lokmanya Tilak Municipal General Hospital (Sion)", 19.0340, 72.8590),
            ("Bombay Hospital (Marine Lines)", 18.9410, 72.8290),
            ("Tata Memorial Hospital (Parel)", 19.0040, 72.8430),
            ("Hinduja Hospital (Mahim)", 19.0330, 72.8390)
        ],
        "landmarks": [
            ("Dadar TT Circle (Dadar East)", 19.0178, 72.8478),
            ("Western Express Highway / Andheri Flyover", 19.1197, 72.8464),
            ("Bandra-Kurla Complex (BKC) Junction", 19.0662, 72.8687),
            ("Sion Circle", 19.0375, 72.8617),
            ("Kalanagar Junction (Bandra East)", 19.0596, 72.8459),
            ("Eastern Express Highway / Ghatkopar", 19.0860, 72.9090),
            ("Lower Parel / Senapati Bapat Marg", 18.9950, 72.8290),
            ("Haji Ali Junction", 18.9775, 72.8105),
            ("Thane Teen Hath Naka", 19.1868, 72.9620),
            ("Borivali National Park Junction", 19.2288, 72.8631)
        ]
    },
    "Delhi": {
        "state": "National Capital Region",
        "lat": 28.6139,
        "lon": 77.2090,
        "zoom": 11,
        "hotspots": [
            ("DEL01", "Dhaula Kuan Flyover", 28.5910, 77.1610),
            ("DEL02", "Ashram Chowk (Ring Road)", 28.5714, 77.2589),
            ("DEL03", "AIIMS / Safdarjung Ring Road", 28.5672, 77.2100),
            ("DEL04", "ITO Junction (Vikas Marg)", 28.6289, 77.2410),
            ("DEL05", "Connaught Place Outer Circle", 28.6328, 77.2197),
            ("DEL06", "Kashmere Gate ISBT", 28.6667, 77.2300),
            ("DEL07", "Lajpat Nagar Flyover", 28.5700, 77.2400),
            ("DEL08", "Akshardham / NH-24 Flyover", 28.6180, 77.2790),
            ("DEL09", "Gurgaon Cyber City / IFFCO Chowk", 28.4720, 77.0720),
            ("DEL10", "Noida Sector 18 / DND Flyway Entry", 28.5680, 77.3240),
            ("DEL11", "Karol Bagh Metro Junction", 28.6515, 77.1906),
            ("DEL12", "Peeragarhi Chowk (Outer Ring Road)", 28.6780, 77.0940),
            ("DEL13", "Mukarba Chowk (GT Karnal Road)", 28.7380, 77.1580),
            ("DEL14", "Sarai Kale Khan ISBT", 28.5900, 77.2550),
            ("DEL15", "Rajouri Garden Chowk (Ring Road)", 28.6490, 77.1230),
            ("DEL16", "Anand Vihar ISBT", 28.6469, 77.3160),
            ("DEL17", "Hauz Khas / IIT Flyover", 28.5430, 77.1980),
            ("DEL18", "Shadipur Depot / Patel Road", 28.6520, 77.1580),
            ("DEL19", "Chirag Delhi Flyover", 28.5390, 77.2280),
            ("DEL20", "Punjabi Bagh Chowk", 28.6680, 77.1290)
        ],
        "ambulance_corridors": [
            ("Ashram Chowk -> AIIMS Emergency Trauma", "Ashram Chowk (Ring Road)", "AIIMS Jai Prakash Apex Trauma Centre", 28.5714, 77.2589, 28.5645, 77.2020),
            ("Connaught Place -> RML Hospital", "Connaught Place Outer Circle", "Dr. Ram Manohar Lohia Hospital", 28.6328, 77.2197, 28.6248, 77.2016),
            ("Dhaula Kuan -> Army R&R Hospital", "Dhaula Kuan Flyover", "Army Hospital Research & Referral", 28.5910, 77.1610, 28.5830, 77.1490),
            ("Noida DND -> Safdarjung Hospital", "Noida Sector 18 / DND Flyway Entry", "Safdarjung Hospital", 28.5680, 77.3240, 28.5695, 77.2070)
        ],
        "hospitals": [
            ("AIIMS Jai Prakash Apex Trauma Centre (Ring Road)", 28.5645, 77.2020),
            ("Dr. Ram Manohar Lohia (RML) Hospital", 28.6248, 77.2016),
            ("Safdarjung Hospital", 28.5695, 77.2070),
            ("Army Hospital Research & Referral (Dhaula Kuan)", 28.5830, 77.1490),
            ("Sir Ganga Ram Hospital (Rajinder Nagar)", 28.6380, 77.1890),
            ("Max Super Speciality Hospital (Saket)", 28.5280, 77.2120),
            ("Lok Nayak Hospital (Delhi Gate)", 28.6360, 77.2410)
        ],
        "landmarks": [
            ("Connaught Place Outer Circle", 28.6328, 77.2197),
            ("Dhaula Kuan Flyover", 28.5910, 77.1610),
            ("Ashram Chowk (Ring Road)", 28.5714, 77.2589),
            ("AIIMS / Safdarjung Ring Road", 28.5672, 77.2100),
            ("ITO Junction (Vikas Marg)", 28.6289, 77.2410),
            ("Kashmere Gate ISBT", 28.6667, 77.2300),
            ("Lajpat Nagar Flyover", 28.5700, 77.2400),
            ("Akshardham / NH-24 Flyover", 28.6180, 77.2790),
            ("Gurgaon Cyber City / IFFCO Chowk", 28.4720, 77.0720),
            ("Noida Sector 18 / DND Flyway Entry", 28.5680, 77.3240)
        ]
    },
    "Hyderabad": {
        "state": "Telangana",
        "lat": 17.3850,
        "lon": 78.4867,
        "zoom": 11,
        "hotspots": [
            ("HYD01", "Gachibowli Junction / ORR", 17.4401, 78.3489),
            ("HYD02", "Hitec City Cyber Towers", 17.4504, 78.3808),
            ("HYD03", "Panjagutta Circle", 17.4265, 78.4528),
            ("HYD04", "Jubilee Hills Checkpost", 17.4325, 78.4070),
            ("HYD05", "Mehdipatnam Rythu Bazar", 17.3916, 78.4390),
            ("HYD06", "Begumpet Flyover", 17.4448, 78.4682),
            ("HYD07", "Secunderabad Station Circle", 17.4344, 78.5015),
            ("HYD08", "LB Nagar Ring Road Junction", 17.3508, 78.5524),
            ("HYD09", "Madhapur Police Station Cross", 17.4485, 78.3908),
            ("HYD10", "KPHB Colony / Kukatpally", 17.4932, 78.3994),
            ("HYD11", "Ameerpet Junction (Maitrivanam)", 17.4375, 78.4482),
            ("HYD12", "Kondapur / Botanical Garden Cross", 17.4640, 78.3610),
            ("HYD13", "Tolichowki Flyover Junction", 17.3990, 78.4120),
            ("HYD14", "Banjara Hills Road No. 12", 17.4140, 78.4350),
            ("HYD15", "Dilsukhnagar Main Road", 17.3688, 78.5247),
            ("HYD16", "Uppal Ring Road Junction", 17.4020, 78.5600),
            ("HYD17", "Miyapur Metro Junction", 17.4968, 78.3582),
            ("HYD18", "Paradise Circle (Secunderabad)", 17.4420, 78.4870),
            ("HYD19", "Nampally Station Road", 17.3920, 78.4710),
            ("HYD20", "Charminar / Madina Circle", 17.3616, 78.4747)
        ],
        "ambulance_corridors": [
            ("Gachibowli -> AIG Hospitals Gachibowli", "Gachibowli Junction / ORR", "AIG Hospitals Mindspace", 17.4401, 78.3489, 17.4428, 78.3685),
            ("Panjagutta -> NIMS Hospital", "Panjagutta Circle", "Nizam's Institute of Medical Sciences", 17.4265, 78.4528, 17.4225, 78.4550),
            ("Jubilee Hills -> Apollo Hospitals Jubilee", "Jubilee Hills Checkpost", "Apollo Hospital Jubilee Hills", 17.4325, 78.4070, 17.4210, 78.4110)
        ],
        "hospitals": [
            ("KIMS Hospital (Minister Road, Secunderabad)", 17.4379, 78.4907),
            ("Apollo Hospitals (Jubilee Hills)", 17.4210, 78.4110),
            ("NIMS Hospital (Panjagutta)", 17.4225, 78.4550),
            ("AIG Hospitals (Gachibowli / Mindspace)", 17.4428, 78.3685),
            ("Yashoda Hospital (Somajiguda)", 17.4270, 78.4590),
            ("Osmania General Hospital (Afzal Gunj)", 17.3780, 78.4740),
            ("Care Hospitals (Banjara Hills)", 17.4170, 78.4480)
        ],
        "landmarks": [
            ("Ameerpet Junction (Maitrivanam)", 17.4375, 78.4482),
            ("Gachibowli Junction / ORR", 17.4401, 78.3489),
            ("Hitec City Cyber Towers", 17.4504, 78.3808),
            ("Panjagutta Circle", 17.4265, 78.4528),
            ("Jubilee Hills Checkpost", 17.4325, 78.4070),
            ("Secunderabad Station Circle", 17.4344, 78.5015),
            ("Mehdipatnam Rythu Bazar", 17.3916, 78.4390),
            ("KPHB Colony / Kukatpally", 17.4932, 78.3994),
            ("Begumpet Flyover", 17.4448, 78.4682),
            ("LB Nagar Ring Road Junction", 17.3508, 78.5524)
        ]
    },
    "Chennai": {
        "state": "Tamil Nadu",
        "lat": 13.0827,
        "lon": 80.2707,
        "zoom": 11,
        "hotspots": [
            ("CHE01", "Kathipara Cloverleaf Flyover", 13.0067, 80.2050),
            ("CHE02", "Gemini Flyover (Anna Salai)", 13.0520, 80.2505),
            ("CHE03", "T. Nagar Panagal Park", 13.0418, 80.2337),
            ("CHE04", "Guindy Race Course / GST Road", 13.0060, 80.2120),
            ("CHE05", "Madhya Kailash / OMR Entry", 13.0075, 80.2520),
            ("CHE06", "Sholinganallur Junction (OMR)", 12.9010, 80.2279),
            ("CHE07", "Koyambedu CMBT Roundabout", 13.0694, 80.1948),
            ("CHE08", "Chennai Central Station Junction", 13.0827, 80.2757),
            ("CHE09", "Vadapalani Signal Junction", 13.0500, 80.2120),
            ("CHE10", "Thiruvanmiyur Signal", 12.9830, 80.2590),
            ("CHE11", "Velachery Bypass Road", 12.9780, 80.2180),
            ("CHE12", "Porur Junction / Mount Poonamallee", 13.0382, 80.1565),
            ("CHE13", "Adyar Signal / LB Road", 13.0064, 80.2570),
            ("CHE14", "Saidapet Bridge / Anna Salai", 13.0200, 80.2240),
            ("CHE15", "Tambaram Sanatorium GST Road", 12.9260, 80.1180),
            ("CHE16", "Perambur Railway Station Road", 13.1110, 80.2440),
            ("CHE17", "Chromepet MIT Gate", 12.9510, 80.1410),
            ("CHE18", "Egmore Station Roundabout", 13.0800, 80.2610),
            ("CHE19", "Royapettah Clock Tower", 13.0540, 80.2640),
            ("CHE20", "Ambattur Estate Road", 13.0990, 80.1620)
        ],
        "ambulance_corridors": [
            ("Kathipara -> MIOT International Hospital", "Kathipara Cloverleaf Flyover", "MIOT International Manapakkam", 13.0067, 80.2050, 13.0180, 80.1790),
            ("Gemini Flyover -> Apollo Hospitals Greams Rd", "Gemini Flyover (Anna Salai)", "Apollo Hospitals Greams Road", 13.0520, 80.2505, 13.0608, 80.2520),
            ("Madhya Kailash -> Fortis Malar Adyar", "Madhya Kailash / OMR Entry", "Fortis Malar Hospital Adyar", 13.0075, 80.2520, 13.0062, 80.2620)
        ],
        "hospitals": [
            ("Apollo Hospitals (Greams Road, Thousand Lights)", 13.0608, 80.2520),
            ("MIOT International Hospital (Manapakkam)", 13.0180, 80.1790),
            ("Fortis Malar Hospital (Adyar)", 13.0062, 80.2620),
            ("Rajiv Gandhi Govt General Hospital (Park Town)", 13.0805, 80.2785),
            ("Sri Ramachandra Medical Centre (Porur)", 13.0370, 80.1430),
            ("Kauvery Hospital (Alwarpet)", 13.0340, 80.2520)
        ],
        "landmarks": [
            ("T. Nagar (Panagal Park)", 13.0418, 80.2337),
            ("Kathipara Cloverleaf Flyover (Guindy)", 13.0067, 80.2050),
            ("Gemini Flyover (Anna Salai)", 13.0520, 80.2505),
            ("Chennai Central Station Junction", 13.0827, 80.2757),
            ("Koyambedu CMBT Roundabout", 13.0694, 80.1948),
            ("Madhya Kailash / OMR Entry", 13.0075, 80.2520),
            ("Sholinganallur Junction (OMR)", 12.9010, 80.2279),
            ("Vadapalani Signal Junction", 13.0500, 80.2120),
            ("Thiruvanmiyur Signal", 12.9830, 80.2590)
        ]
    },
    "Pune": {
        "state": "Maharashtra",
        "lat": 18.5204,
        "lon": 73.8567,
        "zoom": 11,
        "hotspots": [
            ("PUN01", "Chandani Chowk Bypass", 18.5074, 73.7915),
            ("PUN02", "Hinjawadi Shivaji Chowk", 18.5913, 73.7389),
            ("PUN03", "Shivajinagar Sancheti Hospital Chowk", 18.5314, 73.8504),
            ("PUN04", "Swargate Chowk", 18.5018, 73.8580),
            ("PUN05", "University / Pune Vidyapeeth Circle", 18.5529, 73.8260),
            ("PUN06", "Hadapsar Gadital Junction", 18.5020, 73.9280),
            ("PUN07", "Katraj Dehu Road Bypass Chowk", 18.4530, 73.8570),
            ("PUN08", "Viman Nagar / Phoenix Mall Junction", 18.5620, 73.9160),
            ("PUN09", "Deccan Gymkhana FC Road", 18.5160, 73.8420),
            ("PUN10", "Bund Garden Bridge", 18.5360, 73.8820),
            ("PUN11", "Wakad Bridge / Mumbai-Pune Highway", 18.5980, 73.7630),
            ("PUN12", "Baner Road / Balewadi Phata", 18.5590, 73.7920),
            ("PUN13", "Kothrud Paud Road / Vanaz", 18.5070, 73.8050),
            ("PUN14", "Magarpatta City Main Gate", 18.5130, 73.9320),
            ("PUN15", "Koregaon Park North Main Road", 18.5360, 73.8940),
            ("PUN16", "Aundh Rajiv Gandhi Bridge", 18.5600, 73.8080),
            ("PUN17", "Pimpri Chowk / Old Mumbai-Pune Road", 18.6270, 73.8000),
            ("PUN18", "Chinchwad Station Road", 18.6360, 73.7920),
            ("PUN19", "Vishrantwadi Circle", 18.5720, 73.8780),
            ("PUN20", "Kharadi Bypass / EON IT Park", 18.5520, 73.9450)
        ],
        "ambulance_corridors": [
            ("Shivajinagar -> Sancheti Hospital", "Shivajinagar Sancheti Hospital Chowk", "Sancheti Hospital Shivajinagar", 18.5314, 73.8504, 18.5280, 73.8510),
            ("Hinjawadi -> Ruby Hall Clinic Hinjawadi", "Hinjawadi Shivaji Chowk", "Ruby Hall Clinic Wanowrie/Hinjawadi", 18.5913, 73.7389, 18.5860, 73.7420),
            ("Swargate -> Poona Hospital Deccan", "Swargate Chowk", "Poona Hospital & Research Centre", 18.5018, 73.8580, 18.5120, 73.8450)
        ],
        "hospitals": [
            ("Sancheti Hospital (Shivajinagar)", 18.5280, 73.8510),
            ("Ruby Hall Clinic (Wanowrie / Sassoon Rd)", 18.5320, 73.8760),
            ("Poona Hospital & Research Centre (Deccan)", 18.5120, 73.8450),
            ("Deenanath Mangeshkar Hospital (Erandwane)", 18.5020, 73.8340),
            ("Jehangir Hospital (Near Pune Station)", 18.5300, 73.8770)
        ],
        "landmarks": [
            ("Chandani Chowk Bypass", 18.5074, 73.7915),
            ("Hinjawadi Shivaji Chowk", 18.5913, 73.7389),
            ("Shivajinagar Sancheti Hospital Chowk", 18.5314, 73.8504),
            ("Swargate Chowk", 18.5018, 73.8580),
            ("University / Pune Vidyapeeth Circle", 18.5529, 73.8260),
            ("Hadapsar Gadital Junction", 18.5020, 73.9280),
            ("Deccan Gymkhana FC Road", 18.5160, 73.8420),
            ("Katraj Dehu Road Bypass Chowk", 18.4530, 73.8570),
            ("Viman Nagar / Phoenix Mall Junction", 18.5620, 73.9160)
        ]
    },
    "Kolkata": {
        "state": "West Bengal",
        "lat": 22.5726,
        "lon": 88.3639,
        "zoom": 11,
        "hotspots": [
            ("KOL01", "Park Street / Chowringhee Crossing", 22.5535, 88.3512),
            ("KOL02", "Howrah Bridge Approach (MG Road)", 22.5858, 88.3478),
            ("KOL03", "Maa Flyover / Science City Junction", 22.5404, 88.3962),
            ("KOL04", "Ultadanga Crossing / EM Bypass", 22.5902, 88.3968),
            ("KOL05", "Gariahat Crossing", 22.5195, 88.3653),
            ("KOL06", "Esplanade / Dharmatala Junction", 22.5658, 88.3518),
            ("KOL07", "Shyambazar Five-Point Crossing", 22.6022, 88.3714),
            ("KOL08", "Ruby General Hospital Crossing (EM Bypass)", 22.5133, 88.4022),
            ("KOL09", "Chingrighata Flyover Junction", 22.5630, 88.4040),
            ("KOL10", "Taratala Crossing (Diamond Harbour Rd)", 22.5120, 88.3180),
            ("KOL11", "Salt Lake Karunamoyee Circle", 22.5860, 88.4210),
            ("KOL12", "Vidyasagar Setu (2nd Hooghly Bridge) Toll", 22.5560, 88.3240),
            ("KOL13", "Sealdah Station / Flyover", 22.5670, 88.3710),
            ("KOL14", "Newtown Major Arterial Road / Eco Park", 22.5970, 88.4720),
            ("KOL15", "Exide / Rabindra Sadan Crossing", 22.5440, 88.3470),
            ("KOL16", "Beleghata Crossing (EM Bypass)", 22.5670, 88.3990),
            ("KOL17", "Garia / Kavi Nazrul Metro Junction", 22.4640, 88.3890),
            ("KOL18", "Jadavpur 8B Bus Stand", 22.4980, 88.3710),
            ("KOL19", "Dunlop Crossing (BT Road)", 22.6540, 88.3750),
            ("KOL20", "Sector V Tech Hub / College More", 22.5730, 88.4330)
        ],
        "ambulance_corridors": [
            ("Park Street -> SSKM Hospital", "Park Street / Chowringhee Crossing", "SSKM Hospital (IPGMER)", 22.5535, 88.3512, 22.5398, 88.3435),
            ("Science City -> Apollo Multispecialty Hospital", "Maa Flyover / Science City Junction", "Apollo Multispecialty Hospitals Canal Circular", 22.5404, 88.3962, 22.5702, 88.4014),
            ("Ruby Crossing -> Fortis Hospital Anandapur", "Ruby General Hospital Crossing (EM Bypass)", "Fortis Hospital Anandapur", 22.5133, 88.4022, 22.5192, 88.4050)
        ],
        "hospitals": [
            ("SSKM Hospital (IPGMER, Bhowanipore)", 22.5398, 88.3435),
            ("Apollo Multispecialty Hospitals (Canal Circular Road)", 22.5702, 88.4014),
            ("Fortis Hospital Anandapur (EM Bypass)", 22.5192, 88.4050),
            ("Calcutta Medical College and Hospital (College Street)", 22.5740, 88.3610),
            ("AMRI Hospital (Dhakuria)", 22.5110, 88.3660),
            ("Ruby General Hospital (EM Bypass)", 22.5133, 88.4022)
        ],
        "landmarks": [
            ("Park Street / Chowringhee Crossing", 22.5535, 88.3512),
            ("Howrah Bridge Approach (MG Road)", 22.5858, 88.3478),
            ("Maa Flyover / Science City Junction", 22.5404, 88.3962),
            ("Ultadanga Crossing / EM Bypass", 22.5902, 88.3968),
            ("Gariahat Crossing", 22.5195, 88.3653),
            ("Esplanade / Dharmatala Junction", 22.5658, 88.3518),
            ("Shyambazar Five-Point Crossing", 22.6022, 88.3714),
            ("Ruby General Hospital Crossing", 22.5133, 88.4022)
        ]
    }
}


def get_city_hospitals(city):
    """Returns list of verified hospitals [(name, lat, lon)] for the city."""
    return CITIES.get(city, {}).get("hospitals", [])


def get_city_landmarks(city):
    """Returns list of verified landmarks/junctions [(name, lat, lon)] for the city."""
    return CITIES.get(city, {}).get("landmarks", [])


def get_db_connection():
    conn = sqlite3.connect(DB_FILE)
    conn.row_factory = sqlite3.Row
    return conn


def init_database():
    """Initializes tables and seeds data cleanly."""
    conn = get_db_connection()
    c = conn.cursor()

    # 1. Observations Table
    c.execute("""
    CREATE TABLE IF NOT EXISTS city_observations (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        city TEXT NOT NULL,
        hotspot_id TEXT,
        hotspot_name TEXT NOT NULL,
        latitude REAL NOT NULL,
        longitude REAL NOT NULL,
        hour INTEGER,
        day_of_week TEXT,
        traffic_volume REAL,
        average_speed_kmh REAL,
        congestion_score REAL,
        congestion_level TEXT,
        average_waiting_time_min REAL,
        average_queue_length REAL,
        source TEXT DEFAULT 'Historical'
    )
    """)

    # 2. Incident Reports Table
    c.execute("""
    CREATE TABLE IF NOT EXISTS incident_reports (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        city TEXT NOT NULL,
        location TEXT NOT NULL,
        incident_type TEXT NOT NULL,
        severity TEXT NOT NULL,
        description TEXT NOT NULL,
        reporter TEXT NOT NULL,
        timestamp TEXT NOT NULL,
        expiry_hours REAL DEFAULT 4.0,
        status TEXT DEFAULT 'Active'
    )
    """)

    # 3. User Feedback Table
    c.execute("""
    CREATE TABLE IF NOT EXISTS user_feedback (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        city TEXT NOT NULL,
        name TEXT NOT NULL,
        category TEXT NOT NULL,
        rating INTEGER NOT NULL,
        comments TEXT NOT NULL,
        timestamp TEXT NOT NULL
    )
    """)

    # 4. Emergency Broadcast Trips Table (Shared real-time cross-session state)
    c.execute("""
    CREATE TABLE IF NOT EXISTS emergency_broadcast_trips (
        trip_id TEXT PRIMARY KEY,
        ambulance_id TEXT NOT NULL,
        city TEXT NOT NULL,
        origin_name TEXT NOT NULL,
        dest_name TEXT NOT NULL,
        priority TEXT NOT NULL,
        current_lat REAL NOT NULL,
        current_lon REAL NOT NULL,
        heading REAL DEFAULT 0.0,
        speed_kmh REAL DEFAULT 0.0,
        status TEXT NOT NULL,
        route_coords_json TEXT,
        started_at TEXT NOT NULL,
        last_updated_at TEXT NOT NULL
    )
    """)

    conn.commit()

    # Seed Bengaluru Excel if city_observations for Bengaluru is empty
    c.execute("SELECT COUNT(*) FROM city_observations WHERE city = 'Bengaluru'")
    beng_count = c.fetchone()[0]
    if beng_count == 0 and os.path.exists(BENGALURU_EXCEL):
        try:
            beng_df = pd.read_excel(BENGALURU_EXCEL)
            for _, r in beng_df.iterrows():
                c.execute("""
                INSERT INTO city_observations (
                    city, hotspot_id, hotspot_name, latitude, longitude,
                    hour, day_of_week, traffic_volume, average_speed_kmh,
                    congestion_score, congestion_level, average_waiting_time_min,
                    average_queue_length, source
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                """, (
                    "Bengaluru",
                    str(r.get("hotspot_id", "")),
                    str(r.get("hotspot_name", "")),
                    float(r.get("latitude", 12.9716)),
                    float(r.get("longitude", 77.5946)),
                    int(r.get("hour", 8)),
                    str(r.get("day_of_week", "Monday")),
                    float(r.get("traffic_volume", 500)),
                    float(r.get("average_speed_kmh", 30)),
                    float(r.get("congestion_score", 30)),
                    str(r.get("congestion_level", "Moderate")),
                    float(r.get("average_waiting_time_min", 3.0)),
                    float(r.get("average_queue_length", 8.0)),
                    "Bengaluru Historical Dataset"
                ))
            conn.commit()
        except Exception as e:
            print("Error loading Bengaluru Excel to SQLite:", e)


    # Permanent Seeder: Ensure every city has its full 2,100 records
    DAYS = [
        ("Monday", "2026-08-17"),
        ("Tuesday", "2026-08-18"),
        ("Wednesday", "2026-08-19"),
        ("Thursday", "2026-08-20"),
        ("Friday", "2026-08-21"),
        ("Saturday", "2026-08-22"),
        ("Sunday", "2026-08-23")
    ]
    HOURS = list(range(8, 23))

    CITY_PROFILES = {
        "Mumbai": {"base_vol": 680, "base_score": 34.5, "free_speed": 48.0},
        "Delhi": {"base_vol": 710, "base_score": 32.0, "free_speed": 55.0},
        "Hyderabad": {"base_vol": 620, "base_score": 29.8, "free_speed": 50.0},
        "Chennai": {"base_vol": 590, "base_score": 28.5, "free_speed": 49.0},
        "Pune": {"base_vol": 560, "base_score": 30.5, "free_speed": 48.0},
        "Kolkata": {"base_vol": 610, "base_score": 33.2, "free_speed": 44.0}
    }

    import random
    rng = random.Random(42)

    for city_name, prof in CITY_PROFILES.items():
        c.execute("SELECT COUNT(*) FROM city_observations WHERE city = ?", (city_name,))
        cnt = c.fetchone()[0]
        if cnt < 2100:
            c.execute("DELETE FROM city_observations WHERE city = ?", (city_name,))
            hotspots = CITIES[city_name]["hotspots"]
            base_vol = prof["base_vol"]
            base_score = prof["base_score"]
            free_speed = prof["free_speed"]

            city_rows = []
            for h_idx, (h_id, h_name, h_lat, h_lon) in enumerate(hotspots):
                w = 1.0 + ((h_idx % 5) * 0.07)  # Corridor variation
                for day, date_str in DAYS:
                    is_weekend = day in ["Saturday", "Sunday"]
                    for h in HOURS:
                        if not is_weekend:
                            if h in [9, 10]:
                                h_fac = 1.38
                            elif h in [8, 11]:
                                h_fac = 1.18
                            elif h in [12, 13, 14, 15]:
                                h_fac = 0.88
                            elif h in [17, 18, 19]:
                                h_fac = 1.45
                            elif h in [16, 20]:
                                h_fac = 1.22
                            else:
                                h_fac = 0.74
                        else:
                            if h in [8, 9, 10]:
                                h_fac = 0.80
                            elif h in [11, 12, 13]:
                                h_fac = 1.05
                            elif h in [14, 15, 16]:
                                h_fac = 1.00
                            elif h in [17, 18, 19, 20]:
                                h_fac = 1.35
                            else:
                                h_fac = 0.88

                        vol = int(base_vol * w * h_fac * rng.uniform(0.92, 1.08))
                        vol = max(240, min(1480, vol))

                        score = round(base_score * w * h_fac * rng.uniform(0.90, 1.10) * 0.95, 1)
                        score = max(5.0, min(75.0, score))

                        level = "Low" if score < 25.0 else ("Moderate" if score < 42.0 else "High")
                        speed_ratio = 1.0 - (score / 100.0) * 0.65
                        speed = round(max(15.0, free_speed * speed_ratio * rng.uniform(0.94, 1.06)), 1)
                        delay = round(max(0.8, (score / 11.5) * rng.uniform(0.92, 1.08)), 1)
                        queue = round(max(2.0, (vol / 65.0) * (score / 30.0) * rng.uniform(0.88, 1.12)), 1)

                        city_rows.append((
                            city_name, h_id, h_name, h_lat, h_lon,
                            h, day, float(vol), float(speed),
                            float(score), level, float(delay), float(queue),
                            f"{city_name} Historical Observation Baseline"
                        ))

            c.executemany("""
            INSERT INTO city_observations (
                city, hotspot_id, hotspot_name, latitude, longitude,
                hour, day_of_week, traffic_volume, average_speed_kmh,
                congestion_score, congestion_level, average_waiting_time_min,
                average_queue_length, source
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """, city_rows)
            conn.commit()

    conn.commit()

    # Seed sample incidents per city if none exist
    c.execute("SELECT COUNT(*) FROM incident_reports")
    if c.fetchone()[0] == 0:
        now_dt = datetime.datetime.now()
        t1 = (now_dt - datetime.timedelta(minutes=45)).strftime("%Y-%m-%d %H:%M")
        t2 = (now_dt - datetime.timedelta(hours=3, minutes=10)).strftime("%Y-%m-%d %H:%M") # Stale (> 3 hrs)
        t3 = (now_dt - datetime.timedelta(hours=28)).strftime("%Y-%m-%d %H:%M") # Expired

        sample_incidents = [
            # Bengaluru
            ("Bengaluru", "Silk Board Junction", "Vehicle Breakdown", "Moderate", "Stalled commercial lorry on flyover ramp causing single-lane backup.", "Traffic Volunteer", t1, 4.0, "Active"),
            ("Bengaluru", "Hebbal Flyover", "Road Construction", "Low", "Asphalt pothole repair on extreme left lane towards airport.", "Commuter", t2, 4.0, "Active"),
            ("Bengaluru", "Banashankari 3rd Stage Junction", "Pothole Hazard", "Moderate", "Due to water pipe repair old road has deep potholes causing vehicle slowdown.", "Apoorva", t1, 4.0, "Active"),
            # Mumbai
            ("Mumbai", "Western Express Highway / Andheri Flyover", "Accident / Collision", "Severe", "Two-car collision on southbound carriageway; emergency crane on site.", "Mumbai Traffic Police Feed", t1, 4.0, "Active"),
            ("Mumbai", "Dadar TT Circle", "Waterlogging", "Moderate", "Water accumulation near signal causing slow-moving traffic.", "Commuter", t2, 4.0, "Active"),
            # Delhi
            ("Delhi", "Ashram Chowk (Ring Road)", "Road Construction", "Moderate", "Underpass maintenance work blocking middle lane.", "Delhi Commuter", t1, 4.0, "Active"),
            ("Delhi", "Dhaula Kuan Flyover", "Heavy Congestion", "Severe", "Peak hour vehicle bottleneck extending to Subroto Park.", "Traffic Warden", t1, 4.0, "Active"),
            # Hyderabad
            ("Hyderabad", "Gachibowli Junction / ORR", "Signal Malfunction", "Moderate", "Signal timer blinking amber; traffic marshals managing flow manually.", "IT Commuter", t1, 4.0, "Active"),
            # Chennai
            ("Chennai", "Kathipara Cloverleaf Flyover", "Road Maintenance", "Low", "Bridge joint re-alignment work near Guindy exit.", "Citizen Reporter", t2, 6.0, "Active"),
            # Pune
            ("Pune", "Chandani Chowk Bypass", "Heavy Congestion", "Moderate", "Heavy truck movement towards Kothrud causing slow progress.", "Pune Commuter", t1, 4.0, "Active"),
            # Kolkata
            ("Kolkata", "Park Street / Chowringhee Crossing", "Heavy Congestion", "Moderate", "Slow movement towards Victoria Memorial due to evening rush.", "Kolkata Commuter", t1, 4.0, "Active")
        ]

        c.executemany("""
        INSERT INTO incident_reports (
            city, location, incident_type, severity, description,
            reporter, timestamp, expiry_hours, status
        ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
        """, sample_incidents)
        conn.commit()

    conn.close()


# -----------------------------------------------------------------------------
# Incident Query & Persistence Helpers
# -----------------------------------------------------------------------------
def get_city_incidents(city, include_archived=False):
    """
    Returns incident reports for a specific city with calculated age,
    stale warnings (> 2 hours), and expiry status.
    """
    conn = get_db_connection()
    c = conn.cursor()
    c.execute("SELECT * FROM incident_reports WHERE city = ? ORDER BY id DESC", (city,))
    rows = c.fetchall()
    conn.close()

    now = datetime.datetime.now()
    results = []

    for r in rows:
        row_dict = dict(r)
        # Calculate age in hours
        try:
            r_time = datetime.datetime.strptime(row_dict["timestamp"], "%Y-%m-%d %H:%M")
            age_hours = (now - r_time).total_seconds() / 3600.0
        except Exception:
            age_hours = 0.5

        row_dict["age_hours"] = round(age_hours, 1)
        expiry_limit = float(row_dict.get("expiry_hours", 4.0))

        status = row_dict.get("status", "Unverified (Community)")
        if status == "Resolved":
            row_dict["is_expired"] = True
            row_dict["is_stale"] = True
            row_dict["display_status"] = "Resolved / Cleared"
        elif age_hours > expiry_limit or status == "Expired":
            row_dict["is_expired"] = True
            row_dict["is_stale"] = True
            row_dict["display_status"] = "Expired / Archived"
        elif age_hours > 2.0:
            row_dict["is_expired"] = False
            row_dict["is_stale"] = True
            row_dict["display_status"] = f"Stale Observation ({round(age_hours, 1)}h ago)"
        else:
            row_dict["is_expired"] = False
            row_dict["is_stale"] = False
            row_dict["display_status"] = "Fresh Observation (< 2h)"

        # Clean sanitized description for HTML safe display
        desc = str(row_dict.get("description", "")).replace("\n", " ").strip()
        row_dict["clean_description"] = html.escape(desc)
        row_dict["clean_reporter"] = html.escape(str(row_dict.get("reporter", "Anonymous")).replace("\n", " ").strip())
        row_dict["clean_location"] = html.escape(str(row_dict.get("location", "")).replace("\n", " ").strip())

        if include_archived or not row_dict["is_expired"]:
            results.append(row_dict)

    return pd.DataFrame(results) if results else pd.DataFrame(columns=[
        "id", "city", "location", "incident_type", "severity", "clean_description",
        "clean_reporter", "timestamp", "age_hours", "is_stale", "is_expired", "display_status", "status"
    ])


def add_incident_report(city, location, inc_type, severity, description, reporter, expiry_hours=4.0, is_anonymous=False):
    """
    Saves a sanitized incident report into SQLite with duplicate check.
    Returns (success, message).
    """
    clean_desc = str(description).replace("\n", " ").strip()
    clean_rep = "Anonymous Commuter" if is_anonymous else (str(reporter).replace("\n", " ").strip() or "Citizen Reporter")

    conn = get_db_connection()
    c = conn.cursor()

    # Duplicate check: check if an identical location and type was logged within the last 20 minutes
    now_dt = datetime.datetime.now()
    threshold_str = (now_dt - datetime.timedelta(minutes=20)).strftime("%Y-%m-%d %H:%M")
    c.execute("""
        SELECT COUNT(*) FROM incident_reports 
        WHERE city = ? AND location = ? AND incident_type = ? AND timestamp >= ? AND status != 'Resolved'
    """, (city, location, inc_type, threshold_str))
    
    if c.fetchone()[0] > 0:
        conn.close()
        return False, "Duplicate Report Prevented: An identical hazard report was already submitted for this junction within the last 20 minutes."

    ts = now_dt.strftime("%Y-%m-%d %H:%M")
    c.execute("""
    INSERT INTO incident_reports (
        city, location, incident_type, severity, description,
        reporter, timestamp, expiry_hours, status
    ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, 'Unverified (Community)')
    """, (city, location, inc_type, severity, clean_desc, clean_rep, ts, float(expiry_hours)))
    conn.commit()
    conn.close()
    return True, "Incident report successfully saved to SQLite database!"


def resolve_incident(incident_id):
    """Marks an active incident as Resolved / Cleared."""
    conn = get_db_connection()
    c = conn.cursor()
    c.execute("UPDATE incident_reports SET status = 'Resolved' WHERE id = ?", (int(incident_id),))
    conn.commit()
    conn.close()
    return True


def get_city_observations(city):
    """Returns historical/baseline observations strictly isolated for the requested city."""
    conn = get_db_connection()
    df = pd.read_sql_query(
        "SELECT * FROM city_observations WHERE city = ?",
        conn,
        params=(city,)
    )
    conn.close()
    return df


def add_user_feedback(city, name, category, rating, comments):
    """Saves commuter feedback to SQLite."""
    clean_comments = str(comments).replace("\n", " ").strip()
    clean_name = str(name).replace("\n", " ").strip() or "Student Reviewer"
    ts = datetime.datetime.now().strftime("%Y-%m-%d %H:%M")
    conn = get_db_connection()
    c = conn.cursor()
    c.execute("""
    INSERT INTO user_feedback (city, name, category, rating, comments, timestamp)
    VALUES (?, ?, ?, ?, ?, ?)
    """, (city, clean_name, category, int(rating), clean_comments, ts))
    conn.commit()
    conn.close()
    return True


def get_city_feedback(city):
    """Returns feedback entries for the city or all cities."""
    conn = get_db_connection()
    df = pd.read_sql_query(
        "SELECT * FROM user_feedback WHERE city = ? OR city = 'All' ORDER BY id DESC LIMIT 10",
        conn,
        params=(city,)
    )
    conn.close()
    if df.empty:
        # Default starter feedback
        return pd.DataFrame([
            {"name": "Rohan Deshmukh", "city": city, "category": "Routing & Map", "rating": 5, "comments": f"Clean OpenStreetMap display and accurate road geometry for {city} corridors.", "timestamp": "2026-11-15 11:30"},
            {"name": "Sneha P.", "city": city, "category": "Simulation", "rating": 5, "comments": "Ambulance priority simulation audio and vibration is impressive on mobile devices.", "timestamp": "2026-11-15 12:45"}
        ])
    return df


def publish_emergency_trip(trip_id, ambulance_id, city, origin_name, dest_name, priority, current_lat, current_lon, heading, speed_kmh, route_coords_json):
    """Publishes a new active emergency broadcast trip to SQLite."""
    now_str = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    conn = get_db_connection()
    c = conn.cursor()
    c.execute("""
    INSERT OR REPLACE INTO emergency_broadcast_trips (
        trip_id, ambulance_id, city, origin_name, dest_name, priority,
        current_lat, current_lon, heading, speed_kmh, status,
        route_coords_json, started_at, last_updated_at
    ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, 'ACTIVE', ?, ?, ?)
    """, (
        str(trip_id), str(ambulance_id), str(city), str(origin_name), str(dest_name),
        str(priority), float(current_lat), float(current_lon), float(heading),
        float(speed_kmh), str(route_coords_json), now_str, now_str
    ))
    conn.commit()
    conn.close()
    return True


def update_emergency_trip_location(trip_id, current_lat, current_lon, heading=0.0, speed_kmh=0.0):
    """Updates the real-time position of an active emergency trip."""
    now_str = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    conn = get_db_connection()
    c = conn.cursor()
    c.execute("""
    UPDATE emergency_broadcast_trips
    SET current_lat = ?, current_lon = ?, heading = ?, speed_kmh = ?, last_updated_at = ?
    WHERE trip_id = ? AND status = 'ACTIVE'
    """, (float(current_lat), float(current_lon), float(heading), float(speed_kmh), now_str, str(trip_id)))
    conn.commit()
    conn.close()
    return True


def stop_emergency_trip(trip_id):
    """Marks an active emergency trip as COMPLETED."""
    now_str = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    conn = get_db_connection()
    c = conn.cursor()
    c.execute("""
    UPDATE emergency_broadcast_trips
    SET status = 'COMPLETED', last_updated_at = ?
    WHERE trip_id = ?
    """, (now_str, str(trip_id)))
    conn.commit()
    conn.close()
    return True


def get_active_emergency_trips(city=None):
    """Returns list of currently active emergency broadcast trips from SQLite."""
    conn = get_db_connection()
    c = conn.cursor()
    query = "SELECT * FROM emergency_broadcast_trips WHERE status = 'ACTIVE'"
    params = ()
    if city and city != "All":
        query += " AND city = ?"
        params = (city,)
    query += " ORDER BY last_updated_at DESC"
    c.execute(query, params)
    rows = [dict(r) for r in c.fetchall()]
    conn.close()
    return rows
