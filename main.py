# %%  
# # Apple Health Data analyser

if __name__ == "__main__":
    import datetime as dt
    import xml.etree.ElementTree as ET
    from apple_health_analyzer import *
    
    tree = ET.parse('dati esportati.xml') 
    
    sunday_date = dt.date(2023, 9, 3)
    n_of_week = 1  # indica se è la prima, la seconda, la terza o la quarta settimana del mese
    apple_health_analyzer(tree,sunday_date, n_of_week)
        