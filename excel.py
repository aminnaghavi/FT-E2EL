import xlsxwriter     
import pandas as pd
import math

def writeNote(path,note):
    with open(path, 'w') as f:
        f.write(note)

def writeExelByCol(fname,titles,values,notes=None):
    if(notes!=None):
        writeNote(fname+'.txt',notes)
    book = xlsxwriter.Workbook(fname+'.xlsx')     
    sheet = book.add_worksheet()     
    # Rows and columns are zero indexed.     
    row = 0                 
    # iterating through the content list     
    for title in titles :    
        sheet.write(row, 0, title) 
        column=1
        for value in values[row]:
            try:
                sheet.write(row, column, value) 
            except:
                pass
            column+=1
        # incrementing the value of row by one with each iterations.     
        row += 1    
    book.close() 

def writeExelByRow(fname,titles,values,notes=None):
    if(notes!=None):
        writeNote(fname+'.txt',notes)
    book = xlsxwriter.Workbook(fname+'.xlsx')     
    sheet = book.add_worksheet()     
    # Rows and columns are zero indexed.         

    col = 0           
    # iterating through the content list     
    for title in titles :    
        sheet.write(0, col, title) 
        col+=1
    column=0
    for colvalues in values:    
        row=1
        for value in colvalues:
            try:
                sheet.write(row, column, value) 
            except:
                pass
            row+=1
        column+=1
        # incrementing the value of row by one with each iterations.        
    book.close() 

def writeExel2DHorizontal(fname,titlesH,titlesV,columnstitleV,values,notes=None):
    if(notes!=None):
        writeNote(fname+'.txt',notes)
    book = xlsxwriter.Workbook(fname+'.xlsx')     
    sheet = book.add_worksheet()     
    # Rows and columns are zero indexed.         

    c = 2           
    # iterating through the content list     
    for title in titlesH:    
        sheet.write(0, c, title) 
        c+=1
    r=1
    for title in titlesV:
        sheet.write(r+int(len(columnstitleV)/2), 0, title) 
        for coltitle in columnstitleV:
            sheet.write(r, 1, coltitle)
            r+=1 
        r+=1


    for ri in range(len(titlesV)):    
        row=0
        for rri in range(len(columnstitleV)):
            for ci in range(len(titlesH)):
                sheet.write(1+ri*(len(columnstitleV)+1)+rri, ci+2, values[rri][ri][ci]) 
        # incrementing the value of row by one with each iterations.        
    book.close() 


def writeExel2DVertical(fname,titlesV,titlesH,columnstitleH,values,notes=None):
    if(notes!=None):
        writeNote(fname+'.txt',notes)
    book = xlsxwriter.Workbook(fname+'.xlsx')     
    sheet = book.add_worksheet()     
    # Rows and columns are zero indexed.         

  
    r = 0
    # iterating through the content list     
    for title in titlesV:    
        sheet.write(len(titlesV)-1-r, 0, title) 
        r+=1

    c=1
    for title in titlesH:
        sheet.write(len(titlesV)+1, c+int(len(columnstitleH)/2), title) 
        for coltitle in columnstitleH:
            sheet.write(len(titlesV), c, coltitle)
            c+=1 
        c+=1   


        
        
    for ci in range(len(titlesH)):
        for cci in range(len(columnstitleH)):
            for ri in range(len(titlesV)):
                sheet.write((len(titlesV)-1)-ri, 1+ci*(len(columnstitleH)+1)+cci, values[cci][ci][ri]) 
                # incrementing the value of row by one with each iterations.  
    book.close() 




def readExel2DVertical(fname,methodnom=5):
    df=pd.read_excel(fname,engine='openpyxl',dtype=object,header=None)
    data = df.values.tolist()
    Ubounds = [x for x in data[-1] if(math.isnan(x)==False)]
    titles = [data[-2][i] for i in range(1,methodnom+1)]
    # print(titles)
    columns=list(df)
    bins=[]
    # print(int(len(columns)/(methodnom+1)))
    bins=[x for x in df[0] if(math.isnan(x)==False)]
    # print(bins)
    data=[[0 for i in range(methodnom)] for j in range(len(Ubounds))]
    for i in range(len(Ubounds)):
        for j in range(methodnom):
            data[i][j]=df[i*(methodnom+1)+j+1][0:len(bins)].to_list()
        # else:
            
    return Ubounds,titles,bins,data


            

    # print(df)