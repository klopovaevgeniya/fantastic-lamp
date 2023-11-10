import ctypes
import msvcrt
import os
import winsound
import json
import sys
import datetime
import csv

# --- Вспомогательные функции -------------------------------------------
# --- Функция установки курсора в заданную позицию
def gotoxy(x,y):
    print ("%c[%d;%df" % (0x1B, y, x), end='')
    

# --- Функция вывода сообщения в заданных координатах и заданным цветом
def printColoredText(lx, ty, text="", fCol="white", bCol="black", stil="regular"):
    gotoxy(lx,ty)

    myColors = ["black", "red", "green", "yellow", "blue", "magenta", "cyan", "white"]
    outStr  = "\033[0m"
    outStr += "\033["+("1;" if stil=="light" else "") + str(myColors.index(fCol)+30)+"m";
    outStr += "\033["+str(myColors.index(bCol)+40)+"m";
    print(outStr+text, end="")


# --- Функция ожидания нажатия любой клавиши
def getch():
    sys.stdout.flush()
    chCode = int.from_bytes(msvcrt.getch(), "big")
    if chCode in range(127,176):   #А..Я,а..п
        chCode += 912
    elif chCode in range(224,242): #р..я
        chCode += 864
    res = chr(chCode)
    return res


# --- Функция разбиения строки на подстроки по заданной ширине по словам
def formatStr(strLine="", strWidth=0):
    res = []
    tmp = strLine.split()

    i = 0; s = ""
    while i<len(tmp):
        tmp[i] = tmp[i].replace('"','\"')

        if tmp[i]=="<p>":
            res.append(s); s = ""; i += 1
        elif len(s) + len(tmp[i]) < strWidth:
            s += tmp[i]+" "; i +=1
        else:
            res.append(s); s = ""

    if len(s)>0:
        res.append(s)
    return res


# --- Функция ввода строки
def readLine(x,y,inpLen=10,oldStr=""):
    #validChars 

    gotoxy(x+len(oldStr),y)
    res  = oldStr
    while True:
        ch = getch()

        if ord(ch)==27:   # ESC
            res = oldStr
            break
        elif ord(ch)==13: # Enter
            break
        elif (ch.isalnum() or (ch in (" ","-","_"))) and (len(res)<inpLen):
            res += ch
            gotoxy(x,y); print(res, end="")
        elif (ch == "\x08") and (len(res)>0): # Backspace
            res = res[:-1]
            gotoxy(x,y); print(" "*inpLen, end="")
            gotoxy(x,y); print(res, end="")
    return res


# --- Функции и переменные обеспечения игры ------------------------------------------
# --- Глобальные переменные и настройки
kernel32 = ctypes.windll.kernel32;
kernel32.SetConsoleMode(kernel32.GetStdHandle(-11), 7);
sgFileName  = "savegame.json"
csvFileName = "results.csv"

curPlayer  = {"id":0,"name":"", "energy":100, "roomNum":0, "matches":5,
              "medicals":0, "knifes":0, "gold":0, "winner":0}
dialStopLine = -1
rooms = [
         {
            "num"        : 0,
            "name"       : "Чулан",
            "description": "Это комната, с которой начинается Ваше путешествие. В комнате мрачно, на потолке тускло светит маленькая лампа. "+
                           "Из-за этого можно разглядеть только двери и их номера, а в углах - непроглядная темнота...",
            "visited"    : 1,
            "medicals"   : 3,
            "matches"    : 6,
            "knifes"     : 2,
            "gold"       : 100,
            "monster"    : {"count":0, "name":"", "damage":0},
            "doors" :[
                        { "num":1, "toRoom":3 },
                        { "num":2, "toRoom":2 },
                        { "num":3, "toRoom":1 }
                     ]
         },
         {
            "num"        : 1,
            "name"       : "Спальня",
            "description": "В комнате мрачно, над прикроватной тумбочкой слабо горит светильник-бра. "+
                           "Он освещает часть комнаты, поэтому можно разглядеть только двери и их номера, "+
                           "а в углах, как, похоже и во всех других комнатах, - темнота и ничего не видно...",
            "visited"    : 0,
            "medicals"   : 3,
            "matches"    : 0,
            "knifes"     : 0,
            "gold"       : 1000,
            "monster"    : {"count":0, "name":"", "damage":0},
            "doors" :[
                        { "num":1, "toRoom":0 },
                        { "num":2, "toRoom":6 },
                        { "num":3, "toRoom":4 },
                        { "num":4, "toRoom":5 }
                     ]
         },
         {
            "num"        : 2,
            "name"       : "Гардеробная",
            "description": "Дааа... Когда-то здесь было достаточно светло... Но сейчас из-за скопившейся на "+
                           "зажженном светильнике пыли света хватает только для того, чтобы разглядеть очертания "+
                           "дверей и номеров на них... По углам комнаты - непроглядный мрак и страх...",
            "visited"    : 0,
            "medicals"   : 0,
            "matches"    : 6,
            "knifes"     : 1,
            "gold"       : 0,
            "monster"    : {"count":0, "name":"", "damage":0},
            "doors" :[
                        { "num":1, "toRoom":3 },
                        { "num":2, "toRoom":6 },
                        { "num":3, "toRoom":0 }
                     ]
         },
         {
            "num"        : 3,
            "name"       : "Кухня",
            "description": "Хм... Довольно чистенькая кухонька...Правда, и здесь по углам - непроглядный мрак... "+
                           "И только слабый свет единстаенной лампочки в приоткрытом холодильнике дает Вам возможность "+
                           "разглядеть двери в другие комнты и номера на них...",
            "visited"    : 0,
            "medicals"   : 3,
            "matches"    : 4,
            "knifes"     : 4,
            "gold"       : 0,
            "monster"    : {"count":1, "name":"ОГРОМНАЯ ГЕННО-МОДИФИЦИРОВАННАЯ ОСА", "damage":25},
            "doors" :[
                        { "num":1, "toRoom":2 },
                        { "num":2, "toRoom":0 },
                        { "num":3, "toRoom":5 }
                     ]
         },
         {
            "num"        : 4,
            "name"       : "Кабинет",
            "description": "Ты добрался до кабинета...Здесь много книг о разных сверхъественных существах, "+
                           "стол с записями о наблюдениях в лесу, который находится неподалёку от дома."+
                           "Должно быть здесь много разных вещичек, они могут пригодиться вам в дальнейшем...",
            "visited"    : 0,
            "medicals"   : 5,
            "matches"    : 7,
            "knifes"     : 2,
            "gold"       : 0,
            "monster"    : {"count":0, "name":"", "damage":0},
            "doors" :[
                        { "num":1, "toRoom":1 },
                        { "num":2, "toRoom":7 },
                        { "num":3, "toRoom":5 }
                     ]
         },
         {
            "num"        : 5,
            "name"       : "Столовая",
            "description": "Вы добрались до столовой...здесь неприятный запах, скорее всего монстр здесь побывал"+
                           "и потрапезничал. Лучше быстренько осмотреться и идти дальше..."+
                           "",
            "visited"    : 0,
            "medicals"   : 0,
            "matches"    : 8,
            "knifes"     : 0,
            "gold"       : 50,
            "monster"    : {"count":0, "name":"", "damage":0},
            "doors" :[
                        { "num":1, "toRoom":3 },
                        { "num":2, "toRoom":1 },
                        { "num":3, "toRoom":4 }
                     ]
         },
         {
            "num"        : 6,
            "name"       : "Гостиная",
            "description": "В гостиной стоял большой диван, а рядом лежал ковёр. Стояли шкафы с сербранным сервизом, "+
                           "много различных столовых наборов. Стоял комод, ящик которого был немного приоткрыт..."+
                           "Около комода стоял торшер, но он был сломан...",
            "visited"    : 0,
            "medicals"   : 5,
            "matches"    : 3,
            "knifes"     : 0,
            "gold"       : 0,
            "monster"    : {"count":0, "name":"", "damage":0},
            "doors" :[
                        { "num":1, "toRoom":2 },
                        { "num":2, "toRoom":7 },
                        { "num":3, "toRoom":1 }
                     ]
         },
         {
            "num"        : 7,
            "name"       : "Винный погреб",
            "description": "Вы добрались до винного погреба...Здесь много бутылок различных напитков из разных стран."+
                           "На полу тоже лежали бутылки..некоторые пустые, какие-то были разбиты. От разлитого вина остались следы."+
                           "Как всегда, не видно ничего, кроме дверей с их номерами...",
            "visited"    : 0,
            "medicals"   : 0,
            "matches"    : 0,
            "knifes"     : 0,
            "gold"       : 1000,
            "monster"    : {"count":0, "name":"", "damage":0},
            "doors" :[
                        { "num":1, "toRoom":6  },
                        { "num":2, "toRoom":-1 }, # Это выход
                        { "num":3, "toRoom":4  }
                     ]
         }
        ]


# --- Функция рисования интерфейса игры
def showInterface():
    #                       0         1         2         3         4         5         6         7         8         9        10        11
    #                       0123456789012345678901234567890123456789012345678901234567890123456789012345678901234567890123456789012345678901234 
    printColoredText(0, 1, "┌─────────────────────────── ДИАЛОГ ───────────────────────────┬────────────────────── ИГРОК ─────────────────────┐\n" +
                           "│                                                              │                                                  │\n" +
                           "│                                                              │                                                  │\n" +
                           "│                                                              ├──────────────────── ИНВЕНТАРЬ ───────────────────┤\n" +
                           "│                                                              │                                                  │\n" +
                           "│                                                              │                                                  │\n" +
                           "│                                                              │                                                  │\n" +
                           "│                                                              │                                                  │\n" +
                           "│                                                              │                                                  │\n" +
                           "│                                                              ├──────────────────── УПРАВЛЕНИЕ ──────────────────┤\n" +
                           "│                                                              │                                                  │\n" +
                           "│                                                              │                                                  │\n" +
                           "│                                                              │                                                  │\n" +
                           "│                                                              │                                                  │\n" +
                           "│                                                              │                                                  │\n" +
                           "│                                                              │                                                  │\n" +
                           "│                                                              │                                                  │\n" +
                           "│                                                              │                                                  │\n" +
                           "│                                                              │                                                  │\n" +
                           "└──────────────────────────────────────────────────────────────┴──────────────────────────────────────────────────┘", "white", "blue")


# --- Функция для очистки области "ДИАЛОГ"
def clearDialogArea():
    i=2
    while i<20:
        gotoxy(2,i); print(" " * 62)
        i+=1


# --- Функция вывода "Предыстории"
def introText():
    dearPlayer = "Дорогой "+curPlayer["name"]+"!"
    while len(dearPlayer)<60:
        dearPlayer = " " + dearPlayer +" "

    introText = ("Вы находитесь в темном \"лабиринте\" комнат, связанных между собой "+
                 "иногда короткими, а иногда длинными и извивающимися проходами, в которые "+
                 "ведут по несколько дверей. Вам надо выйти из этого \"лабиринта\", "+
                 "открывая двери и переходя из комнаты - в комнату... <p> <p> С каждым Вашим "+
                 "действием здоровье ухудшается, но его можно поправить, используя "+
                 "опции игры... <p> <p> Удачи!")

    tmp1 = ["        Добро пожаловать в игру \"Загадочные комнаты\"!", "", dearPlayer]
    tmp2 = formatStr(introText,60)
    msg  = tmp1 + tmp2

    clearDialogArea()
    i=0
    while i<len(msg):
        printColoredText(3,i+2,msg[i], "white","blue")
        i+=1
    printColoredText(12,19,"Нажмите любую клавишу для продолжения...", "white","blue")
    getch()


# --- Функция вывода финального текста
def finalText():
    clearDialogArea()
    printColoredText(25,8, "Игра окончена!", "white", "blue", "light")
    printColoredText(15,9, "Спасибо за участие, ждем Вас снова!", "white", "blue", "light")
    if curPlayer["energy"] == 0:
        printColoredText(10,11, "P.S. Очень жаль, что Вам не хватило здоровья...", "red", "blue", "light")
    elif curPlayer["winner"] == 1:
        printColoredText(15,11, "ПОЗДРАВЛЯЕМ!!! ВЫ ПРОШЛИ ЛАБИРИНТ!!!", "green", "blue", "light")


# --- Функция ввода имени игрока
def newPlayer():
    clearDialogArea()
    printColoredText(3, 8, "Введите имя нового игрока: ", "white", "blue")
    curPlayer["name"]     = readLine(30,8,30,curPlayer["name"])
    curPlayer["energy"]   = 100
    curPlayer["matches"]  = 5
    curPlayer["medicals"] = 0
    curPlayer["roomNum"]  = 0
    curPlayer["id"] = str(datetime.datetime.now())


# --- Функция сохранения игры
def saveGame():
    sgData = [];
    playerExists = False

    if os.path.exists(sgFileName):
        sgFile = open(sgFileName, "r")
        sgData = json.load(sgFile)
        sgFile.close()

    for item in range(0, len(sgData)-1, 2):
        if curPlayer["id"] == sgData[item]["id"]:
            sgData[item] = curPlayer
            sgData[item+1] = rooms
            playerExists = True
            break

    if playerExists != True:
        sgData.extend([curPlayer, rooms])

    sgFile = open(sgFileName, "w+")
    json.dump(sgData, sgFile)
    sgFile.close()

    # Сохраняем CSV-файл
    headers = []
    for field in curPlayer:
        headers.append(field)

    data = []
    for item in range(0, len(sgData)-1, 2):
        data.append(sgData[item])

    with open(csvFileName, "w+", newline="") as file:
        writer = csv.DictWriter(file,fieldnames=headers,delimiter=";")
        writer.writeheader()
        writer.writerows(data)
        file.close()


# --- Функция формирования меню сохраненных игр
def makeMenu(sg_Data):
    menu = [{"name":"<НАЧАТЬ НОВУЮ ИГРУ>","value":-1}]
    for i in range(0, len(sg_Data), 2):
        menu.append({"name":(str(len(menu))+". ").ljust(4," ")+sg_Data[i]["name"],"value":i})
    return menu


# --- Функция выбора игрока из списка сохраненных игр
def selectPlayer():
    if os.path.exists(sgFileName):
        sgFile = open(sgFileName)
        sgData = json.load(sgFile)
        sgFile.close()
    else:
        sgData = []

    selRes=-1
    curItem=0

    printColoredText(12,2,"Список сохраненных игр (по имени игрока):","white","blue","light")
    printColoredText(66,11,"Перемещение: ↑↓","white","blue")
    printColoredText(66,12,"Выбор      : ◄┘","white","blue")
    printColoredText(66,13,"Удалить    : Ctrl-Del","white","blue")
    printColoredText(66,15,"Примечание:","white","blue")
    printColoredText(66,16,"Сохраненных игр может быть не более 15","white","blue")

    while True:
        menuItems = makeMenu(sgData)
        for i in range(16):
            printColoredText(2,i+4," "*62,"white","blue")

        for item in range(0, len(menuItems)):
            printColoredText(10,4+item,str("-> " if item==curItem else "   ")+menuItems[item]["name"],"white","blue")
        printColoredText(104,16,"","white","blue")

        choice = ord(getch())
        if choice == 13: # Enter
            if ((len(menuItems)==16) and (menuItems[curItem]["value"]==-1))==False:
                selRes = menuItems[curItem]["value"]
                break
        elif choice == 80: # Стрелка "вниз"
            if curItem == len(menuItems)-1:
                curItem = 0
            else:
                curItem += 1
        elif choice == 72: # Стрелка "вверх"
            if curItem == 0:
                curItem = len(menuItems)-1
            else:
                curItem -= 1
        elif choice == 1059:  # Удалить сохраненную игру Crtl-Del
            if menuItems[curItem]["value"] != -1:
                sgData.pop(menuItems[curItem]["value"])
                sgData.pop(menuItems[curItem]["value"])
                curItem=0

                sgFile = open(sgFileName, "w+")
                json.dump(sgData, sgFile)
                sgFile.close()

    if selRes==-1:
        newPlayer()
    else:
        global curPlayer, rooms
        curPlayer = sgData[selRes]
        rooms     = sgData[selRes+1]

    for i in range(6):
        printColoredText(66,i+11," "*48,"white","blue")


# --- Функция отображения запаса энергии
def showEnergy(enVol=0):
    indLength = 29
    fullStr   = int(round(enVol*indLength/100,0))
    emptStr   = indLength-fullStr
    tmp       = " " if enVol < 100 else ""
    energyStr = "█"*fullStr + "▓"*emptStr + tmp + " %.2f%%"

    if enVol > 50:
        printColoredText(78,3,energyStr % (round(enVol,2)),"green","blue","light")
    elif enVol > 25:
        printColoredText(78,3,energyStr % (round(enVol,2)),"yellow","blue")
    else:
        printColoredText(78,3,energyStr % (round(enVol,2)),"red","blue","light")


# --- Функция вывода параметров игрока
def showPlayerParams():
    # Область ИГРОК
    printColoredText(66,2, "Имя игрока: "+curPlayer["name"],"white","blue")
    printColoredText(66,3, "Здоровье  : ","white","blue")
    showEnergy(curPlayer["energy"])

    # Область ИНВЕНТАРЬ
    printColoredText(66,5, "Спички  : " + str(curPlayer["matches"]).ljust(3," ")+"\t(освещает комнату 1 раз)","white","blue")
    printColoredText(66,6, "Аптечки : " + str(curPlayer["medicals"]).ljust(3," "),"white","blue")
    printColoredText(66,7, "Ножи    : " + str(curPlayer["knifes"]).ljust(3," ")+"\t(автоматически убивает врага)","white","blue")
    printColoredText(66,8, "Золото  : " + str(curPlayer["gold"]).ljust(3," "),"white","blue")

    # Область УПРАВЛЕНИЕ
    printColoredText(66,11, "Войти в дверь        (-1% здоровья) : 1..9","white","blue")
    printColoredText(66,12, "Испльзовать спичку   (-1% здоровья) : F","white","blue")
    printColoredText(66,13, "Использовать аптечку (+5% здоровья) : G","white","blue")
    printColoredText(66,15, "Закончить иргать (с сохранением)    : Q","white","blue")


# --- Функция выбора комнаты
def gotoRoom(roomNumber):
    global rooms
    global curPlayer
    global dialStopLine

    if roomNumber == -1: # Номер комнаты, равный "-1" - это выход из лабиринта
        curPlayer["winner"]=1
        return

    i=0
    while i<len(rooms):
        if rooms[i]["num"] == roomNumber:
            rNum = i
            break
        i+=1
    rooms[rNum]["visited"] = 1;

    # Вывод заголовка
    rName = "Вы - в комнате №"+str(rooms[rNum]["num"])+" ("+rooms[rNum]["name"]+")"
    printColoredText(3,2, rName, "white","blue","light")
    printColoredText(3,3, "-"*len(rName), "white","blue","light")

    # Вывод описания
    outStr = "<p> В комнате "+str(len(rooms[rNum]["doors"]))+" двери с номерами: "
    i = 0
    while i < len(rooms[rNum]["doors"]):
        toRoomNum   = rooms[rNum]["doors"][i]["toRoom"]
        toRoomName  = rooms[toRoomNum]["name"]
        toRoomVisit = rooms[toRoomNum]["visited"]

        outStr += str(rooms[rNum]["doors"][i]["num"])
        outStr += " (комната №"+str(toRoomNum)+"-"+toRoomName+")" if toRoomVisit==1 else " (неизвестная комната)"
        outStr += ", " if i<len(rooms[rNum]["doors"])-1 else ""
        i+=1

    lines1 = formatStr(rooms[rNum]["description"],60)
    lines2 = formatStr(outStr, 60)
    lines = lines1 + lines2

    i = 0
    while i<len(lines):
        printColoredText(3,i+4,lines[i],"white","blue")
        i+=1
    dialStopLine = len(lines) + 2

    if rooms[rNum]["monster"]["count"] > 0:
        monsterInRoom(dialStopLine, rNum)

    printColoredText(25, 19, "Ваш выбор ?", "white", "blue")
    

# --- Функция имитации атаки монстра
def monsterInRoom(topY, rN):
    global rooms
    global curPlayer

    if rooms[rN]["monster"]["count"] == 0:
        return
    tmpStr = "О, ужас! В комнате оказался злобный монстр - "+rooms[rN]["monster"]["name"]+"!!! "
    if curPlayer["knifes"] > 0:
        msgColor = "green"
        curPlayer["knifes"] -= 1
        rooms[rN]["monster"]["count"] -= 1
        tmpStr += ("Но у Вас был нож! И этим ножом Вы храбро уничтожили монстра! "+
                  "Правда и нож больше ни на что не годится, пришлось его выбросить...")
    else:
        msgColor = "red"
        curPlayer["energy"] -= rooms[rN]["monster"]["damage"]
        if curPlayer["energy"] < 0:
            curPlayer["energy"] = 0;

        tmpStr += ("К сожалению, у Вас нет ножей и уничтожить монстра Вам нечем... "+
                   "Поэтому, враг нанес Вам урон на ")
        tmpStr += str(rooms[rN]["monster"]["damage"])
        tmpStr += ("% ВАЖНО! Монстр так и будет нападать на Вас всякий раз, "+
                   "когда Вы будете входить в эту комнату, пока Вы не убьете его ножом")

    msg = formatStr(tmpStr, 60)
    i=0;
    while i<len(msg):
        printColoredText(3,topY+3+i, msg[i].ljust(60),msgColor,"white")
        i+=1
      
    showPlayerParams()
    printColoredText(12,19,"Нажмите любую клавишу для продолжения...", "white", "blue")
    getch()

    i=topY;
    while i<17:
        printColoredText(3, i+3, (" "*60),"white","blue")
        i+=1


# --- Функция обработки клавиши 'F' - использовать спичку
def usedMatches():
    global rooms
    global curPlayer

    if curPlayer["matches"]>0:
        curPlayer["matches"] -= 1
        curPlayer["energy"]  -= 1
        msgColor = "red"
        showPlayerParams()

        tmpStr = "Вы зажгли спичку, и на некоторое время тьма в углах комнаты рассеялась, и Вы нашли..."
        foundCount = 0
        rNum = curPlayer["roomNum"]

        if rooms[rNum]["matches"] > 0: # Если в комнате нашлись спички
            tmpStr += " спички (" + str(rooms[rNum]["matches"]) +" шт.)"
            curPlayer["matches"] += rooms[rNum]["matches"]
            foundCount           += rooms[rNum]["matches"]
            rooms[rNum]["matches"] = 0

        if rooms[rNum]["knifes"] > 0:  # Если в комнате нашлись ножи
            tmpStr += " ножи (" + str(rooms[rNum]["knifes"]) +" шт.)"
            curPlayer["knifes"] += rooms[rNum]["knifes"]
            foundCount         += rooms[rNum]["knifes"]
            rooms[rNum]["knifes"] = 0

        if rooms[rNum]["medicals"] > 0: # Если в комнате нашлись аптечки
            curPlayer["medicals"] += rooms[rNum]["medicals"]
            foundCount           += rooms[rNum]["medicals"]
            tmpStr += " аптечки (" + str(rooms[rNum]["medicals"]) +" шт.)"
            rooms[rNum]["medicals"] = 0

        if rooms[rNum]["gold"] > 0:    # Если в комнате нашлось золото
            curPlayer["gold"] += rooms[rNum]["gold"]
            foundCount        += rooms[rNum]["gold"]
            tmpStr += " золото (" + str(rooms[rNum]["gold"]) +" гр.)"
            rooms[rNum]["gold"] = 0
                    
        if foundCount == 0: # Нашлось ноль любых вещей
            tmpStr += " НИЧЕГО, то есть, ничего не нашли... Вот обидно, только здоровье и спичку зря потратили :("
        else:
            msgColor = "green"

        tmpStr = tmpStr.replace(".) ", ".), ")
    else:
        tmpStr = ("К сожалению, у Вас нет спичек, чтобы разогнать темноту, "+
                  "скопившуюся по углам комнаты...")
        winsound.Beep(300,100)

    msg = formatStr(tmpStr, 60)
    i=0;
    while i<len(msg):
        printColoredText(3, dialStopLine+3+i, msg[i].ljust(60),msgColor,"white")
        i+=1
        
    showPlayerParams()
    printColoredText(12,19,"Нажмите любую клавишу для продолжения...", "white","blue")
    getch()


# --- Функция обработки клавиши 'G' - использовать аптечку
def usedMedicals():
    global curPlayer

    if curPlayer["energy"]==100:
        tmpStr   = "У Вас и так отличное, стопроцентное здоровье... Использовать аптечку сейчас не требуется..." 
        msgColor = "green"

    elif curPlayer["medicals"]>0:
        curPlayer["medicals"] -= 1
        curPlayer["energy"]   += 5
        if curPlayer["energy"]>100:
            curPlayer["energy"] = 100

        showPlayerParams()
        tmpStr   = "Вы успешно использовали аптечку и поправили свое здоровье..."
        msgColor = "green"

    else:
        tmpStr = ("К сожалению, у Вас нет аптечки, чтобы поправить свое здоровье... Можно "+
                  "попробовать использовать спичку, чтобы разогнать темноту, скопившуюся по "+
                  "углам комнаты, и поискать аптечку там (не обязательно в этой комнате)... "+
                  "Но никаких гарантий, как говорится...")
        msgColor = "red"
        winsound.Beep(300,100)

    msg = formatStr(tmpStr, 60)
    i=0;
    while i<len(msg):
        printColoredText(3, dialStopLine+3+i, msg[i].ljust(60),msgColor,"white")
        i+=1
        
    showPlayerParams()
    printColoredText(12,19,"Нажмите любую клавишу для продолжения...", "white","blue")
    getch()


# --- Главная программа -------------------------------------------
showInterface()
selectPlayer()
introText()

while True:
    clearDialogArea()
    showPlayerParams()
    gotoRoom(curPlayer["roomNum"])

    if ((curPlayer["energy"] == 0) or
        (curPlayer["winner"] == 1)):
        break

    key = getch()
    if ord(key) in range(ord('1'),ord('9')): # Выбрали номер двери
        if int(key) <= len(rooms[curPlayer["roomNum"]]["doors"]):
            curPlayer["roomNum"] = rooms[curPlayer["roomNum"]]["doors"][int(key)-1]["toRoom"]
            curPlayer["energy"] -=1
        else:
            winsound.Beep(300,100)

    elif key.upper() == 'F':    # Выбрали "использовать спичку"
        usedMatches()
    elif key.upper() == 'G':    # Выбрали "использовать аптечку"
        usedMedicals()
    elif key.upper() =='Q':     # Выбрали выход из программы
        break
    else:                       # Нажали непредусмотренную клавишу
        winsound.Beep(300,100)

saveGame()
finalText()
printColoredText(0,24, "\n")
# --- The end.
