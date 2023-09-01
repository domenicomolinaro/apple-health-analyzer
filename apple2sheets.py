def apple_health_2_google_sheets(df, kind_of_database, month, n_of_week):
    import gspread
    from oauth2client.service_account import ServiceAccountCredentials
    import pygsheets
    import pandas as pd

    title_format = [1, 54, 95, 146, 197]
    training_subtitle_format = [2, 55, 96, 147]
    diet_subtitle_format = [27, 80, 121, 172]
    
    # Imposta il nome del foglio di lavoro su Google Sheets
    nome_foglio = 'apple_health_analysis'

    # Carica il DataFrame nel foglio di lavoro
    credentials_file ='/Users/domenicomolinaro/Desktop/apple_health_export/apple-heatlh-analyser-b0b71acfa62b.json'

    # Autenticazione con le credenziali del tuo progetto Google Cloud
    scope = ['https://spreadsheets.google.com/feeds', 'https://www.googleapis.com/auth/drive']
    creds = ServiceAccountCredentials.from_json_keyfile_name(credentials_file, scope)
    client = gspread.authorize(creds)
    email_utente = 'domenicomolinaro8@gmail.com'
    # Apri il foglio di lavoro esistente o crea un nuovo foglio
    try:
        sh = client.open(nome_foglio)
    except gspread.SpreadsheetNotFound:
        sh = client.create(nome_foglio)
        sh.share(email_utente, perm_type='user', role='writer')

    print(f"Link al foglio di lavoro: {sh.url}")
    
    if kind_of_database == 'training':
        df = df[['duration', 'energy_burned_in_kcal', 'BPM_min', 'BPM_max', 'BPM_mean', 'Corresponding_Day']]
    
    elif kind_of_database == 'diet':
        df = df [['sugar', 'protein', 'fiber', 'sodium', 'carbo','Corresponding_Day','energy']]
    
    
    elif kind_of_database == 'running':
        return 0 # da scrivere
    else:   
        print('unknown kind_of_database')
        return 0
    

    try:
    # Verifica se il worksheet esiste
        worksheet = sh.worksheet(month)
    except gspread.exceptions.WorksheetNotFound:
    # Se il worksheet non esiste, lo creiamo
        worksheet = sh.add_worksheet(title=month, rows=500, cols=500)
       
    ################################################
    ### PAGE FORMATING   
    ################################################

        for n in title_format:
        ## WEEK FORMATTING
            worksheet.format("A" + str(n), {"textFormat": {"bold": True, "fontSize" : 18},"horizontalAlignment": "LEFT"})
        
        for n in training_subtitle_format:
        ## LABEL FORMATTING
            worksheet.format("A" + str(n), {"textFormat": {"bold": True, "fontSize" : 13},"horizontalAlignment": "LEFT"})
            worksheet.update("A" + str(n), 'Training data ')
            
        for n in diet_subtitle_format:
            worksheet.format("A" + str(n), {"textFormat": {"bold": True, "fontSize" : 13},"horizontalAlignment": "LEFT"})
            worksheet.update("A" + str(n), 'Diet Data')    
        

        worksheet.update('A' + str(title_format[0]), 'Week 1')

        worksheet.update('A' + str(title_format[1]), 'Week 2')

        worksheet.update('A' + str(title_format[2]), 'Week 3')

        worksheet.update('A' + str(title_format[3]), 'Week 4')

        worksheet.update('A' + str(title_format[4]), 'Overall ' + month + ' data')
        
        worksheet.update('A' + str(title_format[4]+1), 'Overall training data')
        worksheet.format("A" + str(title_format[4]+1), {"textFormat": {"bold": True, "fontSize" : 13},"horizontalAlignment": "LEFT"})

        worksheet.update("A" + str(title_format[4]+2), 'mean_duration')
        worksheet.update("B" + str(title_format[4]+2), 'mean_energy_consumed')
        worksheet.update("C" + str(title_format[4]+2), 'mean_BPM_min')
        worksheet.update("D" + str(title_format[4]+2), 'mean_BPM_max')
        worksheet.update("E" + str(title_format[4]+2), 'mean_BPM_mean')
        worksheet.update("F" + str(title_format[4]+2), 'week')

        
        worksheet.update('A' + str(title_format[4]+26), 'Overall diet data')
        worksheet.format("A" + str(title_format[4]+26), {"textFormat": {"bold": True, "fontSize" : 13},"horizontalAlignment": "LEFT"})
        
        worksheet.update("A" + str(title_format[4]+27), 'mean_sugar')
        worksheet.update("B" + str(title_format[4]+27), 'mean_protein')
        worksheet.update("C" + str(title_format[4]+27), 'mean_fiber')
        worksheet.update("D" + str(title_format[4]+27), 'mean_sodium')
        worksheet.update("E" + str(title_format[4]+27), 'mean_carbo')
        worksheet.update("F" + str(title_format[4]+27), 'week')
        worksheet.update("G" + str(title_format[4]+27), 'mean_energy')
        

    ################################################
    ## ADDING DATABASE
    ################################################
        
    if n_of_week == 1:
        if kind_of_database == 'training':
            worksheet.update('A'+ str(training_subtitle_format[0]+1),[df.columns.values.tolist()] + df.values.tolist() )
        if kind_of_database == 'diet':
            worksheet.update('A'+str(diet_subtitle_format[0]+1),[df.columns.values.tolist()] + df.values.tolist() )
    
    
    elif n_of_week == 2:
        if kind_of_database == 'training':
            worksheet.update('A'+ str(training_subtitle_format[1]+1),[df.columns.values.tolist()] + df.values.tolist() )
        if kind_of_database == 'diet':
            worksheet.update('A'+str(diet_subtitle_format[1]+1),[df.columns.values.tolist()] + df.values.tolist() )
    
    
    elif n_of_week == 3:
        if kind_of_database == 'training':
            worksheet.update('A'+ str(training_subtitle_format[2]+1),[df.columns.values.tolist()] + df.values.tolist() )
        if kind_of_database == 'diet':
            worksheet.update('A'+str(diet_subtitle_format[2]+1),[df.columns.values.tolist()] + df.values.tolist() )
    
    
    elif n_of_week == 4:
        if kind_of_database == 'training':
            worksheet.update('A'+ str(training_subtitle_format[3]+1),[df.columns.values.tolist()] + df.values.tolist() )
        if kind_of_database == 'diet':
            worksheet.update('A'+str(diet_subtitle_format[3]+1),[df.columns.values.tolist()] + df.values.tolist() )

    ##################################################
    ## MONTH RECORD
    ################################################
    # TRAINING
    
    coordinate_training = ['A', 'B', 'C', 'D','E','F']
    coordinate_diet = ['A', 'B', 'C', 'D','E','F','G']


    if kind_of_database == 'training':

        
        mean_duration = df[df['duration'] != 0]['duration'].mean()
        mean_energy = df[df['energy_burned_in_kcal'] != 0]['energy_burned_in_kcal'].mean()
        mean_bpm_min = df[df['BPM_min'] != 0]['BPM_min'].mean()
        mean_bpm_max = df[df['BPM_max'] != 0]['BPM_max'].mean()
        mean_bpm_mean = df[df['BPM_mean'] != 0]['BPM_mean'].mean()
        week = {
            1 : 'first week',
            2 : 'second week',
            3 : 'third week',
            4 : 'fourth week',
        }
        weekly_review = [mean_duration, mean_energy, mean_bpm_min, mean_bpm_max, mean_bpm_mean, week[n_of_week]]
        for i in range(len(weekly_review)):
            worksheet.update(coordinate_training[i] + str(title_format[4]+2+n_of_week),weekly_review[i])
            
    if kind_of_database == 'diet':
        mean_sugar = df[df['sugar'] != 0]['sugar'].mean()
        mean_protein = df[df['protein'] != 0]['protein'].mean()
        mean_fiber = df[df['fiber'] != 0]['fiber'].mean()
        mean_sodium = df[df['sodium'] != 0]['sodium'].mean()
        mean_carbo = df[df['carbo'] != 0]['carbo'].mean()
        mean_energy = df[df['energy'] != 0]['energy'].mean()
        week = {
            1 : 'first week',
            2 : 'second week',
            3 : 'third week',
            4 : 'fourth week',
        }
        weekly_review = [
            mean_sugar,
            mean_protein,
            mean_fiber,
            mean_sodium,
            mean_carbo,
            mean_energy,
            week[n_of_week]
        ]
        for i in range(len(weekly_review)):
            worksheet.update(coordinate_diet[i] + str(title_format[4]+27+n_of_week),weekly_review[i])

    ## controllo se l'ultima cella della tabella TRAINING MONTH e di DIET MONTH per fare POI i grafici 
    # (la variabile worksheet viene sostituita passando dal tipo gspread al tipo pysheets)
    cell_value_train = worksheet.get('A'+str(title_format[4]+2+4))
    cell_value_diet = worksheet.get('A'+str(title_format[4]+27+4))

    ################################################
    ## ADDING FIGURE
    ################################################
    gc = pygsheets.authorize(service_file='/Users/domenicomolinaro/Desktop/apple_health_export/apple-heatlh-analyser-b0b71acfa62b.json')
    sh = gc.open(nome_foglio)
    worksheet = sh.worksheet_by_title(month)
    
    columns_list = df.columns.to_list()
    
    ## Training 
    if kind_of_database == 'training':
        #x_coordinate = ((6,training_subtitle_format[n_of_week-1]+2),(6, training_subtitle_format[n_of_week-1]+2+6))
        x_coordinate = ((training_subtitle_format[n_of_week-1]+2,6),( training_subtitle_format[n_of_week-1]+2+6,6))

        indice = 10
        for index in range(5):
            y_coordinate = ((training_subtitle_format[n_of_week-1]+2,index+1), ( training_subtitle_format[n_of_week-1]+2+6,index+1) )
            worksheet.add_chart(
                x_coordinate, 
                [y_coordinate], 
                title= columns_list[index], 
                chart_type= pygsheets.ChartType.LINE, 
                anchor_cell= (training_subtitle_format[n_of_week-1]+1, indice),
            )
            indice += 7
    
    ## Diet
    if kind_of_database == 'diet':
        x_coordinate =(coordinate_diet[-2]+str(diet_subtitle_format[n_of_week-1]+2),coordinate_diet[-2]+str(diet_subtitle_format[n_of_week-1]+2+6))
        indice = 10
        y_coordinate = [(coordinate_diet[0]+ str(diet_subtitle_format[n_of_week-1]+2),coordinate_diet[0]+ str(diet_subtitle_format[n_of_week-1]+2+6)),
                        (coordinate_diet[1]+ str(diet_subtitle_format[n_of_week-1]+2),coordinate_diet[1]+ str(diet_subtitle_format[n_of_week-1]+2+6)),
                        (coordinate_diet[2]+ str(diet_subtitle_format[n_of_week-1]+2),coordinate_diet[2]+ str(diet_subtitle_format[n_of_week-1]+2+6)),
                        (coordinate_diet[3]+ str(diet_subtitle_format[n_of_week-1]+2),coordinate_diet[3]+ str(diet_subtitle_format[n_of_week-1]+2+6)),
                        (coordinate_diet[4]+ str(diet_subtitle_format[n_of_week-1]+2),coordinate_diet[4]+ str(diet_subtitle_format[n_of_week-1]+2+6)),
                        ]
        worksheet.add_chart(
            x_coordinate, 
            y_coordinate, 
            title= 'Overall macro consumption', 
            anchor_cell= (diet_subtitle_format[n_of_week-1]+1, indice),
        )
        
        indice += 7
        y_coordinate = (coordinate_diet[-1]+str(diet_subtitle_format[n_of_week-1]+2),coordinate_diet[-1]+str(diet_subtitle_format[n_of_week-1]+2+6))
        worksheet.add_chart(
            x_coordinate, 
            [y_coordinate], 
            title= 'Overall calories assumed', 
            anchor_cell= (diet_subtitle_format[n_of_week-1]+1, indice),
            chart_type = pygsheets.ChartType.LINE,
         )
        
    ################################################
    ## GRAFICI FINE MESE
    ################################################
    if not cell_value_diet and not cell_value_train:
        print("non è ancora il momento")
    else:

        # fai grafici training
        x_coordinate = (coordinate_training[-1]+str(title_format[4]+3),coordinate_training[-1]+str(title_format[4]+3+3))
        indice = 10
        titoli = ["mean_duration", "mean_energy_conserved", "mean_BPM_min", 'mean_BPM_max', 'mean_BPM_mean']
        for i in range(len(coordinate_training)-1):
            y_coordinate = (coordinate_training[i]+str(title_format[4]+3), coordinate_training[i]+str(title_format[4]+3+3))
            worksheet.add_chart(
                x_coordinate,
                [y_coordinate],
                title = titoli[i],
                chart_type= pygsheets.ChartType.LINE, 
                anchor_cell = (title_format[4]+1, indice)
            )
            indice += 7
        
        # fai grafici diet
        x_coordinate = (coordinate_diet[-2]+str(title_format[4]+28),coordinate_diet[-2]+str(title_format[4]+28+3))
        indice = 10
        y_coordinate = [(coordinate_diet[0]+str(title_format[4]+28),coordinate_diet[0]+str(title_format[4]+28+3)),
                        (coordinate_diet[1]+str(title_format[4]+28),coordinate_diet[1]+str(title_format[4]+28+3)),
                        (coordinate_diet[2]+str(title_format[4]+28),coordinate_diet[2]+str(title_format[4]+28+3)),
                        (coordinate_diet[3]+str(title_format[4]+28),coordinate_diet[3]+str(title_format[4]+28+3)),
                        (coordinate_diet[4]+str(title_format[4]+28),coordinate_diet[4]+str(title_format[4]+28+3)),
                        ]
        worksheet.add_chart(
            x_coordinate,
            y_coordinate,
            title = 'Mean macros over current month',
            #chart_type = pygsheets.ChartType.LINE,
            anchor_cell = (title_format[4]+28, indice),
        )

        y_coordinate = (coordinate_diet[-1]+str(title_format[4]+28),coordinate_diet[-1]+str(title_format[4]+28+3))
        indice += 7
        worksheet.add_chart(
            x_coordinate,
            [y_coordinate],
            title = 'Overall mean calories assumed',
            chart_type = pygsheets.ChartType.LINE,
            anchor_cell = (title_format[4]+28, indice),
        )