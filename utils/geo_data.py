"""
Official Geographic Reference Data for LANDGUARD AI.
Covers all 28 States and 8 Union Territories of India with representative districts and coordinates.
"""

GEO_REFERENCE = {
    # --- STATES (28) ---
    "AP": {
        "name": "Andhra Pradesh",
        "type": "STATE",
        "center": [15.9129, 79.7400],
        "districts": [
            {"code": "AP-VIS", "name": "Visakhapatnam", "center": [17.6868, 83.2185]},
            {"code": "AP-VIZ", "name": "Vizianagaram", "center": [18.1066, 83.3956]},
            {"code": "AP-GNT", "name": "Guntur", "center": [16.3067, 80.4365]},
            {"code": "AP-KRN", "name": "Kurnool", "center": [15.8281, 78.0373]},
            {"code": "AP-CTR", "name": "Chittoor", "center": [13.2172, 79.1003]},
            {"code": "AP-KRS", "name": "Krishna", "center": [16.5700, 80.8200]}
        ]
    },
    "AR": {
        "name": "Arunachal Pradesh",
        "type": "STATE",
        "center": [28.2180, 94.7278],
        "districts": [
            {"code": "AR-ITN", "name": "Papum Pare", "center": [27.1000, 93.6200]},
            {"code": "AR-TWG", "name": "Tawang", "center": [27.5861, 91.8594]},
            {"code": "AR-CGL", "name": "Changlang", "center": [27.1300, 95.7300]}
        ]
    },
    "AS": {
        "name": "Assam",
        "type": "STATE",
        "center": [26.2006, 92.9376],
        "districts": [
            {"code": "AS-KMR", "name": "Kamrup Metropolitan", "center": [26.1445, 91.7362]},
            {"code": "AS-DBR", "name": "Dibrugarh", "center": [27.4728, 94.9120]},
            {"code": "AS-SLR", "name": "Silchar (Cachar)", "center": [24.8333, 92.7789]},
            {"code": "AS-JRH", "name": "Jorhat", "center": [26.7509, 94.2037]}
        ]
    },
    "BR": {
        "name": "Bihar",
        "type": "STATE",
        "center": [25.0961, 85.3131],
        "districts": [
            {"code": "BR-PAT", "name": "Patna", "center": [25.5941, 85.1376]},
            {"code": "BR-GAY", "name": "Gaya", "center": [24.7914, 85.0002]},
            {"code": "BR-MZP", "name": "Muzaffarpur", "center": [26.1209, 85.3647]},
            {"code": "BR-BGP", "name": "Bhagalpur", "center": [25.2425, 86.9842]}
        ]
    },
    "CG": {
        "name": "Chhattisgarh",
        "type": "STATE",
        "center": [21.2787, 81.8661],
        "districts": [
            {"code": "CG-RPR", "name": "Raipur", "center": [21.2514, 81.6296]},
            {"code": "CG-BLS", "name": "Bilaspur", "center": [22.0797, 82.1391]},
            {"code": "CG-DRG", "name": "Durg", "center": [21.1904, 81.2849]},
            {"code": "CG-KRB", "name": "Korba", "center": [22.3595, 82.7501]}
        ]
    },
    "GA": {
        "name": "Goa",
        "type": "STATE",
        "center": [15.2993, 74.1240],
        "districts": [
            {"code": "GA-NGO", "name": "North Goa", "center": [15.5494, 73.8682]},
            {"code": "GA-SGO", "name": "South Goa", "center": [15.2736, 73.9581]}
        ]
    },
    "GJ": {
        "name": "Gujarat",
        "type": "STATE",
        "center": [22.2587, 71.1924],
        "districts": [
            {"code": "GJ-AMD", "name": "Ahmedabad", "center": [23.0225, 72.5714]},
            {"code": "GJ-SRT", "name": "Surat", "center": [21.1702, 72.8311]},
            {"code": "GJ-VDR", "name": "Vadodara", "center": [22.3072, 73.1812]},
            {"code": "GJ-RJK", "name": "Rajkot", "center": [22.3039, 70.8022]}
        ]
    },
    "HR": {
        "name": "Haryana",
        "type": "STATE",
        "center": [29.0588, 76.0856],
        "districts": [
            {"code": "HR-GGM", "name": "Gurugram", "center": [28.4595, 77.0266]},
            {"code": "HR-FDB", "name": "Faridabad", "center": [28.4089, 77.3178]},
            {"code": "HR-PKL", "name": "Panchkula", "center": [30.6942, 76.8606]},
            {"code": "HR-KRN", "name": "Karnal", "center": [29.6857, 76.9905]}
        ]
    },
    "HP": {
        "name": "Himachal Pradesh",
        "type": "STATE",
        "center": [31.1048, 77.1734],
        "districts": [
            {"code": "HP-SML", "name": "Shimla", "center": [31.1048, 77.1734]},
            {"code": "HP-KNG", "name": "Kangra", "center": [32.1024, 76.2691]},
            {"code": "HP-MND", "name": "Mandi", "center": [31.7087, 76.9320]}
        ]
    },
    "JH": {
        "name": "Jharkhand",
        "type": "STATE",
        "center": [23.6102, 85.2799],
        "districts": [
            {"code": "JH-RNC", "name": "Ranchi", "center": [23.3441, 85.3096]},
            {"code": "JH-JSH", "name": "Jamshedpur (East Singhbhum)", "center": [22.8046, 86.2029]},
            {"code": "JH-DHN", "name": "Dhanbad", "center": [23.7957, 86.4304]},
            {"code": "JH-BKR", "name": "Bokaro", "center": [23.6693, 86.1511]}
        ]
    },
    "KA": {
        "name": "Karnataka",
        "type": "STATE",
        "center": [15.3173, 75.7139],
        "districts": [
            {"code": "KA-BLR", "name": "Bengaluru Urban", "center": [12.9716, 77.5946]},
            {"code": "KA-MYS", "name": "Mysuru", "center": [12.2958, 76.6394]},
            {"code": "KA-DKN", "name": "Dakshina Kannada (Mangaluru)", "center": [12.9141, 74.8560]},
            {"code": "KA-BEL", "name": "Belagavi", "center": [15.8497, 74.4977]}
        ]
    },
    "KL": {
        "name": "Kerala",
        "type": "STATE",
        "center": [10.8505, 76.2711],
        "districts": [
            {"code": "KL-TVM", "name": "Thiruvananthapuram", "center": [8.5241, 76.9366]},
            {"code": "KL-EKM", "name": "Ernakulam (Kochi)", "center": [9.9816, 76.2999]},
            {"code": "KL-CLT", "name": "Kozhikode", "center": [11.2588, 75.7804]},
            {"code": "KL-TCR", "name": "Thrissur", "center": [10.5276, 76.2144]}
        ]
    },
    "MP": {
        "name": "Madhya Pradesh",
        "type": "STATE",
        "center": [22.9734, 78.6569],
        "districts": [
            {"code": "MP-BPL", "name": "Bhopal", "center": [23.2599, 77.4126]},
            {"code": "MP-IND", "name": "Indore", "center": [22.7196, 75.8577]},
            {"code": "MP-JBP", "name": "Jabalpur", "center": [23.1815, 79.9864]},
            {"code": "MP-GWL", "name": "Gwalior", "center": [26.2183, 78.1828]}
        ]
    },
    "MH": {
        "name": "Maharashtra",
        "type": "STATE",
        "center": [19.7515, 75.7139],
        "districts": [
            {"code": "MH-MUM", "name": "Mumbai Suburban", "center": [19.0760, 72.8777]},
            {"code": "MH-PUN", "name": "Pune", "center": [18.5204, 73.8567]},
            {"code": "MH-NGP", "name": "Nagpur", "center": [21.1458, 79.0882]},
            {"code": "MH-THN", "name": "Thane", "center": [19.2183, 72.9781]},
            {"code": "MH-NSK", "name": "Nashik", "center": [19.9975, 73.7898]}
        ]
    },
    "MN": {
        "name": "Manipur",
        "type": "STATE",
        "center": [24.6637, 93.9063],
        "districts": [
            {"code": "MN-IMP", "name": "Imphal East", "center": [24.8170, 93.9500]},
            {"code": "MN-CBR", "name": "Churachandpur", "center": [24.3333, 93.6833]}
        ]
    },
    "ML": {
        "name": "Meghalaya",
        "type": "STATE",
        "center": [25.4670, 91.3662],
        "districts": [
            {"code": "ML-SHL", "name": "East Khasi Hills (Shillong)", "center": [25.5788, 91.8933]},
            {"code": "ML-TUA", "name": "West Garo Hills (Tura)", "center": [25.5147, 90.2032]}
        ]
    },
    "MZ": {
        "name": "Mizoram",
        "type": "STATE",
        "center": [23.1645, 92.9376],
        "districts": [
            {"code": "MZ-AIZ", "name": "Aizawl", "center": [23.7271, 92.7176]},
            {"code": "MZ-LGL", "name": "Lunglei", "center": [22.8833, 92.7333]}
        ]
    },
    "NL": {
        "name": "Nagaland",
        "type": "STATE",
        "center": [26.1584, 94.5624],
        "districts": [
            {"code": "NL-KHM", "name": "Kohima", "center": [25.6751, 94.1086]},
            {"code": "NL-DMP", "name": "Dimapur", "center": [25.9060, 93.7272]}
        ]
    },
    "OD": {
        "name": "Odisha",
        "type": "STATE",
        "center": [20.9517, 85.0985],
        "districts": [
            {"code": "OD-KHD", "name": "Khurda (Bhubaneswar)", "center": [20.2961, 85.8245]},
            {"code": "OD-CTC", "name": "Cuttack", "center": [20.4625, 85.8828]},
            {"code": "OD-SNG", "name": "Sundargarh (Rourkela)", "center": [22.2604, 84.8536]},
            {"code": "OD-GJM", "name": "Ganjam", "center": [19.3800, 85.0500]}
        ]
    },
    "PB": {
        "name": "Punjab",
        "type": "STATE",
        "center": [31.1471, 75.3412],
        "districts": [
            {"code": "PB-LDH", "name": "Ludhiana", "center": [30.9010, 75.8573]},
            {"code": "PB-ASR", "name": "Amritsar", "center": [31.6340, 74.8723]},
            {"code": "PB-JAL", "name": "Jalandhar", "center": [31.3260, 75.5762]},
            {"code": "PB-SAS", "name": "SAS Nagar (Mohali)", "center": [30.6799, 76.7221]}
        ]
    },
    "RJ": {
        "name": "Rajasthan",
        "type": "STATE",
        "center": [27.0238, 74.2179],
        "districts": [
            {"code": "RJ-JPR", "name": "Jaipur", "center": [26.9124, 75.7873]},
            {"code": "RJ-JHD", "name": "Jodhpur", "center": [26.2389, 73.0243]},
            {"code": "RJ-UDP", "name": "Udaipur", "center": [24.5854, 73.7125]},
            {"code": "RJ-KTA", "name": "Kota", "center": [25.2138, 75.8648]}
        ]
    },
    "SK": {
        "name": "Sikkim",
        "type": "STATE",
        "center": [27.5330, 88.5122],
        "districts": [
            {"code": "SK-GNT", "name": "Gangtok (East Sikkim)", "center": [27.3389, 88.6065]},
            {"code": "SK-NAM", "name": "Namchi (South Sikkim)", "center": [27.1667, 88.3500]}
        ]
    },
    "TN": {
        "name": "Tamil Nadu",
        "type": "STATE",
        "center": [11.1271, 78.6569],
        "districts": [
            {"code": "TN-CHE", "name": "Chennai", "center": [13.0827, 80.2707]},
            {"code": "TN-CBE", "name": "Coimbatore", "center": [11.0168, 76.9558]},
            {"code": "TN-MDU", "name": "Madurai", "center": [9.9252, 78.1198]},
            {"code": "TN-CGL", "name": "Chengalpattu", "center": [12.6841, 79.9836]},
            {"code": "TN-TRY", "name": "Tiruchirappalli", "center": [10.7905, 78.7047]}
        ]
    },
    "TS": {
        "name": "Telangana",
        "type": "STATE",
        "center": [18.1124, 79.0193],
        "districts": [
            {"code": "TS-HYD", "name": "Hyderabad", "center": [17.3850, 78.4867]},
            {"code": "TS-RNG", "name": "Ranga Reddy", "center": [17.3000, 78.4000]},
            {"code": "TS-WGL", "name": "Warangal", "center": [17.9689, 79.5941]},
            {"code": "TS-KHM", "name": "Khammam", "center": [17.2473, 80.1514]}
        ]
    },
    "TR": {
        "name": "Tripura",
        "type": "STATE",
        "center": [23.9408, 91.9882],
        "districts": [
            {"code": "TR-AGT", "name": "West Tripura (Agartala)", "center": [23.8315, 91.2868]},
            {"code": "TR-GMA", "name": "Gomati", "center": [23.5333, 91.4833]}
        ]
    },
    "UP": {
        "name": "Uttar Pradesh",
        "type": "STATE",
        "center": [26.8467, 80.9462],
        "districts": [
            {"code": "UP-LKO", "name": "Lucknow", "center": [26.8467, 80.9462]},
            {"code": "UP-GBN", "name": "Gautam Buddha Nagar (Noida)", "center": [28.5355, 77.3910]},
            {"code": "UP-KAN", "name": "Kanpur Nagar", "center": [26.4499, 80.3319]},
            {"code": "UP-VNS", "name": "Varanasi", "center": [25.3176, 82.9739]},
            {"code": "UP-AGR", "name": "Agra", "center": [27.1767, 78.0081]}
        ]
    },
    "UK": {
        "name": "Uttarakhand",
        "type": "STATE",
        "center": [30.0668, 79.0193],
        "districts": [
            {"code": "UK-DHR", "name": "Dehradun", "center": [30.3165, 78.0322]},
            {"code": "UK-HRD", "name": "Haridwar", "center": [29.9457, 78.1642]},
            {"code": "UK-NTL", "name": "Nainital", "center": [29.3803, 79.4636]}
        ]
    },
    "WB": {
        "name": "West Bengal",
        "type": "STATE",
        "center": [22.9868, 87.8550],
        "districts": [
            {"code": "WB-KOL", "name": "Kolkata", "center": [22.5726, 88.3639]},
            {"code": "WB-24P", "name": "North 24 Parganas", "center": [22.7200, 88.4800]},
            {"code": "WB-HWR", "name": "Howrah", "center": [22.5958, 88.2636]},
            {"code": "WB-PAS", "name": "Paschim Medinipur", "center": [22.4244, 87.3198]}
        ]
    },

    # --- UNION TERRITORIES (8) ---
    "AN": {
        "name": "Andaman and Nicobar Islands",
        "type": "UT",
        "center": [11.7401, 92.6586],
        "districts": [
            {"code": "AN-SND", "name": "South Andaman (Port Blair)", "center": [11.6234, 92.7265]}
        ]
    },
    "CH": {
        "name": "Chandigarh",
        "type": "UT",
        "center": [30.7333, 76.7794],
        "districts": [
            {"code": "CH-CHD", "name": "Chandigarh", "center": [30.7333, 76.7794]}
        ]
    },
    "DH": {
        "name": "Dadra and Nagar Haveli and Daman and Diu",
        "type": "UT",
        "center": [20.3974, 72.8328],
        "districts": [
            {"code": "DH-DMN", "name": "Daman", "center": [20.4283, 72.8397]},
            {"code": "DH-SLV", "name": "Silvassa", "center": [20.2763, 73.0083]}
        ]
    },
    "DL": {
        "name": "Delhi",
        "type": "UT",
        "center": [28.7041, 77.1025],
        "districts": [
            {"code": "DL-NDL", "name": "New Delhi", "center": [28.6139, 77.2090]},
            {"code": "DL-EDL", "name": "East Delhi", "center": [28.6280, 77.2950]},
            {"code": "DL-SDL", "name": "South Delhi", "center": [28.4817, 77.1873]}
        ]
    },
    "JK": {
        "name": "Jammu and Kashmir",
        "type": "UT",
        "center": [33.7782, 76.5762],
        "districts": [
            {"code": "JK-SGR", "name": "Srinagar", "center": [34.0837, 74.7973]},
            {"code": "JK-JMU", "name": "Jammu", "center": [32.7266, 74.8570]}
        ]
    },
    "LA": {
        "name": "Ladakh",
        "type": "UT",
        "center": [34.1526, 77.5771],
        "districts": [
            {"code": "LA-LEH", "name": "Leh", "center": [34.1526, 77.5771]},
            {"code": "LA-KRG", "name": "Kargil", "center": [34.5539, 76.1349]}
        ]
    },
    "LD": {
        "name": "Lakshadweep",
        "type": "UT",
        "center": [10.5667, 72.6417],
        "districts": [
            {"code": "LD-KVT", "name": "Kavaratti", "center": [10.5667, 72.6417]}
        ]
    },
    "PY": {
        "name": "Puducherry",
        "type": "UT",
        "center": [11.9416, 79.8083],
        "districts": [
            {"code": "PY-PUD", "name": "Puducherry", "center": [11.9416, 79.8083]},
            {"code": "PY-KKL", "name": "Karaikal", "center": [10.9254, 79.8380]}
        ]
    }
}


PROJECT_TYPES = [
    "Highway Expansion",
    "Railway Line & Freight Corridor",
    "Industrial Park & SEZ",
    "Urban Metro Rail",
    "Solar & Renewable Energy Park",
    "Port & Maritime Logistics",
    "Airport Expansion",
    "Water Pipeline & Dam Infrastructure"
]

LIFECYCLE_STAGES = [
    "Land Identification",
    "Survey",
    "Documentation",
    "Approval",
    "Notification",
    "Objection/Hearing",
    "Compensation",
    "Legal Resolution",
    "R&R",
    "Possession",
    "Final Handover"
]

ROLES = ["ADMIN", "STATE_OFFICER", "DISTRICT_OFFICER", "PROJECT_MANAGER", "ANALYST"]
SCOPES = ["NATIONAL", "STATE", "DISTRICT", "PROJECT"]
RISK_CATEGORIES = ["LOW", "MEDIUM", "HIGH", "CRITICAL"]
